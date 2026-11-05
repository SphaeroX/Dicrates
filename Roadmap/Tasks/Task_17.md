# Task_17: Hosting-Entscheidung und Staging-Deployment

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_17.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M4 Betrieb und Erreichbarkeit

## Ziel

Für API und Worker ist ein EU-Hosting gewählt, das der Nutzer bestätigt hat. Beide laufen als Container in einer Staging-Umgebung mit eigenem Supabase-Projekt, werden bei jedem Merge auf `main` automatisch ausgerollt, und Migrationen landen kontrolliert in der Cloud. Ab hier kann die App gegen einen echten Server getestet werden.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 16 archiviert (komplettes Kernspiel lokal lauffähig).
- **Relevantes Vorwissen:** `docs/architecture.md` (EU-Hosting, Supabase EU, Settings-Sperre für Nicht-Mistral in Produktion), `.env.example`, Erkenntnisse aus Task 02 (Worker-Start, Migrationen). Ein Supabase-Cloud-Projekt existiert bereits.

## Umfang

**Gehört dazu:**

- Vergleich von mindestens drei EU-Optionen (z. B. Fly.io Frankfurt, Scaleway, Hetzner mit Docker Compose, Google Cloud Run europe-west3) nach EU-Standort und AVV, Kosten für API plus dauerhaft laufenden Worker, Deploy-Aufwand, Logs, Secrets, Skalierung. Kurzer Entscheidungsvorschlag in `docs/architecture.md`.
- **Anhalten und Nutzer fragen**, bevor eine Option umgesetzt wird.
- `backend/Dockerfile` (mehrstufig, uv, ohne Root-Rechte), Prozesse für API und Worker.
- Umgebungen: Staging jetzt, Produktion vorbereitet (Task 29). Entscheidung, ob das bestehende Supabase-Projekt Staging oder Produktion wird; zweites Projekt anlegen lassen (Nutzeraufgabe).
- GitHub-Actions-Workflow: Image bauen, auf Staging ausrollen, Migrationen per Supabase CLI anwenden, danach Smoke-Test gegen `/health`.
- Secrets im Hosting bzw. in GitHub-Environments, nie im Repo.
- App: Build-Konfiguration für Staging (`--dart-define`-Datei oder Flavor), dokumentierter Befehl.
- Fragenbestand nach Staging übertragen (Export/Import-Befehl im CLI).

**Gehört nicht dazu:**

- Produktions-Go-Live (Task 29), Monitoring und Alarme (Task 21), eigene Domain.

## Umsetzungsschritte

1. Vergleich recherchieren und dokumentieren; Nutzer entscheiden lassen; Entscheidung in `Roadmap/README.md` eintragen.
2. Dockerfile per Test absichern (CI baut das Image; Container startet und antwortet auf `/health`).
3. Deploy-Workflow für Staging anlegen; Secrets einrichten (Nutzer hilft bei Konten).
4. Migrationen auf das Staging-Supabase anwenden; RLS-Tests gegen Staging einmal manuell laufen lassen.
5. Export/Import für Fragen per TDD.
6. App-Staging-Build dokumentieren und auf einem Android-Gerät einen Durchlauf machen (Notizen).
7. `docs/architecture.md` und `.env.example` aktualisieren (neue Variablen wie `API_BASE_URL` je Umgebung).

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (hier `backend/tests/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- CI-Job baut das Image und startet einen Container-Smoke-Test.
- Export/Import der Fragen: Rundlauf ergibt identische Daten; Import überspringt Duplikate.
- Settings: `APP_ENV=production` verweigert `google:`-Modelle (bestehender Test bleibt grün).

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Hosting-Entscheidung des Nutzers ist in `docs/architecture.md` und `Roadmap/README.md` dokumentiert.
- [ ] Ein Merge auf `main` rollt Staging aus; der Smoke-Test gegen `/health` ist grün.
- [ ] Ein vollständiger Spielablauf läuft auf Staging (verkürzte Rundendauer, erfundene Texte, Gemini nur mit Testdaten oder Mistral).
- [ ] Keine Secrets im Repo (CI-Check oder manueller Vermerk).

## Offene Fragen / Annahmen

- **Rückfrage an den Nutzer:** Hosting-Anbieter (Pflicht vor der Umsetzung).
- Zweites Supabase-Projekt: Kosten und Anlage durch den Nutzer.
- Ohne eigene Domain läuft die API unter der Plattform-Domain; Umzug in Task 26/29, falls eine Domain kommt.

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
