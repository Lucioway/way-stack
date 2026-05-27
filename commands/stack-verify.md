---
name: stack-verify
description: "Health check for way-stack install. Verifies vault structure, orchestrator presence, hooks, plugins, and design skills. Report-only — no mutations."
---

# /stack-verify — Stack Health Check

Run checks in order. For each, print ✓ / ✗ / ⚠ with one-line detail. Exit 0 if all ✓, 1 if any ✗.

## Checks

1. **Vault exists** — read user's configured vault path from `~/.claude/CLAUDE.md` or ask. Confirm PARA subdirs: `00_INBOX`, `01_PROJECTS`, `02_KNOWLEDGE/{patterns,decisions,retros,learnings}`, `03_REFERENCE`, `04_SESSIONS`, plus `index.md`, `log.md`.

2. **Orchestrator present** — `~/.claude/CLAUDE.md` exists + contains `MASTER ORCHESTRATOR` marker.

3. **Hooks installed** — `~/.claude/hooks/vault-session-log.sh` + `~/.claude/hooks/vault-auto-backup.sh` exist + executable.

4. **Hooks registered** — `~/.claude/settings.json` has `SessionEnd` entries pointing to both hook scripts.

5. **Plugins installed** — read `~/.claude/plugins/installed_plugins.json`. Confirm: `superpowers`, `frontend-design`, `code-review`, `ralph-loop`, `cli-anything`, `claude-mem`.

6. **Caveman installed** (hook-based, not plugin) — `~/.claude/hooks/caveman-activate.js` + `~/.claude/hooks/caveman-mode-tracker.js` exist and are referenced in `~/.claude/settings.json` SessionStart + UserPromptSubmit.

7. **Design skills** — confirm dirs under `~/.claude/skills/`: `refactoring-ui`, `ux-heuristics`, `hooked-ux`, `design-sprint`, `ios-hig-design`, `ui-ux-pro-max`. (`frontend-design` is plugin-level, not listed here.)

8. **Handoff skill** — `~/.claude/skills/handoff/SKILL.md` exists.

9. **Frameworks** (optional, ⚠ if missing — not ✗):
   - GSD: `~/.claude/get-shit-done/VERSION` exists + `~/.claude/skills/gsd-plan-phase/SKILL.md` present
   - BMAD: `~/.claude/skills/bmad/core/bmad-master/SKILL.md` present
   - gstack: `~/.claude/skills/gstack/package.json` present + `browse/dist/browse` binary executable

10. **Vault git repo** — `$VAULT/.git` exists (auto-backup hook no-op without it).

11. **Auto-memory dir** — `~/.claude/projects/` exists (claude-mem auto-populates per-project memory dirs on first session).

## Output format

```
way-stack verify

✓ Vault          — 7 dirs, index.md + log.md present
✓ Orchestrator   — ~/.claude/CLAUDE.md (42 routing rules)
✓ Hooks          — session-log + auto-backup, both +x
✓ Hooks registered — SessionEnd wired
✓ Plugins        — 6/6 installed
⚠ Design skills  — 6/6 present, ui-ux-pro-max SKILL.md missing
✓ Frameworks     — GSD ✓ BMAD ✓ gstack ✓
✓ Vault git      — 12 commits

Result: 7 ✓, 1 ⚠ — mostly healthy. Fix: re-run /stack-bootstrap step 9.
```
