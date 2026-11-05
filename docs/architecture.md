# Tech Stack and Architecture

> When to read: before structural changes, new components, new dependencies, or anything touching data flow, privacy or the LLM layer.

## Monorepo layout

| Folder | Purpose |
|---|---|
| `app/` | Flutter mobile app (Android, iOS) |
| `backend/` | Python API (FastAPI) and job worker (Procrastinate) |
| `website/` | Astro landing page, deployed to GitHub Pages |
| `supabase/` | Supabase config and SQL migrations (not created yet, see below) |
| `docs/` | Project documentation for agents and humans |

## Tech stack

- **App:** Flutter (Dart 3.13+), state management with **Riverpod** (`flutter_riverpod`). Speech-to-text and text-to-speech use **on-device platform APIs** only; audio never leaves the device and is never stored.
- **Backend:** Python 3.14, **FastAPI**, managed with **uv**. Game logic, round state machine, LLM calls, scoring.
- **Jobs:** **Procrastinate** (Postgres-based queue). Chosen over Redis: no extra service, and job enqueueing can share the transaction with round state changes (idempotent transitions).
- **Data/Auth:** **Supabase** in an EU region: Postgres plus Auth (email, Sign in with Apple, Google). The backend verifies Supabase JWTs; the app talks to the backend for all game data.
- **LLM:** **Mistral** (EU) behind a provider-agnostic interface in the backend. Every LLM output that drives the game is structured JSON validated with Pydantic.
- **Push:** Firebase Cloud Messaging (APNs via FCM).
- **Website:** **Astro** static site with Astro i18n (`defaultLocale: 'en'`, only English strings for now), deployed by `.github/workflows/website.yml` to `https://sphaerox.github.io/Dicrates/`.

## Architecture rules

- **Rounds are a state machine:** `FORMING → R1_OPEN → R1_CLOSED → R2_OPEN → R2_CLOSED → R3_OPEN → R3_CLOSED → R4_EVALUATING → FINISHED → ARCHIVED`, plus `ABORTED`. Transitions run only in jobs, are idempotent and deterministic (safe to retry).
- **Anonymity is enforced server-side:** clients never receive raw submissions of other members, only LLM summaries of their room. The account ↔ submission mapping exists only in the backend (Supabase RLS denies direct client reads of submission tables).
- **LLM layer:** one module owns all provider calls. Prompts are versioned files; each stored summary/evaluation records its prompt version. Logs contain no plain-text personal data. Add retries and schema validation for every call.
- **Political opinions are GDPR Art. 9 data:** collect explicit consent, minimize stored text, support account and content deletion, keep processing in the EU.
- **i18n from day one:** no hard-coded user-facing strings in app or website. App and website start with **English** as the base language; more languages come later. LLM prompts take the room language as a parameter.

## Environment

- **Backend:** exactly one project-local virtual env at `backend/.venv`, managed by uv (`uv sync` inside `backend/`). Never install globally. Run tools via `uv run ...` or `.venv\Scripts\python.exe -m ...` (Windows) / `.venv/bin/python -m ...`.
- **App:** Flutter stable (3.47+). Dependencies only via `flutter pub add`. Public Supabase values reach the app through `--dart-define`, never the service role key.
- **Website:** Node 24 (CI) / ≥22.23, npm only (`package-lock.json` is committed).
- **Configuration and secrets:** root `.env` (template: `.env.example`, which lists every variable and its purpose). The backend will load it with `pydantic-settings`.

## First implementation steps (setup not done yet)

- Supabase: Supabase CLI is not installed. Run `npx supabase init` in the repo root to create `supabase/`, then `npx supabase start` for the local stack (needs Docker).
- Backend runtime dependencies (FastAPI, uvicorn, procrastinate, pydantic-settings, mistralai) are not added yet; add them with `uv add` when the first code needs them.
- App: `app/` is the unmodified `flutter create` output (counter demo + its widget test). Replace it with the real app structure; set up `flutter_localizations`/ARB files for i18n.
- Website: `website/` is the Astro minimal starter. Build the landing page with i18n string files under `src/i18n/`.
- GitHub Pages must use "GitHub Actions" as the source.

## Open decisions

- Android/iOS bundle id is `io.github.sphaerox.dicrates` (placeholder until a domain exists).
- See `docs/project-brief.md` for product-level open decisions.

---
Maintenance: update this file immediately whenever stack or architecture changes.
