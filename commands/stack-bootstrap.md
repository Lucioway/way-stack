---
name: stack-bootstrap
description: "One-shot installer for the full way-stack — creates PARA+Karpathy vault, installs orchestrator CLAUDE.md, registers session hooks, adds upstream marketplaces, installs core plugins + caveman (terse mode) + impeccable (design fluency) + watch (video) + mattpocock-skills, fetches 3 design skills (incl. hallmark), installs 2 frameworks (GSD, BMAD), bundles 9 workflow skills (handoff, reboot, dream, session-audit, context-budget, token-budget, council, claudex-loop, …), installs the token management system (tracker, context line, cost env vars). Interactive: asks only vault path + framework opt-ins."
---

# /stack-bootstrap — Full Stack Installer

You are the way-stack bootstrap installer. Execute the 14-step install in order. Halt on any error and report which step failed. Never skip verification.

## STEP 1 — Ask vault path

Ask the user exactly ONE question:

> Where should your vault live? (default: `~/Workspace`)

Accept absolute path or `~` prefix. Expand `~` via `$HOME`. Store as `VAULT`.

## STEP 2 — Create vault folder structure (PARA + Karpathy)

```bash
VAULT="<user-provided>"
mkdir -p "$VAULT"/{00_INBOX,01_PROJECTS,02_KNOWLEDGE/{patterns,decisions,retros,learnings},03_REFERENCE,04_SESSIONS}
touch "$VAULT/index.md" "$VAULT/log.md"
```

Then `git init` inside `$VAULT` if not already a repo (enables auto-backup hook).

## STEP 3 — Write vault CLAUDE.md

Copy `${CLAUDE_PLUGIN_ROOT}/templates/vault-CLAUDE.md` → `$VAULT/CLAUDE.md`. If file already exists, do NOT overwrite — show diff and ask user.

## STEP 4 — Write master orchestrator

Copy `${CLAUDE_PLUGIN_ROOT}/templates/orchestrator-CLAUDE.md` → `~/.claude/CLAUDE.md`. If exists, back up to `~/.claude/CLAUDE.md.bak-$(date +%s)` first. Replace the `{{VAULT_PATH}}` placeholder with the real vault path.

The template is deliberately lean (it loads into every prompt). The full inventory + cheatsheet ship as a separate on-demand reference, plus the grounding kit:

```bash
cp "${CLAUDE_PLUGIN_ROOT}/references/inventory.md" ~/.claude/way-stack-inventory.md
[ -f ~/.claude/mcp-grounding.json ] || cp "${CLAUDE_PLUGIN_ROOT}/templates/mcp-grounding.json" ~/.claude/mcp-grounding.json
mkdir -p ~/.claude/workflows
```

`mcp-grounding.json` (context7 + serena) is NOT registered globally — it is opt-in per session: `claude --mcp-config ~/.claude/mcp-grounding.json`. An always-on MCP server is paid for in every prompt.

## STEP 5 — Install hooks

```bash
mkdir -p ~/.claude/hooks
cp "${CLAUDE_PLUGIN_ROOT}/hooks/vault-session-log.sh" ~/.claude/hooks/
cp "${CLAUDE_PLUGIN_ROOT}/hooks/vault-auto-backup.sh" ~/.claude/hooks/
chmod +x ~/.claude/hooks/vault-*.sh
```

Patch `$VAULT` path into both scripts (replace `__VAULT_PATH__` placeholder with real path).

## STEP 6 — Register hooks in settings.json

Read `~/.claude/settings.json` (create empty `{}` if absent). Merge in:

```json
{
  "hooks": {
    "SessionEnd": [
      { "hooks": [{ "type": "command", "command": "$HOME/.claude/hooks/vault-session-log.sh" }] },
      { "hooks": [{ "type": "command", "command": "$HOME/.claude/hooks/vault-auto-backup.sh" }] }
    ],
    "SessionStart": [
      { "matcher": "clear", "hooks": [{ "type": "command", "command": "$HOME/.claude/hooks/reboot-resume.sh" }] }
    ]
  }
}
```

Also copy the reboot hook (used by the bundled `reboot` skill):

```bash
cp "${CLAUDE_PLUGIN_ROOT}/hooks/reboot-resume.sh" ~/.claude/hooks/ && chmod +x ~/.claude/hooks/reboot-resume.sh
```

Preserve existing hooks — append, don't replace. Use `jq` if available.

Also merge the two cost-control env vars (ask before overwriting an existing value):

