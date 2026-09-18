# way-stack inventory + routing cheatsheet

Reference file, read on demand. The orchestrator (`~/.claude/CLAUDE.md`) points here instead of carrying these lists in every prompt. Installed by `/stack-bootstrap` as `~/.claude/way-stack-inventory.md`.

## Plugins
- **way-stack** — this meta-plugin (orchestrator + vault skills + workflow skills + handoff)
- **superpowers** — TDD, debug, brainstorming, worktrees, subagent-driven-dev, verification-before-completion, dispatching-parallel-agents, writing-skills, executing-plans
- **frontend-design** — production-grade UI generation
- **code-review** — parallel multi-agent review (`/code-review:code-review`)
- **impeccable** (`pbakaus/impeccable`) — frontend design fluency: `/impeccable polish|audit|critique|…`. Composes with `frontend-design`.
- **watch** (`claude-video`) — `/watch <video>`: frames + transcript from any video URL/path, then Q&A. Video analysis = always `/watch`, never guess.
- **mattpocock-skills** — diagnosing-bugs, tdd, prototype, research, domain-modeling, codebase-design, wizard, grilling. `wayfinder` is opt-in (needs `/setup-matt-pocock-skills` per project).
- **caveman** (hook-based, not a plugin) — terse output; `/caveman lite|full|ultra`, off via "stop caveman".
- *Optional, off by default* (each one adds skill descriptions / hooks to every session — install only if you use them): **ralph-loop** (native `/loop` + saved Workflows cover it), **cli-anything** (CLI wrappers for GUI apps), **ponytail** (YAGNI mode), **claude-mem** (native auto-memory covers it).

## Bundled workflow skills
- **handoff** / **reboot** — `HANDOFF.md` for fresh-context resume; `/reboot` = handoff → `/clear` → auto-resume.
- **dream** — memory consolidation; keep `MEMORY.md` a lean index.
- **session-audit** — monthly: repeated manual tasks → proposed skills/automations.
- **context-budget** — audit what agents / skills / MCP / rules cost the context window.
- **token-budget** — the token management system: daily tracker (Ctx/turn, % turns >200k), per-turn context line (Stop hook), empty-chat baseline, context-diet checklist, agent right-sizing, `api_map.py`.
- **council** — four-voice structured disagreement for go/no-go calls.
- **claudex-loop** — plan hardening with an adversarial Codex review loop. Requires `codex` CLI.
- **agent-harness-construction**, **click-path-audit**, **regex-vs-llm-structured-text**, **loop-design-check**, **skill-stocktake**, **rules-distill**.
- **vault-ingest** / **vault-query** / **vault-lint** — Karpathy LLM Wiki ops.

## Fetched skills
- **qa-test**, **agent-browser**, **agent-reach**, **improve**, **opencli-browser** / **opencli-usage**
- Design: **refactoring-ui**, **ui-ux-pro-max**, **hallmark**

## Frameworks (optional)
- **GSD** (`gsd-*`) — `/gsd-new-project` → `/gsd-discuss-phase` → `/gsd-plan-phase` → `/gsd-execute-phase` → `/gsd-verify-work` → `/gsd-code-review` → `/gsd-ship`. Small job: `/gsd-quick`. Unattended: `/gsd-autonomous`.
- **BMAD** (`bmad:*`) — `/bmad:workflow-init` → `product-brief` → `prd` → `architecture` → `tech-spec` → `sprint-planning` → `create-story` → `dev-story`.

## Saved workflows (`~/.claude/workflows/*.js`)
Deterministic multi-agent scripts for jobs you repeat (review-changes, research sweep, weekly report). Every `agent()` call passes an explicit cheap `model`. Run only on explicit user opt-in ("use a workflow").

## Grounding kit (on demand)
`claude --mcp-config ~/.claude/mcp-grounding.json` starts a session with **context7** (library docs) + **serena** (symbol index). Not registered globally: an always-on MCP server is paid for in every prompt. Store-specific doc servers (e.g. Shopify Dev MCP) go in that project's `.mcp.json`.

Project `CLAUDE.md` files carry a `## API MAP` table (name | file | entry point | auth) so cheaper models execute without inventing or denying APIs.

## Cheatsheet
| User says… | Route to… |
|---|---|
| brainstorm | `superpowers:brainstorming` |
| new project | ask size → pick framework |
| build me an agent for X | direct agent `.md`, loop-driven |
| bug | `superpowers:systematic-debugging` |
| design UI | `frontend-design` |
| UI looks off | `refactoring-ui` |
| polish / audit existing frontend | `/impeccable polish` / `/impeccable audit` |
| code review | `/code-review:code-review` |
| security | `gsd-secure-phase` / `/security-review` |
| scrape web | `opencli` / `agent-browser` |
| run overnight | `/loop`, `gsd-autonomous`, saved Workflow |
| save this to vault | `vault-ingest` |
| what do we know about X | `vault-query` |
| vault health check | `vault-lint` |
| stopping mid-task | `/handoff` |
| restart with clean context | `/reboot` |
| what's in this video | `/watch <url-or-path>` |
| ambiguous decision / go-no-go | `council` |
| high-stakes plan, harden it | `claudex-loop` |
| memory bloated / noisy | `dream` |
| what skills am I missing | `session-audit` |
| sessions feel heavy / slow | `context-budget` |
| check token usage / quota gone | `token-budget` |
| QA this app / try to break it | `qa-test` |
| research X across the internet | `agent-reach` |
| automate a website / fill forms | `agent-browser` |
| buttons broken but tests pass | `click-path-audit` |
| parse this text/log/export | `regex-vs-llm-structured-text` |
| about to launch a loop | `loop-design-check` |
| audit my skills | `skill-stocktake` → `rules-distill` |
| "that API doesn't exist" | check `## API MAP`, grep, then grounding kit |
