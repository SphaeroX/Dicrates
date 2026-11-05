# Naming Conventions and Practices

> When to read: when naming things, organizing files, committing, or adding new components.

## Naming

- **Python:** modules and functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- **Dart:** files `snake_case.dart`, classes `PascalCase`, members `lowerCamelCase`, providers end in `Provider` (`roomProvider`).
- **TypeScript/Astro:** components `PascalCase.astro`, other files `kebab-case.ts`.
- **Database:** tables and columns `snake_case`, plural table names (`rooms`, `submissions`).
- **Env vars:** `SCREAMING_SNAKE_CASE`, provider-standard names.
- **Domain terms** (use consistently in code, API and UI keys): `room`, `question`, `round`, `submission`, `summary` (types: `group_picture`, `movement`, `evaluation`), `feedback`, `evaluation`, `rating`, `trust_score`, `invite_code`.
- **Tests:** see `docs/testing.md`.

## Organization

- Backend is organized **by feature** (`rooms`, `rounds`, `questions`, `llm`, `moderation`, `scoring`), each with its own models, service and routes. Shared infrastructure (settings, db, auth) lives in a `core` package.
- App is organized **by feature** under `lib/features/<feature>/` (data, providers, widgets); shared code under `lib/core/`.
- LLM prompts are versioned files next to the `llm` feature (e.g. `group_picture.v1.*`), never inline strings.
- DB schema changes only through SQL migrations in `supabase/migrations/`.

## Project-specific practices

- Never send another member's raw submission to a client; only summaries.
- Never log submission text, transcripts or emails in plain text.
- Read secrets only from environment variables; never hard-code them. Every new variable also goes into `.env.example` with a comment.
- New runtime dependencies need a one-line reason in `docs/architecture.md`.

## Git

- Commit messages: **Conventional Commits** (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`, `ci:`), optional scope `app`, `backend`, `website`, `supabase`, e.g. `feat(backend): add round state machine`.
- Default branch `main`; feature branches `feat/<short-name>`, `fix/<short-name>`.

---
Maintenance: update this file immediately when conventions change or new components are added.
