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

- [ ] Alle Tests grün, Definition of Done erfüllt.
- [ ] `uv run dicrates-admin questions generate --from-news --limit 3` erzeugt mit gesetztem LLM-Key Entwürfe, die `questions list --status draft` zeigt (manuell, Ergebnis in Notizen).
- [ ] Jeder gespeicherte Entwurf hat mindestens zwei Quellen aus unterschiedlichen Medien oder ist als Einzelquelle gekennzeichnet.
- [ ] Quellenliste und Pipeline sind dokumentiert.

## Offene Fragen / Annahmen

- **Rückfrage an den Nutzer vor Umsetzung:** Welche Medien kommen in die Quellenliste (Vorschlag: breites Spektrum deutscher und internationaler Medien mit öffentlichen RSS-Feeds)? Nutzungsbedingungen der Feeds prüfen.
- Annahme: Fragen werden direkt in beiden Sprachen erzeugt (zwei Datensätze, verknüpft über eine gemeinsame Gruppen-ID), damit deutsch- und englischsprachige Räume dieselbe Frage nutzen können.

## Notizen zu diesem Task

Taskspezifische Informationen während der Arbeit hier festhalten. Taskübergreifendes gehört in `Roadmap/README.md`.

## Abschluss-Checkliste

Reihenfolge und Details stehen in `AGENTS.md`, Abschnitt "Abschluss- und Archivierungs-Workflow".

- [ ] Alle Akzeptanzkriterien erfüllt, Tests liegen permanent in den Test-Suites der Teile und laufen grün
- [ ] Definition of Done aus `docs/testing.md` erfüllt und betroffene Dateien in `docs/` aktualisiert
- [ ] Abschnitt "Erkenntnisse für Folge-Agenten" unten ausgefüllt
- [ ] Folge-Tasks und `Roadmap/README.md` geprüft und bei Bedarf angepasst
- [ ] Datei ohne `RUN_` nach `Roadmap/Archiv/` verschoben

## Erkenntnisse für Folge-Agenten

<!-- ERKENNTNISSE-OFFEN: Vor der Archivierung ausfüllen und diese Zeile löschen. -->

Vor der Archivierung vom Agenten auszufüllen. Schreibe so, dass ein Agent, der diesen Task nie gesehen hat, davon bei späteren Tasks profitiert:

- **Umgesetzt (und Abweichungen vom Plan):**
- **Learnings & Stolpersteine:**
- **Wichtige Entscheidungen und ihre Gründe:**
- **Auswirkungen auf Folge-Tasks:**
- **Hinweise zu Tests und Befehlen:**
