# Task_06: Fragenbibliothek + Admin-CLI

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_06.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M2 Streitfragen

## Ziel

Streitfragen leben in einer Bibliothek mit Status-Workflow (Entwurf → freigegeben/abgelehnt → zurückgezogen). Der Betreiber prüft und gibt sie über das CLI `dicrates-admin` frei, die API liefert nur freigegebene Fragen aus, und die App kann eine Frage mit Faktenkasten und Quellen barrierearm darstellen. Die Pipelines in Task 07 und 08 schreiben in diese Bibliothek.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Tasks 02 (DB, Migrationen), 04 (`require_consent`) und 05 (LLM-Schicht, für spätere Pipelines; hier nur Felder wie `prompt_version`) archiviert.
- **Relevantes Vorwissen:** `docs/concept-original.de.md` Kapitel 8 (Fragenformate Dafür/Dagegen mit 5er-Skala, Vorschlagsfrage, Abwägung A vs. B; Faktenkasten mit Quellen), `docs/conventions.md` (Domänenbegriff `question`), Produktentscheidung: Freigabe per CLI, Fragen in `en` und `de`.

## Umfang

**Gehört dazu:**

- Migration `topic_areas` (Seed: z. B. Politik, Wirtschaft, Gesellschaft, Umwelt, Technik, Sport, Kultur, Bildung, Gesundheit; Namen über i18n-Schlüssel) und `questions`: Sprache, Format (`scale`, `proposal`, `tradeoff`), Fragetext, Optionen A/B bei `tradeoff`, Faktenkasten (strukturierte Liste von Fakten mit Quellenbezug), Quellen (URL, Titel, Medium, Datum), Themengebiet, Herkunft (`news`, `evergreen`), Status (`draft`, `approved`, `rejected`, `retired`), Ablehnungsgrund, `prompt_version`, Zeitstempel. RLS: Clients haben keinen direkten Zugriff.
- Pydantic-Modelle mit Validierung (jeder Fakt verweist auf eine vorhandene Quelle).
- API `GET /questions?language=&topic_area=` (nur `approved`, `require_consent`) und `GET /questions/{id}`.
- CLI `dicrates-admin` (Bibliothek wählen, z. B. `typer`, und begründen; Einstieg über `[project.scripts]` bzw. `uv run`): `questions list --status`, `questions show <id>`, `questions approve <id>`, `questions reject <id> --reason`, `questions retire <id>`, `questions edit <id>` (Text/Faktenkasten korrigieren vor Freigabe).
- App: wiederverwendbares Widget „Fragekarte mit Faktenkasten und Quellen" (Quellen als Links, Screenreader-Labels) inkl. Goldens; noch kein eigener Screen.

**Gehört nicht dazu:**

- Erzeugung von Fragen (Tasks 07 und 08), Auswahl beim Raum-Anlegen (Task 09), Meldungen zu Fragen (Task 20).

## Umsetzungsschritte

