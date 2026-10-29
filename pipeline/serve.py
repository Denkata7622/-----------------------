#!/usr/bin/env python3
"""serve.py — Flask сървър за pipeline site + dashboard + orchestrator."""
import sys
import json
import time
import signal
import subprocess
import threading
from pathlib import Path
from datetime import datetime, date
from flask import Flask, render_template, send_from_directory, abort, jsonify, request

BASE = Path(__file__).parent.resolve()
SITE_DIR = BASE.parent
ARTICLES = SITE_DIR / "generated" / "articles"
STATE = BASE / "state.json"
QUEUE = BASE / "queue.jsonl"
PROGRESS = BASE / "progress.json"
COSTS = BASE / "costs.jsonl"
COSTS_LEDGER   = SITE_DIR / "generated" / "costs" / "ledger.jsonl"
COSTS_COMBINED = SITE_DIR / "generated" / "costs" / "combined.json"
COSTS_HISTORICAL = BASE / "provider_costs.json"
LOGS_DIR = BASE / "logs"

app = Flask(__name__, template_folder="templates", static_folder="static")

# ─── Orchestrator state ───
_pipeline_proc = None
_pipeline_lock = threading.Lock()
_started_at = None

# ─── Tool runner state ───
_tool_proc = None
_tool_lock = threading.Lock()
_tool_name = None
_tool_started = None


