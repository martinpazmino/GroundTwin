# Routine: Regression auf den echten PDFs (nur Bericht)

**Erlaubt:** nur der Bericht. Keine Baseline schreiben (`--write` nie), `prototyp_v4.py` nie ändern.

Die PDFs liegen außerhalb des Repositorys (z. B. `..\gt-pdfs\real`, `..\gt-pdfs\stress`, `..\gt-pdfs\synth`; OCR-Cache
`..\gt-pdfs\ocr`). Fehlt ein Ordner: Stress- und Synthesefälle neu erzeugen (`benchmark/README.md`), echte nur nennen.

1. `set GEO_OCR_CACHE=..\gt-pdfs\ocr` und
   `python benchmark/regression.py --module services/extractor/prototyp_v4.py --real ..\gt-pdfs\real --stress ..\gt-pdfs\stress --synth ..\gt-pdfs\synth --baseline benchmark/baseline_v4.json`
2. Zusätzlich `python benchmark/perturb.py ..\gt-pdfs\real ..\gt-pdfs\raster raster150` und dieselbe Regression auf
   `raster/` ohne Baseline (nur SUMME notieren).
3. Bericht: SUMME, jede Zeile „REGRESSION“, Laufzeit je PDF, Vergleich mit dem letzten Bericht.
   „OK: keine Regression“ und gleiche SUMME → ein Satz genügt.
4. Bei REGRESSION: den Commit finden, seit dem es so ist (`git log -- services/extractor`), und oben im Bericht nennen.
5. Bericht auf den Zweig `agy/routine-regression` (Regeln 1, 4, 6 aus `agenten/routinen/README.md`).
