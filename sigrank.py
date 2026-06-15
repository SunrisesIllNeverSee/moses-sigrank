#!/usr/bin/env python3
"""
sigrank — local-first importer for MO§ES SigRank.

Her-style: reads YOUR usage on YOUR machine and prints your operator read. No
paste, no token, no upload. The hosted Space's paste box is the backup; this is
the real-app path.

  python sigrank.py                 # auto-run `ccusage --json` (Claude Code)
  python sigrank.py --codex         # auto-run `ccusage codex --json`
  python sigrank.py --file u.json   # read a saved ccusage/codex json
  python sigrank.py --name "you"    # label your row
  cat u.json | python sigrank.py -  # read from stdin (backup)
  python sigrank.py --no-color      # plain output

Everything quantitative is pure computation (metrics.py). The board comparison
uses db.load_operators() which falls back to the hardcoded SEED corpus, so this
works offline with zero config.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

from ingest import ingest_meta, parse_ccusage
from metrics import compute
import db

GOLD = "\033[38;5;179m"
DIM = "\033[38;5;244m"
BOLD = "\033[1m"
RST = "\033[0m"


def _c(s, color, on=True):
    return f"{color}{s}{RST}" if on else str(s)


def _fmt_int(n):
    for u, d in (("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(n) >= d:
            return f"{n / d:.2f}{u}"
    return str(int(n))


def _classify(m):
    if m["non_compounding"]:
        return "Non-Compounding · stateless pipe"
    v, l = m["velocity"], m["leverage"]
    if v >= 1 and l >= 100:
        return "Closed-Loop Kinetic · holds both axes"
    if l >= 10 and v < 1:
        return "Archival Sponge · high reuse, low generation"
    if v >= 0.8 and l < 2:
        return "Volatile Ingestor · generates, doesn't retain"
    return "Transient · low on both axes"


def _grab_usage(args):
    """Return (raw_text, how) from ccusage, a file, or stdin. Local only."""
    if args.file:
        return open(args.file, encoding="utf-8").read(), f"file {args.file}"
    if args.stdin:
        return sys.stdin.read(), "stdin"
    # auto: run ccusage on the user's machine — subcommand scopes to one agent only
    sub = ["codex", "--json"] if args.codex else ["claude", "--json"]
    label = "ccusage codex" if args.codex else "ccusage claude"
    if shutil.which("ccusage"):
        cmd = ["ccusage"] + sub
    elif shutil.which("npx"):
        cmd = ["npx", "ccusage@latest"] + sub
    else:
        raise RuntimeError(
            "ccusage not found. Install Node/npx, or pass --file <ccusage.json>, "
            "or pipe JSON in: `cat usage.json | python sigrank.py -`"
        )
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise RuntimeError(f"`{' '.join(cmd)}` failed:\n{out.stderr.strip()[:400]}")
    return out.stdout, label


def _rank(name, m):
    """Where this row lands vs the live field (Supabase → SEED fallback)."""
    base = db.load_operators()
    rows = [(n, compute(*v)) for n, v in base.items() if n != name] + [(name, m)]
    rows.sort(key=lambda r: r[1]["yield"], reverse=True)
    idx = next(i for i, (n, _) in enumerate(rows, 1) if n == name)
    return idx, len(rows)


def render(name, m, how, color=True):
    r = m["raw"]
    cost_kind = "real cost" if not m["cost_estimated"] else "list-price est ~"
    dev = f"{m['dev10x']:.2f}" if m["dev10x"] is not None else "— (non-compounding)"
    cav = m.get("_caveat")
    rank, total = _rank(name, m)
    line = _c("─" * 44, DIM, color)

    out = []
    out.append("")
    out.append("  " + _c(f"MO§ES SigRank · {name}", GOLD + BOLD, color))
    out.append("  " + line)
    out.append("  " + _c(f"source: {how} · {cost_kind}", DIM, color))
    if cav:
        out.append("  " + _c(f"⚠ {cav}", DIM, color))
    out.append(
        "  " + _c("ledger", DIM, color)
        + f"   R {_fmt_int(r['cache_read'])} · C {_fmt_int(r['cache_create'])} · "
        f"I {_fmt_int(r['input'])} · O {_fmt_int(r['output'])}"
    )
    out.append("  " + line)
    metrics = [
        ("SNR", f"{m['snr']:.3f}"),
        ("10x DEV", dev),
        ("velocity", f"{m['velocity']:.2f}×"),
        ("leverage", f"{m['leverage']:,.0f}×"),
        ("$/1M", f"{'~' if m['cost_estimated'] else ''}${m['avg_cost_1m']:.3f}"),
    ]
    for k, v in metrics:
        out.append("  " + _c(f"{k:<10}", DIM, color) + v)
    out.append("  " + _c(f"{'Υ yield':<10}", GOLD, color) + _c(f"{m['yield']:,.0f}", GOLD + BOLD, color))
    out.append("  " + line)
    out.append("  " + _c("class", DIM, color) + f"  {_classify(m)}")
    out.append("  " + _c("rank ", DIM, color) + f"  " + _c(f"#{rank}", GOLD + BOLD, color) + f" of {total} vs the live field")
    out.append("  " + line)
    out.append("  " + _c("paste this row on the Space to appear on the board:", DIM, color))
    out.append("  " + f"{r['input']} {r['output']} {r['cache_create']} {r['cache_read']}")
    out.append("")
    return "\n".join(out)


def main(argv=None):
    p = argparse.ArgumentParser(prog="sigrank", description="Local-first SigRank importer.")
    p.add_argument("stdin_dash", nargs="?", default=None, help="pass '-' to read JSON from stdin")
    p.add_argument("--file", help="read a saved ccusage/codex json file")
    p.add_argument("--codex", action="store_true", help="run `ccusage codex --json`")
    p.add_argument("--name", default="you", help="label for your row")
    p.add_argument("--no-color", action="store_true", help="plain output")
    args = p.parse_args(argv)
    args.stdin = args.stdin_dash == "-"

    color = sys.stdout.isatty() and not args.no_color

    # For Codex: detect Claude profile so the parser uses 1:9 pathway.
    operator_profile = None
    if args.codex:
        try:
            _c_args = type("a", (), {"file": None, "stdin": False, "codex": False})()
            _c_raw, _ = _grab_usage(_c_args)
            _ci, _co, _, _, _ = parse_ccusage(_c_raw)
            if _co > 0:
                operator_profile = {"model_type": "claude", "io_ratio": _ci / _co}
        except Exception:
            pass  # no Claude data — Alpha pathway (3:2:1)

    try:
        raw, how = _grab_usage(args)
        i, o, cw, cr, meta = ingest_meta(raw, operator_profile=operator_profile)
    except Exception as e:
        print(f"sigrank: {e}", file=sys.stderr)
        return 1
    if i + o + cw + cr == 0:
        print("sigrank: got zeros — check your usage source.", file=sys.stderr)
        return 1

    m = compute(i, o, cw, cr, cost_usd=meta.get("cost"))
    if meta.get("estimated"):
        m["_caveat"] = meta.get("caveat")
    print(render((args.name or "you").strip()[:24] or "you", m, how, color))
    return 0


if __name__ == "__main__":
    sys.exit(main())
