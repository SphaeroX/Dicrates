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
- **Data/Auth:** **Supabase** in an EU region: Postgres plus Auth (email, Sign in with Apple, Google). The backend verifies Supabase access tokens (asymmetric ES256 signing keys) against the project JWKS endpoint `<SUPABASE_URL>/auth/v1/.well-known/jwks.json`, so no shared JWT secret is configured and key rotation needs no config change; the app talks to the backend for all game data.
- **LLM:** **Mistral** (EU) behind a provider-agnostic interface in the backend. Every LLM output that drives the game is structured JSON validated with Pydantic. The interface is **Pydantic AI** (`pydantic-ai-slim`): a model-agnostic agent framework, chosen so the provider is switched by configuration only, with typed structured output as Pydantic models and built-in test models. `LLM_MODEL` holds a Pydantic AI model string (`<provider>:<model>`, default `mistral:mistral-large-latest`) used for *all* LLM calls; keys come from the provider-standard env vars (`MISTRAL_API_KEY`, `GOOGLE_API_KEY`). **Google Gemini (`google:…`) is a dev-only fallback** while no working Mistral key exists: it is not EU-bound, so it may only see test data, and settings validation must refuse any non-`mistral:` model when `APP_ENV=production`.
- **Push:** Firebase Cloud Messaging (APNs via FCM).
- **Website:** **Astro** static site with Astro i18n (`defaultLocale: 'en'`, only English strings for now), deployed by `.github/workflows/website.yml` to `https://sphaerox.github.io/Dicrates/`.

## Backend package layout

- Code lives in `backend/src/dicrates/` (`package = false` in uv, so the project is not installed). pytest finds it via `pythonpath = ["src"]`, pyright via `extraPaths = ["src"]`, uvicorn via `--app-dir src`.
- `dicrates/main.py`: app factory `create_app()` and module-level `app`; `GET /health` returns `{"status": "ok", "version": ...}` (version in `dicrates/__init__.py`).
- `dicrates/core/settings.py`: `Settings` (pydantic-settings) reads env vars and the root `.env`; `LLM_MODEL` is parsed into `LlmModel(provider, model)`; `APP_ENV=production` refuses any non-`mistral:` model. Supabase/DB values are optional (`None`, empty strings count as unset) until the tasks that need them; secrets are `SecretStr`. Use `get_settings()` (cached) in app code.
- Feature packages (`rooms`, `rounds`, `questions`, `llm`, ...) are added next to `core/` as they are built.

## Backend runtime dependencies

| Package | Reason |
|---|---|
| `fastapi` | HTTP API framework with Pydantic-typed request/response models. |
| `uvicorn` | ASGI server to run the FastAPI app (dev and production). |
| `pydantic-settings` | Typed, validated settings from env vars and `.env` (incl. the production Mistral lock). |

Dev-only: `httpx2` (HTTP client required by Starlette's `TestClient`; Starlette deprecated plain `httpx` for it).

## Architecture rules

- **Rounds are a state machine:** `FORMING → R1_OPEN → R1_CLOSED → R2_OPEN → R2_CLOSED → R3_OPEN → R3_CLOSED → R4_EVALUATING → FINISHED → ARCHIVED`, plus `ABORTED`. Transitions run only in jobs, are idempotent and deterministic (safe to retry).
- **Anonymity is enforced server-side:** clients never receive raw submissions of other members, only LLM summaries of their room. The account ↔ submission mapping exists only in the backend (Supabase RLS denies direct client reads of submission tables).
- **LLM layer:** one module owns all provider calls. Each LLM task is a Pydantic AI `Agent` with an `output_type` Pydantic model; the model is built once from `LLM_MODEL` in the `llm` module and injected, so tests swap in `TestModel`/`FunctionModel`. No provider SDK is imported directly and no provider-specific code exists outside that factory. LLM requests go **directly to the provider API** with our own key; no intermediaries (no OpenRouter, no Pydantic AI Gateway, no Logfire or other LLM telemetry), since every extra recipient of submission text breaks EU processing and needs its own DPA. Prompts are versioned files; each stored summary/evaluation records its prompt version. Logs contain no plain-text personal data. Add retries and schema validation for every call.
- **Political opinions are GDPR Art. 9 data:** collect explicit consent, minimize stored text, support account and content deletion, keep processing in the EU.
- **i18n from day one:** no hard-coded user-facing strings in app or website. App and website start with **English** as the base language; more languages come later. LLM prompts take the room language as a parameter.

## Environment

- **Backend:** exactly one project-local virtual env at `backend/.venv`, managed by uv (`uv sync` inside `backend/`). Never install globally. Run tools via `uv run ...` or `.venv\Scripts\python.exe -m ...` (Windows) / `.venv/bin/python -m ...`.
- **App:** Flutter stable (3.47+). Dependencies only via `flutter pub add`. Public Supabase values reach the app through `--dart-define`, never the service role key.
- **Website:** Node 24 (CI) / ≥22.23, npm only (`package-lock.json` is committed).
- **Configuration and secrets:** root `.env` (template: `.env.example`, which lists every variable and its purpose). The backend will load it with `pydantic-settings`.

## First implementation steps (setup not done yet)

- Supabase: Supabase CLI is not installed. Run `npx supabase init` in the repo root to create `supabase/`, then `npx supabase start` for the local stack (needs Docker).
- Remaining backend runtime dependencies (procrastinate, `pydantic-ai-slim[mistral,google]` as the provider-agnostic LLM framework; the `google` extra only for the dev-only Gemini fallback) are not added yet; add them with `uv add` when the first code needs them.
- App: `app/` is the unmodified `flutter create` output (counter demo + its widget test). Replace it with the real app structure; set up `flutter_localizations`/ARB files for i18n.
- Website: `website/` is the Astro minimal starter. Build the landing page with i18n string files under `src/i18n/`.
- Screenshot pipeline (see `docs/testing.md` → App screenshots): add `alchemist` (dev) and fonts for goldens, `test_driver/integration_test.dart`, and fastlane for store uploads. Screens must take all data from Riverpod providers so demo states can be injected.
- GitHub Pages uses "GitHub Actions" as the source (enabled).

## Open decisions

- Android/iOS bundle id is `io.github.sphaerox.dicrates` (placeholder until a domain exists).
- See `docs/project-brief.md` for product-level open decisions.

---
Maintenance: update this file immediately whenever stack or architecture changes.
