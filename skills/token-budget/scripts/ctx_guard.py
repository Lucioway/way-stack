#!/usr/bin/env python3
# Stop hook: prints a compact context line in chat after every turn, e.g. "🟢 ctx 78k (39%)".
# Reads only the last usage record of the current transcript = instant.
# Env: CC_CTX_WINDOW (default 200000), CC_CTX_WARN (default 140000 → adds a handoff nudge).
import sys, json, os

WINDOW  = int(os.environ.get("CC_CTX_WINDOW", "200000"))  # % denominator
WARN_AT = int(os.environ.get("CC_CTX_WARN", "140000"))    # ping + louder note

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    tp = data.get("transcript_path")
    if not tp or not os.path.exists(tp):
        return
    try:
        with open(tp) as f:
            lines = f.readlines()
    except Exception:
        return
    usage = None
    for line in reversed(lines):
        try:
            o = json.loads(line)
        except Exception:
            continue
        u = (o.get("message") or {}).get("usage")
        if u and (u.get("input_tokens") is not None or u.get("cache_read_input_tokens") is not None):
            usage = u
            break
    if not usage:
        return
    ctx = (usage.get("input_tokens", 0)
           + usage.get("cache_read_input_tokens", 0)
           + usage.get("cache_creation_input_tokens", 0))
    pct = int(ctx / WINDOW * 100) if WINDOW else 0
    k = ctx // 1000
    icon = "🟢" if pct < 50 else ("🟡" if pct < 80 else "🔴")
    line = f"{icon} ctx {k}k ({pct}%)"
    if ctx >= WARN_AT:
        line += " · hand off now: /handoff then /reboot"
    print(json.dumps({"systemMessage": line}))

if __name__ == "__main__":
    main()
