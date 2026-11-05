# Task_24: Barrierefreiheits-Audit

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_24.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M5 Datenschutz und Qualität

## Ziel

Alle App-Screens erfüllen WCAG 2.1 AA und sind mit Screenreader, großer Schrift und ohne Feinmotorik bedienbar. Das ist automatisiert mit Tests belegt und einmal manuell mit TalkBack (und VoiceOver, sobald iOS-Builds möglich sind) geprüft. Eine Einstellung für eine gut lesbare Schriftart steht zur Verfügung.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 19 archiviert (alle MVP-Screens inkl. Sprache und Vorlesen existieren).
- **Relevantes Vorwissen:** `docs/code-style.md` (Semantik-Labels, Text-Skalierung, Kontrast), `docs/concept-original.de.md` Kapitel 11, Golden-Setup aus Task 03.

## Umfang

**Gehört dazu:**

- Automatisierte Prüfungen für jeden Screen mit Flutters Accessibility-Guidelines (`androidTapTargetGuideline`, `iOSTapTargetGuideline`, `labeledTapTargetGuideline`, `textContrastGuideline`).
- Goldens jedes Screens mit Textskalierung 200 % (keine abgeschnittenen Texte, kein Overflow).
- Theme-Test, der Kontrastverhältnisse der Farbpaare berechnet (AA: 4,5:1 Text, 3:1 große Schrift/Bedienelemente), hell und dunkel.
- Fokus-Reihenfolge und Live-Region-Ansagen bei Statuswechseln (z. B. „Runde 2 ist offen", Fehlermeldungen).
- Respekt vor „Bewegung reduzieren".
- Einstellung „Gut lesbare Schrift" (z. B. Atkinson Hyperlegible; Lizenz prüfen) in den App-Einstellungen.
- Manueller Prüfdurchgang mit TalkBack nach Checkliste in `docs/testing.md`; Funde beheben.

**Gehört nicht dazu:**

- Leichte Sprache (Phase 2/3), Website-Barrierefreiheit (Task 25).

## Umsetzungsschritte

1. Gemeinsamen Test-Helfer schreiben, der jeden Screen gegen alle Guidelines prüft; für alle Screens rot laufen lassen und Funde sammeln.
2. Funde beheben, bis alle Tests grün sind.
3. 200-%-Goldens ergänzen und Overflows beheben.
4. Kontrast-Test für das Theme.
5. Schrift-Einstellung per TDD (Provider, Persistenz, Goldens).
6. Manuelle TalkBack-Prüfung nach Checkliste, Ergebnisse in Notizen.
7. `docs/testing.md` um Accessibility-Checks und Checkliste ergänzen.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (hier `app/test/`, `app/test/screenshots/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Guidelines-Test je Screen (alle Zustände: leer, gefüllt, Fehler).
- Goldens mit 200 % Textgröße.
- Kontrastverhältnisse im Theme.
- Schrift-Einstellung wirkt app-weit und bleibt nach Neustart erhalten.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Alle Accessibility-Tests grün, Definition of Done erfüllt.
- [ ] 200-%-Goldens liegen in `app/screenshots/`.
- [ ] TalkBack-Prüfung dokumentiert; offene Punkte, falls vorhanden, mit dem Nutzer abgestimmt.

## Offene Fragen / Annahmen

- VoiceOver-Prüfung ist erst mit iOS-Builds möglich (Apple Developer Program bzw. Mac mit Simulator); bis dahin nur TalkBack.

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
