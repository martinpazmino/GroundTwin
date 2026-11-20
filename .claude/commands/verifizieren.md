Vor "fertig": die Aenderung selbst beweisen (docs/31 §3.3).

1. In `docs/feature_map.json` die Funktionen finden, deren Routen, Operationen oder Module die Aenderung beruehrt.
2. Ihre Beweise laufen lassen: die genannten Tests (`python -m pytest <datei>::<test>`), dazu `tests/test_hausregeln.py`
   und `tests/test_funktionskarte.py`.
3. Neue Funktion: Eintrag in der Karte mit Schritt, *Erweitert* ja/nein und mindestens einem Beweis.
4. Oberflaeche geaendert: `npm run build` in apps/web, dist committen; die passenden Pruefungen aus
   `scripts/check_app.mjs` nennen oder laufen lassen.
5. Extraktion geaendert: Regression (Befehl in CLAUDE.md), ohne Rueckgang `--write` (schreibt Baseline und Huelle).
Dann das Urteil von `python -m agenten pruefen` lesen.
