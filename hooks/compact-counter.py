#!/usr/bin/env python3
"""Claude Code SessionStart hook (OPT-IN, matcher: compact): warn only when autocompact is really thrashing.

Thrash = after a compaction the context fills up again within a few turns. Counting compactions alone
is a bad signal (it flags healthy sessions and subagents); post-compaction token counts alone are too
low (fixed overhead such as tools, memory and skills sits outside them). So this hook measures:
  (a) the number of assistant turns between the last compactions (2 cycles in a row with <= CC_THRASH_TURNS
      turns = the context can't breathe), and
  (b) the real restart size = post-compaction tokens + the typical fixed overhead (median of recent cycles,
      else CC_THRASH_OVERHEAD). At or above CC_THRASH_LIMIT the session is about to thrash.
If either holds, it injects additionalContext telling Claude to keep going in the same session, push heavy
reads/builds to subagents and refresh its handoff notes. Subagents are never flagged.
A per-session counter file is kept in CC_COMPACT_DIR (default ~/.claude/.compact-count); files older
than 3 days are pruned. Never crashes: bad stdin or any error -> silent.

Env: CC_THRASH_TURNS (default 8) · CC_THRASH_LIMIT (tokens, default 105000)
     CC_THRASH_OVERHEAD (tokens, default 60000) · CC_COMPACT_DIR
Test:  python3 compact-counter.py --selftest
"""
import json
import os
import sys
import time


def _int(name, default):
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


TURN_LIMIT = _int("CC_THRASH_TURNS", 8)
EFFECTIVE_LIMIT = _int("CC_THRASH_LIMIT", 105_000)
DEFAULT_OVERHEAD = _int("CC_THRASH_OVERHEAD", 60_000)
TAIL_BYTES = 8_000_000  # roughly the last 8-10 cycles of a big transcript


def counter_dir():
    return os.environ.get("CC_COMPACT_DIR") or os.path.expanduser("~/.claude/.compact-count")


def _ctx(u):
    return ((u.get("input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0)
            + (u.get("cache_creation_input_tokens") or 0))


def cycles(lines):
    """[post_tokens, ctx_of_first_call, turns] per compact_boundary, main chain only."""
    rows, seen = [], set()
    for line in lines:
        if '"compact_boundary"' in line:
            try:
                post = json.loads(line)["compactMetadata"].get("postTokens")
            except Exception:
                post = None
            rows.append([post, None, 0])
            continue
        if not rows or '"usage"' not in line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        if not isinstance(d, dict) or d.get("type") != "assistant" or d.get("isSidechain"):
            continue
        m = d.get("message") or {}
        mid = m.get("id")
        if not m.get("usage") or mid in seen:
            continue
        seen.add(mid)
        r = rows[-1]
        r[2] += 1
        if r[1] is None:
            r[1] = _ctx(m["usage"])
    return rows


def verdict(rows):
    """Reason to warn, or None if the session breathes."""
    done = [r for r in rows if r[2] > 0]
    if len(done) >= 2 and done[-1][2] <= TURN_LIMIT and done[-2][2] <= TURN_LIMIT:
        return f"the last 2 compactions refilled in {done[-2][2]} and {done[-1][2]} turns"
    post = rows[-1][0] if rows else None
    if post is None:
        return None
    over = sorted(r[1] - r[0] for r in done if r[1] and r[0])
    over = over[len(over) // 2] if over else DEFAULT_OVERHEAD
    if post + over >= EFFECTIVE_LIMIT:
        return f"after compaction the context restarts at ~{(post + over) // 1000}k tokens"
    return None


def read_tail(path):
    try:
        with open(path, "rb") as fh:
            fh.seek(0, 2)
            fh.seek(max(0, fh.tell() - TAIL_BYTES))
            return fh.read().decode("utf-8", "ignore").splitlines()
    except OSError:
        return []


def selftest():
    def asst(i, tok):
        return json.dumps({"type": "assistant", "message": {"id": f"m{i}", "usage": {"input_tokens": tok}}})

    boundary = lambda post: json.dumps({"type": "system", "subtype": "compact_boundary",  # noqa: E731
                                        "compactMetadata": {"postTokens": post}})
    # healthy: 20 turns between compactions, low restart size
    healthy = [boundary(20_000)] + [asst(i, 80_000) for i in range(20)] + [boundary(20_000)]
    assert verdict(cycles(healthy)) is None
    # thrash by turns: two cycles of 3 turns each
    thr = [boundary(30_000)] + [asst(i, 100_000) for i in range(3)] + \
          [boundary(30_000)] + [asst(10 + i, 100_000) for i in range(3)]
    assert "refilled" in verdict(cycles(thr))
    # thrash by size: post + default overhead >= limit
    assert "restarts at" in verdict(cycles([boundary(50_000)]))
    # junk lines are ignored
    assert cycles(["junk", "{", boundary(1)]) == [[1, None, 0]]
    # bad stdin never crashes
    import subprocess
    r = subprocess.run([sys.executable, __file__], input="garbage", capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout == ""
    print("selftest ok")
    return 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            return 0
        tp = data.get("transcript_path") or ""
        # never flag subagents: tight jobs, separate context
        if data.get("agent_id") or data.get("agent_type") or "/subagents/" in tp:
            return 0
        sid = str(data.get("session_id") or "unknown").replace(os.sep, "_")
        d = counter_dir()
        os.makedirs(d, exist_ok=True)
        now = time.time()
        for f in os.listdir(d):
            p = os.path.join(d, f)
            try:
                if now - os.path.getmtime(p) > 3 * 86400:
                    os.remove(p)
            except OSError:
                pass
        path = os.path.join(d, sid)
        try:
            n = int(open(path).read().strip() or 0) + 1
        except (OSError, ValueError):
            n = 1
        with open(path, "w") as fh:
            fh.write(str(n))
        why = verdict(cycles(read_tail(tp))) if tp else None
        if not why:
            return 0
        ctx = (f"WARNING, autocompact thrash ahead: {why}. The restart context (tools, memory, skills already "
               "used, summary) leaves few turns. In the main session avoid big reads and do not re-read files "
               "that were just re-attached. Update the project's handoff notes (current progress + next steps) "
               "as insurance, then CONTINUE in this session: delegate builds, reviews and heavy reads to "
               "subagents (tight jobs, short returns) and keep the main thread for orchestration.")
        print(json.dumps({
            "systemMessage": f"Autocompact thrash ahead ({why}): keep going, delegate heavy work to subagents",
            "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx},
        }))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
