# Tech Stack and Architecture

> When to read: before structural changes, new components, new dependencies, or anything touching data flow, privacy or the LLM layer.

## Monorepo layout

| Folder | Purpose |
|---|---|
| `app/` | Flutter mobile app (Android, iOS) |
| `backend/` | Python API (FastAPI) and job worker (Procrastinate) |
| `website/` | Astro landing page, deployed to GitHub Pages |
| `supabase/` | Supabase CLI config (`config.toml`) and SQL migrations (`migrations/`) |
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

- Code lives in `backend/src/dicrates/`. The backend is an installed (editable) package: `uv_build` backend with `module-name = "dicrates"`, so `uv sync` makes `dicrates` importable for pytest, pyright, uvicorn, the Procrastinate CLI and later console scripts (`dicrates-admin`). Version comes from `pyproject.toml` via `importlib.metadata`.
- `dicrates/main.py`: app factory `create_app()` and module-level `app`; `GET /health` returns `{"status": "ok", "version": ...}` (version in `dicrates/__init__.py`).
- `dicrates/core/settings.py`: `Settings` (pydantic-settings) reads env vars and the root `.env`; `LLM_MODEL` is parsed into `LlmModel(provider, model)`; `APP_ENV=production` refuses any non-`mistral:` model. Supabase/DB values are optional (`None`, empty strings count as unset) until the tasks that need them; secrets are `SecretStr`. Use `get_settings()` (cached) in app code.
- `dicrates/core/db.py`: `create_pool(conninfo)` returns an unopened psycopg `AsyncConnectionPool` (open with `async with`). Plain SQL, no ORM.
- `dicrates/jobs/`: Procrastinate `app` (`jobs/app.py`, `PsycopgConnector` on `DATABASE_URL`) and job definitions (`jobs/tasks.py`, example `ping`). Worker: `uv run procrastinate --app=dicrates.jobs.app.app worker` (in `backend/`). Jobs must be idempotent and take **only ids** as arguments: Procrastinate logs job arguments at INFO level, so no submission text, emails or other personal data may ever be a job argument.
- `dicrates/core/auth.py`: `TokenVerifier` checks Supabase access tokens (ES256 only, `aud=authenticated`, `iss=<SUPABASE_URL>/auth/v1`, `exp`/`sub` required) with a `PyJWKClient` on the project JWKS (cached 10 min, reloaded on unknown `kid`). `create_app` stores the verifier in `app.state` (503 without `SUPABASE_URL`); `get_current_user` / `CurrentUser` is the FastAPI dependency (401 + `WWW-Authenticate: Bearer`). Tokens and claims are never logged.
- `dicrates/profiles/`: `GET /me` (creates the profile on first call), `PATCH /me` (pseudonym, language), `POST /me/consent`; `ProfileRepository` protocol with `PostgresProfileRepository`. `require_consent` / `ConsentedUser` is the dependency **every game endpoint must use**: 403 `consent_required` unless the newest consent has the current `CURRENT_CONSENT_VERSION` (`profiles/consent.py`) and `age_confirmed`. Pseudonym rules: 3-24 chars, letters/digits of any script, single inner spaces, `-` and `_` (same rules in the app, `pseudonym_rules.dart`).
- `dicrates/main.py`: lifespan opens the DB pool when `DATABASE_URL` is set (`get_db_pool` dependency, 503 otherwise).
- `dicrates/llm/` (the only place that talks to LLM providers):
  - `factory.build_model(settings)` → `MistralModel` / `GoogleModel` with an explicit provider and key (`MISTRAL_API_KEY`, `GOOGLE_API_KEY` in `Settings`); unknown provider or missing key → `LlmConfigurationError`. Only this file may import provider code: enforced by ruff `TID251` (banned-api in `pyproject.toml`, also bans `logfire`) and by `tests/llm/test_isolation.py`.
  - `prompts`: files `llm/prompts/<name>.v<N>.md`, placeholders `$name` (`string.Template`, so JSON braces are safe), `default_registry().load(name, version=N).render(language=...)` → `RenderedPrompt(version="<name>.v<N>", text)`. A changed prompt is a new file with a higher version; never edit a released version.
  - `runner.LlmRunner(model, model_id=str(settings.llm_model), call_log=...)`. `run(task=, prompt=, output_type=, user_input=, room_id=)` builds a Pydantic AI `Agent` (prompt as `instructions`, `output_type` validated, `output_retries` default 2), retries transient provider errors (rate limit, 5xx, connection, timeout, overloaded) with exponential backoff (default 3 retries), and returns `LlmResult(output, prompt_version, model, input_tokens, output_tokens)`. Errors: `LlmOutputError` (output kept failing validation), `LlmUnavailableError`; messages never contain text.
  - `call_log`: every run (success or failure) writes one `LlmCallRecord` (task, prompt version, model, tokens, duration, success, error kind, attempts, room id) to `llm_calls`; **no text fields exist**. A failing log write is logged and never breaks the game step.
  - `pydantic-ai-slim` pulls in `logfire-api`, a no-op shim; Logfire is never configured, so nothing is sent.
