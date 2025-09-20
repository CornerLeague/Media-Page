## Claude Code Subagents — Sports Media Platform

This folder defines **task-scoped subagents** for Claude Code. They help you plan, code, test, and ship features consistently.

> **Dev-only agents:** `planner`, `content-classification`  
> These do not produce user-facing UI and should only run during development.

---

## 1) Install / Placement

1. Create this folder in your repo: `.claude/agents/`
2. Save each subagent file here (e.g., `frontend.md`, `backend.md`, …).
3. In Claude Code, open the repo root and run `/agents` to list them.

**Precedence:** Project agents in `.claude/agents/` override user-level agents in `~/.claude/agents/`.

---

## 2) Quick Start in Claude Code

- **List agents:** `/agents`
- **Use an agent explicitly:**  
  > “Use the **backend** subagent to scaffold `GET /teams/{team_id}/dashboard` and generate OpenAPI + tests.”
- **Plan Mode (read-only):** `Shift+Tab` to toggle (Normal → Auto-Accept → **Plan**), or start Claude with  
  `claude --permission-mode plan`  
  Default via `.claude/settings.json` → `permissions.defaultMode="plan"`

**Context tricks:**
- Pull files/dirs: `@app/web/app/`, `@app/api/src/main.py`
- Pull MCP resources: `@Archon:doc('initial.md')`

---

## 3) Subagents Catalog

- **planner** *(dev-only)* — Break down backlog into 1–4h tasks, delegate work, enforce gates.
- **frontend** — Next.js pages (`/onboarding`, `/home`, `/settings`) + components (`ArticleCard`, `SummaryPanel`, `SportFilter`, `TeamRanker`). Consumes Backend OpenAPI types.
- **backend** — FastAPI routes (Preferences, Feed, Summaries), Firebase JWT verify, Redis/Celery jobs. Publishes OpenAPI for FE.
- **db-etl** — Supabase/Postgres schemas, Alembic migrations, seeds, RSS/news ingestion with de-dup + FTS.
- **research** — Curates `feeds.yaml`, validates sources, documents parser quirks.
- **validation-testing** — Pytest, Vitest/RTL, Playwright e2e + `@axe-core/playwright`, visual snapshots.
- **release-pr** — GitHub Actions workflows, Semgrep CI, conventional commits, changelog, release tagging.
- **ops** — Docker Compose stack, env templates, CORS, basic OTEL traces/logs.
- **content-classification** *(dev-only)* — Explainable BM25 classification for {injury, roster, trade, general}.

---

## 4) Delegation & Handoffs (Policy)

Always **start with Archon** (docs/code review) before edits.  
Every handoff must include **typed I/O contracts**:

- OpenAPI/TS types for API boundaries
- DB schema/migration version (Alembic)
- Job payload schemas (Pydantic)

**Gate checklist (per task):**
- [ ] Archon research notes attached
- [ ] Typed contracts agreed (schemas/types)
- [ ] Unit + e2e tests updated
- [ ] **Semgrep** clean (no blockers)
- [ ] **A11y** clean (axe serious/critical = 0)
- [ ] Docs + `.env.example` updated
- [ ] Rollback plan documented

---

## 5) Handy Prompts

- **Planner:**  
  “Use **planner** to create a 2-sprint plan to ship the onboarding flow end-to-end. Output tasks sized 1–4h with acceptance criteria.”

- **Backend:**  
  “Use **backend** to add `GET /me/preferences`, Pydantic models, and update OpenAPI. Include httpx tests and retry/backoff policy.”

- **Frontend:**
  "Use **frontend** to implement `SportFilter` with TanStack Query and Firebase auth guards. Generate TS from OpenAPI first and add RTL + Playwright tests."

- **DB/ETL:**  
  “Use **db-etl** to add `article_classification` table and a migration. Document indexes and add an idempotent seed.”

- **Validation/Testing:**  
  “Use **validation-testing** to add Playwright a11y checks to `/home` and set up visual snapshots.”

---

## 6) Troubleshooting

- **Agent not listed?** Confirm `.md` files have YAML frontmatter (`name`, `description`, `tools`) and are in `.claude/agents/`. Reopen Claude Code or run `/agents` again.
- **Edits not applied?** Ensure you’re not in **Plan Mode** when you intend to write. Toggle with `Shift+Tab`.
- **Conflicting edits?** Avoid parallel edits to the same files; have **planner** serialize work.

---

## 7) Notes

- Keep **planner** and **content-classification** strictly dev-only.
- Prefer **small PRs** with clear titles, e.g.  
  `feat(web): add ScoresWidget with live updates`
- Update docs and envs when behavior or configuration changes.

---