```json
{
  "env": {
    "CLAUDE_CODE_SUBAGENT_MODEL": "sonnet",
    "CLAUDE_CODE_DISABLE_1M_CONTEXT": "1",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "75",
    "CLAUDE_CODE_PROMPT_CACHE_TTL": "1h",
    "CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL": "1h",
    "BASH_MAX_OUTPUT_LENGTH": "12000"
  }
}
```

- `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` — generic subagents (Explore / Plan / general-purpose) run on Sonnet. Do NOT add the `_FORCE` variant: custom agents with `model:` in their frontmatter must keep it.
- `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` — removes the `[1m]` context variants from the picker. Every turn re-pays the whole context; sessions that drift past 200k cost more than any model choice and reason worse.
- The other four are explained in the `token-budget` skill (section 2), including when to take the 1h cache TTLs back out.

### STEP 6b — Token management system

Install the `token-budget` scripts, register the per-turn context line, schedule the daily tracker:

```bash
mkdir -p ~/.claude/token-budget/bin
cp "${CLAUDE_PLUGIN_ROOT}/skills/token-budget/scripts/"* ~/.claude/token-budget/bin/
chmod +x ~/.claude/token-budget/bin/*
```

Merge into `settings.json` hooks (append to any existing `Stop` array):

```json
{ "hooks": { "Stop": [ { "hooks": [{ "type": "command", "command": "python3 \"$HOME/.claude/token-budget/bin/ctx_guard.py\"" }] } ] } }
```

Daily run at 23:55 — ask before installing. macOS: write `~/Library/LaunchAgents/com.way-stack.token-tracker.plist` (ProgramArguments `/usr/bin/python3 ~/.claude/token-budget/bin/token_tracker.py` with the absolute home path, `StartCalendarInterval` Hour 23 Minute 55) then `launchctl load` it. Linux: add `55 23 * * * python3 $HOME/.claude/token-budget/bin/token_tracker.py >/dev/null 2>&1` to the user crontab.

Finally record the starting point so later diets have a number to beat:

```bash
~/.claude/token-budget/bin/baseline.sh | tee ~/.claude/token-budget/baseline-$(date +%F).txt
```

## STEP 7 — Add upstream marketplaces

Run these Claude Code commands (use Bash tool with `claude` CLI, or instruct user to paste):

```
/plugin marketplace add anthropics/claude-plugins-official
/plugin marketplace add HKUDS/CLI-Anything
/plugin marketplace add thedotmack/claude-mem
```

> NOTE: `anthropics/claude-plugins-official` (NOT the old `anthropics/claude-plugins`) is the canonical marketplace and bundles `superpowers`, `frontend-design`, `code-review`, and `ralph-loop`. No separate `obra/superpowers-marketplace` needed.

## STEP 8 — Install upstream plugins

```
/plugin install superpowers@claude-plugins-official
/plugin install frontend-design@claude-plugins-official
/plugin install code-review@claude-plugins-official
```

Then the design add-on:

```
/plugin marketplace add pbakaus/impeccable
/plugin install impeccable@impeccable
```

**Optional plugins — ask once, default NO.** Each adds skill descriptions and/or hooks to every session, and on the reference machine all four ended up switched off in the v2.5.0 context diet:

```
/plugin install ralph-loop@claude-plugins-official   # native /loop + saved Workflows cover it
/plugin install cli-anything@cli-anything            # CLI wrappers for GUI apps
/plugin install claude-mem@claude-mem                # native auto-memory covers it
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail                    # YAGNI mode, /ponytail lite|full|ultra
```

- **impeccable** — frontend design fluency: 1 skill + 23 commands (`/impeccable polish|audit|critique|…`) + anti-pattern detection. Composes with `frontend-design`.

Then two more quality-of-life plugins:

```
/plugin marketplace add bradautomates/claude-video
/plugin install watch@claude-video
/plugin marketplace add mattpocock/skills
/plugin install mattpocock-skills@mattpocock
```

- **watch** — `/watch <video URL or path>`: downloads with yt-dlp, extracts frames + transcript, lets Claude answer questions about any video.
- **mattpocock-skills** — process skills: diagnosing-bugs, tdd, prototype, research, domain-modeling, codebase-design, code-review, wizard (interactive bash walkthroughs for human-only steps), grilling (stress-test a plan), and **wayfinder** (multi-session planning as decision tickets).

> **wayfinder is opt-in, not the default planning layer.** It ships with `disable-model-invocation: true`, so Claude will never reach for it on its own — you type it. It also needs a tracker configured per project. Run the setup once if you want it; otherwise planning stays with GSD:

```
/setup-matt-pocock-skills
```

