---
name: stack-verify
description: "Health check for way-stack install. Verifies vault structure, orchestrator presence, hooks, plugins, and design skills. Report-only — no mutations."
---

# /stack-verify — Stack Health Check

Run the 25 checks in order. For each, print ✓ / ✗ / ⚠ (or ℹ for optional items) with one-line detail. Exit 0 if no ✗, 1 if any ✗. This command is report-only.

## Checks

1. **Vault exists** — read user's configured vault path from `~/.claude/CLAUDE.md` or ask. Confirm PARA subdirs: `00_INBOX`, `01_PROJECTS`, `02_KNOWLEDGE/{patterns,decisions,retros,learnings}`, `03_REFERENCE`, `04_SESSIONS`, plus `index.md`, `log.md`.

2. **Orchestrator present** — `~/.claude/CLAUDE.md` exists + contains `MASTER ORCHESTRATOR` marker.

3. **Hooks installed** — `~/.claude/hooks/vault-session-log.sh` + `~/.claude/hooks/vault-auto-backup.sh` exist + executable.

4. **Hooks registered** — both `SessionEnd` hooks (`vault-session-log.sh`, `vault-auto-backup.sh`) are registered, either by the installed plugin's `hooks/hooks.json` (the normal case: the plugin is the single registration) or by `~/.claude/settings.json`. ✗ if neither; ⚠ if registered in BOTH places (they would run twice: remove the `settings.json` copies).

5. **Plugins installed** — read `~/.claude/plugins/installed_plugins.json`. Confirm: `superpowers`, `frontend-design`, `code-review`, `impeccable`. `ralph-loop`, `cli-anything`, `ponytail`, `claude-mem` are optional since v2.5.0 — report as ℹ, never ✗.

