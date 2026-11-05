# Dicrates

Dicrates turns debating into a game: up to six anonymous people discuss a current question in four asynchronous rounds, and an LLM summarizes, proposes a compromise and scores understanding rather than winning. Monorepo: Flutter app (`app/`), Python FastAPI backend + Procrastinate worker (`backend/`), Astro landing page on GitHub Pages (`website/`), Supabase (EU) for Postgres and Auth, Mistral as LLM via the provider-agnostic Pydantic AI framework (`LLM_MODEL`; Gemini as dev-only fallback).

## Top rules

1. **Test-driven development is mandatory.** Always write a failing test first (pytest / flutter_test / Vitest or Playwright), then the minimal code, then refactor (Red, Green, Refactor). No production code without a previously failing test. Bug fixes start with a test that reproduces the bug.
   - Never change, delete or weaken existing tests to get green. If a test fails, fix the implementation. If the test itself is wrong, explain why and get approval.
   - Repair budget: at most 3 attempts per failing test, then stop and report (which tests, what you tried, suspected cause).
   - Run the tests belonging to your change first (targeted commands in `docs/testing.md`); the full suite only for shared code.
2. **Keep docs current.** When stack, architecture, conventions, code style or testing change, update the matching file in `docs/` in the same step. A task is only done when `docs/` is correct.
3. **Environments.**
   - Python: always use the project-local `backend/.venv` via uv (`uv sync`, `uv run ...`, `uv add ...` inside `backend/`). Never install globally, never run Python outside the venv.
   - Flutter: add packages only with `flutter pub add`. Website: npm only.
4. **Privacy and anonymity are product features.** Clients never receive another member's raw submission, only LLM summaries. Never log submission text, transcripts or emails. Audio is never stored or uploaded.
5. **i18n:** no hard-coded user-facing strings in app or website. English is the base language.
6. **Screenshots are part of done:** a new app screen or visible UI change needs an updated screen golden (`app/screenshots/`). See `docs/testing.md` → App screenshots.

## Commands

```bash
# backend/  (Python 3.14, uv)
uv sync
uv run pytest
uv run pytest tests/test_x.py::test_y
uv run ruff check . && uv run ruff format --check . && uv run pyright
uv run ruff format .
uv run uvicorn dicrates.main:app --reload --app-dir src   # dev server

# app/  (Flutter)
flutter pub get
flutter test
flutter test test/x_test.dart --plain-name "name"
flutter analyze
dart format .

# website/  (Astro, npm)
npm ci
npm test
npm run test:e2e
npm run lint && npm run format:check && npm run check
npm run format
npm run build
```

## Documentation (load on demand)

Read only the files relevant to your current task:

- [docs/architecture.md](docs/architecture.md) – read before structural changes, new components or dependencies, DB/LLM/auth work. Stack, monorepo layout, state machine, privacy rules, environment.
- [docs/testing.md](docs/testing.md) – read before writing tests or changing test config. Suites, exact commands, which tests to run, definition of done.
- [docs/code-style.md](docs/code-style.md) – read before writing or formatting code. Formatters, linters, mandatory style rules.
- [docs/conventions.md](docs/conventions.md) – read when naming things, organizing files or committing. Domain terms, feature layout, Conventional Commits.
- [docs/project-brief.md](docs/project-brief.md) – read when goal, scope, game flow or non-goals are unclear. MVP scope and open decisions.
- [docs/concept-original.de.md](docs/concept-original.de.md) – full original product concept (German). Read only when the brief lacks detail.

## Roadmap

Work on roadmap tasks follows [Roadmap/AGENTS.md](Roadmap/AGENTS.md) (strict order, `RUN_` prefix, archive workflow). Open and running task files are in `Roadmap/Tasks/`, the cross-task memory and status in `Roadmap/README.md`.

## Boundaries

- Read secrets only from environment variables; never hard-code or commit them. `.env` is git-ignored; every new variable also goes into `.env.example` with a comment.
- The Supabase service role key is backend-only; the app gets only `SUPABASE_URL` and `SUPABASE_ANON_KEY` via `--dart-define`.
- Tests never call a real LLM API (Mistral, Gemini), Supabase cloud or FCM; use fakes. Real-LLM evaluations carry the `llm` pytest marker and run only on request.
- DB schema changes only via migrations in `supabase/migrations/`.
- Do not add new runtime dependencies without a one-line reason in `docs/architecture.md`.
- Do not decide open product questions (`docs/project-brief.md` → Open decisions) yourself; ask.
- Commit messages follow Conventional Commits with scope (`feat(app): ...`).
