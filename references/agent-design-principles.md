# Agent Design Principles

Condensed principles behind way-stack's agent factory. Every agent generated via `create-agent` / `/agent-*` should follow these.

## The golden rule

One minute of planning saves ten minutes of building. ALWAYS use Plan Mode before building anything complex.

## Required agent architecture

Every generated agent MUST have:

- `CLAUDE.md` — project brain (read by Claude Code at startup, includes the SDD mega prompt)
- `brand_context.md` — business/domain context (if applicable)
- `.claude/skills/` — skill files for Claude Code
- `.env.example` — environment variable template
- `.gitignore` — standard exclusions
- `requirements.txt` — Python dependencies (or `package.json`)
- `SETUP_GUIDE.md` — step-by-step user guide

SDD artifacts generated during development: `PROJECT_BRIEF.md`, `SPEC.md`, `TASKS.md`, `PROGRESS.md`, `FIX_PLAN.md`, `VERIFICATION_REPORT.md` (see `sdd-framework.md`).

## Standard command surface

Every agent MUST support:

```
python main.py                    # Main functionality
python main.py --dry-run          # Simulate without side effects
python main.py --once             # Single run
python main.py --schedule         # Start the automatic scheduler
```

## Design principles

1. **Plan Mode before Build** — analyze everything before writing code
2. **Skills > MCP for efficiency** — skills consume far fewer tokens
3. **Module by module** — build and test one piece at a time
4. **Dry-run always before live** — `--dry-run` and `--once` are mandatory
5. **Context management** — concise, high-information-density prompts
6. **Robust error handling** — retry with backoff, local backup, timestamped logs
7. **Centralized CSS selectors** — for web scrapers, easy to update
8. **Centralized configuration** — one `config.py` with everything
9. **Rate limiting** — respect every service's limits
10. **OpenCLI before Selenium** — if the site is supported by OpenCLI, use it (zero tokens, deterministic, no fragile selectors)
11. **Spec-driven** — `SPEC.md` is the source of truth; code is a derived artifact
12. **Fresh context per task** — each task runs in a clean context (~200k tokens); never accumulate conversation
13. **Never hardcode credentials** — always `.env`
14. **Each agent is a SEPARATE project** — independent folder, own git history

## The 4 permission levels

Match the Claude Code permission level to the build phase:

1. **Ask before edits** — to understand what it will do (initial phase)
2. **Edit automatically** — for fast builds (construction phase)
3. **Plan Mode** — for analysis and planning (design phase)
4. **Bypass permissions** — for full uninterrupted builds (advanced phase)

## CLAUDE.md — the project brain

- Injected at the start of EVERY Claude Code session
- Keep it concise (200-500 lines max)
- Contains: description, stack, file structure, rules, commands
- Treat it as the initial trajectory — everything starts from here

## Skills — the biggest ROI

- They are operational checklists handed to the agent
- Only the frontmatter is loaded into context (very few tokens)
- The body loads only when invoked
- Structure: `skill-folder/` with `SKILL.md` + `scripts/`
- Treat them like a junior employee with a checklist

## Sub-agents and agent teams

- Sub-agent = parallelization (3 tasks in 1 minute instead of 3)
- Use sub-agents for: research, code review, QA, design
- Do NOT use sub-agents for simple tasks (overhead > benefit)

## Context management

- `/cost` to monitor tokens, `/compact` to compress history
- Extended thinking: better reasoning, fewer output tokens
- High-density prompts beat verbose prompts
- MCP consumes MANY tokens — prefer Skills when possible

## MCP vs Skills strategy

- MCP: fast setup (1 minute), many tokens — good for prototyping
- Skills: longer setup (5 minutes), very few tokens — good for recurring use
- Strategy: prototype with MCP → if it works, convert to a Skill

## Automation patterns

| Need | Pattern |
|---|---|
| Email reading | `imaplib` (built-in) or Gmail API |
| WhatsApp | Selenium + WhatsApp Web (persistent session) |
| Web data (supported sites) | OpenCLI (Reddit, TikTok, YouTube, HN, GitHub, IG, Twitter/X, Yahoo Finance — zero tokens, JSON output) |
| Web scraping (custom sites) | Selenium + browser, centralized selectors |
| AI analysis | Claude API (Sonnet for simple tasks, Opus for complex analysis) |
| Storage | Notion API, Google Drive, SQLite, local files |
| Scheduling | APScheduler (Python cron) |
| Deploy | Modal for webhooks, LaunchAgent (macOS) / systemd (Linux) for autostart |

## Common mistakes to avoid

1. Not planning before building
2. Vague prompts ("improve the code" vs "fix the bug in file X line Y")
3. Not testing with `--dry-run`
4. Letting the workspace fill up with temp files
5. Not running `/compact` when context is full
6. Using MCP for recurring tasks instead of Skills
7. Not centralizing configuration
8. Hardcoding credentials
9. Using Selenium for sites OpenCLI supports (wasted maintenance)
10. Vibe coding without a spec (context rot, hallucinations, non-traceability)
11. Accumulating context across tasks
12. Skipping verification before moving to the next task
