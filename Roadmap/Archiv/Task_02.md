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

- [x] `npx supabase start` und `npx supabase db reset` laufen mit allen Migrationen fehlerfrei. (Belegt in CI: `supabase start` wendet alle Migrationen an; lokal mangels Docker noch nicht ausgeführt.)
- [x] `uv run pytest -m integration` ist mit laufendem lokalen Stack grün (in CI, 8 passed); `uv run pytest -m "not integration and not llm"` läuft ohne Stack.
- [x] Der CI-Job für Integrationstests ist grün.
- [x] Der Worker startet mit dem dokumentierten Befehl und führt den Beispiel-Job aus.
- [x] `docs/architecture.md` und `docs/testing.md` beschreiben DB-Bibliothek, Worker-Start und Integrationstest-Setup.

## Offene Fragen / Annahmen

- Annahme: psycopg 3 statt ORM. Falls ein ORM (z. B. SQLAlchemy) klar besser passt, begründen und in `Roadmap/README.md` festhalten.
- Lokale Ports von Supabase können mit anderen Diensten kollidieren; in Notizen festhalten, falls angepasst.

## Notizen zu diesem Task

Taskspezifische Informationen während der Arbeit hier festhalten. Taskübergreifendes gehört in `Roadmap/README.md`.

- Docker ist auf dem Entwicklungsrechner (Windows) nicht installiert; die Installation per `winget install Docker.DockerDesktop` scheiterte an der fehlenden Admin-Bestätigung (UAC), WSL2 fehlt ebenfalls. Der Nutzer muss Docker Desktop (inkl. `wsl --install`) selbst mit Admin-Rechten installieren. Bis dahin sind alle Integrationstests im CI-Job `integration` verifiziert (8 passed, Worker-Smoke-Test grün); lokal werden sie übersprungen.
- Ports: Standardports aus `supabase/config.toml` (API 54321, DB 54322, Studio 54323) unverändert.

## Abschluss-Checkliste

Reihenfolge und Details stehen in `AGENTS.md`, Abschnitt "Abschluss- und Archivierungs-Workflow".

- [x] Alle Akzeptanzkriterien erfüllt, Tests liegen permanent in den Test-Suites der Teile und laufen grün
- [x] Definition of Done aus `docs/testing.md` erfüllt und betroffene Dateien in `docs/` aktualisiert
- [x] Abschnitt "Erkenntnisse für Folge-Agenten" unten ausgefüllt
- [x] Folge-Tasks und `Roadmap/README.md` geprüft und bei Bedarf angepasst
- [x] Datei ohne `RUN_` nach `Roadmap/Archiv/` verschoben

## Erkenntnisse für Folge-Agenten

Vor der Archivierung vom Agenten auszufüllen. Schreibe so, dass ein Agent, der diesen Task nie gesehen hat, davon bei späteren Tasks profitiert:

- **Umgesetzt (und Abweichungen vom Plan):** `supabase/` (per `npx supabase init`, CLI 3.0.0), Migrationen `20261105140000_procrastinate_schema.sql` (generiert, plus RLS/REVOKE für `anon`/`authenticated` auf Tabellen, Sequenzen und Funktionen) und `20261105140100_profiles.sql` (RLS, nur eigenes Profil lesbar, keine Client-Schreibrechte). `dicrates/core/db.py` (`create_pool`), `dicrates/jobs/` (Procrastinate-App, Job `ping`). CI-Job `integration` mit `supabase/setup-cli`, `supabase start`, `pytest -m integration` und Worker-Smoke-Test. **Abweichung:** Das Backend ist jetzt ein installiertes Paket (`uv_build`, `module-name = "dicrates"`) statt `package = false`, weil der Procrastinate-CLI-Loader und das spätere `dicrates-admin` (Task 06, Console-Script) `dicrates` importieren müssen. `pythonpath`/`extraPaths`/`--app-dir src` aus Task 01 sind dadurch entfallen. Ein FastAPI-Lifespan mit DB-Pool wurde bewusst noch nicht gebaut (kein Endpunkt braucht ihn); kommt mit dem ersten DB-Endpunkt in Task 04.
- **Learnings & Stolpersteine:** psycopg async läuft unter Windows nicht auf der Proactor-Event-Loop; `tests/conftest.py` registriert dafür den pytest-asyncio-Hook `pytest_asyncio_loop_factories` – **nur unter Windows**, weil der Hook immer eine nicht-leere Map liefern muss (sonst UsageError in CI). Gleiches Problem gilt für uvicorn/Worker unter Windows, sobald sie die DB nutzen (dort ggf. `--loop` bzw. Selector-Loop setzen). Der Procrastinate-App-Pfad für `--app` ist `dicrates.jobs.app.app` (Objekt, nicht Modul). Procrastinate loggt Job-Argumente auf INFO (`ping[2](message='ci')`).
- **Wichtige Entscheidungen und ihre Gründe:** psycopg 3 + plain SQL statt ORM (gleicher Treiber wie Procrastinate, Transaktion teilbar, RLS/Locks explizit). Procrastinate-Tabellen bleiben im `public`-Schema (CLI-Standard), sind aber für Client-Rollen komplett gesperrt. Integrationstests: eine Transaktion pro Test mit Rollback; lokal Skip, wenn keine DB erreichbar, in CI (`DICRATES_REQUIRE_DB=1`) Fehler.
- **Auswirkungen auf Folge-Tasks:** Jede neue Tabelle in `public` braucht RLS + explizite Grants (Data API!). Job-Argumente nur IDs, nie Texte. Task 04 baut den Lifespan/Pool-Dependency in `main.py` und muss für den Windows-Dev-Server die Selector-Loop beachten. Task 10 (Zustandsautomat) kann Job-Enqueue und Zustandswechsel in derselben psycopg-Transaktion machen (`defer_async` mit dem Connector der App; ggf. Procrastinate-Doku zu „transaction" prüfen).
- **Hinweise zu Tests und Befehlen:** `uv run pytest -m integration` (Stack nötig), `uv run procrastinate --app=dicrates.jobs.app.app worker` (Worker), `--one-shot` beendet nach leerer Queue. Schema neu erzeugen: `uv run procrastinate schema --read`.
