# SCRATCHPAD — cross-agent coordination

> Living status file. ANY system (Claude session, Codex CLI, human) working in
> this repo: READ THIS FIRST, then update the relevant section when you change
> state. Keep it short. Timestamps in UTC.

Last updated: 2026-06-15 (Claude/Opus session) · Deadline: **2026-06-15 23:59 UTC** (~12h)

---

## ONE-LINE STATE
Build is ~correct and verified green. Two work-streams remain: **(1) semantics
fixes** (honesty/labeling/narrative) and **(2) Supabase persistence**. Nothing
about the core math is in question.

## DO NOT TOUCH (frozen — these are the thesis)
- `metrics.py` SEED numbers — verified this session, canonical.
- The Υ formula `(C·O)/I²` and the telescoping identity `(o/i)(cw/o)(cr/cw)==cr/i`.
- The 2:1 Codex anchor must stay **flagged/provisional** — never a silent strict
  assumption.

## RESERVED FOR CODEX (leave these — they earn the $10k Codex-attribution prize)
Do NOT implement these in a non-Codex session; Codex needs the attributed commits.
See `CODEX.md`. They are:
1. Refine 2:1 anchor → turn-delta method (keep 2:1 as fallback).
2. `test_metrics.py` — lock canonical numbers (Υ 18,437, lev 2042, X 3.31, telescoping).
3. Real Codex `$/1M` via OpenAI per-1M prices in `parse_codex` meta.
4. Board visual marker on estimated (Codex) rows.
> Order from FIXES.md: do Codex commits AFTER the repo/Space is in the
> `build-small-hackathon` org, so attribution lands in the submitted location.

## CANONICAL VERIFY (run after every change)
```
cd /Users/dericmchenry/Desktop/moses-sigrank
.venv/bin/python -c "import py_compile,glob; [py_compile.compile(f,doraise=True) for f in glob.glob('*.py')]"
.venv/bin/python metrics.py        # MO§ES must print: Y 18436.98, lev 2042.2, 10xDEV 3.31, $/1M 0.527
```

---

## WORK LOG (newest first)

### Devin session — 2026-06-15
- [done] GPU FIX — applied `@GPU` decorator to `narrate()` in narrate.py (line 60).
  ZeroGPU needs the inference function decorated or GPU alloc never happens and the
  model silently template-falls-back every call. `_try_load()` intentionally NOT
  decorated. No-op fallback path verified (no torch → template, import OK).
- [done] DEAD-CODE FIX — removed unused `ingest()` from ingest.py (old lines 103-112).
  Only `ingest_meta()` is called (app.py, sigrank.py). `ingest_meta()` unchanged.
- [done] README rewrite — kept YAML front matter + all math/formulas/SEED identical.
  Added Origin (word-based ranking → conservation law of commitment → token domain,
  with academic-links placeholder), "The full metric system" (cascade diagnostic,
  4 archetypes from classify(), Scale V, species/quadrant framing — MO§ES = empty
  quadrant not a ladder), "Benchmark convergence" (AA 7:2:1 → 4.0 baseline = (7+1)/2,
  two-instrument validation). Restructured so Υ is the ranking metric within the
  broader system. Demo/Social placeholders untouched. Footer updated with origin.
- [done] Verify green: compile OK · `python3 metrics.py` → MO§ES Y 18436.98, lev
  2042.2, 10xDEV 3.31, $/1M 0.527 (unchanged).

### Claude/Opus session — 2026-06-15
- [done] Verified baseline green (compile + canonical metrics print correct).
- [done] FIX 6 — confirmed board CSS grid = 8 tracks, matches 8 header cells (theme.py:58). No code change needed; visual eyeball still owner's call.
- [done] FIX 1 — persistence-boundary honesty note added to README (Notes) + app.py Leaderboard tab + "your placement".
- [done] FIX 2 — cost-provenance note added to README (Notes) + metrics.py SEED comment.
- [done] FIX 4 — wrote `species_cards.md` (2×2 Scale×Amplification quadrant, MO§ES = empty quadrant, flavor-text fix, honest reuse≠proof line). Deck-only, not the app.
- [done] Supabase persistence build complete (table + seed + db.py + app wiring). See SUPABASE section.
- [done] Final verify green: compile OK · canonical metrics unchanged (Υ 18436.98) · db.py falls back to SEED with no env (7 ops, save no-op) · app.py imports + run_ingest end-to-end + dedup OK · narrate template fallback confirmed (no torch locally).
- NOTE: pre-existing Gradio 6.0 warning (css/theme moved to launch()) is handled by app.py's try/except on both Blocks() and launch(). Warning, not error.

---

## SUPABASE — persistence build (decision + state)
- Project: **AppFeeder** `betcyfbzsgusaghriptz` · org **MO§ES™** `iwiixslkceolawfcbbhg` · region us-west-1 · pg17 · ACTIVE_HEALTHY.
- Standing rule honored: **NEW TABLE ONLY** (`public.sigrank_operators`). 56 existing tables untouched.
- RLS decision: **(A) curated** — public READ, writes blocked for anon (service key only). Keeps FIX 1 honesty note valid (visitor pastes stay transient). Flip to (B) public-write later only with anti-spam.
- Table status: see WORK LOG / `PERSISTENCE_SPEC.md` STEP 1–2.
- Code: `db.py` (load_operators REST-read + save_operator service-key upsert) with **SEED fallback** safety net — app never breaks if Supabase is down/unconfigured.
- **OWNER ACTION REQUIRED** (cannot be done from here): set HF Space secrets
  (Space settings → Variables and secrets):
  ```
  SUPABASE_URL          = https://betcyfbzsgusaghriptz.supabase.co
  SUPABASE_ANON_KEY     = <anon / publishable key>     # READ
  SUPABASE_SERVICE_KEY  = <service_role key>           # WRITE (only if app writes)
  ```
  Until those are set, the app runs on the hardcoded SEED fallback (still works).

## AUTO-INGEST — sigrank.py (her-style local importer, this session)
- `sigrank.py` = local-first CLI. Auto-runs `ccusage --json` (or `--codex`/`--file`/stdin),
  computes via metrics.py, prints a sleek read + live board rank (db.load_operators → SEED fallback).
- No paste, no token, 100% local. The hosted Space paste box stays as the backup.
- `--push` is NOT yet implemented (would need service key); local read+compute only for now.
- Verified: compile OK; file/stdin/4-number paths produce correct profile (MO§ES Υ 18,437).

## BLOCKED ON OWNER (not code)
- FIX 3 — tokscale "MCH (tokscale read)" comparison row: needs a clean re-pull;
  do NOT freeze the screenshot figure. Add as a LABELED instrument-comparison row.
- FIX 5 — install torch/transformers into `.venv` if you want REAL MiniCPM
  narration on camera (optional; numbers identical either way).
- Set the HF Space secrets above.
- Submission: move Space into `build-small-hackathon` org · record 60s video ·
  social post · paste both links into README.
