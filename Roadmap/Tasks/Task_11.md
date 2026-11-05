# Task_11: Runde 1: Position abgeben

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_11.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M3 Kernspiel

## Ziel

In Runde 1 sieht jedes Mitglied Streitfrage und Faktenkasten und gibt blind seine Position ab: Skalenwert, Vorschlag oder Wahl A/B (je nach Format) plus Begründung. Bis zur Frist kann es die Abgabe ändern. Kein Client kann jemals die Abgabe eines anderen lesen, und kein Log enthält ihren Text.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 10 archiviert (Status `R1_OPEN`, Frühschluss-Schnittstelle).
- **Relevantes Vorwissen:** `docs/architecture.md` (Anonymität serverseitig, RLS sperrt Submission-Tabellen), Root-`AGENTS.md` Regel 4 (nie Abgabetext loggen), `docs/concept-original.de.md` Kapitel 9 (Runde 1), Fragekarte aus Task 06.

## Umfang

**Gehört dazu:**

- Migration `submissions`: Raum, Runde, Mitglied, Revision, Skalenwert (1–5) bzw. Vorschlagstext bzw. Wahl A/B, Begründung, Moderationsstatus (für Task 12, Standard `pending`), Zeitstempel. RLS: kein Client-Zugriff.
- API: `PUT /rooms/{id}/rounds/1/submission` (anlegen/ändern), `GET /rooms/{id}/rounds/1/submission` (nur eigene).
- Validierung: Felder passend zum Fragenformat, Längengrenzen (Vorschlag: Begründung 30–2000 Zeichen, mit dem Nutzer prüfen), nur Mitglieder, nur in `R1_OPEN`.
- Nach jeder Abgabe: Frühschluss-Prüfung aus Task 10 aufrufen.
- Logging-Schutz: zentraler Filter oder Konvention, die Abgabetexte nie in Logs oder Fehlermeldungen gelangen lässt; Test dazu.
- App: Runde-1-Screen (Frage, Faktenkasten, barrierearme 5er-Skala mit Text-Beschriftungen, Textfelder, Zeichenzähler, Speichern, Hinweis „Die anderen siehst du nur als Zusammenfassung"), Bearbeiten bis zur Frist, Status „abgegeben".

**Gehört nicht dazu:**

- Inhaltsfilter (Task 12), Spracheingabe (Task 19), Gruppenbild (Task 13).

## Umsetzungsschritte

1. Rote Backend-Tests für Anlegen, Ändern, Validierung und Rechte schreiben, dann Migration und Service.
2. Test „Text erscheint nicht im Log" (`caplog`) schreiben und Logging-Schutz umsetzen.
3. Frühschluss-Aufruf per Integrationstest.
4. RLS-Test: authentifizierter Client kann `submissions` nicht lesen.
5. App: Screen per Widget-Tests (alle drei Formate, Validierung, Bearbeiten), Goldens.
6. Doku: Logging-Regel technisch beschreiben (`docs/code-style.md` oder `docs/architecture.md`).

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`backend/tests/`, `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Abgabe in `R1_OPEN` angelegt und geändert (Revision steigt); nach Frist 409; Nicht-Mitglied 403.
- Format-Validierung je Fragenformat; Längengrenzen.
- `GET` liefert nur die eigene Abgabe; es gibt keinen Endpunkt, der fremde Abgaben liefert.
- Logs enthalten den Begründungstext nicht, auch nicht bei Validierungsfehlern.
- Letzte fehlende Abgabe schließt die Runde vorzeitig.
- App: Formate, Fehleranzeige, Goldens leer/ausgefüllt/abgegeben.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Alle Tests grün, Definition of Done für Backend und App erfüllt.
- [ ] RLS-Integrationstest belegt: direkter Supabase-Zugriff auf `submissions` liefert nichts.
- [ ] Goldens liegen in `app/screenshots/`.

## Offene Fragen / Annahmen

- Längengrenzen der Begründung sind ein Vorschlag; bei Bedarf mit dem Nutzer abstimmen.
- Annahme: Beim Format `proposal` gibt es keinen Skalenwert, nur Vorschlag und Begründung.

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
