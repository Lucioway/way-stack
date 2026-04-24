#!/usr/bin/env bash
# way-stack SessionEnd hook — git-commit any vault changes after a session.
# Silent no-op if vault isn't a git repo. Never pushes — local only.

set -eu

VAULT="__VAULT_PATH__"
[ -d "$VAULT/.git" ] || exit 0

cd "$VAULT"

# Only commit if there are actual changes (staged or unstaged or untracked)
if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
  git add -A
  git commit -m "chore(vault): auto-backup $(date +%Y-%m-%d\ %H:%M)" >/dev/null 2>&1 || true
fi

exit 0
