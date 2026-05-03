# Changelog

All notable changes to way-stack are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/). Versioning follows [Semantic Versioning](https://semver.org/).

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
