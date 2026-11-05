# Task_14: Runde 3: Bewegung und Argument-Feedback

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_14.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M3 Kernspiel

## Ziel

Nach Runde 2 fasst das LLM zusammen, was sich in der Gruppe bewegt hat und was offen bleibt, ohne einzelne Personen erkennbar zu machen. In Runde 3 geben die Mitglieder Feedback zu Argumenten (nicht zu Personen): hilfreich, überzeugend, unklar, hier fehlt etwas, optional mit Freitext. Dieses Feedback ist später ein schwaches Zusatzsignal für die Bewertung.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 13 archiviert (Gruppenbild mit Argument-IDs, Runde-2-Abgaben, `summaries`).
- **Relevantes Vorwissen:** `docs/concept-original.de.md` Kapitel 9 (Runde 3, Feedback auf Argumente), Erkenntnisse aus Task 13 (Prompt-Aufbau, Wortübernahme-Prüfung, interne Zuordnung Argument ↔ Mitglied).

## Umfang

**Gehört dazu:**

- Prompt `movement.v1` und Ausgabemodell: Veränderungen, gehaltene Positionen mit Begründungen, offene Punkte, Argumente mit IDs (bestehende IDs aus dem Gruppenbild wiederverwenden, neue ergänzen); aggregierte Formulierungen ohne Aussagen über einzelne Personen; keine Verteilung.
- Hook: `R2_CLOSED` → Bewegungs-Job → `R3_OPEN`; gleiche Schutzprüfungen wie in Task 13.
- Migration `feedback` (Raum, Runde, gebendes Mitglied, Argument-ID, Tags, optionaler Freitext, Moderationsstatus). Freitext läuft durch den Filter aus Task 12.
- Regeln: kein Feedback auf eigene Argumente (Backend kennt die Zuordnung), höchstens ein Feedback je Argument und Mitglied, nur in `R3_OPEN`.
- Teilnahme an Runde 3 = mindestens ein Feedback abgegeben (für Frühschluss und Punkte).
- API und App: Bewegungs-Screen mit KI-Hinweis; Argumentliste mit Feedback-Auswahl.

**Gehört nicht dazu:**

- Einfluss des Feedbacks auf Punkte (Task 16), Meldefunktion (Task 20).

## Umsetzungsschritte

1. Ausgabemodell und Prompt; rote Tests mit `FunctionModel`.
2. Eingabe-Aufbereitung (Runde 1 und 2 je Pseudonym, Gruppenbild) per TDD.
3. Hook und Übergang `R3_OPEN` per TDD.
4. Feedback-Endpunkte und Regeln per TDD (inkl. „eigenes Argument" verboten).
5. App-Screens mit Widget-Tests und Goldens.
6. Manueller Lauf mit erfundenen Daten, Notizen.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`backend/tests/`, `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Bewegungs-Zusammenfassung wird erzeugt und gespeichert; `R3_OPEN` erst danach.
- Feedback auf eigenes Argument → 409 (ohne zu verraten, dass es das eigene ist: neutrale Fehlermeldung).
- Doppeltes Feedback auf dasselbe Argument wird ersetzt bzw. abgelehnt (Verhalten festlegen).
- Freitext wird gefiltert; `flagged` wird nicht verwendet.
- API gibt nie preis, welches Argument von wem stammt.
- App: Feedback-Auswahl barrierearm; Goldens.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Alle Tests grün, Definition of Done erfüllt.
- [ ] Ein lokaler Raum erreicht nach Runde 2 automatisch `R3_OPEN` mit Bewegungs-Zusammenfassung (Notizen).
- [ ] Kein API-Feld erlaubt Rückschlüsse von Argument auf Mitglied (Test).

## Offene Fragen / Annahmen

- Die App blendet eigene Argumente in der Feedback-Liste einfach aus. Das verrät dem Mitglied nur, welche Argumente von ihm selbst stammen, und das weiß es ohnehin. Diese Annahme dokumentieren.
- Annahme: In Räumen mit 3 Mitgliedern formuliert das LLM besonders vorsichtig („einige", „ein Teil der Gruppe").

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
