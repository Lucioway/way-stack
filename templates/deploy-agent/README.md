# Deploy Agent — template

Standalone Python CLI that scans, secures, and deploys web projects to Vercel. Non-conversational counterpart to the `deploy-project` skill — use it for repeatable runs or CI.

Pipeline: **scan → security audit → auth setup → git push → Vercel deploy**.

## Requirements

- Python 3.11+ (stdlib only — no pip dependencies)
- `gh` CLI installed and authenticated (`gh auth login`)
- `vercel` CLI installed and authenticated (`npm i -g vercel && vercel login`)
- Node.js 18+ and git

## Configuration

| Env var | Purpose | Default |
|---|---|---|
| `GITHUB_OWNER` | GitHub user/org for new repos | auto-detected from `gh` auth |

## Usage

```bash
python main.py --project /path/to/project              # full pipeline
python main.py --project /path/to/project --dry-run    # simulate, no changes
python main.py --project /path/to/project --scan-only  # analysis only
python main.py --project /path/to/project --skip-auth
python main.py --project /path/to/project --skip-security
python main.py --project /path/to/project --repo-url https://github.com/you/existing-repo
```

The CLI asks for confirmation at every critical step: security overrides, auth setup, repo creation, production promotion.

## Modules

| File | Role |
|---|---|
| `main.py` | Entry point, pipeline orchestration, interactive prompts |
| `config.py` | All detection patterns, secret regexes, security headers |
| `scanner.py` | Framework/auth/DB/env-var detection, project structure |
| `security_audit.py` | 5-level audit: secrets, gitignore, deps, OWASP, readiness |
| `auth_setup.py` | Clerk integration (Next.js, React, Astro) |
| `git_manager.py` | git init, .gitignore enforcement, private repo creation, push |
| `deployer.py` | vercel link, env vars, security headers, preview + prod |
| `reporter.py` | Scan / security / final reports |

## Safety guarantees

- Deploy is **blocked** on CRITICAL/HIGH security findings (override requires explicit confirmation)
- `.env` files are never committed — removed from tracking before any commit
- Build must pass before any deploy
- New repos are **private** by default
- Security headers are merged into `vercel.json` on every deploy
