#!/usr/bin/env python3
"""Claude Code Stop hook (OPT-IN): enforce the orchestrator's closing summary.

Work turn = at least one tool_use after the last real user message. Then:
  (a) final text (after the last tool call) lacks the "✅ Done" marker -> block once;
  (b) a closing LINE asks the user for a go-ahead/choice on reversible work, and that same line
      names no real gate (ads, messages to people, deploy, money, deletion, accounts, sign-off,
      creative taste) -> block once.
stop_hook_active -> pass (no loops). Headless runs (entrypoint sdk*) -> pass. Missing transcript -> pass.

Test:  python3 closing-guard.py --test <transcript.jsonl>     python3 closing-guard.py --selftest
"""
import json
import os
import re
import sys
from pathlib import Path

MARK = "✅ Done"
REASON = (
    "The mandatory closing is missing. Add, after a blank line and `---`, in plain everyday words: "
    "`> **✅ Done** — 2-6 bullets, each a TRUE change (file, service, account, money; failures stated)`; "
    "`> **👉 Now** — 0-4 bullets, only things that need the user's hand, else `nothing, you're set``."
)

# Closing lines that hand back work Claude could finish itself.
GO_ASK = re.compile(
    r"(?:\b(?:say|type|reply|tell\s+me|send\s+me)\s+(?:me\s+)?[\"'`*«]*go\b"
    r"|\bwant\s+me\s+to\s+(?:proceed|continue|do\s+it|fix|apply|run)\b"
    r"|\bshall\s+i\b"
    r"|\bshould\s+i\s+(?:proceed|continue)\b"
    r"|\bproceed\s*\?"
    r"|\blet\s+me\s+know\s+if\b"
    r"|\bpick\s+(?:a|1|one)\b"
    r"|\bwhich\s+(?:one\s+)?do\s+you\s+prefer\b"
    r"|\bconfirm\s*\?)",
    re.I,
)
# A real gate: the user's hand is genuinely needed.
GATE = re.compile(
    r"(?:\bads?\b|campaign|ad\s?set|budget"
    r"|\bmessages?\b|e-?mails?|\bposts?\b|customers?|clients?"
    r"|deploy|production|\blive\b|publish|\bpush\b|release|merge"
    r"|money|payments?|\bpay\b|purchas|refund|invoice|\bprice|\bpricing"
    r"|delete|remove|uninstall|revoke|rotate"
    r"|account|log\s?in|password|credential"
    r"|contract|\bsign\b|signature"
    r"|policy|decision|approv"
    r"|\bphotos?\b|\bvideos?\b|design|\bcopy\b)",
    re.I,
)
GO_REASON = (
    "The closing asks the user for a go-ahead or a choice on work you can finish yourself. Finish the "
    "reversible work now. If the user's hand is truly needed (ads, messages to people, deploy/live, "
    "money, deletion, accounts, sign-off, creative taste), name the exact gate and why in the "
    "closing instead of a generic 'say go'."
)


def unjustified_go_ask(text: str) -> bool:
    """True if some line asks for a go/choice without naming a real gate on the same line."""
    return any(GO_ASK.search(ln) and not GATE.search(ln) for ln in text.splitlines())


def last_turn(path: Path):
    """Return (had_tool_use, final_text) for the turn after the last real user message."""
    turn = []
    for ln in path.read_text(errors="ignore").splitlines():
        try:
            m = json.loads(ln)
        except Exception:
            continue
        msg = m.get("message") or {}
        role = msg.get("role") or m.get("type")
        content = msg.get("content")
        if role == "user" and (
            isinstance(content, str)
            or (isinstance(content, list) and any(c.get("type") == "text" for c in content if isinstance(c, dict)))
        ):
            turn = []  # real user message (not a tool_result)
            continue
        turn.append(m)
    had_tool, texts = False, []
    for m in turn:
        msg = m.get("message") or {}
        if (msg.get("role") or m.get("type")) != "assistant":
            continue
        for c in msg.get("content") or []:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "tool_use":
                had_tool, texts = True, []
            elif c.get("type") == "text" and c.get("text", "").strip():
                texts.append(c["text"])
    # empty final text = transcript lagging behind -> do not block
    return had_tool, ("\n".join(texts) if texts else MARK)


def is_headless(path: Path) -> bool:
    ep = os.environ.get("CLAUDE_CODE_ENTRYPOINT", "")
    if not ep:
        for ln in path.read_text(errors="ignore").splitlines()[:50]:
            try:
                ep = json.loads(ln).get("entrypoint") or ""
            except Exception:
                continue
            if ep:
                break
    return ep.startswith("sdk")


def decide(payload: dict) -> dict:
    if not isinstance(payload, dict) or payload.get("stop_hook_active"):
        return {}
    p = payload.get("transcript_path")
    if not isinstance(p, str) or not p or not Path(p).is_file() or is_headless(Path(p)):
        return {}
    try:
        had_tool, text = last_turn(Path(p))
    except Exception:
        return {}
    if had_tool and MARK not in text:
        return {"decision": "block", "reason": REASON}
    if had_tool and unjustified_go_ask(text):
        return {"decision": "block", "reason": GO_REASON}
    return {}


def selftest() -> int:
    bad = [
        "Say go and I will fix it.", "Want me to proceed?", "Shall I continue with the refactor?",
        "Should I proceed?", "Proceed?", "Let me know if that works.", "Pick A or B.",
        "Which one do you prefer?", "Confirm?", "Reply go when ready.",
    ]
    good = [
        "Want me to deploy to production?", "Shall I send the email to the customers?",
        "Which design do you prefer?", "Say go and I will delete the old branch.",
        "Let me know if the refund price is fine.", "All done, tests pass.",
    ]
    for t in bad:
        assert unjustified_go_ask(t), ("should flag", t)
    for t in good:
        assert not unjustified_go_ask(t), ("should pass", t)
    assert decide({"stop_hook_active": True}) == {}
    assert decide({}) == {}
    assert decide([]) == {}
    assert decide({"transcript_path": 5}) == {}
    print("selftest ok:", len(bad) + len(good) + 4, "asserts")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    if len(sys.argv) > 2 and sys.argv[1] == "--test":
        print(last_turn(Path(sys.argv[2])))
        return 0
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    try:
        out = decide(payload)
    except Exception:  # a guard must never crash the session
        return 0
    if out:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
