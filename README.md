# way-stack

**One-link Claude Code stack replicator.** Three commands → full dev environment: lean master orchestrator (head/arms model routing + loop-first mode), PARA + Karpathy LLM Wiki vault, workflow skills (handoff, reboot, dream, session-audit, context-budget, **token-budget**, council, claudex-loop), session-persistence hooks, 6 upstream plugins (4 more optional), 3 design skills, 5 agent-native CLI tools, and 2 optional frameworks (GSD, BMAD) wired up.

Designed to replicate a complete Claude Code "pro" setup on any fresh machine in three commands.

## What you get

| Layer | What |
|---|---|
| **Master orchestrator** | `~/.claude/CLAUDE.md` — routing tree: classifies every request → picks the right skill/framework |
| **Vault** | PARA folders (`00_INBOX`, `01_PROJECTS`, `02_KNOWLEDGE`, `03_REFERENCE`, `04_SESSIONS`) + Karpathy LLM Wiki (`index.md` + `log.md`) |
| **Hooks** | Auto-session log + git auto-backup of vault on `SessionEnd` |
| **Agent monitor** | `templates/agent-monitor/` — real-time 3D dashboard (WebSocket + Three.js) for your agent fleet: launchd/process/log state, errors, last outputs |
| **Deploy agent** | `deploy-project` skill — conversational 10-step deploy pipeline to Vercel (preflight, deep scan, 5-level security audit, auth, build test, git, preview, production, registry) + scriptable Python CLI at `templates/deploy-agent/` |
| **Vault skills** | `vault-ingest`, `vault-query`, `vault-lint` (Karpathy wiki ops) |
| **Plugins installed** | superpowers, frontend-design, code-review, **impeccable** (design fluency), **watch** (video Q&A), **mattpocock-skills** (process skills). Optional since v2.5.0 (default off — each costs context every session): ralph-loop, cli-anything, ponytail, claude-mem |
| **Token management (v2.5.0)** | `token-budget` skill: daily tracker (Ctx/turn, % turns >200k), per-turn context line, empty-chat baseline, context-diet playbook, `api_map.py`. Took the reference machine from 200-230k to 78k context per turn |
| **Cost controls (v2.5.0)** | Lean ~6 KB orchestrator (inventory moved to an on-demand reference), head/arms model routing, `CLAUDE_CODE_SUBAGENT_MODEL=sonnet`, `[1m]` context disabled, on-demand grounding kit (`~/.claude/mcp-grounding.json`: context7 + serena), `## API MAP` convention |
| **Workflow skills (bundled)** | **handoff** (HANDOFF.md), **reboot** (handoff → /clear → auto-resume), **dream** (memory consolidation), **session-audit** (find missing skills monthly), **context-budget** (context-cost audit), **token-budget** (token management system: tracker + context line + baseline + diet), **council** (4-voice decision panel), **claudex-loop** (plan hardening w/ adversarial Codex review) |
| **Model routing** | Orchestrator suggests the right model tier per task (`/model`), the `/effort` lever before downgrading, and the advisor pattern (mid model executes, top model advises) |
| **Hook-based add-ons** | caveman (terse mode) — installs SessionStart + UserPromptSubmit hooks via its own installer |
| **Knowledge-graph layer** | **graphify** — `/graphify .` builds a graph from any folder of `.md`/`.json`/code. Queryable from Claude via MCP (`query_graph`, `shortest_path`, `god_nodes`, `get_neighbors`). Replaces hand-curated wikilinks with analytical traversal. |
| **Design skills fetched** | refactoring-ui, ui-ux-pro-max, **hallmark** (ux-heuristics + ios-hig-design dropped in v2.4.0 — never invoked in a year of use) |
| **Bundled skills** | **deploy-project**, **shinen-design**, vault-ingest, vault-query, vault-lint, **handoff**, reboot, dream, session-audit, context-budget, token-budget, council, claudex-loop, agent-harness-construction, click-path-audit, regex-vs-llm-structured-text, loop-design-check, skill-stocktake, rules-distill |
| **Power skills fetched** | **qa-test** (adversarial front-end QA), **agent-browser** (browser automation CLI), **agent-reach** (multi-platform research) |
| **Power CLI tools** | **unclog** (context-cost audit), **opencli** (any website → CLI via your logged-in Chrome), **gws** (Google Workspace: Drive/Gmail/Calendar/Sheets/Docs), **browser-harness** (self-healing CDP control), **srt** (OS-level sandbox for agent-run code) |
| **Audit & video skills** | **improve** (strong model audits, cheap model executes), **opencli-browser** + **opencli-usage**, 6× **seedance-\*** (Seedance 2.0 × Higgsfield video prompting: cinematic, motion-design-ad, ecommerce-ad, product-360, social-hook, fashion-lookbook) |
| **Design system** | `shinen-design` skill — SHIN-EN 深淵: dark Japanese minimal monochrome for tool dashboards. One stylesheet (`shinen.css`, vanilla CSS, `.sn-*` classes) + signature ghosted step numerals. No frameworks, inlines into stdlib HTTP servers. |
| **Frameworks (optional)** | GSD (`gsd-*` skills + `gsd-*` agents + workflow guard hooks), BMAD v6 (15 `bmad:*` skills). gstack removed in v2.4.0 |

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

