---
name: stack-bootstrap
description: "One-shot installer for the full way-stack — creates PARA+Karpathy vault, installs orchestrator CLAUDE.md, registers session hooks, adds 5 upstream marketplaces, installs 6 plugins (incl. caveman), fetches 7 design skills, installs 3 frameworks (GSD, BMAD, gstack). Interactive: asks only vault path + framework opt-ins."
---

# /stack-bootstrap — Full Stack Installer

You are the way-stack bootstrap installer. Execute the 11-step install in order. Halt on any error and report which step failed. Never skip verification.

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
/plugin install caveman@claude-code-caveman
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

## STEP 10 — Install frameworks (optional, ask once per framework)

Frameworks are heavyweight (50–100+ skills each). Ask the user which to install. Default = ALL.

> Install frameworks? GSD, BMAD, gstack — pick any/all/none. (default: all)

### 10a — GSD (Get-Shit-Done) — gsd-build/get-shit-done

```bash
# Requires Node.js 18+
npx -y get-shit-done-cc --claude --global
```

Installs `~/.claude/get-shit-done/` runtime + `~/.claude/skills/gsd-*/` (~70 skills) + `~/.claude/agents/gsd-*` agents. Adds `/gsd-*` slash commands.

### 10b — BMAD-METHOD v6 — bmad-code-org/BMAD-METHOD

```bash
# Requires Node.js 20+
npx -y bmad-method install
```

Interactive installer. Pick `Claude Code` as host when prompted. Installs `~/.claude/skills/bmad/{core,bmm,bmb,cis}/` (9 skills) + `bmad:*` slash commands.

### 10c — gstack — garrytan/gstack

```bash
# Requires Bun (https://bun.sh) for build step
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup
```

Installs ~38 gstack skills (`/office-hours`, `/qa`, `/cso`, `/review`, `/ship`, `/design-review`, `/retro`, …) + `browse` headless browser binary.

If any framework install fails, log warning and continue — orchestrator template handles missing frameworks gracefully (marked "if installed").

## STEP 11 — Verify install

Run `/stack-verify`. Report pass/fail summary to user:

```
✓ Vault created at <path>
✓ Orchestrator installed
✓ Hooks registered
✓ 6 plugins installed (5 official + caveman)
✓ 7 design skills fetched
✓ Frameworks: GSD ✓ BMAD ✓ gstack ✓
⚠ 1 skill failed (nextlevelbuilder moved) — install manually
```

## Error handling

- Any step that fails → print which step + exact error + remediation hint
- Never rollback automatically — user's files are sacred
- Idempotent: re-running `/stack-bootstrap` must be safe
