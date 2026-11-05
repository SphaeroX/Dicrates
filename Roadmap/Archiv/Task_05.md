# Task_05: LLM-Schicht

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_05.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M1 Fundament

## Ziel

Es gibt genau ein Backend-Modul, das alle LLM-Aufrufe besitzt: Modell-Factory aus `LLM_MODEL`, versionierte Prompt-Dateien, strukturierte und validierte Ausgaben, Retries, Kosten- und Nutzungsprotokoll ohne Klartext und ein Gerüst für echte LLM-Evaluationen. Alle späteren LLM-Aufgaben (Fragen, Filter, Zusammenfassungen, Bewertung) bauen nur noch Agents und Prompts darauf.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 02 archiviert (DB für das Nutzungsprotokoll; Task 01 für Settings).
- **Relevantes Vorwissen:** `docs/architecture.md` → LLM (Pydantic AI, `pydantic-ai-slim[mistral,google]`, keine Provider-SDKs direkt, keine Zwischenhändler, keine LLM-Telemetrie, Prompt-Version speichern), `docs/testing.md` (`TestModel`/`FunctionModel`, `models.ALLOW_MODEL_REQUESTS = False` in `conftest.py`, Marker `llm`), `docs/conventions.md` (Prompts als Dateien `name.vN.*`).

## Umfang

**Gehört dazu:**

- `uv add "pydantic-ai-slim[mistral,google]"`.
- Feature-Paket `llm`: Factory, die aus `Settings.llm_model` ein Pydantic-AI-Modell baut und injizierbar macht; Fehler bei unbekanntem Provider.
- Prompt-Registry: Dateien unter `llm/prompts/` (z. B. `group_picture.v1.md`), Laden nach Name und Version, Parameter (u. a. Raumsprache), Fehler bei fehlender Datei.
- Ausführungs-Wrapper: führt einen Agent mit `output_type` aus, nutzt Output-Retries bei Validierungsfehlern und begrenzte Retries bei Netzwerk- oder Ratenfehlern, liefert Ergebnis plus Metadaten (Prompt-Version, Modell).
- Nutzungsprotokoll: Tabelle `llm_calls` (Migration) mit Aufgabe, Prompt-Version, Modell, Token ein/aus, Dauer, Erfolg, optional `room_id`, **ohne** Prompt- oder Antworttext.
- `backend/tests/conftest.py` setzt `ALLOW_MODEL_REQUESTS = False`.
- Eval-Gerüst: Ordner für Real-LLM-Checks mit Marker `llm` und ein Admin-Befehl oder Test „LLM-Ping", der manuell gegen das konfigurierte Modell läuft.

**Gehört nicht dazu:**

- Konkrete Prompts für Fragen, Filter, Zusammenfassungen und Bewertung (Tasks 07, 08, 12–16), Qualitäts- und Bias-Suite (Task 23).

## Umsetzungsschritte

