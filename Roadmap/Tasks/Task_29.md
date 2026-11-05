# Task_29: Öffentlicher Release

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_29.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M6 Beta und Release

## Ziel

Dicrates 1.0 ist öffentlich im Google Play Store (und im App Store, sofern das Apple-Konto existiert) verfügbar. Rechtstexte sind anwaltlich geprüft und live, die Produktionsumgebung besteht eine automatische Vorabprüfung, die Fragenbibliothek ist gefüllt, und ein Runbook beschreibt Betrieb, Moderation, Vorfälle und Datenschutzanfragen.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 28 archiviert (Review abgeschlossen); anwaltliche Freigabe der Rechtstexte (Nutzer).
- **Relevantes Vorwissen:** `docs/operations.md`, `docs/store.md`, `docs/security-review.md`, `docs/beta-report.md`, `docs/llm-eval/` (Bericht mit Produktionsmodell wiederholen, falls in Task 23 nur vorläufig).

## Umfang

**Gehört dazu:**

- Rechtstexte in die vom Anwalt freigegebene Fassung bringen, Entwurfshinweise entfernen, Einwilligungsversion erhöhen (bestehende Beta-Nutzer bestätigen neu).
- CLI `ops preflight`: prüft `APP_ENV=production`, `mistral:`-Modell, alle Pflicht-Secrets gesetzt, Migrationen aktuell, Backups/PITR aktiv, Watchdog und Alarme aktiv, Mindestanzahl freigegebener Fragen je Sprache (Vorschlag: 30), Fehler-Tracking ohne personenbezogene Daten.
- LLM-Evaluation aus Task 23 mit dem Produktionsmodell wiederholen, falls nötig.
- Runbook in `docs/operations.md` vervollständigen: Deploy und Rollback, Vorfälle, Moderationsroutine, Auskunfts- und Löschanfragen, Rotation von Keys, Kostenkontrolle.
- Release-Build (Version 1.0.0), Store-Einträge final, Produktions-Track bzw. App-Store-Einreichung vorbereiten. Das Absenden zur Prüfung macht der Nutzer.
- Website: Store-Links eintragen, Beta-Hinweise entfernen.
- README-Status aktualisieren, Git-Tag `v1.0.0`, Status in `Roadmap/README.md` auf „abgeschlossen".

**Gehört nicht dazu:**

- Phase-2-Funktionen (Matching, Rating, Web-Admin u. a.), Marketing.

## Umsetzungsschritte

1. `ops preflight` per TDD (jede Prüfung einzeln testbar, mit Fakes).
2. Rechtstexte final übernehmen; E2E-Tests der Website prüfen, dass kein Entwurfshinweis mehr vorhanden ist.
3. Einwilligungsversion erhöhen; Widget-Test für Neubestätigung.
4. Runbook vervollständigen.
5. Preflight gegen Produktion laufen lassen; alle Punkte grün (Ausgabe in Notizen).
6. Release-Build erzeugen, Store-Metadaten final hochladen (Nutzer reicht ein).
7. Nach Freigabe in den Stores: Website-Links, README, Tag, Roadmap-Status.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`backend/tests/`, `app/test/`, `website/tests/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Preflight: jede Prüfung meldet Erfolg und Fehler korrekt.
- Website-E2E: keine Entwurfshinweise, Store-Links vorhanden.
- App: neue Einwilligungsversion erzwingt Neubestätigung.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Alle Tests grün, Definition of Done für alle Teile erfüllt.
- [ ] `uv run dicrates-admin ops preflight` gegen Produktion ist vollständig grün (Ausgabe in Notizen).
- [ ] Die App ist im Play Store öffentlich verfügbar (Link in README und Website); iOS-Stand dokumentiert.
- [ ] `docs/operations.md` ist vollständig; Tag `v1.0.0` existiert.
- [ ] `Roadmap/README.md` meldet die Roadmap als abgeschlossen.

## Offene Fragen / Annahmen

- **Nutzeraufgaben:** anwaltliche Freigabe, Einreichung in den Stores, ggf. Apple-Konto.
- Wenn Store-Prüfungen Änderungen verlangen, werden diese als eigene Fixes mit reproduzierendem Test umgesetzt und hier notiert.

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
