#!/usr/bin/env python3
"""Claude Code PreToolUse hook (OPT-IN, matcher Bash): keep macOS Keychain secrets off the screen.

macOS ONLY (it guards the `security` CLI; harmless but useless elsewhere).
Denies: `security dump-keychain`; `security find-(generic|internet)-password ... -g` (prints the password);
`-w` outside `$(...)` (the value lands in the output, even through `| head -c N`).
Allowed: existence checks (`security find-generic-password -s X >/dev/null 2>&1; echo $?`),
`TOK=$(security find-generic-password -s X -w)`, reading inside a script file.
Never crashes: bad stdin or any error -> allow.
Test:  python3 keychain-guard.py --selftest
"""
import json
import re
import sys

FIND = re.compile(r"security\s+find-(?:generic|internet)-password\b([^;&|\n)]*)")


def reason_for(cmd):
    if not isinstance(cmd, str):
        return ""
    if re.search(r"security\s+dump-keychain", cmd):
        return "security dump-keychain"
    for m in FIND.finditer(cmd):
        flags = [t for t in m.group(1).split() if re.fullmatch(r"-[A-Za-z]+", t)]
        if any("g" in f for f in flags):
            return "find-*-password -g prints the password"
        if any("w" in f for f in flags) and not re.search(r"\$\(\s*$", cmd[:m.start()]):
            return "find-*-password -w outside $(...) prints the secret"
    return ""


def selftest():
    cases = {
        "security dump-keychain | grep svce": True,
        "security find-generic-password -g -s MY_TOKEN": True,
        "security find-generic-password -s MY_TOKEN -gw": True,
        "security find-generic-password -s MY_IMAP -w | head -c 5": True,
        "security find-generic-password -s X -w": True,
        "security find-generic-password -s X >/dev/null 2>&1; echo $?": False,
        'TOK=$(security find-generic-password -s X -w); curl -s -H "Authorization: Bearer $TOK" u': False,
        'curl -H "Authorization: Bearer $(security find-generic-password -s API_KEY -w)" u': False,
        "python3 smoke.py": False,
        "grep -rn 'find-generic-password' ~/tools": False,
    }
    bad = [c for c, want in cases.items() if bool(reason_for(c)) != want]
    assert not bad, bad
    assert reason_for(None) == ""
    print("selftest ok")
    return 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict) or data.get("tool_name") != "Bash":
            return 0
        r = reason_for((data.get("tool_input") or {}).get("command", ""))
        if r:
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Keychain: {r}. Check existence with `>/dev/null 2>&1; echo $?`; "
                                            "read values inside `$(...)` or inside a script, never to the screen.",
            }}))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