1. Rote Tests für die Factory (Mistral- und Google-String, unbekannter Provider) schreiben, dann umsetzen.
2. Prompt-Registry per TDD.
3. Wrapper per TDD mit `FunctionModel` (erst ungültige, dann gültige Ausgabe → Erfolg nach Retry; dauerhaft ungültig → definierter Fehler).
4. Migration `llm_calls` und Protokollierung per TDD; Test, dass keine Textfelder gespeichert werden.
5. `conftest.py` mit Request-Sperre.
6. LLM-Ping mit Marker `llm`; mit Gemini und erfundenem Text manuell ausprobieren (Mistral-Key fehlt noch).
7. `docs/architecture.md` (Modulaufbau, Prompt-Dateiformat) und `docs/testing.md` (Eval-Ordner) aktualisieren.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (hier `backend/tests/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Factory: korrekte Modellklasse je Provider, Fehler bei unbekanntem Provider.
- Registry: lädt Version, setzt Parameter ein, Fehler bei fehlender Version.
- Wrapper: Retry nach Validierungsfehler, Abbruch nach maximalen Versuchen, Metadaten im Ergebnis.
- Protokoll: Eintrag mit Token-Zahlen, aber ohne Text; Fehlschläge werden ebenfalls protokolliert.
- Ein Test belegt, dass echte Modellaufrufe in der normalen Suite blockiert sind.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [x] Alle Tests oben grün; `uv run pytest -m "not integration and not llm"` ruft kein echtes Modell auf.
- [x] Außerhalb von `llm/` importiert kein Modul `pydantic_ai`-Provider-Klassen direkt (per Test oder ruff-Regel belegt).
- [x] `uv run pytest -m llm -k ping` funktioniert mit gesetztem Key (manuell, Ergebnis in Notizen).
- [x] Doku aktualisiert, Abhängigkeit begründet.

## Offene Fragen / Annahmen

- Kein Mistral-Key vorhanden: Entwicklung mit `google:…` nur mit erfundenen Daten. Produktions-Key ist Voraussetzung für Task 27.
- Annahme: Ein Modell (`LLM_MODEL`) für alle Aufgaben. Wenn sich für den Inhaltsfilter ein kleineres Modell lohnt, ist das eine Architekturänderung und wird beim Nutzer erfragt.

## Notizen zu diesem Task

Taskspezifische Informationen während der Arbeit hier festhalten. Taskübergreifendes gehört in `Roadmap/README.md`.

- LLM-Ping manuell (2026-11-05): `uv run pytest -m llm -k ping -s` mit `LLM_MODEL=google:gemini-3.8-flash` und erfundenem Text → `PingReply(reply='Hallo, die Testnachricht wurde erfolgreich empfangen und die Verbindung steht!', language='de')`, 1 passed (ca. 60 s). Mit Mistral noch nicht möglich (kein Key).

## Abschluss-Checkliste

Reihenfolge und Details stehen in `AGENTS.md`, Abschnitt "Abschluss- und Archivierungs-Workflow".

- [x] Alle Akzeptanzkriterien erfüllt, Tests liegen permanent in den Test-Suites der Teile und laufen grün
- [x] Definition of Done aus `docs/testing.md` erfüllt und betroffene Dateien in `docs/` aktualisiert
- [x] Abschnitt "Erkenntnisse für Folge-Agenten" unten ausgefüllt
- [x] Folge-Tasks und `Roadmap/README.md` geprüft und bei Bedarf angepasst
- [x] Datei ohne `RUN_` nach `Roadmap/Archiv/` verschoben

## Erkenntnisse für Folge-Agenten

Vor der Archivierung vom Agenten auszufüllen. Schreibe so, dass ein Agent, der diesen Task nie gesehen hat, davon bei späteren Tasks profitiert:

- **Umgesetzt (und Abweichungen vom Plan):** Paket `dicrates/llm/` mit `factory.py`, `prompts.py` (+ `prompts/ping.v1.md`), `runner.py`, `call_log.py`; Migration `llm_calls`; Settings-Felder `mistral_api_key`, `google_api_key`; Request-Sperre in `tests/conftest.py`; Eval-Ordner `tests/llm_evals/` mit Ping. Kein Admin-CLI-Befehl für den Ping (der `llm`-Test erfüllt den Zweck; `dicrates-admin` kommt in Task 06). `LlmRunner` ist noch nicht in FastAPI/Jobs verdrahtet – das macht der erste Task, der ihn braucht.
- **Learnings & Stolpersteine:** Pydantic AI ist bei 2.66: `Agent(model, output_type=..., instructions=..., retries={"output": n})`, `agent.run(prompt, usage=RunUsage())` sammelt Tokens auch über Wiederholungen. Fehlerklassen: `ModelRateLimitError`, `ModelServerError`, `ModelConnectionError`, `ModelUnavailableError`, `ModelRequestTimeout` (transient) vs. z. B. `ModelHTTPError(400)`/`ModelAuthenticationError` (permanent); erschöpfte Output-Retries → `UnexpectedModelBehavior`. `FunctionModel` bekommt `info.output_tools[0].name` für strukturierte Antworten. Ohne `-m 'not llm'` in `addopts` lief der echte Ping bei jedem `uv run pytest` mit – jetzt standardmäßig abgewählt. Teilstring-Prüfungen auf Spaltennamen sind falsch (`input_tokens` enthält „input"); stattdessen exakte Spaltenliste.
- **Wichtige Entscheidungen und ihre Gründe:** Provider explizit mit Key aus `Settings` statt Env-Autoerkennung (klarer Fehler `LlmConfigurationError`, testbar). Eigene Retry-Schleife für transiente Fehler (injizierbares `backoff`) statt HTTP-Transport-Retries (provider-unabhängig, testbar). Prompt-Platzhalter mit `string.Template` (`$language`), damit JSON-Beispiele in Prompts gehen. Ein Protokolleintrag pro Lauf (nicht pro Versuch) mit `attempts`.
- **Auswirkungen auf Folge-Tasks:** Jede LLM-Aufgabe (Tasks 07, 08, 12–16) = neue Prompt-Datei `<name>.v1.md` + Pydantic-Ausgabemodell + `LlmRunner.run(...)`; gespeicherte Ergebnisse speichern `result.prompt_version` und `result.model`. Raumsprache als Prompt-Parameter. Tests mit `FunctionModel` und JSON-Fixtures. Für Jobs einen Runner über `build_model(get_settings())` + `PostgresLlmCallLog(pool)` bauen. `llm_calls.room_id` bekommt in Task 09 einen Fremdschlüssel. Task 23 (Evals) erweitert `tests/llm_evals/`.
- **Hinweise zu Tests und Befehlen:** `uv run pytest` (87 Unit, Ping abgewählt), `uv run pytest -m integration` (17, Stack nötig), `uv run pytest -m llm -k ping -s` (echter Aufruf, Key nötig).
