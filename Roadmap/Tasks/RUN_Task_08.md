# Task_08: Zeitlose und historische Streitfragen

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_08.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M2 Streitfragen

## Ziel

Neben den News-Fragen gibt es einen wachsenden Bestand an zeitlosen und historischen Streitfragen (z. B. Tempolimit, Wehrpflicht, Atomkraft, Grundeinkommen, Wahlalter 16), damit die Bibliothek nie leer ist. Das LLM erzeugt sie aus einer kuratierten Themenliste mit derselben Prüfung wie in Task 07. Am Ende liegt ein freigabefähiger Startbestand in beiden Sprachen vor. Leitlinie: „Hauptsache kontrovers".

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 06 archiviert; Task 07 liefert Prompts `question_draft` und `question_check`, die hier wiederverwendet werden.
- **Relevantes Vorwissen:** Erkenntnisse aus Task 07 (Prompt-Verhalten, Kosten, Duplikatschutz), `docs/concept-original.de.md` Kapitel 8 und 14 (klare Regeln für heikle Themen: sachliche Diskussion erlaubt, Menschenverachtung nicht).

## Umfang

**Gehört dazu:**

- Kuratierte Themenliste (z. B. `backend/config/evergreen_topics.yaml`): Thema, Themengebiet, optional Leitfrage und vertrauenswürdige Quellen-URLs (z. B. Bundeszentrale für politische Bildung, Parlamentsdokumente, Wikipedia als Einstieg), Kennzeichnung `historical` oder `evergreen`.
- LLM-Agent „zeitlose Streitfrage": aktuelle Gültigkeit beachten (historische Debatten werden als heute entscheidbare Frage formuliert), Faktenkasten nur aus angegebenen Quellen.
- Erreichbarkeitsprüfung der Quellen-URLs hinter einem Interface (Fake in Tests).
- CLI `questions generate --evergreen [--topic <id>] [--limit]`, Speicherung als `draft` mit Herkunft `evergreen`.
- Startbestand: mindestens 30 Entwürfe je Sprache erzeugen, damit der Nutzer mindestens 20 je Sprache freigeben kann.

**Gehört nicht dazu:**

- Freigabe selbst (Nutzeraufgabe per CLI), automatische Aktualisierung von Fakten, Bias-Evaluation (Task 23).

## Umsetzungsschritte

1. Rote Tests für Laden und Validieren der Themenliste schreiben, dann umsetzen.
2. Prompt `evergreen_question.v1` und Pipeline per TDD mit `FunctionModel`; Check aus Task 07 wiederverwenden.
3. Erreichbarkeitsprüfung per TDD (unerreichbare Quelle → Entwurf wird markiert, nicht verworfen).
4. CLI-Befehl per TDD.
5. Themenliste mit ca. 40 kontroversen Themen anlegen und dem Nutzer zur Durchsicht vorlegen.
6. Startbestand mit echtem LLM erzeugen (erfundene Nutzerdaten sind hier nicht beteiligt; nur öffentliche Themen) und Anzahl in Notizen festhalten.
7. Doku aktualisieren.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (hier `backend/tests/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Themenliste: Pflichtfelder, ungültiges Themengebiet wird abgelehnt.
- Pipeline: erzeugt `draft` mit Herkunft `evergreen`; Duplikat zu bestehender Frage wird übersprungen.
- Quellen-Erreichbarkeit: unerreichbar → Markierung im Entwurf.
- Safety-Check `reject` bei menschenverachtender Prämisse (Fixture).

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Alle Tests grün, Definition of Done erfüllt.
- [ ] Mindestens 30 Entwürfe je Sprache liegen in der lokalen Bibliothek (Befehl und Ergebnis in Notizen).
- [ ] Die Themenliste ist mit dem Nutzer abgestimmt (Vermerk in Notizen).
- [ ] Doku beschreibt, wie neue Themen ergänzt werden.

## Offene Fragen / Annahmen

- **Rückfrage an den Nutzer:** Grenzen bei besonders heiklen Themen (z. B. Abtreibung, Todesstrafe, Migration, Geschlechtsidentität): alle erlaubt, solange neutral formuliert und ohne menschenverachtende Prämisse? Ergebnis in die Prüfregeln und in `Roadmap/README.md`.
- Der Startbestand liegt zunächst lokal; die Übernahme in Staging/Produktion regelt Task 17 bzw. 29 (z. B. Export/Import per CLI).
- Freigabe der Entwürfe ist eine Nutzeraufgabe.

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
