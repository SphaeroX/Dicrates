# Debattier-App – Projektbeschreibung

**Arbeitstitel:** Debattier-App (Name noch offen)
**Stand:** 05.11.2026
**Zweck dieses Dokuments:** Gesamtbild der Idee für die Projektplanung und Umsetzung. Es enthält alles, was bisher festgelegt wurde, plus Vorschläge für die technische Umsetzung.

**Kennzeichnung der Aussagen**

- **[Fest]** = Teil der ursprünglichen Idee, so gewollt.
- **[Vorschlag]** = Empfehlung, die noch bestätigt oder verändert werden kann.
- **[Offen]** = Entscheidung steht noch aus (gesammelt in Kapitel 20).

---

## 1. Vision und Problem

**[Fest]** Die App macht Debattieren zum Spiel. Mehrere anonyme Personen setzen sich gemeinsam mit einem aktuellen Thema auseinander, hören einander zu und werden dafür belohnt, andere Standpunkte zu verstehen und Kompromisse zu finden, nicht dafür, Recht zu behalten.

**Das Problem:** In sozialen Medien werden Kommentare nur noch abgeworfen, ohne dass echte Diskussion entsteht. Im echten Leben muss man aber den eigenen Standpunkt verteidigen, fremde Standpunkte verstehen und kompromissbereit sein.

**Die Idee dahinter:**

- Menschen setzen sich aktiv mit aktuellen Themen auseinander, aus ihrem Interessengebiet und manchmal bewusst auch darüber hinaus.
- Die Kommunikation in der Gesellschaft wird angeregt, ebenso das Zuhören und das Verständnis für andere.
- Man erlebt, dass Kompromissbereitschaft zu einer besseren Lösung führen kann als die, die man anfangs im Kopf hatte.
- Leitgedanke ist Sokrates: „Ich weiß, dass ich nichts weiß.“
- Auch kontroverse und populistisch aufgeladene Fragen sollen vorkommen (z. B. ein dritter Geschlechtseintrag „divers“ im Personalausweis), aber sachlich und ordentlich diskutiert werden, sodass man andere Sichtweisen in die eigene Meinung einfließen lassen kann.

## 2. Ziele und Nicht-Ziele

**Ziele**

- Ein Spielerlebnis, das echte Diskussion mit Zuhören und Kompromissfindung erzeugt.
- Niedrige Hürde: anonym, auch per Sprache bedienbar, auch für introvertierte Menschen und für Menschen, die ungern tippen.
- Faire, nachvollziehbare Bewertung durch ein LLM.
- Skalierbares Matching mit Rankingsystem, das Erfahrene und Neulinge sowie Trolle trennt.
- Tragfähiges Finanzierungsmodell ohne Vertrauensverlust.

**Nicht-Ziele (zunächst)**

- Kein soziales Netzwerk mit Profilen, Followern oder freien Kommentarspalten.
- Kein Live-Chat in Echtzeit als Pflicht (siehe Kapitel 7, asynchron als Vorschlag).
- Kein Verkauf von Rohdaten der Nutzer (siehe Kapitel 17 und 18).

## 3. Zielgruppe

**[Offen]** Wer zuerst erreicht werden soll, beeinflusst Ton, Moderationsstrenge und Marketing. Denkbare Gruppen:

- Politik- und gesellschaftlich Interessierte
- Freundes-, Familien- und Kollegenrunden (Gesellschaftsspiel)
- Schulen, Bildungseinrichtungen, Organisationen (später)

## 4. Kernprinzipien (für alle Entscheidungen im Projekt)

1. **Verstehen vor Gewinnen.** Punkte belohnen Argumentqualität und Offenheit, nicht Lautstärke oder Durchsetzung.
2. **Anonymität.** Niemand sieht, wer welche Meinung vertritt. Das nimmt Vorurteile heraus.
3. **Gruppenbild statt Einzelmeinungen.** Das LLM verdichtet, die Nutzer sehen Argumente statt Personen.
4. **Barrierefreiheit von Anfang an.** Sprechen, Vorlesen, Screenreader.
5. **Neutralität und Transparenz** des LLM, besonders bei politischen Themen.
6. **Datensparsamkeit.** Politische Meinungen sind besonders schützenswerte Daten.

## 5. Begriffe