Then **install caveman via its official one-line installer** (it ships its own hooks/skill, not the plugin system):

```bash
# macOS / Linux / WSL / Git Bash
curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash
```

(Windows PowerShell: `irm https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.ps1 | iex`)

The installer auto-detects every installed agent (Claude Code, Codex, Gemini, …) and wires caveman into each. Needs Node ≥18, ~30s, safe to re-run. Repo: `JuliusBrussee/caveman` (formerly `claude-code-caveman`, renamed 2026-06).

## STEP 9 — Fetch design skills

```bash
mkdir -p ~/.claude/skills && cd ~/.claude/skills

# wondelai/skills — refactoring-ui (ux-heuristics + ios-hig-design dropped v2.4.0: never invoked)
for s in refactoring-ui; do
  if [ ! -d "$s" ]; then
    git clone --depth 1 --filter=blob:none --sparse \
      https://github.com/wondelai/skills.git ".tmp-$s" 2>/dev/null && \
    (cd ".tmp-$s" && git sparse-checkout set "$s") && \
    mv ".tmp-$s/$s" "./$s" && rm -rf ".tmp-$s"
  fi
done

# ui-ux-pro-max
[ ! -d ui-ux-pro-max ] && git clone --depth 1 \
  https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git ui-ux-pro-max

# hallmark — anti-AI-slop structural variety for landing/app pages (nutlope)
# skill lives in the repo's skills/ subdir — clone temp, move skill out
if [ ! -d hallmark ]; then
  git clone --depth 1 https://github.com/nutlope/hallmark.git .tmp-hallmark && \
  mv .tmp-hallmark/skills/hallmark ./hallmark && rm -rf .tmp-hallmark
fi
```

Then three third-party power skills (fetched, not vendored):

```bash
# qa-test — automated front-end QA (standard + crawl + adversarial break-it modes)
[ ! -d qa-test ] && git clone --depth 1 https://github.com/adampaulwalker/qa-test.git qa-test && rm -rf qa-test/.git

# agent-browser — browser automation CLI for agents (Vercel Labs)
[ ! -d agent-browser ] && npx -y agent-browser@latest install 2>/dev/null || echo "agent-browser: install manually — https://github.com/vercel-labs/agent-browser"

# agent-reach — multi-platform internet research (15 channels: Reddit, X, YouTube, LinkedIn, …)
[ ! -d agent-reach ] && git clone --depth 1 https://github.com/Panniantong/Agent-Reach.git .tmp-reach && \
  { mv .tmp-reach/skills/agent-reach ./agent-reach 2>/dev/null || mv .tmp-reach ./agent-reach; rm -rf .tmp-reach; }
```

If `git clone` fails (repo moved / renamed), log warning and continue — don't halt.

## STEP 9b — Power CLI tools (agent-native surfaces)

Five binaries and three skill sets. Each one hands the agent a command line where it
previously had only a browser or a guess.

```bash
# unclog — audit what MCP servers / skills / CLAUDE.md actually cost your context window
command -v unclog >/dev/null 2>&1 || uv tool install unclog

# browser-harness — self-healing CDP browser control (survives a changed selector)
command -v browser-harness >/dev/null 2>&1 || uv tool install --python 3.12 browser-harness
mkdir -p ~/.claude/skills/browser-harness && \
  browser-harness skill > ~/.claude/skills/browser-harness/SKILL.md 2>/dev/null

# sandbox-runtime — OS-level filesystem + network limits on agent-run code (binary: srt)
command -v srt >/dev/null 2>&1 || npm install -g @anthropic-ai/sandbox-runtime

# gws — Google Workspace CLI: Drive, Gmail, Calendar, Sheets, Docs, Admin
command -v gws >/dev/null 2>&1 || npm install -g @googleworkspace/cli

# opencli — turn any website into a CLI using your already-logged-in Chrome
command -v opencli >/dev/null 2>&1 || npm install -g @jackwener/opencli
```

Three of these need one human step each, and the bootstrap must NOT attempt them:

| Tool | Human step | Why it can't be scripted |
|---|---|---|
| `gws` | `gws auth setup && gws auth login` | OAuth against a Google Cloud project the user owns |
| `opencli` | Install the Browser Bridge extension — <https://opencli.info/download> | Drives the user's logged-in Chrome session |
| `browser-harness` | `browser-harness recordings enable` | Recordings capture page content; default is OFF, enable only on explicit consent |

Then the fetched skill sets:

