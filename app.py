"""
MO§ES SigRank — HF/Gradio Build Small Hackathon.
Operator pastes ccusage/codex output -> ingestion -> full profile + board placement.
Board ranks by Net Volumetric Yield (Υ). Four raw integers drive everything.
"""
import gradio as gr
import math as _math
import re as _re
from metrics import compute, SEED
from ingest import ingest_meta
from theme import CSS
import db
try:
    from narrate import narrate
except Exception:
    def narrate(name, m, klass): return f"**{klass}.**"

# ---------- operator corpus (Supabase if configured, else SEED) ----------
_OPS = None
def operators(force=False):
    """Cached board corpus. Reads from Supabase via db.load_operators() (which
    itself falls back to metrics.SEED if persistence is unconfigured/down).
    Cached so a page render isn't one REST call per board; force=True refreshes
    after a write so a newly-persisted row shows immediately."""
    global _OPS
    if _OPS is None or force:
        _OPS = db.load_operators()
    return _OPS

def _fmt_int(n):
    for u,d in (("T",1e12),("B",1e9),("M",1e6),("K",1e3)):
        if abs(n)>=d: return f"{n/d:.2f}{u}"
    return str(int(n))

def _cost_str(m):
    c = m.get("avg_cost_1m")
    if not c: return "\u2014"
    mark = "~" if m.get("cost_estimated") else ""
    return f"{mark}${c:.2f}"

# ---------- leaderboard (HTML hero, log-scaled Υ, cost column) ----------
def board_html(extra=None):
    ops = operators()
    # dedup: if `extra` is already persisted, replace it so it shows once + highlighted
    rows=[(n,compute(*v)) for n,v in ops.items() if not (extra and n==extra[0])]
    if extra: rows.append(extra)
    rows.sort(key=lambda r:r[1]["yield"], reverse=True)
    ymax=rows[0][1]["yield"] or 1
    out=['<div class="moses-board">']
    out.append('<div class="mb-head"><span class="mb-rank">#</span>'
               '<span class="mb-op">operator</span>'
               '<span class="mb-num">SNR</span><span class="mb-num">10x DEV</span>'
               '<span class="mb-num">velocity</span><span class="mb-num">leverage</span>'
               '<span class="mb-num">$/1M</span>'
               '<span class="mb-y">\u03a5 yield</span></div>')
    for i,(n,m) in enumerate(rows,1):
        y=m["yield"]; you = extra and n==extra[0]
        orders=_math.log10(ymax/y) if y>0 else 99
        barpct=max(2,100*(1-orders/5))
        d=f"{m['dev10x']:.2f}" if m['dev10x'] is not None else "\u2014"
        rank_cls = f"mb-rank-{i}" if i <= 3 else ""
        cls = "mb-row you" if you else ("mb-row rank1" if i==1 else "mb-row")
        out.append(f'<div class="{cls}">'
            f'<span class="mb-rank {rank_cls}">{i}</span>'
            f'<span class="mb-op"><b>{n}</b><br><span class="mb-raw">R {_fmt_int(m["raw"]["cache_read"])} \u00b7 C {_fmt_int(m["raw"]["cache_create"])} \u00b7 I {_fmt_int(m["raw"]["input"])} \u00b7 O {_fmt_int(m["raw"]["output"])}</span></span>'
            f'<span class="mb-num">{m["snr"]:.3f}</span>'
            f'<span class="mb-num">{d}</span>'
            f'<span class="mb-num">{m["velocity"]:.2f}</span>'
            f'<span class="mb-num">{m["leverage"]:,.0f}\u00d7</span>'
            f'<span class="mb-num">{_cost_str(m)}</span>'
            f'<span class="mb-y"><span class="mb-bar" style="width:{barpct:.0f}%"></span>'
            f'<span class="mb-yval">{y:,.0f}</span></span>'
            f'</div>')
    out.append('</div>')
    out.append('<div class="mb-foot">\u03a5 bar is log-scaled \u00b7 MO\u00a7ES leads the field by ~4 orders of magnitude \u00b7 $/1M blended cost (~ = list-price estimate) \u00b7 volume can\'t buy rank</div>')
    return "".join(out)

# ---------- profile ----------
def classify(m):
    if m["non_compounding"]: return "Non-Compounding \u00b7 stateless pipe"
    v,l=m["velocity"],m["leverage"]
    if v>=1 and l>=100: return "Closed-Loop Kinetic \u00b7 holds both axes"
    if l>=10 and v<1:   return "Archival Sponge \u00b7 high reuse, low generation"
    if v>=0.8 and l<2:  return "Volatile Ingestor \u00b7 generates, doesn't retain"
    return "Transient \u00b7 low on both axes"

