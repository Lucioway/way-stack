---
name: reboot
description: Write the handoff, then restart with fresh context resuming from it. Use when the user says /reboot, "handoff and restart", "clear and continue", "restart with fresh context".
---

One command: handoff → clear → resume.

Steps:

1. Write/update the handoff doc exactly as the `handoff` skill specifies (Goal, Current Progress, What Worked, What Didn't Work, Next Steps). Save as `HANDOFF.md` in the project root, or update the existing one.

2. Arm the resume by writing the absolute handoff path to `~/.claude/.reboot-pending`:

   ```bash
   printf '%s\n' "<abs path to HANDOFF.md>" > ~/.claude/.reboot-pending
   ```

3. Tell the user, in one line: `Handoff written: <path>. Now run /clear — I will resume from it on my own.`

Then stop. Do not start new work in this context.

On the next session the `SessionStart` hook (matcher `clear`) reads `.reboot-pending`, injects the handoff path as context, and deletes the file — so the fresh session picks the work back up automatically.

`/clear` cannot be typed by the agent; that keystroke stays with the user. Everything around it is automatic.
