# Codex handoff — MO§ES SigRank

Read this first. It's the instruction set for driving **OpenAI Codex** against this
repo and the thing that earns the **Codex $10k sponsor prize**.

Local path (desktop storage): `/Users/dericmchenry/Desktop/moses-sigrank`
GitHub (current): `github.com/Burnmydays/hf-`  →  upload target: `github.com/SunrisesIllNeverSee`

## How the prize works (important)
The sponsor track rewards repos where **Codex did real work**, shown through
**Codex-attributed commits**. It does NOT require that 100% of the repo is Codex's.
Two rules:
1. **Genuine work only.** Let Codex actually write the code and commit it with its own
   attribution. Do not hand-copy output or fake attribution — that risks disqualification.
2. **Verify the official rule** on the hackathon page before relying on this.

## Current state (as of this handoff)
Done and pushed to Burnmydays/hf- (main):
- Codex parser fixed — `_codex_input_estimate` in `ingest.py` (Beta = output × real Claude
  io_ratio; Alpha = output × 2.0 AA baseline). Two pathways, both flagged `*` estimated.
- `./sigrank --all` (run every provider in turn).
- Instructions sharpened (app.py "Clock Your Signal" tab + README).
- Wild corpus = 10 tokscale.ai operators; board = 11 rows; Supabase migrated + synced.

## Codex parser — DONE (do not change)
The Codex token conversion is FINAL: the ratio model in `_codex_input_estimate`
(`ingest.py`) — Alpha `output×2` (no Claude profile) / Beta `output×io_ratio` (Claude
profile present) — handles the estimate. **Do NOT add turn/daily-delta logic.**

## Codex's job: DEPLOY (the main handoff)
Do these in order so the work + attribution land in the submitted location.

1. **Upload the repo to GitHub → `github.com/SunrisesIllNeverSee`.**
   The current working copy is at `/Users/dericmchenry/Desktop/moses-sigrank` (also on
   `github.com/Burnmydays/hf-`). Commit with Codex attribution and push to SunrisesIllNeverSee.

2. **Deploy to the HuggingFace Space** (Gradio SDK; `README.md` already has valid Space
   front-matter). Create/link the Space under the owner's HF account (`burnmydays`) and
   push the repo to the Space's git remote.

3. **Set the Space secrets** (Space → Settings → Variables and secrets). Copy the values
   from `SECRETS.local.md` (gitignored — never commit them):
   - `SUPABASE_URL`        → read endpoint
   - `SUPABASE_ANON_KEY`   → read (RLS-gated, public-read)
   - `SUPABASE_SERVICE_KEY`→ **only if** signed-in visitor rows should persist; leave UNSET
     for the curated demo (then writes are no-ops and pastes stay transient).
   Without these the app still boots on the SEED fallback (11 rows), so it never breaks.

## Optional extra attributed commits (nice-to-have for the prize)
- **`test_metrics.py`** — lock MO§ES Υ 18,436.98 / lev 2042.2 / 10x DEV 3.31 + the
  telescoping identity `(o/i)·(cw/o)·(cr/cw)==cr/i` for every SEED row, plus both Codex
  pathways (Alpha `output×2`, Beta `output×io_ratio`).
- **Real Codex `$/1M`** — OpenAI per-1M prices in `parse_codex_submission` meta (keep `*`).

## Verify BEFORE every Codex commit
```
cd /Users/dericmchenry/Desktop/moses-sigrank
.venv/bin/python -c "import py_compile,glob; [py_compile.compile(f,doraise=True) for f in glob.glob('*.py')]"
.venv/bin/python metrics.py    # MO§ES must print Y 18436.98, lev 2042.2, 10xDEV 3.31, $/1M 0.527
```
(use `python3` if there's no `.venv`.)

## DO NOT let Codex touch
- The MO§ES (ccusage) SEED row in `metrics.py` (canonical, Υ 18436.98).
- The Υ formula `(C·O)/I²` or the telescoping identity — these are the thesis.
- The Codex estimation must stay **flagged (`*`)** — never a silent strict assumption.

## Already done — NOT available as Codex commits
- 2:1 → real-ratio anchor refinement (Alpha/Beta unified). Done by Claude this session.
- Board `~`/`*` estimated-row marker. Done by Claude this session.

See `SCRATCHPAD.md` for live cross-agent state and `TODO.md` for the full task board.
