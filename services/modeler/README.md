---
title: "Layer modeler (baugrundmodell)"
date: 2026-10-27
tags: [model, layer-cake, ifc]
aliases: [baugrundmodell]
---

# Layer modeler (`baugrundmodell`)

Canonical JSON of the extraction → automatic Einheiten → surfaces → closed solids → IFC 4.3
(`IfcGeomodel` + `IfcBorehole`) for That Open. Design, parameters and results:
[18 Layer modeler](../../docs/18_layer_modeler.md).

```bash
pip install -r requirements.txt
cd services/modeler
python -m baugrundmodell model.ifc extraction1.json [extraction2.json ...] --bericht report.json
#   --methode idw|tps   --raster 2.0   --puffer 15   --basis 10.0 (m NHN)   --ohne-bohrsaeulen
#   --einheiten einheiten.json   (the engineer's Einheiten; template in report.json → vorlage_einheiten)
python -m pytest tests                                     # tests with synthetic ground truth
python -m baugrundmodell.synthetisch demo demo.json        # cases: geneigt auskeilen linse zensiert stoerungen demo
```

| Module | What it does |
|---|---|
| [`einheiten.py`](baugrundmodell/einheiten.py) | Preparation of the Bohrungen (exclusions with the reason), correlation of the Schichtfolgen by dynamic programming, exact / free / censored / unknown contacts |
| [`flaechen.py`](baugrundmodell/flaechen.py) | Domain (hull + buffer), TIN mesh with the Bohrungen as nodes, exact IDW/TPS, lenses, censoring, trimming, extent of partial Einheiten |
| [`koerper.py`](baugrundmodell/koerper.py) | Closed solid per Einheit, closure and volume check |
| [`umgebung.py`](baugrundmodell/umgebung.py) | Terrain from a DGM: top of the model pulled onto the GOK at the Bohrungen, terrain around the model (IfcGeographicElement TERRAIN) ([18 §3](../../docs/18_layer_modeler.md#3-surfaces-and-solids)) |
| [`ifc4x3.py`](baugrundmodell/ifc4x3.py) | IFC 4.3 writer (N1 columns and N3 model, terrain, LoD2 buildings as context), colours, Psets |
| [`modell.py`](baugrundmodell/modell.py) | Orchestration, JSON report, Reifegrad (Gutachten / Vorerkundung / gemischt) from the `herkunft` of the Bohrungen ([21 §4.7](../../docs/21_app_schritte_normen.md#47-standort-ohne-gutachten-a-vorerkundung-from-a-point)) |
| [`synthetisch.py`](baugrundmodell/synthetisch.py) | Cases with known ground truth (tests and viewer demo) |
| [`normen.py`](baugrundmodell/normen.py) + [`normen.json`](baugrundmodell/normen.json) | Mini database of norms (DIN 4023, EN ISO 14688-1, DIN 18196) and reading of the descriptions ([21 §3](../../docs/21_app_schritte_normen.md#3-mini-database-of-norms)) |
| [`homogenbereiche.py`](baugrundmodell/homogenbereiche.py) + [`homogenbereiche.json`](baugrundmodell/homogenbereiche.json) | VOB/C Homogenbereiche per Gewerk (ATV), Kennwerte from descriptions, report tables and laboratory sheets, proposals per Anwendungsfall and from the Gutachter ([28](../../docs/28_homogenbereiche.md)) |
| [`bodenkennwerte.py`](baugrundmodell/bodenkennwerte.py) | Proposal and assignment of extracted Bodenkennwerte (`kennwerte.py`) to the model Einheiten by name, Bodenart or NHN height range ([28 §9](../../docs/28_homogenbereiche.md#9-kennwerte-from-the-report-tables-issue-18-2026-11-19-training-pdfs-not-blind)) |
| [`labor.py`](baugrundmodell/labor.py) | Assignment of laboratory samples (`services/extractor/labor.py`) to the Schicht of their Bohrung and summary per Einheit (`n`, `min`, `max`, `mean`) for ATV Kennwerte and `CPset_Laborwerte` ([28 §9b](../../docs/28_homogenbereiche.md#9b-laboratory-sheets-of-the-annexes-issue-18-2026-11-19-training-pdfs-not-blind)) |
| [`wasser.py`](baugrundmodell/wasser.py) | Groundwater kind (`art`) and date per level, merging report water tables, and selection for the Grundwasserfläche ([06 §4](../../docs/06_grundwasser.md#4-data-model-and-ifc)) |

See the result: [`apps/web` viewer](../../apps/web/README.md) or the step app (`python -m server`,
[21](../../docs/21_app_schritte_normen.md)).

Up: [Documentation index](../../docs/README.md)

Related: [18 Layer modeler](../../docs/18_layer_modeler.md) · [Architecture §7](../../docs/ARCHITECTURE_BAUGRUNDMODELL.md#7-baugrundmodell-generating-the-geometry) · [IFC spike (history)](https://github.com/martinpazmino/GroundTwin/tree/03be932/spikes/ifc_thatopen)
