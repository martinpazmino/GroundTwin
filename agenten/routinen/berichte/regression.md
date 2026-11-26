# Bericht: Routine `regression`

**Datum:** 2026-11-26  
**Zweig:** `agy/routine-regression` (Basis: `origin/main` @ `de49a8a`)

## Ergebnis

**Status:** `OK: keine Regression` — 0 `REGRESSION`-Zeilen gegen `benchmark/baseline_v4.json` (`services/extractor/prototyp_v4.py`, `pymupdf` `2.0` / MuPDF `1.28.5` in `.venv`). Alle 13 echten PDFs (`real`), alle 30 Stressfälle (`s01`–`s30` aus `stress_v4`) und alle 6 Synthesefälle (`synth_A`–`synth_B`) erreichen die Baseline bei `0` falschen Bohrungen, `0` falschen Grenzen und `0` falschem GW.

## SUMME

- **Hauptlauf** (`..\gt-pdfs\real`, `..\gt-pdfs\stress_v4`, `..\gt-pdfs\synth` mit `GEO_OCR_CACHE=..\gt-pdfs\ocr_cache`):  
  `{'Bohrungen': '102/107', 'Grenzen': '606/619', 'Grenzen exakt': '598/619', 'Bodenart': '365/393', 'GOK': '87/94', 'GW': '44/49', 'falsche Bohrungen': 0, 'falsche Grenzen': 0, 'falsches GW': 0, 'XY': '25/25', 'GW-Status': '20/23'}`
- **Zusatzlauf `raster150`** (`..\gt-pdfs\raster\raster150` nach `benchmark/perturb.py ... raster150`, ohne Baseline):  
  `{'Bohrungen': '47/61', 'Grenzen': '203/369', 'Grenzen exakt': '196/369', 'Bodenart': '108/130', 'GOK': '35/53', 'GW': '13/18', 'falsche Bohrungen': 0, 'falsche Grenzen': 0, 'falsches GW': 0, 'XY': '4/7', 'GW-Status': '17/20'}`

*(Hinweis zu den Ordnern unter `..\gt-pdfs`: Der OCR-Cache liegt dort unter `ocr_cache` statt `ocr`; für die Stressfälle wurde `stress_v4` mit allen 30 Fällen `s01`–`s30` statt des älteren Ordners `stress` mit nur `s01`–`s19` verwendet.)*

## Vergleich mit dem letzten Bericht

Gegenüber dem Vorbericht vom `2026-11-22` (`origin/main` @ `52926f4`, `stress_v3`, Hauptlauf `Bohrungen 100/106`, `Grenzen 594/614`, `Grenzen exakt 586/614`, `Bodenart 354/385`, `GOK 85/93`, `GW 43/48`, `falsche Bohrungen 2`, `falsche Grenzen 6`, `GW-Status 16/23`):

- Alle 8 damaligen `REGRESSION`-Zeilen bei `real/rednitzhembach` sind behoben (`4/4` Bohrungen, `15/15` Grenzen, `13/15` Grenzen exakt, `12/15` Bodenart, `4/4` GOK, `4/4` GW-Status, `0` falsche Bohrungen/Grenzen; behoben durch `d875a8e` sowie `pymupdf` `2.0` im `.venv`).
- Der Stress-Satz umfasst neu `s28`–`s30` (`stress_v4` statt `stress_v3`), wodurch `s28_zeile_grundlinie` `+1/1` Bohrungen, `+5/5` Grenzen, `+5/5` Grenzen exakt, `+5/5` Bodenart, `+1/1` GOK und `+1/1` GW zur `SUMME` beiträgt.
- Im Zusatzlauf `raster150` ist die `SUMME` exakt identisch zum `2026-11-22` (`47/61` Bohrungen, `203/369` Grenzen, `196/369` Grenzen exakt, `108/130` Bodenart, `35/53` GOK, `13/18` GW, `0` falsche, `4/7` XY, `17/20` GW-Status).

## Laufzeit je PDF

### Echte PDFs (`real`) und `raster150`

| Fall | Laufzeit `real` | Laufzeit `raster150` |
|---|---|---|
| `real/16132` | 26522.3s *(inkl. System-Ruhezustand; wach 13.7s)* | 2.4s |
| `real/A7367` | 7.2s | 1.1s |
| `real/berlin_v67b` | 41.2s | 36.8s |
| `real/clipping_test` | 0.3s | 0.9s |
| `real/example_borehole_profile` | 7.1s | 2.7s |
| `real/halle` | 17.7s | 14.7s |
| `real/hausham` | 45.8s | 58.6s |
| `real/marl_251` | 124.9s | 59.6s |
| `real/rednitzhembach` | 54.0s | 35.5s |
| `real/talheim` | 51.5s | 24.8s |
| `real/triefenstein_bp41` | 47.8s | 51.7s |
| `real/wachenroth` | 73.0s | 64.2s |
| `real/wesel_anlage12` | 11.6s | 18.6s |

### Stressfälle (`stress_v4`) und Synthesefälle (`synth`)

| Fall | Laufzeit | Fall | Laufzeit |
|---|---|---|---|
| `stress/s01_kontrolle` | 0.2s | `stress/s20_raster_gw_symbol` | 1.1s |
| `stress/s02_gedreht` | 0.2s | `stress/s21_raster_schraffur_dreiecke` | 1.1s |
| `stress/s03_titel_zusatz` | 0.3s | `stress/s22_raster_dreieck_ohne_linie` | 1.1s |
| `stress/s04_einheit_gwtext` | 1.0s | `stress/s23_raster_legende_dach` | 1.3s |
| `stress/s05_oberkante` | 0.3s | `stress/s24_raster_tiefenlineal_gw` | 1.1s |
| `stress/s06_proben_gwm` | 0.3s | `stress/s25_raster_lineal_widerspruch` | 1.1s |
| `stress/s07_schnitt_dph` | 0.9s | `stress/s26_sv_wasserstand` | 0.9s |
| `stress/s08_kuerzel` | 0.3s | `stress/s27_sv_kein_grundwasser` | 0.8s |
| `stress/s09_schraffur` | 0.2s | `stress/s28_zeile_grundlinie` | 0.2s |
| `stress/s10_tabelle` | 0.4s | `stress/s29_ls_wasserlinien` | 0.2s |
| `stress/s11_shx_sv` | 1.4s | `stress/s30_ls_wasserlinien_fallen` | 0.2s |
| `stress/s12_raster` | 1.1s | `synth/synth_A` | 1.2s |
| `stress/s13_fremdcode` | 0.2s | `synth/synth_A2` | 1.1s |
| `stress/s14_massstab_widerspruch` | 0.3s | `synth/synth_A3` | 1.1s |
| `stress/s15_oberkante_mehrzeilig` | 0.2s | `synth/synth_A4` | 1.1s |
| `stress/s16_kopf_fern` | 0.3s | `synth/synth_A5` | 1.1s |
| `stress/s17_schraffur_gestrichelt` | 0.2s | `synth/synth_B` | 0.9s |
| `stress/s18_legende_dach` | 0.3s | | |
| `stress/s19_dach_ohne_legende` | 0.3s | | |

## Offen

- `..\gt-pdfs\stress` enthält weiterhin nur `s01`–`s19` und `..\gt-pdfs\ocr_cache` heißt nicht `ocr` (Anpassung der lokalen Ordner oder der Pfade in der Routine bei Bedarf).
