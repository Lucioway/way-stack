#!/bin/sh
# Armed by the /reboot skill: after /clear, point the fresh session at the handoff.
# ponytail: single global pending file, one reboot in flight at a time.
P="$HOME/.claude/.reboot-pending"
[ -f "$P" ] || exit 0
H=$(head -n1 "$P")
rm -f "$P"
[ -f "$H" ] || exit 0
python3 - "$H" <<'EOF'
import json, sys
h = sys.argv[1]
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": f"REBOOT RESUME: the previous session ended with /reboot. Read {h} and continue that work from its Next Steps. Do not re-do what Current Progress already lists."
}}))
EOF
