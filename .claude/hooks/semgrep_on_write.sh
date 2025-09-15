#!/usr/bin/env bash
set -euo pipefail

# Run Semgrep after edits on changed files. Fails the step on blocking findings.

have() { command -v "$1" >/dev/null 2>&1; }
have semgrep || exit 0

# Gather changed files (limit language sets Semgrep recognizes)
mapfile -t FILES < <(git ls-files -m \
  | grep -E '\.(py|ts|tsx|js|jsx|go|java|rb|php|cs|kt|scala|yaml|yml)$' || true)

[[ "${#FILES[@]}" -eq 0 ]] && exit 0

# Build --include args for speed
ARGS=()
for f in "${FILES[@]}"; do
  ARGS+=( "--include" "$f" )
done

# Use your org policy or public registry; adjust as needed
semgrep --error --config p/ci "${ARGS[@]}" || {
  echo "❌ Semgrep found issues in changed files." >&2
  exit 1
}
markdown
Copy code