```bash
# opencli agent skills — the core two (adapter/sitemap authors on demand)
npx -y skills@latest add jackwener/opencli --skill opencli-browser --skill opencli-usage

# improve — strong model audits the codebase, cheap model executes the written plan
npx -y skills@latest add shadcn/improve
```

And the Seedance 2.0 x Higgsfield video skills — 6 of 15, the ones that apply to
product and ecommerce work:

```bash
mkdir -p ~/.claude/skills && cd ~/.claude/skills
if [ ! -d seedance-ecommerce-ad ]; then
  git clone --depth 1 https://github.com/beshuaxian/higgsfield-seedance2-jineng.git .tmp-sd 2>/dev/null && \
  for d in 01-cinematic 06-motion-design-ad 07-ecommerce-ad 09-product-360 11-social-hook 13-fashion-lookbook; do
    n=$(sed -n 's/^name: //p' ".tmp-sd/skills/$d/SKILL.md" | head -1)
    [ -n "$n" ] && mkdir -p "$n" && cp ".tmp-sd/skills/$d/SKILL.md" "$n/SKILL.md"
  done
  rm -rf .tmp-sd
fi
```

The other 9 (cartoon, anime, fight-scenes, comic-to-video, music-video, food-beverage,
real-estate, 3d-cgi) are skipped on purpose: each `SKILL.md` runs 900-2300 lines and its
description loads into context every session. Add one back only when a job needs it.

## STEP 10 — Bundled workflow skills

The `handoff` skill writes `HANDOFF.md` so a fresh-context agent can resume work. Bundled with way-stack (no remote fetch):

```bash
mkdir -p ~/.claude/skills/handoff
cp "${CLAUDE_PLUGIN_ROOT}/templates/skills/handoff/SKILL.md" ~/.claude/skills/handoff/SKILL.md
```

These further workflow skills ship inside the way-stack plugin itself (nothing to copy — active as soon as the plugin is installed):

- **reboot** — handoff → `/clear` → auto-resume via the `reboot-resume.sh` SessionStart hook (STEP 6)
- **dream** — memory consolidation: merge duplicates, resolve contradictions, absolute dates, keep `MEMORY.md` under the ~24.4KB load limit
- **session-audit** — monthly diagnosis of repeated manual tasks → propose new skills/automations
- **context-budget** — audit context-window cost of agents/skills/MCP/rules, prioritized savings
- **token-budget** — token management system: daily tracker, per-turn context line, baseline, diet playbook, `api_map.py` (scripts installed in STEP 6b)
- **council** — four-voice structured disagreement for ambiguous decisions / go-no-go calls
- **claudex-loop** — four-phase plan hardening with adversarial OpenAI Codex review (requires `codex` CLI; skip if not installed)

Plus command `/caveman-commit` (terse conventional commits).

And six engineering-craft skills, also bundled in the plugin:

- **agent-harness-construction** — design agent action spaces, tool definitions, observation formatting
- **click-path-audit** — trace every UI touchpoint through its full state-change sequence (finds bugs unit tests miss)
- **regex-vs-llm-structured-text** — decision framework: regex first, LLM only for low-confidence edge cases
- **loop-design-check** — verify an agentic loop has automated verification + the 3 hard stops before launch
- **skill-stocktake** — audit your skills/commands for quality (Quick Scan + Full modes)
- **rules-distill** — extract cross-cutting principles from skills into rule files

## STEP 11 — Install frameworks (optional, ask once per framework)

Frameworks are heavyweight (50–100+ skills each). Ask the user which to install. Default = ALL.

> Install frameworks? GSD, BMAD — pick either/both/none. (default: both)

### 11a — GSD (Get-Shit-Done) — gsd-build/get-shit-done

```bash
# Requires Node.js 18+
npx -y get-shit-done-cc --claude --global
```

Installs `~/.claude/get-shit-done/` runtime + `~/.claude/skills/gsd-*/` (**90+ skills** as of 2026-05) + `~/.claude/agents/gsd-*` agents + GSD hooks (`gsd-check-update.js`, `gsd-session-state.sh`, `gsd-context-monitor.js`, `gsd-phase-boundary.sh`, `gsd-prompt-guard.js`, `gsd-read-guard.js`, `gsd-workflow-guard.js`, `gsd-validate-commit.sh`). Adds `/gsd-*` slash commands.

### 11b — BMAD-METHOD v6 — bmad-code-org/BMAD-METHOD

```bash
# Requires Node.js 20+
npx -y bmad-method install
```

Interactive installer. Pick `Claude Code` as host when prompted. Installs `~/.claude/skills/bmad/{core,bmm,bmb,cis}/` (15 `bmad:*` skills) + `bmad:*` slash commands.

