"""
MO§ES SigRank — HF/Gradio Build Small Hackathon.
Operator pastes ccusage/codex output -> ingestion -> full profile + board placement.
Board ranks by Net Volumetric Yield (Υ). Four raw integers drive everything.
"""
import gradio as gr
import html as _html
import math as _math
import re as _re
from datetime import datetime, timezone
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
# column label -> metrics key, used by the "Rank by" control on the board
SORT_LABELS = {"Υ yield": "yield", "SNR": "snr", "10x DEV": "dev10x",
               "velocity": "velocity", "leverage": "leverage", "$/1M": "avg_cost_1m"}

def board_html(extra=None, sort_key="yield"):
    ops = operators()
    # dedup: if `extra` is already persisted, replace it so it shows once + highlighted
    rows=[(n,compute(*v)) for n,v in ops.items() if not (extra and n==extra[0])]
    if extra: rows.append(extra)
    ymax=max((m["yield"] for _,m in rows), default=1) or 1   # Υ bar always scales to Υ
    asc = sort_key == "avg_cost_1m"                          # cheapest leads for cost
    rows.sort(key=lambda r:(r[1].get(sort_key) if r[1].get(sort_key) is not None
                            else float("-inf")), reverse=not asc)
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
        rkey = rarity_class(m)[0]
        if you:
            cls = f"mb-row rarity-{rkey} you"
        elif i == 1:
            cls = f"mb-row rarity-{rkey} rank1"
        else:
            cls = f"mb-row rarity-{rkey}"
        ne = _html.escape(n)
        est_mark = " <span class='mb-est' title='* structural estimation'>*</span>" if m.get("cost_estimated") else ""
        out.append(f'<div class="{cls}">'
            f'<span class="mb-rank {rank_cls}">{i}</span>'
            f'<span class="mb-op"><b>{ne}{est_mark}</b><br><span class="mb-raw">R {_fmt_int(m["raw"]["cache_read"])} \u00b7 C {_fmt_int(m["raw"]["cache_create"])} \u00b7 I {_fmt_int(m["raw"]["input"])} \u00b7 O {_fmt_int(m["raw"]["output"])}</span></span>'
            f'<span class="mb-num">{m["snr"]:.3f}</span>'
            f'<span class="mb-num">{d}</span>'
            f'<span class="mb-num">{m["velocity"]:.2f}</span>'
            f'<span class="mb-num">{m["leverage"]:,.0f}\u00d7</span>'
            f'<span class="mb-num">{_cost_str(m)}</span>'
            f'<span class="mb-y"><span class="mb-bar" style="width:{barpct:.0f}%"></span>'
            f'<span class="mb-yval">{y:,.0f}</span></span>'
            f'</div>')
    out.append('</div>')
    out.append('<div class="mb-foot">\u03a5 bar is log-scaled \u00b7 MO\u00a7ES leads the field by ~4 orders of magnitude \u00b7 $/1M blended cost (~ = list-price estimate) \u00b7 * = structural estimation \u00b7 volume can\'t buy rank</div>')
    return "".join(out)

# ---------- profile ----------
def classify(m):
    if m["non_compounding"]: return "Non-Compounding \u00b7 stateless pipe"
    v,l=m["velocity"],m["leverage"]
    if v>=1 and l>=100: return "Closed-Loop Kinetic \u00b7 holds both axes"
    if l>=10 and v<1:   return "Archival Sponge \u00b7 high reuse, low generation"
    if v>=0.8 and l<2:  return "Volatile Ingestor \u00b7 generates, doesn't retain"
    return "Transient \u00b7 low on both axes"