- `dicrates/core/language.py`: `Language` enum (`en`, `de`) shared by profiles, questions and later rooms.
- `dicrates/questions/`: `QuestionContent` (language, format `scale|proposal|tradeoff`, text, options A/B only for `tradeoff`, fact box `facts[{text, source_ids}]` that must reference `sources[{id, url, title, outlet, published_on}]`, `topic_area`, origin `news|evergreen`, `prompt_version`) and `Question` (+ id, status, rejection reason, timestamps). `service.py` holds the operator actions (`approve`, `reject` with reason, `retire`, `edit` drafts only) and enforces `ensure_transition` (`draft → approved|rejected`, `approved → retired`). API: `GET /questions?language=&topic_area=` and `GET /questions/{id}` return only approved questions (`QuestionOut`, no status/prompt fields) and require `ConsentedUser`.
- `dicrates/admin/cli.py`: operator CLI `dicrates-admin` (typer, console script in `pyproject.toml`), see `docs/operations.md`. `make_app(questions_repository=...)` takes a repository factory so tests inject a fake; `run()` uses a selector event loop on Windows.
- Feature packages (`rooms`, `rounds`, ...) are added next to `core/` and `llm/` as they are built.

## Backend runtime dependencies

| Package | Reason |
|---|---|
| `fastapi` | HTTP API framework with Pydantic-typed request/response models. |
| `uvicorn` | ASGI server to run the FastAPI app (dev and production). |
| `pydantic-settings` | Typed, validated settings from env vars and `.env` (incl. the production Mistral lock). |
| `psycopg[binary,pool]` | Async Postgres driver with connection pool; plain SQL keeps queries explicit (RLS, locking) and it is the same driver Procrastinate uses, so job enqueueing can share a transaction with state changes. Chosen over an ORM. |
| `procrastinate` | Postgres-based job queue (see Tech stack). |
| `pydantic-ai-slim[mistral,google]` | Provider-agnostic LLM layer with typed structured output and test models (see LLM above); `google` extra only for the dev-only Gemini fallback. |
| `typer` | Typed CLI for `dicrates-admin` with a test runner; builds on click, type hints define options. |
| `pyjwt[crypto]` | JWT decoding and ES256 verification plus `PyJWKClient` (JWKS fetch, cache, refresh on unknown `kid`); small and standard, no Supabase SDK needed in the backend. |

