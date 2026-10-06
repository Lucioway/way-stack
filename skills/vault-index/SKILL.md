---
name: vault-index
description: "Use when an agent must navigate a vault, or when the user says 'index the vault', 'refresh indexes', 'add index.md everywhere'. Writes an auto-generated index block into an index.md at every folder level; hand-written text outside the markers is preserved."
allowed-tools: ["Read", "Bash", "Glob"]
---

# vault-index — an index.md at every folder level

## When to use

Agents navigate a vault by reading, not by grepping blind. One `index.md` per folder (a short list of subfolders + notes with a one-line title each) lets an agent walk top-down and open only what it needs — Chase-style progressive disclosure. Run it after bulk imports, or weekly.

## Run

```bash
S="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/way-stack}/skills/vault-index/scripts/vault_index.py"
python3 "$S" --vault ~/Workspace --dry     # preview: lists CREATE / UPDATE lines
python3 "$S" --vault ~/Workspace           # apply
```

- Vault path: `--vault PATH` or env `WAY_VAULT`. Neither → the script errors with usage.
- `--follow-symlink NAME` (repeatable): descend into that symlinked folder. Default none: symlinked folders are only listed.
- Output ends with `changes=N written=M notes_total=K`. A second run must report `changes=0` (idempotent).

## Rules the script follows

- Writes ONLY between `<!-- auto-index:start -->` and `<!-- auto-index:end -->`. Text you wrote outside the markers is preserved. An existing `index.md` without markers gets the block appended.
- Missing `index.md` → created with a `# <folder>` header.
- A pre-existing `index.md` is copied to `index.md.bak` before its first rewrite.
- Skips `.obsidian .git node_modules .trash graphify-out` and dotfiles.
- A subfolder that is a git repo (contains `.git`) is listed as "repo, not indexed" and never entered.
- A folder with more than 300 notes is summarized by month instead of listed.

## Schedule weekly (optional)

```bash
# cron: Sunday 07:00
(crontab -l 2>/dev/null; echo '0 7 * * 0 WAY_VAULT=$HOME/Workspace python3 $HOME/.claude/plugins/way-stack/skills/vault-index/scripts/vault_index.py >> $HOME/.claude/vault-index.log 2>&1') | crontab -
```

On macOS prefer launchd if cron lacks disk access to your vault folder.