| Begriff | Bedeutung |
|---|---|
| Partie / Raum | Eine Diskussionsrunde mit bis zu 6 Personen zu einer Streitfrage |
| Streitfrage | Konkret und neutral formulierte Frage, vom LLM erzeugt |
| Runde | Ein Abschnitt der Partie (vier Runden pro Partie) |
| Position | Haltung der Person (Skala oder eigener Vorschlag) plus Begründung |
| Gruppenbild | LLM-Zusammenfassung aller Positionen und Argumente |
| Kompromissvorschlag | Vom LLM erarbeiteter Vorschlag am Ende der Partie |
| Rating | Zahl, die Erfahrung und Spielstärke abbildet, steuert das Matching |
| Trust-Score | Eigener Wert für Verhalten, steuert die Trennung von Trollen |
| Freundesraum | Privater Raum mit Einladungscode |

## 6. Nutzer, Konto und Profil

- **[Fest]** Nutzer melden sich an und wählen Themengebiete, die sie interessieren (z. B. Sport, Wirtschaft, Politik).
- **[Vorschlag]** Anmeldung per E-Mail sowie Sign in with Apple und Google. Kein Klarname nötig, ein Pseudonym im Profil genügt. Intern hat jede Person ein eindeutiges Konto (wichtig für Moderation und Missbrauchsschutz, auch wenn die Partie anonym ist).
- **[Vorschlag]** Profilfelder: Interessengebiete (Mehrfachauswahl), Sprachen, Spielsprache, Rating, Trust-Score, Statistik (Partien, Punkteentwicklung), Barrierefreiheitseinstellungen (Vorlesen, Leichte Sprache, Schriftart).
- **[Offen]** Altersgrenze (z. B. 16+ oder 18+).

## 7. Spielmodi und Raumbildung

### 7.1 Öffentlicher Modus (Matching)

- **[Fest]** Ein Raum fasst bis zu 6 Personen.
- **[Fest]** Gematcht werden Personen mit den meisten Überschneidungen bei den Themen. Aus dem Gebiet mit der häufigsten Überschneidung wird ein aktuelles Thema gemacht.
- **[Fest]** Sprachräume: Entweder rein deutschsprachige Räume oder später auch europäische Räume mit europäischen Themen. Die App ist potenziell mehrsprachig.
- **[Fest]** Rankingabhängiges Matching: Erfahrene spielen gegen Erfahrene, Neulinge arbeiten sich hoch. Trolle werden abgestuft und spielen nur noch mit Trollen (siehe Kapitel 13 und 14).
- **[Fest]** Gelegentlich darf das Thema auch außerhalb des Kerninteresses liegen, um den Horizont zu erweitern.

**[Vorschlag] Matching-Algorithmus (Grundidee):**

1. Spieler tritt der Warteschlange bei (Sprache, Interessen, Rating, Trust-Band).
2. Ein Job bildet periodisch Gruppen: gleiche Sprache und Trust-Band, ähnliches Rating (Toleranzband, das mit Wartezeit wächst), maximale Themenüberlappung.
3. Mindestgröße einer Gruppe (z. B. 4) mit Zielgröße 6. Bei langer Wartezeit wird das Band erweitert, aber nie über Trust-Grenzen hinweg.
4. Das häufigste gemeinsame Themengebiet bestimmt die Streitfrage (Kapitel 8).

### 7.2 Freundesräume

- **[Fest]** Man kann auch privat mit Freunden und Bekannten spielen, Beitritt über Einladungscode oder Link. Es ist eine Art Gesellschaftsspiel.
- **[Vorschlag]** Anonymität in Freundesräumen optional einstellbar (Familie, Kollegen, Schulklassen können sie wollen, Freunde brauchen sie oft nicht).
- **[Vorschlag]** Der Ersteller wählt Themengebiet oder konkrete Streitfrage, Sprache und Rundendauer. Punkte aus Freundesräumen können getrennt oder mit geringerer Gewichtung ins Rating einfließen, damit das Ranking nicht manipuliert werden kann (**[Offen]**).

### 7.3 Synchron oder asynchron

