"""
MO§ES SigRank — metric engine.
Four raw integers in, full ledger out. No circular dependencies.
Every formula verified in session docs 023/024/025.
Optional cost: pass a `cost_usd` (from ccusage) to get Avg $/1M.
"""
import math

# default per-1M prices (USD) — Claude Sonnet-class, used only if no cost given
DEFAULT_PRICES = {"input": 3.0, "output": 15.0, "cache_read": 0.30, "cache_create": 3.75}

def compute(i, o, cw, cr, cost_usd=None, prices=None):
    """i=input, o=output, cw=cache_create, cr=cache_read (raw integers).
    cost_usd: total $ for the window (ccusage provides it) -> Avg $/1M.
    prices: optional per-1M price dict to compute cost when cost_usd is None."""
    i = max(i, 0); o = max(o, 0); cw = max(cw, 0); cr = max(cr, 0)
    cache = cw + cr
    total = i + o + cache
    safe_i = i if i > 0 else 1

    snr        = o / (i + o) if (i + o) > 0 else 0.0
    velocity   = o / safe_i
    leverage   = cr / safe_i
    yield_     = (cr / safe_i) * (o / safe_i)

    if cw > 0 and o > 0 and i > 0 and cr > 0:
        transmission = o / i
        commitment   = cw / o
        reuse        = cr / cw
        dev10x       = math.log10(transmission * commitment * reuse)
        cascade_str  = f"{transmission:.1f}\u00d7{commitment:.1f}\u00d7{reuse:.1f}"
    else:
        transmission = commitment = reuse = dev10x = None
        cascade_str  = "\u2014"

    op_ratio = f"{cache/safe_i:.0f}:1:{o/safe_i:.1f}"
    efficiency = ((cache + o) / safe_i) / 4.0

    # Avg cost per 1M tokens (blended across all states)
    if cost_usd is None:
        p = prices or DEFAULT_PRICES
        cost_usd = (i*p["input"] + o*p["output"] + cr*p["cache_read"]
                    + cw*p["cache_create"]) / 1_000_000
        cost_estimated = prices is None  # default prices => estimate
    else:
        cost_estimated = False
    avg_cost_1m = (cost_usd / (total / 1_000_000)) if total > 0 else 0.0

    V = math.log10(total) if total > 0 else 0.0
    comp = {
        "input":  100*i/total  if total else 0,
        "output": 100*o/total  if total else 0,
        "create": 100*cw/total if total else 0,
        "read":   100*cr/total if total else 0,
    }

    return {
        "raw": {"input": i, "output": o, "cache_create": cw, "cache_read": cr},
        "snr": snr, "dev10x": dev10x, "op_ratio": op_ratio,
        "velocity": velocity, "leverage": leverage, "efficiency": efficiency,
        "yield": yield_,
        "avg_cost_1m": avg_cost_1m, "cost_usd": cost_usd, "cost_estimated": cost_estimated,
        "cascade_str": cascade_str,
        "transmission": transmission, "commitment": commitment, "reuse": reuse,
        "V": V, "composition": comp, "total": total,
        "non_compounding": cw == 0,
    }

# seed corpus + hardcoded fallback for db.load_operators() (do NOT delete — safety net).
#
# WILD CORPUS SOURCE: the 10 wild operators are public ccusage footprints published
# on the tokscale.ai leaderboard (https://tokscale.ai). Each row is stored as the four
# token pillars (input, output, cache_create, cache_read). Real blended cost for these
# operators is also published on tokscale (kept in Supabase `cost_usd`); the board,
# however, recomputes $/1M at list price (~) for ALL corpus rows for apples-to-apples
# comparison. Real cost only appears on the live ccusage paste path (cost_usd passed in).
# MO§ES is verified ccusage data (not tokscale) and reproduces its real cost ($0.527).
SEED = {
    "MO§ES (ccusage)":          (1_251_211, 11_296_121, 128_196_310, 2_555_179_769),
    # ---- wild corpus (tokscale.ai) — (input, output, cache_create, cache_read) ----
    "vincentkoc":               (10_000, 500, 6_530, 295_500),
    "ben (@cexll)":             (10_000, 9_500, 30, 5_500),
    "MapleEve":                 (1_000, 80, 196, 22_800),
    "Nepomuk5665":              (50_000, 1_200, 500, 15_000),
    "Ólafur Nils Sigurðsson":   (20_500_000, 1_900_000, 1_400_000, 572_400_000),
    "Ivan Golovach":            (17_000_000, 1_300_000, 352, 512_000_000),
    "Feng GAO":                 (26_500_000, 2_000_000, 238, 471_000_000),
    "steve wu":                 (164_100_000, 26_000_000, 170_100, 296_800_000),
    "Max Ghenis":               (16_100_000, 1_100_000, 1_000_000, 358_100_000),
    "Sylvain Tissier":          (8_300_000, 495_200, 111_400, 210_600_000),
}

if __name__ == "__main__":
    for name,(i,o,cw,cr) in SEED.items():
        m = compute(i,o,cw,cr)
        d = f"{m['dev10x']:.2f}" if m['dev10x'] is not None else "—"
        print(f"{name:18} SNR {m['snr']:.3f}  10xDEV {d:>6}  "
              f"vel {m['velocity']:.2f}  lev {m['leverage']:.1f}  "
              f"$/1M {m['avg_cost_1m']:.3f}  Y {m['yield']:.2f}")
