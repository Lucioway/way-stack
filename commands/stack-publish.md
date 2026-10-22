---
name: stack-publish
description: "Publish a new way-stack version — bumps plugin.json version, updates CHANGELOG.md, commits, tags, and pushes to origin. Run from inside the way-stack repo. Usage: /stack-publish <version> <description>"
---

# /stack-publish — One-shot release

Publish a new version of the way-stack plugin repo. Handles version bump, changelog, commit, tag, and push in one flow.

## Arguments

`$ARGUMENTS` = `<version> <description>`

Examples:
- `/way-stack:stack-publish 1.1.0 "add new agent-refine command"`
- `/way-stack:stack-publish 1.0.1 "fix vault path detection on Linux"`
- `/way-stack:stack-publish 2.0.0 "BREAKING: rename /agent-* to /sdd-*"`

Version must follow semver (MAJOR.MINOR.PATCH). Description goes into commit message + CHANGELOG.

## Preconditions

1. Current directory is the `way-stack` plugin repo root — verify by checking `.claude-plugin/plugin.json` exists
2. `git status` is clean OR has only changes the user WANTS to release — do not auto-stash
3. Current branch is `main` — warn if not
4. Remote `origin` exists and points to GitHub

Abort with clear error if any precondition fails.

## Process

### Step 1 — Parse version
Parse `$ARGUMENTS` into `VERSION` and `DESC`. Validate `VERSION` matches `^\d+\.\d+\.\d+$`.

### Step 2 — Confirm with user
Print a summary and ask for go/no-go:
```
Publishing way-stack v<VERSION>
Description: <DESC>

Changes to commit:
  <git diff --stat output>

Proceed? (yes/no)
```
Wait for explicit yes. Abort on anything else.

### Step 3 — Update plugin.json
Read `.claude-plugin/plugin.json`, update `"version"` field to `<VERSION>`, write back. Pretty-print (2-space indent).

### Step 4 — Update CHANGELOG.md
Prepend entry to `CHANGELOG.md` (create the file if it does not exist):

```md
# Changelog

## v<VERSION> — YYYY-MM-DD
- <DESC>

## v<prev-version> — YYYY-MM-DD
- <prev description>
...
```

### Step 5 — Commit + tag + push
Run:
```bash
git add .claude-plugin/plugin.json CHANGELOG.md <other-modified-files>
git commit -m "release: v<VERSION> — <DESC>"
git tag -a v<VERSION> -m "v<VERSION>: <DESC>"
git push origin main
git push origin v<VERSION>
```

### Step 6 — Report
```
✓ Published v<VERSION>
  Commit: <sha>
  Tag: v<VERSION>
  URL: https://github.com/<owner>/way-stack/releases/tag/v<VERSION>

Users can update:
  /plugin update way-stack
```

## Failure handling

- Push auth failure → print exact error, suggest `gh auth login` or PAT
- Tag already exists → suggest bumping further
- Non-clean working tree → show `git status`, let user fix manually
- Never force-push, never `--no-verify`

## Do NOT

- Do NOT auto-bump version (semantic meaning is user's judgment call)
- Do NOT publish from branches other than `main` without explicit confirmation
- Do NOT push when pre-commit hook fails — fix underlying issue first
- Do NOT delete old tags
