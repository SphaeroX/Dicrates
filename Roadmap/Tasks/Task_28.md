# Task_28: Sicherheits- und Datenschutz-Review

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_28.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M6 Beta und Release

## Ziel

Vor dem öffentlichen Release ist systematisch geprüft und belegt, dass Rechte, Anonymität und Datenschutz halten: RLS auf allen Tabellen, eine vollständige Berechtigungsmatrix aller Endpunkte, keine bekannten verwundbaren Abhängigkeiten, keine Secrets im Repo, KI-Kennzeichnung überall. Die Unterlagen, die der Nutzer mit Anwalt und Anbietern braucht (AVVs, Verarbeitungsverzeichnis, Datenschutz-Folgenabschätzung, DSA-Meldeweg), liegen als Entwürfe vor.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 27 archiviert (Beta abgeschlossen, Funde behoben oder eingeplant).
- **Relevantes Vorwissen:** `docs/data-inventory.md`, `docs/architecture.md` (Privacy-Regeln), `docs/operations.md`, `docs/concept-original.de.md` Kapitel 17 (DSGVO, DSA, KI-Verordnung, Barrierefreiheitsstärkungsgesetz).

## Umfang

**Gehört dazu:**

- Automatischer Test, der alle Tabellen im Schema aufzählt und prüft, dass RLS aktiv ist und Clients keine fremden Zeilen sehen (Rollen `anon` und `authenticated`).
- Berechtigungsmatrix: jeder Endpunkt × (anonym, ohne Einwilligung, Nicht-Mitglied, Mitglied, gesperrt) als parametrisierter Test.
- Abhängigkeitsprüfung: Python (z. B. `uv run --with pip-audit pip-audit` oder vergleichbar im Projekt-Env), Dart (`flutter pub outdated` und bekannte Advisories), npm (`npm audit`); Funde beheben oder begründet akzeptieren.
- Secret-Scan in CI (z. B. gitleaks-Action) über die ganze Git-Historie.
- Prüfung von Eingabegrenzen, Ratenbegrenzung und Fehlermeldungen auf Informationslecks.
- Test, dass jede API-Antwort mit LLM-Inhalt ein Kennzeichen „KI-generiert" trägt und die App es anzeigt.
- Entwürfe in `docs/legal/`: Verzeichnis von Verarbeitungstätigkeiten, Datenschutz-Folgenabschätzung (Art. 35, politische Meinungen), AVV-Checkliste je Anbieter (Supabase, Mistral, Hosting, Firebase, Fehler-Tracking, SMTP), DSA-Kontaktstelle und Melde- und Abhilfeverfahren, Prüfliste Barrierefreiheitsstärkungsgesetz, Fragenliste für den Anwalt.

**Gehört nicht dazu:**

- Externer Penetrationstest (optional, Entscheidung des Nutzers), Unterzeichnung von Verträgen (Nutzer).

## Umsetzungsschritte

1. RLS-Aufzählungstest schreiben; Funde beheben.
2. Berechtigungsmatrix als parametrisierte Tests; Funde beheben.
3. Abhängigkeits- und Secret-Scans in CI aufnehmen; Funde bearbeiten.
4. KI-Kennzeichnungstest.
5. Rechts- und Datenschutzunterlagen als Entwürfe schreiben.
6. Ergebnisbericht `docs/security-review.md` mit Funden, Status und Restrisiken; dem Nutzer vorlegen.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`backend/tests/`, `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- RLS für jede Tabelle (Aufzählung aus dem Schema, damit neue Tabellen automatisch geprüft werden).
- Berechtigungsmatrix aller Endpunkte.
- KI-Kennzeichnung in API und App.
- CI-Jobs für Abhängigkeits- und Secret-Scan.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Alle neuen Tests grün, Definition of Done für alle Teile erfüllt.
- [ ] Abhängigkeits- und Secret-Scan laufen in CI ohne offene kritische Funde.
- [ ] `docs/security-review.md` und `docs/legal/` liegen vor; der Nutzer hat die Unterlagen erhalten.

## Offene Fragen / Annahmen

- **Nutzeraufgaben:** AVVs abschließen, Anwalt beauftragen, über externen Pentest entscheiden.
- Ob eine Datenschutz-Folgenabschätzung Pflicht ist, bewertet der Anwalt; der Entwurf wird vorsorglich erstellt.

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
