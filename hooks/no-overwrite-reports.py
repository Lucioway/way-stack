#!/usr/bin/env python3
"""Claude Code PreToolUse hook (OPT-IN, matcher Write|Edit|MultiEdit): never overwrite existing report files.

Blocks Write/Edit on an EXISTING .csv/.xlsx/.xls (extensions configurable) unless the target is a test
path (a /test/ directory anywhere in the path, or a TEST_ filename prefix). New files pass, test files
pass, other extensions pass. Unparseable input never blocks (fail-open, so the hook can't wedge a session).
Exit 0 = allow · Exit 2 = block (reason on stderr).

Env: CC_REPORT_EXTS (comma-separated, default ".csv,.xlsx,.xls")
Test:  python3 no-overwrite-reports.py --selftest
"""
import json
import os
import sys
import tempfile


def exts():
    raw = os.environ.get("CC_REPORT_EXTS", ".csv,.xlsx,.xls")
    return tuple(e.strip().lower() for e in raw.split(",") if e.strip())


def blocked(fp):
    """True if writing fp would overwrite an existing protected report."""
    if not isinstance(fp, str) or not fp:
        return False
    low = fp.lower()
    if not low.endswith(exts()):
        return False
    if "/test/" in low.replace(os.sep, "/") or os.path.basename(fp).upper().startswith("TEST_"):
        return False
    return os.path.exists(fp)


def selftest():
    with tempfile.TemporaryDirectory() as d:
        old = os.path.join(d, "report.csv")
        open(old, "w").write("a,b\n")
        os.makedirs(os.path.join(d, "test"))
        in_test = os.path.join(d, "test", "report.csv")
        open(in_test, "w").write("x")
        prefixed = os.path.join(d, "TEST_report.csv")
        open(prefixed, "w").write("x")
        txt = os.path.join(d, "notes.txt")
        open(txt, "w").write("x")
        assert blocked(old)
        assert not blocked(os.path.join(d, "new.csv"))
        assert not blocked(in_test) and not blocked(prefixed) and not blocked(txt)
        assert not blocked("") and not blocked(None)
    print("selftest ok")
    return 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    try:
        data = json.load(sys.stdin)
        ti = (data.get("tool_input") or {}) if isinstance(data, dict) else {}
        fp = ti.get("file_path") or ti.get("path") or ""
        if blocked(fp):
            print(f"BLOCKED: '{os.path.basename(fp)}' is an existing report file and must not be overwritten. "
                  "Write the new run to a /test/ subfolder or use a TEST_ filename prefix, "
                  f"or save under a new name. (path: {fp})", file=sys.stderr)
            return 2
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
