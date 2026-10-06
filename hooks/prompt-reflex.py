#!/usr/bin/env python3
# UserPromptSubmit hook: two reflexes that rules in memory alone never enforced.
#  1) prompt contains an image path -> Read every image FIRST; "these/this" = what is inside.
#  2) short status ping ("done?", "where are we") -> answer in text NOW, zero tool calls first.
# Never blocks: only injects additionalContext. Any error -> silent pass.
import json
import re
import sys

# Local paths only: not inside URLs, no hopping across " /next/path" (spaces allowed, e.g. macOS
# "Screenshot 2026-01-01 at 10.00.00.png").
IMG = re.compile(
    r"(?<![\w:/.~])(~?\.{0,2}/(?:[^\s\"'<>|]|[ \t](?![/~]))*?\.(?:png|jpe?g|heic|webp|gif))(?!\w)", re.I
)
STATUS = re.compile(
    r"\b(done|finished|status|where are we|where we at|how'?s it going|how is it going|"
    r"what'?s left|what is left|what do i (?:need|have) to do|what should i do|"
    r"any (?:update|news|progress)|updates?\s*\?|eta|recap)\b",
    re.I,
)


def is_status_ping(prompt: str) -> bool:
    """Short prompt that IS a status question: keyword + ends with '?', or opens with the keyword.
    "fix the header, done when tests pass" is an instruction, not a ping."""
    if len(prompt) > 80 or not STATUS.search(prompt):
        return False
    return prompt.rstrip().endswith("?") or bool(STATUS.match(prompt.lstrip(" ,.!-")))


def build(prompt: str):
    ctx = []
    if "<task-notification>" in prompt:  # background-agent events are not user prompts
        return ctx
    paths = list(dict.fromkeys(p.strip() for p in IMG.findall(prompt)))
    if paths:
        ctx.append(
            "[Image] The prompt contains image files: " + " | ".join(paths[:6]) + ". FIRST action: "
            "Read every one of them with the Read tool and look at what is inside. 'these/this' in "
            "the prompt refers to what is inside the image. Never ask the user what it shows."
        )
    if not paths and is_status_ping(prompt):
        ctx.append(
            "[Status] The user is asking for status. Answer NOW in plain text with zero tool calls "
            "first: what is done, what is still running, what is left, what needs the user. "
            "Then continue the work if needed."
        )
    return ctx


def main() -> None:
    try:
        prompt = (json.load(sys.stdin).get("prompt") or "").strip()
        ctx = build(prompt)
    except Exception:
        ctx = []
    if ctx:
        print(json.dumps({
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": " ".join(ctx),
            },
        }))
    else:
        print(json.dumps({"continue": True, "suppressOutput": True}))


if __name__ == "__main__":
    main()