- **[Offen, wichtige Produktentscheidung]** Live (alle gleichzeitig online) oder asynchron (jede Runde läuft z. B. 12 bis 24 Stunden).
- **[Vorschlag]** Asynchron als Standard. Vorteile: Matching wird einfacher (keine gleichzeitige Verfügbarkeit nötig), durchdachtere Antworten, besser für Sprache und Barrierefreiheit. Ein Live-Modus für Freundesräume kann später folgen.
- **[Vorschlag]** Timeout-Regeln: Runde schließt nach Fristablauf. Wer nicht abgibt, bekommt für die Runde keine Punkte. Mindestbeteiligung (z. B. 4 von 6) nötig, sonst wird die Partie abgebrochen ohne Punktabzug für die Teilnehmenden.

## 8. Themen und Streitfragen

- **[Fest]** Fragestellung, Auswertung und Bewertung laufen über LLMs im Backend.
- **[Fest]** Die Themen sind aktuell (Nachrichtenlage). Beispiele reichen von Sport und Wirtschaft bis zu kontroversen gesellschaftlichen Fragen.
- **[Fest]** Die Themen sollen konkret sein: Man ist dafür oder dagegen, oder man hat einen konkreten Vorschlag, je nach Fragestellung. Offene Wertungen wie „Ist es gut, dass …“ sind zu unscharf.

**[Vorschlag] Fragenformate**

1. **Dafür/Dagegen:** „Sollte X eingeführt werden?“ mit 5-stufiger Skala (klar dagegen … klar dafür) plus Begründung.
2. **Vorschlagsfrage:** „Wie sollte X geregelt werden?“ mit freiem Vorschlag plus Begründung.
3. **Abwägung:** „Was sollte Vorrang haben, A oder B?“

**[Vorschlag] Themen-Pipeline**

1. **Quellen:** Verlässliche Nachrichtenquellen (RSS oder News-API, kuratierte Liste, mehrere politische Richtungen).
2. **Kandidaten:** Das LLM extrahiert strittige, aktuelle Themen und ordnet sie Themengebieten zu.
3. **Formulierung:** Das LLM formuliert eine neutrale, konkrete Streitfrage und einen kurzen Faktenkasten mit Quellenangaben (damit alle auf demselben Stand sind und das LLM nichts erfindet).
4. **Prüfung:** Automatischer Neutralitäts- und Sicherheitscheck (keine suggestive Wortwahl, keine verbotenen Inhalte, kein Aufruf zu Gewalt).
5. **MVP:** Zusätzlich menschliche Freigabe oder eine kuratierte Fragenliste, bis die Qualität der Pipeline belegt ist.

**Beispiele für Streitfragen** (neutral formuliert, zur Illustration)

- „Soll im Personalausweis neben „männlich“ und „weiblich“ auch „divers“ als Geschlechtseintrag möglich sein?“
- „Soll ein generelles Tempolimit auf Autobahnen eingeführt werden?“

## 9. Spielablauf im Detail

Eine Partie besteht aus vier Runden. **[Fest]** ist das Grundprinzip, **[Offen]** sind Dauer und genaue Zahl der Runden, die ausdrücklich noch veränderbar sind.

### Runde 1 – Meinung abgeben (blind)

- Alle sehen dieselbe Streitfrage und den Faktenkasten.
- **[Fest]** Jede Person gibt ihre Meinung ab: dafür, dagegen oder ein konkreter Vorschlag, je nach Frage, mit Begründung. Sie sieht dabei keine anderen Meinungen (kein Ankereffekt, kein Mitläufertum).
- **[Vorschlag]** Eingabe: Skalenwert plus Begründung als Text oder gesprochen.
- **[Vorschlag]** Vor der Weitergabe filtert das LLM Beleidigungen und Hassrede (siehe Kapitel 14).

### Runde 2 – Gruppenbild lesen, Position überarbeiten

- **[Fest]** Die Nutzer sehen keine Einzelmeinungen. Das LLM fasst alle Meinungen zu einer Gesamtzusammenfassung zusammen: wie die anderen das sehen, welche Hauptargumente kommen, welche Randthemen besprochen werden.
- **[Fest]** Danach kann jede Person ihre Position überarbeiten oder bewusst dabei bleiben.
- **[Vorschlag] Anforderungen an das Gruppenbild:**
  - Jede Position in ihrer stärksten Form darstellen, auch Minderheitenmeinungen mit gutem Argument sichtbar machen (Zusammenfassungen neigen sonst zur Mitte).
  - Neutraler Ton, keine Wertung.
  - Keine Rückschlüsse auf Einzelpersonen (Stil glätten).
  - **[Offen]** Verteilung anzeigen („4 dafür, 2 dagegen“)? Das gibt Information, erzeugt aber sozialen Druck. Per A/B-Test klären.
  - Kurze Rückfrage „Wurde deine Position fair dargestellt?“ als Qualitätssignal für das LLM.

