# Changelog

All notable changes to way-stack are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/). Versioning follows [Semantic Versioning](https://semver.org/).

## v1.2.0 — 2026-05-27

### Added
- **claude-mem** (`thedotmack/claude-mem`) — persistent auto-memory across sessions. Adds `$cmem` recap at session start, typed memory files (user / feedback / project / reference) under `~/.claude/projects/<proj>/memory/MEMORY.md`. STEP 7 (marketplace) + STEP 8 (plugin install) updated.
- **handoff** skill — bundled in `templates/skills/handoff/SKILL.md` and installed by new STEP 10. Writes `HANDOFF.md` so the next fresh-context agent can resume.
- **caveman** install via repo `install.sh` (instead of broken `/plugin install`) — drops `caveman-activate.js`, `caveman-mode-tracker.js`, `caveman-config.js`, `caveman-statusline.sh` into `~/.claude/hooks/` and wires SessionStart + UserPromptSubmit.
- New STEP 12 — scaffold `~/.claude/projects/` for claude-mem.
- Orchestrator template: 2 new HARD RULES (auto-skill check via `superpowers:using-superpowers`, `/handoff` at end-of-session), 3 new cheatsheet rows (handoff, caveman, $cmem).
- `/stack-verify` — 3 new checks: caveman hooks (#6), handoff skill (#8), auto-memory dir (#11).

### Changed
- **Marketplace name fix**: `anthropics/claude-plugins` → `anthropics/claude-plugins-official` (correct upstream name). Dropped redundant `obra/superpowers-marketplace` — superpowers ships in `claude-plugins-official` now.
- Marketplace count: 5 → 3 (only `claude-plugins-official`, `HKUDS/CLI-Anything`, `thedotmack/claude-mem` needed; caveman uses repo installer).
- Bootstrap: 11 steps → 13 steps.
- GSD framework: ~70 skills → 90+ (added `gsd-list-workspaces`, `gsd-set-profile`, `gsd-profile-user`, `gsd-thread`, `gsd-extract_learnings`, …).
- BMAD framework: 9 skills → 15 (v6 expanded).
- README: updated upstream table, "What you get" rows, bundled skills row.

### Fixed
- Caveman: was listed as `/plugin install caveman@claude-code-caveman` (never worked — caveman is hook-based, not a Claude Code plugin). Now uses its canonical `install.sh`.
- Superpowers marketplace reference (`obra/...`) removed — broken since Anthropic absorbed it into the official marketplace.

### Why
v1.1.0 install flow had two broken marketplace references and missed the two most-used additions of the past 24 days: claude-mem (persistent memory) and the `handoff` skill. Without claude-mem the orchestrator's "read `MEMORY.md` first" rule is a no-op — the dir doesn't exist. v1.2.0 closes that gap so a fresh install matches the live stack 1:1.

## v1.1.0 — 2026-05-03

### Added
- `/stack-bootstrap` STEP 10 — optional install of three heavyweight frameworks:
  - **GSD** (`gsd-build/get-shit-done`) via `npx get-shit-done-cc --claude --global`
  - **BMAD v6** (`bmad-code-org/BMAD-METHOD`) via `npx bmad-method install`
  - **gstack** (`garrytan/gstack`) via git clone + `./setup`
- `caveman` plugin (`JuliusBrussee/claude-code-caveman`) added to STEP 8 install list — marketplace was already registered in STEP 7 but plugin was never installed
- `/stack-verify` — new check #7 confirms framework presence (warn-only, not fail)

### Changed
- README "What you get" + "Upstream dependencies" sections list new plugins/frameworks
- Bootstrap is now an 11-step flow (was 10)
- Plugin description updated: "6 plugins" + "3 frameworks"
- README install line corrected: `Lucioway/way-stack` (was `lcwy9671/way-stack` — wrong owner)

### Why
Goal: a single link that replicates the entire operational Claude stack on a fresh machine. v1.0.x covered orchestrator + vault + 5 plugins + design skills, but missed the three frameworks (GSD/BMAD/gstack) that the orchestrator routes to. Replica was incomplete.

## v1.0.1 — 2026-04-24

### Added
- `/stack-publish` command — one-shot release flow (version bump + CHANGELOG + commit + tag + push)
- `CHANGELOG.md` — this file

### Fixed
- Corrected GitHub owner from `lcwy9671` to `Lucioway` in `plugin.json` and `marketplace.json`

## v1.0.0 — 2026-04-24

### Added
- Initial release
- Master orchestrator template (`templates/orchestrator-CLAUDE.md`) — routing tree across plugins, skills, frameworks
- PARA + Karpathy LLM Wiki vault template (`templates/vault-CLAUDE.md`)
- SDD agent factory flow: `/agent-spec`, `/agent-tasks`, `/agent-execute`, `/agent-verify`, `/agent-ship`
- 4 auto-activating skills: `create-agent`, `vault-ingest`, `vault-query`, `vault-lint`
- SessionEnd hooks: `vault-session-log.sh` + `vault-auto-backup.sh`
- `/stack-bootstrap` — 10-step installer that adds 5 upstream marketplaces and fetches 7 design skills
- `/stack-verify` — health check
- MIT license