6. **Caveman installed** (own installer, not plugin) — PASS if ANY of: a `caveman-*.js`/`caveman-*.sh` file exists under `~/.claude/hooks/`, OR a caveman skill dir (`~/.claude/skills/caveman*`), OR a `caveman` reference in `~/.claude/settings.json`. (The `JuliusBrussee/caveman` installer detects each agent and wires itself in — exact artifact names vary by version, so don't hard-match old `caveman-activate.js`.)

7. **Design skills** — confirm each file exists: `~/.claude/skills/refactoring-ui/SKILL.md`, `~/.claude/skills/ui-ux-pro-max/SKILL.md`, `~/.claude/skills/hallmark/SKILL.md` (a directory without `SKILL.md` is a failed fetch: ✗ with the name). (`frontend-design` is plugin-level, not listed here.)

8. **Handoff skill** — `~/.claude/skills/handoff/SKILL.md` exists.

9. **Frameworks** (optional, ⚠ if missing — not ✗):
   - GSD: `~/.claude/get-shit-done/VERSION` exists + `~/.claude/skills/gsd-plan-phase/SKILL.md` present
   - BMAD: per-project installer, not global. Never ✗/⚠ when absent globally: report ℹ "optional, per project (run `npx -y bmad-method install` inside the project)". If `~/.claude/skills/bmad/core/bmad-master/SKILL.md` exists, report ✓.

10. **Vault git repo** — `$VAULT/.git` exists (auto-backup hook no-op without it).

11. **Auto-memory dir** — `~/.claude/projects/` exists (claude-mem auto-populates per-project memory dirs on first session).

12. **Graphify** — required part: `graphify` CLI on `$PATH` (`command -v graphify`) + `~/.claude/skills/graphify/` exists (✗ if missing). Optional part: `~/.claude.json` `mcpServers.graphify-vault` (or equivalent) registered (⚠ if missing, never ✗: the MCP is optional). ⚠ if the MCP is registered but `graph.json` doesn't exist yet: user just hasn't run `/graphify .` inside the vault.

13. **Power CLI tools** — `command -v` for each: `unclog`, `browser-harness`, `srt`, `gws`, `opencli`. ⚠ (not ✗) for `gws` and `opencli` if the binary is present but unauthenticated — both need a one-time human step (`gws auth setup`; OpenCLI Browser Bridge extension) that the bootstrap deliberately does not attempt.

14. **Fetched audit/video skills** — `~/.claude/skills/browser-harness/SKILL.md` exists; `improve` and `opencli-browser` resolve (either `~/.claude/skills/` or the project `.agents/skills/` dir `npx skills` writes to); at least one `seedance-*` dir present.

15. **Dead skill links** — no broken symlinks under `~/.claude/skills/` (`find ~/.claude/skills -maxdepth 2 -type l ! -exec test -e {} \; -print`). A skill dir whose `SKILL.md` points nowhere still shows up in the skill list and wastes a lookup. ✗ if any found, with the paths.

16. **Cost controls** — `~/.claude/settings.json` `env` has `CLAUDE_CODE_SUBAGENT_MODEL` (⚠ if missing: generic subagents inherit the main model) and `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` (⚠ if missing). ✗ if `model` in settings ends with `[1m]`. `~/.claude/way-stack-inventory.md` and `~/.claude/mcp-grounding.json` exist.

17. **Orchestrator is lean** — `wc -c ~/.claude/CLAUDE.md` ≤ 8000 bytes (⚠ above: it loads into every prompt; move lists to `~/.claude/way-stack-inventory.md`). ✗ if it still mentions `gstack` or `/office-hours` (dead routes from before v2.4.0).

18. **Token management** — `~/.claude/token-budget/bin/{token_tracker.py,ctx_guard.py,api_map.py,baseline.sh}` exist; `settings.json` has a `Stop` hook pointing at `ctx_guard.py`; a daily schedule exists (`launchctl list | grep token-tracker` or `crontab -l | grep token_tracker`) — ⚠ if not. If `~/.claude/token-budget/db.json` exists, print the latest day's Ctx/turn and % >200k: ⚠ when Ctx/turn > 150k or >200k share > 5%.

19. **Behavior hooks** — `hooks/hooks.json` of the installed plugin registers `prompt-reflex.py` under `UserPromptSubmit` (✗ if not). `closing-guard` is opt-in: if `~/.claude/hooks/closing-guard.py` exists, confirm `settings.json` has a `Stop` hook pointing at it and `python3 ~/.claude/hooks/closing-guard.py --selftest` passes; if absent, ⚠ "not opted in" (never ✗).

20. **AnyDoc** — `command -v anydoc` (⚠ if missing: `vault-ingest` cannot convert Office files; `npm install -g @firecrawl/anydoc`).

21. **vault-index** — the `vault-index` skill exists with `scripts/vault_index.py`, and `python3 <script> --vault "$VAULT" --dry` ends with `changes=0` (⚠ otherwise: run it once without `--dry`, then re-check).

22. **Guard hooks + agents** — for each of `post-edit-test.py`, `big-read-guard.py`, `compact-counter.py`, `no-overwrite-reports.py`, `keychain-guard.py` present in `~/.claude/hooks/`: `settings.json` references it and `--selftest` passes (✗ if present but unregistered or failing; ⚠ "not opted in" if absent, never ✗). `agents/custodian.md` and `agents/silent-failure-hunter.md` exist in the installed plugin (✗ if missing). No `*.md` in subfolders of `~/.claude/agents/` (✗: subfolders get loaded as agents too).

23. **Watch plugin** — `watch` appears in `~/.claude/plugins/installed_plugins.json` (⚠ if missing, never ✗: `/plugin install watch@claude-video`).

24. **Power skills** — `~/.claude/skills/{qa-test,agent-browser,agent-reach,browser-harness}/SKILL.md` each exist (⚠ per missing one, never ✗; `agent-browser` may also live where `npx skills ... -g -a claude-code` put it, so accept any path that resolves).

25. **Reboot hook** — `~/.claude/hooks/reboot-resume.sh` exists + executable, and `~/.claude/settings.json` has a `SessionStart` entry (matcher `clear`) pointing at it (⚠ if either is missing: the `reboot` skill will not auto-resume).

## Output format

Print one line per check (grouped as below), then the result line.

```
way-stack verify

✓ 1  Vault              — 7 dirs, index.md + log.md present
✓ 2  Orchestrator       — ~/.claude/CLAUDE.md (MASTER ORCHESTRATOR marker)
✓ 3  Hooks              — session-log + auto-backup, both +x
✓ 4  Hooks registered   — SessionEnd wired via the plugin's hooks.json
✓ 5  Plugins            — superpowers, frontend-design, code-review, impeccable
✓ 6  Caveman            — hook files found
⚠ 7  Design skills      — ui-ux-pro-max/SKILL.md missing
✓ 8  Handoff skill      — SKILL.md present
✓ 9  Frameworks         — GSD ✓ · BMAD ℹ optional, per project
✓ 10 Vault git          — 12 commits
✓ 11 Auto-memory dir    — ~/.claude/projects exists
✓ 12 Graphify           — CLI + skill ✓ · MCP ⚠ not registered (optional)
✓ 13 Power CLI tools    — unclog, browser-harness, srt, gws, opencli
✓ 14 Fetched skills     — browser-harness, improve, opencli-browser, seedance-*
✓ 15 Dead skill links   — none
✓ 16 Cost controls      — env + inventory + grounding kit
✓ 17 Orchestrator lean  — 6.1 KB
✓ 18 Token management   — scripts, Stop hook, daily schedule
✓ 19 Behavior hooks     — prompt-reflex registered, closing-guard opt-in
⚠ 20 AnyDoc             — not installed
✓ 21 vault-index        — changes=0
✓ 22 Guard hooks+agents — 2 agents, no opt-in guards
✓ 23 Watch plugin       — installed
✓ 24 Power skills       — 4/4 SKILL.md present
✓ 25 Reboot hook        — installed + registered

Result: 22 ✓, 3 ⚠, 0 ✗ — mostly healthy. Fix: re-run /way-stack:stack-bootstrap step 9.
```
