
# Sports Media Platform — `initial.md` (Claude Code)

## Personalized sports news feed with on-demand AI summaries, powered by FastAPI + Supabase/Postgres, React + shadcn/ui, Firebase auth, Redis for queues/cache, and typed agent workflows.

---

## 0) Quick Pitch (MVP)
A web app that personalizes team content from onboarding to a data-driven home page:
- Users select sports (ordered) and teams during onboarding.
- Home shows the user’s **most‑liked team**: latest score + recent results, **news cards**, **AI short summary**, categorized intel (injuries, roster moves, trade rumors, depth chart), **ticket deals**, and **fan experiences**.  
- Realtime updates during live games.

---

## 1) Tech Stack & Tooling

**Frontend**: Next.js (TypeScript, App Router), SSR + client hydration  
**API**: FastAPI (Python, async), REST + WebSocket for live updates  
**DB**: Supabase Postgres + RLS; Supabase Storage for snapshots  
**Workers/Queue**: Celery + Redis (scheduled scrapes, ranking, summarization)  
**Containers**: Docker (dev via Compose; prod blue‑green / K8s‑ready)  
**Observability**: Prometheus + Grafana + Loki + Tempo  
**Security**: Firebase auth (JWT), strict CORS, SAST via Semgrep, non‑root containers  
**Scraping**: Ethical crawling (robots.txt, rate limiting) via proxy; MinHash de‑dup  
**Ranking**: BM25 indexes per team/category (memory‑mapped)

**Developer MCPs (for reviews/tooling only):**
- **Archon MCP** — documentation reviews
- **Playwright MCP** — frontend review + a11y checks
- **Semgrep MCP** — static analysis / security
- **Exa MCP** — supplemental docs/search for intel gathering

> Claude Code: enable these MCP servers if available in your environment. Keep them **dev‑only**.

---

## 2) Repository Layout (proposed)

```
/app
  /web/            # Next.js (TypeScript, App Router)
  /api/            # FastAPI service
  /workers/        # Celery tasks (scrapers, summarizer, ranks)
  /infra/          # Docker, compose, k8s manifests (optional)
  /scripts/        # one-off scripts and CLIs
  /docs/           # this file + ADRs + diagrams
  /tests/          # unit/integration/e2e specs
.env.example
README.md
```

**Web substructure**
```
/app/web
  /app/                # Next.js app router
  /components/         # UI components
  /lib/                # client utils (fetchers, ws)
  /styles/             # Tailwind/CSS
```

**API substructure**
```
/app/api
  /src/
    main.py            # FastAPI entry
    deps.py            # auth & db deps
    routes/            # routers by domain
    models/            # pydantic
    db/                # SQLAlchemy + queries
    ws/                # websocket events
```

**Workers substructure**
```
/app/workers
  tasks/               # celery tasks
  pipelines/           # scrape -> parse -> classify -> publish
  agents/              # Scores, News, DepthChart, Tickets, Experiences
  dev_agents/          # Planner, ContentClassification (dev-only)
```

---

## 3) Environment & Running Locally

1. **Prereqs**
   - Node 20+, PNPM/Yarn, Python 3.11+, Docker, Redis
   - Supabase project + service key
   - Firebase project with Authentication enabled

2. **Copy envs**
   ```bash
   cp .env.example .env
   ```

3. **Key env vars**
   ```bash
   # Firebase Auth
   FIREBASE_PROJECT_ID=...
   FIREBASE_PRIVATE_KEY=...
   FIREBASE_CLIENT_EMAIL=...
   FIREBASE_WEB_API_KEY=...
   FIREBASE_AUTH_DOMAIN=...

   # Supabase
   SUPABASE_URL=...
   SUPABASE_ANON_KEY=...
   SUPABASE_SERVICE_ROLE_KEY=...
   DATABASE_URL=postgresql://... # for API/workers migrations

   # Redis
   REDIS_URL=redis://localhost:6379/0

   # Scraping
   PROXY_URL=...
   ALLOWED_SOURCES=espn.com, theathletic.com, nba.com, mlb.com, nfl.com

   # LLM (summaries)
   LLM_PROVIDER=openai|anthropic|...
   LLM_API_KEY=...
   ```

