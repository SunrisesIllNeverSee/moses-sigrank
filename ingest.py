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
    return ("cached_input_tokens" in keys or "cachedInputTokens" in keys or
            "reasoning_output_tokens" in keys or "reasoningOutputTokens" in keys)

def parse_codex(text, io_ratio=None):
    """
    Codex reports combined input_tokens (incl. cached) + cached_input_tokens +
    output + reasoning. cache_create is never reported by OpenAI.

    Anchor strategy (turn-delta-first, ratio fallback):
    - If daily/session granularity is present, estimate cache_create from
      per-day context deltas (turn-delta method): each day's input growth above
      the previous day's total \u2248 new cache writes.
    - Else, fall back to io_ratio anchor: est_fresh = io_ratio * output.
    - io_ratio defaults to 2.0 (provisional); pass Claude's measured I/O ratio
      for better accuracy.

    cache_read = cachedInputTokens (measured directly).
    """
    d = json.loads(text) if isinstance(text, str) else text
    tot = {"in":0, "cached":0, "out":0, "reason":0, "cost":0.0}
    days = []  # for turn-delta
    def add(e, track=False):
        if not isinstance(e, dict): return
        i   = e.get("input_tokens", e.get("inputTokens",0)) or 0
        ca  = e.get("cached_input_tokens", e.get("cachedInputTokens",0)) or 0
        o   = e.get("output_tokens", e.get("outputTokens",0)) or 0
        r   = e.get("reasoning_output_tokens", e.get("reasoningOutputTokens",0)) or 0
        c   = e.get("costUSD", e.get("cost",0)) or 0.0
        tot["in"] += i; tot["cached"] += ca
        tot["out"] += o; tot["reason"] += r; tot["cost"] += c
        if track and i > 0:
            days.append({"date": e.get("date",""), "in": i, "cached": ca})
    if isinstance(d, list):
        for e in d: add(e)
    else:
        for key in ("daily","session","sessions","data","entries","events"):
            v = d.get(key) if isinstance(d, dict) else None
            if isinstance(v, list):
                for e in v: add(e, track=True)
                break
            if isinstance(v, dict):
                for e in v.values(): add(e)
                break
        else:
            add(d)

    combined_in = tot["in"]; read = tot["cached"]; O = tot["out"] + tot["reason"]
    anchor_used = "2:1 fixed"

    # --- turn-delta method (when we have daily granularity) ---
    if len(days) >= 2:
        days.sort(key=lambda x: x["date"])
        # Each day's fresh input above the previous day's floor \u2248 new cache writes.
        # Heuristic: new context added each day = max(0, today.in - prev.in)
        create = 0
        prev = days[0]["in"]
        for day in days[1:]:
            delta = max(0, day["in"] - prev)
            create += delta
            prev = day["in"]
        create += days[0]["in"]  # first day's full input is new cache
        I = combined_in  # fresh input IS inputTokens (not combined with reads)
        anchor_used = "turn-delta"
        caveat = "estimated via turn-delta (cache_create from daily context growth)"
    else:
        # --- ratio anchor fallback ---
        ratio = io_ratio if io_ratio and io_ratio > 0 else 2.0
        est_fresh = ratio * O
        create = combined_in - est_fresh
        if create >= 0:
            I = est_fresh
            label = f"{ratio:.2f}:1 anchor (Claude-measured)" if io_ratio else "2:1 anchor (fixed)"
            anchor_used = label
            caveat = f"estimated via {label}"
        else:
            create = 0
            I = max(combined_in - read, 0) or combined_in
            anchor_used = "fallback (anchor inverted)"
            caveat = "estimated \u2193 output-rich (anchor inverted)"

    meta = {"source":"codex", "estimated":True, "caveat":caveat,
            "anchor": anchor_used,
            "cost": tot["cost"] if tot["cost"] > 0 else None}
    return I, O, int(create), read, meta

def ingest_meta(text, io_ratio=None):
    """Returns (i,o,cw,cr,meta) with estimated/caveat/cost."""
    text=text.strip()
    if not text: raise ValueError("empty")
    if text[0] in "{[":
        d=json.loads(text)
        if is_codex_shape(d):
            return parse_codex(d, io_ratio=io_ratio)
        i,o,cw,cr,cost = parse_ccusage(text)
        return i,o,cw,cr,{"source":"ccusage","estimated":False,"caveat":None,"cost":cost}
    i,o,cw,cr = parse_four(text)
    return i,o,cw,cr,{"source":"manual","estimated":False,"caveat":None,"cost":None}
