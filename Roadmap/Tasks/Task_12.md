# Task_12: Inhaltsfilter

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_12.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M3 Kernspiel

## Ziel

Jede Abgabe und jeder Freitext wird vom LLM auf Beleidigungen, Hassrede, Gewaltaufrufe, Doxing und Spam geprüft, bevor er in eine Zusammenfassung einfließen kann. Markierte Inhalte werden mit verständlichem Hinweis zur Überarbeitung zurückgegeben und als Moderationsereignis gespeichert. Sachliche Positionen zu heiklen Themen bleiben ausdrücklich erlaubt.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Tasks 05 (LLM-Schicht) und 11 (Abgaben mit Moderationsstatus) archiviert.
- **Relevantes Vorwissen:** `docs/concept-original.de.md` Kapitel 14 (mehrstufiger Schutz, klare Regeln für heikle Themen) und 15 (Aufgabe 4), Erkenntnisse aus Task 05.

## Umfang

**Gehört dazu:**

- Prompt `content_filter.v1` und Agent mit Ausgabe `allow` oder `flag` (Kategorie: Beleidigung, Hassrede, Gewaltaufruf, Doxing/personenbezogene Daten, Spam; kurzer Grund ohne Zitat des Textes).
- Generischer Filter-Service, der für Abgaben (jetzt) und für Feedback-Freitexte (Tasks 14, 15) nutzbar ist.
- Job direkt nach dem Speichern einer Abgabe; Ergebnis im Moderationsstatus (`allowed`, `flagged`, `pending`).
- Migration `moderation_events` (Nutzer, Raum, Typ, Quelle `llm`/`human`, Wirkung, Zeit; ohne Inhaltstext).
- Rundenschluss: Abgaben mit `pending` werden synchron nachgeprüft; `flagged` zählt als nicht abgegeben und fließt nicht in Zusammenfassungen ein.
- API liefert dem Autor den Moderationsstatus seiner Abgabe; App zeigt einen Hinweis mit Kategorie und Bitte um Überarbeitung (en/de).
- Fehlerfall LLM: Retries; bleibt `pending` bis zum Rundenschluss, dann Entscheidung nach dokumentierter Regel (Vorschlag: nicht verwenden und Ereignis protokollieren).

**Gehört nicht dazu:**

- Meldefunktion und Sanktionen (Task 20), Trust-Score (Phase 2).

## Umsetzungsschritte

1. Ausgabemodell und Prompt entwerfen; rote Tests mit `FunctionModel` für `allow` und `flag` schreiben.
2. Filter-Service und Job per TDD.
3. Migration und Protokollierung der Ereignisse per TDD.
4. Rundenschluss-Integration aus Task 10 per TDD (Nachprüfung, Ausschluss).
5. API-Feld und App-Hinweis per Widget-Tests, Goldens.
6. Prompt-Regeln für heikle Themen formulieren und einige erfundene Grenzfälle als Fixtures für Task 23 ablegen.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`backend/tests/`, `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- `flag` setzt Status und erzeugt ein Ereignis ohne Inhaltstext.
- `allow` setzt Status `allowed`.
- LLM-Fehler → Retry, danach `pending`; Rundenschluss prüft nach.
- `flagged` wird nicht an Zusammenfassungs-Hooks übergeben.
- Überarbeitete Abgabe wird neu geprüft.
- App: Hinweis je Kategorie in en/de; Golden.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Alle Tests grün, Definition of Done erfüllt.
- [ ] Zusammenfassungs-Eingaben bestehen nachweislich nur aus Abgaben mit Status `allowed` (Test).
- [ ] Grenzfall-Fixtures für Task 23 liegen bereit (erfundene Texte).

## Offene Fragen / Annahmen

- Annahme: Ein Modell für alle Aufgaben. Wenn Kosten oder Latenz des Filters zu hoch sind, Vorschlag für ein kleineres Filtermodell beim Nutzer einholen (Architekturänderung).
- Annahme: Der Autor sieht nur die Kategorie, nicht die Begründung des LLM im Detail.

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