def comp_bar_html(c):
    return (f'<div class="comp-bar">'
            f'<div class="comp-read" style="width:{c["read"]:.1f}%"></div>'
            f'<div class="comp-create" style="width:{c["create"]:.1f}%"></div>'
            f'<div class="comp-output" style="width:{c["output"]:.1f}%"></div>'
            f'<div class="comp-input" style="width:{c["input"]:.3f}%"></div>'
            f'</div>'
            f'<div style="font-size:10px;color:#8a7f68;margin-bottom:8px">'
            f'read {c["read"]:.1f}% \u00b7 create {c["create"]:.1f}% \u00b7 output {c["output"]:.1f}% \u00b7 input {c["input"]:.3f}%'
            f'</div>')

def _first_sentence(text, limit=120):
    t = _re.sub(r"[*_`>#]", "", text or "").replace("\n", " ").strip()
    parts = _re.split(r"(?<=[.!?])\s", t, maxsplit=1)
    s = parts[0] if parts else t
    if len(s) > limit:
        s = s[:limit].rstrip() + "\u2026"
    return s

def card_html(name, m, rank, total_ops, narration_text):
    archetype = classify(m).split("\u00b7")[0].strip()
    c = m["composition"]
    if m["transmission"] is not None:
        cascade = (
            f'<div class="sig-card-cascade-box">{m["transmission"]:.1f}\u00d7<small>trans</small></div>'
            f'<span class="sig-card-cascade-arrow">\u2192</span>'
            f'<div class="sig-card-cascade-box">{m["commitment"]:.1f}\u00d7<small>commit</small></div>'
            f'<span class="sig-card-cascade-arrow">\u2192</span>'
            f'<div class="sig-card-cascade-box">{m["reuse"]:.1f}\u00d7<small>reuse</small></div>'
            f'<span class="sig-card-cascade-arrow">=</span>'
            f'<div class="sig-card-cascade-box">{m["leverage"]:,.0f}\u00d7<small>leverage</small></div>'
        )
    else:
        cascade = '<div class="sig-card-cascade-box">\u2014<small>non-compounding</small></div>'
    quote = _first_sentence(narration_text)
    return (
        '<div class="sig-card">'
        '<div class="sig-card-watermark">MO\u00a7ES\u2122 SIGRANK</div>'
        f'<div class="sig-card-name">{name}</div>'
        f'<div class="sig-card-archetype">{archetype}</div>'
        f'<div class="sig-card-yield">{m["yield"]:,.0f}</div>'
        '<div class="sig-card-yield-label">net volumetric yield</div>'
        f'<div class="sig-card-rank">#<span>{rank}</span> of {total_ops} operators</div>'
        f'<div class="sig-card-cascade">{cascade}</div>'
        f'{comp_bar_html(c)}'
        f'<div class="sig-card-quote">{quote}</div>'
        '<div class="sig-card-footer"><span>sigrank.hf.space</span><span>\u03a5=(C\u00b7O)/I\u00b2</span></div>'
        '</div>'
    )

def profile_md(name, m, rank, total_ops, read=None):
    c=m["composition"]; r=m["raw"]
    d=f"{m['dev10x']:.3f}" if m['dev10x'] is not None else "\u2014 non-compounding (no cache_create)"
    if read is None:
        read = narrate(name, m, classify(m))
    cav = m.get("_caveat")
    cav_line = f"\n\n`\u26a0 {cav}`" if cav else ""
    cost_note = " (list-price estimate)" if m.get("cost_estimated") else " (from ccusage)"
    return f"""## OPERATOR \u00b7 {name}
ranked **#{rank}** of {total_ops} by \u03a5{cav_line}

> {read}

### raw ledger (the four pillars)
| | tokens |
|---|---|
| input | {r['input']:,} |
| output | {r['output']:,} |
| cache_create | {r['cache_create']:,} |
| cache_read | {r['cache_read']:,} |
| **total** | **{m['total']:,}** |

### board metrics
| metric | value | |
|---|---|---|
| SNR | {m['snr']:.3f} | output share |
| 10x DEV | {d} | amplification exponent |
| Operating Ratio | {m['op_ratio']} | vs AA 7:2:1 |
| Velocity | {m['velocity']:.3f}\u00d7 | output per input |
| Leverage | {m['leverage']:,.1f}\u00d7 | reads per human token |
| Efficiency | {m['efficiency']:,.1f}\u00d7 | vs AA baseline |
| Avg $/1M | ${m['avg_cost_1m']:.3f} |{cost_note} |
| **\u03a5 Yield** | **{m['yield']:,.2f}** | un-gameable rank |

**cascade** — {m['cascade_str']} (transmission \u00d7 commitment \u00d7 reuse)
**scale V** — {m['V']:.2f}
"""