### Runde 3 – Bewegung der Gruppe und Feedback

- **[Fest]** Es werden die überarbeiteten Standpunkte gezeigt: Hat sich etwas geändert?
- **[Fest, so entschieden]** Auch hier erscheint eine Zusammenfassung („was hat sich in der Gruppe bewegt?“) statt der einzelnen anonymen Positionen. Das schützt die Anonymität besser.
- **[Fest]** Die Nutzer können Feedback zu den anderen Standpunkten geben: was sie sich gewünscht hätten, ob etwas gut war oder nicht.
- **[Vorschlag]** Feedback bezieht sich auf Argumente (nicht auf Personen), z. B. „hilfreich“, „überzeugend“, „unklar“, „hier fehlt etwas“, plus optionaler Freitext. Es fließt als schwaches Zusatzsignal in die Bewertung ein, das LLM bleibt Hauptbewerter (Manipulationsgefahr).

### Runde 4 – Auswertung

- **[Fest]** Das LLM liefert eine Zusammenfassung, wie die Gruppe das Thema sieht, einen Kompromissvorschlag sowie Pro und Contra dazu.
- **[Fest]** Es werden Punkte vergeben: wie gut sich die Nutzer geschlagen haben, wie gut sie argumentiert haben, ob sie auf andere zugegangen sind, um die bestmögliche Lösung für die Gruppe zu finden.
- **[Fest]** Am Ende können die Nutzer offenes Feedback zur Runde und zu den Meinungen geben, wie sie die Runde empfunden haben.
- **[Vorschlag]** Zwei Feedbackarten trennen: (a) Feedback zur Partie (Thema gut formuliert, Zusammenfassung fair?) verbessert Produkt und LLM-Prompts, (b) Feedback zu Teilnehmern (wer war konstruktiv?) nur als schwaches Zusatzsignal.

### Zustandsautomat einer Partie (Vorschlag)

```
FORMING → R1_OPEN → R1_CLOSED → R2_OPEN → R2_CLOSED → R3_OPEN → R3_CLOSED → R4_EVALUATING → FINISHED → ARCHIVED
              ↘ (zu wenige Abgaben nach Timeout) ABORTED
```

Übergänge laufen über Timer und Jobs. Jede Runde hat Start, Frist und Mindestbeteiligung.

## 10. Anonymität

- **[Fest]** Niemand sieht, welcher Spieler welche Meinung hat. Das blendet Vorurteile aus und hilft introvertierten Menschen, sich frei zu äußern.
- **[Vorschlag]** Umsetzung:
  - In der Partie nur anonyme Platzhalter oder gar keine Zuordnung. Die Zuordnung Konto ↔ Beitrag bleibt nur im Backend (für Moderation und Bewertung).
  - Das LLM gibt Beiträge nur als Zusammenfassung weiter und glättet den Sprachstil, damit niemand am Schreibstil erkannt wird (besonders in Freundesgruppen).
  - Bei Freundesräumen kann Anonymität optional sein.
  - Schutz vor Verantwortungslosigkeit: Konto im Hintergrund, Inhaltsfilter, Meldefunktion, Trust-Score.

## 11. Barrierefreiheit, Spracheingabe und Sprachausgabe

- **[Fest]** Eingaben nicht nur per Tippen, sondern auch per Sprache (viele tippen ungern oder schlecht). Alles lässt sich vorlesen.
- **[Vorschlag] Spracheingabe:**
  - Aufnahme in der App, Speech-to-Text (Plattform-API oder Cloud-Dienst, DSGVO-konform).
  - **Transkript vor dem Absenden anzeigen** und bearbeitbar machen (Dialekte, Akzente und Fachbegriffe machen Fehler). Das Transkript ist auch vorlesbar.
  - Audio wird nicht gespeichert und nie anderen vorgespielt. Nach der Transkription sofort löschen (Stimme ist ein identifizierendes Merkmal und widerspricht der Anonymität).