4. **Run dev services**
   ```bash
   docker compose up -d     # db, redis, grafana stack
   pnpm -C app/web dev      # Next.js
   uvicorn app.api.src.main:app --reload  # FastAPI
   celery -A app.workers.tasks.celery_app worker -l INFO
   celery -A app.workers.tasks.celery_app beat -l INFO
   ```

5. **Playwright & Semgrep (optional)**
   ```bash
   pnpm -C app/web dlx playwright install
   semgrep --config p/ci
   ```

---

## 4) Product Scope — In/Out (MVP)

**In scope**
- Onboarding (auth → pick sports → order → pick teams per sport)
- Home for the **most‑liked team**:
  - Latest score + recent results
  - News cards (de‑duplicated)
  - AI short summary
  - Auto‑sorted: injuries, roster moves, trade rumors, depth chart
  - Ticket deals (best value)
  - Fan experiences

**Dev‑only (no UI)**
- Planner Agent
- Content Classification Agent

**Out of scope**
- Native mobile apps
- Social (comments/follows)
- Push/mobile notifications

---

## 5) User Flows

### 5.1 Onboarding
1) Authenticate with Firebase (email/password, Google, GitHub, etc.)
2) Select sports (multi‑select) → drag to set order
3) Select teams for any sport that has teams
4) Persist preferences (see schema below)

### 5.2 Home
- Top dropdown: sports in saved order
- Hero: most‑liked team
  - Scores widget: live/latest + recent history
  - News cards with category chips
  - Short AI summary (2–3 sentences)
  - Depth chart table (if available)
  - Ticket deals carousel
  - Fan experiences list
- WebSocket: live updates for scores & breaking news

---

## 6) Database (Supabase Postgres, RLS enabled)

**Users & Preferences**
- `user_profile(id, firebase_uid, display_name, email, location_geo, created_at)`
- `user_sport_prefs(user_id, sport_id, rank)` (unique: user_id, rank)
- `user_team_follows(user_id, team_id, affinity_score, created_at)`

**Sports & Teams**
- `sport(id, name, has_teams)`
- `team(id, sport_id, name, slug, league, market)`

**Games & Scores**
- `game(id, team_id_home, team_id_away, start_time, venue, status)`
- `score(game_id, team_id, pts, period, is_final, updated_at)`

**News & Processing**
- `article(id, team_id, source, title, url, published_at, snapshot_uri, body_text, hash_min)`
- `article_classification(article_id, category ENUM[injury, roster, trade, general], confidence, rationale_json)`
- `article_entities(article_id, entity_type, value)`

**Depth Chart**
- `depth_chart(id, team_id, position, player_name, depth_order, source, captured_at)`

**Tickets**
- `ticket_deal(id, game_id, provider, section, row, price, seat_quality, fees_est, availability, captured_at, deal_score)`

**Fan Experiences**
- `experience(id, team_id, type, title, url, venue, start_time, end_time, location_geo, quality_score, captured_at)`

**Pipelines & Ops**
- `agent_run(id, agent_type, subject_key, status, started_at, finished_at, meta_json, error_text)`
- `scrape_job(id, subject_type, subject_id, job_type, scheduled_for, status, last_run_at)`
- `source_registry(id, name, base_url, crawl_rules_json, credibility_score)`

**Indexes**
- GIN on `article(body_text, title)`; btree on (`published_at`, `team_id`)

**RLS (examples)**
- `user_profile`: user can `SELECT/UPDATE` where `firebase_uid` matches JWT `sub` claim
- Content tables: read‑only to authed users; writes only via service role

---

## 7) API Contracts (FastAPI)

**Auth:** Validate Firebase JWT in middleware; inject `user_id` from `sub` claim

### 7.1 User & Prefs
- `GET /me` → profile
- `PUT /me` → update profile
- `GET /me/preferences` → sports order + teams
- `PUT /me/preferences` → upsert `{ sports:[{id,rank}], teams:[team_id] }`

