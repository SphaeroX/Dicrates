# Task_08: Zeitlose und historische Streitfragen

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_08.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M2 Streitfragen

## Ziel

Neben den News-Fragen gibt es einen wachsenden Bestand an zeitlosen und historischen Streitfragen (z. B. Tempolimit, Wehrpflicht, Atomkraft, Grundeinkommen, Wahlalter 16), damit die Bibliothek nie leer ist. Das LLM erzeugt sie aus einer kuratierten Themenliste mit derselben Prüfung wie in Task 07. Am Ende liegt ein freigabefähiger Startbestand in beiden Sprachen vor. Leitlinie: „Hauptsache kontrovers".

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 06 archiviert; Task 07 liefert Prompts `question_draft` und `question_check`, die hier wiederverwendet werden.
- **Relevantes Vorwissen:** Erkenntnisse aus Task 07 (Prompt-Verhalten, Kosten, Duplikatschutz), `docs/concept-original.de.md` Kapitel 8 und 14 (klare Regeln für heikle Themen: sachliche Diskussion erlaubt, Menschenverachtung nicht).

## Umfang

**Gehört dazu:**

- Kuratierte Themenliste (z. B. `backend/config/evergreen_topics.yaml`): Thema, Themengebiet, optional Leitfrage und vertrauenswürdige Quellen-URLs (z. B. Bundeszentrale für politische Bildung, Parlamentsdokumente, Wikipedia als Einstieg), Kennzeichnung `historical` oder `evergreen`.
- LLM-Agent „zeitlose Streitfrage": aktuelle Gültigkeit beachten (historische Debatten werden als heute entscheidbare Frage formuliert), Faktenkasten nur aus angegebenen Quellen.
- Erreichbarkeitsprüfung der Quellen-URLs hinter einem Interface (Fake in Tests).
- CLI `questions generate --evergreen [--topic <id>] [--limit]`, Speicherung als `draft` mit Herkunft `evergreen`.
- Startbestand: mindestens 30 Entwürfe je Sprache erzeugen, damit der Nutzer mindestens 20 je Sprache freigeben kann.

**Gehört nicht dazu:**

- Freigabe selbst (Nutzeraufgabe per CLI), automatische Aktualisierung von Fakten, Bias-Evaluation (Task 23).

## Umsetzungsschritte

