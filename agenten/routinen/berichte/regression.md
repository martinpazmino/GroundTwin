# Bericht: Routine `regression`

**Datum:** 2026-11-22  
**Zweig:** `agy/routine-regression` (Basis: `origin/main` @ `52926f4`)

## Ergebnis & Befund (REGRESSION)

**Status:** `FEHLGESCHLAGEN` — 8 `REGRESSION`-Zeilen, alle ausschließlich bei `real/rednitzhembach`. Alle übrigen 12 echten PDFs, alle 27 Stressfälle (`s01`–`s27`) und alle 6 Synthesefälle (`synth_A`–`synth_B`) erreichen exakt die Baseline (`benchmark/baseline_v4.json`).

**Commit-Prüfung (`git log -- services/extractor`):**  
`52926f4` (HEAD), `0da913a`, `ce52894`, `a43206d`.  
In dieser Umgebung tritt der Fehler auf `real/rednitzhembach` bereits **seit dem ersten Commit `a43206d`** unverändert auf (geprüft: `a43206d`, `762c41c`, `3f3e364`, `0da913a` und `52926f4` liefern jeweils exakt dasselbe Ergebnis `3/4` Bohrungen, `8/15` Grenzen, `falsche Bohrungen: 2`, `falsche Grenzen: 6`, sowohl mit als auch ohne `GEO_OCR_CACHE`).

**Ursache (Umgebungsabweichung vs. Code):**  
Im verwendeten `.venv` ist `pymupdf` **2.1** (MuPDF `1.28.6`) installiert statt `pymupdf==2.0` (`constraints.txt:27`). Auf den Seiten 28 und 30 von `rednitzhembach.pdf` liefert `page.get_text("words")` unter `pymupdf` 2.1 für `'2'` bzw. `'4'` minimal kleinere `y0`-Koordinaten als für `'B'` (z. B. S. 28: `'2'` `y0=193.92`, `'B'` `y0=194.53`). `services/extractor/prototyp_v4.py:598` sortiert Wörter derselben Zeile nach `(x[0].y0, x[0].x0)` und setzt dadurch `'2 B'` und `'4 B'` statt `'B 2'` und `'B 4'` zusammen; `'B4'` auf Seite 35 wird entsprechend als falsche Bohrung ausgegeben. Im Rasterlauf (`raster150`, OCR statt eingebetteter PDF-Textlage) erreicht `rednitzhembach` `4/4` Bohrungen und `15/15` Grenzen (`0` falsche).

## REGRESSION-Zeilen (`benchmark/baseline_v4.json`)

```text
REGRESSION real/rednitzhembach: Bohrungen 4/4 -> 3/4
REGRESSION real/rednitzhembach: Grenzen 15/15 -> 8/15
REGRESSION real/rednitzhembach: Grenzen exakt 13/15 -> 6/15
REGRESSION real/rednitzhembach: Bodenart 12/15 -> 6/12
REGRESSION real/rednitzhembach: GOK 4/4 -> 3/4
REGRESSION real/rednitzhembach: GW-Status 4/4 -> 0/4
REGRESSION real/rednitzhembach: falsche Bohrungen 0 -> 2
REGRESSION real/rednitzhembach: falsche Grenzen 0 -> 6
```

## SUMME

- **Hauptlauf** (`real`, `stress_v3`, `synth` mit `GEO_OCR_CACHE=..\gt-pdfs\ocr_cache`):  
  `{'Bohrungen': '100/106', 'Grenzen': '594/614', 'Grenzen exakt': '586/614', 'Bodenart': '354/385', 'GOK': '85/93', 'GW': '43/48', 'falsche Bohrungen': 2, 'falsche Grenzen': 6, 'falsches GW': 0, 'XY': '25/25', 'GW-Status': '16/23'}`
- **Zusatzlauf `raster150`** (`..\gt-pdfs\raster\raster150` ohne Baseline):  
  `{'Bohrungen': '47/61', 'Grenzen': '203/369', 'Grenzen exakt': '196/369', 'Bodenart': '108/130', 'GOK': '35/53', 'GW': '13/18', 'falsche Bohrungen': 0, 'falsche Grenzen': 0, 'falsches GW': 0, 'XY': '4/7', 'GW-Status': '17/20'}`

