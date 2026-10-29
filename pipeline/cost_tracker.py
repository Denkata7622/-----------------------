#!/usr/bin/env python3
"""cost_tracker.py — централен ledger за всички AI разходи."""
from __future__ import annotations
import json, threading, time
from datetime import datetime
from pathlib import Path
from typing import Optional

MODEL_PRICING: dict[str, dict[str, float]] = {
    "gpt-6.1-sol":        {"input": 1.50, "output": 8.00},
    "gpt-6.1":            {"input": 1.50, "output": 8.00},
    "gpt-oss-120b":       {"input": 0.15, "output": 0.60},
    "deepseek-v3.2":      {"input": 0.15, "output": 0.30},
    "deepseek-r1":        {"input": 0.75, "output": 2.50},
    "deepseek-v3":        {"input": 0.15, "output": 0.30},
    "claude-opus-5.5":    {"input": 15.00, "output": 75.00},
    "claude-opus-4.5":    {"input": 15.00, "output": 75.00},
    "claude-sonnet-5.5":  {"input":  3.00, "output": 15.00},
    "claude-sonnet-4.6":  {"input":  3.00, "output": 15.00},
    "claude-sonnet-4.5":  {"input":  3.00, "output": 15.00},
    "claude-haiku-4.5":   {"input":  1.00, "output":  5.00},
    "glm-5.3-flashx":     {"input":  0.10, "output":  0.40},
    "glm-5.3-flash":      {"input":  0.05, "output":  0.20},
    "mistral-ocr-latest": {"input":  0.0,  "output":  0.0},
}

_ledger_path: Optional[Path] = None
_lock = threading.Lock()


def init(path) -> Path:
    global _ledger_path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    _ledger_path = p
    return p


def _find_pricing(model: str) -> Optional[dict]:
    if not model:
        return None
    low = model.lower()
    for key, price in MODEL_PRICING.items():
        if key in low:
            return price
    return None


def compute_cost(model: str, in_tokens: int, out_tokens: int) -> float:
    p = _find_pricing(model)
    if not p:
        return 0.0
    return (in_tokens * p["input"] + out_tokens * p["output"]) / 1_000_000.0


def extract_usage(data: dict, is_anthropic: bool = False):
    usage = data.get("usage", {}) or {}
    if is_anthropic:
        in_t = int(usage.get("input_tokens", 0) or 0)
        out_t = int(usage.get("output_tokens", 0) or 0)
    else:
        in_t = int(usage.get("prompt_tokens", 0) or 0)
        out_t = int(usage.get("completion_tokens", 0) or 0)
    total = int(usage.get("total_tokens", 0) or (in_t + out_t))
    api_cost = usage.get("cost") or usage.get("total_cost") or usage.get("cost_usd") or 0.0
    try:
        api_cost = float(api_cost)
    except (TypeError, ValueError):
        api_cost = 0.0
    return in_t, out_t, total, api_cost


def extract_extras(data: dict, is_anthropic: bool = False) -> dict:
    """Всички допълнителни полета от API response:
       cost_details.* + completion_tokens_details.* + cached_tokens + is_byok."""
    usage = data.get("usage", {}) or {}

    cost_details = usage.get("cost_details", {}) or {}
    prompt_cost = float(cost_details.get("upstream_inference_prompt_cost", 0) or 0)
    completion_cost = float(cost_details.get("upstream_inference_completions_cost", 0) or 0)

    comp_details = usage.get("completion_tokens_details", {}) or {}
    reasoning_t = int(comp_details.get("reasoning_tokens", 0) or 0)
    image_t = int(comp_details.get("image_tokens", 0) or 0)
    audio_t = int(comp_details.get("audio_tokens", 0) or 0)

    prompt_details = usage.get("prompt_tokens_details", {}) or {}
    cached_t = int(prompt_details.get("cached_tokens", 0) or 0)
    cache_write_t = int(prompt_details.get("cache_write_tokens", 0) or 0)

    return {
        "cost_prompt":       round(prompt_cost, 8),
        "cost_completion":   round(completion_cost, 8),
        "reasoning_tokens":  reasoning_t,
        "image_tokens":      image_t,
        "audio_tokens":      audio_t,
        "cached_tokens":     cached_t,
        "cache_write_tokens": cache_write_t,
        "is_byok":           bool(usage.get("is_byok", False)),
    }


def log_call(module, role, model, in_tokens, out_tokens, cost,
             status="ok", item_id=None, latency_ms=None, extra=None):
    if _ledger_path is None:
        return
    record = {
        "ts":         datetime.now().isoformat(timespec="seconds"),
        "module":     module,
        "role":       role,
        "model":      model,
        "in_tokens":  int(in_tokens or 0),
        "out_tokens": int(out_tokens or 0),
        "tokens":     int(in_tokens or 0) + int(out_tokens or 0),
        "cost":       round(float(cost or 0.0), 8),
        "status":     status,
    }
    if item_id is not None:
        record["item_id"] = str(item_id)[:80]
    if latency_ms is not None:
        record["latency_ms"] = int(latency_ms)
    if extra:
        for k, v in extra.items():
            if k not in record:
                record[k] = v
    line = json.dumps(record, ensure_ascii=False)
    with _lock:
        try:
            with open(_ledger_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass


def track_call(module, role, model, data, item_id=None,
               is_anthropic=False, t0=None):
    """Parse `data` (API response) → log to ledger. Never raises."""
    try:
        in_t, out_t, _, api_cost = extract_usage(data, is_anthropic=is_anthropic)
        total = api_cost or compute_cost(model, in_t, out_t)

        extras = extract_extras(data, is_anthropic=is_anthropic)

        # Ако API не върна cost_details, но имаме total — split по pricing
        if extras["cost_prompt"] == 0 and extras["cost_completion"] == 0 and total > 0:
            p = _find_pricing(model)
            if p and (in_t + out_t) > 0:
                extras["cost_prompt"]     = round(in_t  * p["input"]  / 1_000_000, 8)
                extras["cost_completion"] = round(out_t * p["output"] / 1_000_000, 8)

        lat = None
        if t0 is not None:
            lat = int((time.time() - t0) * 1000)

        log_call(module=module, role=role, model=model,
                 in_tokens=in_t, out_tokens=out_t, cost=total,
                 status="ok", item_id=item_id, latency_ms=lat,
                 extra=extras)
    except Exception:
        pass