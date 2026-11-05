# Task_10: Zustandsautomat der Runden

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_10.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M3 Kernspiel

## Ziel

Ein gestarteter Raum läuft automatisch durch die Zustände `R1_OPEN → … → FINISHED` bzw. `ABORTED`, gesteuert von Procrastinate-Jobs mit Fristen. Übergänge sind deterministisch, idempotent und sicher bei Wiederholung oder Gleichzeitigkeit. Die App zeigt Phase und Countdown. Spätere Tasks hängen ihre LLM-Schritte nur noch an definierte Übergänge an.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 09 archiviert (Räume, Start); Task 02 (Procrastinate, gemeinsame Transaktion).
- **Relevantes Vorwissen:** `docs/architecture.md` → „Rounds are a state machine" (Zustände inkl. `ARCHIVED`, Übergänge nur in Jobs), Produktentscheidungen (Runde schließt früh, wenn alle abgegeben haben; unter 3 gültigen Abgaben → `ABORTED` ohne Abzug).

## Umfang

**Gehört dazu:**

- Migration `rounds` (Raum, Nummer 1–4, Öffnung, Frist, Schlusszeit) und vollständiges Status-Enum für `rooms`.
- Reine Übergangsfunktion (Domänenlogik ohne I/O) mit Tabelle erlaubter Übergänge.
- Service, der Übergänge mit Zeilensperre (`SELECT … FOR UPDATE`) anwendet und Folge-Jobs in derselben Transaktion einreiht.
- Jobs: Runde schließen zur Frist (`schedule_at`), vorzeitiges Schließen, wenn alle aktiven Mitglieder abgegeben haben (Aufruf-Schnittstelle für Task 11), Abbruch bei unter 3 gültigen Abgaben in Runde 1.
- Hook-Schnittstelle: Registrierung von Schritten, die nach einem Übergang laufen müssen (z. B. „nach `R1_CLOSED` Gruppenbild erzeugen, dann `R2_OPEN`"); in diesem Task mit No-op-Schritten, die direkt weiterschalten.
- Injizierbare Uhr für Tests.
- Verfall von Räumen, die 7 Tage in `FORMING` bleiben; `FINISHED → ARCHIVED` nach Frist (Dauer als Einstellung, Löschfristen folgen in Task 22).
- API `GET /rooms/{id}/status` (Phase, Runde, Frist, eigener Abgabestatus, Anzahl Abgaben als Zahl).
- App: Raum-Screen mit Phase, Countdown, Aktualisierung (Pull-to-Refresh, periodisches Abfragen im Vordergrund).

**Gehört nicht dazu:**

- Inhalte der Runden (Tasks 11–16), Push-Benachrichtigungen (Task 18).

## Umsetzungsschritte

1. Rote Tests für die Übergangstabelle (alle erlaubten und verbotenen Übergänge) schreiben, dann die reine Funktion.
2. Service mit Sperre und Job-Einreihung per TDD (Integration).
3. Idempotenz- und Gleichzeitigkeitstests (gleicher Job zweimal, zwei Worker parallel).
4. Abbruch- und Frühschluss-Logik per TDD.
5. Hook-Registry per TDD.
6. Status-Endpunkt und App-Screen mit Widget-Tests und Goldens.
7. `docs/architecture.md` um Hook-Mechanismus und Regeln für Mindestbeteiligung ergänzen.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`backend/tests/`, `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Übergangstabelle vollständig.
- Job doppelt ausgeführt → gleicher Endzustand, keine doppelten Folge-Jobs.
- Zwei gleichzeitige Schließversuche → genau ein Übergang.
- Frist abgelaufen mit 2 Abgaben in Runde 1 → `ABORTED`.
- Alle haben abgegeben → Runde schließt vor der Frist.
- Verfall von `FORMING` nach 7 Tagen.
- App: Countdown-Anzeige, Phasen-Texte in `en`/`de`, Goldens.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Alle Tests grün, Definition of Done für Backend und App erfüllt.
- [ ] Ein Raum mit Rundendauer 1 h läuft lokal mit Worker ohne manuelles Eingreifen bis `FINISHED` (mit No-op-Hooks; Ablauf mit verkürzter Testuhr oder kurzer Dauer in Notizen belegt).
- [ ] Übergänge passieren ausschließlich in Jobs (Code-Review-Vermerk in Notizen).

## Offene Fragen / Annahmen

- Annahme: Mindestbeteiligung gilt hart nur für Runde 1. In Runden 2 und 3 bekommt, wer nicht abgibt, für diese Runde keine Punkte; die Partie läuft weiter. Mit dem Nutzer bestätigen, falls Zweifel bestehen.
- Annahme: Die Anzahl der Abgaben („3 von 5 haben abgegeben") darf angezeigt werden, weil sie keine Meinungsverteilung verrät.

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
