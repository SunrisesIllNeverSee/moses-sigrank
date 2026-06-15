# FIXES — open items for the SigRank build

Status legend:  [ ] not done · [~] partial/optional · [x] done
Completed items are moved to the BOTTOM. Everything still TO DO is up top.

═══════════════════════════════════════════════════════════════════
# 🔧 STILL TO DO
═══════════════════════════════════════════════════════════════════

## FIX 3 — tokscale MCH row (DATA, BLOCKED on your re-pull)
- [ ] FILE: metrics.py SEED
- WHAT: add "MCH (tokscale read)" as a LABELED instrument-comparison row, NOT a
  second person. Frame: same operator via the noisy instrument (input inflated
  to ~8.36M vs ccusage 1.25M — the +568% streaming-sum artifact).
- WHY: demonstrates instrument divergence honestly. Held open until you re-pull
  clean numbers (don't freeze the screenshot figure).

## FIX 5 — MiniCPM not in venv (DEMO QUALITY, optional pre-record)
- [~] requirements.txt lists torch/transformers; venv only has gradio.
- WHAT: for REAL MiniCPM narration on camera (not the template fallback):
    .venv/bin/python -m pip install torch transformers accelerate sentencepiece
- NOTE: heavy download. Numbers/board/cost/cascade identical either way — only
  the prose paragraph changes.

## SUBMISSION (yours, not code — from TODO.md)
- [ ] Move Space into build-small-hackathon ORG
- [ ] Record demo video (script in TODO.md) + paste link in README
- [ ] Social post + paste link in README
- [ ] If chasing Codex $10k: do Codex commits AFTER repo is in the org
      (so attribution lands in the submitted location) — see CODEX.md

## NEXT BUILD — automatic importer (her-style, paste = backup)
- [ ] Clean/sleek local importer that auto-reads ccusage (no paste). See SCRATCHPAD.md.

## VERIFY (run after every fix)
```
cd /Users/dericmchenry/Desktop/moses-sigrank
.venv/bin/python -c "import py_compile,glob; [py_compile.compile(f,doraise=True) for f in glob.glob('*.py')]"
.venv/bin/python metrics.py     # canonical numbers must still print
```

═══════════════════════════════════════════════════════════════════
# ✅ DONE
═══════════════════════════════════════════════════════════════════

## FIX 1 — Persistence boundary documented (HONESTY) — DONE this session
- [x] Added the honesty note to README (Notes), app.py Leaderboard tab, and
  "your placement". Phrased for curated mode so it stays true: pasted rows score
  live against the field but are NOT added to the persisted board.

## FIX 2 — Cost provenance stated (LABEL) — DONE this session
- [x] README Notes + metrics.py SEED comment now state: board $/1M is a list-price
  recompute (~) for all rows; MO§ES reproduces its real ccusage $0.527; the 6
  wild operators have no real cost data. Real cost only on the live ccusage paste.

## FIX 4 — Species/quadrant framing (NARRATIVE) — DONE this session
- [x] Wrote species_cards.md: 2×2 Scale×Amplification quadrant, MO§ES = the empty
  quadrant (not "top rank"), flavor-text fix ("built to compound, not just spend"),
  and the honest line (high reuse is the SIGNATURE of compounding, not proof).
  Deck-only, not the app.

## FIX 6 — CSS 8-col grid (VISUAL) — DONE this session
- [x] Verified theme.py:58 grid-template-columns = 8 tracks, matches the 8 header
  cells in board_html(). No change needed. (Pixel eyeball at your width still yours.)

## PERSISTENCE — Supabase (NEW, this session) — DONE + VERIFIED
- [x] Table public.sigrank_operators built + seeded (7 rows) in AppFeeder, curated RLS.
- [x] db.py (REST read + service-key upsert) with SEED fallback safety net.
- [x] app.py reads from db.load_operators() (cached, db→SEED) + save-on-ingest; requirements gained requests.
- [x] VERIFIED LIVE: anon REST read returns 7 rows; anon write blocked (401). Set Space secrets from SECRETS.local.md to activate.

## CONFIRMED WORKING (baseline)
- [x] ccusage import → fills ALL board columns. Verified MO§ES Υ 18,437, $0.527.
- [x] Codex import → 2:1 anchor split, clamped ≥0, caveat-flagged, full cascade.
- [x] Four-number fallback. Garbage input handled gracefully.
- [x] Avg $/1M is a real board column (8-col grid).
- [x] Board used on BOTH tabs — hero version consistent.
- [x] App boots under gradio 6.x (version-safe launch).
