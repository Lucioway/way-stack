# way-stack

**One-link Claude Code stack replicator.** Three commands → full dev environment: master orchestrator, PARA + Karpathy LLM Wiki vault, Spec-Driven Development (SDD) agent factory, session-persistence hooks, 6 upstream plugins, 7 design skills, and 3 optional frameworks (GSD, BMAD, gstack) wired up.

Designed to replicate a complete Claude Code "pro" setup on any fresh machine in three commands.

## What you get

| Layer | What |
|---|---|
| **Master orchestrator** | `~/.claude/CLAUDE.md` — routing tree: classifies every request → picks the right skill/framework |
| **Vault** | PARA folders (`00_INBOX`, `01_PROJECTS`, `02_KNOWLEDGE`, `03_REFERENCE`, `04_SESSIONS`) + Karpathy LLM Wiki (`index.md` + `log.md`) |
| **Hooks** | Auto-session log + git auto-backup of vault on `SessionEnd` |
| **Agent factory** | `/agent-spec` → `/agent-tasks` → `/agent-execute` → `/agent-verify` → `/agent-ship` — full SDD flow + bundled references (full SDD framework w/ Mega Prompt, agent design principles, CLI tools stack) |
| **Agent monitor** | `templates/agent-monitor/` — real-time 3D dashboard (WebSocket + Three.js) for your agent fleet: launchd/process/log state, errors, last outputs |
| **Deploy agent** | `deploy-project` skill — conversational 10-step deploy pipeline to Vercel (preflight, deep scan, 5-level security audit, auth, build test, git, preview, production, registry) + scriptable Python CLI at `templates/deploy-agent/` |
| **Vault skills** | `vault-ingest`, `vault-query`, `vault-lint` (Karpathy wiki ops) |
| **Plugins installed** | superpowers, frontend-design, code-review, ralph-loop, cli-anything, **claude-mem** (auto-memory) |
| **Hook-based add-ons** | caveman (terse mode) — installs SessionStart + UserPromptSubmit hooks via its own installer |
| **Knowledge-graph layer** | **graphify** — `/graphify .` builds a graph from any folder of `.md`/`.json`/code. Queryable from Claude via MCP (`query_graph`, `shortest_path`, `god_nodes`, `get_neighbors`). Replaces hand-curated wikilinks with analytical traversal. |
| **Design skills fetched** | refactoring-ui, ux-heuristics, hooked-ux, design-sprint, ios-hig-design, ui-ux-pro-max |
| **Bundled skills** | create-agent, **deploy-project**, vault-ingest, vault-query, vault-lint, **handoff** |
| **Frameworks (optional)** | GSD (90+ `gsd-*` skills), BMAD v6 (15 `bmad:*` skills), gstack (~38 skills + headless browser) |

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
| "deploy this project: /path/to/app" | `deploy-project` skill — 10-step secure deploy to Vercel |
| "new project, full web app, auth + payments" | orchestrator asks size → picks framework |

## Anatomy

```
way-stack/
├── .claude-plugin/plugin.json
├── commands/              # /stack-bootstrap, /stack-verify, /agent-*
├── skills/                # create-agent, deploy-project, vault-{ingest,query,lint}
├── hooks/                 # session log + auto-backup
├── templates/             # orchestrator CLAUDE.md, vault CLAUDE.md, project CLAUDE.md,
│   ├── agent-monitor/     #   3D live dashboard for the agent fleet (monitor.py + Three.js)
│   └── deploy-agent/      #   scriptable deploy CLI (scan → audit → auth → git → Vercel)
├── references/            # SDD framework (full, w/ Mega Prompt), agent design principles, CLI tools stack
├── README.md
└── LICENSE                # MIT
```

## Upstream dependencies (fetched by `/stack-bootstrap`)

| Dependency | Source | Purpose |
|---|---|---|
| superpowers | anthropics/claude-plugins-official | TDD, debug, brainstorming, worktrees, verification-before-completion, dispatching-parallel-agents |
| frontend-design | anthropics/claude-plugins-official | Production-grade UI generation |
| code-review | anthropics/claude-plugins-official | Multi-agent parallel review |
| ralph-loop | anthropics/claude-plugins-official | Autonomous iteration loop |
| cli-anything | HKUDS/CLI-Anything | GUI-OSS CLI wrappers |
| **claude-mem** | thedotmack/claude-mem | Persistent auto-memory across sessions (`$cmem` recap, typed memory files) |
| caveman (hook-based) | JuliusBrussee/claude-code-caveman | Terse-mode prompt compression — installed via its own `install.sh` |
| **graphify** | safishamsi/graphifyy (pip `graphifyy`) | Knowledge-graph builder + MCP server. `/graphify .` extracts entities/edges from any folder; MCP exposes graph to Claude (`query_graph`, `get_node`, `get_neighbors`, `shortest_path`, `god_nodes`) |
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
