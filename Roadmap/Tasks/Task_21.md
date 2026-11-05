# Task_21: Beobachtung und Schutz im Betrieb

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_21.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M4 Betrieb und Erreichbarkeit

## Ziel

Der Betrieb ist beobachtbar, ohne die Privatsphäre zu verletzen: strukturierte Logs ohne Inhalte, Fehler-Tracking in der EU, Ratenbegrenzung, Erkennung hängender Räume und fehlgeschlagener Jobs, LLM-Kosten pro Partie mit Schwellwert-Alarm sowie geprüfte Backups. Probleme in der Beta fallen auf, bevor Nutzer sie melden.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 17 archiviert (Staging-Betrieb, Hosting-Plattform).
- **Relevantes Vorwissen:** Root-`AGENTS.md` Regel 4 (keine Texte, Transkripte oder E-Mails loggen), `docs/architecture.md` (keine LLM-Telemetrie, keine Drittempfänger ohne AVV), Logging-Schutz aus Task 11, `llm_calls` aus Task 05, Hook-Fehlerpfade aus Tasks 13–16.

## Umfang

**Gehört dazu:**

- Strukturiertes JSON-Logging im Backend mit zentralem Schwärzungsfilter (Felder wie `text`, `reasoning`, `email`, `transcript`, Request-Bodies).
- Fehler-Tracking: EU-Option wählen (z. B. Sentry EU-Region oder selbst gehostetes GlitchTip), ohne personenbezogene Daten und Request-Bodies; Entscheidung begründen und den Nutzer vor Vertragsabschluss fragen (neuer Auftragsverarbeiter). App-Crash-Reporting nur mit derselben Schwärzung oder gar nicht.
- Ratenbegrenzung für schreibende Endpunkte je Nutzer (Bibliothek oder Postgres-basiert, begründen) mit 429-Antwort und App-Hinweis.
- Job `ops_watchdog`: Räume, deren Frist überschritten ist, ohne Übergang; fehlgeschlagene Procrastinate-Jobs; Alarm (Kanal festlegen, z. B. E-Mail oder Push an Betreiber).
- CLI `ops stuck-rooms`, `ops retry <job>`, `stats costs [--since]` (Kosten je Partie und Aufgabe aus `llm_calls`), Alarm bei Kosten über Schwellwert.
- Uptime-Check auf `/health` (Plattform-Feature oder externer EU-Dienst).
- Backups: Supabase-Plan und Point-in-Time-Recovery prüfen, Wiederherstellung einmal auf Staging testen (mit Nutzer).

**Gehört nicht dazu:**

- Produkt-Analytics über Kennzahlen hinaus (Beta-Kennzahlen in Task 27), LLM-Telemetrie (verboten).

## Umsetzungsschritte

1. Roten Test „Log enthält keine geschwärzten Felder" schreiben, Logging-Konfiguration umsetzen.
2. Ratenbegrenzung per TDD.
3. Watchdog-Erkennung per TDD (Uhr injizieren).
4. Kosten-Auswertung und Schwellwert-Alarm per TDD.
5. Fehler-Tracking-Option vorschlagen, Nutzer entscheiden lassen, Integration mit Test der Schwärzung (`before_send`).
6. Uptime-Check und Backup-Test einrichten bzw. dokumentieren.
7. `docs/operations.md` (Runbook: Alarme, Reaktion, Wiederherstellung) und `docs/architecture.md` aktualisieren.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`backend/tests/`, `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Schwärzungsfilter entfernt alle definierten Felder, auch verschachtelt und in Ausnahmen.
- Ratenbegrenzung: Grenze überschritten → 429; nach Ablauf wieder erlaubt.
- Watchdog findet hängende Räume und ignoriert gesunde.
- Kostenbericht summiert korrekt; Alarm feuert über Schwellwert.
- Fehler-Tracking-Hook entfernt Bodies und Nutzerdaten.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Alle Tests grün, Definition of Done erfüllt.
- [ ] Ein absichtlich ausgelöster Fehler auf Staging erscheint im Fehler-Tracking ohne personenbezogene Daten (Notizen).
- [ ] Wiederherstellung aus Backup auf Staging einmal durchgeführt oder als Nutzeraufgabe mit Anleitung dokumentiert.
- [ ] `docs/operations.md` enthält Runbook für Alarme.

## Offene Fragen / Annahmen

- **Rückfrage an den Nutzer:** Fehler-Tracking-Anbieter (neuer Auftragsverarbeiter) und Alarmkanal.
- Kosten-Schwellwert pro Partie: Vorschlag aus den Messungen der Tasks 16 und 23 ableiten.

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
