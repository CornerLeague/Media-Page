#!/usr/bin/env bash
set -euo pipefail

# Blocks edits to sensitive files. Exits non-zero to halt the tool.
# Tries to read the target path from Claude env; falls back to $1 or recent git changes.

TARGET="${CLAUDE_TARGET_PATH:-${1:-}}"

get_recent_changes() {
  git ls-files -m 2>/dev/null || true
}

is_sensitive() {
  case "$1" in
    *.env|.env|.env.*|**/*.pem|**/*.key|**/*.crt) return 0 ;;
    infra/prod/*|**/k8s/prod/*|**/terraform/prod/*) return 0 ;;
    .github/workflows/*prod*|.github/workflows/release*.yml) return 0 ;;
    supabase/.env|supabase/config.toml) return 0 ;;
    *) return 1 ;;
  esac
}

check_one() {
  local p="$1"
  [[ -z "$p" ]] && return 1
  if is_sensitive "$p"; then
    echo "❌ Blocked edit to sensitive path: $p" >&2
    echo "Tip: make changes via a reviewed PR or update allowlist in protect_sensitive.sh." >&2
    exit 1
  fi
}

if [[ -n "${TARGET}" ]]; then
  check_one "$TARGET"
else
  # Scan recently modified files as a fallback
  CHANGED="$(get_recent_changes)"
  while IFS= read -r f; do
    [[ -n "$f" ]] && check_one "$f"
  done <<< "$CHANGED"
fi

# Allow the tool to proceed
exit 0