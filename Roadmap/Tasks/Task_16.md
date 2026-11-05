# Task_16: Punktevergabe

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_16.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M3 Kernspiel

## Ziel

Am Ende jeder Partie bekommt jedes Mitglied Punkte in sechs Dimensionen mit kurzer Begründung: Argumentqualität, Perspektivübernahme, Offenheit, Kompromissbeitrag, Respekt und Ton, Beteiligung. Die Bewertung ist stabil (mehrere LLM-Läufe, Median), belohnt Positionswechsel nicht an sich, bestraft begründetes Festhalten nicht und ist transparent und anfechtbar. Jeder sieht nur seine eigenen Punkte.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 15 archiviert (Auswertung, Hook-Kette bis `FINISHED`).
- **Relevantes Vorwissen:** `docs/concept-original.de.md` Kapitel 13 (Bewertungskriterien, Designregeln, Einspruch), `docs/project-brief.md` („Changing one's position never earns points by itself"), Erkenntnisse aus Tasks 13–15 (Argument-IDs, Feedback-Daten).

## Umfang

**Gehört dazu:**

- Prompt `scoring.v1` und Ausgabemodell: je Mitglied fünf LLM-Dimensionen 0–100 mit Begründung in Raumsprache. Eingabe: eigene Abgaben R1/R2, eigenes gegebenes Feedback, Gruppenbilder, aggregiertes Feedback anderer auf eigene Argumente (schwaches Signal, klar so markiert).
- Beteiligung wird deterministisch berechnet (abgegebene Runden), nicht vom LLM.
- Drei Läufe je Mitglied, Median je Dimension; Begründung aus dem Lauf, der dem Median am nächsten liegt.
- Gesamtpunktzahl nach dokumentierter Formel (Gewichte in `docs/` und in der App erklärt).
- Migration `evaluations` (Raum, Mitglied, Punkte je Dimension, Begründungen, Prompt-Version, Modell) und `appeals` (Mitglied, Raum, Grund, Status, Ergebnis).
- Hook vor `FINISHED`: Auswertung → Punktevergabe → `FINISHED`.
- API: eigene Punkte (`GET /rooms/{id}/evaluation/me`), Einspruch (`POST …/appeal`); Summe der Punkte im Profil (`/me`), kein Ranking.
- CLI `appeals list/show/resolve` (neu bewerten oder Punkte manuell anpassen, mit Protokoll).
- App: Punkte-Ansicht im Ergebnis, Screen „Wie wird bewertet?" mit Kriterien, Einspruch-Formular, Gesamtpunkte im Profil.

**Gehört nicht dazu:**

- Rating, Trust-Score, Ranking (Phase 2), echte Bias-Messung (Task 23).

## Umsetzungsschritte

1. Rote Tests für Median-Logik, Beteiligungsberechnung und Gesamtformel (rein, ohne LLM) schreiben, dann umsetzen.
2. Prompt und Ausgabemodell; Tests mit `FunctionModel` (drei unterschiedliche Läufe → Median).
3. Hook-Integration vor `FINISHED` per TDD.
4. Endpunkte, Rechte und Einspruch per TDD.
5. CLI für Einsprüche per TDD.
6. App-Screens mit Widget-Tests und Goldens.
7. Erfundene Fixture-Paare anlegen (gleiche Qualität, einmal Wechsel, einmal begründetes Festhalten) für Task 23.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`backend/tests/`, `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Median je Dimension aus drei Läufen; Auswahl der Begründung.
- Beteiligung: alle Runden, fehlende Runde 2, fehlende Runde 3.
- Mitglied kann fremde Punkte nicht abrufen (403/404).
- Einspruch: einmal je Partie, Statuswechsel per CLI, Neu-Bewertung ersetzt Punkte nachvollziehbar.
- Bewertung nutzt nur `allowed`-Inhalte.
- App: Punkte, Kriterien-Erklärung, Einspruch; Goldens.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Alle Tests grün, Definition of Done erfüllt.
- [ ] Ein lokaler Komplettdurchlauf endet mit Punkten für alle Mitglieder (Notizen).
- [ ] Gewichte und Formel sind in `docs/` und in der App erklärt.
- [ ] Fixture-Paare für Task 23 liegen bereit.

## Offene Fragen / Annahmen

- **Rückfrage an den Nutzer:** Gewichtung der Dimensionen in der Gesamtpunktzahl (Vorschlag: gleich gewichtet, Beteiligung als Multiplikator).
- Kosten: Drei Läufe je Mitglied bei 6 Mitgliedern sind 18 Aufrufe; Kosten pro Partie aus `llm_calls` in den Notizen festhalten.

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
