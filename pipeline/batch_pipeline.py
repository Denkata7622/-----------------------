#!/usr/bin/env python3
"""
batch_pipeline.py — Batch generation when generator.model ends with :batch

Called from pipeline.py main() when CONFIG["generator"]["model"] ends with ":batch".

Flow:
  1. Strip ":batch" suffix → get base model name
  2. Discover working batch endpoint (Anthropic or OpenRouter format)
  3. Build all prompts (reuse Pipeline's helpers)
  4. Submit batch (all pending items at once)
  5. Poll until complete
  6. Fetch results, verify each, write to disk
  7. Update state.json
"""
import sys
import time
import json
import requests
from datetime import datetime
from pathlib import Path

# ── cost tracker init ──
from cost_tracker import init as _ct_init, log_call as _ct_log
_ct_init(Path(__file__).parent.parent / "generated" / "costs" / "ledger.jsonl")


# Batch endpoints to try (in order). Format: (adapter_type, url)
BATCH_ENDPOINTS = [
    ("anthropic", "https://ai.hackclub.com/proxy/v1/messages/batches"),
    # OpenRouter Batch API (beta endpoint)
    ("openrouter", "https://ai.hackclub.com/proxy/api/beta/batches"),
]

POLL_INTERVAL = 30          # seconds between polls
POLL_TIMEOUT = 3600         # 1 hour max
SUBMIT_TIMEOUT = 60
FETCH_TIMEOUT = 60


def _headers():
    from pipeline import CONFIG
    return {
        "Authorization": f"Bearer {CONFIG['generator']['api_key']}",
        "Content-Type": "application/json",
    }


def _discover_endpoint():
    """
    Probe batch endpoints. Returns (adapter_type, endpoint_url, batch_id) — a
    test batch is created and cancelled immediately to prove the endpoint works.
    """
    print("[batch] Търся работещ batch endpoint...")
    for adapter, url in BATCH_ENDPOINTS:
        print(f"  · пробвам {url} ({adapter})...")
        try:
            # Minimal valid-looking submit
            if adapter == "anthropic":
                body = {"requests": []}
            else:
                body = {"endpoint": "/v1/chat/completions", "model": "test", "requests": []}

            r = requests.post(url, headers=_headers(), json=body, timeout=15)

            # 404 = endpoint doesn't exist, try next
            if r.status_code == 404:
                print(f"    ✗ 404 (endpoint не съществува)")
                continue

            # 400 = endpoint exists but body invalid — still useful info
            if r.status_code == 400:
                print(f"    ✓ Endpoint exists (400 при празен body — очаквано)")
                return adapter, url

            # 200/201/202 = worked (shouldn't happen with empty body, but let's handle)
            if r.status_code in (200, 201, 202):
                print(f"    ✓ Endpoint работи (status {r.status_code})")
                return adapter, url

            # 401/403 = auth issue
            if r.status_code in (401, 403):
                print(f"    ✗ Auth failed ({r.status_code}): {r.text[:200]}")
                return None, None

            # other status
            print(f"    ? status {r.status_code}: {r.text[:200]}")

        except requests.RequestException as e:
            print(f"    ✗ network: {e}")

    print("\n⚠ Не намерих работещ batch endpoint.")
    print("  Възможно е Hack Club proxy да не излага batch API за този модел.")
    print("  Опитай синхронен модел (без :batch в config.json).")
    return None, None


def _build_submit_payload(adapter, base_model, jobs):
    """
    Build submit payload for given adapter.
    jobs: list of dicts {custom_id, system, user, max_tokens, temperature}
    """
    from pipeline import CONFIG

    if adapter == "anthropic":
        return {
            "requests": [
                {
                    "custom_id": job["custom_id"],
                    "params": {
                        "model": base_model,
                        "max_tokens": job["max_tokens"],
                        "temperature": job["temperature"],
                        "system": job["system"],
                        "messages": [{"role": "user", "content": job["user"]}],
                    }
                }
                for job in jobs
            ]
        }
    else:  # openrouter
        return {
            "endpoint": "/v1/chat/completions",
            "model": base_model,
            "requests": [
                {
                    "custom_id": job["custom_id"],
                    "body": {
                        "messages": [
                            {"role": "system", "content": job["system"]},
                            {"role": "user", "content": job["user"]},
                        ],
                        "max_tokens": job["max_tokens"],
                        "temperature": job["temperature"],
                        "response_format": {"type": "json_object"},
                    }
                }
                for job in jobs
            ]
        }


