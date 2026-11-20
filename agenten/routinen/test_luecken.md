# Routine: eine Testlücke schließen

**Erlaubt:** neue Testfunktionen in `tests/test_*.py` (nicht `test_hausregeln.py`, nicht `test_funktionskarte.py`),
die Spalte `beweis.tests` in `docs/feature_map.json`. Kein Code außerhalb von `tests/`.

1. Wähle **eine** Funktion aus `docs/feature_map.json` mit dem dünnsten Beweis (kein Test, nur e2e, oder ein Test
   ohne Fehlerfall). Nicht dieselbe wie im letzten Bericht.
2. Schreibe einen Test, der ein echtes Verhalten prüft (auch einen Fehlerfall: ungültige Eingabe → ValueError/400).
   Ohne Netz, ohne echte Gutachten (Beispiele aus `data/beispiele`).
3. Zeige, dass er etwas fängt: die geprüfte Zeile kurz kaputt machen, Test rot, zurück (im Bericht nennen, welche).
   Ein Test, der dabei grün bleibt, wird verworfen.
4. Findet der Test einen Fehler im Code: **nicht** den Code ändern. Test als `xfail(strict=True)` mit Grund und den
   Fehler oben in den Bericht („Issue vorschlagen“).
5. Eintrag in `beweis.tests` der Karte, dann Regeln 3–6 aus `agenten/routinen/README.md`.
