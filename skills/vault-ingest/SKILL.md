---
name: vault-ingest
description: "Use when user says 'ingest', 'save this to vault', 'remember this source', or drops an article/PDF/note to summarize. Reads source → writes structured page to vault → updates index.md + log.md. Karpathy LLM Wiki pattern."
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "WebFetch"]
---

# vault-ingest — Karpathy LLM Wiki Ingest

## When to use

User says:
- "ingest this [article/PDF/note]"
- "save this to vault"
- "remember this source"
- "take notes on this"

Or drops a URL / file / long paste and expects it saved for later retrieval.

## Process

1. **Read source** — file, URL, or pasted text
2. **Discuss takeaways** with user in chat — confirm what's worth keeping vs noise
3. **Classify target folder**:
   - Raw / triage-later → `00_INBOX/`
   - Reusable solution across projects → `02_KNOWLEDGE/patterns/`
   - Architectural decision with alternatives → `02_KNOWLEDGE/decisions/` (ADR-NNN)
   - Milestone retrospective → `02_KNOWLEDGE/retros/`
   - Single fix / gotcha / learning → `02_KNOWLEDGE/learnings/`
   - Stable reference doc → `03_REFERENCE/`
4. **Write summary page** — structured markdown with frontmatter:

   ```md
   ---
   type: pattern | decision | retro | learning | inbox | reference
   date: YYYY-MM-DD
   tags: [tag1, tag2]
   source: <url or path>
   ---

   # <Title>

   ## Summary
   <2-3 sentences of the core takeaway>

   ## Key points
   - <point>
   - <point>

   ## Related
   - [[other-note|title]]
   ```

5. **Update `index.md`** — add entry under the right section, format:
   ```
   - [[02_KNOWLEDGE/<type>/<slug>|<title>]] — <one-line hook>
   ```
6. **Append to `log.md`**:
   ```
   ## [YYYY-MM-DD] ingest | <type> | <title>
   <one-line hook>. See [[02_KNOWLEDGE/<type>/<slug>]]
   ```
7. **Update related pages** — if new page references existing entities/concepts, add backlinks there too

## Boundaries

- Do NOT ingest conversation noise (casual Q&A, status checks)
- Do NOT duplicate — grep vault first for existing entry on same topic
- Do NOT fabricate — only content actually in source
- If nothing qualifies: say "nothing durable to save" and exit

## Locate vault

Read `$VAULT_PATH` from `~/.claude/CLAUDE.md` or probe `~/Workspace`, `~/Desktop/Workspace`, `~/vault` in that order. Confirm with user if ambiguous.
