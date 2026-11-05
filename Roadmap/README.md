# Dicrates – Roadmap

Projektübergreifendes Gedächtnis. Agenten lesen diese Datei vor jedem Task und aktualisieren sie, wenn sich etwas ergibt, das über einen einzelnen Task hinausgeht. Regeln für die Arbeit: [AGENTS.md](AGENTS.md).

## Projektziel

Dicrates macht Debattieren zum Spiel: Drei bis sechs Personen diskutieren anonym eine aktuelle, konkret formulierte und gern kontroverse Streitfrage in vier asynchronen Runden. Ein LLM fasst die Positionen zusammen, schlägt einen Kompromiss vor und vergibt Punkte für Verstehen, Argumentqualität und Kompromissbereitschaft statt für Rechthaben.

Ziel dieser Roadmap ist **Produktionsreife des MVP (Phase 1)**: Nach einer geschlossenen Beta ist die App öffentlich im Google Play Store und im Apple App Store verfügbar, betrieben in der EU, mit Einwilligung, Löschkonzept, Moderation und Rechtstexten.

**Was die Software tut:** Ein angemeldeter Nutzer (18+) erstellt einen Freundesraum, wählt eine vom LLM aus aktuellen News oder zeitlosen Debatten vorbereitete und vom Betreiber freigegebene Streitfrage sowie die Rundendauer und lädt per Code oder Link 2 bis 5 weitere Personen ein. In Runde 1 gibt jede Person blind ihre Position mit Begründung ab (Text oder Spracheingabe auf dem Gerät). In Runde 2 sehen alle nur ein LLM-Gruppenbild (keine Einzelmeinungen, keine Verteilung) und überarbeiten ihre Position oder bleiben begründet dabei. In Runde 3 zeigt eine Zusammenfassung, was sich bewegt hat, und es gibt Feedback zu Argumenten. In Runde 4 liefert das LLM Gesamtbild, Kompromissvorschlag mit Pro und Contra sowie Punkte je Dimension mit Begründung. Push-Benachrichtigungen begleiten die Runden, alles ist vorlesbar.

**Zielgruppe:** Für das MVP Freundes-, Familien- und Kollegenrunden ab 18 Jahren, zunächst mit App-Sprache Englisch und Deutsch.

**Nicht-Ziele:** Öffentliches Matching mit Warteschlange, Rating (Elo/Glicko) und Trust-Score mit Troll-Pool, Reset-Regeln, Web-Admin-Oberfläche, europäische Räume, Live-Modus, Leichte Sprache, Bildungs- und Premium-Angebote (alles Phase 2/3, siehe Ausblick unten). Grundsätzlich nie: soziales Netzwerk mit Profilen, Followern oder Kommentarspalten; Verkauf von Rohdaten; politische Werbung.

## Aktueller Status

Stand: 2026-11-05 – Roadmap angelegt, noch kein Task begonnen.

| Task | Titel | Status |
|---|---|---|
| 01 | Backend-Skelett + CI | offen |
| 02 | Lokales Supabase, DB und Jobs | offen |
| 03 | App-Skelett + CI | offen |
| 04 | Anmeldung end to end | offen |
| 05 | LLM-Schicht | offen |
| 06 | Fragenbibliothek + Admin-CLI | offen |
| 07 | News-Pipeline für Streitfragen | offen |
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
- **Kein Root-Ordner `tests/`:** Das Prüfskript des Roadmap-Skills meldet dessen Fehlen als Fehler; das ist hier gewollt (siehe Entscheidung oben).
- **Ausblick Phase 2/3 (nicht Teil dieser Roadmap):** Interessen und Matching-Warteschlange, öffentliche Räume, Rating und Trust-Score mit Troll-Pool und Reset-Regeln, Web-Admin, Verteilungsanzeige per A/B-Test, optionale Anonymität in Freundesräumen, europäische Räume, Live-Modus, Leichte Sprache, Statistiken, Saisons, Bildungs- und Premium-Angebote.
