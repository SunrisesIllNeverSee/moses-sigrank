"""
Ingestion — turn whatever the user pastes into four integers (+cost).
Survives ccusage version differences and routes Codex shape separately.
"""
import json

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
    """Accept four numbers in any delimiter."""
    import re
    nums=[int(float(x)) for x in re.findall(r"[\d,.]+", text.replace(",",""))]
    if len(nums)<4: raise ValueError("need 4 numbers: input output cache_create cache_read")
    return nums[0],nums[1],nums[2],nums[3]

# ---------- Codex parse (combined-input split via 2:1 field anchor) ----------
def is_codex_shape(d):
    keys = set()
    def scan(o):
        if isinstance(o, dict):
            keys.update(o.keys())
            for v in o.values(): scan(v)
        elif isinstance(o, list):
            for v in o: scan(v)
    scan(d)
    return "cached_input_tokens" in keys or "reasoning_output_tokens" in keys

def parse_codex(text):
    """
    Codex reports combined input_tokens (incl. cached) + cached_input_tokens +
    output + reasoning. No cache_create exists. We estimate the split using the
    measured field anchor input:output ~ 2:1 (provisional, being refined):
      est_fresh_input = 2 * output
      cache_create    = combined_input - est_fresh_input   (clamped >=0)
      cache_read      = cached_input_tokens                 (measured)
    Returns (i, o, cache_create, cache_read, meta) with a directional caveat.
    """
    d = json.loads(text) if isinstance(text, str) else text
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
    else:
        for key in ("daily","session","sessions","data","entries","events"):
            v = d.get(key) if isinstance(d, dict) else None
            if isinstance(v, list):
                for e in v: add(e)
                break
            if isinstance(v, dict):
                for e in v.values(): add(e)
                break
        else:
            add(d)
    combined_in = tot["in"]; read = tot["cached"]; O = tot["out"] + tot["reason"]
    est_fresh = 2 * O
    create = combined_in - est_fresh
    if create >= 0:
        I = est_fresh
        caveat = ("estimated \u2191 input-heavy vs 2:1 baseline" if combined_in > est_fresh
                  else "estimated \u2248 2:1 baseline")
    else:
        create = 0
        I = max(combined_in - read, 0) or combined_in
        caveat = "estimated \u2193 output-rich (2:1 anchor inverted)"
    meta = {"source":"codex", "estimated":True, "caveat":caveat,
            "anchor":"input:output 2:1 (provisional)",
            "cost": tot["cost"] if tot["cost"] > 0 else None}
    return I, O, create, read, meta

def ingest_meta(text):
    """Returns (i,o,cw,cr,meta) with estimated/caveat/cost."""
    text=text.strip()
    if not text: raise ValueError("empty")
    if text[0] in "{[":
        d=json.loads(text)
        if is_codex_shape(d):
            return parse_codex(d)
        i,o,cw,cr,cost = parse_ccusage(text)
        return i,o,cw,cr,{"source":"ccusage","estimated":False,"caveat":None,"cost":cost}
    i,o,cw,cr = parse_four(text)
    return i,o,cw,cr,{"source":"manual","estimated":False,"caveat":None,"cost":None}
