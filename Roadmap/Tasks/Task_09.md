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

- [ ] Alle Tests grün, Definition of Done für Backend und App erfüllt.
- [ ] Keine API-Antwort enthält die Nutzer-ID oder das Pseudonym anderer Mitglieder (Test), sofern der Nutzer der Annahme unten nicht widerspricht.
- [ ] Manueller Durchlauf mit drei Konten (anlegen, beitreten, starten) ist in den Notizen dokumentiert.
- [ ] Goldens liegen in `app/screenshots/`.

## Offene Fragen / Annahmen

- **Rückfrage an den Nutzer:** Sieht man in der Lobby die Pseudonyme der Mitglieder (Freunde kennen sich ohnehin) oder nur die Anzahl? Annahme bis zur Antwort: nur die Anzahl, weil das die Anonymität am besten schützt.
- Annahme: Der Ersteller kann einen Raum in `FORMING` auflösen; Räume, die 7 Tage nicht gestartet werden, verfallen (Job in Task 10).

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
