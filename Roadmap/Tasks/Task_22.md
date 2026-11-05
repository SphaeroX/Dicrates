# Task_22: Löschung, Datenexport und Löschfristen

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_22.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M5 Datenschutz und Qualität

## Ziel

Nutzer können ihr Konto samt Beiträgen löschen, ihre Daten exportieren und die Einwilligung widerrufen. Klartext-Beiträge werden nach einer festen Frist nach Partieende automatisch gelöscht oder anonymisiert, dauerhaft bleibt nur, was für Punkte und Statistik nötig ist. Damit ist das Löschkonzept für politische Meinungen (DSGVO Art. 9) technisch umgesetzt.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 16 archiviert (alle Datentabellen des Spiels existieren); Tasks 18 und 20 (Geräte-Tokens, Meldungen, Sanktionen).
- **Relevantes Vorwissen:** `docs/architecture.md` (Art.-9-Daten, Löschung), `docs/concept-original.de.md` Kapitel 17 (Löschkonzept), alle Migrationen in `supabase/migrations/` (Liste der personenbezogenen Tabellen erstellen).

## Umfang

**Gehört dazu:**

- Inventar aller personenbezogenen Daten (Tabelle, Feld, Zweck, Löschregel) in `docs/data-inventory.md`; Grundlage für Datenschutzerklärung (Task 25) und Review (Task 28).
- `DELETE /me`: löscht Profil, Einwilligungen, Abgaben, Feedback, Geräte-Tokens, Meldungen des Nutzers und den Supabase-Auth-Nutzer (Admin-API). In laufenden Partien wird das Mitglied als ausgetreten markiert; seine Inhalte fließen in keine weitere Zusammenfassung ein. Bestehende Zusammenfassungen bleiben (aggregiert, ohne Personenbezug).
- Sanktionsdaten: Umgang festlegen (z. B. gehashte Sperrliste gegen Wiederanmeldung), mit dem Nutzer abstimmen.
- `GET /me/export`: maschinenlesbares JSON aller eigenen Daten.
- Widerruf der Einwilligung = Löschung der Meinungsdaten bzw. des Kontos (Ablauf mit dem Nutzer abstimmen).
- Löschfristen-Job: N Tage nach `FINISHED`/`ABORTED` werden Klartexte (Abgaben, Freitexte) gelöscht; Punkte, Zusammenfassungen und anonyme Kennzahlen bleiben; Raum geht nach `ARCHIVED`.
- App: „Konto löschen" mit Bestätigung, „Meine Daten exportieren" (Datei teilen), „Einwilligung widerrufen".

**Gehört nicht dazu:**

- Rechtstexte (Task 25), juristische Bewertung der Fristen (Task 28).

## Umsetzungsschritte

1. Datenschutz-Inventar erstellen.
2. Rote Integrationstests für `DELETE /me` (alle Tabellen leer für den Nutzer, laufende Partie läuft weiter) schreiben, dann umsetzen.
3. Export per TDD (vollständig, nur eigene Daten).
4. Löschfristen-Job per TDD mit injizierter Uhr.
5. App-Screens per Widget-Tests und Goldens.
6. Ein Test, der jede Tabelle mit Nutzerbezug kennt und fehlschlägt, wenn eine neue Tabelle ohne Löschregel hinzukommt.
7. Doku aktualisieren.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`backend/tests/`, `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Nach `DELETE /me` existieren keine Zeilen mit der Nutzer-ID mehr (außer dokumentierten Ausnahmen); Auth-Nutzer ist gelöscht (Fake der Admin-API).
- Laufende Partie nach Austritt: Hooks ignorieren die Inhalte des Ausgetretenen.
- Export enthält alle eigenen Daten und nichts Fremdes.
- Löschfristen-Job entfernt Klartexte genau nach N Tagen, Punkte bleiben.
- Schutztest gegen neue Tabellen ohne Löschregel.
- App: Bestätigungsdialog, Export teilen; Goldens.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Alle Tests grün, Definition of Done erfüllt.
- [ ] `docs/data-inventory.md` listet jede personenbezogene Tabelle mit Zweck und Löschregel.
- [ ] Löschung und Export wurden auf Staging mit einem Testkonto end to end durchgeführt (Notizen).

## Offene Fragen / Annahmen

- **Rückfrage an den Nutzer:** Länge der Frist N für Klartexte (Vorschlag: 30 Tage nach Partieende, damit Einsprüche möglich bleiben).
- **Rückfrage an den Nutzer:** Umgang mit Sanktionen nach Kontolöschung (Schutz vor Umgehung vs. Datensparsamkeit).

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
