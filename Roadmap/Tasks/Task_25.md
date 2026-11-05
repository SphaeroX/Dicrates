# Task_25: Website und Rechtstexte

> ## ⚠️ PFLICHT – BEVOR DU IRGENDETWAS ANDERES TUST
>
> 1. **Lies als Allererstes die Datei `AGENTS.md` im übergeordneten Ordner `Roadmap/`** (von hier: `../AGENTS.md`) und befolge sie strikt.
> 2. **Deine allererste Aktion** ist, diese Datei in `RUN_Task_25.md` umzubenennen, um den Task als laufend zu markieren. Das passiert **noch bevor irgendein Code geschrieben** wird.

**Meilenstein:** M6 Beta und Release

## Ziel

Die Website erklärt Dicrates in Englisch und Deutsch (Idee, Ablauf einer Partie, Anonymität, KI-Transparenz) und stellt Impressum, Datenschutzerklärung, Nutzungsbedingungen mit Verhaltensregeln, KI-Hinweis und Kontakt- und Meldeweg bereit. Die Rechtstexte sind als Entwurf zur anwaltlichen Prüfung gekennzeichnet. Die App verlinkt sie, und die deutsche App-Übersetzung ist vollständig.

## Kontext & Abhängigkeiten

- **Voraussetzung:** Task 22 archiviert (`docs/data-inventory.md` als Grundlage der Datenschutzerklärung); Tasks 17, 18, 21 (Anbieterliste: Hosting, Supabase, Mistral, Firebase, Fehler-Tracking).
- **Relevantes Vorwissen:** `docs/architecture.md` → Website (Astro i18n, `defaultLocale: 'en'`, GitHub Pages), `docs/testing.md` (Vitest, Playwright mit Accessibility-Basisprüfungen), `website/src/pages/index.astro` (Starter), Produktentscheidungen (18+, Deutsch als zweite Sprache).

## Umfang

**Gehört dazu:**

- Astro-i18n für `en` und `de`, Strings in `website/src/i18n/`.
- Landingpage: Hero, „So läuft eine Partie" (vier Runden), Prinzipien (Verstehen vor Gewinnen, Anonymität, KI-Transparenz, Datensparsamkeit), FAQ, Platzhalter für Store-Links, Screenshots aus `app/screenshots/`.
- Seiten: Impressum, Datenschutzerklärung (Art.-9-Einwilligung, Verarbeiter mit Standort, Fristen aus Task 22, Rechte, Kontakt), Nutzungsbedingungen mit Verhaltensregeln (sachlich ja, Menschenverachtung nein; Sanktionen), KI-Hinweis (was das LLM tut, wie bewertet wird, Einspruch), Kontakt und Meldeweg für rechtswidrige Inhalte. Jede Seite trägt sichtbar „Entwurf – anwaltliche Prüfung ausstehend", bis Task 29 sie freigibt.
- App: Bereich „Rechtliches" in den Einstellungen mit Links; Einwilligungsbildschirm verlinkt die Datenschutzerklärung; Einwilligungsversion an die Textversion koppeln.
- Vollständige deutsche Übersetzung aller ARB-Schlüssel und Backend-Nachrichten; sprachliche Durchsicht.
- Playwright-E2E: alle Seiten in beiden Sprachen erreichbar, `lang`-Attribut, Überschriftenstruktur, Alt-Texte, Sprachumschalter.

**Gehört nicht dazu:**

- Anwaltliche Prüfung (Nutzeraufgabe), eigene Domain (offen), Store-Einträge (Task 26).

## Umsetzungsschritte

1. Rote Playwright- und Vitest-Tests für Seiten, Sprachen und Accessibility-Basis schreiben.
2. i18n-Struktur und Landingpage umsetzen.
3. Rechtstexte als Entwürfe aus `docs/data-inventory.md` und der Anbieterliste erstellen; Platzhalter für Angaben, die nur der Nutzer liefern kann (Name, Anschrift für das Impressum), deutlich markieren und erfragen.
4. App-Links und Kopplung der Einwilligungsversion per Widget-Tests.
5. Deutsche Übersetzung vervollständigen; ARB-Vollständigkeitstest aus Task 03 grün.
6. Deploy über den bestehenden Workflow `website.yml` prüfen.

## Tests

Alle Tests dieses Tasks werden permanent in den Test-Suites der Teile abgelegt (`website/tests/`, `app/test/`; siehe `docs/testing.md` und `AGENTS.md`). TDD: erst roter Test, dann Code.

- E2E: jede Seite in `en` und `de`, korrektes `lang`, genau eine `h1`, alle Bilder mit Alt-Text, Sprachumschalter funktioniert, Entwurfshinweis sichtbar.
- Unit: i18n-Hilfsfunktionen, keine fehlenden Schlüssel zwischen `en` und `de`.
- App: Links öffnen die richtige URL je Sprache; geänderte Textversion verlangt neue Einwilligung.

## Akzeptanzkriterien

Der Task gilt erst als fertig, wenn alle Punkte erfüllt und durch Tests oder einen konkreten Befehl belegt sind:

- [ ] `npm test`, `npm run test:e2e`, `npm run lint`, `npm run format:check`, `npm run check` grün; App-Definition-of-Done erfüllt.
- [ ] Website ist unter `https://sphaerox.github.io/Dicrates/` in beiden Sprachen live.
- [ ] Liste der vom Nutzer zu liefernden Angaben und der Punkte für den Anwalt steht in den Notizen und in `Roadmap/README.md`.

## Offene Fragen / Annahmen

- **Nutzer liefert:** Angaben für das Impressum (Name, ladungsfähige Anschrift, Kontakt).
- Anwaltliche Prüfung ist Voraussetzung für Task 29.

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