- **[Vorschlag] Sprachausgabe:** Streitfrage, Gruppenbild und Auswertung per Text-to-Speech mit neutraler, synthetischer Stimme (passt zur Anonymität).
- **[Vorschlag] Weitere Barrierefreiheit:** Screenreader-Unterstützung (VoiceOver, TalkBack), skalierbare Schrift, hohe Kontraste, Schriftart für Legastheniker, Leichte Sprache als Option (das LLM kann Zusammenfassungen vereinfachen), Bedienung ohne Feinmotorik. Ziel: WCAG 2.1 AA bzw. EU-Barrierefreiheitsanforderungen.

## 12. Mehrsprachigkeit

- **[Fest]** Potenziell mehrsprachig: reine Deutsch-Räume, später europäische Räume mit europäischen Themen.
- **[Vorschlag]** Start nur Deutsch. App-Texte von Anfang an in Sprachdateien (i18n) auslagern. LLM-Prompts parametrisiert nach Sprache. **[Offen]** Ob in europäischen Räumen gemischtsprachig diskutiert und vom LLM übersetzt wird oder nur Räume pro Sprache existieren.

## 13. Punktesystem und Ranking

- **[Fest]** Das Punktesystem wird vom LLM berechnet. Punkte können auch wieder verloren werden.
- **[Fest]** Je höher das Ranking, desto relevanter beim Matching: Erfahrene treten gegeneinander an, Neulinge müssen sich hocharbeiten.
- **[Fest]** Trolle werden komplett abgestuft und spielen nur noch mit Trollen.
- **[Fest]** Ein Punkte-Reset kann beantragt werden, aber nur selten (etwa einmal im Monat, bei klar negativem Verlauf durch Trollen länger).

**[Vorschlag] Bewertungskriterien** (je Dimension z. B. 0 bis 100, als strukturierte Ausgabe, z. B. JSON):

| Dimension | Frage an das LLM |
|---|---|
| Argumentqualität | Ist die Begründung nachvollziehbar, logisch, belegt? |
| Perspektivübernahme | Geht die Person auf Gegenargumente ein, stellt sie andere Sichtweisen fair dar? |
| Offenheit | Zeigt die Überarbeitung echte Auseinandersetzung (Anpassung ODER begründetes Festhalten)? |
| Kompromissbeitrag | Trägt die Person konstruktiv zur gemeinsamen Lösung bei? |
| Respekt und Ton | Sachlich, keine Herabwürdigung? |
| Beteiligung | Alle Runden abgeschlossen? |

**Wichtige Designregeln**

- Ein Positionswechsel an sich bringt **keine** Punkte, sonst wird taktisches Einknicken belohnt. Gut begründetes Festhalten darf nicht bestraft werden. Bewertet wird die Qualität der Auseinandersetzung.
- Argumentqualität und Offenheit werden getrennt bewertet.
- Mehrfachauswertung (z. B. zwei bis drei LLM-Läufe, Median oder Konsens) für stabile Ergebnisse. Einspruchsmöglichkeit für Nutzer.
- Teilnehmerfeedback der anderen nur als schwaches Zusatzsignal.

**Rating-Mechanik (Vorschlag):** Elo- oder Glicko-ähnliches Rating, das aus dem Partieergebnis (Gesamtpunkte relativ zur Gruppe und zur Erwartung) aktualisiert wird. Separater **Trust-Score** für Verhalten (Verstöße, Meldungen, Trolling-Indikatoren), der die Trennung von Trollen steuert. Rating = Können, Trust = Verhalten.

**Reset:** Antrag möglich, Sperrfrist (z. B. 30 Tage), bei negativem Verlauf deutlich länger. Ein Reset setzt das Rating zurück, aber nicht den Trust-Score.

## 14. Moderation und Sicherheit

