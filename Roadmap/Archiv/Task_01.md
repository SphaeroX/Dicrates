# Task_01: Backend-Skelett + CI

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_01.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M1 Fundament

## Ziel

Das Backend wird zum lauffähigen FastAPI-Dienst mit typisierten Einstellungen und einem Health-Endpunkt, und jeder Push prüft es automatisch in GitHub Actions. Damit stehen Paketstruktur, Settings-Validierung (inklusive Produktionssperre für Nicht-Mistral-Modelle) und CI, auf denen alle weiteren Backend-Tasks aufbauen.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Keine. Erster Task.
- **Relevantes Vorwissen:** `docs/architecture.md` (Stack, Environment, LLM-Regeln zu `LLM_MODEL`), `docs/code-style.md` (pyright strict, ruff), `docs/testing.md` (Befehle, Settings-Tests), `docs/conventions.md` (Organisation nach Feature, `core`-Paket), `backend/pyproject.toml` (`package = false`, `testpaths = ["tests"]`, Marker `integration` und `llm`), `.env.example`. `backend/src/` und `backend/tests/` enthalten bisher nur `.gitkeep`.

## Umfang

**Gehört dazu:**

- Laufzeit-Abhängigkeiten per `uv add`: `fastapi`, `uvicorn`, `pydantic-settings`; Test-Abhängigkeit `httpx` (für den FastAPI-TestClient) per `uv add --dev`.
- Paketstruktur unter `backend/src/` (Vorschlag: `src/dicrates/` mit `core/` und später Feature-Paketen), App-Factory und `GET /health`.
- `core/settings.py` mit `pydantic-settings`: liest die Root-`.env`, parst `LLM_MODEL` (`<provider>:<model>`), `APP_ENV` (`development`/`production`), Supabase- und DB-Variablen; verweigert bei `APP_ENV=production` jedes Modell, das nicht mit `mistral:` beginnt.
- GitHub-Actions-Workflow `.github/workflows/backend.yml`: uv installieren, `uv sync`, `ruff check`, `ruff format --check`, `pyright`, `pytest -m "not integration and not llm"`; Auslöser bei Änderungen unter `backend/**`.
- Kurze Begründung je neuer Laufzeit-Abhängigkeit in `docs/architecture.md`.

**Gehört nicht dazu:**

- Datenbank, Procrastinate, Supabase (Task 02), Auth (Task 04), LLM-Aufrufe (Task 05), Docker und Deployment (Task 17).

## Umsetzungsschritte

1. Roten Test für `GET /health` schreiben (Status 200, JSON mit `status` und `version`), dann App-Factory und Route bauen.
2. Rote Settings-Tests schreiben (gültige/ungültige `LLM_MODEL`-Strings, Produktionssperre), dann `core/settings.py` umsetzen.
3. Entscheiden, wie pytest und pyright den Code unter `src/` finden (z. B. `pythonpath` in der pytest-Konfiguration, da `package = false`), und in `docs/architecture.md` bzw. `docs/testing.md` dokumentieren.
4. Einen Start-Befehl für die lokale Entwicklung festlegen (z. B. `uv run uvicorn dicrates.main:app --reload`) und in `docs/testing.md`/README ergänzen.
5. `.github/workflows/backend.yml` anlegen und lokal die gleichen Befehle grün laufen lassen.
6. `docs/architecture.md` aktualisieren (Abhängigkeiten, Paketstruktur), Abschnitt „First implementation steps" entsprechend kürzen.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (hier `backend/tests/`, Struktur spiegelt `src/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- `GET /health` liefert 200 und das erwartete JSON.
- `LLM_MODEL=mistral:mistral-large-latest` wird in Provider und Modell zerlegt; ein String ohne `:` erzeugt einen Validierungsfehler.
- `APP_ENV=production` mit `google:…` wird abgewiesen, mit `mistral:…` akzeptiert; `APP_ENV=development` akzeptiert beide.
- Settings-Tests setzen Umgebungsvariablen über Fixtures (`monkeypatch`), nie über die echte `.env`.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [x] `uv run pytest` in `backend/` ist grün und enthält Health- und Settings-Tests.
- [x] `uv run ruff check .`, `uv run ruff format --check .` und `uv run pyright` laufen fehlerfrei.
- [x] Der Workflow `backend.yml` läuft auf einem Push oder PR grün.
- [x] Lokal liefert `curl http://127.0.0.1:8000/health` nach dem dokumentierten Start-Befehl Status 200.
- [x] `docs/architecture.md` nennt jede neue Laufzeit-Abhängigkeit mit Begründung.