If any framework install fails, log warning and continue — orchestrator template handles missing frameworks gracefully (marked "if installed").

## STEP 12 — Scaffold auto-memory directory

> **Note (2026-09-10):** Claude Code now ships its own auto-memory (`~/.claude/projects/<project>/memory/` + a `MEMORY.md` index loaded every session). `claude-mem` predates it and still works, but running both means two memory systems writing in parallel and ~7 extra hooks per session. If you only want one, keep the native one and skip `claude-mem` in STEP 8 — the rest of the stack does not depend on it.

`claude-mem` (installed STEP 8) needs a per-project memory dir. Create it lazily for the current project + a global one:

```bash
mkdir -p ~/.claude/projects
touch ~/.claude/projects/.gitkeep
```

Per-project `memory/MEMORY.md` index files are auto-created by `claude-mem` on first session start. Nothing else to do here.

> **Convention — keep `MEMORY.md` lean.** It loads into every prompt, so it is pure context cost. Hold only identity + cross-project rules + one-line pointers; offload per-brand/per-project detail into `index_<topic>.md` sub-index files that get lazy-loaded only when that topic is in play. Re-fold the index whenever a section grows past ~15 entries.

## STEP 13 — Install Graphify (knowledge-graph MCP)

`graphify` (safishamsi/graphifyy) builds a knowledge graph from any folder of `.md`/`.json`/code files and exposes it to Claude via MCP. It replaces hand-curated wikilinks: instead of you maintaining `[[links]]`, Graphify infers the graph structurally — cross-entity traversal, shortest path, god-nodes detection — and Claude queries it natively.

### 13a — Install CLI

```bash
# Preferred: uv tool install (isolated venv)
uv tool install graphifyy 2>/dev/null || pip install --user graphifyy
```

### 13b — Install Claude Code skill

```bash
graphify install --platform claude
```

Adds `/graphify` skill to `~/.claude/skills/graphify/` so you can build graphs by running `cd <folder> && /graphify .` inside Claude Code.

### 13c — Register cross-vault MCP server (optional, recommended)

If the user wants Graphify queryable directly from any Claude session via MCP tools (`query_graph`, `get_node`, `get_neighbors`, `shortest_path`, `god_nodes`):

```bash
# Find graphifyy install path (uv or pip)
GRAPHIFY_PY="$(uv tool dir 2>/dev/null)/graphifyy/bin/python"
[ ! -x "$GRAPHIFY_PY" ] && GRAPHIFY_PY="$(python3 -c 'import sys; print(sys.executable)')"

# Register MCP server at user scope, pointed at vault graph (built on first /graphify run)
claude mcp add graphify-vault \
  --scope user \
  -- "$GRAPHIFY_PY" -m graphify.serve "$VAULT/graphify-out/graph.json"
```

If `$VAULT/graphify-out/graph.json` doesn't exist yet, the MCP server starts but returns empty results until the user runs `/graphify .` once inside the vault.

If `claude mcp add` is not yet available in the installed CLI version, instead patch `~/.claude.json` manually:

```json
"mcpServers": {
  "graphify-vault": {
    "type": "stdio",
    "command": "<GRAPHIFY_PY>",
    "args": ["-m", "graphify.serve", "<VAULT>/graphify-out/graph.json"],
    "env": {}
  }
}
```

## STEP 14 — Verify install

Run `/stack-verify`. Report pass/fail summary to user:

```
✓ Vault created at <path>
✓ Orchestrator installed
✓ Hooks registered (vault + reboot + caveman + claude-mem)
✓ 10 plugins installed (superpowers, frontend-design, code-review, ralph-loop, cli-anything, claude-mem, ponytail, impeccable, watch, mattpocock-skills)
✓ Caveman hooks installed
✓ 6 design skills fetched (incl. hallmark)
✓ 3 power skills fetched (qa-test, agent-browser, agent-reach)
✓ 14 skills bundled (handoff, reboot, dream, session-audit, context-budget, token-budget, council, claudex-loop, agent-harness-construction, click-path-audit, regex-vs-llm-structured-text, loop-design-check, skill-stocktake, rules-distill)
✓ Frameworks: GSD ✓ BMAD ✓
✓ Graphify CLI + skill + MCP server registered
⚠ 1 skill failed (nextlevelbuilder moved) — install manually
```

## Error handling

- Any step that fails → print which step + exact error + remediation hint
- Never rollback automatically — user's files are sacred
- Idempotent: re-running `/stack-bootstrap` must be safe