- **[Fest]** Trolle werden abgestuft und isoliert (nur noch mit Trollen).
- **[Vorschlag]** Mehrstufiger Schutz:
  1. **Eingangsfilter:** Das LLM erkennt Beleidigungen, Hassrede, Gewaltaufrufe, Doxing und Spam, bevor Inhalte in Zusammenfassungen einfließen. Betroffene Beiträge werden ausgeblendet und gehen in den Trust-Score ein.
  2. **Zusammenfassung als zweiter Filter:** Da nur Zusammenfassungen angezeigt werden, kommen Provokationen kaum bei den anderen an.
  3. **Meldefunktion** für Themen, Zusammenfassungen und Nutzerverhalten.
  4. **Shadow-Pool:** Nutzer mit niedrigem Trust-Score landen in einem getrennten Pool.
  5. **Eskalation:** Verwarnung, temporäre Sperre, Ausschluss. Manueller Review-Kanal (Admin-Oberfläche).
  6. **Klare Regeln** für heikle Themen (Migration, Geschlechtsidentität usw.): sachliche Diskussion erlaubt, Menschenverachtung nicht.
  7. **Themen-Sicherheitscheck** vor der Veröffentlichung (siehe Kapitel 8).
- **[Offen]** Umgang mit rechtswidrigen Inhalten (Meldepflichten nach DSA/NetzDG-Nachfolge), mit Fachanwalt klären.

## 15. LLM-Aufgaben im Backend

**[Fest]** Alles läuft über LLMs im Hintergrund. Aufgabenliste:

| # | Aufgabe | Eingabe | Ausgabe |
|---|---|---|---|
| 1 | Themenerkennung | Nachrichtenartikel | Kandidaten, Themengebiete |
| 2 | Streitfrage formulieren | Kandidat, Quellen | Neutrale Frage, Faktenkasten |
| 3 | Neutralitäts- und Sicherheitscheck | Frage | OK / Überarbeitung / abgelehnt |
| 4 | Inhaltsfilter | Nutzerbeiträge | Freigabe, Flag, Kategorie |
| 5 | Gruppenbild Runde 2 | Alle Positionen | Zusammenfassung, Hauptargumente, Randthemen (ggf. Verteilung) |
| 6 | Zusammenfassung Runde 3 | Überarbeitete Positionen, Feedback | Veränderungen, offene Punkte |
| 7 | Auswertung Runde 4 | Alle Daten der Partie | Gruppenbild, Kompromissvorschlag, Pro/Contra |
| 8 | Punktebewertung | Verlauf je Teilnehmer | Punkte je Dimension, Begründung |
| 9 | Troll-/Verhaltensanalyse | Verlauf, Meldungen | Trust-Anpassung |
| 10 | Vereinfachte Sprache (optional) | Texte | Leichte Sprache |

**Qualität und Neutralität (wichtig, da das LLM das Ergebnis faktisch steuert)**

- Prompts versionieren und testen. Testset mit Beispielpartien (inklusive politisch verschiedener Richtungen und Minderheitenmeinungen).
- Bias-Tests: gleiche Argumente in Links-/Rechts-Framing, Ergebnis darf sich nicht systematisch verschieben.
- Transparenz: Die Nutzer sehen, wie bewertet wird (Kriterien), Bewertungen haben eine kurze Begründung.
- Einspruch- und Feedbackkanal.
- LLM-Anbieter abstrahieren (austauschbar), Kosten pro Partie überwachen, Ausgaben möglichst als strukturiertes JSON mit Validierung.
- Hinweis in der App, dass Zusammenfassungen und Bewertungen KI-generiert sind (Transparenzpflichten prüfen).

## 16. Technische Umsetzung (Vorschlag, Entscheidung beim Entwickler)

**Architektur**

- **Mobile App:** Cross-Platform für Android und iOS (z. B. Flutter).
- **Backend:** API-Server (z. B. Python/FastAPI oder Node/TypeScript), Job-Worker für Matching, Rundentimer und LLM-Aufrufe (Queue, z. B. Redis), PostgreSQL als Hauptdatenbank.
- **Benachrichtigungen:** Push (FCM und APNs) bei Rundenstart, Rundenende, Auswertung.
- **Auth:** E-Mail, Apple, Google. Sitzungen per Token.
- **Echtzeit:** Für den asynchronen Modus nicht nötig. Für Live-Modus später WebSockets.
- **LLM-Schicht:** Eigene Abstraktionsschicht, Prompt-Versionierung, Logging (ohne Klartext-Personenbezug), Retry und Validierung.
- **STT/TTS:** Plattform-APIs auf dem Gerät oder DSGVO-konforme Cloud-Dienste.
- **Admin-Oberfläche:** Moderation, Reports, Themenfreigabe, Prompt-Tests.
- **Hosting:** EU-Region.

**Datenmodell (Grobentwurf)**