def rarity_class(m):
    """Returns (rarity_key, label, passive, effect).
    MYTHIC > EPIC > RARE > COMMON based on velocity/leverage axes.
    Mirrors the user's trading-card design: four species of greatness.
    """
    v, l = m["velocity"], m["leverage"]
    if v >= 1 and l >= 100:
        return ("mythic", "MYTHIC",
                "Compound Interest",
                "Multipliers stack. Transmission \u00d7 Commitment \u00d7 Reuse = Leverage. "
                "The rare operator the leverage/generation tradeoff says shouldn\u2019t exist.")
    if l >= 10 and v < 1:
        return ("epic", "EPIC",
                "Persistent Memory",
                "Builds reusable structures. Each cache write is read many times. "
                "Holds context beautifully \u2014 the architecture compounds without the velocity.")
    if v >= 0.5:
        return ("rare", "RARE",
                "Direct Production",
                "Strong input-to-output conversion. Fast on single shots. "
                "Memory doesn\u2019t persist into a compounding loop.")
    return ("common", "COMMON",
            "Mass Transit",
            "Moves enormous token mass. Volume is the strategy. "
            "Amplification is not the goal \u2014 scale is.")

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
    rkey, rlabel, passive, effect = rarity_class(m)
    c = m["composition"]
    parsing_mode = m.get("_parsing_mode", "")
    mode_badge = (f'<div class="sig-card-mode">* {_html.escape(parsing_mode)}</div>'
                  if parsing_mode else "")
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
        f'<div class="sig-card rarity-{rkey}">'
        '<div class="sig-card-watermark">MO\u00a7ES\u2122 SIGRANK</div>'
        f'<div class="sig-card-rarity rarity-{rkey}">{rlabel}</div>'
        f'<div class="sig-card-name">{name}</div>'
        f'<div class="sig-card-archetype">{archetype}</div>'
        f'<div class="sig-card-passive">Passive: {passive}</div>'
        f'<div class="sig-card-effect">{effect}</div>'
        f'{mode_badge}'
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
    mode = m.get("_parsing_mode")
    mode_line = f"\n\n`* {mode}`" if mode else ""
    return f"""## OPERATOR \u00b7 {name}
ranked **#{rank}** of {total_ops} by \u03a5{cav_line}{mode_line}

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

**cascade** \u2014 {m['cascade_str']} (transmission \u00d7 commitment \u00d7 reuse)
**scale V** \u2014 {m['V']:.2f}
"""

def _greatest_hits_html(name):
    """Render top sessions for this operator from session history."""
    history = db.load_session_history(name, limit=5)
    if not history:
        return ""
    rows = []
    for h in history:
        i = int(h.get("input", 0) or 0)
        o = int(h.get("output", 0) or 0)
        cw = int(h.get("cache_create", 0) or 0)
        cr = int(h.get("cache_read", 0) or 0)
        m = compute(i, o, cw, cr)
        ts = h.get("submitted_at", "")
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                ts = dt.strftime("%Y-%m-%d %H:%M UTC")
            except (ValueError, TypeError):
                pass
        src = h.get("source", "")
        rows.append(
            f'<tr><td>{ts}</td><td>{_fmt_int(m["yield"])}</td>'
            f'<td>{m["velocity"]:.2f}\u00d7</td><td>{m["leverage"]:,.0f}\u00d7</td>'
            f'<td>{src}</td></tr>'
        )
    return (
        '<div class="greatest-hits">'
        '<h4>Greatest Hits</h4>'
        '<table><thead><tr><th>when</th><th>\u03a5</th><th>vel</th><th>lev</th><th>source</th></tr></thead>'
        '<tbody>' + "".join(rows) + '</tbody></table>'
        '</div>'
    )

# ---------- ingestion handler ----------
def run_ingest(blob, name, request: gr.Request):
    hf_user = None
    if request:
        hf_user = getattr(request, "username", None)
    name=(name or "you").strip()[:24] or "you"
    try:
        i,o,cw,cr,meta = ingest_meta(blob or "")
    except Exception as e:
        return ("Paste your `ccusage claude --json` output, your "
                "`ccusage codex --json` output, or `ccusage --json` "
                "for all providers. You can also paste four numbers: "
                "input output cache_create cache_read.\n\n"
                f"_parser said: {e}_"), "", "", "", board_html()
    if i+o+cw+cr==0:
        return "Got zeros \u2014 check your paste.", "", "", "", board_html()
    m=compute(i,o,cw,cr, cost_usd=meta.get("cost"))
    if meta.get("estimated"):
        m["_caveat"]=meta.get("caveat")
    if meta.get("parsing_mode"):
        m["_parsing_mode"] = meta["parsing_mode"]
    # persist only if HF-authenticated + writes configured
    saved=False
    if hf_user and db.writes_enabled():
        saved=db.save_operator(name,i,o,cw,cr, cost=meta.get("cost"),
                               source=meta.get("source","manual"),
                               estimated=bool(meta.get("estimated")),
                               caveat=meta.get("caveat"),
                               hf_user=hf_user)
    base=operators(force=saved)
    rows=[(nn,compute(*vv)) for nn,vv in base.items() if nn!=name]+[(name,m)]
    rows.sort(key=lambda r:r[1]['yield'],reverse=True)
    rank=next(idx for idx,(nn,_) in enumerate(rows,1) if nn==name)
    read = narrate(name, m, classify(m))

    save_note = ""
    if not hf_user:
        save_note = "\n\n*\u26a0 Sign in with HuggingFace to save your entry to the board. Paste-only results are a snapshot \u2014 not persisted.*"
    elif saved:
        save_note = f"\n\n*Saved to the board as **{_html.escape(name)}** at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}.*"

    hits_html = _greatest_hits_html(name) if hf_user else ""
    profile = profile_md(name,m,rank,len(rows),read) + save_note

    return (profile,
            comp_bar_html(m["composition"]),
            card_html(name,m,rank,len(rows),read),
            hits_html,
            board_html((name,m)))

