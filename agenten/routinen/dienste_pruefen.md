# Routine: Dienste der Länder prüfen (nur Bericht)

**Erlaubt:** nur der Bericht. `services/geodaten/geodaten/dienste.json` ändert diese Routine **nicht** (ein Eintrag wird
nie ohne Beleg als geprüft markiert; das macht ein Mensch im Werkzeug `dienste.html`).

1. `python scripts/dienste_pruefen.py` (Windows: `.venv\Scripts\python scripts\dienste_pruefen.py`) auf diesem Rechner.
2. Bericht je Dienst, der nicht geht: Land, Art (Bohrungen/DGM/LoD2), Fehler (DNS, TLS, HTTP), seit wann
   (Vergleich mit dem letzten Bericht in `agenten/routinen/berichte/dienste_pruefen.md`).
3. Ein Dienst, der zweimal hintereinander ausfällt: im Bericht oben als „Issue vorschlagen“ mit der Fehlerzeile.
4. Bericht auf den Zweig `agy/routine-dienste_pruefen` (Regeln 1, 4, 6 aus `agenten/routinen/README.md`).
