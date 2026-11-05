# Task_23: LLM-Qualität und Bias-Tests

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_23.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M5 Datenschutz und Qualität

## Ziel

Die Qualität und Neutralität der LLM-Ausgaben ist mit einem wiederholbaren Evaluationslauf gegen das echte Modell belegt: Minderheitenmeinungen erscheinen im Gruppenbild, es gibt keine wörtlichen Übernahmen und keine Verteilung, die Bewertung verschiebt sich nicht systematisch nach politischem Framing und belohnt Positionswechsel nicht an sich. Die Kosten pro Partie sind gemessen. Prompts werden bei Bedarf in neuen Versionen verbessert.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 16 archiviert (alle LLM-Aufgaben existieren); Fixtures aus Tasks 12 und 16.
- **Relevantes Vorwissen:** `docs/concept-original.de.md` Kapitel 15 (Qualität und Neutralität, Bias-Tests mit Links-/Rechts-Framing), `docs/testing.md` (Marker `llm`, läuft nur auf Anfrage), Eval-Gerüst aus Task 05, Prompt-Versionierung.

## Umfang

**Gehört dazu:**

- Eval-Datensatz mit erfundenen Partien in `de` und `en` unter `backend/tests/` (Ordner aus Task 05): verschiedene politische Richtungen, klare Minderheitenposition, Troll-Inhalte, Grenzfälle für den Filter, Paare für Positionswechsel vs. begründetes Festhalten.
- Gespiegelte Paare für Bias: gleiche Argumentqualität, einmal linkes, einmal rechtes Framing.
- Prüfungen: Minderheitenposition im Gruppenbild (LLM-als-Richter mit eigenem Prompt oder strukturierter Abgleich), keine Verteilung, keine wörtlichen Übernahmen, Filter-Trefferquote auf Grenzfällen, Punktedifferenz bei gespiegelten Paaren innerhalb einer Toleranz, kein Bonus für Wechsel, Streuung über drei Läufe.
- Bericht als Markdown (z. B. `docs/llm-eval/<datum>.md`) mit Modell, Prompt-Versionen, Kennzahlen und Kosten pro Partie.
- Prompt-Verbesserungen als neue Versionen (`*.v2`), wenn Prüfungen fehlschlagen; alte Versionen bleiben für gespeicherte Ergebnisse nachvollziehbar.

**Gehört nicht dazu:**

- Dauerhafte Ausführung in CI (nur auf Anfrage), Modellwechsel ohne Rückfrage.

## Umsetzungsschritte

1. Auswertungslogik (Kennzahlen, Toleranzen, Bericht) per TDD mit `FunctionModel` bauen, damit die Harness selbst getestet ist.
2. Datensatz anlegen (nur erfundene Inhalte).
3. Lauf gegen das echte Modell mit `uv run pytest -m llm` bzw. einem CLI-Befehl; mit Mistral, falls der Key da ist, sonst mit Gemini (erfundene Daten sind erlaubt) und Vermerk im Bericht.
4. Ergebnisse auswerten; bei Verstößen Prompt-Versionen verbessern und erneut messen (höchstens drei Iterationen je Prompt, dann dem Nutzer berichten).
5. Bericht und Kosten pro Partie dokumentieren; Toleranzen in `docs/testing.md` festhalten.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (hier `backend/tests/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Unit: Kennzahlen-Berechnung, Toleranzprüfung, Berichtserzeugung (ohne echtes Modell).
- `llm`-Marker: echte Evaluation, nur auf Anfrage.
- Alle bestehenden Unit-Tests der Prompts bleiben grün, wenn neue Prompt-Versionen eingeführt werden.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Harness-Tests grün, Definition of Done erfüllt.
- [ ] Ein Evaluationsbericht liegt in `docs/llm-eval/` mit Modell, Prompt-Versionen, Kennzahlen und Kosten pro Partie.
- [ ] Alle Prüfungen bestehen oder die verbleibenden Abweichungen sind dem Nutzer berichtet und von ihm akzeptiert (Vermerk in Notizen).

## Offene Fragen / Annahmen

- Ohne Mistral-Key gilt der Bericht nur vorläufig; vor dem Release (Task 29) muss er mit dem Produktionsmodell wiederholt werden.
- Toleranz für Bias-Differenz (Vorschlag: höchstens 5 Punkte Mittelwertdifferenz je Dimension) mit dem Nutzer abstimmen.

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
