---
title: MO§ES SigRank
emoji: 📡
colorFrom: yellow
colorTo: gray
sdk: gradio
sdk_version: "6.17.3"
app_file: app.py
hf_oauth: true
pinned: false
license: mit
short_description: Rank AI operators by architecture. Volume can't buy rank.
models:
  - openbmb/MiniCPM4-0.5B
tags:
  - thousand-token-wood
  - off-brand
  - tiny-titan
  - best-demo
  - minicpm
  - track:wood
  - sponsor:openbmb
  - sponsor:openai
  - achievement:offgrid
  - achievement:offbrand
  - achievement:sharing
  - achievement:fieldnotes
---

# MO§ES™ SigRank — the diagnostic x-ray of the token economy

A leaderboard that judges AI coding operators by **architecture, not budget**.
Paste your token usage; get an operator profile with a tiny-model narration and
your rank. The ranking metric **Υ = (Cache·Output)/Input²** penalizes raw-input
padding quadratically — volume can't buy rank — but Υ is only the headline of a
larger metric system whose mathematical thesis is the **cascade decomposition**.

**GitHub:** [github.com/SunrisesIllNeverSee](https://github.com/SunrisesIllNeverSee) · **Repo:** [SunrisesIllNeverSee/moses-sigrank](https://github.com/SunrisesIllNeverSee/moses-sigrank) · **Deck:** [mos2es.com/deck](https://mos2es.com/deck) · **Benchmarks:** [mos2es.com/benchmarks](https://mos2es.com/benchmarks)

---

> **SigRank is Layer 2 of the MO§ES™ stack** (SIGRANK: human–AI operator intelligence).
> MO§ES™ is the substrate — compression, recursive execution, drift control, governed meaning at source.
> Built by [Deric J. McHenry](https://github.com/SunrisesIllNeverSee) · Ello Cello LLC.
>
> **IP:** 4 patent filings · IC 042 trademark · [Conservation Law of Commitment — Zenodo DOI 10.5281/zenodo.18792459](https://zenodo.org/records/20029607)

---

## Origin & Theory

SigRank is grounded in a published law: **the Conservation Law of Commitment**.

> **C(T(S)) ≈ C(S)** — Commitment is conserved when enforcement holds.
> If the meaning of a signal is preserved across transformations, the architecture is sound.
> If it drifts, the architecture is leaking.
> [Formal proof — Zenodo DOI 10.5281/zenodo.18792459 →](https://zenodo.org/records/20029607)

When token-level data became available via ccusage, the word-based commitment framework
translated directly into token-domain measurement:

- commitment → `cache_create / output`
- reuse → `cache_read / cache_create`
- transmission → `output / input`

The cascade identity `(O/I) × (C_w/O) × (C_r/C_w) = C_r/I` is the token-domain expression
of the same conservation law. **Operators who conserve commitment compound. Operators who don't, pay for it.**

## What it does

Paste `ccusage claude --json` (Claude Code), `ccusage codex --json` (Codex), or four numbers →

- **operator profile** — a 0.5B MiniCPM model narrates your architecture, plus raw ledger, composition, full metrics, cascade breakdown
- **leaderboard placement** vs real operators, ranked by Υ, with blended **$/1M cost**
- **trading card** — species classification, cascade decomposition, composition bar

## How to measure yourself

SigRank is **local-first** — the importer reads your usage on your own machine.

**1 — Primary: the local importer.** Clone it once, then run it (no install step — runs on system Python + [Node.js](https://nodejs.org)):

```
git clone https://github.com/SunrisesIllNeverSee/moses-sigrank
cd moses-sigrank
./sigrank
```

`./sigrank --codex` for Codex · `./sigrank --all` for both providers in one pass.
It runs `ccusage` for you, computes your profile + Υ, and prints your board rank.
**Nothing leaves your machine.**

**2 — Backup: paste on the Space.** No repo? Run `ccusage` yourself and paste the JSON
into the **Clock Your Signal** box. Run **one command per provider**:

```
npx ccusage@latest claude --json
```
```
npx ccusage@latest codex --json
```

(ccusage installed globally? drop the prefix: `ccusage claude --json`.) Or type four numbers: `input output cache_create cache_read`.

> ⚠️ Don't use bare `ccusage --json` (no subcommand): it merges every agent into one total, which inflates input and distorts the architecture read.

**3 — Saving (optional).** Sign in with HuggingFace on the Space to earn one persistent board entry + session history (Greatest Hits). Without login, your read is a live snapshot only.

**Codex note.** Codex doesn't report a fresh-vs-cache input split, so its input is *estimated*: alone → AA-backed **2:1** baseline; with a Claude profile → your own Claude input:output ratio. Estimated rows flagged with `*`.

## The model (Tiny Titan / Best MiniCPM)

`openbmb/MiniCPM4-0.5B` (0.5B params, well under the 4B cap) runs on ZeroGPU and
narrates the operator read. **Non-blocking**: if unavailable, a deterministic template is used and the app still works. Everything quantitative is pure computation.

## The full metric system

Υ is the *ranking* metric. The *mathematical thesis* is the cascade decomposition
of leverage into three behavioral stages — Υ is what you sort by, the cascade is what explains *why* an operator lands where they do.

### The cascade as a diagnostic

```
(O/I)  ×  (C_w/O)   ×  (C_r/C_w)   =   C_r/I
 │          │            │               │
transmission commitment  compounding   leverage
 generate    commit to   reuse what
 output      cache        was cached
```

`10x DEV` is the **log₁₀** of that product — the amplification exponent. By telescoping, `10^(10x DEV) = leverage = C_r/I`.

### Operator species

| species | signature |
|---|---|
| **Cascade Matrix** | velocity ≥ 1 *and* leverage ≥ 100 · recursive processing loop |
| **Cache Architect** | leverage ≥ 10, velocity < 1 · persistent context layer |
| **Converter Loop** | velocity ≥ 0.5, leverage < 2 · single-pass processing velocity |
| **Throughput Pipe** | low on both axes · raw metric bandwidth |
| **Non-Compounding** | no `cache_create` — cascade can't form |

### Species / quadrants

```
              high amplification
                     │
   CASCADE (stacks)  │   (— rare / empty —)
   low scale ◄───────┼───────► high scale
   CONVERTER (I→O)   │   THROUGHPUT (volume)
   CACHE ARCHITECT   │   (reuse)
                     │
              low amplification
```

MO§ES occupies the **empty quadrant** — low scale, high amplification. The claim is *not* "top of a ladder"; it's that this region of the token economy is structurally empty, and the geometry of `(C·O)/I²` is what makes it empty.

### Full metric table

| metric | formula | meaning |
|---|---|---|
| SNR | O/(I+O) | output share |
| 10x DEV | log₁₀(cascade) | amplification exponent |
| Operating Ratio | C:I:O, input=1 | footprint vs Artificial Analysis 7:2:1 |
| Velocity | O/I | output per input token |
| Leverage | C/I | cache reads per human token |
| Efficiency | (C+O)/I ÷ 4.0 | vs AA baseline |
| Avg $/1M | blended cost ÷ total | efficient architecture is also cheapest |
| **Υ (Yield)** | (C·O)/I² | **un-gameable ranking metric** |

## Benchmark convergence — two independent instruments

### Instrument 1 — Artificial Analysis model benchmarks
AA benchmarks measure *models* at a **7:2:1** (cache : input : output) token mix.
SigRank measures *operators* from their own token logs.
Both converge: **cache-dominant architecture is the most efficient AND cheapest per token.**
The AA 7:2:1 ratio is the source of the **4.0 efficiency baseline**: `(7+1)/2 = 4.0`.

### Instrument 2 — Five measured kernels ([mos2es.com/benchmarks](https://mos2es.com/benchmarks))

MO§ES operator measured against the AA Coding Agent Index field average — 7-day window,
raw JSONL extraction across **98 session files**, all subagents. **#1 in all five categories:**

| kernel | MO§ES™ | field avg | delta |
|---|---|---|---|
| I · Cache hit rate | **94.66%** | 90.68% | +3.98pp · #1 |
| II · Output : Input ratio | **17.9×** | 0.162× | 110× field avg · #1 |
| III · Tokens per task | **810K** | 4.67M | 5.8× fewer · #1 |
| IV · Time per task | **1.84 min** | 11.92 min | 6.5× faster · #1 |
| V · Cost per LOC | **$0.0007** | $0.067 | 96× cheaper · #1 |

Raw token ledger (98 sessions · 1,123B total):

| | Input | Output | Cache Create | Cache Read | Total | Sessions | LOC |
|---|---|---|---|---|---|---|---|
| MO§ES™ | 123K | 3.90M | 34.83M | 1.084B | 1.123B | 98 / 1,465 tasks | 35,242 |
| Field avg (per model) | 162.9M | 17.2M | — | 1.49B | 1.67B | 1 / 358 tasks | 7,160 |

> Field data: [artificialanalysis.ai/agents/coding-agents](https://artificialanalysis.ai/agents/coding-agents) · extracted 2026-05-14.
> MO§ES: sustained product build, 7-day window (2026-05-08 → 2026-05-14).
> The convergence of #1 leadership across both isolated benchmark runs and sustained product builds is the structural result.

**This is the real-world grounding behind SigRank's thesis** — the same operator that ranks #1 on Υ also ranks #1 on every external benchmark kernel.

## IP & legal record

SigRank is Phase 2 of a fully filed, commercially structured IP portfolio:

| filing | serial | date | protected layer |
|---|---|---|---|
| PPA 01 · MOS²ES | 63/877,177 | Sep 7, 2025 · Conf. 7067 | Constitutional governance, signal encoding, compression substrate |
| PPA 02 · SCS Engine | 63/883,018 | Sep 17, 2025 · Conf. 6401 | Signal Compression System Engine, lineage, sovereign compression |
| Utility 03 · CIVITAS | 19/426,028 | Dec 18, 2025 · Conf. 2165 | Frontend civic infrastructure: SIGRANK, SigEconomy, Agent City-State |
| PPA 04 · Commitment Conservation | 63/991,282 | Feb 26, 2026 · Conf. 6108 | Semantic commitment conservation under recursive transformation |
| MO§ES™ Trademark | 99408355 · IC 042 | Sep 23, 2025 | Software / governance protocol identity |

**Published law:** Conservation Law of Commitment · [Zenodo DOI 10.5281/zenodo.18792459](https://zenodo.org/records/20029607)

Full legal ledger: [mos2es.com/legal](https://mos2es.com/legal)

## The MO§ES™ stack

SigRank sits at **Layer 2** of a four-layer constitutional architecture:

| layer | product | purpose |
|---|---|---|
| 04 | **SIGNOMY** | Governed agent marketplace — execution-layer governance, participatory trust, agent provenance |
| 03 | **SIGRANK** | Human–AI operator leaderboard — sync telemetry, resonance metrics ← *this app* |
| 02 | **AQUA** | Application workflow — answer banks, reusable submission memory |
| 01 | **MO§ES™** | Substrate — compression, recursive execution, drift control, lineage |

> MO§ES™ IS THE ENGINE · AQUA + SIGRANK ARE THE WEDGES · SIGNOMY IS THE GOVERNED ECONOMY

## Codex support

Codex never itemizes cache writes, so SigRank estimates the high-signal user input from output via two pathways (`_codex_input_estimate` in `ingest.py`):

- **Alpha — Codex alone:** AA-backed **2:1** baseline — `est_input = 2 × output`
- **Beta — Codex + Claude profile:** operator's **own** measured Claude `input:output` ratio — `est_input = output × (claude_input / claude_output)`. CLI builds this automatically (`./sigrank --codex` reads Claude first).

Every Codex-derived row is **flagged with `*`** and names the exact pathway used.

## Cost

For Claude Code, ccusage supplies real cost → exact $/1M. For manual/wild rows, $/1M is a list-price estimate (shown with `~`). Either way: the cache-dominant operator at the top is also the cheapest per token, by an order of magnitude.

## Demo video
[Watch the demo on Loom →](https://www.loom.com/share/edc345e2e5164e20aed3acb6436a08c3)

## Social post
[View on X →](https://x.com/burnmydays/status/2066666214143758576?s=20)

## Notes

- **Persistence boundary.** Pasted rows are scored live but not added to the persisted board — corpus is curated (owner-seeded). Backed by Supabase with hardcoded-seed fallback.
- **Cost provenance.** Board's `$/1M` is a list-price recompute for every corpus row (`~`) so all rows compare apples-to-apples. MO§ES's verified ccusage cost is **$0.527**, reproduced exactly by the recompute.
- **Wild corpus (10 operators).** Public ccusage footprints from [tokscale.ai](https://tokscale.ai). MO§ES is verified ccusage data, not tokscale.
- Υ is an engineered macro-efficiency index motivated by thermodynamics (Landauer, Ohmic dissipation); log Υ = X + log(Velocity). An analogy, not a microscopic-entropy derivation.

---

Built for the HF/Gradio Build Small Hackathon · Thousand Token Wood 🍄

**Built by [Deric J. McHenry](https://github.com/SunrisesIllNeverSee)** · [github.com/SunrisesIllNeverSee](https://github.com/SunrisesIllNeverSee) · Ello Cello LLC · Codex + Claude + Devin

Patent pending 19/426,028 · IC 042 TM 99408355 · DOI [10.5281/zenodo.18792459](https://zenodo.org/records/20029607)
