# Task_03: App-Skelett + CI

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_03.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M1 Fundament

## Ziel

Die Flutter-Zähler-Demo wird durch die echte App-Struktur ersetzt: Feature-Ordner, Riverpod, Routing, Lokalisierung in Englisch und Deutsch, barrierearmes Theme, API-Client und die Screenshot-Pipeline mit Goldens. Ein Startbildschirm ruft `/health` des Backends auf. Jeder Push prüft die App in CI.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 01 archiviert (Backend `/health` existiert und hat einen dokumentierten Start-Befehl).
- **Relevantes Vorwissen:** `docs/architecture.md` (Riverpod, `--dart-define` für öffentliche Werte, Bundle-ID-Platzhalter), `docs/testing.md` → „App screenshots" (alchemist, `app/test/screenshots/`, `app/screenshots/`), `docs/code-style.md` (keine Strings im Code, Semantik-Labels, Text-Skalierung, Kontrast), `docs/conventions.md` (`lib/features/<feature>/`, `lib/core/`). Produktentscheidung 2026-11-05: Deutsch ist zweite App-Sprache und wird ab jetzt in jedem Task mitgepflegt.

## Umfang

**Gehört dazu:**

- `app/lib/main.dart` und `app/test/widget_test.dart` (Zähler-Demo) ersetzen; Aufbau `lib/core/` (Theme, Router, l10n, Konfiguration, API-Client) und `lib/features/`.
- `flutter_localizations` + ARB-Dateien `app_en.arb` (Basis) und `app_de.arb`; Locale folgt dem System, Fallback Englisch.
- Routing per `flutter pub add go_router` (Begründung in `docs/architecture.md`).
- Theme hell/dunkel mit WCAG-AA-Kontrasten, Respekt vor System-Textgröße.
- Konfiguration per `--dart-define`: `API_BASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY` (noch ungenutzt bis Task 04).
- API-Client (Bibliothek wählen, z. B. `http` oder `dio`, und begründen) mit Health-Abruf; Startbildschirm zeigt lokalisierten App-Namen und Verbindungsstatus.
- Golden-Setup: `alchemist` (dev), echte Schriften im Test laden, `flutter_test_config.dart`, Ausgabe in `app/screenshots/`, erste Goldens des Startbildschirms (hell/dunkel, Telefon/Tablet).
- GitHub-Actions-Workflow `.github/workflows/app.yml`: `flutter analyze`, `dart format --output=none --set-exit-if-changed .`, `flutter test` inkl. Goldens.
- README-Galerie für `app/screenshots/` vorbereiten.

**Gehört nicht dazu:**

- Anmeldung (Task 04), Spiel-Screens (ab Task 09), Store-Screenshots per `integration_test` und fastlane (Task 26).

## Umsetzungsschritte

1. Rote Widget-Tests für den Startbildschirm (englischer und deutscher Titel, Status „verbunden"/„nicht erreichbar" über überschriebenen Provider) schreiben.
2. Struktur, l10n, Theme, Router und Provider umsetzen; Zähler-Demo entfernen.
3. API-Client mit Test gegen einen gefakten HTTP-Client bauen.
4. alchemist einrichten, Schriften laden, Goldens erzeugen (`flutter test --update-goldens test/screenshots`).
5. Plattformunterschiede bei Goldens klären (CI läuft auf Linux): Strategie festlegen (z. B. CI-Goldens von alchemist oder Goldens nur auf einer Plattform verifizieren) und in `docs/testing.md` dokumentieren.
6. `app.yml` anlegen, lokal dieselben Befehle grün laufen lassen.
7. `docs/architecture.md` und `docs/testing.md` aktualisieren (neue Pakete, Start-Befehl mit `--dart-define`).

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (hier `app/test/`, `app/test/screenshots/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Startbildschirm zeigt den lokalisierten Titel in `en` und `de`.
- Health-Status „verbunden" und „nicht erreichbar" über Provider-Overrides.
- API-Client parst die Health-Antwort und behandelt Netzwerkfehler.
- Goldens: Startbildschirm hell/dunkel, Telefon/Tablet.
- Ein Test, der prüft, dass `app_de.arb` alle Schlüssel aus `app_en.arb` enthält.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Keine Spur der Zähler-Demo mehr in `app/lib/` und `app/test/`.
- [ ] `flutter test`, `flutter analyze` und die Format-Prüfung sind grün, lokal und im Workflow `app.yml`.
- [ ] PNGs des Startbildschirms liegen in `app/screenshots/`.
- [ ] Der ARB-Vollständigkeitstest ist grün.
- [ ] `flutter run --dart-define=API_BASE_URL=...` zeigt bei laufendem Backend den Status „verbunden".

## Offene Fragen / Annahmen

- Annahme: `go_router` für Routing (Deep Links für Einladungen kommen in Task 09).
- Golden-Plattformstrategie entscheidet dieser Task; Ergebnis in `Roadmap/README.md` eintragen, weil jeder UI-Task betroffen ist.

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
