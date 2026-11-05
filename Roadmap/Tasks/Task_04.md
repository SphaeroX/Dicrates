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

- [ ] Alle oben genannten Backend- und App-Tests sind grün; Definition of Done für Backend und App erfüllt.
- [ ] Gegen den lokalen Supabase-Stack funktioniert eine E-Mail-OTP-Anmeldung manuell end to end (Ablauf in den Notizen dokumentiert).
- [ ] Kein Secret im Repo; neue Variablen stehen kommentiert in `.env.example`.
- [ ] Goldens der neuen Screens liegen in `app/screenshots/`.

## Offene Fragen / Annahmen

- Apple Developer Program fehlt: Sign in with Apple bleibt deaktiviert. App-Store-Richtlinie 4.8 verlangt bei Google-Login eine gleichwertige datenschutzfreundliche Option; vor Task 26 klären, ob E-Mail-Login genügt oder Apple-Login Pflicht ist.
- Ist das Pseudonym für andere Raummitglieder sichtbar? Wird in Task 09 mit dem Nutzer geklärt; hier nur speichern.
- Annahme: Altersbestätigung als Selbstauskunft genügt (rechtliche Prüfung in Task 28).

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