### 7.2 Home/Team
- `GET /me/home` → resolves most‑liked team → dashboard payload
- `GET /teams/{team_id}/dashboard` →
  ```json
  {
    "team": {"id":"bos-celtics","name":"Boston Celtics"},
    "latestScore": {"gameId":"g123","status":"FINAL","home":{"id":"bos","pts":112},"away":{"id":"mia","pts":106}},
    "recentResults": [{"gameId":"g122","result":"W","diff":7,"date":"2025-09-10"}],
    "summary": {"text":"Two-game streak; Brown probable (knee).","generated_at":"2025-09-12T20:10:05Z"},
    "news": [{"id":"a1","title":"Team signs ...","category":"roster","published_at":"2025-09-12T18:02:00Z"}],
    "depthChart":[{"position":"SG","player_name":"...","depth_order":1}],
    "ticketDeals":[{"provider":"StubHub","price":92,"section":"110","deal_score":0.84}],
    "experiences":[{"type":"watch_party","title":"Bar X viewing","start_time":"2025-09-14T21:00:00Z"}]
  }
  ```

### 7.3 News & Summaries
- `GET /teams/{team_id}/news?limit&category`
- `GET /teams/{team_id}/summary` → `{ text, generated_at }`

### 7.4 Realtime
- `WS /ws/teams/{team_id}` events: `score_update`, `breaking_news`, `ticket_update`

### 7.5 Admin/Dev (protected)
- `POST /dev/plan` — enqueue Planner runs
- `POST /dev/reindex` — rebuild BM25 per team/category
- `GET /dev/healthz` — liveness checks
- `GET /dev/runs/{id}` — pipeline run details

---

## 8) Agents & Pipelines

### 8.1 Scores Agent
- Sources: premium APIs + official game centers
- Cadence: live 10–30s; non‑live hourly; schedule daily
- Logic: cross‑source validate → write `game`/`score` → WS events
- SLO: <5s p50 latency for live pushes; no duplicate finals

### 8.2 News Scraping Agent
- Sources: curated outlets (robots aware via proxy)
- Pipeline: fetch → snapshot → parse → MinHash de‑dup → BM25 index per team
- SLO: no exact duplicates; ≥95% team relevance

### 8.3 Content Classification Agent (dev‑only)
- Method: multi‑corpus BM25 (corpora: injury, roster, trade, general)
- Output: `article_classification` (confidence + rationale)
- Policy: precision ≥90%; ambiguous → `general`

### 8.4 AI Summary Bot
- Input: top‑N articles (freshness‑weighted) + entities
- Output: 2–3 sentence summary; no hallucinated transactions; sources logged
- Cache: per team, TTL 10min; invalidate on breaking flag

### 8.5 Depth Chart Parser
- Discovery via BM25 → source‑specific parsers → normalized rows

### 8.6 Stadium Seat Agent
- Normalize fees, seat location, availability → `deal_score`

### 8.7 Fan Experience Agent
- Sources: watch parties/bars/community calendars; geofenced
- Scoring: proximity + quality + recency

### 8.8 Planner Agent (dev‑only)
- Orchestrates scrape → parse → rank → classify → publish
- Backoff on failure; circuit‑break per source

---

## 9) Scheduling (Celery Beat — defaults)
- Scores (live): 10–30s
- Scores (non‑live): 1h
- News: every 10m per active team; daily backfill
- Depth chart: 1–2/day
- Tickets: 4h (1h ≤72h to tip‑off)
- Experiences: daily
- Summary: on breaking or every 10m idle

---

## 10) Observability & Alerts
**Dashboards**: API latency, WS fan‑out, scrape success, de‑dup ratio, BM25 freshness, summary cache hit, ticket price drift, RLS deny counts, cost trend  
**Alerts**
- Critical: scores stale >2m live; 5xx >2%; queue depth high
- Warning: index stale >6h; de‑dup anomaly
- Info: weekly cost budget trend

---

## 11) Security & Compliance
- Firebase JWT on every request; validate with Firebase Admin SDK; map to `user_profile`
- Supabase RLS: least privilege; service role for workers
- CORS allowlist; HTTPS only; non‑root containers
- Secrets via orchestrator; read‑only FS where possible
- SAST via Semgrep on PR; Playwright a11y checks
- Scraping ethics: robots.txt, rate limit, snapshotting for audit

