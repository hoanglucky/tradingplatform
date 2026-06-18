#!/usr/bin/env bash
set -euo pipefail

REMOTE_NAME="${REMOTE_NAME:-origin}"
DEFAULT_BRANCH="${DEFAULT_BRANCH:-main}"
COMMIT_MESSAGE="${*:-chore: update trading framework}"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: run this script inside a git repository." >&2
  exit 1
fi

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$CURRENT_BRANCH" == "HEAD" ]]; then
  echo "Error: detached HEAD. Checkout a branch before pushing." >&2
  exit 1
fi

if ! git remote get-url "$REMOTE_NAME" >/dev/null 2>&1; then
  git remote add "$REMOTE_NAME" "https://github.com/hoanglucky/tradingplatform.git"
fi

echo "Remote:"
git remote -v
echo

echo "Current branch: $CURRENT_BRANCH"
echo "Checking working tree..."

if git diff --quiet && git diff --cached --quiet && [[ -z "$(git ls-files --others --exclude-standard)" ]]; then
  echo "No changes to commit."
else
  git add .
  git commit -m "$COMMIT_MESSAGE"
fi

if git rev-parse --abbrev-ref --symbolic-full-name "@{u}" >/dev/null 2>&1; then
  git push
else
  TARGET_BRANCH="$CURRENT_BRANCH"
  if [[ -z "$TARGET_BRANCH" ]]; then
    TARGET_BRANCH="$DEFAULT_BRANCH"
  fi
  git push -u "$REMOTE_NAME" "$TARGET_BRANCH"
fi

echo "Done."

