# Workspace Vault — PARA + Karpathy LLM Wiki

This is the user's knowledge vault. Obsidian-compatible. Append-only log, catalog-first retrieval.

## Layout

```
<vault>/
├── 00_INBOX/               # raw drops, triage weekly
├── 01_PROJECTS/            # active projects (one folder each)
├── 02_KNOWLEDGE/           # durable knowledge
│   ├── patterns/           # reusable solutions across projects
│   ├── decisions/          # ADR (numbered, ADR-NNN)
│   ├── retros/             # milestone retrospectives
│   └── learnings/          # single fixes, gotchas, insights
├── 03_REFERENCE/           # stable docs, specs, cheatsheets
├── 04_SESSIONS/            # auto-written by way-stack hook
├── index.md                # catalog of knowledge (Karpathy pattern)
├── log.md                  # chronological append-only
└── CLAUDE.md               # this file
```

## Write rules

1. **Raw note / idea** → `00_INBOX/<slug>.md`
2. **Reusable pattern** → `02_KNOWLEDGE/patterns/<slug>.md`
3. **Architectural decision** → `02_KNOWLEDGE/decisions/ADR-NNN-<slug>.md` (increment NNN — find highest existing)
4. **Milestone retro** → `02_KNOWLEDGE/retros/YYYY-MM-DD-<project>.md`
5. **Single learning / fix** → `02_KNOWLEDGE/learnings/<slug>.md`
6. **Session log** → `04_SESSIONS/` (managed by hook, do NOT write by hand)
7. **Stable reference** → `03_REFERENCE/`

## Frontmatter standard

```yaml
---
type: pattern | decision | retro | learning | session | inbox | reference
date: YYYY-MM-DD
project: <project-slug or "global">
tags: [tag1, tag2]
---
```

## Linking

- Use `[[wikilink]]` Obsidian syntax
- From `01_PROJECTS/<project>.md` → link retro / pattern / learning for that project
- From pattern → link projects that use it

## Karpathy LLM Wiki operations

Three canonical ops (see way-stack vault-* skills):

- **Ingest** — source → summary page in `00_INBOX/` or `02_KNOWLEDGE/` → update `index.md` → append `log.md`
- **Query** — read `index.md` → drill into pages → synthesize with `[[citations]]` → optionally file new page
- **Lint** — health check (contradictions, orphans, stale, gaps) → report in `02_KNOWLEDGE/learnings/`

## Special files

- `index.md` — content-oriented catalog. Update on every ingest.
- `log.md` — chronological append-only. Prefix `## [YYYY-MM-DD] <op> | <title>` — grep-parsable.

## Priority

1. Before creating a file → grep vault for existing note on same topic
2. Every end-of-session → hook writes to `04_SESSIONS/` automatically
3. Every major decision → ADR in `02_KNOWLEDGE/decisions/`
4. Vault grows — old notes updated with `updated: YYYY-MM-DD`, never deleted

## Orchestrator

Global routing rules live in `~/.claude/CLAUDE.md`. This file is the **"where to save"** layer. Orchestrator is the **"how to work"** layer.