Dev-only: `httpx2` (HTTP client required by Starlette's `TestClient`; Starlette deprecated plain `httpx` for it).

## App structure

- `app/lib/main.dart` starts `DicratesApp` (`lib/app.dart`, `MaterialApp.router`) inside a Riverpod `ProviderScope`. `DicratesApp` takes optional `themeMode` and `locale` (used by tests and screenshots; `null` locale follows the system).
- `lib/core/`: `config/app_config.dart` (`AppConfig` from `--dart-define`, `appConfigProvider`), `api/` (`ApiClient` over `package:http`, `apiClientProvider`), `router/app_router.dart` (`routerProvider`, go_router), `theme/app_theme.dart` (Material 3 light/dark from one seed color, bundled Roboto).
- `lib/features/<feature>/{data,providers,widgets}`: `home` (start screen with backend health, `backendHealthProvider`), `auth` (`AuthRepository` interface, `SupabaseAuthRepository`, login and code screens), `questions` (`Question` model, `QuestionCard` with fact box and source links, `linkOpenerProvider`, `topicAreaName`), `onboarding` (`Me`, `meProvider`, `ageConfirmationProvider`, age/under-age/consent/pseudonym screens), `splash` (loading and backend-unreachable state).
- **Auth flow:** email one-time code (`signInWithOtp` + `verifyOTP`, no magic link because there is no domain for universal links) and Google via `signInWithOAuth` with the deep link `io.github.sphaerox.dicrates://login-callback` (Android intent filter, iOS `CFBundleURLTypes`, Supabase `additional_redirect_urls`). Sign in with Apple is implemented but hidden behind `--dart-define=ENABLE_APPLE_SIGN_IN=true` (no Apple Developer account yet). `main.dart` initialises Supabase only when `SUPABASE_URL` and `SUPABASE_ANON_KEY` are defined; otherwise `UnconfiguredAuthRepository` shows a "not available" error.
- **Router gate** (`core/router/app_gate.dart`, `redirectFor` in `app_router.dart`): signed out → login; signed in → age confirmation → consent (versioned text `consentBodyV<n>`, sent with `age_confirmed: true`) → pseudonym → home. Under 18 and declined consent are dead ends with sign-out. The age answer is kept in memory only and stored by the backend together with the consent. The email address is never part of a route and never persisted by the app.
- `ApiClient` sends the Supabase access token as `Authorization: Bearer` and throws `ApiException(statusCode)` (`null` = network error).
- **i18n:** `flutter_localizations` + `intl`, ARB files `lib/l10n/app_en.arb` (template, with `@key` descriptions) and `app_de.arb`; `l10n.yaml` with `nullable-getter: false`. `AppLocalizations` is generated by `flutter pub get` into `lib/l10n/` and git-ignored. Supported locales are listed English-first (`supportedAppLocales` in `app.dart`) so unsupported system locales fall back to English.
- **Fonts:** Roboto (regular/medium/bold, Apache 2.0, copied from the Flutter SDK's `material_fonts`) is bundled in `app/assets/fonts/` so devices and goldens render the same text.
- **Config (`--dart-define`):** `API_BASE_URL` (default `http://127.0.0.1:8000`; Android emulator: `http://10.0.2.2:8000`), `SUPABASE_URL`, `SUPABASE_ANON_KEY` (public values only). Run: `flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000`. Debug Android builds allow cleartext HTTP (`src/debug/AndroidManifest.xml`); iOS allows local networking only (`NSAllowsLocalNetworking`).

## App dependencies

| Package | Reason |
|---|---|
| `flutter_riverpod` | State management; providers are overridable in tests and screenshots. |
| `flutter_localizations`, `intl` | Generated, type-safe localizations from ARB files (en, de). |
| `go_router` | Declarative routing with deep-link support (invite links in Task 09). |
| `http` | Small, well-supported HTTP client with a built-in `MockClient` for tests; no interceptors needed yet (chosen over `dio`). |
| `url_launcher` | Opens fact-box source links in the external browser. |
| `supabase_flutter` | Supabase Auth client (email OTP, OAuth deep links, session persistence and token refresh); the app uses Supabase only for auth, all game data goes through the backend. |

Dev-only: `mocktail`, `alchemist` (golden screenshots).

## Database and Supabase

- Supabase CLI runs via `npx supabase ...` (no global install). Local stack: `npx supabase start` in the repo root (needs Docker); it applies all files in `supabase/migrations/`. `npx supabase db reset` re-applies them from scratch. Local Postgres: `postgresql://postgres:postgres@127.0.0.1:54322/postgres` (default ports from `supabase/config.toml`).
- Migrations: `supabase/migrations/<timestamp>_<name>.sql`. `..._procrastinate_schema.sql` is generated by `uv run procrastinate schema --read` (procrastinate 3.10.0); Procrastinate upgrades ship migration SQL that goes in as new migrations.
- **Everything in `public` is reachable through the Supabase Data API**, so every new table gets RLS enabled and explicit `REVOKE`/`GRANT` for `anon` and `authenticated`; functions in `public` get `REVOKE ALL ... FROM PUBLIC, anon, authenticated` unless clients must call them. The Procrastinate tables and functions are locked down this way.
- `profiles`: one row per `auth.users` id (`pseudonym`, `language` `en`/`de`, `created_at`); clients may only `SELECT` their own row, all writes go through the backend.
- The backend connects as the database owner (`postgres`) and therefore bypasses RLS; access control for game data is enforced in backend code.
- `llm_calls`: usage log without any text (see LLM layer); backend-only. `room_id` gets its foreign key once `rooms` exists.
- `topic_areas` (seeded slugs) and `questions` (fact box and sources as `jsonb`, validated by the backend models; check constraints for enums, tradeoff options and rejection reason): backend-only.
- `consents`: append-only (`user_id`, `consent_version`, `age_confirmed`, `granted_at`), newest row counts; backend-only (RLS on, no grants). Profiles and consents are deleted with the auth user (`ON DELETE CASCADE`).
- **Local Auth** (`supabase/config.toml`): tokens are signed with an ES256 key from `supabase/signing_keys.json` (git-ignored; create once with `echo '[]' > supabase/signing_keys.json && npx supabase gen signing-key --algorithm ES256`), so local tokens are verified via JWKS exactly like in the cloud. Email sign-in sends a 6-digit code (template `supabase/templates/sign_in_code.html`, en + de); local mails land in Mailpit (http://127.0.0.1:54324). Google is prepared in `[auth.external.google]` but `enabled = false` until OAuth client data exists in `.env`. The cloud project needs the same settings in the dashboard (Task 17).

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

- Website: `website/` is the Astro minimal starter. Build the landing page with i18n string files under `src/i18n/`.
- Store screenshot pipeline (see `docs/testing.md` → App screenshots): `test_driver/integration_test.dart` and fastlane for store uploads are still missing (Task 26). Screens must take all data from Riverpod providers so demo states can be injected.
- GitHub Pages uses "GitHub Actions" as the source (enabled).

## Open decisions

- Android/iOS bundle id is `io.github.sphaerox.dicrates` (placeholder until a domain exists).
- See `docs/project-brief.md` for product-level open decisions.

---
Maintenance: update this file immediately whenever stack or architecture changes.
