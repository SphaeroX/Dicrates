# Roadmap-Regelwerk für KI-Agenten – Dicrates

Diese Datei legt fest, wie Tasks dieses Projekts abgearbeitet werden. Lies sie vollständig, bevor du an einem Task arbeitest, und halte dich strikt daran. Die Regeln sind bewusst starr: Mehrere Agenten arbeiten nacheinander am selben Projekt, und nur ein einheitlicher Ablauf stellt sicher, dass jeder den Stand des Vorgängers findet.

## 1. Ordner-Logik

| Ort | Inhalt |
|---|---|
| `Roadmap/Tasks/` | Offene und aktuell laufende Tasks (`Task_01.md`, `Task_02.md`, ...). |
| `Roadmap/Archiv/` | Vollständig erledigte Tasks. |
| `backend/tests/`, `app/test/` (inkl. `app/test/screenshots/`), `app/integration_test/`, `website/tests/` (**nicht** in `Roadmap/`) | Die permanente Testing-Suite des Projekts, je Teil. Für dieses Monorepo vom Nutzer so festgelegt statt eines Root-Ordners `tests/`. |
| `Roadmap/README.md` | Projekt- und taskübergreifendes Gedächtnis: Ziel, Status, globale Entwicklungsinfos, Auffälligkeiten. |

## 2. Strikte Reihenfolge

Die Tasks in `Roadmap/Tasks/` werden streng numerisch nacheinander abgearbeitet: erst `Task_01`, dann `Task_02`, dann `Task_03` und so weiter. Es wird nie ein Task übersprungen, vorgezogen oder parallel begonnen. Der nächste Task ist immer der mit der kleinsten Nummer, der noch in `Roadmap/Tasks/` liegt.

Liegt dort eine Datei mit dem Präfix `RUN_`, ist das der laufende Task: Mache dort weiter, statt einen neuen zu beginnen. Es darf nie mehr als eine `RUN_`-Datei geben.

## 3. Start-Prozedur (`RUN`-Kürzel)

Wenn du einen Task beginnst, ist die **allererste Aktion** das Umbenennen der Task-Datei: Setze `RUN_` vor den Dateinamen.

```
Task_01.md  →  RUN_Task_01.md
```

Das passiert vor allem anderen: bevor du Code schreibst, planst oder recherchierst. So ist auf einen Blick erkennbar, welcher Task gerade läuft. Verwende `git mv`, wenn das Projekt ein Git-Repository ist.

Danach, in dieser Reihenfolge:

1. `Roadmap/README.md` lesen.
2. Den laufenden Task vollständig lesen.
3. Die Abschnitte "Erkenntnisse für Folge-Agenten" der Vorgänger-Tasks in `Roadmap/Archiv/` lesen, mindestens die der Tasks, von denen dieser Task abhängt.

## 4. Informations-Trennung

- **Taskspezifische** Informationen (Entscheidungen, Stolpersteine, Notizen zu diesem Task) gehören in die jeweilige Task-Datei.
- **Projekt- und taskübergreifende** Informationen (Architekturentscheidungen, globales Wissen, Besonderheiten, die mehrere Tasks betreffen) gehören in `Roadmap/README.md`.

Im Zweifel: Würde ein Agent bei einem *anderen* Task davon profitieren? Dann in die README.

## 5. Testing-Pflicht

Ist ein Task fertig programmiert, muss alles zwingend durch Testing bestätigt werden. Die dafür erstellten Tests liegen **permanent** in den Test-Suites der Teile (`backend/tests/`, `app/test/`, `app/integration_test/`, `website/tests/`) und bauen dort eine dauerhafte Testing-Suite auf. Sie werden nie in `Roadmap/` abgelegt und beim Archivieren eines Tasks nie gelöscht.

Testing-Suites, exakte Befehle (alle Tests, einzelne Datei, einzelner Test), Definition of Done und Screenshot-Goldens stehen verbindlich in `docs/testing.md`; Kurzfassung in der Root-`AGENTS.md`. Kurz: Backend `uv run pytest` (in `backend/`), App `flutter test` (in `app/`), Website `npm test` und `npm run test:e2e` (in `website/`), dazu die statischen Prüfungen je Teil.

Schlägt das Testing fehl, wird der Task nicht archiviert: Er bleibt als `RUN_Task_NN.md` in `Roadmap/Tasks/`, bis die Tests bestehen. Bestehende Tests werden nicht abgeschwächt oder gelöscht, um Grün zu erreichen; der Fehler liegt in der Implementierung.

## 6. Abschluss- und Archivierungs-Workflow

War das Testing erfolgreich, passieren vor dem Verschieben ins Archiv noch genau drei Dinge, in dieser Reihenfolge:

1. **Erkenntnisse dokumentieren.** Schreibe wichtige Erkenntnisse, Learnings und Details unten in die aktuelle Task-Datei, in den Abschnitt "Erkenntnisse für Folge-Agenten". Nachfolgende Agenten profitieren davon bei späteren Tasks.
2. **Folge-Tasks prüfen und anpassen.** Wenn vorne etwas fertig wird, ändert sich hinten oft etwas. Prüfe, ob sich für die darauffolgenden Tasks (`Task_02`, `Task_03` usw.) etwas geändert hat, und passe sie bei Bedarf an. Aktualisiere ebenso die `Roadmap/README.md`: den aktuellen Status und alle neuen taskübergreifenden Erkenntnisse.
3. **Ins Archiv verschieben.** Erst wenn Testing, Erkenntnis-Dokumentation und die Anpassung der Folge-Tasks erledigt sind, wird der Task **ohne** das `RUN_`-Präfix nach `Roadmap/Archiv/` verschoben:

   ```
   Roadmap/Tasks/RUN_Task_01.md  →  Roadmap/Archiv/Task_01.md
   ```

Danach kann der nächste Task begonnen werden (Abschnitt 3). Liegt in `Roadmap/Tasks/` kein Task mehr, ist die Roadmap abgeschlossen: Setze den Status in der `Roadmap/README.md` entsprechend und melde das dem Nutzer.

## 7. Zusammenspiel mit dem restlichen Projekt

Die Regeln der Root-`AGENTS.md` (striktes TDD mit Reparaturbudget, `backend/.venv` via uv, Privacy und Anonymität, i18n, Screen-Goldens, Conventional Commits) und der Dateien in `docs/` gelten zusätzlich; `docs/` wird im selben Task aktualisiert, wenn sich Stack, Architektur, Konventionen oder Testing ändern. Offene Produktentscheidungen (`docs/project-brief.md` → Open decisions) und die in den Tasks markierten Rückfragen werden nicht selbst entschieden, sondern beim Nutzer erfragt. Bei Widerspruch zu diesem Regelwerk anhalten und beim Nutzer nachfragen.
