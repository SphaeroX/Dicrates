# Operations (operator CLI)

> When to read: before reviewing or releasing questions, or when adding operator commands.

In the MVP all operator work (question approval, later reports and moderation) runs through the backend CLI `dicrates-admin`; there is no web admin. It works against the database in `DATABASE_URL` (root `.env`), so point it at the local stack or, carefully, at staging/production.

```bash
# backend/
uv run dicrates-admin --help
uv run dicrates-admin questions list --status draft      # draft | approved | rejected | retired
uv run dicrates-admin questions show <id>                # full JSON with fact box and sources
uv run dicrates-admin questions approve <id>             # draft -> approved (offered to rooms)
uv run dicrates-admin questions reject <id> --reason "Leading wording"
uv run dicrates-admin questions retire <id>              # approved -> retired (no new rooms)
uv run dicrates-admin questions edit <id> --text "..." [--option-a ... --option-b ...]
uv run dicrates-admin questions edit <id> --content-file fix.json   # replace e.g. facts and sources
uv run dicrates-admin questions import question.json     # create a draft by hand
uv run dicrates-admin questions generate --from-news --limit 3   # fetch feeds, draft questions now
```

`questions list` marks drafts whose sources all come from one outlet with `[single source]`; check those extra carefully.

## News pipeline

- **Sources:** `backend/config/news_sources.toml` (approved 2026-11-05): tagesschau.de, Deutschlandfunk, DER SPIEGEL, Süddeutsche Zeitung, Frankfurter Allgemeine, WELT, taz, Neue Zürcher Zeitung, BBC News, The Guardian, DW, POLITICO Europe, The Telegraph. Edit the file to add or remove outlets; keep the political spectrum balanced (`leaning`). Feed terms must be confirmed before the public release (`terms_note`). As of 2026-11-05 the Telegraph feed refuses automated requests (skipped and logged).
- **Schedule:** the worker runs `news_questions` every 6 hours (needs the worker running, see `docs/testing.md`), at most 3 new questions per run. Nothing is published without `questions approve`.
- **Flow:** feeds → `news_items` (7 days) → LLM topic candidates → bilingual draft with fact box (facts cite only the stored feed entries) → automatic neutrality/safety check (one revision allowed) → `draft` or `rejected` ("Automatic check: ...").
- **Cost per run** (measured 2026-11-05 with `gemini-3.1-flash-lite`, 3 questions): 7 LLM calls, about 14,000 input and 1,100 output tokens. Check real numbers with `SELECT task, count(*), sum(input_tokens), sum(output_tokens) FROM llm_calls WHERE created_at > now() - interval '1 day' GROUP BY task;`.

## Question review checklist

Approve only when all hold; otherwise edit the draft or reject it with a reason:

1. **Concrete and controversial:** one can be for or against it (or propose something concrete); no vague "Is it good that ..." questions.
2. **Neutral wording:** no loaded or suggestive terms, no implied answer, both sides recognisable.
3. **Facts are sourced:** every fact in the box points to a listed source that actually says so; open the links.
4. **Format fits:** `scale` (for/against), `proposal` (how should X be done?), `tradeoff` (A or B, both options filled and comparable).
5. **Language and topic area** are right; nothing that calls for violence or targets groups.

Status rules (enforced by the backend): `draft → approved | rejected`, `approved → retired`; only drafts can be edited; a rejection needs a reason.

## JSON format (import and `--content-file`)

```json
{
  "language": "en",
  "format": "scale",
  "text": "Should the town of Exampleville introduce a car-free market square?",
  "option_a": null,
  "option_b": null,
  "facts": [{"text": "The square is crossed by about 4,000 cars per day.", "source_ids": [1]}],
  "sources": [{"id": 1, "url": "https://example.test/report", "title": "Traffic report", "outlet": "Gazette", "published_on": "2026-10-01"}],
  "topic_area": "society",
  "origin": "evergreen",
  "prompt_version": null
}
```

Topic areas: `politics`, `economy`, `society`, `environment`, `technology`, `sports`, `culture`, `education`, `health` (seeded by migration; display names in the app ARB files `topicArea_<slug>`).

---
Maintenance: update this file whenever operator commands or review rules change.
