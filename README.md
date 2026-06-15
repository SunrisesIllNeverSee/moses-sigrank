---
title: MO§ES SigRank
emoji: 📡
colorFrom: yellow
colorTo: gray
sdk: gradio
sdk_version: "4.44.0"
app_file: app.py
pinned: false
license: mit
models:
  - openbmb/MiniCPM4-0.5B
tags:
  - thousand-token-wood
  - off-brand
  - tiny-titan
  - best-demo
  - minicpm
---

# MO§ES™ SigRank — the diagnostic x-ray of the token economy

A leaderboard that judges AI coding operators by **architecture, not budget**.
Paste your token usage; get an operator profile with a tiny-model narration and
your rank. The ranking metric **Υ = (Cache·Output)/Input²** penalizes raw-input
padding quadratically — volume can't buy rank — but Υ is only the headline of a
larger metric system whose mathematical thesis is the **cascade decomposition**.

## Origin
SigRank grew out of an earlier attempt to rank AI coding operators by *words* —
measuring commitment, output quality, and reuse through language rather than
numbers. That work produced a **conservation law of commitment**: the insight
that compounding architectures leave a measurable signature regardless of the
instrument used to observe them.

When token-level data became available via ccusage, the word-based framework
translated directly: commitment → `cache_create/output`, reuse → `cache_read/cache_create`,
transmission → `output/input`. The cascade identity `(O/I)×(C_w/O)×(C_r/C_w) = C_r/I`
is the token-domain expression of the same conservation law.

*[Full theoretical lineage — placeholder for extended write-up]*

### Academic work & references
<!-- TODO: add links to the word-based ranking / conservation-law write-up,
     any preprints, talks, or external references here. -->
- *[Conservation law of commitment — link placeholder]*
- *[Word-based operator ranking — link placeholder]*

## What it does
Paste `ccusage claude --json` (Claude Code), `ccusage codex --json` (Codex),
or four numbers →
- **operator profile** — a 0.5B MiniCPM model narrates your architecture, plus
  raw ledger, composition, full metrics, cascade breakdown
- **leaderboard placement** vs real operators, ranked by Υ, with blended **$/1M cost**

## How to measure yourself
Three things: **what data, where to get it, where to put it.**

