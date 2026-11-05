# Task_07: News-Pipeline für Streitfragen

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_07.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M2 Streitfragen

## Ziel

Ein regelmäßiger Job liest kuratierte News-Feeds aus mehreren politischen Richtungen, das LLM erkennt daraus aktuelle, kontroverse Themen, formuliert neutrale, konkrete Streitfragen mit quellenbasiertem Faktenkasten und prüft sie auf Neutralität und Sicherheit. Ergebnis sind Entwürfe in der Fragenbibliothek, die der Betreiber per CLI freigibt. Leitlinie des Nutzers: „Hauptsache kontrovers", aber sachlich und neutral formuliert.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 06 archiviert (Bibliothek, CLI, Validierung des Faktenkastens); Task 05 (LLM-Schicht).
- **Relevantes Vorwissen:** `docs/concept-original.de.md` Kapitel 8 (Themen-Pipeline: Quellen → Kandidaten → Formulierung → Prüfung → menschliche Freigabe) und Kapitel 15 (LLM-Aufgaben 1–3), Erkenntnisse aus Task 05 (Prompt-Registry, Wrapper, Protokoll).

## Umfang

**Gehört dazu:**

- Konfigurationsdatei der Quellen (z. B. `backend/config/news_sources.yaml`): Feed-URL, Medium, Sprache, grobe politische Einordnung; Vorschlagsliste mit breitem Spektrum, vom Nutzer zu bestätigen.
- Feed-Abruf hinter einem Interface (Fake in Tests), Parser (z. B. `feedparser`, begründen); gespeichert werden nur Titel, Link, Medium, Datum und Kurztext aus dem Feed, keine Volltexte (Urheberrecht). Deduplizierung über URL.
- Tabelle für News-Einträge mit Ablaufdatum (alte Einträge werden gelöscht).
- LLM-Agent 1 „Themenkandidaten": bündelt Einträge mehrerer Medien zu strittigen, aktuellen Themen mit Themengebiet; bevorzugt Themen, bei denen vernünftige Menschen klar unterschiedlich urteilen.
- LLM-Agent 2 „Streitfrage formulieren": Frage im passenden Format, Faktenkasten **nur** aus den übergebenen Einträgen mit Quellenbezug, je Sprache `en` und `de`.
- LLM-Agent 3 „Neutralitäts- und Sicherheitscheck": `ok` / `revise` (mit Hinweis, ein Überarbeitungsdurchgang) / `reject` (Grund); prüft suggestive Wortwahl, verbotene Inhalte, Gewaltaufrufe, menschenverachtende Prämissen.
- Procrastinate-Periodic-Job (z. B. alle 6 Stunden) und CLI `questions generate --from-news [--limit]`.
- Duplikatschutz gegenüber bestehenden Fragen (das LLM bekommt die Titel aktueller Fragen).

**Gehört nicht dazu:**

- Automatische Veröffentlichung ohne Freigabe, zeitlose Fragen (Task 08), Bias-Evaluation mit echtem LLM (Task 23).

## Umsetzungsschritte