---

## 12) CI/CD
- **CI**: lint/typecheck, unit tests, Semgrep, container build, Playwright E2E
- **CD**: staging→prod via blue‑green; versioned DB migrations w/ rollback
- **Feature Flags**: enable/disable agents per sport/league

---

## 13) Testing Plan (MVP)
- **Unit**: classification margins, de‑dup, deal scoring, RLS
- **Integration**: scrape→snapshot→parse→classify→publish→API
- **E2E**: onboarding, home data render, live score push, news→summary, tickets/experiences
- **Load**: WS fan‑out 5k concurrent; ingest burst 50/min

---

## 14) Acceptance Criteria (Done = ✅)
- Onboarding persists sports order + teams
- Home auto‑selects most‑liked team, shows:
  - Latest score (or live badge) + last 5 results
  - ≥6 deduped news cards (≤24h old) w/ category chips
  - AI summary (timestamped)
  - Depth chart table (if extractable)
  - ≥3 ticket deals & ≥3 experiences when sources exist
- Live score updates p50 <5s
- Observability dashboards live; critical alerts wired
- RLS enforced; Semgrep + Playwright pass on CI
- Blue‑green deploy works end‑to‑end

---

## 15) Work Plan (Next 2 Sprints)

**Sprint 1**
- Scaffold Next.js + Firebase Auth; onboarding UI (sports→order→teams)
- FastAPI skeleton; `/me`, preferences endpoints; Supabase schema & RLS
- Celery + Redis; Planner skeleton; Scores Agent (one league); WS channel
- Home page w/ team + scores; Grafana stack up

**Sprint 2**
- News Scraping Agent + MinHash de‑dup + per‑team BM25
- Content Classification (dev‑only) + category chips
- AI summary service w/ cache + invalidation
- Tickets Agent (one provider), Experiences Agent (one source)
- Depth Chart parser (one reliable source)
- CI (Semgrep, Playwright), blue‑green deploy, alerting

---

## 16) Claude Code — Operating Guidelines

**When editing code:**
- Follow this `initial.md` and prefer **small PRs** with commit messages:
  `feat(web): add ScoresWidget with live WS updates`
- Create/modify code only under relevant service directories.
- Add/modify tests alongside code.
- For breaking changes, propose an ADR in `/docs/adr/XXXX-title.md`.

**When implementing features:**
1. Draft a short plan (bulleted) before writing code.
2. Touch the minimal number of files.
3. Add telemetry (metrics/logs) where appropriate.
4. Update `.env.example` if new envs are introduced.

**Use MCP servers only for dev reviews** (Playwright, Semgrep, Archon, Exa). Do **not** add UI for them.

**Style/Conventions:**
- Web: React Server Components where possible, SWR/React Query for client fetch, Tailwind for styling.
- API: pydantic models; dependency‑injected db sessions; 2xx/4xx/5xx semantics.
- Workers: idempotent tasks; retries with jitter; structured logs.

---

## 17) Glossary
- **Most‑liked team**: the first selected team, modulated by recent engagement (clicks/views).
- **BM25**: ranking algorithm used for per‑team relevance + category classification (dev‑only corpora).

---

## 18) Appendix — Sample DB DDL (sketch)

```sql
-- Users
create table if not exists user_profile (
  id uuid primary key default gen_random_uuid(),
  firebase_uid text unique not null,
  display_name text,
  email text,
  location_geo jsonb,
  created_at timestamptz default now()
);

create table if not exists user_sport_prefs (
  user_id uuid references user_profile(id) on delete cascade,
  sport_id text not null,
  rank int not null,
  primary key (user_id, rank)
);

create table if not exists user_team_follows (
  user_id uuid references user_profile(id) on delete cascade,
  team_id text not null,
  affinity_score real default 0,
  created_at timestamptz default now(),
  primary key (user_id, team_id)
);
```

---

## 19) Licensing & Compliance
- Respect site terms; use snapshots for auditability.
- Keep sensitive keys out of source; use `.env` and secret stores.
- Attribute sources where required; avoid redistributing paid content.