**1 — What / where to get it.** SigRank needs four integers — `input`, `output`,
`cache_create`, `cache_read`. [`ccusage`](https://github.com/ryoppippi/ccusage) reads
them from your local logs. Run **one command per provider** — Claude and Codex are
different operators, so measure them **separately**:

```
ccusage claude --json       # Claude Code
ccusage codex --json        # Codex
```

> ⚠️ Don't use bare `ccusage --json` (no subcommand): it merges every agent into one
> total, which inflates input and distorts the architecture read.

**2 — Where to put it.** Either:

- **Local importer (no paste):** `./sigrank` (Claude), `./sigrank --codex` (Codex),
  or `./sigrank --all` (each provider in turn). Reads your usage on your machine and
  prints your profile + board rank. Nothing leaves your computer.
- **Hosted Space:** paste one provider's JSON into the **Clock Your Signal** box, or type
  the four numbers `input output cache_create cache_read`.

**3 — Saving (optional).** On the Space, sign in with HuggingFace to earn one persistent
board entry + session history (Greatest Hits). Without login, your read is a live
snapshot only — scored against the field but not saved.

**Codex note.** Codex doesn't report a fresh-vs-cache input split, so its input is
*estimated*: on its own it uses the AA-backed **2:1** baseline; if you also have a Claude
profile (e.g. `./sigrank --codex`, which reads your Claude ratio first) it calibrates with
**your own Claude input:output ratio**. Estimated rows are flagged with `*`.

## The model (Tiny Titan / MiniCPM)
`openbmb/MiniCPM4-0.5B` (0.5B params, well under the 4B cap) runs on ZeroGPU and
narrates the operator read. It is **non-blocking**: if unavailable, a deterministic
template is used and the app still works. Everything quantitative is pure computation.

## The full metric system
Υ is the *ranking* metric. The *mathematical thesis* is the cascade decomposition
of leverage into three behavioral stages — Υ is what you sort by, the cascade is
what explains *why* an operator lands where it does.

### The cascade as a diagnostic
Leverage `C_r/I` is not a single number; it factors into three compounding stages:

```
(O/I)  ×  (C_w/O)   ×  (C_r/C_w)   =   C_r/I
 │          │            │               │
transmission commitment  compounding   leverage
 generate    commit to   reuse what
 output      cache        was cached
```

`10x DEV` is the **log₁₀** of that product — the amplification *exponent*. By
telescoping, `10^(10x DEV) = leverage = C_r/I`. The cascade tells you which stage
an operator is winning or losing on, not just the bottom line.

### Operator archetypes (`classify()` in `app.py`)
Velocity (`O/I`) and leverage (`C_r/I`) place each operator in a behavioral class:

| archetype | signature |
|---|---|
| **Closed-Loop Kinetic** | holds both axes — velocity ≥ 1 *and* leverage ≥ 100 |
| **Archival Sponge** | high reuse, low generation — leverage ≥ 10, velocity < 1 |
| **Volatile Ingestor** | generates, doesn't retain — velocity ≥ 0.8, leverage < 2 |
| **Transient** | low on both axes |
| **Non-Compounding** | stateless pipe — no `cache_create`, so the cascade can't form |

### Scale (V) — the volume axis
**V = log₁₀(total tokens)** measures how much volume an operator moves. Scale and
amplification are *independent* axes: a huge operator can have Υ ≈ 0, and a small
one can have high Υ. That independence is what produces the species map below.

### Species / quadrants (`species_cards.md`)
Plot **Scale (V)** against **Amplification (Υ)** and operators sort into four
species by *which term of the math dominates* — not by who is "better":

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

| species | dominant term | signature |
|---|---|---|
| **Throughput** | raw volume | enormous total, Υ≈0 — scale without compounding |
| **Converter** | transmission `O/I` | high velocity, low leverage |
| **Cache Architect** | reuse `C/I` | high leverage, low velocity |
| **Cascade** | all three compound | low scale, high amplification |

MO§ES occupies the **empty quadrant** — low scale, high amplification. The claim
is *not* "top of a ladder"; it's that this region of the token economy is empty,
and the geometry of `(C·O)/I²` is what makes it empty.

## How the numbers work
Four raw integers — `input`, `output`, `cache_create`, `cache_read` — drive all:

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

Cascade (10x DEV) = transmission (O/I) × commitment (Create/O) × compounding
(Read/Create); its log-sum is the exponent. By telescoping, 10^X = Leverage = C/I.

## Benchmark convergence
SigRank's finding is corroborated by a second, independent instrument.

- **Artificial Analysis (AA)** benchmarks measure *models* at a **7:2:1**
  (cache : input : output) token mix.
- **SigRank** measures *operators / users* from their own token logs.
- Both instruments converge on the same result: **cache-dominant architecture is
  the most efficient AND the cheapest per token.**

The AA **7:2:1** ratio is the source of the **4.0 efficiency baseline** used in
the Efficiency metric: `(7 + 1) / 2 = 4.0`. Two independent instruments — model
benchmarks on one side, real user token ledgers on the other — landing on the
same architecture is the validation.

## Codex support
Codex never itemizes cache writes, so SigRank estimates the high-signal user input
from output via two pathways (`_codex_input_estimate` in `ingest.py`):

- **Alpha — Codex alone:** the AA-backed **2:1** baseline — `est_input = 2 × output`.
- **Beta — Codex + a Claude profile:** the operator's **own** measured Claude
  `input:output` ratio — `est_input = output × (claude_input / claude_output)`. The
  CLI builds this automatically (`./sigrank --codex` reads your Claude usage first).

`cache_create` is the remainder (`raw_input − est_input`, clamped ≥0); `cache_read` is
measured directly. Every Codex-derived row is **flagged with `*`** and names the exact
pathway used in its caveat.

## Cost
For Claude Code, ccusage supplies real cost → exact $/1M. For manual/wild rows
without cost data, $/1M is a list-price estimate (shown with ~). Either way the
finding holds: the cache-dominant operator at the top of the board is also the
cheapest per token, by an order of magnitude.

## Demo video
<!-- TODO: paste YouTube/HF link before submission (60-sec script in TODO.md) -->

## Social post
<!-- TODO: paste link to your X/LinkedIn post before submission (draft in TODO.md) -->

## Notes
- **Persistence boundary.** Your pasted row is scored live against the field but
  is *not* added to the persisted board — the leaderboard corpus is curated
  (owner-seeded). The board is backed by Supabase with a hardcoded-seed fallback,
  so it renders identically even if the database is unreachable.
- **Cost provenance.** The board's `$/1M` is a list-price recompute for every
  corpus row (shown with `~`); only the **live ccusage paste** path surfaces real
  blended cost. MO§ES's verified ccusage cost is **$0.527**, which the list-price
  recompute reproduces exactly. The six wild operators have no real cost data.
- Wild-corpus operator values are provisional (public tokscale footprints);
  MO§ES row is verified ccusage data.
- Υ is an engineered macro-efficiency index motivated by thermodynamics
  (Landauer, Ohmic dissipation); log Υ = X + log(Velocity). An analogy, not a
  microscopic-entropy derivation.

Built for the HF/Gradio Build Small Hackathon · Thousand Token Wood 🍄 · MO§ES™ —
SigRank began as a word-based ranking of AI operators and a conservation law of
commitment, then translated into token-domain measurement.
