# Task_04: Anmeldung end to end

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_04.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M1 Fundament

## Ziel

Ein Mensch kann sich in der App per E-Mail oder Google anmelden, bestätigt, dass er 18 oder älter ist, erteilt die ausdrückliche Einwilligung zur Verarbeitung politischer Meinungen (DSGVO Art. 9) und wählt ein Pseudonym. Das Backend erkennt ihn über die Prüfung des Supabase-Tokens per JWKS und sperrt Spiel-Endpunkte ohne Einwilligung.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Tasks 02 (DB, `profiles`) und 03 (App-Struktur, l10n, Goldens) archiviert.
- **Aus Task 02:** Es gibt noch keinen FastAPI-Lifespan mit DB-Pool; `create_pool` aus `dicrates/core/db.py` hier in `main.py` per Lifespan öffnen und als Dependency bereitstellen (`/health` muss ohne DB weiter starten). Unter Windows braucht psycopg async eine Selector-Event-Loop (auch für uvicorn). Neue Tabelle `consents` mit RLS + expliziten Grants.
- **Relevantes Vorwissen:** `docs/architecture.md` (JWKS-Endpunkt `<SUPABASE_URL>/auth/v1/.well-known/jwks.json`, ES256, kein JWT-Secret; App erhält nur URL und Anon-Key), `docs/project-brief.md` (Konto, Pseudonym, Einwilligung, Löschung), Produktentscheidung 18+.

## Umfang

**Gehört dazu:**

- App: `supabase_flutter` per `flutter pub add`; Anmeldung per E-Mail (Vorschlag: Einmal-Code/OTP statt Magic Link, da ohne Domain keine Universal Links) und Google; Sign in with Apple im Code vorbereitet, aber per Schalter aus (kein Apple-Konto).
- Onboarding nach der ersten Anmeldung: Altersbestätigung 18+ (Selbstauskunft), Einwilligungsbildschirm mit versioniertem Einwilligungstext (ARB, en + de) und Platzhalter-Link zur Datenschutzerklärung (final in Task 25), Pseudonym-Wahl.
- Backend: `core/auth` mit Prüfung des Tokens gegen JWKS (Bibliothek wählen, z. B. `PyJWT[crypto]`, und begründen), JWKS-Cache, Prüfung von `aud`, `exp`, `iss`.
- Endpunkte `GET /me`, `PATCH /me` (Pseudonym, Sprache), `POST /me/consent` (speichert Einwilligungsversion, Zeitpunkt, Altersbestätigung in neuer Tabelle `consents`, Migration).
- Abhängigkeit `require_consent` für alle späteren Spiel-Endpunkte (403 ohne gültige Einwilligung oder Altersbestätigung).
- Abmelden in der App.

**Gehört nicht dazu:**

- Konto löschen und Datenexport (Task 22), Live-Schaltung von Sign in with Apple (sobald Apple-Konto da ist, spätestens Task 26), eigenes SMTP für Auth-Mails (Task 27).

## Umsetzungsschritte