def _submit(endpoint, payload):
    r = requests.post(endpoint, headers=_headers(), json=payload, timeout=SUBMIT_TIMEOUT)
    if r.status_code not in (200, 201, 202):
        raise RuntimeError(f"Submit failed ({r.status_code}): {r.text[:400]}")
    data = r.json()
    batch_id = data.get("id") or data.get("batch_id")
    if not batch_id:
        raise RuntimeError(f"No batch id in response: {data}")
    return batch_id, data


def _poll(endpoint, batch_id, timeout=POLL_TIMEOUT):
    poll_url = f"{endpoint}/{batch_id}"
    start = time.time()
    last = None

    while time.time() - start < timeout:
        try:
            r = requests.get(poll_url, headers=_headers(), timeout=30)
            if r.status_code == 404:
                raise RuntimeError(f"Batch {batch_id} не е намерен при poll (404)")
            if r.status_code != 200:
                print(f"    ⚠ poll status {r.status_code} — retry")
                time.sleep(POLL_INTERVAL)
                continue

            data = r.json()
            status = data.get("status", "?").lower()
            if status != last:
                elapsed = int(time.time() - start)
                counts = ""
                if "request_counts" in data:
                    rc = data["request_counts"]
                    counts = f"  [done={rc.get('succeeded', 0)}, fail={rc.get('errored', 0)}, total={rc.get('processing',0)+rc.get('succeeded',0)+rc.get('errored',0)+rc.get('canceled',0)+rc.get('expired',0)}]"
                print(f"    → status: {status} (elapsed {elapsed}s){counts}")
                last = status

            if status in ("completed", "completed_with_errors", "ended", "failed", "expired", "cancelled"):
                return data
        except requests.RequestException as e:
            print(f"    ⚠ poll error: {e}")

        time.sleep(POLL_INTERVAL)

    raise TimeoutError(f"Batch {batch_id} not complete after {timeout}s")


def _fetch_results(endpoint, batch_id, poll_result):
    """Results may be inline (in poll_result) or at a /results endpoint."""
    # 1. Try inline first (OpenRouter format)
    if poll_result.get("results"):
        return poll_result["results"]

    # 2. Try /results endpoint
    url = f"{endpoint}/{batch_id}/results"
    r = requests.get(url, headers=_headers(), timeout=FETCH_TIMEOUT)
    if r.status_code == 200:
        data = r.json()
        return data.get("results", data if isinstance(data, list) else [])

    raise RuntimeError(f"Не мога да взема резултати: {r.status_code} {r.text[:300]}")


def _extract_choice(adapter, result):
    """
    Extract (content, tokens, cost) from a batch result.
    Supports both Anthropic and OpenRouter response formats.
    """
    # Anthropic format: result["result"] is a message object
    if adapter == "anthropic":
        msg = result.get("result") or {}
        content_blocks = msg.get("content") or []
        text = "".join(b.get("text", "") for b in content_blocks if b.get("type") == "text")
        usage = msg.get("usage") or {}
        tokens = (usage.get("input_tokens", 0) or 0) + (usage.get("output_tokens", 0) or 0)
        cost = usage.get("cost", 0.0) or 0.0
        return text.strip(), tokens, cost

    # OpenRouter format: result["response"]["body"] is chat completion
    resp = result.get("response") or {}
    body = resp.get("body") or resp  # some variants don't nest under "body"
    choices = body.get("choices") or []
    text = ""
    if choices:
        text = (choices[0].get("message") or {}).get("content") or ""
    usage = body.get("usage") or {}
    tokens = usage.get("total_tokens", 0) or 0
    cost = usage.get("cost", 0.0) or 0.0
    return text.strip(), tokens, cost


