#!/usr/bin/env python3
"""Claude Code PostToolUse hook (OPT-IN, matcher Edit|Write|MultiEdit): run the tests next to the edited file.

Silent on pass, loud on fail (exit 2 -> stderr is fed back to Claude).
Opt-out: a `.claude-notest` file in the edited file's dir or ANY ancestor (checked first).
Opt-in: nearest ancestor (<= 4 levels up) holding a `.claude-test` file (its content is the command),
        or, for a .py file, a dir containing test_*.py (runs `python3 -m pytest -q -x .`).
Timeout: the test process group is killed and Claude is told the check is INCOMPLETE (exit 2).
Container dirs (/, /tmp, $HOME, ~/Documents, per-user temp, agent scratchpads, plus CC_TEST_CONTAINERS)
are never test roots and stop the upward walk, so a stray scratch file can't trigger a huge test run.
Never crashes: any internal error -> exit 0 with a one-line note.

Env: CC_TEST_TIMEOUT (seconds, default 90) · CC_TEST_CONTAINERS (colon-separated extra dirs, default none)
Test:  python3 post-edit-test.py --selftest
"""
import json
import os
import signal
import subprocess
import sys
import tempfile

HOME = os.path.expanduser("~")
EXTS = (".py", ".js", ".ts", ".mjs", ".html", ".liquid", ".json")


def containers():
    base = {"/", "/tmp", "/private/tmp", HOME, os.path.join(HOME, "Documents")}
    for p in os.environ.get("CC_TEST_CONTAINERS", "").split(":"):
        if p.strip():
            base.add(os.path.abspath(os.path.expanduser(p.strip())))
    return base


def is_container(path):
    if path in containers():
        return True
    p = path.split(os.sep)
    # /private/tmp/claude-<uid>/<project>/<session>/scratchpad: only dirs strictly INSIDE a scratchpad
    # can be a test root (the scratchpad itself holds unrelated loose scripts)
    for base in (["", "private", "tmp"], ["", "tmp"]):
        n = len(base)
        if p[:n] == base and len(p) > n and p[n].startswith("claude-") and "scratchpad" not in p[n:-1]:
            return True
    # macOS per-user temp: /var/folders/<xx>/<hash>/<T|C|0> and everything above it
    for base in (["", "private", "var", "folders"], ["", "var", "folders"]):
        if p[:len(base)] == base and len(p) <= len(base) + 3:
            return True
    return False


def find_command(fp):
    """Return (cmd, cwd) for the edited file, or (None, None). Raises OSError on unreadable dirs."""
    start = os.path.dirname(os.path.abspath(fp))
    cur = start
    while True:  # opt-out anywhere up the tree wins
        if os.path.exists(os.path.join(cur, ".claude-notest")):
            return None, None
        nxt = os.path.dirname(cur)
        if nxt == cur:
            break
        cur = nxt
    cur = start
    for _ in range(5):
        if is_container(cur):
            break
        marker = os.path.join(cur, ".claude-test")
        if os.path.isfile(marker):
            with open(marker) as fh:
                return fh.read().strip(), cur
        if fp.endswith(".py") and any(n.startswith("test_") and n.endswith(".py") for n in os.listdir(cur)):
            return "python3 -m pytest -q -x --no-header -p no:cacheprovider .", cur
        nxt = os.path.dirname(cur)
        if nxt == cur:
            break
        cur = nxt
    return None, None


def main():
    try:
        d = json.load(sys.stdin)
    except Exception:
        return 0
    ti = d.get("tool_input") if isinstance(d, dict) else None
    fp = ti.get("file_path") if isinstance(ti, dict) else None
    if not isinstance(fp, str) or not os.path.isfile(fp) or os.path.splitext(fp)[1] not in EXTS:
        return 0
    try:
        cmd, cwd = find_command(fp)
    except OSError as e:
        print(f"[post-edit-test] skipped: cannot read directory: {e}", file=sys.stderr)
        return 0
    if not cmd:
        return 0
    try:
        timeout = int(os.environ.get("CC_TEST_TIMEOUT", "90"))
    except ValueError:
        timeout = 90
    p = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         stdin=subprocess.DEVNULL, start_new_session=True)
    try:
        out, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except Exception:
            pass
        print(f"[post-edit-test] INCOMPLETE: tests in {cwd} exceeded {timeout}s and were killed (`{cmd}`). "
              "Run them yourself before claiming green.", file=sys.stderr)
        return 2
    if p.returncode == 0:
        return 0
    tail = "\n".join((out or "").strip().splitlines()[-30:])
    print(f"[post-edit-test] TESTS FAILED after editing {os.path.basename(fp)} (cwd {cwd}, `{cmd}`):\n{tail}",
          file=sys.stderr)
    return 2


def selftest():
    assert is_container("/") and is_container(HOME) and is_container("/private/tmp")
    assert is_container("/private/tmp/claude-501/proj")
    assert not is_container("/private/tmp/claude-501/proj/sess/scratchpad/work")
    with tempfile.TemporaryDirectory() as t:
        t = os.path.realpath(t)
        proj = os.path.join(t, "proj")
        os.makedirs(proj)
        f = os.path.join(proj, "a.js")
        open(f, "w").write("x")
        os.environ["CC_TEST_CONTAINERS"] = t
        assert find_command(f) == (None, None)  # no marker
        open(os.path.join(proj, ".claude-test"), "w").write("true")
        assert find_command(f) == ("true", proj)
        open(os.path.join(proj, ".claude-notest"), "w").write("")
        assert find_command(f) == (None, None)  # opt-out wins
        os.remove(os.path.join(proj, ".claude-notest"))
        # end to end: failing command -> exit 2, passing -> exit 0, garbage stdin -> 0
        for cmd, want in (("true", 0), ("false", 2)):
            open(os.path.join(proj, ".claude-test"), "w").write(cmd)
            r = subprocess.run([sys.executable, __file__], input=json.dumps({"tool_input": {"file_path": f}}),
                               capture_output=True, text=True, env=dict(os.environ))
            assert r.returncode == want, (cmd, r.returncode, r.stderr)
        r = subprocess.run([sys.executable, __file__], input="not json", capture_output=True, text=True)
        assert r.returncode == 0
    print("selftest ok")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    try:
        sys.exit(main())
    except Exception as e:  # never break the editing loop because of the hook itself
        print(f"[post-edit-test] hook error (ignored): {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(0)
