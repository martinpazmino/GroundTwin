# Routinen für Antigravity (geplante Aufgaben auf dem Rechner des Nutzers)

Der Nutzer legt in Antigravity eine geplante Aufgabe an; die Anweisung dort ist nur eine Zeile:

> Lies `agenten/routinen/README.md` und führe `agenten/routinen/<name>.md` aus.

So steht der eigentliche Auftrag versioniert im Repository (docs/31: Prosa so kurz wie möglich, Prüfungen davor).

## Regeln für jede Routine

1. **Stand holen:** `git fetch origin` und von `origin/main` aus arbeiten, im Arbeitsbaum `../gt-routine`
   (`git worktree add -B agy/routine-<name> ../gt-routine origin/main`; vorhanden: `git -C ../gt-routine reset --hard origin/main`).
   Nie im Arbeitsbaum des Nutzers.
2. **Nur die erlaubten Dateien** der Routine ändern. Geschützt bleibt alles aus `AGENTS.md` Punkt 8.
3. **Vor dem Push** grün: `python -m pytest -q tests/test_hausregeln.py tests/test_funktionskarte.py` und
   `python -m agenten doku`. Sonst nicht pushen, sondern den Bericht schreiben.
4. **Push nur auf den eigenen Zweig** `agy/routine-<name>` (`git push -u origin agy/routine-<name>`, nie `--force`,
   nie `main`). Claude prüft und führt zusammen (Squash). Ein Zweig je Routine, er wird jedes Mal neu von main aus gebaut.
5. **Nichts geändert → nichts pushen.** Dann nur der Bericht.
6. **Bericht** immer: `agenten/routinen/berichte/<name>.md` im Zweig (oder, ohne Änderung, als Antwort der Aufgabe):
   Datum, was geprüft, was geändert (mit Beleg), was offen ist. Kurz.
7. Code, Kommentare, Meldungen auf Deutsch; Dokumentation auf Englisch mit deutschen Fachbegriffen (`docs/glossary.md`).
   Keine Gutachten-PDFs, keine Schlüssel, keine Kennungen von Claude-Modellen in Dateien.
8. Was du nicht sicher entscheiden kannst: in den Bericht, nicht raten.

## Routinen

| Datei | Rhythmus | Push | Was |
|---|---|---|---|
| `readme_aktualisieren.md` | wöchentlich | ja (Doku) | README und Index der Doku auf den Stand des Codes bringen |
| `doku_pflege.md` | wöchentlich | ja (Doku) | CHANGELOG aus den Commits, tote Links, Doku ↔ Code (Funktionskarte, Entscheidungen) |
| `dienste_pruefen.md` | wöchentlich | nur Bericht | alle Dienste der Länder vom Rechner des Nutzers aus ansprechen |
| `regression.md` | wöchentlich | nur Bericht | Regression auf den echten PDFs des Nutzers (liegen außerhalb des Repositorys) |
| `regeln_audit.md` | alle zwei Wochen | ja (Doku) | Regeln in CLAUDE.md/docs/16: welche schon Prüfung sind, welche Prosa; Vorschläge |
| `abhaengigkeiten.md` | monatlich | nur Bericht | veraltete oder unsichere Pakete (pip, npm), Lizenzen |
| `test_luecken.md` | wöchentlich | ja (Tests) | eine Funktion der Karte mit dünnem Beweis: ein Test mehr |
