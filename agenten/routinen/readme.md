# Routine: README und Index der Doku

**Erlaubt:** `README.md`, `docs/README.md`, `services/*/README.md`, `apps/web/README.md`, `benchmark/README.md`.

1. Lies die Commits seit dem letzten Lauf: `git log --since="8 days ago" --oneline origin/main` und `CHANGELOG.md` [Unreleased].
2. Prüfe gegen den Code, nicht gegen dein Gedächtnis:
   - Startbefehle (`python -m server`, `start.bat`, Port 8500), Variablen in `server/` (`GEO_AGENT_*`), Python- und Node-Version
     (`Dockerfile`, `.github/workflows/pruefungen.yml`), Lizenz AGPL-3.0-or-later, Link *Quellcode*.
   - Funktionen: `docs/feature_map.json` (Name, Schritt, eingeklappt). Eine Funktion, die dort steht und im README fehlt,
     kommt mit einem Satz dazu; nichts erfinden, was nicht in der Karte steht.
   - `docs/README.md`: jede Datei `docs/NN_*.md` hat eine Zeile, keine Zeile ohne Datei.
3. Ändere nur, was nachweislich veraltet ist; Stil und Aufbau bleiben. Keine Werbesprache, keine Zahlen ohne Beleg
   (Blind- und Trainingszahlen nie mischen, docs/15).
4. Regeln 3–6 aus `agenten/routinen/README.md`.
