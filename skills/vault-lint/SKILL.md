---
name: vault-lint
description: "Use when user says 'lint the vault', 'health check', 'find stale notes', 'vault audit'. Scans for contradictions, orphan pages, stale claims, missing cross-refs. Produces lint report in 02_KNOWLEDGE/learnings/."
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Write"]
---

# vault-lint — Karpathy LLM Wiki Health Check

## When to use

User says:
- "lint the vault"
- "health check"
- "find stale notes"
- "vault audit"
- "any contradictions?"

## Checks to run

### 1. Contradictions
Grep for opposing claims on the same fact across pages. E.g., two notes saying different things about "X library version" or "Y config flag".

### 2. Stale claims
Pages with `date:` frontmatter older than 6 months that reference fast-moving topics (versions, APIs, services). Cross-reference `log.md` — if newer entries on same topic contradict, flag.

### 3. Orphan pages
Pages with zero inbound `[[wikilinks]]` from other notes. Grep all pages for links to each page. Report pages with 0 hits.

### 4. Concept gaps
Mentions of entities/concepts without their own page. Heuristic: capitalized multi-word terms mentioned in 3+ pages but not having a dedicated note.

### 5. Missing cross-refs
Pages on related topics that don't link to each other. E.g., two pattern notes on "caching" that don't reference each other.

### 6. Fillable gaps
Concept pages with `TBD` or empty sections that could be filled via `WebSearch` — flag for ingest.

### 7. Index drift
Pages in `02_KNOWLEDGE/` not listed in `index.md`, or index entries pointing to deleted files.

## Output

Write report to `02_KNOWLEDGE/learnings/YYYY-MM-DD-vault-lint.md`:

```md
---
type: learning
date: YYYY-MM-DD
tags: [vault, lint, audit]
---

# Vault Lint — YYYY-MM-DD

## Summary
- N pages scanned
- X contradictions
- Y orphans
- Z stale

## Contradictions
- [[page-a]] vs [[page-b]]: <claim>

## Orphans
- [[page-c]] — suggest: link from [[page-d]]

## Stale
- [[page-e]] — last updated YYYY-MM-DD, references <topic>, newer info in [[log.md]] line N

## Gaps
- Concept "<X>" mentioned in 3 pages, no dedicated note
- Suggested ingest: <WebSearch query>

## Index drift
- [[page-f]] in 02_KNOWLEDGE/ but missing from index.md
- index.md → [[dead-link]] no longer exists

## Actions
- [ ] Resolve contradiction X
- [ ] Link orphan Y from Z
- [ ] Update stale page E
```

Append to `log.md`:
```
## [YYYY-MM-DD] lint | N findings
Report: [[02_KNOWLEDGE/learnings/YYYY-MM-DD-vault-lint]]
```

## Rules

- Read-only by default — report findings, don't auto-fix
- Only write the lint report itself
- If user says "fix automatically" → do fixes one at a time with explicit confirmation each
