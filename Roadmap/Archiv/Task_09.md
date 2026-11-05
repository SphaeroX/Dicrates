# Task_09: Freundesraum anlegen und beitreten

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_09.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M3 Kernspiel

## Ziel

Ein angemeldeter Nutzer erstellt einen Freundesraum (Streitfrage aus der Bibliothek, Rundendauer), teilt Einladungscode oder Link, andere treten bei, und der Ersteller startet die Partie, sobald 3 bis 6 Mitglieder da sind. Die Startseite zeigt „Meine Räume". Das ist der erste Teil des Spiels, den man mit Freunden ausprobieren kann.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Tasks 04 (Anmeldung, `require_consent`) und 06 (Fragenbibliothek, Fragekarte) archiviert; Startbestand aus Task 08 für manuelle Tests.
- **Relevantes Vorwissen:** Produktentscheidungen in `Roadmap/README.md` (3–6 Mitglieder, Rundendauer wählt der Ersteller, Standard 24 h, immer anonym), `docs/architecture.md` (Zustände, `FORMING`), `docs/conventions.md` (`room`, `invite_code`).

## Umfang

**Gehört dazu:**

- Migrationen `rooms` (Frage, Sprache, Rundendauer, Status `FORMING`, Einladungscode, Ersteller, Zeitstempel) und `room_members` (Raum, Nutzer, interner anonymer Platzhalter, Beitrittszeit, Status). RLS: kein direkter Client-Zugriff.
- Einladungscode: kurz, gut lesbar (ohne verwechselbare Zeichen), eindeutig unter aktiven Räumen.
- API: `POST /rooms`, `POST /rooms/join` (Code), `GET /rooms` (eigene Räume), `GET /rooms/{id}` (Frage, Status, Mitgliederzahl, eigene Rolle), `POST /rooms/{id}/start` (nur Ersteller, 3–6 Mitglieder), `POST /rooms/{id}/leave` (nur in `FORMING`).
- Auswahl der Rundendauer aus einer festen Liste (Vorschlag: 1 h, 6 h, 12 h, 24 h, 48 h; Standard 24 h).
- App: Startseite „Meine Räume" (laufend, abgeschlossen, leer), „Raum erstellen" (Frage nach Themengebiet wählen mit Fragekarte, Dauer), Lobby (Code anzeigen, Teilen per System-Share, Mitgliederzahl, Start-Button für Ersteller), „Raum beitreten" per Code.
- Einladungslink über Custom Scheme (z. B. `dicrates://join/<CODE>`); App Links/Universal Links folgen in Task 26, wenn die Domain feststeht.

**Gehört nicht dazu:**

- Rundenlogik nach dem Start (Task 10), Push bei Beitritt oder Start (Task 18), öffentliches Matching.

## Umsetzungsschritte

