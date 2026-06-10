# CLI Tools Stack — Recommended Dev Environment

Companion tooling for way-stack agents. Install once, every generated agent benefits.

## Quick install (macOS)

```bash
brew install lazygit zoxide fzf ripgrep fd ast-grep difftastic shellcheck glow btop scc sd yq hyperfine
npm install -g @jackwener/opencli
```

Verify:

```bash
opencli doctor    # Check OpenCLI works
opencli list      # Show all available commands
```

---

## OpenCLI — browser automation via CLI

Turns any website into a deterministic CLI command. Reuses your already-logged-in Chrome session (credentials never leave the browser), produces structured output (JSON, YAML, CSV, Markdown), and costs **zero tokens** at runtime.

Why use it:

- **Zero tokens** — deterministic output, no LLM at runtime
- **Zero maintenance** — no fragile CSS selectors
- **1 command** replaces hundreds of lines of Python scraper
- **Structured output** — JSON ready for analysis with the Claude API

### Supported sites (17+)

| Platform | Main commands | Browser required? |
|---|---|---|
| Reddit | hot, search, subreddit, upvote, save, comment | Yes |
| Twitter/X | trending, search, timeline, post, reply, like | Yes |
| YouTube | search, trending, download | Yes |
| HackerNews | top, frontpage, search, read | No |
| GitHub | trending, search, user, repo | No |
| TikTok | search, trending | Yes |
| Instagram | search, feed, user | Yes |
| BBC | news, articles | No |
| Reuters | news, search | No |
| Yahoo Finance | quote, search, news | No |
| Bilibili | hot, search, user | Yes |
| Zhihu | hot, search, article | Yes |
| Xiaohongshu | search, feed, user, download | Yes |
| Weibo | hot, search, user | Yes |
| V2EX | hot, latest | No |
| Xueqiu | hot, search | Yes |
| Boss Zhipin | search, jobs | Yes |

"Browser: Yes" requires Chrome open and logged into the site. "No" works via public API.

### Key commands

```bash
opencli list                                          # Discover all available commands
opencli doctor                                        # Verify setup
opencli reddit search 'thermal leggings' -f json      # Reddit search → JSON
opencli tiktok search 'product review' -f json        # TikTok search → JSON
opencli hackernews top --limit 5 -f yaml              # Top HN → YAML
opencli youtube search 'unboxing haul' -f json        # YouTube search → JSON
```

### AI-powered discovery (new sites)

```bash
opencli explore https://example.com --site mysite      # Discover the site's API
opencli synthesize mysite                              # Auto-generate the adapter
opencli cascade https://api.example.com/data           # Test auth strategies
opencli generate https://example.com --goal "trending" # All in one shot
```

### OpenCLI vs Selenium

| Scenario | Tool | Why |
|---|---|---|
| Reddit, TikTok, YouTube, HN, GitHub, Twitter/X, Instagram | **OpenCLI** | Fast, reliable, zero tokens, structured output |
| WhatsApp Web (read/send messages) | **Selenium** | Not supported by OpenCLI, needs persistent session |
| Amazon (reviews, competitors) | **Selenium** | Not supported by OpenCLI |
| Meta Ad Library | **Selenium** | Not supported by OpenCLI |
| Trustpilot | **Selenium** | Not supported by OpenCLI |
| Heavy-Cloudflare sites | **Selenium (headed)** | Needs manual interaction |
| Custom competitor sites | **Selenium** | Needs custom CSS selectors |
| Unknown site | **`opencli list` first** | If supported use OpenCLI, otherwise Selenium |

### Claude Code integration

Add this line to the CLAUDE.md of every agent that collects web data:

```
To discover available CLI tools, run: opencli list
```

### Dual-engine architecture

1. **YAML Declarative Engine** — ~30 lines of YAML per adapter. Covers most sites.
2. **TypeScript Injection Engine** — for complex sites with dynamic rendering, infinite scroll, auth.
3. **Anti-detection** — 7 automatic patches via CDP (Chrome DevTools Protocol).
4. **Dynamic Loader** — drop a `.ts` or `.yaml` file in `clis/` = new command auto-registered.

---

## Companion tools for Claude Code

### Navigation and search

| Tool | Function | Typical use |
|---|---|---|
| **zoxide** | Smart cd with memory | `z project` → jump to ~/Projects |
| **fzf** | Universal fuzzy finder | `Ctrl+R` → shell history search |
| **fd** | Modern, fast find | `fd '\.py$'` → find Python files |
| **ripgrep (rg)** | Ultra-fast grep | `rg 'def process'` → search code |

### Code and analysis

| Tool | Function | Typical use |
|---|---|---|
| **ast-grep** | Structural (AST) search/refactoring | Patterns that look like real code, 20+ languages |
| **difftastic** | Semantic AST-node diff | Review AI output without false positives |
| **scc** | Per-language code counter | Codebase overview: lines, complexity |
| **sd** | Modern sed with PCRE regex | Replacement without escaping headaches |
| **shellcheck** | Shell script linter | Find bugs in AI-generated commands |

### Monitoring

| Tool | Function | Typical use |
|---|---|---|
| **btop** | CPU/memory/process monitor | Check Claude Code sessions aren't overloading |
| **hyperfine** | Benchmarking with statistics | Real numbers for optimizations |

### Git and visualization

| Tool | Function | Typical use |
|---|---|---|
| **lazygit** | Full Git TUI | Real-time monitoring of AI changes |
| **glow** | Markdown rendering in terminal | Review reports without an editor |
| **yq** | jq for YAML/JSON/TOML/XML | Query and edit while preserving comments |

---

## Claude Code ecosystem

- **ccusage** (`npx ccusage`) — token, cost, and usage analysis from local JSONL files
- **cc-toolkit** — 41 free tools for session analysis, AI autonomy, costs
- **Dippy** — auto-approves safe bash commands, confirms destructive ops
- **parry** — prompt-injection scanner for Claude Code hooks
- **TDD Guard** — monitors file operations and blocks TDD violations
- **cc-safe-setup** — 8 security hooks in 10 seconds (`npx cc-safe-setup`)
- **ast-grep skill** — teaches Claude Code structural searches with ast-grep

Resources: **awesome-claude-code** (GitHub, curated skills/hooks/commands list), **Trail of Bits claude-code-config** (opinionated config).

---

## Alternative AI CLIs (for reference)

| Tool | Strengths | Pricing |
|---|---|---|
| **Claude Code** (way-stack default) | Deep reasoning, 1M context, autonomy | $20-100/mo |
| **Gemini CLI** (Google) | Generous free tier (60 req/min), 1M context | Free |
| **OpenCode** | 75+ LLM providers, max flexibility | Open source |
| **Aider** | Git-first, auto-commit, mature community | Open source |
| **Codex CLI** (OpenAI) | Fast (Rust), granular permission system | $20/mo |