# ---------- interactive leaderboard helpers ----------
def resort_board(label):
    """Re-render the board sorted by the chosen column (the 'Rank by' control)."""
    return board_html(sort_key=SORT_LABELS.get(label, "yield"))

def view_operator(name):
    """Render a corpus operator's full profile + share card (the 'open a profile' picker)."""
    ops = operators()
    if not name or name not in ops:
        return "", ""
    m = compute(*ops[name])
    rows = sorted(((n, compute(*v)) for n, v in ops.items()),
                  key=lambda r: r[1]["yield"], reverse=True)
    rank = next(i for i, (n, _) in enumerate(rows, 1) if n == name)
    read = narrate(name, m, classify(m))
    return profile_md(name, m, rank, len(rows), read), card_html(name, m, rank, len(rows), read)

# ---------- UI ----------
import os as _os
_ON_SPACE = bool(_os.environ.get("SPACE_ID"))

# Ghost/"unminted" card so the right column is never an empty void on first load.
CARD_PLACEHOLDER = (
    '<div class="sig-card rarity-common" id="ghost-card">'
    '<div class="sig-card-watermark">MO§ES™ SIGRANK</div>'
    '<div class="sig-card-rarity rarity-common">UNMINTED</div>'
    '<div class="sig-card-name">Awaiting Operator…</div>'
    '<div class="sig-card-archetype">Signal Offline</div>'
    '<div class="sig-card-yield">0,000</div>'
    '<div class="sig-card-yield-label">insert token ledger to scan</div>'
    '</div>'
)

