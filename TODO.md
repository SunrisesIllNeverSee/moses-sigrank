# TODO — MO§ES SigRank submission

Deadline: **June 15 2026, 23:59 UTC**. Track: Thousand Token Wood 🍄
Completed items are at the BOTTOM. Everything still TO DO is up top.

═══════════════════════════════════════════════════════════════════
# ⚡ TO DO — DO NOT FORGET
═══════════════════════════════════════════════════════════════════

### A. Turn persistence ON (HF Space → Settings → Variables and secrets)
- **Keys live in `SECRETS.local.md`** (gitignored, NOT uploaded). Copy `SUPABASE_URL` + `SUPABASE_ANON_KEY` into the Space secrets.
- Curated mode = set ONLY those two on the public Space (leave `service_role` OFF so visitor pastes stay transient).
- DB verified live: anon read returns 7 rows, anon write blocked (401). Just needs the secrets set on the Space.

### B. Blocked on owner (data / quality)
- [ ] FIX 3 — re-pull clean tokscale numbers, add "MCH (tokscale read)" as a LABELED instrument-comparison row.
- [ ] FIX 5 — (optional, pre-record) install MiniCPM deps for REAL narration: `.venv/bin/python -m pip install torch transformers accelerate sentencepiece`

### C. Reserved for Codex (earns the $10k attribution — do AFTER repo is in the org)
- [ ] Refine 2:1 anchor → turn-delta method (keep 2:1 fallback)
- [ ] `test_metrics.py` — lock Υ 18,437 / lev 2042 / X 3.31 / telescoping
- [ ] Real Codex `$/1M` via OpenAI prices in `parse_codex` meta
- [ ] Board visual marker on estimated (Codex) rows

### D. NEXT BUILD — automatic importer (her-style, paste = backup)
- [ ] Clean/sleek local importer that auto-reads ccusage (no paste, local-first). Design in SCRATCHPAD.md.

### E. Submission (non-negotiable)
- [ ] Move Space into `build-small-hackathon` org
- [ ] Record 60s demo video + paste link in README
- [ ] Social post (X/LinkedIn) + paste link in README

═══════════════════════════════════════════════════════════════════
# 📋 REFERENCE (for the remaining submission tasks)
═══════════════════════════════════════════════════════════════════

## DEMO VIDEO — 60-sec script (open cold on the board)
1. (0-10s) Open ON the leaderboard. Don't explain. Let the eye hit the 4-orders Υ gap.
   "This is every operator's token usage, ranked by one number."
2. (10-25s) Point at $/1M column. "The operator at the top is also the cheapest.
   Efficiency isn't a tradeoff against cost — it IS the cost."
3. (25-45s) Go to Measure Yourself. Paste a live `ccusage --json`. Hit compute.
   New operator drops onto the board in real time with a narrated profile.
4. (45-60s) "Υ = cache × output over input squared. You can't buy rank with volume —
   padding input is penalized quadratically. That's the whole game." End on board.

## SOCIAL POST — draft
"Built MO§ES SigRank for the @Gradio Build Small hackathon: a diagnostic x-ray of
the token economy. Paste your ccusage output, get ranked by Net Volumetric Yield —
the metric where volume can't buy rank. A 0.5B MiniCPM narrates your architecture.
🍄 Thousand Token Wood. [link]"

## BADGES IN REACH (mostly engineered — confirm in README/tags)
- [x] Off Brand ($1,500) — custom non-default UI ✓ (theme.py)
- [x] Tiny Titan ($1,500) — ≤4B model ✓ (0.5B)
- [ ] Best Demo ($1,000) — needs the video to land
- [x] Best MiniCPM sponsor ($2,500) — built on MiniCPM ✓
- [ ] Codex sponsor ($10k) — needs Codex-attributed commits (see CODEX.md)
- [x] Model ≤32B confirmed (MiniCPM4-0.5B)

═══════════════════════════════════════════════════════════════════
# ✅ DONE
═══════════════════════════════════════════════════════════════════

## CODE — done
- [x] metrics.py — engine, 4 ints in, full ledger (incl Avg $/1M)
- [x] ingest.py — ccusage parser (any shape) + Codex parser (2:1 anchor, clamped, flagged) + four-number fallback
- [x] narrate.py — MiniCPM4-0.5B, non-blocking, template fallback
- [x] theme.py — gold/dark CSS, log-scaled Υ bars, 8-col board grid
- [x] app.py — board_html hero (with $/1M column) on BOTH tabs; profile; measure-yourself
- [x] requirements.txt, README.md
- [x] stress test passes (compile + logic cases)

## PERSISTENCE — Supabase (this session)
- [x] Table sigrank_operators built + seeded (7 rows), curated RLS, in AppFeeder
- [x] db.py (REST read + service-key upsert) with SEED fallback; app.py wired; requests added
- [x] Verified live: anon read 7 rows, anon write 401-blocked

## SEMANTICS — fixes (this session)
- [x] FIX 1 persistence-boundary honesty note · FIX 2 cost provenance · FIX 4 species/quadrant reframe · FIX 6 grid check

## REPO
- [x] Pushed full build to github.com/Burnmydays/hf- (main = cf4055a)