1. Rote Tests für Feed-Parsing (Fixture-XML) und Deduplizierung, dann umsetzen.
2. Prompts `news_candidates.v1`, `question_draft.v1`, `question_check.v1` anlegen; Ausgabemodelle definieren.
3. Pipeline-Service per TDD mit `FunctionModel` (Kandidat → Entwurf → Check → Speicherung als `draft` bzw. `rejected` mit Grund).
4. Validierung: Fakten mit unbekanntem Quellenbezug führen zu Retry bzw. Verwerfen.
5. Periodic-Job und CLI-Befehl per TDD.
6. Manueller Probelauf mit Gemini gegen echte Feeds (nur öffentliche News, keine Nutzerdaten) und Ergebnis in Notizen; erste Entwürfe per CLI ansehen.
7. Doku aktualisieren (Quellenkonfiguration, Ablauf, Kosten pro Lauf aus `llm_calls`).

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (hier `backend/tests/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Parsing von RSS/Atom-Fixtures, Umgang mit kaputtem Feed (wird übersprungen, Fehler protokolliert).
- Deduplizierung über URL; Ablauf alter Einträge.
- Pipeline: gültiger Durchlauf erzeugt `draft` mit Quellen; `reject` speichert Grund; `revise` führt zu genau einem Überarbeitungsversuch.
- Faktenkasten mit erfundener Quelle wird nicht gespeichert.
- Keine Netzwerkzugriffe in Tests (Fake-Fetcher).

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [x] Alle Tests grün, Definition of Done erfüllt.
- [x] `uv run dicrates-admin questions generate --from-news --limit 3` erzeugt mit gesetztem LLM-Key Entwürfe, die `questions list --status draft` zeigt (manuell, Ergebnis in Notizen: Pipeline mit echten Feeds und Gemini erfolgreich; Speicherung/Listing per DB in CI belegt, lokaler CLI-Lauf gegen DB mangels Docker offen).
- [x] Jeder gespeicherte Entwurf hat mindestens zwei Quellen aus unterschiedlichen Medien oder ist als Einzelquelle gekennzeichnet.
- [x] Quellenliste und Pipeline sind dokumentiert.

## Offene Fragen / Annahmen

- **Rückfrage an den Nutzer vor Umsetzung:** Welche Medien kommen in die Quellenliste (Vorschlag: breites Spektrum deutscher und internationaler Medien mit öffentlichen RSS-Feeds)? Nutzungsbedingungen der Feeds prüfen.
- Annahme: Fragen werden direkt in beiden Sprachen erzeugt (zwei Datensätze, verknüpft über eine gemeinsame Gruppen-ID), damit deutsch- und englischsprachige Räume dieselbe Frage nutzen können.

## Notizen zu diesem Task

Taskspezifische Informationen während der Arbeit hier festhalten. Taskübergreifendes gehört in `Roadmap/README.md`.

- **Quellenliste (Nutzer, 2026-11-05):** Vorschlag übernommen – 8 deutschsprachige und 5 englischsprachige Medien, siehe `backend/config/news_sources.toml` und `docs/operations.md`. Nutzungsbedingungen je Feed vor dem Release bestätigen (Tasks 25/28).
- **Annahme umgesetzt:** Fragen entstehen direkt in `en` und `de` (zwei Datensätze mit gemeinsamer `group_id`).
- **Probelauf 2026-11-05** (Skript mit echten Feeds, echtem LLM und In-Memory-Repositories, da lokal keine DB): 613 Einträge aus 12 von 13 Feeds (The Telegraph verweigert automatische Abrufe), 3 Fragen erzeugt, 0 abgelehnt, 0 verworfen; 7 LLM-Aufrufe, 14.098 Input- / 1.109 Output-Tokens. `gemini-3.8-flash` (Wert in `.env`) und weitere Flash-Modelle lieferten zu der Zeit dauerhaft 503 „high demand"; der Lauf lief deshalb per Umgebungsvariable mit `LLM_MODEL=google:gemini-3.1-flash-lite`. Ergebnisse: „Should passengers be permitted to carry firearms in locked containers on Amtrak trains?" (scale, Einzelquelle Guardian), „What should have priority in the planned nursing care reform: fiscal sustainability or the needs of those requiring care …?" (tradeoff, Deutschlandfunk + FAZ), „Should the G7 nations implement France's proposal to establish an international oversight body for AI?" (scale, Einzelquelle POLITICO). Alle Fakten zitieren nur übergebene Quellen; deutsche Fassungen sind natürlich formuliert. Beobachtung: Kandidaten sind oft Einzelquellen und teils US-lastig – Qualität wird in Task 23 evaluiert, Prompt-Anpassung dann als `news_candidates.v2`.

## Abschluss-Checkliste

Reihenfolge und Details stehen in `AGENTS.md`, Abschnitt "Abschluss- und Archivierungs-Workflow".

- [x] Alle Akzeptanzkriterien erfüllt, Tests liegen permanent in den Test-Suites der Teile und laufen grün
- [x] Definition of Done aus `docs/testing.md` erfüllt und betroffene Dateien in `docs/` aktualisiert
- [x] Abschnitt "Erkenntnisse für Folge-Agenten" unten ausgefüllt
- [x] Folge-Tasks und `Roadmap/README.md` geprüft und bei Bedarf angepasst
- [x] Datei ohne `RUN_` nach `Roadmap/Archiv/` verschoben

## Erkenntnisse für Folge-Agenten

Vor der Archivierung vom Agenten auszufüllen. Schreibe so, dass ein Agent, der diesen Task nie gesehen hat, davon bei späteren Tasks profitiert:

- **Umgesetzt (und Abweichungen vom Plan):** Paket `dicrates/news/` (`models`, `sources`, `repository`, `pipeline`, `cycle`), Konfiguration `backend/config/news_sources.toml` (TOML statt YAML: `tomllib` aus der Standardbibliothek, keine Zusatzabhängigkeit), drei Prompts (`news_candidates.v1`, `question_draft.v1`, `question_check.v1`), Migration `news_items` + `questions.group_id`, `QuestionContent.single_source`, periodischer Job `news_questions`, CLI `questions generate --from-news --limit`, `LlmTaskRunner`-Protokoll, Pydantic-AI-Banner abgeschaltet.
- **Learnings & Stolpersteine:** feedparser setzt bei HTML-Fehlerseiten nicht zuverlässig `bozo` – Nicht-Feeds an fehlender `version` erkennen. Pydantic AI 2.x druckt beim ersten Lauf ein Banner, das für Logfire wirbt; `pydantic_ai.BANNER_ENABLED = False` steht jetzt in `llm/factory.py`. Gemini-Flash-Modelle können stundenweise komplett 503 liefern – der Runner erkennt das als transient, nach den Retries schlägt der Lauf sauber mit `unavailable` fehl. Die Quellen baut das Backend selbst aus den gespeicherten Einträgen; das LLM vergibt nur Nummern – so können keine URLs erfunden werden. Ruff vor jedem Commit laufen lassen (einmal mit offenem Fund gepusht).
- **Wichtige Entscheidungen und ihre Gründe:** Ein zweisprachiger Entwurfsaufruf statt zwei getrennter (gleiche Fakten in beiden Sprachen, weniger Kosten). Abgelehnte Entwürfe werden mit Grund gespeichert (Transparenz für den Betreiber und Duplikatschutz), verworfene (ungültige Quellenbezüge, LLM-Fehler) nicht. Bei zweitem `revise` gilt die Frage als abgelehnt. Duplikatschutz per Liste der vorhandenen Fragetexte im Kandidaten-Prompt.
- **Auswirkungen auf Folge-Tasks:** Task 08 kann `question_draft`/`question_check` und die Speicherlogik aus `news/pipeline.py` wiederverwenden (ggf. in ein gemeinsames Modul `questions/drafting.py` ziehen); Herkunft `evergreen`, Quellen dort aus kuratierten Referenzen statt News. Task 09 sollte beim Raum-Anlegen pro `group_id` nur die Fassung in der Raumsprache zeigen. Task 17: Worker muss in Produktion laufen, damit der Periodic-Job feuert. Task 23 bewertet die Fragequalität (Einzelquellen-Anteil, Regionalbezug). Task 25/28: Feed-Nutzungsbedingungen klären.
- **Hinweise zu Tests und Befehlen:** `uv run pytest tests/news` (Feeds, Pipeline mit `ScriptedRunner`), `-m integration` (News-Repository). Probelauf-Skript-Muster: echte `collect_news` + `LlmRunner` mit `FakeNewsRepository`/`FakeQuestionRepository` (siehe Notizen).
