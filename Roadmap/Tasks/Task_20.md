# Task_20: Meldefunktion und Moderations-CLI

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_20.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M4 Betrieb und Erreichbarkeit

## Ziel

Nutzer können Streitfragen, Zusammenfassungen und problematisches Verhalten in einem Raum melden und sehen den Bearbeitungsstand ihrer Meldung. Der Betreiber bearbeitet Meldungen per CLI und kann Fragen zurückziehen, Zusammenfassungen neu erzeugen sowie Nutzer verwarnen oder sperren. Damit erfüllt die App die Grundanforderung der Stores an nutzergenerierte Inhalte und legt den Grundstein für DSA-Meldewege.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Tasks 06 (Fragen, CLI) und 13 (Zusammenfassungen) archiviert; Task 12 (`moderation_events`).
- **Relevantes Vorwissen:** `docs/concept-original.de.md` Kapitel 14 (Meldefunktion, Eskalation: Verwarnung, temporäre Sperre, Ausschluss), Produktentscheidung: Moderation im MVP per CLI.

## Umfang

**Gehört dazu:**

- Migration `reports` (meldendes Mitglied, Zieltyp `question`/`summary`/`room_behavior`/`feedback`, Ziel-ID, Kategorie, optionaler Text, Status `open`/`in_review`/`resolved`/`dismissed`, Ergebnis, Zeitstempel) und `user_sanctions` (Nutzer, Art `warning`/`suspension`/`ban`, bis, Grund, Quelle).
- API `POST /reports`, `GET /me/reports` (eigene Meldungen mit Status).
- Gesperrte Nutzer können keine Räume erstellen oder beitreten (403 mit Hinweis); laufende Partien: Abgaben werden nicht mehr angenommen.
- CLI: `reports list/show/resolve/dismiss`, Aktionen `questions retire`, `summaries regenerate <room> <round>` (neuer Lauf, neue Version, Mitglieder sehen die neue Fassung), `users warn/suspend/ban/unban`. Bei `room_behavior` zeigt das CLI die betroffenen Abgaben des Raums, die Zuordnung zu Konten nur, wenn ausdrücklich angefordert und protokolliert.
- Jede Aktion erzeugt ein `moderation_event` mit Quelle `human`.
- App: „Melden"-Aktion an Frage, Zusammenfassungen und Ergebnis sowie „Verhalten im Raum melden"; Liste „Meine Meldungen"; Hinweis bei Verwarnung oder Sperre.

**Gehört nicht dazu:**

- Web-Admin (Phase 2), Trust-Score und Troll-Pool (Phase 2), rechtliche Ausgestaltung der DSA-Pflichten (Task 28).

## Umsetzungsschritte

1. Rote Backend-Tests für Meldungen und Sanktionswirkung schreiben, dann Migrationen und Service.
2. CLI-Befehle per TDD, inkl. Protokollierung jeder Zuordnungsanzeige.
3. `summaries regenerate` per TDD (neue Version ersetzt Anzeige, alte bleibt für Nachvollziehbarkeit bis zur Löschfrist).
4. App-Aktionen und Screens per Widget-Tests und Goldens.
5. Moderationsablauf (wer prüft wie oft, Reaktionszeiten) als Entwurf in `docs/operations.md` anlegen oder ergänzen.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`backend/tests/`, `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Meldung nur für Inhalte des eigenen Raums bzw. sichtbare Fragen; Status sichtbar für den Meldenden.
- Gesperrter Nutzer: Erstellen und Beitreten 403; Abgabe 403.
- Aufhebung einer Sperre stellt Rechte wieder her.
- `summaries regenerate` erzeugt eine neue Version; API liefert die neueste.
- Anzeige der Konto-Zuordnung im CLI wird protokolliert.
- App: Melde-Dialog, Status-Liste, Sperrhinweis; Goldens.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Alle Tests grün, Definition of Done erfüllt.
- [ ] Ein Meldeablauf (melden → prüfen → Aktion → Status beim Meldenden) ist lokal end to end belegt (Notizen).
- [ ] `docs/operations.md` enthält den Moderationsablauf.

## Offene Fragen / Annahmen

- Reaktionszeiten und rechtliche Pflichten (DSA, Meldepflichten bei strafbaren Inhalten) klärt Task 28 mit dem Anwalt; hier nur technische Grundlage.

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
