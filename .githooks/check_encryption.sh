#!/bin/sh
# Encryption guard. Usage: check_encryption.sh index | tree <commit>
# Fails (exit 1) when git-crypt is missing/locked or a protected path is stored unencrypted.
# Protected: jobs/ voices/ inbox/ reference/ library/history.json and any facts.md / review.md.
mode="$1"
commit="$2"

fail() {
  echo "[encryption-guard] BLOCKED: $1" >&2
  exit 1
}

if [ -z "$ENCRYPTION_GUARD_CI" ]; then   # CI inspects committed blobs only (it never holds the key at this step)
  command -v git-crypt >/dev/null 2>&1 || fail "git-crypt is not installed (see docs/SETUP_LOCAL.md)"
  [ -n "$(git config --get filter.git-crypt.smudge 2>/dev/null)" ] || fail "repository is locked (run: git-crypt unlock <key file>)"
fi

MAGIC=004749544352595054   # "\0GITCRYPT" as hex
EMPTY=e69de29bb2d1d6434b8b

is_protected() {
  case "$1" in
    jobs/*|voices/*|inbox/*|reference/*|library/history.json|*/facts.md|*/review.md|facts.md|review.md) return 0 ;;
  esac
  return 1
}

list_blobs() {
  if [ "$mode" = "tree" ]; then
    git -c core.quotepath=false ls-tree -r "$commit"
  else
    git -c core.quotepath=false ls-files -s
  fi
}

TAB=$(printf '\t')
bad=$(list_blobs | while IFS="$TAB" read -r meta path; do
  is_protected "$path" || continue
  if [ "$mode" = "tree" ]; then sha=$(echo "$meta" | awk '{print $3}'); else sha=$(echo "$meta" | awk '{print $2}'); fi
  case "$sha" in "$EMPTY"*) continue ;; esac
  head9=$(git cat-file blob "$sha" 2>/dev/null | head -c 9 | od -An -tx1 | tr -d ' \n')
  [ "$head9" = "$MAGIC" ] || echo "$path"
done)

if [ -n "$bad" ]; then
  echo "[encryption-guard] These protected files are NOT encrypted:" >&2
  echo "$bad" >&2
  fail "fix with: git-crypt status -f  (then re-add) and make sure the repo is unlocked"
fi
exit 0
