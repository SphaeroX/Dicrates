# Task_27: Geschlossene Beta

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_27.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M6 Beta und Release

## Ziel

Echte Testgruppen (Freunde, Familie, Kollegen) spielen Dicrates über Play Internal Testing (und TestFlight, falls das Apple-Konto existiert) auf der Produktionsinfrastruktur mit Mistral. Die Beta liefert Kennzahlen (Abbruchrate je Runde, wahrgenommene Fairness, Überdenken vs. begründetes Festhalten, gefilterte und gemeldete Beiträge, Kosten pro Partie, Wiederkehr) und Feedback, aus dem der Nutzer entscheidet, was vor dem Release noch nötig ist.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Tasks 18 (Push), 21 (Beobachtung) und 26 (Store-Vorbereitung) archiviert.
- **Relevantes Vorwissen:** `docs/concept-original.de.md` Kapitel 19 (Erfolgskriterien), `docs/operations.md`, `docs/store.md`, Erkenntnisse aus Tasks 17 und 21.
- **Harte Voraussetzung:** produktiver Mistral-Key. Mit echten Nutzerdaten darf kein `google:`-Modell laufen.

## Umfang

**Gehört dazu:**

- Produktionsumgebung aufsetzen (zweites Supabase-Projekt bzw. Umgebung nach Entscheidung in Task 17), `APP_ENV=production`, Mistral-Modell, Migrationen, Fragenbestand übertragen.
- Eigenes SMTP für Supabase-Auth-Mails (EU-Anbieter, Absenderadresse; abhängig von Domain-Entscheidung) einrichten, da der Standardversand begrenzt ist.
- CI-Lane: Upload auf Play Internal Testing per fastlane; TestFlight, falls möglich.
- In-App „Feedback zur Beta" (allgemein, außerhalb einer Partie) mit Filter aus Task 12; sichtbar nur in Beta-Builds (Build-Konfiguration).
- CLI `stats beta [--since]`: Abbruchrate je Runde, Abschlussquote, Verteilung der Fairness-Antworten, Anteil Überarbeiten vs. „bleibe dabei", Anteil gefilterter und gemeldeter Beiträge, Kosten pro Partie, Räume pro Nutzer, Wiederkehr nach 7 Tagen; nur aggregiert, keine Einzeldaten.
- Leitfaden für Tester (`docs/beta.md`, en/de): Ablauf, Hinweis auf KI und Datenschutz, Feedback-Wege.
- Beta-Bericht nach Ende der Testphase (Dauer bestimmt der Nutzer): Kennzahlen, Feedback-Themen, Empfehlungen. Neue Tasks schlägt der Agent dem Nutzer vor; nach Zustimmung werden sie vor Task 28 eingefügt und alle folgenden Tasks umnummeriert (README-Tabelle anpassen).

**Gehört nicht dazu:**

- Öffentlicher Release (Task 29), große Funktionsänderungen ohne Zustimmung des Nutzers.

## Umsetzungsschritte

1. Rote Tests für die Kennzahlen-Berechnung (erfundene Daten) schreiben, dann `stats beta` umsetzen.
2. Beta-Feedback per TDD (Backend und App, Build-Schalter).
3. Produktionsumgebung einrichten (mit Nutzer: Keys, Projekte, SMTP); Preflight-Prüfung `APP_ENV`/Modell.
4. Upload-Lane einrichten und erste Version an Testgruppen verteilen (Nutzer lädt Tester ein).
5. Während der Beta: Monitoring aus Task 21 beobachten, kritische Fehler beheben (je Fehler zuerst ein reproduzierender Test).
6. Beta-Bericht in `docs/beta-report.md` schreiben und dem Nutzer vorlegen.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`backend/tests/`, `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Kennzahlen: jede Formel mit erfundenen Partien inkl. Abbrüchen und fehlenden Runden.
- Bericht enthält keine Einzeldaten (Test auf Mindestgruppengröße, z. B. erst ab 5 Partien).
- Beta-Feedback nur in Beta-Builds sichtbar; Freitext wird gefiltert.
- Preflight verweigert Start mit `google:`-Modell in Produktion (bestehende Tests).

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Alle Tests grün, Definition of Done erfüllt.
- [ ] Eine Beta-Version ist über Play Internal Testing an Testgruppen verteilt (Notizen mit Versionsnummer).
- [ ] `docs/beta-report.md` liegt vor; der Nutzer hat entschieden, welche Funde vor dem Release behoben werden.
- [ ] Beschlossene Zusatz-Tasks sind angelegt und einsortiert.

## Offene Fragen / Annahmen

- **Nutzeraufgaben:** Mistral-Key, Produktionsprojekt(e), SMTP-Anbieter, Tester einladen, Dauer der Beta.
- iOS-Beta nur mit Apple Developer Program.

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