def _check_error(adapter, result):
    """Return error string if result indicates failure, else None."""
    if adapter == "anthropic":
        if result.get("result", {}).get("type") == "error":
            err = result["result"].get("error") or {}
            return f"{err.get('type','?')}: {err.get('message','?')}"
        return None
    # openrouter
    if result.get("error"):
        return str(result["error"])[:300]
    resp = result.get("response") or {}
    if resp.get("status_code") and resp["status_code"] >= 400:
        return f"HTTP {resp['status_code']}: {resp.get('body', {})}"
    return None


def run_batch(only_id=None):
    """Main batch orchestration. Called from pipeline.py when model ends with :batch."""
    from pipeline import (
        Pipeline, CONFIG, format_prompt,
        ARTICLE_PROMPT, ARTICLE_WRITER,
    )

    full_model = CONFIG["generator"]["model"]
    base_model = full_model.replace(":batch", "")

    print()
    print("═" * 60)
    print(f"  BATCH MODE")
    print(f"  Full model: {full_model}")
    print(f"  Base model: {base_model}")
    print("═" * 60)

    # 1. Setup pipeline (we won't call process_item — only use its helper methods)
    p = Pipeline(only_id=only_id)
    p.generator = None  # unused in batch mode

    # 2. Discover endpoint
    adapter, endpoint = _discover_endpoint()
    if not endpoint:
        return 1

    # 3. Collect pending items
    pending = p.queue.pending(p.state, only_id=only_id)
    if not pending:
        print("\nНяма pending items.")
        return 0

    # 4. Budget pre-check
    est_cost = len(pending) * CONFIG["generator"]["cost_per_call_usd"]
    remaining = p.state.budget_remaining()
    print(f"\n[batch] {len(pending)} items pending")
    print(f"  Очаквана цена: ~${est_cost:.2f}")
    print(f"  Оставаща бюджет: ${remaining:.2f}")
    if est_cost > remaining:
        print(f"\n⚠ Batch-ът ще надхвърли бюджета!")
        try:
            ans = input("Продължи? [y/N]: ").strip().lower()
        except EOFError:
            ans = "n"
        if ans != "y":
            print("Отказано.")
            return 1

    # 5. Build all prompts
    print(f"\n[1/5] Строя {len(pending)} prompt-а...")
    jobs = []
    item_map = {}
    for item in pending:
        try:
            user = format_prompt(
                ARTICLE_PROMPT,
                title=item.title,
                point_id=item.id,
                desc=item.desc or "(няма описание)",
                prereqs=p._load_prereqs(item.id),
                source_problems=p._load_source_problems(item),
                real_problems=p._load_real_problems(item.id),
                next_topic=p._load_next_topic(item.id),
            )
        except Exception as e:
            print(f"  ✗ {item.id}: prompt build failed — {e}")
            p.state.mark(item.id, "error")
            continue

        jobs.append({
            "custom_id": item.id,
            "system": ARTICLE_WRITER,
            "user": user,
            "max_tokens": CONFIG["generator"]["max_tokens"],
            "temperature": CONFIG["generator"]["temperature"],
        })
        item_map[item.id] = item

    if not jobs:
        print("Няма валидни jobs.")
        return 1
    print(f"  ✓ {len(jobs)} jobs built")

    # 6. Submit
    print(f"\n[2/5] Подавам batch...")
    try:
        payload = _build_submit_payload(adapter, base_model, jobs)
        batch_id, resp = _submit(endpoint, payload)
        print(f"  ✓ Batch ID: {batch_id}")
        print(f"  ✓ Endpoint: {endpoint}")
        print(f"  ✓ Adapter: {adapter}")
    except Exception as e:
        print(f"  ✗ Submit failed: {e}")
        return 1

    # 7. Poll
    print(f"\n[3/5] Чакам резултати (до {POLL_TIMEOUT//60} мин)...")
    try:
        poll_result = _poll(endpoint, batch_id)
    except Exception as e:
        print(f"  ✗ Poll failed: {e}")
        return 1

    status = poll_result.get("status", "?").lower()
    print(f"  ✓ Batch {status}")

    # 8. Fetch results
    print(f"\n[4/5] Изтеглям резултати...")
    try:
        results = _fetch_results(endpoint, batch_id, poll_result)
        print(f"  ✓ {len(results)} results")
    except Exception as e:
        print(f"  ✗ Fetch failed: {e}")
        return 1

    # 9. Process each result
    print(f"\n[5/5] Обработвам резултати...")
    processed = 0
    errors = 0
    total_cost = 0.0
    total_tokens = 0

    for res in results:
        custom_id = res.get("custom_id")
        item = item_map.get(custom_id)
        if not item:
            print(f"  ⚠ Unknown custom_id: {custom_id}")
            continue

        err = _check_error(adapter, res)
        if err:
            print(f"  ✗ {custom_id}: {err}")
            p.state.mark(custom_id, "error")
            errors += 1
            continue

        try:
            text, tokens, cost = _extract_choice(adapter, res)
            if not text:
                print(f"  ✗ {custom_id}: empty text")
                p.state.mark(custom_id, "error")
                errors += 1
                continue

            _ct_log(module="batch_pipeline", role="gen", model=base_model,
                    in_tokens=0, out_tokens=tokens, cost=cost,
                    status="ok", item_id=custom_id,
                    extra={"batch": True})

            # Parse JSON
            parsed = p._parse_json(text)
            if not parsed or not parsed.get("article_markdown"):
                print(f"  ✗ {custom_id}: JSON parse failed")
                print(f"      raw: {text[:200]!r}")
                p.state.mark(custom_id, "error")
                errors += 1
                continue

            article_md = parsed["article_markdown"].strip()
            parsed["word_count"] = len(article_md.split())

            if not cost:
                cost = CONFIG["generator"]["cost_per_call_usd"]

            # Verify with sync verifier (Sol, etc.)
            verification = None
            ver_cost = 0.0
            if p.verifier is not None:
                verification, ver_cost = p._verify(item, article_md)

            # Prepare item for writer
            item.result = article_md[:800]
            item.deep_result = article_md
            item.verification = verification
            item.tokens_used = tokens
            item.cost_usd = cost + ver_cost
            item.status = "done"
            item.finished_at = time.time()

            p.writer.write(item, parsed)

            sc = verification.get("score") if verification else None
            verdict = verification.get("verdict") if verification else None
            math_err_count = len(verification.get("math_errors", [])) if verification else 0
            issue_count = len(verification.get("issues", [])) if verification else 0

            p.state.mark(
                custom_id, "done", cost + ver_cost, tokens,
                score=sc,
                verdict=verdict,
                word_count=parsed["word_count"],
                generator_model=base_model,
                verifier_model=CONFIG["verifier"]["model"],
                attempts=1,
                math_errors=math_err_count,
                issues=issue_count,
            )
            p.state.add_cost(cost + ver_cost, tokens)
            total_cost += cost + ver_cost
            total_tokens += tokens

            print(f"  ✓ {custom_id}: {parsed['word_count']}w | score {sc} ({verdict}) | ${cost + ver_cost:.4f}")
            processed += 1

        except Exception as e:
            print(f"  ✗ {custom_id}: {e}")
            p.state.mark(custom_id, "error")
            errors += 1

    # 10. Summary
    print()
    print("═" * 60)
    print(f"  BATCH DONE")
    print(f"  Processed: {processed}")
    print(f"  Errors:    {errors}")
    print(f"  Cost:      ${total_cost:.4f}")
    print(f"  Tokens:    {total_tokens}")
    print("═" * 60)
    print()

    return 0 if errors == 0 else 1