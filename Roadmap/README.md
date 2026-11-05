# Dicrates – Roadmap

Projektübergreifendes Gedächtnis. Agenten lesen diese Datei vor jedem Task und aktualisieren sie, wenn sich etwas ergibt, das über einen einzelnen Task hinausgeht. Regeln für die Arbeit: [AGENTS.md](AGENTS.md).

## Projektziel

Dicrates macht Debattieren zum Spiel: Drei bis sechs Personen diskutieren anonym eine aktuelle, konkret formulierte und gern kontroverse Streitfrage in vier asynchronen Runden. Ein LLM fasst die Positionen zusammen, schlägt einen Kompromiss vor und vergibt Punkte für Verstehen, Argumentqualität und Kompromissbereitschaft statt für Rechthaben.

Ziel dieser Roadmap ist **Produktionsreife des MVP (Phase 1)**: Nach einer geschlossenen Beta ist die App öffentlich im Google Play Store und im Apple App Store verfügbar, betrieben in der EU, mit Einwilligung, Löschkonzept, Moderation und Rechtstexten.

**Was die Software tut:** Ein angemeldeter Nutzer (18+) erstellt einen Freundesraum, wählt eine vom LLM aus aktuellen News oder zeitlosen Debatten vorbereitete und vom Betreiber freigegebene Streitfrage sowie die Rundendauer und lädt per Code oder Link 2 bis 5 weitere Personen ein. In Runde 1 gibt jede Person blind ihre Position mit Begründung ab (Text oder Spracheingabe auf dem Gerät). In Runde 2 sehen alle nur ein LLM-Gruppenbild (keine Einzelmeinungen, keine Verteilung) und überarbeiten ihre Position oder bleiben begründet dabei. In Runde 3 zeigt eine Zusammenfassung, was sich bewegt hat, und es gibt Feedback zu Argumenten. In Runde 4 liefert das LLM Gesamtbild, Kompromissvorschlag mit Pro und Contra sowie Punkte je Dimension mit Begründung. Push-Benachrichtigungen begleiten die Runden, alles ist vorlesbar.

**Zielgruppe:** Für das MVP Freundes-, Familien- und Kollegenrunden ab 18 Jahren, zunächst mit App-Sprache Englisch und Deutsch.

**Nicht-Ziele:** Öffentliches Matching mit Warteschlange, Rating (Elo/Glicko) und Trust-Score mit Troll-Pool, Reset-Regeln, Web-Admin-Oberfläche, europäische Räume, Live-Modus, Leichte Sprache, Bildungs- und Premium-Angebote (alles Phase 2/3, siehe Ausblick unten). Grundsätzlich nie: soziales Netzwerk mit Profilen, Followern oder Kommentarspalten; Verkauf von Rohdaten; politische Werbung.

## Aktueller Status

Stand: 2026-11-05 – Tasks 01–07 erledigt (M1 Fundament abgeschlossen).

| Task | Titel | Status |
|---|---|---|
| 01 | Backend-Skelett + CI | erledigt |
| 02 | Lokales Supabase, DB und Jobs | erledigt |
| 03 | App-Skelett + CI | erledigt |
| 04 | Anmeldung end to end | erledigt |
| 05 | LLM-Schicht | erledigt |
| 06 | Fragenbibliothek + Admin-CLI | erledigt |
| 07 | News-Pipeline für Streitfragen | erledigt |
| 08 | Zeitlose und historische Streitfragen | offen |
| 09 | Freundesraum anlegen und beitreten | offen |
| 10 | Zustandsautomat der Runden | offen |
| 11 | Runde 1: Position abgeben | offen |
| 12 | Inhaltsfilter | offen |
| 13 | Runde 2: Gruppenbild und Überarbeitung | offen |
| 14 | Runde 3: Bewegung und Argument-Feedback | offen |
| 15 | Runde 4: Auswertung und Kompromiss | offen |
| 16 | Punktevergabe | offen |
| 17 | Hosting-Entscheidung und Staging-Deployment | offen |
| 18 | Push-Benachrichtigungen | offen |
| 19 | Spracheingabe und Vorlesen | offen |
| 20 | Meldefunktion und Moderations-CLI | offen |
| 21 | Beobachtung und Schutz im Betrieb | offen |
| 22 | Löschung, Datenexport und Löschfristen | offen |
| 23 | LLM-Qualität und Bias-Tests | offen |
| 24 | Barrierefreiheits-Audit | offen |
| 25 | Website und Rechtstexte | offen |
| 26 | Store-Vorbereitung | offen |
| 27 | Geschlossene Beta | offen |
| 28 | Sicherheits- und Datenschutz-Review | offen |
| 29 | Öffentlicher Release | offen |

