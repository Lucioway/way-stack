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

5. **Plugins installed** — read `~/.claude/plugins/installed_plugins.json`. Confirm: `superpowers`, `frontend-design`, `code-review`, `ralph-loop`, `cli-anything`. `claude-mem` is ⚠ (optional) — the native auto-memory covers the same need.

6. **Caveman installed** (own installer, not plugin) — PASS if ANY of: a `caveman-*.js`/`caveman-*.sh` file exists under `~/.claude/hooks/`, OR a caveman skill dir (`~/.claude/skills/caveman*`), OR a `caveman` reference in `~/.claude/settings.json`. (The `JuliusBrussee/caveman` installer detects each agent and wires itself in — exact artifact names vary by version, so don't hard-match old `caveman-activate.js`.)

7. **Design skills** — confirm dirs under `~/.claude/skills/`: `refactoring-ui`, `ui-ux-pro-max`, `hallmark`. (`frontend-design` is plugin-level, not listed here.)

8. **Handoff skill** — `~/.claude/skills/handoff/SKILL.md` exists.

9. **Frameworks** (optional, ⚠ if missing — not ✗):
   - GSD: `~/.claude/get-shit-done/VERSION` exists + `~/.claude/skills/gsd-plan-phase/SKILL.md` present
   - BMAD: `~/.claude/skills/bmad/core/bmad-master/SKILL.md` present

10. **Vault git repo** — `$VAULT/.git` exists (auto-backup hook no-op without it).

11. **Auto-memory dir** — `~/.claude/projects/` exists (claude-mem auto-populates per-project memory dirs on first session).

12. **Graphify** — `graphify` CLI on `$PATH` (`command -v graphify`) + `~/.claude/skills/graphify/` exists + `~/.claude.json` `mcpServers.graphify-vault` (or equivalent) registered. ⚠ if MCP server registered but `graph.json` doesn't exist yet — user just hasn't run `/graphify .` inside the vault.

13. **Power CLI tools** — `command -v` for each: `unclog`, `browser-harness`, `srt`, `gws`, `opencli`. ⚠ (not ✗) for `gws` and `opencli` if the binary is present but unauthenticated — both need a one-time human step (`gws auth setup`; OpenCLI Browser Bridge extension) that the bootstrap deliberately does not attempt.

14. **Fetched audit/video skills** — `~/.claude/skills/browser-harness/SKILL.md` exists; `improve` and `opencli-browser` resolve (either `~/.claude/skills/` or the project `.agents/skills/` dir `npx skills` writes to); at least one `seedance-*` dir present.

## Output format

```
way-stack verify

✓ Vault          — 7 dirs, index.md + log.md present
✓ Orchestrator   — ~/.claude/CLAUDE.md (42 routing rules)
✓ Hooks          — session-log + auto-backup, both +x
✓ Hooks registered — SessionEnd wired
✓ Plugins        — 5/5 installed
⚠ Design skills  — 3/3 present, ui-ux-pro-max SKILL.md missing
✓ Frameworks     — GSD ✓ BMAD ✓
✓ Vault git      — 12 commits

Result: 7 ✓, 1 ⚠ — mostly healthy. Fix: re-run /stack-bootstrap step 9.
```

15. **Dead skill links** — no broken symlinks under `~/.claude/skills/` (`find ~/.claude/skills -maxdepth 2 -type l ! -exec test -e {} \; -print`). A skill dir whose `SKILL.md` points nowhere still shows up in the skill list and wastes a lookup. ✗ if any found, with the paths.