def _build_demo():
    _blocks_kw = {"title": "MO\u00a7ES SigRank"}
    _b = gr.Blocks(**_blocks_kw)
    # dynamic hero stats (don't hardcode counts that drift when the corpus changes)
    _ops_now = operators()
    _names = list(_ops_now.keys())
    _ys = sorted((compute(*v)["yield"] for v in _ops_now.values()), reverse=True)
    _lead = (_ys[0] / _ys[1]) if len(_ys) > 1 and _ys[1] > 0 else 0.0
    with _b:
        with gr.Column(elem_id="moses-hero"):
            gr.HTML("<h1>MO\u00a7ES\u2122 SigRank</h1>"
                    "<p>The diagnostic x-ray of the token economy // ranked by \u03a5 (Net Volumetric Yield) // volume can't buy rank</p>")
            gr.HTML('<div id="moses-stat-strip">'
                    f'<div>OPERATORS RANKED <span>{len(_ops_now)}</span></div>'
                    f'<div>MO\u00a7ES LEADS BY <span>{_lead:,.0f}\u00d7</span></div>'
                    '<div>ARCHITECTURE BEATS BUDGET</div>'
                    '</div>')
            gr.HTML('<div id="moses-footprint">compute footprint \u00b7 0.5B params (MiniCPM4-0.5B) \u00b7 '
                    'non-blocking deterministic fallback \u00b7 ZeroGPU \u00b7 \u03a5 = (Cache\u00b7Output)/Input\u00b2</div>')

        # ---- TAB 1: Leaderboard (board + sticky profile inspector) ----
        with gr.Tab("Leaderboard"):
            gr.Markdown("Ranked by **\u03a5 = (Cache\u00b7Output)/Input\u00b2**. Raw Read\u00b7Create\u00b7In\u00b7Out stacked under each operator. $/1M is blended cost \u2014 efficient architecture is also the cheapest.")
            with gr.Row():
                with gr.Column(scale=7):
                    rank_by = gr.Radio(list(SORT_LABELS.keys()), value="\u03a5 yield",
                                       label="Rank by", elem_id="rank-by")
                    lb = gr.HTML(board_html())
                    rank_by.change(resort_board, rank_by, lb)
                    gr.Markdown("*Curated corpus \u00b7 pasting scores you live but isn't persisted unless you sign in \u00b7 $/1M is a list-price recompute (~) \u00b7 \\* = structural estimation.*", elem_id="moses-foot")
                with gr.Column(scale=5):
                    gr.Markdown("### Operator profile inspector")
                    op_pick = gr.Dropdown(_names, label="Select an operator to pull their card",
                                          value=None, elem_id="op-pick")
                    op_card = gr.HTML(CARD_PLACEHOLDER)
                    op_prof = gr.Markdown(elem_id="moses-profile")
                    op_pick.change(view_operator, op_pick, [op_prof, op_card])

        # ---- TAB 2: Clock Your Signal (primary importer up top, then ingest + card) ----
        with gr.Tab("Clock Your Signal"):
            gr.Markdown("### Primary path \u2014 run the local importer")
            gr.Markdown("Reads your usage on your own machine. **Nothing leaves your computer.** Clone it once, then run:")
            gr.Code(value="git clone https://github.com/Burnmydays/hf-\ncd hf-\n./sigrank",
                    language="shell", show_label=False, elem_id="clone-code")
            with gr.Accordion("More options \u2014 Codex, all providers, or paste instead", open=False):
                gr.Markdown("""`./sigrank --codex` reads Codex usage \u00b7 `./sigrank --all` runs every provider in turn.

**No terminal? Paste instead (the backup).** Run one of these, copy the JSON, drop it in the box below:
```
npx ccusage@latest claude --json
```
```
npx ccusage@latest codex --json
```
\u26a0\ufe0f Run Claude and Codex **separately** \u2014 never bare `ccusage --json` (it merges every agent and distorts the read). No JSON? Type four numbers: `input output cache_create cache_read`.

*Codex input is estimated (\\*): alone \u2192 AA 2:1 baseline; with a Claude profile \u2192 your own Claude input:output ratio.*""")
            gr.HTML("<hr style='border:0;border-top:1px solid var(--moses-line);margin:18px 0;'>")
            with gr.Row():
                with gr.Column(scale=5):
                    gr.Markdown("### Ingest a signal")
                    if _ON_SPACE:
                        gr.LoginButton(elem_id="hf-login-btn")
                    else:
                        gr.Markdown("*HuggingFace login available on the hosted Space \u2014 local mode is transient.*", elem_id="moses-foot")
                    nm = gr.Textbox(label="operator name / handle", placeholder="your handle", max_lines=1)
                    blob = gr.Textbox(label="ccusage JSON \u2014or\u2014 four numbers (I O C R)", lines=5,
                                      placeholder='Paste ccusage JSON here\n\nor four numbers: input output cache_create cache_read\n\nExample: 1251211 11296121 128196310 2555179769')
                    go = gr.Button("Clock My Signal", variant="primary", elem_id="compute-btn")
                    gr.Markdown("### Your live board placement")
                    ob = gr.HTML(board_html())
                    gr.Markdown("### Greatest hits")
                    hits = gr.HTML()
                with gr.Column(scale=6):
                    gr.Markdown("### Minted operator card")
                    card = gr.HTML(CARD_PLACEHOLDER)
                    gr.Markdown("*Right-click \u2192 Save image to share your architectural footprint.*", elem_id="moses-foot")
                    prof_bar = gr.HTML()
                    prof = gr.Markdown(elem_id="moses-profile")
            go.click(run_ingest, [blob, nm], [prof, prof_bar, card, hits, ob])
            gr.Examples(
                examples=[
                    ['{"totals":{"inputTokens":1251211,"outputTokens":11296121,"cacheCreationTokens":128196310,"cacheReadTokens":2555179769}}','MO\u00a7ES'],
                    ['{"data":[{"inputTokens":58920000,"cachedInputTokens":707300000,"outputTokens":3500000,"reasoningOutputTokens":510000}]}','codex-operator'],
                    ['1251211 11296121 128196310 2555179769', 'manual-paste'],
                ],
                inputs=[blob, nm])

        gr.Markdown(elem_id="moses-foot", value="""Four integers in, full ledger out. Architecture is the only variable that matters.
Wild corpus: tokscale.ai footprints \u00b7 MO\u00a7ES row verified ccusage \u00b7 * = structural estimation.""")
    return _b

demo = _build_demo()

if __name__ == "__main__":
    demo.launch(css=CSS, theme=gr.themes.Base())
