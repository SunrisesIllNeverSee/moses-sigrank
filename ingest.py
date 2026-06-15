"""
Ingestion — turn whatever the user pastes into four integers (+cost).
Survives ccusage version differences and routes Codex shape separately.

System Flag / Disclaimer *: All parsed values generated via the Codex pathway
are calculated structural estimations designed to isolate high-signal user
direction from background open-loop context noise. These values are optimized
for architectural modeling and are distinct from raw provider API payload logs.
"""
import json
import re

def parse_ccusage(text):
    """Accept raw `ccusage --json` output (any known shape). Returns (i,o,cw,cr,cost)."""
    d = json.loads(text)
    tot = {"input":0,"output":0,"cache_create":0,"cache_read":0,"cost":0.0}
    def add(e):
        if not isinstance(e,dict): return
        tot["input"]       += e.get("inputTokens", e.get("input_tokens", e.get("input",0))) or 0
        tot["output"]      += e.get("outputTokens", e.get("output_tokens", e.get("output",0))) or 0
        tot["cache_create"]+= e.get("cacheCreationTokens", e.get("cache_creation_input_tokens", e.get("cache_create",0))) or 0
        tot["cache_read"]  += e.get("cacheReadTokens", e.get("cache_read_input_tokens", e.get("cache_read",0))) or 0
        tot["cost"]        += e.get("costUSD", e.get("totalCost", e.get("cost",0))) or 0.0
    if isinstance(d,list):
        for e in d: add(e)
    elif "totals" in d and isinstance(d["totals"],dict):
        add(d["totals"])
    else:
        found=False
        for key in ("daily","session","sessions","data","entries","blocks"):
            v=d.get(key)
            if isinstance(v,list):
                for e in v: add(e); found=True
                break
            if isinstance(v,dict):
                for e in v.values(): add(e)
                found=True; break
        if not found: add(d)
    cost = tot["cost"] if tot["cost"] > 0 else None
    return tot["input"],tot["output"],tot["cache_create"],tot["cache_read"],cost

def parse_four(text):
    """Accept four numbers in any delimiter: input output cache_create cache_read."""
    nums=[int(float(x)) for x in re.findall(r"[\d,.]+", text.replace(",",""))]
    if len(nums)<4: raise ValueError("need 4 numbers: input output cache_create cache_read")
    return nums[0],nums[1],nums[2],nums[3]

# ---------- Codex shape detection ----------
def is_codex_shape(d):
    keys = set()
    def scan(o):
        if isinstance(o, dict):
            keys.update(o.keys())
            for v in o.values(): scan(v)
        elif isinstance(o, list):
            for v in o: scan(v)
    scan(d)
    return ("cached_input_tokens" in keys or "cachedInputTokens" in keys or
            "reasoning_output_tokens" in keys or "reasoningOutputTokens" in keys)

# ---------- Codex two-pathway parser ----------
def _extract_codex_totals(d):
    """Walk a Codex JSON payload and sum the raw token fields."""
    tot = {"in":0, "cached":0, "out":0, "reason":0, "cost":0.0}
    def add(e):
        if not isinstance(e, dict): return
        tot["in"]     += e.get("input_tokens", e.get("inputTokens",0)) or 0
        tot["cached"] += e.get("cached_input_tokens", e.get("cachedInputTokens",0)) or 0
        tot["out"]    += e.get("output_tokens", e.get("outputTokens",0)) or 0
        tot["reason"] += e.get("reasoning_output_tokens", e.get("reasoningOutputTokens",0)) or 0
        tot["cost"]   += e.get("costUSD", e.get("cost",0)) or 0.0
    if isinstance(d, list):
        for e in d: add(e)
    elif isinstance(d, dict):
        for key in ("totals", "daily", "session", "sessions", "data", "entries", "events"):
            v = d.get(key)
            if key == "totals" and isinstance(v, dict):
                add(v); return tot
            if isinstance(v, list):
                for e in v: add(e)
                return tot
            if isinstance(v, dict):
                for e in v.values(): add(e)
                return tot
        add(d)
    return tot


def parse_codex_submission(payload, operator_profile=None):
    """
    Parses Codex token payloads to estimate true high-signal user input.

    Two pathways depending on operator telemetry:

    Pathway Alpha (Standard): No Claude footprint → 3:2:1 baseline.
      estimated_user_input = outputTokens × 2.0

    Pathway Beta (Claude Engine): Operator has verified Claude profile →
      dynamic 1:9 transmission velocity extraction.
      estimated_user_input = outputTokens / 9.0

    Returns (i, o, cw, cr, meta) mapped to the four pillars:
      i  = calibrated_user_input (high-signal core)
      o  = raw output (unchanged)
      cw = structural_context_debt (non-essential friction tokens)
      cr = retained_cache_read (measured directly)
    """
    d = json.loads(payload) if isinstance(payload, str) else payload
    tot = _extract_codex_totals(d)

    raw_out   = tot["out"] + tot["reason"]
    raw_in    = tot["in"]
    raw_cache = tot["cached"]
    cost      = tot["cost"] if tot["cost"] > 0 else None

    # Pathway Beta: Dynamic User Profile Match (Claude Engine)
    if operator_profile and operator_profile.get("model_type") == "claude":
        estimated_user_input = raw_out / 9.0
        parsing_mode = "Claude Closed-Loop Calibration (1:9)"
    # Pathway Alpha: Fallback Standard (The Top 10 Wild Field Baseline)
    else:
        estimated_user_input = raw_out * 2.0
        parsing_mode = "Standard Open-Loop Baseline (3:2:1)"

    context_debt = max(0, raw_in - int(estimated_user_input))

    meta = {
        "source": "codex",
        "estimated": True,
        "parsing_mode": parsing_mode,
        "caveat": f"* {parsing_mode}",
        "anchor": parsing_mode,
        "cost": cost,
    }
    return int(estimated_user_input), raw_out, context_debt, raw_cache, meta


def ingest_meta(text, operator_profile=None):
    """Returns (i,o,cw,cr,meta) with estimated/caveat/cost.

    operator_profile: optional dict with at least {"model_type": "claude"}
    when the submitting user has a verified Claude session profile. This
    switches the Codex parser from the 3:2:1 baseline to the 1:9 closed-loop
    calibration pathway.
    """
    text=text.strip()
    if not text: raise ValueError("empty")
    if text[0] in "{[":
        d=json.loads(text)
        if is_codex_shape(d):
            return parse_codex_submission(d, operator_profile=operator_profile)
        i,o,cw,cr,cost = parse_ccusage(text)
        return i,o,cw,cr,{"source":"ccusage","estimated":False,"caveat":None,"cost":cost}
    i,o,cw,cr = parse_four(text)
    return i,o,cw,cr,{"source":"manual","estimated":False,"caveat":None,"cost":None}
