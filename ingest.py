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

# Field names we recognise (ccusage camelCase and snake_case variants)
_FIELD_ALIASES = {
    "input":        ("inputTokens", "input_tokens"),
    "output":       ("outputTokens", "output_tokens"),
    "cache_create": ("cacheCreationTokens", "cache_creation_input_tokens"),
    "cache_read":   ("cacheReadTokens", "cache_read_input_tokens",
                     "cachedInputTokens", "cached_input_tokens"),
    "cost":         ("totalCost", "costUSD", "cost"),
    "reasoning":    ("reasoningOutputTokens", "reasoning_output_tokens"),
}

def _has_named_fields(text):
    """True if text contains at least two recognised ccusage field names."""
    hits = 0
    for aliases in _FIELD_ALIASES.values():
        for alias in aliases:
            if alias in text:
                hits += 1
                break
    return hits >= 2


def _try_fix_json(text):
    """Try to turn a partial JSON fragment into valid JSON.

    Common pastes:
      "totals": { ... }          →  {"totals": { ... }}
      { "totals": { ... }        →  add missing closing brace
      "inputTokens": 123, ...    →  { ... }
    """
    t = text.strip()
    # Already valid JSON
    if t[0] in "{[":
        try:
            json.loads(t)
            return t
        except json.JSONDecodeError:
            # Missing closing brace — try adding one
            try:
                json.loads(t + "}")
                return t + "}"
            except json.JSONDecodeError:
                try:
                    json.loads(t + "}}")
                    return t + "}}"
                except json.JSONDecodeError:
                    pass
    # Starts with a quoted key like "totals": { ... } or "inputTokens": 123
    if t.startswith('"'):
        candidate = "{" + t
        # Try adding closing braces
        for suffix in ("", "}", "}}"):
            try:
                json.loads(candidate + suffix)
                return candidate + suffix
            except json.JSONDecodeError:
                continue
    return None


def _extract_by_name(text):
    """Extract token values from text containing named fields (any format).

    Works on partial JSON, terminal output, or any text where field names
    appear next to their values. Returns (i, o, cw, cr, cost) or None.
    """
    def grab(aliases):
        for alias in aliases:
            # Match "fieldName": 12345 or "fieldName": 12345.67
            m = re.search(rf'"{re.escape(alias)}"\s*:\s*([\d,.]+)', text)
            if m:
                raw = m.group(1).replace(",", "")
                return int(float(raw))
        return 0

    i  = grab(_FIELD_ALIASES["input"])
    o  = grab(_FIELD_ALIASES["output"])
    cw = grab(_FIELD_ALIASES["cache_create"])
    cr = grab(_FIELD_ALIASES["cache_read"])
    cost_val = None
    for alias in _FIELD_ALIASES["cost"]:
        m = re.search(rf'"{re.escape(alias)}"\s*:\s*([\d,.]+)', text)
        if m:
            raw = m.group(1).replace(",", "")
            cost_val = float(raw)
            if cost_val > 0:
                break
    reasoning = grab(_FIELD_ALIASES["reasoning"])
    if reasoning > 0:
        o += reasoning

    if i + o + cw + cr == 0:
        return None
    return i, o, cw, cr, cost_val


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

    Pathway Alpha (Standard): No Claude footprint -> 3:2:1 baseline.
      estimated_user_input = outputTokens * 2.0

    Pathway Beta (Claude Engine): Operator has verified Claude profile ->
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

    Handles:
      - Full ccusage JSON (Claude: measured, Codex: two-pathway estimation)
      - Partial JSON fragments ("totals": { ... } pasted from terminal)
      - Text with named fields (extracts by field name, not position)
      - Four bare numbers: input output cache_create cache_read

    operator_profile: optional dict with at least {"model_type": "claude"}
    when the submitting user has a verified Claude session profile. This
    switches the Codex parser from the 3:2:1 baseline to the 1:9 closed-loop
    calibration pathway.
    """
    text=text.strip()
    if not text: raise ValueError("empty")

    # --- Strategy 1: Try to parse as valid JSON (or fix partial JSON) ---
    fixed = None
    if text[0] in '{["':
        fixed = _try_fix_json(text)
    if fixed:
        d = json.loads(fixed)
        if is_codex_shape(d):
            return parse_codex_submission(d, operator_profile=operator_profile)
        i,o,cw,cr,cost = parse_ccusage(fixed)
        return i,o,cw,cr,{"source":"ccusage","estimated":False,"caveat":None,"cost":cost}

    # --- Strategy 2: Text has named fields — extract by name ---
    if _has_named_fields(text):
        result = _extract_by_name(text)
        if result:
            i, o, cw, cr, cost_val = result
            has_codex_fields = any(
                alias in text
                for alias in ("cachedInputTokens", "cached_input_tokens",
                              "reasoningOutputTokens", "reasoning_output_tokens")
            )
            if has_codex_fields:
                # Re-route through Codex pathway with extracted totals
                raw_cache = 0
                for alias in _FIELD_ALIASES["cache_read"]:
                    m = re.search(rf'"{re.escape(alias)}"\s*:\s*([\d,.]+)', text)
                    if m:
                        raw_cache = int(float(m.group(1).replace(",", "")))
                        break
                raw_in = 0
                for alias in _FIELD_ALIASES["input"]:
                    m = re.search(rf'"{re.escape(alias)}"\s*:\s*([\d,.]+)', text)
                    if m:
                        raw_in = int(float(m.group(1).replace(",", "")))
                        break
                raw_out = o  # already includes reasoning from _extract_by_name
                if operator_profile and operator_profile.get("model_type") == "claude":
                    est_input = raw_out / 9.0
                    parsing_mode = "Claude Closed-Loop Calibration (1:9)"
                else:
                    est_input = raw_out * 2.0
                    parsing_mode = "Standard Open-Loop Baseline (3:2:1)"
                context_debt = max(0, raw_in - int(est_input))
                meta = {
                    "source": "codex", "estimated": True,
                    "parsing_mode": parsing_mode,
                    "caveat": f"* {parsing_mode}",
                    "anchor": parsing_mode, "cost": cost_val,
                }
                return int(est_input), raw_out, context_debt, raw_cache, meta
            else:
                cost = cost_val if cost_val and cost_val > 0 else None
                return i, o, cw, cr, {
                    "source": "ccusage", "estimated": False,
                    "caveat": None, "cost": cost,
                }

    # --- Strategy 3: Four bare numbers ---
    i,o,cw,cr = parse_four(text)
    return i,o,cw,cr,{"source":"manual","estimated":False,"caveat":None,"cost":None}
