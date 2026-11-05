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
- Tests never call the real LLM, Supabase cloud or FCM. Use fakes behind the provider interfaces. Real-LLM checks (prompt/bias evaluation) carry the `llm` marker and run only on request.

## Test structure

- **Backend:** `backend/tests/` mirrors `backend/src/`; files `test_<module>.py`, functions `test_<behavior>`. DB tests carry the `integration` marker and use a local Supabase/Postgres. LLM tests use recorded, validated JSON fixtures.
- **App:** `app/test/` mirrors `app/lib/`; files `<name>_test.dart`. Widget tests override Riverpod providers instead of mocking globals. Integration tests in `app/integration_test/` only for core flows.
- **Website:** unit tests `website/tests/unit/*.test.ts`, E2E `website/tests/e2e/*.spec.ts`. E2E checks include basic accessibility (headings, alt text, lang attribute).
- **Privacy in tests:** fixtures use invented opinions only; never real user data.

---
Maintenance: update this file immediately when test suites or strategy change.
