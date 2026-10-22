#!/usr/bin/env python3
"""Claude Code PreToolUse hook (OPT-IN, matcher Read): no whole-file reads of big text files.

A whole-file Read stays in the context until the session ends; saved tool outputs, memory dumps and
workflow docs are the usual offenders. Denies a Read with no limit/offset on a text file larger than
CC_BIG_READ_BYTES (default 40000). Images, PDFs (they have `pages`), notebooks and SVGs pass.
Claude can retry with an explicit limit (a conscious choice), or better grep first / use a subagent.
Never crashes: bad stdin, missing file, any error -> allow.

Env: CC_BIG_READ_BYTES (default 40000)
Test:  python3 big-read-guard.py --selftest
"""
import json
import os
import shutil
import sys
import tempfile

SKIP_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".heic", ".bmp", ".tiff", ".pdf", ".ipynb", ".svg")


def max_bytes():
    try:
        return int(os.environ.get("CC_BIG_READ_BYTES", "40000"))
    except ValueError:
        return 40000


def reason_for(ti):
    if not isinstance(ti, dict) or ti.get("limit") or ti.get("offset") or ti.get("pages"):
        return ""
    fp = os.path.expanduser(ti.get("file_path") or "")
    if not fp or fp.lower().endswith(SKIP_EXT):
        return ""
    try:
        size = os.path.getsize(fp)
    except OSError:
        return ""
    if size <= max_bytes():
        return ""
    return f"{os.path.basename(fp)} is {size // 1000} KB"


def selftest():
    d = tempfile.mkdtemp(prefix="bigread-")
    try:
        big, small, img = (os.path.join(d, n) for n in ("big.txt", "small.md", "shot.png"))
        for p, n in ((big, 60_000), (small, 5_000), (img, 200_000)):
            with open(p, "w") as f:
                f.write("x" * n)
        cases = [
            ({"file_path": big}, True),
            ({"file_path": big, "limit": 200}, False),
            ({"file_path": big, "offset": 400}, False),
            ({"file_path": small}, False),
            ({"file_path": img}, False),
            ({"file_path": os.path.join(d, "missing.txt")}, False),
            (None, False),
        ]
        for ti, want in cases:
            assert bool(reason_for(ti)) == want, ti
        os.environ["CC_BIG_READ_BYTES"] = "1000"
        assert reason_for({"file_path": small})
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print("selftest ok")
    return 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict) or data.get("tool_name") != "Read":
            return 0
        r = reason_for(data.get("tool_input"))
        if not r:
            return 0
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"Whole-file Read of a big file ({r}): it stays in context for the "
                                        "whole session. Grep for the lines you need, then Read with offset/limit; "
                                        "to understand a whole file, hand it to a subagent. If you truly need "
                                        "everything, retry with an explicit limit.",
        }}))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
