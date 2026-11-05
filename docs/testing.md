# Testing Strategy

> When to read: before writing tests or changing test configuration.

## Test suites

| Part | Suite | Why |
|---|---|---|
| `backend/` | **pytest** + pytest-asyncio + pytest-cov | Python standard, fast single-test runs, fixtures fit async FastAPI and DB tests. |
| `app/` | **flutter_test** + **mocktail**, `integration_test` | Built into Flutter; mocktail needs no code generation; Riverpod providers can be overridden in tests. |
| `website/` | **Vitest** (unit) + **Playwright** (E2E) | Vitest shares Astro's Vite config; Playwright checks the built static site on desktop and mobile. |

## TDD cycle (mandatory)

1. Red: write a test, run it, confirm it fails for the expected reason.
2. Green: write the minimal code until it passes.
3. Refactor: clean up, tests stay green.

## Commands

```bash
# backend (run inside backend/)
uv run pytest                                   # all tests
uv run pytest tests/test_rounds.py              # one file
uv run pytest tests/test_rounds.py::test_name   # one test
uv run pytest -m "not integration and not llm"  # fast unit tests only
uv run pytest --cov=src                         # coverage

uv run uvicorn dicrates.main:app --reload                  # local dev server, http://127.0.0.1:8000/health
uv run pytest -m integration                    # needs `npx supabase start` (repo root, Docker)
uv run procrastinate --app=dicrates.jobs.app.app worker    # job worker (needs DATABASE_URL)

# app (run inside app/)
flutter test                                    # all unit + widget tests
flutter test test/some_test.dart                # one file
flutter test --plain-name "test name"           # one test by name
flutter test integration_test                   # on a device/emulator

# website (run inside website/)
npm test                                        # Vitest, all unit tests
npx vitest run tests/unit/foo.test.ts           # one file
npm run test:watch                              # watch mode
npm run test:e2e                                # Playwright (builds + previews)
npx playwright test tests/e2e/home.spec.ts      # one E2E file
```

## Which tests to run

- Change in `backend/` → backend tests of the touched module; full backend suite when changing shared code (models, LLM layer, state machine, settings).
- Change in `app/lib/` → matching tests in `app/test/`; full app suite when changing shared providers, theme or l10n.
- Change in `website/` → Vitest for changed logic, Playwright when pages/layout/i18n change.
- API contract changes → backend tests **and** app tests that consume the contract.

## Definition of done

A task is done when, for every touched part:

1. Tests pass: `uv run pytest` / `flutter test` / `npm test` (+ `npm run test:e2e` for page changes).
2. Static checks pass:
   - backend: `uv run ruff check .`, `uv run ruff format --check .`, `uv run pyright`
   - app: `flutter analyze`, `dart format --output=none --set-exit-if-changed .`
   - website: `npm run lint`, `npm run format:check`, `npm run check`
3. No existing test was changed, deleted or weakened (unless explicitly requested).

## Hard rules

- A failing test means fixing the implementation, not the test.
- At most 3 repair attempts per failing test; then stop and report.
- If an existing test must change, state why and wait for approval.
- Tests never call a real LLM (Mistral or Gemini), Supabase cloud or FCM. Use Pydantic AI `TestModel`/`FunctionModel` (with `models.ALLOW_MODEL_REQUESTS = False` in `conftest.py`) and fakes behind the other provider interfaces. Settings tests cover `LLM_MODEL` parsing and that non-`mistral:` models are refused when `APP_ENV=production`. Real-LLM checks (prompt/bias evaluation) carry the `llm` marker and run only on request.

## App screenshots (mockups, repo preview, store listings)

Every app screen must be reproducible as a screenshot without manual clicking. Two layers:

1. **Screen goldens (repo preview / mockups):** golden tests (package `alchemist`, real fonts loaded) render each screen with fake Riverpod providers in fixed states (empty, filled, error), light and dark, phone and tablet sizes. Run without an emulator, so they work in CI.
   - Tests in `app/test/screenshots/`, output PNGs in `app/screenshots/` (committed, shown in the README gallery).
   - Update: `flutter test --update-goldens test/screenshots` · verify: `flutter test test/screenshots`.
   - **Platform strategy** (`app/test/flutter_test_config.dart`): font rendering differs per OS, so alchemist *platform goldens* (real text) are rendered only on **Windows** (main dev machine) and written to `app/screenshots/<name>.png`; they are skipped on other OSes and whenever `CI` is set. alchemist *CI goldens* (text as blocks, no shadows, platform independent) live in `app/test/screenshots/goldens/ci/` and are verified everywhere, including the Linux CI (`.github/workflows/app.yml`). Always regenerate both on Windows with `--update-goldens` and commit both.
   - Golden variants: each screen state in light/dark × phone (390×844) / tablet (834×1194), see `test/screenshots/screen_sizes.dart`. Name files `<screen>_<state>_<theme>_<size>`.
   - `test/helpers/pump_app.dart` → `buildTestApp(...)` builds the full app with fake providers; use it for widget tests and goldens.
   - A new screen or a visible UI change is only done when its golden exists/is updated.
