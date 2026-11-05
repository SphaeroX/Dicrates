# Task_19: Spracheingabe und Vorlesen

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_19.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M4 Betrieb und Erreichbarkeit

## Ziel

Wer ungern tippt, kann Positionen, Überarbeitungen und Feedback einsprechen. Die Erkennung läuft ausschließlich auf dem Gerät, das Transkript erscheint editierbar im Textfeld und wird nie automatisch abgeschickt. Streitfrage, Faktenkasten, Zusammenfassungen und Ergebnis lassen sich vorlesen. Audio wird nie gespeichert und verlässt nie das Gerät.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 11 archiviert (Eingabe-Screens); Screens aus Tasks 13–16 für das Vorlesen.
- **Relevantes Vorwissen:** `docs/architecture.md` (STT/TTS nur über Plattform-APIs auf dem Gerät, Audio nie gespeichert), Root-`AGENTS.md` Regel 4, `docs/concept-original.de.md` Kapitel 11.

## Umfang

**Gehört dazu:**

- Paketwahl für Spracherkennung (z. B. `speech_to_text`) und Vorlesen (z. B. `flutter_tts`) per `flutter pub add`, mit Begründung in `docs/architecture.md`.
- Erzwingen der Erkennung auf dem Gerät: iOS `requiresOnDeviceRecognition`, Android Offline-Erkennung (z. B. `EXTRA_PREFER_OFFLINE` bzw. On-Device-Recognizer). Ist das nicht verfügbar, wird das Mikrofon deaktiviert und erklärt, statt an einen Cloud-Dienst auszuweichen.
- Interfaces `SpeechInput` und `ReadAloud` mit Fakes für Tests.
- Mikrofon-Button an allen Freitextfeldern (Runde 1, 2, Feedback, Partie-Feedback); Transkript wird ins Feld eingefügt und bleibt editierbar.
- Vorlese-Button an Frage, Faktenkasten, Gruppenbild, Bewegung, Ergebnis und eigener Bewertung; Sprache folgt der Raumsprache.
- Berechtigungstexte (Info.plist, Android-Manifest) lokalisiert.

**Gehört nicht dazu:**

- Cloud-Spracherkennung, Audio-Speicherung, Leichte Sprache (Phase 2/3).

## Umsetzungsschritte

1. Prüfen, ob die Pakete Erkennung ausschließlich auf dem Gerät erzwingen können; Ergebnis in Notizen. Wenn nicht, anhalten und den Nutzer fragen.
2. Rote Widget-Tests mit Fakes: Mikrofon nicht verfügbar, Transkript eingefügt, nichts wird automatisch gesendet.
3. Interfaces, Implementierungen und Buttons umsetzen.
4. Vorlese-Buttons per Widget-Tests (richtiger Text, richtige Sprache, Stop).
5. Goldens für Zustände „Aufnahme läuft" und „Vorlesen läuft".
6. Manueller Test auf Android, inkl. Flugmodus als Beleg für Offline-Erkennung (Notizen).

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (hier `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- Ohne On-Device-Erkennung ist der Mikrofon-Button deaktiviert und hat ein erklärendes Semantik-Label.
- Transkript landet im Feld und ist editierbar; Absenden erfordert weiterhin den Button.
- Vorlesen nutzt die Raumsprache und den angezeigten Text.
- Keine Audio-Datei wird geschrieben (Fake prüft, dass keine Speicher-API aufgerufen wird).

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] Alle Tests grün, Definition of Done erfüllt.
- [ ] Manueller Test im Flugmodus auf Android: Spracheingabe funktioniert oder ist nachvollziehbar deaktiviert (Notizen).
- [ ] Goldens aktualisiert.

## Offene Fragen / Annahmen

- Wenn Android auf einem Gerät keine On-Device-Erkennung für die Sprache anbietet, bleibt die Funktion dort aus. Diese Einschränkung in die Store-Beschreibung bzw. Hilfe aufnehmen (Task 26).

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
