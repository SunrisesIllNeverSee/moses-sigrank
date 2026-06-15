# REVIEW — what changed this session, for your eyes

> Quick review file. Delete after you've read it.

---

## What the numbers look like now

```
=== CLAUDE (./sigrank) ===
source: ccusage claude
ledger   R 2.65B · C 136.21M · I 2.90M · O 12.32M
SNR       0.810
10x DEV   2.96
velocity  4.25×
leverage  914×
$/1M      $0.715
Υ yield   3,886
class     Closed-Loop Kinetic · holds both axes
rank      #2 of 8

=== CODEX (./sigrank --codex) ===
source: ccusage codex
⚠ estimated via turn-delta (cache_create from daily context growth)
ledger   R 707.30M · C 26.17M · I 58.92M · O 4.01M
SNR       0.064
10x DEV   1.08
velocity  0.07×
leverage  12×
$/1M      $0.561
Υ yield   1
class     Archival Sponge · high reuse, low generation
rank      #5 of 8
```

---

## Problem being solved

`ccusage --json` combines Claude + Codex + every other agent into one total.
When combined, Codex's large `inputTokens` (58.9M) tanked Υ quadratically.
Fix: run them separately — `ccusage claude --json` and `ccusage codex --json`.

---

## What was wrong with Codex before (and the fix)

**Bug 1 — detection miss (already fixed earlier):**  
`is_codex_shape()` checked for `cached_input_tokens` (snake_case) but
`ccusage codex --json` emits `cachedInputTokens` (camelCase). Codex JSON
fell through to `parse_ccusage` — no split, no cache, raw 58.9M input.
Fix: check both cases.

**Bug 2 — anchor now uses turn-delta (CODEX.md item 1):**  
Old: `est_fresh = 2 * output` (fixed 2:1).  
New: with daily granularity present (we have 29 days of data), estimates
`cache_create` from per-day context growth deltas instead.  
Fallback: if no daily data, uses Claude's measured I/O ratio (0.236:1)
instead of fixed 2:1 — grounded in your real data, not a constant.

---

## What the Codex numbers mean

| field | value | source |
|---|---|---|
| input (I) | 58.92M | `inputTokens` — fresh input directly from Codex JSON |
| output (O) | 4.01M | `outputTokens` + `reasoningOutputTokens` |
| cache_create (C) | 26.17M | **estimated** via turn-delta |
| cache_read (R) | 707.30M | `cachedInputTokens` — measured directly |
| cost | real ($0.561/1M) | from `costUSD` in the JSON |

The 707.3M cache reads are real and measured. Codex is reading a LOT of
cached context. It just generates very little output relative to input
(velocity 0.07×), so Υ is low. That's Codex's architecture, not a bug.

---

## Board marker (CODEX.md item 4)

Estimated rows (Codex-anchored) now show a `~` next to the operator name
in the leaderboard. Measured rows (real ccusage) show clean.

---

## What is NOT right (open questions for you)

1. **Codex `inputTokens` interpretation** — the turn-delta treats `inputTokens`
   as already-fresh (not combined with reads). If OpenAI actually reports
   combined fresh+cached in that field, the I value (58.92M) is too high
   and Υ will be artificially low. Do you know which it is?

2. **Υ=1 for Codex** — with 58.9M fresh input and only 4M output, Υ is
   nearly 0. That may be correct (Codex is a heavy reader, light generator)
   or it may mean `inputTokens` is the combined figure and needs splitting.

3. **CODEX.md items 2 + 3 still open:**
   - Item 2: `test_metrics.py` (pytest for canonical numbers)
   - Item 3: self-cost via OpenAI per-1M pricing table in `parse_codex`
     (cost already comes through from `costUSD`, so this may be done?)

---

## Files changed this session

| file | what changed |
|---|---|
| `ingest.py` | `is_codex_shape` → camelCase fix; `parse_codex` → turn-delta + io_ratio param; `ingest_meta` → io_ratio passthrough |
| `sigrank.py` | default changed to `ccusage claude --json`; `--codex` path fetches Claude ratio first |
| `app.py` | `html.escape(name)` XSS fix; `~` marker on estimated board rows |