2. **Store screenshots:** an `integration_test` flow (`app/integration_test/store_screenshots_test.dart`) with seeded demo data takes screenshots via `IntegrationTestWidgetsFlutterBinding.takeScreenshot` on the store device sizes; run with `flutter drive --driver=test_driver/integration_test.dart --target=integration_test/store_screenshots_test.dart`. Output goes to the fastlane metadata folders (`app/android/fastlane/metadata/android/<locale>/images/`, `app/ios/fastlane/screenshots/<locale>/`) per locale, so new languages get screenshots automatically. Upload with fastlane `supply` / `deliver` (later CI job).

Screenshots use invented demo content only and the in-app locale under test.

## Test structure

- **Backend integration tests:** marker `integration`, run against the local Supabase stack (`npx supabase start`, needs Docker). Fixtures in `backend/tests/conftest.py`: `database_url` (default local stack, override with `TEST_DATABASE_URL`) and `db_connection` (one transaction per test, rolled back afterwards). Without a reachable database, integration tests are **skipped** locally; with `DICRATES_REQUIRE_DB=1` (set in CI) they fail instead. RLS tests switch role inside the transaction (`set_config('request.jwt.claims', ...)` + `SET LOCAL ROLE authenticated|anon`). Job unit tests use `procrastinate.testing.InMemoryConnector` via `app.replace_connector(...)` and `app.run_worker_async(wait=False)`. On Windows, `conftest.py` makes pytest-asyncio use a `SelectorEventLoop` (psycopg async does not work on the Proactor loop). CI job `integration` in `backend.yml` starts Supabase with `supabase/setup-cli`, runs `pytest -m integration` and smoke-tests the worker command.
- **Backend auth tests:** `tests/auth_helpers.py` creates ES256 test key pairs (`SigningKey(kid=...).token(...)`) and a `FakeJwksClient` (in-memory JWKS, counts fetches). Endpoint tests override `get_token_verifier` and `get_profile_repository` via `app.dependency_overrides` and use `tests/profiles/fakes.py` (`FakeProfileRepository`). `tests/test_auth_e2e.py` (integration) signs in with a real email OTP against the local stack (code read from Mailpit) and calls `/me`; it needs `TEST_SUPABASE_ANON_KEY` (`npx supabase status -o json`), is skipped locally without it and required in CI. pytest has `pythonpath = ["."]` so tests can import `tests.*` helpers.
- **Backend:** `backend/tests/` mirrors `backend/src/dicrates/` (e.g. `tests/core/test_settings.py`); files `test_<module>.py`, functions `test_<behavior>`. pytest uses `--import-mode=importlib`, so test folders need no `__init__.py` and equal basenames in different folders are fine. Settings tests set env vars via `monkeypatch` and construct `Settings(_env_file=None)`, never reading the real `.env`. CI: `.github/workflows/backend.yml` runs ruff, pyright and `pytest -m "not integration and not llm"` on changes under `backend/**`. DB tests carry the `integration` marker and use a local Supabase/Postgres. LLM tests use recorded, validated JSON fixtures.
- **App:** `app/test/` mirrors `app/lib/`; files `<name>_test.dart`. `test/core/l10n/arb_completeness_test.dart` fails if any ARB file lacks a key of `app_en.arb`. Locale tests set `tester.platformDispatcher.localesTestValue`; text-scaling tests set `textScaleFactorTestValue`. `test/helpers/fake_auth_repository.dart` (valid code `123456`) and `test/helpers/fake_backend.dart` (in-memory `/health`, `/me`, `/me/consent` behind a `MockClient`) back `buildTestApp(auth:, backend:)`, which defaults to a signed-in, onboarded user. Single screens without the router: `test/helpers/screen_app.dart` → `buildScreenApp(screen, overrides:)`. CI: `.github/workflows/app.yml` (format check, analyze, `flutter test`). Widget tests override Riverpod providers instead of mocking globals. Integration tests in `app/integration_test/` only for core flows.
- **Website:** unit tests `website/tests/unit/*.test.ts`, E2E `website/tests/e2e/*.spec.ts`. E2E checks include basic accessibility (headings, alt text, lang attribute).
- **Privacy in tests:** fixtures use invented opinions only; never real user data.

---
Maintenance: update this file immediately when test suites or strategy change.
