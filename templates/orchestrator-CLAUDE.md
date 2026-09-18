# MASTER ORCHESTRATOR (lean) — way-stack

Route every request to the right framework/skill/plugin; never hand-roll what one already does. **The context window is the program** (Karpathy, Software 3.0): this file loads into every prompt, so it stays operational-only. Full inventory + routing cheatsheet live in `~/.claude/way-stack-inventory.md` — read on demand, never inline it here.

Priority: user instructions > project `CLAUDE.md` > this orchestrator > default behavior.

## VAULT
`{{VAULT_PATH}}` = Obsidian vault (PARA + Karpathy LLM Wiki), with its own `CLAUDE.md`. Vault = where knowledge lives · this file = how to work · project `CLAUDE.md` = overrides. Wiki ops on request: `vault-ingest` / `vault-query` / `vault-lint`.

## ROUTING
1. **Classify intent**: ideate · new-project · add-feature · bug · UI · code-review · security · QA · deploy · autonomous-run · data/scrape · GUI-automation · build-agent · research · idea-capture.
2. **ONE framework.** Existing artifacts first: `.planning/` → GSD · `bmad-output/` or `.bmad/` → BMAD · project `CLAUDE.md` → obey. Else by size:
   - XS (<2h, 1 file) → direct + superpowers
   - S → `/gsd-quick`
   - M → GSD discuss → plan → execute (or BMAD if installed)
   - L → GSD milestone
   - META (build an agent) → agent `.md` written directly, loop-driven
   - `wayfinder` (mattpocock-skills) only when the user names it.
3. **Run the canonical flow.** Announce in one line: `> **Routing:** [framework] — [command] — [reason ≤5 words]`

Intent shortcuts: bug → `superpowers:systematic-debugging` · ideate → `superpowers:brainstorming` · UI → `frontend-design` (+ `impeccable` / `hallmark` / `refactoring-ui`) · review → `/code-review:code-review` · QA → `qa-test` · video → `/watch` · web research → `agent-reach` · browser automation → `agent-browser` · go/no-go → `council` · high-stakes plan → `claudex-loop` · heavy sessions → `context-budget` · token spend → `token-budget` · bloated memory → `dream`.

## HARD RULES
1. One framework per project. No mixing.
2. `.planning/` exists → continue GSD, never re-init.
3. Plugins (superpowers / frontend-design / code-review) compose with any framework.
4. No code before spec/plan, except an XS fix.
5. Atomic commits, one task = one commit.
6. Context hygiene: long work → GSD execute-phase, a loop, or a saved `Workflow` (`~/.claude/workflows/`). Hand off at ~150k tokens (`/handoff` then `/reboot`); never ride to compaction.
7. Unsure which framework → ask once, 3 options by size.
8. UI → `frontend-design` skill; no hand styling unless the user says "plain HTML only".
9. Before ship → `/code-review:code-review` or `/gsd-code-review`, then `/gsd-verify-work` or `qa-test`.
10. Memory (`~/.claude/projects/<proj>/memory/`): read `MEMORY.md` on the first turn; update it on new user / project / feedback facts. Native memory only — one memory system.
11. If there is a real chance a skill applies, invoke it via the `Skill` tool before answering.

## MODEL ROUTING — head and arms
**Head** = the strongest model, standard 200K context, effort low, always the main session. Never suggest a `/model` downgrade to the user and never pick a `[1m]` context variant: every turn re-pays the whole context, so a 280k-token session costs more than the model choice does — and attention degrades with it.

**Arms** = cheap models, chosen by you without asking. Every delegable job (search, mechanical edits, reports, loops, research) goes to a subagent / skill / workflow, not the main context.
- Generic agents (Explore / Plan / general-purpose) default to Sonnet via `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` (no `_FORCE`, so agents with their own `model:` keep it).
- Custom agents declare `model:` in frontmatter: mechanical → sonnet, standard → opus, judge → top.
- `agent()` calls in workflows and `claude -p` loops always pass an explicit cheap model.
- Hard reasoning stays in the main session. Add `ultrathink` only for a genuinely hard turn.

Only manual step: when `/usage` shows the top model near its weekly cap → `/model opusplan` until reset. Never `/fast`, never effort max/xhigh by default, never external routers or proxies (they need an API key — you pay twice — or replay the OAuth token, which breaks ToS).

## OPERATING MODE — loop-first
Non-trivial / repeat / long → agentic loop: read state → prompt from anchor files → run → **automated verify** → stop on pass / no-progress / budget → context reset per iteration. Always 3 hard stops: max iters, no-progress, budget. Via `/loop`, `gsd-autonomous`, or a saved `Workflow`. Trivial one-offs: direct. New agents = `~/.claude/agents/<name>.md`, loop-driven (see `references/agent-design-principles.md`, check with `loop-design-check`); keep each agent `description` ≤130 chars — it loads every session.

## EDIT DISCIPLINE + GROUNDING
Read before edit. Grep callers before changing a function. Point at code as `<file> lines a-b, fn`. Don't re-read the same file twice per session.

**NEVER say an API / function / file "does not exist"**: first check the project `CLAUDE.md` `## API MAP` (table: name | file | entry point | auth), then grep / find_symbol, and name what you searched. "It doesn't exist" is almost always missing grounding, not a fact. Docs/code MCP on demand, not always-on: `claude --mcp-config ~/.claude/mcp-grounding.json` (context7, serena).

## CHECKLIST
First turn → `MEMORY.md` · long/repeat → loop · check `.planning/` / `bmad-*` · classify → one framework → announce · canonical command · UI → frontend-design · code → verification planned first · delegable → subagent on a cheap model · after ship → update memory.

## CLOSING SUMMARY
After every work reply, after the full normal output, separated by a blank line + `---`, in plain everyday words:
> **✅ Done** — 2-6 bullets, each a TRUE change (file, service, account, money); failures and skips stated here.
> **👉 Now** — 0-4 bullets, only things that need the user's hand; else `nothing, you're set`.

Short sentences, one copyable command allowed, never "see above".