*(Hinweis zu den Ordnern unter `..\gt-pdfs`: Der OCR-Cache liegt dort unter `ocr_cache` statt `ocr`; für die Stressfälle wurde `stress_v3` mit allen 27 Fällen `s01`–`s27` statt des älteren Ordners `stress` mit nur `s01`–`s19` verwendet.)*

## Vergleich mit dem letzten Bericht

Kein früherer Bericht unter `agenten/routinen/berichte/regression.md` vorhanden (Ersterstellung). Gegenüber `benchmark/baseline_v4.json` (Stand `52926f4`) ist einzig `real/rednitzhembach` schlechter (siehe oben); im Lauf `raster150` entsprechen `GW 13/18` und `0` falsche Bohrungen/Grenzen/GW den Werten aus `CHANGELOG.md`.

## Laufzeit je PDF

### Echte PDFs (`real`) und `raster150`

| Fall | Laufzeit `real` | Laufzeit `raster150` |
|---|---|---|
| `real/16132` | 11.0s | 11.7s |
| `real/A7367` | 2.8s | 2.0s |
| `real/berlin_v67b` | 26.4s | 47.1s |
| `real/clipping_test` | 0.3s | 1.1s |
| `real/example_borehole_profile` | 5.8s | 2.8s |
| `real/halle` | 11.8s | 24.9s |
| `real/hausham` | 33.0s | 69.7s |
| `real/marl_251` | 148.8s | 71.2s |
| `real/rednitzhembach` | 55.3s | 47.7s |
| `real/talheim` | 70.4s | 44.6s |
| `real/triefenstein_bp41` | 55.7s | 87.4s |
| `real/wachenroth` | 84.3s | 142.9s |
| `real/wesel_anlage12` | 15.6s | 32.6s |

### Stressfälle (`stress_v3`) und Synthesefälle (`synth`)

| Fall | Laufzeit | Fall | Laufzeit |
|---|---|---|---|
| `stress/s01_kontrolle` | 0.3s | `stress/s18_legende_dach` | 0.4s |
| `stress/s02_gedreht` | 0.4s | `stress/s19_dach_ohne_legende` | 0.4s |
| `stress/s03_titel_zusatz` | 0.4s | `stress/s20_raster_gw_symbol` | 1.5s |
| `stress/s04_einheit_gwtext` | 1.3s | `stress/s21_raster_schraffur_dreiecke` | 1.6s |
| `stress/s05_oberkante` | 0.3s | `stress/s22_raster_dreieck_ohne_linie` | 1.7s |
| `stress/s06_proben_gwm` | 0.4s | `stress/s23_raster_legende_dach` | 1.9s |
| `stress/s07_schnitt_dph` | 1.2s | `stress/s24_raster_tiefenlineal_gw` | 1.6s |
| `stress/s08_kuerzel` | 0.4s | `stress/s25_raster_lineal_widerspruch` | 2.1s |
| `stress/s09_schraffur` | 0.3s | `stress/s26_sv_wasserstand` | 1.3s |
| `stress/s10_tabelle` | 0.5s | `stress/s27_sv_kein_grundwasser` | 1.2s |
| `stress/s11_shx_sv` | 2.4s | `synth/synth_A` | 1.5s |
| `stress/s12_raster` | 1.4s | `synth/synth_A2` | 1.4s |
| `stress/s13_fremdcode` | 0.4s | `synth/synth_A3` | 1.4s |
| `stress/s14_massstab_widerspruch` | 0.4s | `synth/synth_A4` | 1.4s |
| `stress/s15_oberkante_mehrzeilig` | 0.4s | `synth/synth_A5` | 1.4s |
| `stress/s16_kopf_fern` | 0.5s | `synth/synth_B` | 1.2s |
| `stress/s17_schraffur_gestrichelt` | 0.4s | | |

## Offen

- `.venv` wieder auf `pymupdf==2.0` (`constraints.txt:27`) pinnen **oder** Zeilensortierung in `services/extractor/prototyp_v4.py:598` tolerant für leichte `y0`-Abweichungen innerhalb einer Zeile machen (wie `rows()`), damit `rednitzhembach` auch unter `pymupdf` 2.1 stabil `'B 2'`/`'B 4'` liest.
- `..\gt-pdfs\stress` auf die 27 Fälle (`s01`–`s27`, wie `stress_v3`) aktualisieren, falls künftige Läufe `..\gt-pdfs\stress` direkt ansprechen.