1. Rote Tests für Modelle und Validierung schreiben, dann Migrationen und Modelle.
2. Repository/Service für Fragen per TDD (Statusübergänge nur erlaubt: `draft → approved|rejected`, `approved → retired`).
3. API-Endpunkte per TDD.
4. CLI per TDD (CLI-Runner der gewählten Bibliothek).
5. App-Widget mit Widget-Tests und Goldens (alle drei Formate).
6. Doku: CLI-Nutzung in `docs/` (z. B. neuer Abschnitt in `docs/architecture.md` oder `docs/operations.md`, falls angelegt).

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`backend/tests/`, `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Validierung: Fakt ohne gültigen Quellenbezug wird abgelehnt; `tradeoff` ohne Optionen wird abgelehnt.
- Statusübergänge: erlaubte und verbotene Übergänge.
- API: nur `approved` in der gewünschten Sprache; ohne Einwilligung 403.
- CLI: `approve`, `reject` mit Grund, `retire` (Integration).
- App: Fragekarte in allen drei Formaten, Quellenlinks haben Semantik-Labels; Goldens.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [x] Alle Tests grün, Definition of Done für Backend und App erfüllt.
- [x] `uv run dicrates-admin questions list --status draft` funktioniert gegen den lokalen Stack (belegt durch `tests/admin/test_cli_integration.py` im CI-Job `integration` gegen den Supabase-Stack; lokal mangels Docker nicht ausgeführt).
- [x] Ein direkter Client-Zugriff auf `questions` über die Supabase-API ist durch RLS gesperrt (Integrationstest).
- [x] Goldens der Fragekarte liegen in `app/screenshots/`.

## Offene Fragen / Annahmen

- Annahme: Alle drei Fragenformate kommen ins MVP. Falls `tradeoff` den Spielablauf unnötig verkompliziert, mit dem Nutzer klären und hier vermerken.
- Annahme: Themengebiete sind fest per Seed; sie werden im MVP nur zum Filtern beim Raum-Anlegen genutzt.

## Notizen zu diesem Task

Taskspezifische Informationen während der Arbeit hier festhalten. Taskübergreifendes gehört in `Roadmap/README.md`.

- Annahme bestätigt umgesetzt: alle drei Formate (`scale`, `proposal`, `tradeoff`) im MVP; Themengebiete fest per Seed.
- Zusätzlich zum Plan: `questions import <datei.json>` (Entwurf von Hand anlegen), damit der Betreiber kuratierte Fragen einpflegen kann und der CLI-Integrationstest ohne Pipeline auskommt.

## Abschluss-Checkliste

Reihenfolge und Details stehen in `AGENTS.md`, Abschnitt "Abschluss- und Archivierungs-Workflow".

- [x] Alle Akzeptanzkriterien erfüllt, Tests liegen permanent in den Test-Suites der Teile und laufen grün
- [x] Definition of Done aus `docs/testing.md` erfüllt und betroffene Dateien in `docs/` aktualisiert
- [x] Abschnitt "Erkenntnisse für Folge-Agenten" unten ausgefüllt
- [x] Folge-Tasks und `Roadmap/README.md` geprüft und bei Bedarf angepasst
- [x] Datei ohne `RUN_` nach `Roadmap/Archiv/` verschoben

## Erkenntnisse für Folge-Agenten

Vor der Archivierung vom Agenten auszufüllen. Schreibe so, dass ein Agent, der diesen Task nie gesehen hat, davon bei späteren Tasks profitiert:

- **Umgesetzt (und Abweichungen vom Plan):** Backend-Paket `questions` (Modelle, Repository, Service, Routen), `core/language.py`, Migration `topic_areas` + `questions`, CLI `dicrates-admin` (`admin/cli.py`, typer) mit `list/show/approve/reject/retire/edit/import`, Doku `docs/operations.md` mit Prüf-Checkliste. App: `features/questions` mit `QuestionCard` (Themen-Chip, Formathinweis, Optionen A/B, Faktenkasten mit Quellennummern, Quellenlinks mit Semantik-Label), `url_launcher`, 12 neue Goldens.
- **Learnings & Stolpersteine:** pydantic `model_copy(update=...)` validiert nicht – verschachtelte Modelle werden dann zu dicts (im Fake aufgefallen); `model_validate` verwenden. ruff S608 meldet auch konstante String-Verkettungen in SQL – Spaltenlisten über `psycopg.sql.SQL(...).format(columns=...)` einsetzen. Bash-Heredocs mit `'` im Inhalt scheitern im Agent-Tool sporadisch – Dateien mit dem Write-Tool anlegen. Typer-App mit injizierbarer Repository-Factory (`make_app`) macht das CLI ohne DB testbar. `asyncio.run(..., loop_factory=...)` (Python 3.14) löst das Windows-Selector-Loop-Problem für CLI-Befehle.
- **Wichtige Entscheidungen und ihre Gründe:** Faktenkasten und Quellen als `jsonb` in `questions` (immer zusammen gelesen, Validierung in Pydantic) statt eigener Tabellen. Statusregeln im Service (`ensure_transition`) plus DB-Check für Ablehnungsgrund/Optionen. API gibt nur `approved` aus und blendet Status/Prompt-Version aus. Themennamen nur als i18n-Schlüssel (`topicArea_<slug>`), unbekannte Slugs → „Sonstiges".
- **Auswirkungen auf Folge-Tasks:** Tasks 07/08 erzeugen `QuestionContent` (mit `prompt_version` und `origin`) und speichern per `QuestionRepository.create` als Entwurf; Freigabe per `dicrates-admin`. Task 09 nutzt `GET /questions` beim Raum-Anlegen und `QuestionCard` in der App (`FakeBackend` um `/questions` erweitern). Neue Operator-Befehle als weitere Typer-Unter-App in `admin/cli.py` (Task 20) und in `docs/operations.md` dokumentieren. Neue Themengebiete brauchen Migration + ARB-Schlüssel.
- **Hinweise zu Tests und Befehlen:** Backend `uv run pytest` (127 Unit), `-m integration` (Repository, RLS, CLI gegen DB). App `flutter test` (142 inkl. Goldens). Demo-Fragen: Backend `tests/questions/factories.py`, App `test/helpers/demo_questions.dart`.
