# Changelog

All notable changes to way-stack are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/). Versioning follows [Semantic Versioning](https://semver.org/).

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
