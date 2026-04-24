---
name: stack-bootstrap
description: "One-shot installer for the full way-stack — creates PARA+Karpathy vault, installs orchestrator CLAUDE.md, registers session hooks, adds 5 upstream marketplaces, installs 5 plugins, fetches 7 design skills. Interactive: asks only vault path."
---

# /stack-bootstrap — Full Stack Installer

You are the way-stack bootstrap installer. Execute the 10-step install in order. Halt on any error and report which step failed. Never skip verification.

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

Copy `${CLAUDE_PLUGIN_ROOT}/templates/orchestrator-CLAUDE.md` → `~/.claude/CLAUDE.md`. If exists, back up to `~/.claude/CLAUDE.md.bak-$(date +%s)` first.

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
    ]
  }
}
```

Preserve existing hooks — append, don't replace. Use `jq` if available.

## STEP 7 — Add upstream marketplaces

Run these Claude Code commands (use Bash tool with `claude` CLI, or instruct user to paste):

```
/plugin marketplace add anthropics/claude-plugins
/plugin marketplace add obra/superpowers-marketplace
/plugin marketplace add HKUDS/CLI-Anything
/plugin marketplace add JuliusBrussee/claude-code-caveman
/plugin marketplace add thedotmack/thedotmack-plugins
```

## STEP 8 — Install upstream plugins

```
/plugin install superpowers@claude-plugins-official
/plugin install frontend-design@claude-plugins-official
/plugin install code-review@claude-plugins-official
/plugin install ralph-loop@claude-plugins-official
/plugin install cli-anything@cli-anything
```

## STEP 9 — Fetch design skills

```bash
mkdir -p ~/.claude/skills && cd ~/.claude/skills

# wondelai/skills — 5 design skills
for s in refactoring-ui ux-heuristics hooked-ux design-sprint ios-hig-design; do
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
```

If `git clone` fails (repo moved / renamed), log warning and continue — don't halt.

## STEP 10 — Verify install

Run `/stack-verify`. Report pass/fail summary to user:

```
✓ Vault created at <path>
✓ Orchestrator installed
✓ Hooks registered
✓ 5 plugins installed
✓ 7 design skills fetched
⚠ 1 skill failed (nextlevelbuilder moved) — install manually
```

## Error handling

- Any step that fails → print which step + exact error + remediation hint
- Never rollback automatically — user's files are sacred
- Idempotent: re-running `/stack-bootstrap` must be safe