It will ask once where your vault should live (default `~/Workspace`), then install everything. Asks once whether to install the heavyweight frameworks (GSD/BMAD) — default = both.

### 3. Verify

```
/stack-verify
```

Expected: all ✓. Any ⚠ includes a fix hint.

## Usage

Once bootstrapped, every request is routed by the orchestrator. Examples:

| You say… | way-stack routes to… |
|---|---|
| "build me an agent that summarizes my inbox every morning" | direct agent `.md` in `~/.claude/agents/`, loop-driven (`loop-design-check` before launch) |
| "UI looks off, fix it" | `refactoring-ui` skill |
| "what do we know about rate-limiting Gmail API?" | `vault-query` skill |
| "save this article on RAG patterns" | `vault-ingest` skill |
| "deploy this project: /path/to/app" | `deploy-project` skill — 10-step secure deploy to Vercel |
| "dark dashboard for this tool" | `shinen-design` skill — SHIN-EN monochrome design system |
| "new project, full web app, auth + payments" | orchestrator asks size → GSD or BMAD |

## Anatomy

```
way-stack/
├── .claude-plugin/plugin.json
├── commands/              # /stack-bootstrap, /stack-verify, /stack-publish, /caveman-commit
├── skills/                # deploy-project, shinen-design, vault-{ingest,query,lint}, workflow + craft skills
├── hooks/                 # session log + auto-backup
├── templates/             # orchestrator CLAUDE.md, vault CLAUDE.md, project CLAUDE.md,
│   ├── agent-monitor/     #   3D live dashboard for the agent fleet (monitor.py + Three.js)
│   └── deploy-agent/      #   scriptable deploy CLI (scan → audit → auth → git → Vercel)
├── references/            # agent design principles, CLI tools stack
├── README.md
└── LICENSE                # MIT
```

## Upstream dependencies (fetched by `/stack-bootstrap`)

| Dependency | Source | Purpose |
|---|---|---|
| superpowers | anthropics/claude-plugins-official | TDD, debug, brainstorming, worktrees, verification-before-completion, dispatching-parallel-agents |
| frontend-design | anthropics/claude-plugins-official | Production-grade UI generation |
| code-review | anthropics/claude-plugins-official | Multi-agent parallel review |
| ralph-loop *(optional)* | anthropics/claude-plugins-official | Autonomous iteration loop |
| cli-anything | HKUDS/CLI-Anything | GUI-OSS CLI wrappers |
| claude-mem *(optional)* | thedotmack/claude-mem | Predates Claude Code's built-in auto-memory. Skip it unless you want the `$cmem` recap — running both means two memory systems and ~7 extra hooks per session |
| caveman (hook-based) | JuliusBrussee/caveman | Terse-mode prompt compression — installed via its one-line `install.sh` (`curl … | bash`) |
| **ponytail** *(optional)* | DietrichGebert/ponytail | Lazy-senior-dev mode — simplest solution that works (YAGNI, stdlib first, shortest diff). `/ponytail lite\|full\|ultra` |
| **impeccable** | pbakaus/impeccable | Frontend design fluency — 1 skill, 23 commands (`/impeccable polish\|audit\|critique\|…`), anti-pattern detection |
| **graphify** | safishamsi/graphifyy (pip `graphifyy`) | Knowledge-graph builder + MCP server. `/graphify .` extracts entities/edges from any folder; MCP exposes graph to Claude (`query_graph`, `get_node`, `get_neighbors`, `shortest_path`, `god_nodes`) |
| refactoring-ui | wondelai/skills | Visual hierarchy / spacing / color audit |
| ui-ux-pro-max | nextlevelbuilder/ui-ux-pro-max-skill | Full design system skill |
| **hallmark** | nutlope/hallmark | Anti-AI-slop structural variety for landing/app pages (audit/redesign/study verbs) |
| **watch** | claude-video marketplace | `/watch <video>` — frames + transcript + Q&A on any video |
| **mattpocock-skills** | mattpocock marketplace | Process skills: tdd, diagnosing-bugs, prototype, wizard, grilling, … plus `wayfinder` (multi-session planning). wayfinder ships `disable-model-invocation: true` — it never auto-triggers, you type it, and it needs `/setup-matt-pocock-skills` per project |
| **GSD** (optional) | gsd-build/get-shit-done (`npx get-shit-done-cc --claude --global`) | Spec-driven dev framework — the default planning layer |
| **BMAD v6** (optional) | bmad-code-org/BMAD-METHOD (`npx bmad-method install`) | Agile multi-role methodology, 15 skills |

way-stack does NOT redistribute these — it adds their marketplaces / runs their canonical installers at bootstrap time. They stay on their own update tracks.

## Philosophy

**Orchestrator + vault + memory** is the minimum viable "pro" Claude Code setup. Everything else is optional layering.

- **Orchestrator** picks the tool. You stop hand-routing every request.
- **Vault** persists what you learn across sessions. Claude reads it instead of re-asking.
- **Frameworks** (GSD by default) enforce plan → build → verify → ship. Stops the "Claude wrote 500 lines I didn't ask for" failure mode.

Everything else (BMAD agile, wayfinder tickets, advanced debugging) layers cleanly on top if you want it.

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
