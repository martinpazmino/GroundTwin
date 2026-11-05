# GroundTwin — Auftrag für Agenten (nicht Claude)

Kurzspezifikation für Agenten außer Claude (Gemini über `python -m agenten`, Antigravity per Übergabe). Die
vollständigen Regeln stehen in `CLAUDE.md`, `docs/16_lessons_learned.md` (P, E, G, L/T, B, W, S, R, M, X),
`docs/17_extraction_algorithm.md`, `docs/18_layer_modeler.md` und `docs/21_app_schritte_normen.md`; hier nur, was
jeder Auftrag einhalten muss.

**Ziel des Projekts:** aus einem Bodengutachten (PDF) geprüfte, nachvollziehbare Bohrungen und ein IFC-4.3-Baugrundmodell.

**Unverhandelbar:**
1. Regressionstests nie abschwächen: keinen Test löschen, überspringen oder lockern, keine Baseline senken.
2. Blindtest: keine Blind-PDFs, keine Grundwahrheit vor dem Einfrieren; Blind- und Trainingszahlen nie mischen.
3. Keine Ausnahmen für ein PDF oder ein Büro: nur allgemeine Regeln aus Merkmalen der Zeichnung.
4. Unsichere geotechnische Werte markieren (Hinweis, niedrige Konfidenz, unklassifiziert), nie still übernehmen.
5. Herkunft und Konfidenz jeder Angabe erhalten.
6. IFC 4.3 gültig, Einheit METRE, exakte Kontakte, geschlossene Körper.
7. Grundlegende Architektur nur mit technischer Begründung ändern.
8. Geschützt (nur mit ausdrücklicher Freigabe): `services/extractor/prototyp_v4.py`, `benchmark/`,
   `constraints.txt`, `.github/workflows/`, `CLAUDE.md`, `LICENSE`, `agenten/`.

**Sprache:** Code, Kommentare und Oberfläche auf Deutsch; Dokumentation auf Englisch mit den deutschen Fachbegriffen
(Bohrung, Schicht, GOK, Lageplan …).

**Antwort:** immer das verlangte JSON, knapp; jede Aussage mit Beleg (Datei:Zeile); was unsicher ist, als unsicher.