# ---------- ingestion handler ----------
def run_ingest(blob, name):
    name=(name or "you").strip()[:24] or "you"
    try:
        i,o,cw,cr,meta = ingest_meta(blob or "")
    except Exception as e:
        return ("Paste your `npx ccusage@latest --json` output, your "
                "`ccusage codex --json` output, or four numbers: "
                "input output cache_create cache_read.\n\n"
                f"_parser said: {e}_"), "", "", board_html()
    if i+o+cw+cr==0:
        return "Got zeros — check your paste.", "", "", board_html()
    m=compute(i,o,cw,cr, cost_usd=meta.get("cost"))
    if meta.get("estimated"):
        m["_caveat"]=meta.get("caveat")
    # persist only if writes are configured (curated demo leaves them off -> transient)
    saved=False
    if db.writes_enabled():
        saved=db.save_operator(name,i,o,cw,cr, cost=meta.get("cost"),
                               source=meta.get("source","manual"),
                               estimated=bool(meta.get("estimated")),
                               caveat=meta.get("caveat"))
    base=operators(force=saved)   # refresh cache only if a row was actually written
    rows=[(nn,compute(*vv)) for nn,vv in base.items() if nn!=name]+[(name,m)]
    rows.sort(key=lambda r:r[1]['yield'],reverse=True)
    rank=next(idx for idx,(nn,_) in enumerate(rows,1) if nn==name)
    read = narrate(name, m, classify(m))
    return (profile_md(name,m,rank,len(rows),read),
            comp_bar_html(m["composition"]),
            card_html(name,m,rank,len(rows),read),
            board_html((name,m)))

# ---------- UI ----------
_blocks_kw = {"title": "MO\u00a7ES SigRank"}
try:
    _b = gr.Blocks(css=CSS, theme=gr.themes.Base(), **_blocks_kw)
except TypeError:
    _b = gr.Blocks(**_blocks_kw)
with _b as demo:
    with gr.Column(elem_id="moses-hero"):
        gr.HTML("<h1>MO§ES\u2122 SigRank</h1>"
                "<p>the diagnostic x-ray of the token economy \u00b7 ranked by \u03a5 (Net Volumetric Yield) \u00b7 volume can't buy rank</p>")
        gr.HTML('<div id="moses-stat-strip">'
                '<div>operators ranked <span>7</span></div>'
                '<div>MO§ES leads by <span>3,141\u00d7</span></div>'
                '<div>architecture beats budget</div>'
                '</div>')

    with gr.Tab("Leaderboard"):
        gr.Markdown("Ranked by **Υ = (Cache·Output)/Input²**. Raw Read·Create·In·Out stacked under each operator. $/1M is blended cost — efficient architecture is also the cheapest.")
        gr.Markdown("*Corpus is curated — pasting your usage scores you live against the field but doesn't add you to the persisted board. $/1M is a list-price recompute (~); real cost shows when you paste your own ccusage.*", elem_id="moses-foot")
        lb = gr.HTML(board_html())

    with gr.Tab("Measure yourself"):
        gr.Markdown("""**Get your operator profile — automatic, no paste.**

**① Run the local importer** (reads your usage on your machine, 100% local):
```
./sigrank
```
(or `python3 sigrank.py`). It auto-runs `ccusage`, computes your profile + Υ, and prints your board rank. No paste, no upload, no token.

**② Paste — the backup.** No importer handy? Run `npx ccusage@latest --json` (Claude Code) or `ccusage codex --json` (Codex) and drop it below, or just four numbers (input, output, cache_create, cache_read).
*Codex note: combined input is split via the 2:1 field anchor; estimated rows are flagged.*""")
        nm = gr.Textbox(label="operator name", placeholder="your handle", max_lines=1)
        blob = gr.Textbox(label="ccusage / codex JSON  —or—  four numbers", lines=6,
                          placeholder='{"totals":{"inputTokens":...}}   or   1251211 11296121 128196310 2555179769')
        go = gr.Button("Compute my SigRank", variant="primary", elem_id="compute-btn")
        prof = gr.Markdown(elem_id="moses-profile")
        prof_bar = gr.HTML()
        gr.Markdown("### share card")
        card = gr.HTML()
        gr.Markdown("*Screenshot to share \u00b7 right-click \u2192 Save image*", elem_id="moses-foot")
        gr.Markdown("### your placement")
        gr.Markdown("*Live placement against the curated field — your row is transient (not saved to the board).*", elem_id="moses-foot")
        ob = gr.HTML(board_html())
        go.click(run_ingest, [blob, nm], [prof, prof_bar, card, ob])
        gr.Examples(
            examples=[
                ['{"totals":{"inputTokens":1251211,"outputTokens":11296121,"cacheCreationTokens":128196310,"cacheReadTokens":2555179769}}','MO§ES'],
                ['{"data":[{"input_tokens":145809,"cached_input_tokens":112512,"output_tokens":2094,"reasoning_output_tokens":710}]}','codex-operator'],
            ],
            inputs=[blob, nm])

    gr.Markdown(elem_id="moses-foot", value="""Four integers in, full ledger out. 
Architecture is the only variable that matters. 
Wild-corpus values provisional · MO§ES row verified ccusage · [How it works ↗](#)""")

if __name__ == "__main__":
    try:
        demo.launch(css=CSS, theme=gr.themes.Base())
    except TypeError:
        demo.launch()