Status ist `offen`, `läuft` (Datei trägt das Präfix `RUN_`) oder `erledigt` (Datei liegt in `Archiv/`). Die Tabelle wird beim Archivieren eines Tasks aktualisiert.

**Meilensteine:** M1 Fundament (01–05) · M2 Streitfragen (06–08) · M3 Kernspiel (09–16) · M4 Betrieb und Erreichbarkeit (17–21) · M5 Datenschutz und Qualität (22–24) · M6 Beta und Release (25–29).

## Taskübergreifende Entwicklungsinfos

Globale Informationen, Architekturentscheidungen und Wissen, das für das gesamte Projekt gilt. Wird laufend ergänzt; jeden Eintrag mit dem Task kennzeichnen, aus dem er stammt.

**Produktentscheidungen aus dem Roadmap-Interview (2026-11-05, Nutzer):**

- Umfang „Produktionsreife" = MVP Phase 1 bis zum öffentlichen Store-Release, mit geschlossener Beta davor.
- Rundendauer wählt der Raum-Ersteller beim Anlegen (Standard 24 h). Eine Runde schließt vorzeitig, sobald alle aktiven Mitglieder abgegeben haben.
- Räume haben 3 bis 6 Mitglieder. Unter 3 gültigen Abgaben wird die Partie ohne Punktabzug abgebrochen (`ABORTED`).
- Mindestalter 18+.
- Freundesräume sind immer anonym; das Gruppenbild zeigt keine Verteilung („4 dafür, 2 dagegen").
- Streitfragen: automatisch aus kuratierten News-Feeds plus zeitlose/historische Debatten, vom LLM vorbereitet (Frage, Faktenkasten, Quellen, Neutralitätscheck). Kriterium: „Hauptsache kontrovers", aber neutral formuliert. Nichts erscheint ohne Freigabe durch den Betreiber.
- Freigaben, Meldungen und Moderation laufen im MVP über ein CLI im Backend (`dicrates-admin`), keine Web-Admin-Oberfläche.
- App-Sprachen: Englisch (Basis) und Deutsch, Deutsch vollständig vor der Beta. Website ebenfalls Englisch und Deutsch.
- Produktions-Hosting für API und Worker wird in Task 17 entschieden, nach Rückfrage beim Nutzer.
- Tests liegen in den bestehenden Suites der Teile (`backend/tests/`, `app/test/`, `app/integration_test/`, `website/tests/`), nicht in einem Root-Ordner `tests/`.

**Backend-Grundlagen (Task 01, angepasst in Task 02):** Code unter `backend/src/dicrates/`, seit Task 02 als installiertes Paket (`uv_build`, `uv sync` installiert es editable). Settings zentral in `dicrates/core/settings.py` (`get_settings()`), Secrets als `SecretStr`. CI: `.github/workflows/backend.yml`. Unter Windows schreibt Python CRLF – Repo erzwingt LF, Dateien mit `newline="
"` schreiben.

**Datenbank und Jobs (Task 02):** Lokaler Stack `npx supabase start` (Docker nötig), Migrationen in `supabase/migrations/`. Alles im `public`-Schema ist über die Supabase Data API erreichbar: jede neue Tabelle braucht RLS und explizite `REVOKE`/`GRANT` für `anon`/`authenticated`, Funktionen ein `REVOKE ... FROM PUBLIC, anon, authenticated`. Backend verbindet als Owner (umgeht RLS) – Zugriffskontrolle für Spieldaten liegt im Backend-Code. Procrastinate loggt Job-Argumente: **Jobs bekommen nur IDs**, nie Texte oder E-Mails. Integrationstests: Marker `integration`, lokal Skip ohne DB, in CI Pflicht.

**App-Grundlagen (Task 03):** Struktur `lib/core/` + `lib/features/<feature>/{data,providers,widgets}`, Riverpod 3, go_router, `http`. Strings nur in `lib/l10n/app_en.arb` + `app_de.arb` (Vollständigkeitstest). **Golden-Strategie:** Plattform-Goldens mit echter Schrift nur unter Windows → `app/screenshots/`; CI-Goldens (plattformunabhängig) → `app/test/screenshots/goldens/ci/`, in CI geprüft. Goldens immer unter Windows mit `flutter test --update-goldens test/screenshots` erzeugen und beide Ordner committen. Test-Helfer `buildTestApp` in `app/test/helpers/pump_app.dart`.

**Anmeldung und Einwilligung (Task 04):** Backend prüft Supabase-Tokens per JWKS (ES256) in `dicrates.core.auth` (`CurrentUser`). **Jeder Spiel-Endpunkt nutzt `ConsentedUser`** aus `dicrates.profiles.dependencies` (403 ohne aktuelle Einwilligung + 18+). Einwilligungstext ist versioniert (Backend `CURRENT_CONSENT_VERSION`, App `currentConsentVersion`, ARB `consentBodyV<n>`). App-Router-Gate: Login → Alter → Einwilligung → Pseudonym → Home (`core/router/app_gate.dart`). Lokales Supabase braucht `supabase/signing_keys.json` (ES256, git-ignored). Muster für Daten: Repository-Protocol + Postgres-Implementierung + Fake in den Tests.

**LLM-Schicht (Task 05):** Alle LLM-Aufrufe über `dicrates.llm` (`build_model`, `default_registry`, `LlmRunner`); Provider-Imports nur in `llm/factory.py` (ruff TID251). Prompts als Dateien `llm/prompts/<name>.v<N>.md`, Version wird mit jedem Ergebnis gespeichert. Nutzungsprotokoll `llm_calls` ohne jeden Text. Tests: `FunctionModel`; echte Evals nur mit `-m llm` (standardmäßig abgewählt).

**Fragen und Betreiber-CLI (Task 06):** Streitfragen in `questions` (Faktenkasten/Quellen als `jsonb`, Status `draft → approved|rejected`, `approved → retired`). Pipelines legen nur Entwürfe an; Freigabe ausschließlich per `uv run dicrates-admin questions approve <id>` (siehe `docs/operations.md`). Betreiber-Befehle kommen als Typer-Unter-Apps in `dicrates/admin/cli.py`. App-Widget `QuestionCard` für alle Rundenscreens.

**News-Pipeline (Task 07):** Quellen in `backend/config/news_sources.toml` (vom Nutzer bestätigt). Job `news_questions` alle 6 h bzw. `dicrates-admin questions generate --from-news`. Fragen entstehen zweisprachig (en+de, gemeinsame `group_id`); Quellen baut das Backend aus gespeicherten Feed-Einträgen, das LLM vergibt nur Quellennummern. LLM-Features hängen vom Protokoll `LlmTaskRunner` ab, Tests nutzen `tests/llm/scripted_runner.py`.

**Bestehende Projektregeln:** Root-`AGENTS.md` (TDD, Umgebungen, Privacy, i18n, Screenshots) und `docs/` (Architektur, Testing, Code-Style, Konventionen, Brief) gelten für jeden Task.

## Auffälligkeiten & Details

Dinge, die global noch zu beachten sind: Besonderheiten, bekannte Einschränkungen, kleinere Details. Wird laufend ergänzt.

- **Externe Voraussetzungen (Nutzer):**
  - Apple Developer Program fehlt noch. Ohne Konto kein Sign in with Apple, kein APNs-Push, kein TestFlight und kein App Store. Betroffen: Tasks 04, 18, 26, 27, 29. Android geht vor.
  - Google Play Console ist vorhanden.
  - Kein Mistral-Key vorhanden. Bis dahin Entwicklung mit Gemini **nur mit erfundenen Testdaten**. Spätestens vor der Beta (Task 27) ist ein produktiver Mistral-Key Pflicht.
  - Supabase-Cloud-Projekt und Firebase-Projekt existieren (Werte in `.env`).
  - Keine eigene Domain: Website läuft auf `sphaerox.github.io/Dicrates/`, Bundle-ID `io.github.sphaerox.dicrates` ist Platzhalter. Vor dem ersten Store-Upload (Task 26) endgültig entscheiden, da die ID danach nicht mehr änderbar ist.
  - Anwaltliche Prüfung der Rechtstexte, AVVs mit Anbietern und eine Datenschutz-Folgenabschätzung sind Nutzeraufgaben (Tasks 25, 28, 29).
- **Docker fehlt lokal (Task 02):** Auf dem Windows-Rechner des Nutzers ist kein Docker/WSL2 installiert (winget-Installation scheiterte an UAC). Integrationstests laufen bis dahin nur in CI (`backend.yml`, Job `integration`). Nutzer installiert Docker Desktop selbst.
- **Windows-Sandbox des Agenten (Task 03):** Aus der Sandbox angelegte Ordner erhalten das ReadOnly-Attribut; Flutter (gen-l10n, `build/`) und `uv` (Löschen in `.venv`) scheitern dann mit „Zugriff verweigert". Flutter- und uv-Befehle, die Dateien löschen/erzeugen, ohne Sandbox ausführen und ggf. das Attribut entfernen.
- **Kein Android-Gerät/AVD (Task 03):** Gerätetests (`flutter run`, `integration_test`) sind auf dem Rechner derzeit nicht möglich; Nutzer müsste ein AVD anlegen oder ein Gerät anschließen.
- **uvicorn unter Windows mit DB (Task 04):** psycopg async braucht die Selector-Event-Loop; uvicorn nutzt unter Windows standardmäßig Proactor. Für lokalen Dev-Server mit DB eine Lösung schaffen, sobald Docker lokal läuft (z. B. `--loop` mit eigener Factory) – in CI/Produktion (Linux) kein Problem.
- **Google-OAuth-Client fehlt (Task 04):** Google-Login ist im Code fertig, lokal aber deaktiviert, bis der Nutzer einen OAuth-Client anlegt (siehe Archiv/Task_04.md, Notizen).
- **Gemini-Verfügbarkeit (Task 07):** `google:gemini-3.8-flash` (in `.env`) war am 2026-11-05 zeitweise dauerhaft überlastet (503); `google:gemini-3.1-flash-lite` lief. Für manuelle Läufe ggf. per `LLM_MODEL=...` überschreiben. Produktion braucht ohnehin Mistral.
- **Kein Root-Ordner `tests/`:** Das Prüfskript des Roadmap-Skills meldet dessen Fehlen als Fehler; das ist hier gewollt (siehe Entscheidung oben).
- **Ausblick Phase 2/3 (nicht Teil dieser Roadmap):** Interessen und Matching-Warteschlange, öffentliche Räume, Rating und Trust-Score mit Troll-Pool und Reset-Regeln, Web-Admin, Verteilungsanzeige per A/B-Test, optionale Anonymität in Freundesräumen, europäische Räume, Live-Modus, Leichte Sprache, Statistiken, Saisons, Bildungs- und Premium-Angebote.
