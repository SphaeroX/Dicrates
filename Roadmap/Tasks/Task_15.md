# Task_15: Runde 4: Auswertung und Kompromiss

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_15.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M3 Kernspiel

## Ziel

Nach Runde 3 erstellt das LLM die Auswertung: wie die Gruppe das Thema insgesamt sieht, einen konkreten Kompromissvorschlag sowie Pro und Contra dazu. Alle Mitglieder sehen das Ergebnis und können offenes Feedback zur Partie geben (Thema gut formuliert? Zusammenfassungen fair? Wie war die Runde?). Der Betreiber liest dieses Feedback per CLI.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 14 archiviert (Bewegung, Argument-Feedback).
- **Relevantes Vorwissen:** `docs/concept-original.de.md` Kapitel 9 (Runde 4, zwei Feedbackarten getrennt), Erkenntnisse aus Tasks 13–14.

## Umfang

**Gehört dazu:**

- Prompt `evaluation.v1` und Ausgabemodell: Gesamtbild, Kompromissvorschlag, Pro- und Contra-Punkte, offene Fragen; neutral, keine Verteilung, keine Personenbezüge.
- Hook: `R3_CLOSED` → `R4_EVALUATING` → Auswertungs-Job → `FINISHED` (Task 16 fügt die Punktevergabe vor `FINISHED` ein).
- Migration `match_feedback` (Raum, Mitglied, Bewertung der Frage, Fairness der Zusammenfassungen, Freitext mit Filter aus Task 12).
- CLI `dicrates-admin feedback list [--room]` mit aggregierten Werten; Freitexte nur nach ausdrücklichem Befehl und ohne Nutzerbezug.
- App: Ergebnis-Screen (Gesamtbild, Kompromiss, Pro/Contra, KI-Hinweis), Partie-Feedback-Formular, abgeschlossene Räume in „Meine Räume" mit Zugriff auf das Ergebnis.

**Gehört nicht dazu:**

- Punkte (Task 16), Vorlesen (Task 19), Löschfristen für Texte (Task 22).

## Umsetzungsschritte

1. Ausgabemodell und Prompt; rote Tests mit `FunctionModel`.
2. Hook-Kette bis `FINISHED` per TDD (Integration), inkl. Wiederholbarkeit.
3. Partie-Feedback per TDD.
4. CLI-Befehl per TDD.
5. App-Screens mit Widget-Tests und Goldens.
6. Manueller Komplettdurchlauf R1–R4 mit drei Testkonten und erfundenen Texten (Notizen).

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`backend/tests/`, `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Auswertung wird erzeugt, gespeichert und erst dann `FINISHED` gesetzt.
- Fehler im Auswertungs-Job → Raum bleibt in `R4_EVALUATING`, Retry möglich, kein doppeltes Ergebnis.
- Partie-Feedback nur nach `FINISHED`, einmal je Mitglied.
- CLI zeigt Aggregat ohne Nutzerbezug.
- App: Ergebnis-Screen in en/de, Goldens.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Alle Tests grün, Definition of Done erfüllt.
- [ ] Ein vollständiger lokaler Durchlauf von Raum anlegen bis Ergebnis ist in den Notizen belegt.
- [ ] Goldens der Ergebnis- und Feedback-Screens liegen in `app/screenshots/`.

## Offene Fragen / Annahmen

- Annahme: Der Kompromissvorschlag ist ein Vorschlag des LLM, keine Abstimmung; eine Zustimmung „Kompromiss tragbar?" könnte als Kennzahl dienen. Mit dem Nutzer klären, ob sie ins MVP soll.

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