1. Rote Tests für Laden und Validieren der Themenliste schreiben, dann umsetzen.
2. Prompt `evergreen_question.v1` und Pipeline per TDD mit `FunctionModel`; Check aus Task 07 wiederverwenden.
3. Erreichbarkeitsprüfung per TDD (unerreichbare Quelle → Entwurf wird markiert, nicht verworfen).
4. CLI-Befehl per TDD.
5. Themenliste mit ca. 40 kontroversen Themen anlegen und dem Nutzer zur Durchsicht vorlegen.
6. Startbestand mit echtem LLM erzeugen (erfundene Nutzerdaten sind hier nicht beteiligt; nur öffentliche Themen) und Anzahl in Notizen festhalten.
7. Doku aktualisieren.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (hier `backend/tests/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Themenliste: Pflichtfelder, ungültiges Themengebiet wird abgelehnt.
- Pipeline: erzeugt `draft` mit Herkunft `evergreen`; Duplikat zu bestehender Frage wird übersprungen.
- Quellen-Erreichbarkeit: unerreichbar → Markierung im Entwurf.
- Safety-Check `reject` bei menschenverachtender Prämisse (Fixture).

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [x] Alle Tests grün, Definition of Done erfüllt.
- [x] Mindestens 30 Entwürfe je Sprache liegen vor: 40 en + 40 de in `backend/seed/evergreen_questions.json` (Abweichung: Datei statt lokaler DB, da lokal kein Docker; Import per `questions import seed/evergreen_questions.json`, sobald eine DB läuft).
- [x] Die Themenliste ist mit dem Nutzer abgestimmt (Vermerk in Notizen).
- [x] Doku beschreibt, wie neue Themen ergänzt werden.

## Offene Fragen / Annahmen

- **Rückfrage an den Nutzer:** Grenzen bei besonders heiklen Themen (z. B. Abtreibung, Todesstrafe, Migration, Geschlechtsidentität): alle erlaubt, solange neutral formuliert und ohne menschenverachtende Prämisse? Ergebnis in die Prüfregeln und in `Roadmap/README.md`.
- Der Startbestand liegt zunächst lokal; die Übernahme in Staging/Produktion regelt Task 17 bzw. 29 (z. B. Export/Import per CLI).
- Freigabe der Entwürfe ist eine Nutzeraufgabe.

## Notizen zu diesem Task

Taskspezifische Informationen während der Arbeit hier festhalten. Taskübergreifendes gehört in `Roadmap/README.md`.

- **Heikle Themen (Nutzer, 2026-11-05):** Alle erlaubt, solange neutral formuliert und ohne menschenverachtende Prämisse. Umgesetzt in `question_check.v2` (gilt jetzt auch für die News-Pipeline) und der Freigabe-Checkliste in `docs/operations.md`.
- **Themenliste (Nutzer, 2026-11-05):** Vorschlag mit 42 Themen bestätigt. Quellen: je ein Wikipedia-Artikel de und en, per API gesucht, Fehltreffer (z. B. Cannabis → „Georg Wurth", WM-Boykott → U-15-Turnier) von Hand korrigiert; alle 84 URLs am 2026-11-05 erreichbar.
- **Startbestand:** `LLM_MODEL=google:gemini-3.1-flash-lite uv run dicrates-admin questions generate --evergreen --limit 50 --output seed/evergreen_questions.json` (gemini-3.8-flash war überlastet) → 40 Entwürfe (= 40 en + 40 de), 0 abgelehnt, 2 verworfen (`cannabis_legalisation`, `olympics_bid_germany`: Faktenbezug auf nicht vorhandene Quelle; beim nächsten Lauf werden nur diese beiden erneut versucht). Nachbearbeitung: Das Modell hatte 16 Ja/Nein-Fragen als `tradeoff` mit Optionen „dafür/dagegen" angelegt; diese Paare wurden deterministisch zu `scale` ohne Optionen umgestellt (Fakten unverändert). Alle 80 Einträge validieren gegen `QuestionContent`.

## Abschluss-Checkliste

Reihenfolge und Details stehen in `AGENTS.md`, Abschnitt "Abschluss- und Archivierungs-Workflow".

- [x] Alle Akzeptanzkriterien erfüllt, Tests liegen permanent in den Test-Suites der Teile und laufen grün
- [x] Definition of Done aus `docs/testing.md` erfüllt und betroffene Dateien in `docs/` aktualisiert
- [x] Abschnitt "Erkenntnisse für Folge-Agenten" unten ausgefüllt
- [x] Folge-Tasks und `Roadmap/README.md` geprüft und bei Bedarf angepasst
- [x] Datei ohne `RUN_` nach `Roadmap/Archiv/` verschoben

## Erkenntnisse für Folge-Agenten

Vor der Archivierung vom Agenten auszufüllen. Schreibe so, dass ein Agent, der diesen Task nie gesehen hat, davon bei späteren Tasks profitiert:

- **Umgesetzt (und Abweichungen vom Plan):** Paket `dicrates/evergreen/` (Themenliste, URL-Prüfung, Pipeline), gemeinsames Modul `questions/drafting.py` (News-Pipeline darauf umgestellt, Tests unverändert grün), Prompts `evergreen_question.v1` und `question_check.v2`, `QuestionContent.topic_key`/`review_notes` (+ Migration), `questions/memory.py` (In-Memory-Repository), CLI `generate --evergreen [--topic] [--limit] [--output]`, `import` akzeptiert Listen, `core/http.py` mit gemeinsamem User-Agent. Konfiguration als TOML (`config/evergreen_topics.toml`) statt YAML. **Abweichung:** Startbestand als Seed-Datei statt in der lokalen DB (kein Docker); das löst zugleich die Übernahme nach Staging/Produktion (Task 17/29: `questions import`).
- **Learnings & Stolpersteine:** Wikimedia lehnt Bots ohne Kontaktangabe im User-Agent mit 403 ab (auch HEAD); Wikipedia-API drosselt (429) – Pausen einbauen. Flash-Lite wählt das Format `tradeoff` oft für Ja/Nein-Fragen; ein Abgleich Format ↔ Formulierung fehlt im Check-Prompt (Kandidat für `question_check.v3`/Task 23). Etwa 5 % der Entwürfe zitieren nicht vorhandene Quellennummern und werden korrekt verworfen.
- **Wichtige Entscheidungen und ihre Gründe:** Duplikatschutz über `topic_key` statt über das LLM (deterministisch, erlaubt Wiederaufnahme nach Abbrüchen). Unerreichbare Quellen verwerfen den Entwurf nicht, sondern landen in `review_notes` (CLI-Markierung `[check notes]`). `--output` setzt auf einer bestehenden Datei auf (Wiederaufnahme).
- **Auswirkungen auf Folge-Tasks:** Task 09 kann die Seed-Datei für manuelle Tests importieren und freigeben. Task 17/29: Seed per `questions import` in Staging/Produktion laden, dort freigeben. Task 23: Prompt-Qualität (Format-Wahl, Einzelquellen, Regionalbezug) mit echten Evals, ggf. neue Prompt-Versionen. Neue Generatoren nutzen `Drafter` aus `questions/drafting.py`.
- **Hinweise zu Tests und Befehlen:** `uv run pytest tests/evergreen` (prüft auch die Themenliste), `uv run pytest tests/admin`. Alle Quellen-URLs prüfen: siehe Snippet mit `HttpxUrlChecker` in den Notizen bzw. `generate` schreibt Unerreichbares in `review_notes`.