| Entität | Wichtige Felder |
|---|---|
| User | id, E-Mail oder Provider-ID, Pseudonym, Sprache, Rating, Trust-Score, Reset-Datum |
| UserInterest | user_id, topic_area |
| TopicArea | id, Name (Sport, Wirtschaft, Politik …) |
| Question | id, Text, Format, Themengebiet, Sprache, Faktenkasten, Quellen, Status |
| Room | id, Typ (öffentlich/Freunde), Sprache, question_id, Status, Rundenfristen, Einladungscode, Anonymität |
| RoomMember | room_id, user_id, anonymer Platzhalter, Status |
| Round | room_id, Nummer, Start, Frist |
| Submission | round, member, Skalenwert, Text, Revision |
| Summary | round, Typ (Gruppenbild, Bewegung, Auswertung), Text, Prompt-Version |
| Feedback | round, von, Ziel (Argument), Typ, Text |
| Evaluation | room, member, Punkte je Dimension, Begründung |
| RatingHistory | user, Partie, Rating vorher/nachher |
| Report | von, Ziel, Grund, Status |
| ModerationEvent | user, Typ, Quelle (LLM/Mensch), Wirkung |

**Wichtige technische Punkte**

- Einmalige, deterministische Rundenübergänge (Idempotenz bei Jobs).
- Rechte: Nutzer sehen nur Inhalte ihres Raums, nur Zusammenfassungen, nie Rohdaten anderer.
- Löschfunktion für Konto und Beiträge.
- Monitoring: Fehlerquote der LLM-Aufrufe, Kosten, Abbruchrate der Partien.

## 17. Datenschutz und Recht

Wichtig, weil politische Meinungen nach DSGVO (Art. 9) besonders geschützte Daten sind. **Dies ist keine Rechtsberatung, bitte mit einer Fachperson (Datenschutz, Medien-/IT-Recht) abstimmen.**

- Ausdrückliche Einwilligung für die Verarbeitung der Meinungsbeiträge, Datenminimierung, Zweckbindung.
- Löschkonzept: Klartextbeiträge nach definierter Frist löschen oder anonymisieren. Dauerhaft behalten nur, was für Rating und Statistik nötig ist.
- LLM- und STT-Anbieter mit Auftragsverarbeitungsvertrag, EU-Verarbeitung bevorzugt, keine Nutzung der Nutzerdaten zum Training bei den Anbietern.
- Audio nicht speichern (Stimme identifiziert Personen).
- Jugendschutz und Altersgrenze klären. Impressum, Datenschutzerklärung, Nutzungsbedingungen mit Verhaltensregeln.
- Pflichten rund um Meldeverfahren für rechtswidrige Inhalte (DSA) und Kennzeichnung von KI (EU-KI-Verordnung) prüfen.
- Barrierefreiheit: Anforderungen des Barrierefreiheitsstärkungsgesetzes prüfen.

## 18. Monetarisierung

Ursprüngliche Gedanken: Daten aus dem Nutzerinput verwerten, später auch Werbung (eher nicht gern gesehen), dazu Fördergelder auf EU- oder Landesebene für Projekte, die gesellschaftlichen Zusammenhalt stärken.

**[Vorschlag] Einschätzung und Reihenfolge**

1. **Fördergelder** (EU, Land, Bundeszentrale für politische Bildung, Stiftungen, Demokratieförderprogramme): passt am besten zum Ziel und stärkt das Vertrauen.
2. **Bildungsangebote:** Lizenzen für Schulen, Hochschulen, Vereine und Unternehmen (Teamdebatten, Moderationstraining).
3. **Premium-Abo:** z. B. erweiterte Statistiken, Freundesräume ohne Limit, mehr Themenwahl.
4. **Daten:** Rohdaten zu politischen Meinungen sollten **nicht** verkauft werden (rechtlich heikel und vertrauenszerstörend). Möglich nur in aggregierter, anonymisierter Form mit Einwilligung, z. B. für Forschungskooperationen.
5. **Werbung:** nur als letzte Option, mit klaren Grenzen (keine politische Werbung, keine Personalisierung nach Meinungen).

## 19. MVP-Umfang und Phasen

**[Vorschlag] Phase 1 – MVP (Kernidee testen)**

