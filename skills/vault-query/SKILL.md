---
name: vault-query
description: "Use when user asks 'what do we know about X?', 'have we solved this before?', 'find notes on Y'. Reads vault index → drills into relevant pages → synthesizes answer with [[wikilink]] citations. Karpathy LLM Wiki pattern."
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# vault-query — Karpathy LLM Wiki Query

## When to use

User asks:
- "what do we know about X?"
- "have we solved this before?"
- "find notes on Y"
- "any learnings about Z?"
- "check the vault for …"

## Process

1. **Locate vault** — read `$VAULT_PATH` from `~/.claude/CLAUDE.md` or probe standard locations
2. **Read `index.md`** — catalog-first retrieval
3. **Grep for topic** across `02_KNOWLEDGE/` + `03_REFERENCE/` + `00_INBOX/` — pattern: case-insensitive substring or tag match
4. **Drill into matching pages** — read relevant ones
5. **Synthesize answer** with citations:
   ```
   Based on vault: X works this way because [[02_KNOWLEDGE/patterns/x|X pattern]].
   Seen in: [[01_PROJECTS/proj-a]], [[01_PROJECTS/proj-b]].
   Gotcha documented in [[02_KNOWLEDGE/learnings/x-edge-case]].
   ```
6. **Promote valuable queries** — if the synthesis itself is novel (comparison across sources, new connection), ask user: "save as new page?" → if yes, write to `02_KNOWLEDGE/` and update index
7. **Append to log.md**:
   ```
   ## [YYYY-MM-DD] query | <question>
   Answered from [[...pages...]]
   ```

## Fallback

If nothing in vault matches → say so explicitly. Do NOT fabricate. Offer to:
- Run `vault-ingest` on a new source to fill the gap
- Run WebSearch if online info would help

## Output format

- Lead with direct answer
- Follow with citations as `[[wikilink]]`
- End with confidence level: "high (3 sources agree)" / "medium (single source)" / "low (inferred)"
