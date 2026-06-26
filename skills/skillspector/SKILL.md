---
name: skillspector
description: "Security-scan an AI agent skill before installing or shipping it. Use when asked to audit/scan/vet a skill, plugin, or MCP for safety; when installing an untrusted skill from a marketplace/GitHub; or before publishing a skill. Wraps NVIDIA SkillSpector — 68 vulnerability patterns across 17 categories (prompt injection, data exfiltration, privilege escalation, supply chain, tool poisoning, MCP least-privilege, etc.), two-stage static + optional LLM analysis, OSV.dev CVE lookups, SARIF/JSON/Markdown reports."
version: "1.0.0"
license: "Skill: MIT (way-stack). Underlying tool: NVIDIA SkillSpector, Apache-2.0"
allowed-tools: ["Bash", "Read", "Glob"]
metadata:
  homepage: "https://github.com/NVIDIA/SkillSpector"
  openclaw:
    emoji: "🛡️"
    homepage: "https://github.com/NVIDIA/SkillSpector"
    requires:
      anyBins:
        - skillspector
        - uv
---

# SkillSpector — Agent Skill Security Scanner

Answers one question: **"Is this skill safe to install?"** Research behind the tool
found 26.1% of public skills contain vulnerabilities and 5.2% show likely malicious
intent. Scan before you trust.

## Activation

User says something like:
- "scan this skill: <path|url|repo>"
- "is this plugin safe to install?"
- "audit <skill> for security"
- "vet this MCP before I add it"
- "security-check my skill before publishing"

## Ensure the tool is installed

`skillspector` is a standalone CLI (Python 3.12+). If `which skillspector` is empty,
install it once — prefer `uv`:

```bash
uv tool install git+https://github.com/NVIDIA/skillspector.git
# update later: uv tool update skillspector
```

Do NOT vendor the NVIDIA repo into this plugin — it is large and Apache-2.0 licensed.
This skill only orchestrates the installed CLI.

## Run a scan

Input can be a directory, single file, git repo URL, remote URL, or zip.

```bash
# Fast static-only scan (no API key needed) — default for quick triage
skillspector scan <target> --no-llm

# Full scan with LLM semantic pass (filters false positives, explains findings)
SKILLSPECTOR_PROVIDER=anthropic ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  skillspector scan <target>

# Machine-readable report to a file
skillspector scan <target> --no-llm --format json --output report.json
# formats: terminal (default), json, markdown, sarif
```

## Interpreting output

- **Risk score 0–100** with severity label + recommendation. Higher = more dangerous.
- Findings are categorised (e.g. SC4 = vulnerable dependency via OSV.dev, prompt
  injection, data exfiltration, MCP tool poisoning). Read the category + the matched
  snippet, don't just trust the number.
- Static stage = regex/AST/taint/YARA (fast, can false-positive). The LLM stage prunes
  false positives and explains intent — run it for anything you're about to actually install.

## Suppressing known false positives

Re-scans only need to surface *new* issues. Accept known findings with a baseline:

```bash
skillspector scan <target> --no-llm --baseline .skillspector-baseline.json
```

## Report back

Summarise: risk score, the top high/critical findings (category + file:line + why),
and a clear verdict — **safe / review-needed / do-not-install**. For audits before
publishing, list each finding the author should fix.

## Lucio note

Use this on anything pulled from a third-party marketplace before it lands in
`~/.claude/skills` or `~/.claude/plugins`. The local install lives at
`~/.local/bin/skillspector`.
