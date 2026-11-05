# Task_26: Store-Vorbereitung

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_26.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M6 Beta und Release

## Ziel

Die App ist bereit für die Stores: endgültiger Name, Icon und Bundle-ID, signierte Release-Builds aus CI, automatisch erzeugte Store-Screenshots in Englisch und Deutsch, Store-Texte, ausgefüllte Datenschutzangaben (Play Data Safety, App Privacy) und Altersfreigabe 18+. Android ist vollständig vorbereitet, iOS so weit, wie es ohne bzw. mit Apple-Konto möglich ist.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Tasks 24 (barrierefreie Screens) und 25 (Rechtstexte, Website-Links) archiviert.
- **Relevantes Vorwissen:** `docs/testing.md` → „App screenshots" (Store-Screenshots per `integration_test`, `flutter drive`, fastlane-Ordner je Locale), `docs/architecture.md` (Bundle-ID-Platzhalter `io.github.sphaerox.dicrates`), `docs/data-inventory.md` (für Datenschutzangaben), Google Play Console vorhanden, Apple Developer Program fehlt.

## Umfang

**Gehört dazu:**

- **Entscheidung mit dem Nutzer:** endgültige Bundle-ID (ist nach dem ersten Upload nicht mehr änderbar) und ob eine eigene Domain kommt (App Links/Universal Links für Einladungen).
- App-Icon und Splash (z. B. `flutter_launcher_icons`), App-Name lokalisiert.
- Versionierungsschema (`version` in `pubspec.yaml`, Build-Nummer aus CI).
- Android: Upload-Key (erzeugt der Nutzer, Ablage als GitHub-Secret), Play App Signing, Release-AAB im CI-Workflow.
- iOS: Projekt-Einstellungen, Berechtigungstexte, Sign in with Apple aktivieren und APNs einrichten, **sofern** das Apple-Konto inzwischen existiert; sonst Checkliste für später.
- Store-Screenshots: `app/integration_test/store_screenshots_test.dart` mit erfundenen Demo-Daten über Provider-Overrides, `test_driver/integration_test.dart`, Ausgabe in die fastlane-Ordner je Locale (`en-US`, `de-DE`).
- fastlane für Android (`supply`) und iOS (`deliver`) einrichten; Metadaten (Kurz- und Langbeschreibung, Hinweis auf On-Device-Spracheingabe, KI-Kennzeichnung) in en/de.
- Ausgefüllte Antworten für Play Data Safety, Content Rating (Nutzerinhalte, Moderation, 18+) und Apple App Privacy als Dokument in `docs/store.md`.
- App Links für Einladungen, falls eine Domain entschieden ist; sonst bleibt das Custom Scheme.

**Gehört nicht dazu:**

- Einreichung zur Prüfung (Task 27 intern, Task 29 öffentlich), Beta-Verteilung (Task 27).

## Umsetzungsschritte

1. Bundle-ID und Domain mit dem Nutzer klären; ggf. Bundle-ID überall anpassen (Android, iOS, Firebase-Konfiguration).
2. Icon, Name und Versionierung umsetzen.
3. Store-Screenshot-Test schreiben und auf Emulatoren in beiden Sprachen laufen lassen.
4. Signierung und Release-Build in CI einrichten (Secrets durch den Nutzer).
5. fastlane und Metadaten anlegen; `fastlane supply --validate_only` bzw. Dry-Run.
6. `docs/store.md` mit Datenschutzangaben und Altersfreigabe schreiben.
7. iOS-Teil je nach Kontostand umsetzen oder als Checkliste dokumentieren.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`app/integration_test/`, `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Store-Screenshot-Flow läuft für beide Locales und erzeugt die erwartete Anzahl Bilder.
- Widget-Test: App-Name lokalisiert.
- CI: Release-Build-Job erzeugt ein signiertes AAB (auf Branch oder manuell ausgelöst).

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Bundle-ID ist final und in `docs/architecture.md` dokumentiert.
- [ ] Signiertes Release-AAB wird von CI gebaut.
- [ ] Store-Screenshots in `en-US` und `de-DE` liegen in den fastlane-Ordnern.
- [ ] `docs/store.md` enthält alle Formularantworten; der Nutzer hat sie gegengelesen.
- [ ] iOS-Stand ist dokumentiert (umgesetzt oder Checkliste).

## Offene Fragen / Annahmen

- **Rückfrage an den Nutzer:** Bundle-ID und Domain (Pflicht vor dem ersten Upload).
- **Nutzeraufgabe:** Apple Developer Program beantragen, wenn iOS zum Release dabei sein soll; Upload-Key erzeugen.
- Klären, ob App-Store-Richtlinie 4.8 Sign in with Apple verlangt (siehe Task 04).

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