- Nur Freundesräume mit Einladungscode
- Eine Streitfrage pro Partie (kuratiert oder LLM mit manueller Freigabe), nur Deutsch
- Kompletter Rundenablauf (R1 bis R4), asynchron, mit Push-Benachrichtigungen
- LLM-Gruppenbild, Bewegungs-Zusammenfassung, Auswertung mit Kompromissvorschlag
- Anonymität, Inhaltsfilter, Meldefunktion
- Einfache Punktevergabe (ohne Ranking)
- Eingabe per Text und Spracheingabe mit Transkript-Prüfung, Vorlesen
- Konto, Einwilligung, Löschfunktion

**Ziel von Phase 1:** Zeigen, dass die Kernidee Spaß macht und dass das LLM faire Zusammenfassungen liefert, ohne Matching, Ranking und aufwendige Moderation bauen zu müssen.

**Phase 2 – Öffentliche Räume**

- Interessen, Matching mit Warteschlange, automatische Themenpipeline aus Nachrichten
- Rating und Trust-Score, Shadow-Pool, Reset-Regeln
- Erweiterte Moderation und Admin-Oberfläche

**Phase 3 – Wachstum**

- Europäische Räume, weitere Sprachen
- Live-Modus, Bildungs- und Organisationsangebote, Premium
- Statistiken, Saisonen, Auszeichnungen

**Erfolgskriterien (Metriken, Vorschlag)**

- Anteil abgeschlossener Partien (Abbruchrate je Runde)
- Anteil der Nutzer, die ihre Position in Runde 2 überdenken oder begründet halten
- Wahrgenommene Fairness der Zusammenfassung (Rückfrage „fair dargestellt?“)
- Wiederkehrende Nutzung (Retention), Anzahl Freundesräume pro Nutzer
- Anteil gemeldeter oder gefilterter Beiträge

## 20. Risiken und offene Entscheidungen

**Risiken**

| Risiko | Gegenmaßnahme |
|---|---|
| Matching braucht viele Nutzer (Henne-Ei) | Asynchrone Runden, Freundesräume als Einstieg, Wartebänder erweitern |
| Punktesystem wird gespielt (Kompromissbereitschaft vortäuschen) | Argumentqualität und Offenheit trennen, Positionswechsel nicht belohnen, Mehrfachauswertung |
| Voreingenommenheit oder fehlendes Vertrauen in das LLM | Transparente Kriterien, faire Darstellung jeder Position, Bias-Tests, Einspruch |
| Minderheitenmeinungen gehen in Zusammenfassungen unter | Prompt-Vorgabe „stärkste Form jeder Position“, Rückfrage zur fairen Darstellung |
| Trolle und Hassrede | Filter, Meldefunktion, Trust-Score, Shadow-Pool, Review |
| Halluzinierte oder veraltete Fakten in Themen | Quellenbasierte Pipeline, Faktenkasten, menschliche Freigabe im MVP |
| Datenschutz (Art. 9 DSGVO) | Einwilligung, Datensparsamkeit, Löschkonzept, kein Datenverkauf |
| Kosten pro Partie (viele LLM-Aufrufe) | Kostenmonitoring, kleinere Modelle für Filter, Caching, Aufrufe bündeln |
| Stilerkennung trotz Anonymität | Zusammenfassungen statt Einzelbeiträge, Stil glätten |

**Offene Entscheidungen**

1. Zielgruppe zuerst (Politikinteressierte, Freundesgruppen, Schulen)?
2. Asynchron oder live (Vorschlag: asynchron)?
3. Genaue Rundenzahl und Rundendauer (z. B. 12 bis 24 Stunden)?
4. Verteilung („4 dafür, 2 dagegen“) im Gruppenbild anzeigen?
5. Wie Freundesräume ins Rating einfließen?
6. Mindestbeteiligung und Verhalten bei Nichtabgabe?
7. Altersgrenze der App?
8. Europäische Räume: pro Sprache getrennt oder mit Übersetzung?
9. Name und Branding der App?
10. Welche LLM-, STT- und TTS-Anbieter (EU-Hosting, Datenschutz, Kosten)?
11. Themenquellen für die Nachrichtenpipeline (welche Medien, welche Bandbreite)?
12. Lizenz und Open-Source-Frage, falls relevant.

---

*Dieses Dokument wird mit dem Projektfortschritt weiterentwickelt. Alle Punkte mit [Vorschlag] sind Diskussionsgrundlage für die Planung.*
