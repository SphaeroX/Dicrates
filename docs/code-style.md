# Code Style and Formatting

> When to read: before writing, changing or formatting code.

## Tools

| Part | Formatter | Linter / types | Config (authoritative) |
|---|---|---|---|
| backend | `uv run ruff format .` | `uv run ruff check .`, `uv run pyright` (strict) | `backend/pyproject.toml` |
| app | `dart format .` | `flutter analyze` (flutter_lints) | `app/analysis_options.yaml` |
| website | `npm run format` (Prettier + astro plugin) | `npm run lint` (ESLint), `npm run check` (astro check) | `website/eslint.config.js`, `website/.prettierrc.json` |

Rules live in those config files and are not repeated here.

## Mandatory

- Python: full type annotations (pyright strict must pass). Pydantic models for every API payload and every LLM output.
- Dart: no `dynamic` in public APIs; immutable state classes for Riverpod state.
- TypeScript: strict mode (`astro/tsconfigs/strict`).
- No user-facing string literals in code: app strings go into ARB files, website strings into `website/src/i18n/` files.
- Accessibility: every interactive widget/element has a semantic label; respect system text scaling; meet WCAG 2.1 AA contrast.

## Recommended

- Keep functions small and pure where possible; side effects (DB, LLM, push) at the edges.
- Prefer explicit names over abbreviations in domain code (`submission`, not `sub`).

---
Maintenance: update this file immediately when style or tool rules change.
