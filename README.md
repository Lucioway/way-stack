# way-stack

**One-link Claude Code stack replicator.** Three commands → full dev environment: master orchestrator, PARA + Karpathy LLM Wiki vault, Spec-Driven Development (SDD) agent factory, session-persistence hooks, 6 upstream plugins, 7 design skills, and 3 optional frameworks (GSD, BMAD, gstack) wired up.

Designed to replicate a complete Claude Code "pro" setup on any fresh machine in three commands.

## What you get

| Layer | What |
|---|---|
| **Master orchestrator** | `~/.claude/CLAUDE.md` — routing tree: classifies every request → picks the right skill/framework |
| **Vault** | PARA folders (`00_INBOX`, `01_PROJECTS`, `02_KNOWLEDGE`, `03_REFERENCE`, `04_SESSIONS`) + Karpathy LLM Wiki (`index.md` + `log.md`) |
| **Hooks** | Auto-session log + git auto-backup of vault on `SessionEnd` |
| **Agent factory** | `/agent-spec` → `/agent-tasks` → `/agent-execute` → `/agent-verify` → `/agent-ship` — full SDD flow |
| **Vault skills** | `vault-ingest`, `vault-query`, `vault-lint` (Karpathy wiki ops) |
| **Plugins installed** | superpowers, frontend-design, code-review, cli-anything, ralph-loop, caveman |
| **Design skills fetched** | refactoring-ui, ux-heuristics, hooked-ux, design-sprint, ios-hig-design, ui-ux-pro-max |
| **Frameworks (optional)** | GSD (~70 `gsd-*` skills), BMAD v6 (9 `bmad:*` skills), gstack (~38 skills + headless browser) |

## Install — 3 commands

### 1. Add marketplace + install way-stack

In Claude Code:

```
/plugin marketplace add Lucioway/way-stack
/plugin install way-stack
```

### 2. Bootstrap the stack

```
/stack-bootstrap
```

It will ask once where your vault should live (default `~/Workspace`), then install everything. Asks once whether to install the heavyweight frameworks (GSD/BMAD/gstack) — default = all.

### 3. Verify

```
/stack-verify
```

Expected: all ✓. Any ⚠ includes a fix hint.

## Usage

Once bootstrapped, every request is routed by the orchestrator. Examples:

| You say… | way-stack routes to… |
|---|---|
| "build me an agent that summarizes my inbox every morning" | `create-agent` skill → `/agent-spec` → SDD flow |
| "UI looks off, fix it" | `refactoring-ui` skill |
| "what do we know about rate-limiting Gmail API?" | `vault-query` skill |
| "save this article on RAG patterns" | `vault-ingest` skill |
| "new project, full web app, auth + payments" | orchestrator asks size → picks framework |

## Anatomy

```
way-stack/
├── .claude-plugin/plugin.json
├── commands/              # /stack-bootstrap, /stack-verify, /agent-*
├── skills/                # create-agent, vault-{ingest,query,lint}
├── hooks/                 # session log + auto-backup
├── templates/             # orchestrator CLAUDE.md, vault CLAUDE.md, project CLAUDE.md
├── references/            # SDD framework doc
├── README.md
└── LICENSE                # MIT
```

## Upstream dependencies (fetched by `/stack-bootstrap`)

| Dependency | Source | Purpose |
|---|---|---|
| superpowers | obra/superpowers-marketplace | TDD, debug, brainstorming, worktrees |
| frontend-design | anthropics/claude-plugins | Production-grade UI generation |
| code-review | anthropics/claude-plugins | Multi-agent parallel review |
| cli-anything | HKUDS/CLI-Anything | GUI-OSS CLI wrappers |
| ralph-loop | anthropics/claude-plugins | Autonomous iteration loop |
| caveman | JuliusBrussee/claude-code-caveman | Terse-mode prompt compression |
| refactoring-ui, ux-heuristics, hooked-ux, design-sprint, ios-hig-design | wondelai/skills | Design skills |
| ui-ux-pro-max | nextlevelbuilder/ui-ux-pro-max-skill | Full design system skill |
| **GSD** (optional) | gsd-build/get-shit-done (`npx get-shit-done-cc --claude --global`) | Spec-driven dev framework, ~70 skills |
| **BMAD v6** (optional) | bmad-code-org/BMAD-METHOD (`npx bmad-method install`) | Agile multi-role methodology, 9 skills |
| **gstack** (optional) | garrytan/gstack (git clone + `./setup`) | Garry Tan's virtual team, ~38 skills + browser |

way-stack does NOT redistribute these — it adds their marketplaces / runs their canonical installers at bootstrap time. They stay on their own update tracks.

## Philosophy

**Orchestrator + vault + SDD** is the minimum viable "pro" Claude Code setup. Everything else is optional layering.

- **Orchestrator** picks the tool. You stop hand-routing every request.
- **Vault** persists what you learn across sessions. Claude reads it instead of re-asking.
- **SDD** enforces spec → tasks → verify → ship. Stops the "Claude wrote 500 lines I didn't ask for" failure mode.

Everything else (gstack roles, BMAD agile, advanced debugging) layers cleanly on top if you want it.

## Uninstall

```
/plugin uninstall way-stack
```

Vault and orchestrator `~/.claude/CLAUDE.md` are not removed — they're yours. Delete manually if desired:

```bash
rm ~/.claude/CLAUDE.md ~/.claude/hooks/vault-*.sh
# vault stays untouched — it's your knowledge
```

## Contributing

PRs welcome. Focus areas:
- Additional `/agent-*` phases (e.g., `/agent-refine` for mid-milestone pivots)
- Alternate vault layouts (Zettelkasten, LYT)
- Framework-specific bootstrap variants (Rails, Django, Next.js)

## License

MIT