1. Backend: rote Tests mit eigenem Test-Schlüsselpaar und gefaktem JWKS (gültig, abgelaufen, falsche Signatur, falsches `aud`) schreiben, dann `core/auth` umsetzen.
2. Migration `consents`, Endpunkte `/me` und `/me/consent` per TDD.
3. `require_consent` per TDD.
4. App: Auth-Repository-Interface mit Fake für Tests; Login-, Altersbestätigungs-, Einwilligungs- und Pseudonym-Screens per Widget-Tests.
5. Supabase-Auth lokal konfigurieren (E-Mail-OTP, Google-Provider mit Test-Client), Einrichtung in `docs/architecture.md` dokumentieren; Google-OAuth-Client-Daten gehören in `.env`/`--dart-define`, nie ins Repo.
6. Goldens für alle neuen Screens.
7. `.env.example` um neue Variablen ergänzen.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`backend/tests/`, `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Backend: Token-Prüfung (gültig → 200, abgelaufen/falsche Signatur/falsches `aud` → 401, fehlender Header → 401), JWKS-Cache wird bei unbekannter `kid` neu geladen.
- Backend: `GET /me` legt beim ersten Aufruf ein Profil an; `POST /me/consent` speichert Version und Zeitpunkt.
- Backend: Endpunkt mit `require_consent` liefert 403 ohne Einwilligung bzw. ohne Altersbestätigung.
- App: Onboarding-Reihenfolge, Ablehnung der Einwilligung führt nicht ins Spiel, Pseudonym-Validierung.
- Goldens: Login, Altersbestätigung, Einwilligung, Pseudonym (hell/dunkel).

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [x] Alle oben genannten Backend- und App-Tests sind grün; Definition of Done für Backend und App erfüllt.
- [x] Gegen den lokalen Supabase-Stack funktioniert eine E-Mail-OTP-Anmeldung end to end (automatisiert statt manuell: `backend/tests/test_auth_e2e.py` läuft im CI-Job `integration` gegen echtes Supabase Auth mit ES256-Schlüssel; Ablauf in den Notizen. Ein Lauf mit der echten App auf einem Gerät steht noch aus – kein Docker und kein Emulator auf dem Rechner).
- [x] Kein Secret im Repo; neue Variablen stehen kommentiert in `.env.example`.
- [x] Goldens der neuen Screens liegen in `app/screenshots/`.

## Offene Fragen / Annahmen

- Apple Developer Program fehlt: Sign in with Apple bleibt deaktiviert. App-Store-Richtlinie 4.8 verlangt bei Google-Login eine gleichwertige datenschutzfreundliche Option; vor Task 26 klären, ob E-Mail-Login genügt oder Apple-Login Pflicht ist.
- Ist das Pseudonym für andere Raummitglieder sichtbar? Wird in Task 09 mit dem Nutzer geklärt; hier nur speichern.
- Annahme: Altersbestätigung als Selbstauskunft genügt (rechtliche Prüfung in Task 28).

## Notizen zu diesem Task

Taskspezifische Informationen während der Arbeit hier festhalten. Taskübergreifendes gehört in `Roadmap/README.md`.

**E-Mail-OTP end to end (lokaler Stack):**

1. Einmalig: `echo '[]' > supabase/signing_keys.json && npx supabase gen signing-key --algorithm ES256` (Repo-Root), dann `npx supabase start`.
2. Backend: `.env` mit `SUPABASE_URL=http://127.0.0.1:54321` und `DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres`; `uv run uvicorn dicrates.main:app --reload` (unter Windows: siehe Auffälligkeit Selector-Loop in `Roadmap/README.md`).
3. App: `flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000 --dart-define=SUPABASE_URL=http://10.0.2.2:54321 --dart-define=SUPABASE_ANON_KEY=<ANON_KEY aus npx supabase status>`.
4. E-Mail eingeben → Code aus Mailpit (http://127.0.0.1:54324) → Alter → Einwilligung → Pseudonym → Startbildschirm.

Automatisiert belegt (CI): `test_auth_e2e.py` fordert per Supabase-Auth-API einen Code an, liest ihn aus Mailpit, verifiziert ihn und ruft mit dem ES256-Token `/me` auf (200, Profil angelegt; ohne Token 401). App-Seite per Widget-Tests mit Fakes. Echter Gerätelauf offen (kein Docker/Emulator).

**Google-Login:** Code und Deep Link (`io.github.sphaerox.dicrates://login-callback`) sind fertig; lokal ist `[auth.external.google]` `enabled = false`, bis der Nutzer einen OAuth-Client (Typ Web, Redirect `http://127.0.0.1:54321/auth/v1/callback`) anlegt und `SUPABASE_AUTH_EXTERNAL_GOOGLE_CLIENT_ID/SECRET` in `.env` setzt. Für die Cloud im Supabase-Dashboard konfigurieren (Task 17).

## Abschluss-Checkliste

Reihenfolge und Details stehen in `AGENTS.md`, Abschnitt "Abschluss- und Archivierungs-Workflow".

- [x] Alle Akzeptanzkriterien erfüllt, Tests liegen permanent in den Test-Suites der Teile und laufen grün
- [x] Definition of Done aus `docs/testing.md` erfüllt und betroffene Dateien in `docs/` aktualisiert
- [x] Abschnitt "Erkenntnisse für Folge-Agenten" unten ausgefüllt
- [x] Folge-Tasks und `Roadmap/README.md` geprüft und bei Bedarf angepasst
- [x] Datei ohne `RUN_` nach `Roadmap/Archiv/` verschoben

## Erkenntnisse für Folge-Agenten

Vor der Archivierung vom Agenten auszufüllen. Schreibe so, dass ein Agent, der diesen Task nie gesehen hat, davon bei späteren Tasks profitiert:

- **Umgesetzt (und Abweichungen vom Plan):** Backend: `core/auth.py` (ES256 via JWKS, `CurrentUser`), Paket `profiles` (`/me`, `PATCH /me`, `POST /me/consent`, `require_consent`/`ConsentedUser`, `PostgresProfileRepository`), Migration `consents`, DB-Lifespan in `main.py`. App: Features `auth`, `onboarding`, `splash`, Router-Gate, `SignOutAction` auf dem Startbildschirm, 6 neue Screens mit Goldens. Supabase: ES256-Signaturschlüssel lokal, Code-E-Mail-Template, Google-Provider vorbereitet (aus). **Abweichung:** Der „manuelle" E2E-Test wurde als automatisierter CI-Integrationstest umgesetzt (lokal kein Docker).
- **Learnings & Stolpersteine:** Lokales Supabase signiert ohne `signing_keys_path` mit HS256 – dann schlägt die JWKS-Prüfung fehl; `supabase gen signing-key` braucht eine vorhandene Datei (`echo '[]' > ...`). `supabase status -o json | jq -r .ANON_KEY` liefert den Anon-Key in CI. Pydantic-Settings: `Settings(_env_file=None, ...)` – pyright-Ignore muss auf der `_env_file`-Zeile stehen. `get_token_verifier` darf nicht global gecacht sein, sonst ignoriert `create_app(settings)` die übergebenen Settings – Verifier liegt jetzt in `app.state`. gen-l10n sortiert Locales alphabetisch (siehe Task 03). Vor jedem Commit `dart format .` laufen lassen (CI prüft es; einmal vergessen). Riverpod 3: `FutureProvider(..., retry: (_, _) => null)` schaltet Auto-Retry ab (sonst Endlosschleifen bei Backend-Fehlern in Tests).
- **Wichtige Entscheidungen und ihre Gründe:** `pyjwt[crypto]` statt Supabase-SDK im Backend (nur Verifikation nötig). E-Mail-OTP statt Magic Link (keine Domain für Universal Links). Einwilligung append-only mit Version; `require_consent` prüft Version **und** Altersbestätigung; Version `1` in `profiles/consent.py` und `pseudonym_rules.dart` (`currentConsentVersion`) – bei Textänderung beide erhöhen und neuen ARB-Schlüssel `consentBodyV2` anlegen. Altersantwort nur im Speicher, gespeichert wird sie mit der Einwilligung. E-Mail nie in Routen. Pseudonym ist nicht eindeutig (Sichtbarkeit wird in Task 09 geklärt).
- **Auswirkungen auf Folge-Tasks:** Alle Spiel-Endpunkte (ab Task 09) nutzen `ConsentedUser` aus `dicrates.profiles.dependencies`. Neue Repositories nach dem Muster Protocol + Postgres-Implementierung + Fake in `tests/<feature>/fakes.py`. App: neue Screens hinter dem Gate als Routen in `app_router.dart`; `buildTestApp` liefert standardmäßig einen eingeloggten, fertig onboardeten Nutzer mit `FakeBackend` – das `FakeBackend` um neue Endpunkte erweitern. Task 17: Supabase-Cloud braucht E-Mail-Template mit `{{ .Token }}`, Redirect-URL `io.github.sphaerox.dicrates://login-callback`, Google-Provider. Task 22 (Löschung): Profile und Einwilligungen hängen per `ON DELETE CASCADE` am Auth-User. Task 26: Apple-Login-Pflicht (Richtlinie 4.8) klären.
- **Hinweise zu Tests und Befehlen:** Backend `uv run pytest` (62 Unit-Tests), `uv run pytest -m integration` (15, braucht Stack; E2E zusätzlich `TEST_SUPABASE_ANON_KEY`). App `flutter test` (110 inkl. Goldens). Goldens neu: `flutter test --update-goldens test/screenshots` unter Windows.
