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

# ---------- UI ----------
import os as _os
_ON_SPACE = bool(_os.environ.get("SPACE_ID"))

def _build_demo():
    _blocks_kw = {"title": "MO\u00a7ES SigRank"}
    try:
        _b = gr.Blocks(css=CSS, theme=gr.themes.Base(), **_blocks_kw)
    except TypeError:
        _b = gr.Blocks(**_blocks_kw)
    with _b:
        with gr.Column(elem_id="moses-hero"):
            gr.HTML("<h1>MO\u00a7ES\u2122 SigRank</h1>"
                    "<p>the diagnostic x-ray of the token economy \u00b7 ranked by \u03a5 (Net Volumetric Yield) \u00b7 volume can't buy rank</p>")
            gr.HTML('<div id="moses-stat-strip">'
                    '<div>operators ranked <span>7</span></div>'
                    '<div>MO\u00a7ES leads by <span>3,141\u00d7</span></div>'
                    '<div>architecture beats budget</div>'
                    '</div>')

        with gr.Tab("Leaderboard"):
            gr.Markdown("Ranked by **\u03a5 = (Cache\u00b7Output)/Input\u00b2**. Raw Read\u00b7Create\u00b7In\u00b7Out stacked under each operator. $/1M is blended cost \u2014 efficient architecture is also the cheapest.")
            gr.Markdown("*Corpus is curated \u2014 pasting your usage scores you live against the field but doesn't add you to the persisted board unless you're signed in via HuggingFace. $/1M is a list-price recompute (~); real cost shows when you paste your own ccusage. * = structural estimation.*", elem_id="moses-foot")
            gr.HTML(board_html())

        with gr.Tab("Clock Your Signal"):
            gr.Markdown("""**Get your operator profile \u2014 every provider, one command.**

**\u2460 Run ccusage** (reads your local usage \u2014 one command per provider):
```
ccusage claude --json       # Claude Code stats
ccusage codex --json        # Codex stats (estimated *)
ccusage --json              # ALL providers combined
```
Or use the local importer:
```
./sigrank                   # Claude Code (measured)
./sigrank --codex           # Codex (applies field anchor *)
```

**\u2461 Paste the JSON below.** Drop your `ccusage` output \u2014 Claude, Codex, or combined \u2014 and we'll route it automatically. Or paste four numbers: `input output cache_create cache_read`.

*Codex / non-Claude providers: input is calibrated via the 3:2:1 field anchor (or 1:9 if you have a Claude profile). Estimated rows are flagged with \\*.*

**\u2462 Sign in to save.** HuggingFace users get one persistent board entry + session history. Paste without login = snapshot only.""")
            if _ON_SPACE:
                gr.LoginButton(elem_id="hf-login-btn")
            else:
                gr.Markdown("*HuggingFace login available on the hosted Space \u2014 local mode is transient.*", elem_id="moses-foot")
            nm = gr.Textbox(label="operator name", placeholder="your handle", max_lines=1)
            blob = gr.Textbox(label="ccusage JSON (any provider) \u2014or\u2014 four numbers (I O C R)", lines=6,
                              placeholder='Paste ccusage claude/codex/combined --json output here\n\nor four numbers: input output cache_create cache_read\n\nExample: 1251211 11296121 128196310 2555179769')
            go = gr.Button("Clock My Signal", variant="primary", elem_id="compute-btn")
            prof = gr.Markdown(elem_id="moses-profile")
            prof_bar = gr.HTML()
            gr.Markdown("### share card")
            card = gr.HTML()
            gr.Markdown("*Screenshot to share \u00b7 right-click \u2192 Save image*", elem_id="moses-foot")
            gr.Markdown("### greatest hits")
            hits = gr.HTML()
            gr.Markdown("*Top sessions by \u03a5 \u2014 sign in with HuggingFace to track your history.*", elem_id="moses-foot")
            gr.Markdown("### your placement")
            gr.Markdown("*Live placement against the curated field \u2014 sign in to persist your entry.*", elem_id="moses-foot")
            ob = gr.HTML(board_html())
            go.click(run_ingest, [blob, nm], [prof, prof_bar, card, hits, ob])
            gr.Examples(
                examples=[
                    ['{"totals":{"inputTokens":1251211,"outputTokens":11296121,"cacheCreationTokens":128196310,"cacheReadTokens":2555179769}}','MO\u00a7ES'],
                    ['{"data":[{"inputTokens":58920000,"cachedInputTokens":707300000,"outputTokens":3500000,"reasoningOutputTokens":510000}]}','codex-operator'],
                    ['1251211 11296121 128196310 2555179769', 'manual-paste'],
                ],
                inputs=[blob, nm])

        gr.Markdown(elem_id="moses-foot", value="""Four integers in, full ledger out. 
Architecture is the only variable that matters. 
Wild-corpus values provisional \u00b7 MO\u00a7ES row verified ccusage \u00b7 * = structural estimation \u00b7 [How it works \u2197](#)""")
    return _b

demo = _build_demo()

if __name__ == "__main__":
    try:
        demo.launch(css=CSS, theme=gr.themes.Base())
    except TypeError:
        demo.launch()
