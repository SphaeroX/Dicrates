# Task_13: Runde 2: Gruppenbild und Überarbeitung

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_13.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M3 Kernspiel

## Ziel

Nach Runde 1 erzeugt das LLM ein Gruppenbild: jede Position in ihrer stärksten Form, Minderheitenmeinungen sichtbar, Hauptargumente und Randthemen, neutral, stilgeglättet und ohne Verteilung. Alle Mitglieder lesen es (als KI-generiert gekennzeichnet), überarbeiten ihre Position oder bleiben begründet dabei und beantworten „Wurde deine Position fair dargestellt?". Das ist der Kern des Produkts.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 12 archiviert (nur `allowed`-Abgaben); Task 10 (Hook nach `R1_CLOSED`).
- **Relevantes Vorwissen:** `docs/project-brief.md` (Runde 2), `docs/concept-original.de.md` Kapitel 9 (Anforderungen an das Gruppenbild) und 10 (Stilglättung), Produktentscheidung: keine Verteilung anzeigen, KI-Kennzeichnung (AI Act).

## Umfang

**Gehört dazu:**

- Migration `summaries` (Raum, Runde, Typ `group_picture`/`movement`/`evaluation`, strukturierter Inhalt als JSON, Prompt-Version, Modell, Zeit).
- Prompt `group_picture.v1` und Ausgabemodell: Überblick, Positionen (jeweils stärkste Form mit Argumenten, jedes Argument mit stabiler ID), Minderheitenpositionen, Randthemen; keine Zahlen zur Verteilung, keine Zitate.
- Eingabe ans LLM: nur `allowed`-Abgaben, pseudonymisiert (P1…Pn) und gemischt, keine Nutzerdaten. Die interne Zuordnung Argument-ID ↔ Mitglied bleibt im Backend (für Task 14 und 16).
- Schutz gegen Wiedererkennung: Prüfung auf wörtliche Übernahmen (z. B. gemeinsame Wortfolgen ab einer festen Länge) mit Retry; Prüfung, dass keine Verteilung genannt wird.
- Hook: `R1_CLOSED` → Gruppenbild-Job → bei Erfolg `R2_OPEN`; bei dauerhaftem Fehler bleibt der Raum stehen und wird für Task 21 als „hängend" erkennbar.
- API: `GET /rooms/{id}/summaries` (nur Mitglieder, nur bereits erzeugte), Runde-2-Abgabe (`PUT …/rounds/2/submission`) als Überarbeitung oder „Ich bleibe dabei" mit optionaler Begründung, Fairness-Rückmeldung (Tabelle `summary_feedback`: ja/teilweise/nein, optionaler Freitext über den Filter aus Task 12).
- App: Gruppenbild-Screen mit KI-Hinweis, Überarbeiten-Screen (vorbefüllt mit eigener Runde-1-Position), Fairness-Frage.

**Gehört nicht dazu:**

- Bewegungs-Zusammenfassung (Task 14), Vorlesen (Task 19), Qualitäts- und Bias-Evaluation mit echtem LLM (Task 23).

## Umsetzungsschritte

1. Ausgabemodell und Prompt entwerfen; rote Tests mit `FunctionModel` für gültige und ungültige Ausgaben.
2. Eingabe-Aufbereitung (Pseudonymisierung, Mischen, nur `allowed`) per TDD.
3. Wortübernahme- und Verteilungsprüfung per TDD.
4. Hook-Integration und Übergang `R2_OPEN` per TDD (Integration).
5. Endpunkte für Zusammenfassungen, Runde-2-Abgabe und Fairness-Rückmeldung per TDD.
6. App-Screens mit Widget-Tests und Goldens.
7. Manueller Lauf mit Gemini und erfundenen Abgaben; Ergebnis bewerten und in Notizen festhalten.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`backend/tests/`, `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- LLM-Eingabe enthält keine Nutzer-IDs, Pseudonyme oder `flagged`-Abgaben.
- Ausgabe mit langer wörtlicher Übernahme → Retry; dauerhaft → Fehlerpfad.
- Ausgabe mit Verteilungsangabe wird abgelehnt.
- `R2_OPEN` erst nach gespeichertem Gruppenbild; Job doppelt → ein Gruppenbild.
- Nicht-Mitglied bekommt 403; vor `R1_CLOSED` keine Zusammenfassung.
- „Ich bleibe dabei" erzeugt eine Abgabe der Runde 2 mit Verweis auf Runde 1.
- App: KI-Hinweis sichtbar und vom Screenreader lesbar; Goldens.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Alle Tests grün, Definition of Done erfüllt.
- [ ] Ein lokaler Raum mit drei Testkonten erreicht nach Runde 1 automatisch `R2_OPEN` und zeigt ein Gruppenbild (manuell, mit Gemini und erfundenen Texten, in Notizen belegt).
- [ ] Jede gespeicherte Zusammenfassung trägt Prompt-Version und Modell.

## Offene Fragen / Annahmen

- Schwellwert für wörtliche Übernahmen (Vorschlag: 8 Wörter in Folge) wird im Task festgelegt und in `Roadmap/README.md` notiert.
- Annahme: Fairness-Rückmeldung ist freiwillig und beeinflusst keine Punkte.

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
