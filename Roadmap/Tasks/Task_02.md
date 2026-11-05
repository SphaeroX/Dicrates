# Task_02: Lokales Supabase, DB und Jobs

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_02.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M1 Fundament

## Ziel

Es gibt einen lokalen Supabase-Stack mit versionierten Migrationen, das Backend spricht mit Postgres, und ein Procrastinate-Worker führt Jobs aus. Integrationstests laufen lokal und in CI. Das ist das Fundament für den Zustandsautomaten der Runden (Task 10) und alle Tabellen danach.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 01 archiviert (Settings, Paketstruktur, Backend-CI).
- **Relevantes Vorwissen:** `docs/architecture.md` (Procrastinate statt Redis, gleiche Transaktion für Job und Zustandswechsel; Abschnitt „First implementation steps": `npx supabase init`, `npx supabase start`, Docker nötig), `docs/conventions.md` (Tabellen `snake_case` im Plural, Migrationen nur in `supabase/migrations/`), `docs/testing.md` (Marker `integration`). Ein Supabase-Cloud-Projekt existiert bereits (`.env`), wird hier aber nicht verändert.

## Umfang

**Gehört dazu:**

- `npx supabase init` im Repo-Root (Supabase CLI per `npx`, keine globale Installation); `supabase/` ins Repo, lokale Secrets bleiben git-ignored.
- Erste Migration: Tabelle `profiles` (`id` = `auth.users.id`, `pseudonym`, `language`, `created_at`) mit aktivierter RLS; Clients dürfen nur das eigene Profil lesen.
- DB-Zugriff im Backend (`core/db`): Bibliothek wählen (Vorschlag: `psycopg` 3 async mit Connection-Pool und plain SQL, da Procrastinate ebenfalls psycopg nutzt) und in `docs/architecture.md` begründen.
- Procrastinate per `uv add`: App-Objekt, Worker-Startbefehl, Procrastinate-Schema als Migration in `supabase/migrations/` (generiert über das Procrastinate-CLI), ein Beispiel-Job (`ping`), der beweist, dass Enqueue und Ausführung funktionieren.
- Test-Infrastruktur: Fixtures für Integrationstests gegen den lokalen Stack (Transaktion pro Test mit Rollback oder frische Schema-Kopie), Unit-Tests mit Procrastinates In-Memory-Connector.
- CI-Job für Integrationstests (Supabase CLI in GitHub Actions, z. B. `supabase/setup-cli`, `supabase start`, Migrationen anwenden, `pytest -m integration`).

**Gehört nicht dazu:**

- Auth und Token-Prüfung (Task 04), Spieltabellen (ab Task 06), Migrationen in die Cloud (Task 17).

## Umsetzungsschritte

1. `npx supabase init`, lokalen Stack starten, Ergebnis und Docker-Voraussetzung in `docs/architecture.md`/`docs/testing.md` festhalten.
2. Roten Integrationstest für DB-Verbindung schreiben, `core/db` umsetzen, `DATABASE_URL` aus den Settings nutzen.
3. Migration `profiles` mit RLS schreiben; roten Test „Client mit anon/authenticated-Rolle sieht fremde Profile nicht" schreiben und grün machen.
4. Procrastinate einbinden, Schema-Migration erzeugen, Beispiel-Job mit Unit- und Integrationstest.
5. Worker-Startbefehl festlegen (z. B. `uv run procrastinate --app=dicrates.jobs.app worker`) und dokumentieren.
6. CI-Job für Integrationstests ergänzen.
7. `.env.example` prüfen (lokale `DATABASE_URL` als Beispiel kommentieren), Doku aktualisieren.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (hier `backend/tests/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Integration: Verbindung zur lokalen DB, einfache Abfrage.
- Integration: RLS auf `profiles` (eigene Zeile lesbar, fremde nicht; anon sieht nichts).
- Unit: Job wird enqueued und mit In-Memory-Connector ausgeführt.
- Integration: Job läuft über den echten Postgres-Connector.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] `npx supabase start` und `npx supabase db reset` laufen mit allen Migrationen fehlerfrei.
- [ ] `uv run pytest -m integration` ist mit laufendem lokalen Stack grün; `uv run pytest -m "not integration and not llm"` läuft ohne Stack.
- [ ] Der CI-Job für Integrationstests ist grün.
- [ ] Der Worker startet mit dem dokumentierten Befehl und führt den Beispiel-Job aus.
- [ ] `docs/architecture.md` und `docs/testing.md` beschreiben DB-Bibliothek, Worker-Start und Integrationstest-Setup.

## Offene Fragen / Annahmen

- Annahme: psycopg 3 statt ORM. Falls ein ORM (z. B. SQLAlchemy) klar besser passt, begründen und in `Roadmap/README.md` festhalten.
- Lokale Ports von Supabase können mit anderen Diensten kollidieren; in Notizen festhalten, falls angepasst.

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