def load_json(path, default=None):
    if not path.exists():
        return default or {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default or {}


def list_versions(article_dir):
    versions = []
    for f in sorted(article_dir.glob("deep-v*.md")):
        try:
            v = int(f.stem.replace("deep-v", ""))
            versions.append(v)
        except ValueError:
            pass
    latest = max(versions) if versions else None
    return versions, latest


# ═══════════════════════════════════════════════════════════════
# SITE + ARTICLES
# ═══════════════════════════════════════════════════════════════
@app.route("/")
def home():
    return send_from_directory(str(SITE_DIR), "index.html")


@app.route("/article/<point_id>")
def article_page(point_id):
    safe = point_id.replace(".", "_")
    d = ARTICLES / safe
    if not d.exists():
        abort(404)
    versions, latest = list_versions(d)
    meta = load_json(d / "metadata.json")
    return render_template(
        "article.html.j2",
        point_id=point_id,
        versions=versions,
        latest=latest,
        meta=meta,
    )


# ═══════════════════════════════════════════════════════════════
# API: STATE / QUEUE
# ═══════════════════════════════════════════════════════════════
@app.route("/api/state")
def api_state():
    state = load_json(STATE)
    progress = load_json(PROGRESS)
    procs = state.get("processed", {})
    done = sum(1 for v in procs.values() if v.get("status") == "done")
    err = sum(1 for v in procs.values() if v.get("status") == "error")
    scores = [v.get("score") for v in procs.values() if v.get("score")]
    return jsonify({
        "budget": state.get("budget", {}),
        "total_cost_usd": state.get("total_cost_usd", 0),
        "by_model": state.get("by_model", {}),
        "stats": {
            "done": done,
            "error": err,
            "scores": {
                "avg": round(sum(scores) / len(scores), 1) if scores else 0,
                "max": max(scores) if scores else 0,
                "min": min(scores) if scores else 0,
                "distribution": {str(s): scores.count(s) for s in set(scores)},
            },
        },
        "progress": progress,
    })


@app.route("/api/queue")
def api_queue():
    pending = []
    if QUEUE.exists():
        for line in QUEUE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                pending.append(json.loads(line))
            except Exception:
                pass
    state = load_json(STATE)
    done_ids = {k for k, v in state.get("processed", {}).items()
                if v.get("status") == "done"}
    return jsonify({
        "total": len(pending),
        "done": len(done_ids),
        "pending": [p for p in pending if p.get("id") not in done_ids],
    })


# ═══════════════════════════════════════════════════════════════
# API: ARTICLE
# ═══════════════════════════════════════════════════════════════
@app.route("/api/article/<point_id>")
def api_article(point_id):
    safe = point_id.replace(".", "_")
    d = ARTICLES / safe
    if not d.exists():
        abort(404)
    versions, latest = list_versions(d)
    return jsonify({
        "id": point_id,
        "versions": versions,
        "latest": latest,
        "metadata": load_json(d / "metadata.json"),
    })


@app.route("/api/article/<point_id>/v/<int:version>")
def api_article_version(point_id, version):
    safe = point_id.replace(".", "_")
    path = ARTICLES / safe / f"deep-v{version}.md"
    if not path.exists():
        abort(404)
    content = path.read_text(encoding="utf-8")
    if "\n---\n" in content:
        content = content.split("\n---\n", 1)[1]
    return jsonify({"content": content, "version": version})


# ═══════════════════════════════════════════════════════════════
# API: ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════
@app.route("/api/orchestrator/status")
def orch_status():
    global _pipeline_proc, _started_at
    with _pipeline_lock:
        if _pipeline_proc is None:
            return jsonify({"running": False, "pid": None, "uptime_sec": 0})
        code = _pipeline_proc.poll()
        if code is None:
            uptime = int(time.time() - _started_at) if _started_at else 0
            return jsonify({
                "running": True,
                "pid": _pipeline_proc.pid,
                "uptime_sec": uptime,
            })
        _pipeline_proc = None
        _started_at = None
        return jsonify({"running": False, "pid": None, "exit_code": code})


@app.route("/api/orchestrator/start", methods=["POST"])
def orch_start():
    global _pipeline_proc, _started_at
    with _pipeline_lock:
        if _pipeline_proc and _pipeline_proc.poll() is None:
            return jsonify({"error": "already running"}), 400
        try:
            flags = 0
            if sys.platform == "win32":
                flags = subprocess.CREATE_NEW_PROCESS_GROUP
            _pipeline_proc = subprocess.Popen(
                [sys.executable, "pipeline.py"],
                cwd=str(BASE),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=flags,
            )
            _started_at = time.time()
            return jsonify({"status": "started", "pid": _pipeline_proc.pid})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/api/orchestrator/stop", methods=["POST"])
def orch_stop():
    global _pipeline_proc, _started_at
    with _pipeline_lock:
        if not _pipeline_proc or _pipeline_proc.poll() is not None:
            return jsonify({"error": "not running"}), 400
        try:
            if sys.platform == "win32":
                _pipeline_proc.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                _pipeline_proc.terminate()
            try:
                _pipeline_proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                _pipeline_proc.kill()
            _pipeline_proc = None
            _started_at = None
            return jsonify({"status": "stopped"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/api/orchestrator/once", methods=["POST"])
def orch_once():
    """Изпълнява pipeline.py --once [--point X.Y] синхронно."""
    data = request.get_json(silent=True) or {}
    point_id = data.get("point_id")
    args = [sys.executable, "pipeline.py", "--once"]
    if point_id:
        args.extend(["--point", point_id])
    try:
        result = subprocess.run(
            args,
            cwd=str(BASE),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=1800,
        )
        return jsonify({
            "status": "completed" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "stdout": result.stdout[-3000:],
            "stderr": result.stderr[-2000:],
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "timeout after 30 min"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/orchestrator/reset/<point_id>", methods=["POST"])
def orch_reset(point_id):
    """Изтрива дадена точка от state.json (за retry)."""
    state = load_json(STATE)
    if point_id in state.get("processed", {}):
        del state["processed"][point_id]
        STATE.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return jsonify({"status": "reset", "id": point_id})
    return jsonify({"status": "not_found", "id": point_id}), 404


# ═══════════════════════════════════════════════════════════════
# API: LOGS
# ═══════════════════════════════════════════════════════════════
@app.route("/api/logs/tail")
def logs_tail():
    lines = min(int(request.args.get("lines", 200)), 2000)
    log_file = LOGS_DIR / f"pipeline_{date.today()}.log"
    if not log_file.exists():
        return jsonify({"lines": [], "total": 0, "path": str(log_file)})
    try:
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
        return jsonify({
            "lines": all_lines[-lines:],
            "total": len(all_lines),
            "path": str(log_file),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════
# API: COSTS
# ═══════════════════════════════════════════════════════════════
@app.route("/api/costs/by-model")
def costs_by_model():
    if not COSTS.exists():
        return jsonify({})
    by_model = {}
    try:
        with open(COSTS, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                    m = e.get("model", "unknown")
                    s = by_model.setdefault(m, {"calls": 0, "tokens": 0, "cost": 0.0})
                    s["calls"] += 1
                    s["tokens"] += e.get("tokens", 0)
                    s["cost"] += e.get("cost", 0.0)
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return jsonify(by_model)


@app.route("/api/costs/recent")
def costs_recent():
    n = min(int(request.args.get("n", 50)), 500)
    if not COSTS.exists():
        return jsonify([])
    entries = []
    try:
        with open(COSTS, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines[-n:]:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except Exception:
        pass
    return jsonify(entries[::-1])


@app.route("/api/costs/today")
def costs_today():
    if not COSTS.exists():
        return jsonify({"total": 0, "calls": 0, "by_model": {}})
    today = str(date.today())
    total = 0.0
    calls = 0
    by_model = {}
    try:
        with open(COSTS, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                    if e.get("ts", "")[:10] != today:
                        continue
                    total += e.get("cost", 0.0)
                    calls += 1
                    m = e.get("model", "unknown")
                    bm = by_model.setdefault(m, {"cost": 0.0, "calls": 0})
                    bm["cost"] += e.get("cost", 0.0)
                    bm["calls"] += 1
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return jsonify({"total": total, "calls": calls, "by_model": by_model})


# ═══════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html.j2")


# ═══════════════════════════════════════════════════════════════
# API: TOOLS — call every .py script in the pipeline
# ═══════════════════════════════════════════════════════════════

def _spawn_tool(name: str, cmd: list, timeout: int = 1800):
    """Изпълнява .py скрипт синхронно, връща stdout/stderr.

    ВАЖНО:
      • НЕ ползваме creationflags=CREATE_NEW_PROCESS_GROUP тук —
        комбинацията с capture_output на Windows дава stdout=None.
      • ФОРСИРАМЕ UTF-8 и в дъщерния, и в parent процеса. Без това
        emoji в integrate.py / pipeline.py хвърлят UnicodeEncodeError
        на cp1252, а изходът се губи/mojibake-ва.
    """
    import os
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["PYTHONLEGACYWINDOWSSTDIO"] = "0"

    try:
        result = subprocess.run(
            [sys.executable] + cmd,
            cwd=str(BASE),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=timeout,
        )
        stdout = result.stdout if result.stdout is not None else ""
        stderr = result.stderr if result.stderr is not None else ""
        return {
            "status": "completed" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "stdout": stdout[-4000:],
            "stderr": stderr[-2000:],
            "name": name,
            "_diag": {
                "stdout_len": len(stdout),
                "stderr_len": len(stderr),
            },
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "name": name, "error": f"timeout {timeout}s"}
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "name": name,
            "error": str(e),
            "traceback": traceback.format_exc()[-2000:],
        }


@app.route("/api/tools/list")
def tools_list():
    """Списък с всички .py скриптове."""
    scripts = []
    for f in sorted(BASE.glob("*.py")):
        scripts.append({
            "name": f.name,
            "size_kb": round(f.stat().st_size / 1024, 1),
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        })
    return jsonify(scripts)


# ─── Safe tools (no API cost) ───
@app.route("/api/tools/scan-queue", methods=["POST"])
def tool_scan_queue():
    return jsonify(_spawn_tool("scan-queue",
        ["pipeline.py", "--scan", "--no-verify"], 60))


@app.route("/api/tools/pipeline-stats", methods=["POST"])
def tool_pipeline_stats():
    return jsonify(_spawn_tool("pipeline-stats",
        ["pipeline.py", "--stats"], 30))


@app.route("/api/tools/pipeline-report", methods=["POST"])
def tool_pipeline_report():
    return jsonify(_spawn_tool("pipeline-report",
        ["pipeline.py", "--report"], 60))


@app.route("/api/tools/chunker-audit", methods=["POST"])
def tool_chunker_audit():
    return jsonify(_spawn_tool("chunker-audit",
        ["pdf_chunker.py", "--audit"], 120))


@app.route("/api/tools/chunker-stats", methods=["POST"])
def tool_chunker_stats():
    return jsonify(_spawn_tool("chunker-stats",
        ["pdf_chunker.py", "--stats"], 60))


@app.route("/api/tools/chunker-scan", methods=["POST"])
def tool_chunker_scan():
    data = request.get_json(silent=True) or {}
    args = ["pdf_chunker.py", "--scan"]
    if data.get("limit"):
        args.extend(["--limit", str(int(data["limit"]))])
    return jsonify(_spawn_tool("chunker-scan", args, 120))


@app.route("/api/tools/chunker-merge", methods=["POST"])
def tool_chunker_merge():
    return jsonify(_spawn_tool("chunker-merge",
        ["pdf_chunker.py", "--merge"], 300))


@app.route("/api/tools/chunker-aggregate", methods=["POST"])
def tool_chunker_aggregate():
    return jsonify(_spawn_tool("chunker-aggregate",
        ["pdf_chunker.py", "--aggregate"], 120))


# ─── Costly tools (use API credits) ───
@app.route("/api/tools/chunker-extract", methods=["POST"])
def tool_chunker_extract():
    """ВНИМАНИЕ: таксува API. UI трябва да попита за потвърждение."""
    data = request.get_json(silent=True) or {}
    args = ["pdf_chunker.py", "--extract"]
    if data.get("pdf"):
        args.extend(["--pdf", data["pdf"]])
    if data.get("limit"):
        args.extend(["--limit", str(int(data["limit"]))])
    if data.get("force"):
        args.append("--force-extract")
    return jsonify(_spawn_tool("chunker-extract", args, 1800))


@app.route("/api/tools/chunker-classify", methods=["POST"])
def tool_chunker_classify():
    """ВНИМАНИЕ: таксува API. UI трябва да попита за потвърждение."""
    data = request.get_json(silent=True) or {}
    args = ["pdf_chunker.py", "--classify-paired"]
    if data.get("pdf"):
        args.extend(["--pdf", data["pdf"]])
    if data.get("force"):
        args.append("--force")
    if data.get("limit"):
        args.extend(["--limit", str(int(data["limit"]))])
    return jsonify(_spawn_tool("chunker-classify", args, 1800))


# ─── Full refresh chain ───
@app.route("/api/tools/full-refresh", methods=["POST"])
def tool_full_refresh():
    """Chain: merge → classify → aggregate. БЕЗ extract (скъпо е)."""
    steps = [
        ("chunker-merge",     ["pdf_chunker.py", "--merge"],            300),
        ("chunker-classify",  ["pdf_chunker.py", "--classify-paired"],  1800),
        ("chunker-aggregate", ["pdf_chunker.py", "--aggregate"],        120),
    ]
    results = []
    for name, cmd, t in steps:
        r = _spawn_tool(name, cmd, t)
        results.append(r)
        if r["status"] != "completed":
            break
    ok = all(r["status"] == "completed" for r in results)
    return jsonify({"steps": results, "status": "completed" if ok else "partial"})


# ─── Utility commands on single points ───
@app.route("/api/tools/verify/<point_id>", methods=["POST"])
def tool_verify(point_id):
    """verify_only.py <id> — верификация без регенерация (≈$0.08)"""
    return jsonify(_spawn_tool("verify",
        ["verify_only.py", point_id], 300))


@app.route("/api/tools/recover/<point_id>", methods=["POST"])
def tool_recover(point_id):
    """recover_point.py <id> — възстановява от temp"""
    return jsonify(_spawn_tool("recover",
        ["recover_point.py", point_id], 60))


@app.route("/api/tools/rebuild-index", methods=["POST"])
def tool_rebuild_index():
    """integrate.py — ако съществува"""
    integrate = BASE / "integrate.py"
    if not integrate.exists():
        return jsonify({
            "status": "skipped",
            "reason": "integrate.py not found in pipeline/",
        }), 404
    return jsonify(_spawn_tool("rebuild-index",
        ["integrate.py"], 600))


@app.route("/api/articles")
def api_articles():
    """Пълен списък със статии + метаданни."""
    state = load_json(STATE)
    procs = state.get("processed", {})
    articles = []
    for pid, d in procs.items():
        articles.append({
            "id": pid,
            "status": d.get("status"),
            "score": d.get("score"),
            "verdict": d.get("verdict"),
            "word_count": d.get("word_count"),
            "cost": d.get("cost", 0),
            "tokens": d.get("tokens", 0),
            "ts": d.get("ts"),
            "attempts": d.get("attempts"),
            "generator_model": d.get("generator_model"),
            "verifier_model": d.get("verifier_model"),
            "math_errors": d.get("math_errors", 0),
            "issues": d.get("issues", 0),
        })
    return jsonify(articles)


@app.route("/api/costs/all")
def api_costs_all():
    """Пълен costs.jsonl — за timeline chart."""
    if not COSTS.exists():
        return jsonify([])
    entries = []
    try:
        with open(COSTS, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return jsonify(entries)


# ═══════════════════════════════════════════════════════════════
# API: COSTS — combined + ledger + refresh
# ═══════════════════════════════════════════════════════════════
@app.route("/api/costs/combined")
def api_costs_combined():
    """combined.json = provider_costs.json + ledger.jsonl (от cost_aggregate.py)."""
    if not COSTS_COMBINED.exists():
        # Опитай да го генерираме on-the-fly (първи старт)
        try:
            from cost_tracker import init as _ct_init
            _ct_init(COSTS_LEDGER)
            import subprocess as _sp
            _sp.run(
                [sys.executable, "cost_aggregate.py"],
                cwd=str(BASE),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
        except Exception:
            pass

    if not COSTS_COMBINED.exists():
        return jsonify({
            "generated_at": None,
            "sources": {"historical": 0, "live": 0, "combined": 0},
            "totals": {"cost": 0, "calls": 0, "tokens": 0,
                       "reasoning_tokens": 0, "cached_tokens": 0,
                       "cost_prompt": 0, "cost_completion": 0},
            "by_model": {}, "by_day": {}, "by_role": {},
        })
    try:
        return jsonify(json.loads(COSTS_COMBINED.read_text(encoding="utf-8")))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/costs/refresh", methods=["POST"])
def api_costs_refresh():
    """Re-run cost_aggregate.py и върни summary."""
    try:
        result = subprocess.run(
            [sys.executable, "cost_aggregate.py"],
            cwd=str(BASE),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        if result.returncode != 0:
            return jsonify({
                "error": "cost_aggregate.py failed",
                "stderr": result.stderr[-1000:],
            }), 500

        if COSTS_COMBINED.exists():
            data = json.loads(COSTS_COMBINED.read_text(encoding="utf-8"))
            return jsonify({
                "ok": True,
                "entries": data.get("sources", {}).get("combined", 0),
                "historical": data.get("sources", {}).get("historical", 0),
                "live": data.get("sources", {}).get("live", 0),
                "total": data.get("totals", {}).get("cost", 0),
                "stdout": result.stdout[-1000:],
            })
        return jsonify({"error": "combined.json not produced"}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"error": "timeout 60s"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/costs/ledger/tail")
def api_costs_ledger_tail():
    """Live ledger — последните N записа (за debug)."""
    n = min(int(request.args.get("n", 50)), 500)
    if not COSTS_LEDGER.exists():
        return jsonify({"lines": [], "total": 0})
    try:
        with open(COSTS_LEDGER, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return jsonify({
            "lines": [json.loads(l) for l in lines[-n:] if l.strip()],
            "total": len(lines),
            "path": str(COSTS_LEDGER),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════
# API: DEBUG — диагностика на subprocess
# ═══════════════════════════════════════════════════════════════
@app.route("/api/tools/debug", methods=["GET"])
def tools_debug():
    """Diagnostic — показва как subprocess.run се държи в тази среда."""
    import traceback
    out = {
        "python": sys.executable,
        "version": sys.version,
        "platform": sys.platform,
        "cwd": str(BASE),
    }

    # Test 1: базов subprocess без флагове
    try:
        r = subprocess.run(
            [sys.executable, "-c", "print('hello-from-debug')"],
            cwd=str(BASE), capture_output=True, text=True, timeout=10,
        )
        out["test_basic"] = {
            "returncode": r.returncode,
            "stdout": r.stdout,
            "stderr": r.stderr,
            "stdout_type": type(r.stdout).__name__,
            "stderr_type": type(r.stderr).__name__,
            "has_stdout": r.stdout is not None,
            "has_stderr": r.stderr is not None,
        }
    except Exception as e:
        out["test_basic_error"] = str(e)
        out["test_basic_traceback"] = traceback.format_exc()

    # Test 2: със CREATE_NEW_PROCESS_GROUP
    if sys.platform == "win32":
        try:
            r = subprocess.run(
                [sys.executable, "-c", "print('hello-with-flag')"],
                cwd=str(BASE), capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
            out["test_with_flag"] = {
                "returncode": r.returncode,
                "stdout": r.stdout,
                "stderr": r.stderr,
                "stdout_type": type(r.stdout).__name__,
                "stderr_type": type(r.stderr).__name__,
                "has_stdout": r.stdout is not None,
                "has_stderr": r.stderr is not None,
            }
        except Exception as e:
            out["test_with_flag_error"] = str(e)
            out["test_with_flag_traceback"] = traceback.format_exc()

    # Test 3: реален pipeline.py --stats
    try:
        r = subprocess.run(
            [sys.executable, "pipeline.py", "--stats"],
            cwd=str(BASE), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30,
        )
        out["test_pipeline_stats"] = {
            "returncode": r.returncode,
            "stdout_len": len(r.stdout) if r.stdout is not None else -1,
            "stderr_len": len(r.stderr) if r.stderr is not None else -1,
            "stdout_preview": (r.stdout or "")[-500:],
            "stderr_preview": (r.stderr or "")[-500:],
            "has_stdout": r.stdout is not None,
            "has_stderr": r.stderr is not None,
        }
    except Exception as e:
        out["test_pipeline_stats_error"] = str(e)
        out["test_pipeline_stats_traceback"] = traceback.format_exc()

    return jsonify(out)


# ═══════════════════════════════════════════════════════════════
# STATIC FILE FALLBACK — сервира всичко от SITE_DIR
# (data/*.js, style.css, ai_assistant.js и т.н.)
# ═══════════════════════════════════════════════════════════════
@app.route("/<path:filename>")
def serve_site_file(filename):
    # Не пипаме API/dashboard/article routes
    if (filename.startswith("api/") or
        filename == "dashboard" or
        filename.startswith("dashboard/") or
        filename == "article" or
        filename.startswith("article/")):
        abort(404)

    file_path = SITE_DIR / filename
    if not file_path.exists() or not file_path.is_file():
        abort(404)

    # Security: prevent path traversal
    try:
        file_path.resolve().relative_to(SITE_DIR.resolve())
    except ValueError:
        abort(403)

    return send_from_directory(str(SITE_DIR), filename)


# ═══════════════════════════════════════════════════════════════
# BACKGROUND SCHEDULER — cost_aggregate на всеки 5 мин
# ═══════════════════════════════════════════════════════════════
def _cost_scheduler_loop(interval_sec: int = 300):
    """Rebuild-ва combined.json на всеки 5 мин (в daemon thread)."""
    time.sleep(10)  # изчакай Flask да стартира
    while True:
        try:
            result = subprocess.run(
                [sys.executable, "cost_aggregate.py"],
                cwd=str(BASE),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
            )
            if result.returncode == 0:
                print(f"[cost_scheduler] ✓ combined.json rebuilt "
                      f"({datetime.now().strftime('%H:%M:%S')})")
            else:
                print(f"[cost_scheduler] ✗ failed: {result.stderr[-300:]}")
        except Exception as e:
            print(f"[cost_scheduler] ✗ {e}")
        time.sleep(interval_sec)


if __name__ == "__main__":
    print("═" * 60)
    print("  AI Pipeline Control Center")
    print("  http://localhost:8000              — основен сайт")
    print("  http://localhost:8000/dashboard    — контролен панел")
    print("  http://localhost:8000/api/costs/combined    — combined costs")
    print("  http://localhost:8000/api/costs/refresh     — refresh costs")
    print("═" * 60)

    # Background cost aggregator (daemon — умира с процеса)
    _sched_thread = threading.Thread(
        target=_cost_scheduler_loop,
        args=(300,),
        daemon=True,
        name="cost_scheduler",
    )
    _sched_thread.start()

    app.run(host="127.0.0.1", port=8000, debug=False, threaded=True)