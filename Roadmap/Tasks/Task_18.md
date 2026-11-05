# Task_18: Push-Benachrichtigungen

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_18.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M4 Betrieb und Erreichbarkeit

## Ziel

Mitglieder werden per Push über die wichtigen Momente einer asynchronen Partie informiert: Partie gestartet, neue Runde offen, Erinnerung vor Fristende (nur wer noch nicht abgegeben hat), Ergebnis da. Ein Tipp öffnet direkt den Raum. Benachrichtigungen enthalten nie Inhalte aus Abgaben.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Tasks 10 (Übergänge, Hooks) und 17 (Staging, Secrets) archiviert.
- **Relevantes Vorwissen:** `docs/architecture.md` (FCM, APNs via FCM), `.env.example` (`FCM_PROJECT_ID`, `GOOGLE_APPLICATION_CREDENTIALS`), Firebase-Projekt existiert. Apple Developer Program fehlt → iOS-Push erst, wenn das Konto da ist.

## Umfang

**Gehört dazu:**

- App: `firebase_core` und `firebase_messaging` per `flutter pub add`, Android-Konfiguration, Berechtigungsabfrage mit vorheriger Erklärung (nicht beim ersten Start, sondern beim ersten Raum), Token registrieren/abmelden, Tipp auf Benachrichtigung → Raum öffnen.
- Migration `device_tokens` (Nutzer, Token, Plattform, Sprache, zuletzt gesehen).
- API `POST /me/devices`, `DELETE /me/devices/{token}`.
- Backend: Interface `PushSender` mit FCM-HTTP-v1-Implementierung (Service-Account) und Fake für Tests; ungültige Tokens werden entfernt.
- Ereignisse über die Hooks aus Task 10: Start, Runde offen, Erinnerung (Vorschlag: 2 h vor Frist bzw. bei 1-h-Runden 15 min), Ergebnis da, Raum abgebrochen.
- Benachrichtigungstexte lokalisiert über einen Backend-Nachrichtenkatalog (en/de), keine fest kodierten Strings; kein Abgabeinhalt, nur Raum- und Phasenbezug.
- Einstellung in der App: Benachrichtigungen ein/aus.

**Gehört nicht dazu:**

- iOS/APNs-Konfiguration (sobald Apple-Konto da ist; spätestens Task 26 prüft das), E-Mail-Benachrichtigungen.

## Umsetzungsschritte

1. Rote Backend-Tests: welche Ereignisse an welche Mitglieder (inkl. Erinnerung nur an Nicht-Abgeber), dann Dispatcher mit Fake-Sender.
2. FCM-Implementierung hinter dem Interface; Test mit gefaktem HTTP.
3. Device-Endpunkte und Migration per TDD.
4. Nachrichtenkatalog en/de mit Vollständigkeitstest.
5. App: Messaging-Service hinter Interface, Widget-/Unit-Tests für Token-Registrierung und Navigation bei Tipp.
6. Manueller Test auf Android gegen Staging (Notizen).
7. Doku aktualisieren (Firebase-Setup, Variablen).

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`backend/tests/`, `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Jedes Ereignis erreicht genau die richtigen Mitglieder; abgemeldete Geräte erhalten nichts.
- Erinnerung nur an Mitglieder ohne Abgabe; nicht doppelt bei Wiederholung des Jobs.
- Ungültiges Token wird nach FCM-Fehler gelöscht.
- Nachrichtentext enthält keinen Abgabetext (Test mit erfundenem Inhalt).
- App: Tipp öffnet den richtigen Raum; Einstellung aus → keine Registrierung.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Alle Tests grün, Definition of Done erfüllt.
- [ ] Auf einem Android-Gerät kommen gegen Staging alle Ereignisse einer Partie an (Notizen).
- [ ] Nachrichtenkatalog vollständig in en und de (Test).

## Offene Fragen / Annahmen

- iOS-Push braucht das Apple Developer Program (APNs-Schlüssel). Bis dahin nur Android.
- Annahme: Erinnerungszeitpunkt wie oben vorgeschlagen; bei Bedarf mit dem Nutzer abstimmen.

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