## Offene Fragen / Annahmen

- Annahme: Paketname `dicrates` unter `backend/src/`. Wenn eine andere Struktur besser zu `package = false` passt, Entscheidung in `Roadmap/README.md` festhalten.
- Annahme: Supabase- und DB-Variablen sind in Task 01 optional (Default `None`) und werden erst in den Tasks Pflicht, die sie brauchen, damit `/health` ohne Datenbank startet.

## Notizen zu diesem Task

Taskspezifische Informationen während der Arbeit hier festhalten. Taskübergreifendes gehört in `Roadmap/README.md`.

## Abschluss-Checkliste

Reihenfolge und Details stehen in `AGENTS.md`, Abschnitt "Abschluss- und Archivierungs-Workflow".

- [x] Alle Akzeptanzkriterien erfüllt, Tests liegen permanent in den Test-Suites der Teile und laufen grün
- [x] Definition of Done aus `docs/testing.md` erfüllt und betroffene Dateien in `docs/` aktualisiert
- [x] Abschnitt "Erkenntnisse für Folge-Agenten" unten ausgefüllt
- [x] Folge-Tasks und `Roadmap/README.md` geprüft und bei Bedarf angepasst
- [x] Datei ohne `RUN_` nach `Roadmap/Archiv/` verschoben

## Erkenntnisse für Folge-Agenten

Vor der Archivierung vom Agenten auszufüllen. Schreibe so, dass ein Agent, der diesen Task nie gesehen hat, davon bei späteren Tasks profitiert:

- **Umgesetzt (und Abweichungen vom Plan):** Paket `backend/src/dicrates/` mit `main.py` (App-Factory `create_app()`, Modul-`app`, `GET /health` → `{"status":"ok","version":"0.1.0"}`), `core/settings.py` (`Settings`, `LlmModel`, `AppEnv`, `get_settings()`), Workflow `.github/workflows/backend.yml`. Abweichung: Test-Abhängigkeit ist `httpx2` statt `httpx`, weil Starlette 1.x `httpx` für den `TestClient` als deprecated markiert und pyright sonst die TestClient-Typen nicht auflöst.
- **Learnings & Stolpersteine:** Bei pydantic-settings werden komplexe Feldtypen aus Env-Variablen als JSON dekodiert; `LLM_MODEL` ist deshalb mit `Annotated[LlmModel, NoDecode]` plus `field_validator(mode="before")` umgesetzt. `.env.example` liefert leere Strings – leere Supabase-/DB-Werte werden zu `None`. Unter Windows schlug `uv remove` mehrfach mit „Zugriff verweigert" auf `*.dist-info/licenses` fehl; Ordner per PowerShell `Remove-Item -Recurse -Force` löschen, dann `uv sync`. Python-`write_text` unter Windows schreibt CRLF – Dateien mit `newline="
"` schreiben oder nachträglich normalisieren (Repo erzwingt LF).
- **Wichtige Entscheidungen und ihre Gründe:** Kein installiertes Paket (`package = false` bleibt): pytest nutzt `pythonpath = ["src"]`, pyright `extraPaths = ["src"]`, uvicorn `--app-dir src`. pytest läuft mit `--import-mode=importlib`, damit Testordner kein `__init__.py` brauchen. Secrets in den Settings sind `SecretStr` (tauchen nicht in `repr` auf). Version steht in `dicrates/__init__.py`.
- **Auswirkungen auf Folge-Tasks:** Neue Settings-Felder einfach in `Settings` ergänzen; Pflichtfelder erst in dem Task scharf schalten, der sie braucht (z. B. `database_url` in Task 02 für DB-Code). App-Code holt Settings über `get_settings()` (lru_cache) – in Tests per FastAPI-Dependency-Override oder `Settings(_env_file=None)` ersetzen.
- **Hinweise zu Tests und Befehlen:** Start lokal: `uv run uvicorn dicrates.main:app --reload --app-dir src` (in `backend/`), dann `curl http://127.0.0.1:8000/health` → 200 (geprüft). Settings-Tests löschen relevante Env-Vars per autouse-Fixture und bauen `Settings(_env_file=None)`.