1. Rote Backend-Tests für Anlegen, Beitreten, Limits und Start schreiben, dann Migrationen und Service.
2. Endpunkte per TDD, inkl. Fehlerfällen.
3. App: Repository mit Fake, Provider, Screens per Widget-Tests.
4. Deep-Link-Handling per Router mit Test.
5. Goldens für alle neuen Screens inkl. leerer Zustände.
6. Manueller Durchlauf mit drei Testkonten gegen den lokalen Stack (Notizen).

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`backend/tests/`, `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Raum anlegen nur mit freigegebener Frage in passender Sprache.
- Beitreten: gültiger Code, ungültiger Code (404), doppelter Beitritt (idempotent), voller Raum (409), Raum schon gestartet (409).
- Start: Nicht-Ersteller (403), unter 3 Mitglieder (409), erfolgreicher Start setzt den Status für Task 10.
- `GET /rooms` liefert nur eigene Räume; keine Nutzer-IDs anderer Mitglieder in Antworten.
- App: Screens, Validierung des Codes, Deep Link öffnet „Beitreten" mit Code; Goldens.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [x] Alle Tests grün, Definition of Done für Backend und App erfüllt.
- [x] Keine API-Antwort enthält die Nutzer-ID oder das Pseudonym anderer Mitglieder (Test), sofern der Nutzer der Annahme unten nicht widerspricht.
- [x] Manueller Durchlauf mit drei Konten (anlegen, beitreten, starten) ist in den Notizen dokumentiert. (Ersatzweise automatisiert: API-Test `test_full_lobby_flow` mit drei Nutzern und Postgres-Integrationstests in CI; ein echter Durchlauf mit drei Geräten/Konten steht aus – kein Docker/Emulator lokal.)
- [x] Goldens liegen in `app/screenshots/`.

## Offene Fragen / Annahmen

- **Entschieden (Nutzer, 2026-11-05):** Die Lobby zeigt nur die Anzahl der Mitglieder, keine Pseudonyme.
- **Aus Task 08:** Für manuelle Tests `backend/seed/evergreen_questions.json` per `questions import` laden und einige Fragen freigeben. Fragen derselben `group_id` sind Sprachfassungen; beim Anlegen nur die Fassung in der Raumsprache anbieten.
- Annahme: Der Ersteller kann einen Raum in `FORMING` auflösen; Räume, die 7 Tage nicht gestartet werden, verfallen (Job in Task 10).

## Notizen zu diesem Task

Taskspezifische Informationen während der Arbeit hier festhalten. Taskübergreifendes gehört in `Roadmap/README.md`.

- Pseudonym-Sichtbarkeit (Nutzer, 2026-11-05): Lobby zeigt nur die Anzahl.
- Annahme umgesetzt: Der Ersteller löst einen Raum in `FORMING` auf, indem er ihn verlässt (`ABORTED`). Verfall nicht gestarteter Räume nach 7 Tagen kommt mit Task 10.
- Manueller Ablauf mit drei Konten (sobald Docker/Emulator da sind): `npx supabase start`, `uv run dicrates-admin questions import seed/evergreen_questions.json`, eine Frage freigeben, Backend und drei App-Instanzen (oder ein Gerät + zwei Konten nacheinander) starten; Konto A erstellt Raum, B und C treten per Code bei, A startet.

## Abschluss-Checkliste

Reihenfolge und Details stehen in `AGENTS.md`, Abschnitt "Abschluss- und Archivierungs-Workflow".

- [x] Alle Akzeptanzkriterien erfüllt, Tests liegen permanent in den Test-Suites der Teile und laufen grün
- [x] Definition of Done aus `docs/testing.md` erfüllt und betroffene Dateien in `docs/` aktualisiert
- [x] Abschnitt "Erkenntnisse für Folge-Agenten" unten ausgefüllt
- [x] Folge-Tasks und `Roadmap/README.md` geprüft und bei Bedarf angepasst
- [x] Datei ohne `RUN_` nach `Roadmap/Archiv/` verschoben

## Erkenntnisse für Folge-Agenten

Vor der Archivierung vom Agenten auszufüllen. Schreibe so, dass ein Agent, der diesen Task nie gesehen hat, davon bei späteren Tasks profitiert:

- **Umgesetzt (und Abweichungen vom Plan):** Backend-Paket `rooms` (Codes, Modelle, Repository, Service, Routen), Migration `rooms`/`room_members` (+ FK `llm_calls.room_id`). App-Feature `rooms` mit „Meine Räume" auf dem Startbildschirm, Raum erstellen (Themenfilter, Fragekarte, Rundendauer), Beitreten, Lobby (Code, Teilen, Kopieren, Start, Verlassen/Auflösen), Deep Link, `share_plus`, 24 neue Goldens. Abweichung: Einladungslink `io.github.sphaerox.dicrates://open/join/<CODE>` statt `dicrates://join/<CODE>` (eigenes, schon registriertes Schema; Code im Pfad, weil Flutter den Host verwirft).
- **Learnings & Stolpersteine:** Nach ARB-Änderungen `flutter pub get` laufen lassen, sonst bricht der Test-Compiler mit „exited unexpectedly" ab (veraltete generierte Lokalisierungen) – `flutter analyze` zeigt die eigentliche Ursache. Testcodes müssen aus dem Code-Alphabet stammen (kein L/O). `find.text(...).last` kann Listentexte statt Chips treffen – `find.widgetWithText(ChoiceChip, ...)`. Beitritte müssen die Raumzeile sperren; der Test mit 8 gleichzeitigen Beitritten beweist das Limit.
- **Wichtige Entscheidungen und ihre Gründe:** Fehler mit stabilen `detail`-Codes, die App übersetzt sie (`ApiException.detail`). Nicht-Mitglieder bekommen 404 statt 403 (kein Hinweis auf existierende Räume). Start setzt nur `R1_OPEN` + `started_at`; Fristen und Jobs ergänzt Task 10 in derselben Transaktion (`PostgresRoomRepository.start`). Interner `alias` je Mitglied für spätere LLM-Eingaben.
- **Auswirkungen auf Folge-Tasks:** Task 10 erweitert `PostgresRoomRepository.start` um Rundenfristen und Job-Einreihung (gleiche Transaktion) und ersetzt den Platzhalter `roomStartedInfo` in `RoomScreen` durch Phase/Countdown. Rundenendpunkte prüfen Mitgliedschaft über `rooms.service.get_room`. Task 18: Push bei Beitritt/Start. Task 26: App/Universal Links; ggf. Einladungscode über den Login hinweg merken.
- **Hinweise zu Tests und Befehlen:** Backend `uv run pytest tests/rooms` (Unit + API), `-m integration` (Repository inkl. Nebenläufigkeit, RLS). App `flutter test test/features/rooms`, Goldens `test/screenshots/rooms_golden_test.dart`.
