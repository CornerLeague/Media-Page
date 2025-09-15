# Hooks for Claude Code

These hooks wire up:
- **PreToolUse / Edit|MultiEdit|Write** → `protect_sensitive.sh` (blocks edits to sensitive files)
- **PostToolUse / Edit|MultiEdit|Write** → `format_on_write.sh` (prettier/ruff/black)
- **PostToolUse / Edit|MultiEdit|Write** → `semgrep_on_write.sh` (security scan)

## Setup

```bash
chmod +x .claude/hooks/*.sh
