#!/usr/bin/env python3
"""Daily token tracker: aggregates Claude Code transcript usage per day/model.
Usage: token_tracker.py [--days N] [--out FILE] [--json]
Reads ~/.claude/projects/**/*.jsonl (assistant messages with usage), dedupes by message id.
"""
import argparse, glob, json, os, sys, datetime as dt
from collections import defaultdict

ROOT = os.path.expanduser("~/.claude/projects")
STATE = os.path.expanduser(os.environ.get("TOKEN_TRACKER_DIR", "~/.claude/token-budget"))
OUT = os.path.join(STATE, "token_usage.md")
SUMMARY = os.path.join(STATE, "summary.json")
DB = os.path.join(STATE, "db.json")
LOCAL = dt.datetime.now().astimezone().tzinfo

def short(m):
    m = m or "?"
    for k in ("fable", "opus", "sonnet", "haiku"):
        if k in m: return k
    return m[:12]

def scan(days):
    since = (dt.datetime.now(LOCAL) - dt.timedelta(days=days)).date()
    seen = set()
    agg = defaultdict(lambda: defaultdict(lambda: dict(turns=0, inp=0, cw=0, cr=0, out=0, ctx=0, big=0)))
    for f in glob.iglob(os.path.join(ROOT, "**", "*.jsonl"), recursive=True):
        try:
            if dt.datetime.fromtimestamp(os.path.getmtime(f)).date() < since: continue
            with open(f, errors="ignore") as fh:
                for line in fh:
                    if '"usage"' not in line: continue
                    try: d = json.loads(line)
                    except Exception: continue
                    if d.get("type") != "assistant": continue
                    m = d.get("message") or {}
                    u = m.get("usage") or {}
                    mid = m.get("id") or d.get("uuid")
                    if not mid or mid in seen: continue
                    ts = d.get("timestamp")
                    if not ts: continue
                    day = dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(LOCAL).date()
                    if day < since: continue
                    seen.add(mid)
                    inp, cw, cr, out = (u.get("input_tokens", 0), u.get("cache_creation_input_tokens", 0),
                                        u.get("cache_read_input_tokens", 0), u.get("output_tokens", 0))
                    ctx = inp + cw + cr
                    r = agg[str(day)][short(m.get("model"))]
                    r["turns"] += 1; r["inp"] += inp; r["cw"] += cw; r["cr"] += cr; r["out"] += out
                    r["ctx"] += ctx; r["big"] += 1 if ctx > 200_000 else 0
        except Exception as e:
            print("skip", f, e, file=sys.stderr)
    return agg

def codex_tokens(days):
    """Codex CLI: last cumulative total_token_usage of each rollout, booked on the rollout's day."""
    import re
    since = (dt.datetime.now(LOCAL) - dt.timedelta(days=days)).date()
    out = defaultdict(int); rx = re.compile(r'"total_token_usage":\{[^}]*?"total_tokens":(\d+)')
    for f in glob.iglob(os.path.expanduser("~/.codex/sessions/*/*/*/*.jsonl")):
        try:
            y, m, d = f.split(os.sep)[-4:-1]; day = dt.date(int(y), int(m), int(d))
            if day < since: continue
            hits = rx.findall(open(f, errors="ignore").read())
            if hits: out[str(day)] += int(hits[-1])
        except Exception: pass
    return out

def summary():
    """today + rolling 7 days, as JSON for a status bar / dashboard."""
    agg = scan(7); cx = codex_tokens(7); today = str(dt.datetime.now(LOCAL).date())
    def tot(days):
        by = defaultdict(int)
        for d in days:
            for model, r in agg.get(d, {}).items():
                if model.startswith("<"): continue
                by[model] += r["inp"] + r["cw"] + r["cr"] + r["out"]
        return {"total": sum(by.values()), "byModel": dict(by), "codex": sum(cx.get(d, 0) for d in days)}
    week = [str(dt.datetime.now(LOCAL).date() - dt.timedelta(days=i)) for i in range(7)]
    return {"at": dt.datetime.now(LOCAL).isoformat(timespec="seconds"), "day": tot([today]), "week": tot(week)}

def k(n): return f"{n/1000:.0f}k" if n < 1_000_000 else f"{n/1e6:.2f}M"

def render(agg):
    lines = ["# Token usage daily (auto: way-stack token_tracker.py)", "",
             f"Updated: {dt.datetime.now(LOCAL):%Y-%m-%d %H:%M}. Tot = input+cache_write+cache_read+output (what the quota sees). Ctx/turn = average context re-paid on every turn. >200k = % of turns above 200k (should be 0).", "",
             "| Day | Model | Turns | Tot | Cache read | Cache write | Output | Ctx/turn | >200k |", "|---|---|---|---|---|---|---|---|---|"]
    for day in sorted(agg, reverse=True):
        tot_day = {k_: 0 for k_ in ("turns","inp","cw","cr","out","ctx","big")}
        for model in sorted(agg[day]):
            r = agg[day][model]
            for k_ in tot_day: tot_day[k_] += r[k_]
            tot = r["inp"]+r["cw"]+r["cr"]+r["out"]
            lines.append(f"| {day} | {model} | {r['turns']} | {k(tot)} | {k(r['cr'])} | {k(r['cw'])} | {k(r['out'])} | {k(r['ctx']/max(r['turns'],1))} | {100*r['big']/max(r['turns'],1):.0f}% |")
        r = tot_day; tot = r["inp"]+r["cw"]+r["cr"]+r["out"]
        lines.append(f"| **{day}** | **all** | **{r['turns']}** | **{k(tot)}** | {k(r['cr'])} | {k(r['cw'])} | {k(r['out'])} | **{k(r['ctx']/max(r['turns'],1))}** | {100*r['big']/max(r['turns'],1):.0f}% |")
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--out", default=OUT); ap.add_argument("--json", action="store_true")
    ap.add_argument("--summary", action="store_true", help="write summary.json (today + 7 days) and print it")
    a = ap.parse_args()
    os.makedirs(STATE, exist_ok=True)
    if a.summary:
        sm = summary(); tmp = SUMMARY + ".tmp"
        json.dump(sm, open(tmp, "w")); os.replace(tmp, SUMMARY); print(json.dumps(sm)); sys.exit()
    agg = scan(a.days)
    if a.json: print(json.dumps(agg, indent=1)); sys.exit()
    md = render(agg)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w").write(md)
    # persist merged db (never lose old days)
    db = {}
    if os.path.exists(DB):
        try: db = json.load(open(DB))
        except Exception: db = {}
    db.update({d: dict(v) for d, v in agg.items()})
    json.dump(db, open(DB, "w"), indent=0)
    print(md)
