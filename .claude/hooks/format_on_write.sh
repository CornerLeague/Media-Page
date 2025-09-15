#!/usr/bin/env bash
set -euo pipefail

# Auto-format changed files after edits. Safe no-op if tools not installed.

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo .)"
cd "$ROOT"

# Collect modified files
mapfile -t FILES < <(git ls-files -m 2>/dev/null || true)
[[ "${#FILES[@]}" -eq 0 ]] && exit 0

have() { command -v "$1" >/dev/null 2>&1; }

# Split by extension
JS_TS=()
PY=()
MD_JSON_YML=()
for f in "${FILES[@]}"; do
  case "$f" in
    *.js|*.jsx|*.ts|*.tsx|*.css|*.scss|*.html) JS_TS+=("$f") ;;
    *.py) PY+=("$f") ;;
    *.md|*.json|*.yml|*.yaml) MD_JSON_YML+=("$f") ;;
  esac
done

# Prettier for web + md/json/yml
run_prettier() {
  local -a arr=("$@"); [[ ${#arr[@]} -eq 0 ]] && return 0
  if have pnpm; then pnpm dlx prettier --write "${arr[@]}" || true
  elif have npx; then npx -y prettier --write "${arr[@]}" || true
  fi
}

# Python formatters
run_python_fmt() {
  local -a arr=("$@"); [[ ${#arr[@]} -eq 0 ]] && return 0
  if have ruff; then ruff check --fix "${arr[@]}" || true; ruff format "${arr[@]}" || true
  elif have black; then black "${arr[@]}" || true
  fi
}

run_prettier "${JS_TS[@]}"
run_prettier "${MD_JSON_YML[@]}"
run_python_fmt "${PY[@]}"

exit 0