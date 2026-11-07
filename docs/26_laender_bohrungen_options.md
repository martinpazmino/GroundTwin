---
title: "26 Borehole data for Länder without a BoreholeML WFS: survey, options and prototype"
date: 2026-11-06
updated: 2026-11-06
tags: [open-data, boreholeml, wfs, wms, inspire, gbl, bgr, laender, geoldg, bohrdaten]
aliases: [Länder-Bohrungen Optionen, Bohrdaten WMS, Bohrdaten-Bestandsaufnahme]
---

# 26 Borehole data for Länder without a BoreholeML WFS: survey, options and prototype

**Question:** how can GroundTwin obtain official `Bohrungen` with `Schichten` (or at least reliable
`Kopfdaten`: `Lage`, `GOK`, `Endteufe`, and a direct link to the state archive) for the 12 Länder
currently listed only as `portal-bohrungen` (`ungeprueft`) in
[`dienste.json`](../services/geodaten/geodaten/dienste.json) (`SH`, `HH`, `NI`, `HB`, `HE`, `RP`,
`BY`, `SL`, `MV`, `SN`, `ST`, `TH`), for `BE` and `BB` (which currently only provide `wfs-kopf`
without `Schichten`), and via the federal BGR (`DE-BGR`)?

**Summary of findings:**

1. **Immediate full-layer win (`HH`):** **Hamburg** publishes a public, open-data **BoreholeML 3.0 WFS**
   (`https://geodienste.hamburg.de/HH_WFS_BoreholeML3`, feature type `bml:Borehole`, `dl-de/by-2.0`)
   that delivers both `Kopfdaten` and full `Schichten` (`bml:Interval` with SEP3 `rockName` codes).
   Live tests confirm that GroundTwin's existing [`boreholeml.importieren()`](../services/geodaten/geodaten/boreholeml.py)
   parses Hamburg's WFS response without a single line of code change. Only the `HH` entry in
   `dienste.json` needs to be switched from `portal-bohrungen` to `wfs-boreholeml` once `dienste.json`
   is unlocked.
2. **Automated nationwide `Kopfdaten` + hint (`DE-BGR` + `HB` WMS `GetFeatureInfo`, Option b):**
   - The federal **BGR Geoviewer Bohrungen Deutschland (GBL)** provides a public OGC WMS
     (`https://services.bgr.de/wms/geologie/gbl/`, layer `0` `Einzelbohrungen Info`,
     `INFO_FORMAT=text/xml`) and an ArcGIS REST layer covering **13 Länder** (`BY`, `SN`, `NI`, `SH`,
     `ST`, `TH`, `MV`, `HB`, `HH`, `BE`, `BB`, `BW`, `NW` — including **9 of the 12 previously
     unserved Länder**). It returns exact coordinates (`EPSG:25832`), `GOK` (`surfaceLevel`),
     `Endteufe` (`totalLength`), whether a digital `Schichtenverzeichnis` exists (`layerData`), and the
     state archive identifier (`gml_ID` / `shortName`).
   - **Bremen (`HB`)** provides a public OGC WMS (`https://geodienste.bremen.de/wms_bohrdatenbank`,
     `INFO_FORMAT=application/vnd.ogc.gml`, license `CC BY`) that returns `Kopfdaten` (`hoehe_bohransatz`,
     `endtiefe`, `x_4647`, `y_4647`) **plus** a direct download URL (`bohrprofil_pdf_url` on
     `https://gdfbgis.marum.de/download?shortname=...&format=pdf`) for a machine-readable vector PDF
     `Bohrprofil` containing the `Schichten`.
3. **Bulk open-data downloads for offline/file import (Option c & Option d):**
   - **Mecklenburg-Vorpommern (`MV`)** has decommissioned its legacy WFS (`mv_a7_lbds_wfs.php` returns
     `HTTP 410 Gone`), but provides a statewide GeoPackage download (`bohrdaten_dl.zip`, 8.29 MB ZIP /
     41.6 MB `.gpkg`, 122,429 `Bohrungen` with `RW`, `HW` in `EPSG:5650`, `ZCOORDB` GOK, and `ZCOORDE`
     Endteufe under `CC BY-SA 3.0`).
   - **Bremen (`HB`)** provides a statewide INSPIRE GML download (`inspire_ge_bohrdaten.zip`, 3.09 MB
     ZIP / 109.5 MB `.gml`, 83,090 `ge:Borehole` features, `Kopfdaten` only, `CC BY`).
   - **Hamburg (`HH`)** provides a bulk archive (`Bohrarchiv_HH.rar`, 116.1 MB, `dl-de/by-2.0`).
   - **BGR (`DE-BGR`)** provides INSPIRE ATOM/ZIP downloads (`GBL-INSPIRE_*.zip`, 24.9–115.2 MB per
     Land) for 10 Länder (`BY`, `HH`, `SN`, `SH`, `TH`, `ST`, `MV`, `BE`, `BW`, `NW`), containing only
     `Kopfdaten` (`ge:logElement` is `xsi:nil="true"`) under BGR general terms (`https://www.bgr.bund.de/agb`).
4. **Experimental BoreholeML 3.1 OGC API Features (`DE-BGR`, Option a):**
   - BGR operates a public OGC API Features prototype (`https://servicestest.bgr.de/bmloaf/datasets/BoreholeML_3.1.0`)
     delivering BoreholeML 3.1 with `Schichten` for test subsets in **Niedersachsen (`NI`)** and
     **Brandenburg (`BB`)** (where Brandenburg's own WFS only links raster PNG images). Because it runs
     on `servicestest.bgr.de` ("Prototyp 4 / Testdaten"), it should be monitored but not yet enabled as a
     production default.

---

## 1. Survey by Land (`Land × Fundstelle`)

All endpoints below were tested live on `2026-11-06` from the GroundTwin workspace without registration,
API keys, or bypassing any access control.

| Land | SGD / Authority | Fundstelle & Official URL | Type | Scope (`Kopf` / `Schichten`) | CRS | License & Attribution | Live Test (`2026-11-06`: Status, Time, Result) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **HH** | BUKEA Hamburg | `https://geodienste.hamburg.de/HH_WFS_BoreholeML3` (`bml:Borehole`) | WFS 2.0.0 (BoreholeML 3.0) | **`Kopfdaten` + full `Schichten`** (`bml:Interval`, SEP3 `rockName`) | `EPSG:5555` / `EPSG:25832` | `dl-de/by-2.0` (`Freie und Hansestadt Hamburg, BUKEA`) | `HTTP 200`, `359 ms` (Capabilities); `GetFeature` (`COUNT=5` in BBOX): `HTTP 200`, `703 ms`, `225,528 B`, 5 `Bohrungen` with full `Schichten` parsed by `boreholeml.importieren()`. |
| **HH** | BUKEA Hamburg | `https://geodienste.hamburg.de/HH_WFS_BoreholeML3-Header` | WFS 2.0.0 | `Kopfdaten` only | `EPSG:25832` | `dl-de/by-2.0` | `HTTP 200`, `203 ms` (`19,581 B` Capabilities). Redundant since `HH_WFS_BoreholeML3` delivers full `Schichten`. |
| **HH** | BUKEA Hamburg | `https://daten-hamburg.de/umwelt_klima/bohrarchiv/Bohrarchiv_HH.rar` | Bulk Download (RAR) | `Kopfdaten` + `Schichten` | `EPSG:25832` | `dl-de/by-2.0` | `HTTP 206` (Range test), `359 ms`, `116.1 MB` archive. |
| **HB** | GDfB / GeoInformation Bremen | `https://geodienste.bremen.de/wms_bohrdatenbank` (`Bohrpunkte_Bremen`) | WMS 1.1.1 (`GetFeatureInfo` GML) | **`Kopfdaten` + `bohrprofil_pdf_url`** (`hoehe_bohransatz`, `endtiefe`, `x_4647`, `y_4647`) | `EPSG:25832` / `EPSG:4647` / `EPSG:31467` | `CC BY` (`Freie Hansestadt Bremen, GeoInformation Bremen / GDfB`) | `HTTP 200`, `407 ms` (Capabilities); `GetFeatureInfo` (`application/vnd.ogc.gml`): `HTTP 200`, `483 ms`, returns `<Bohrungen0bis10m>` features with PDF links. |
| **HB** | GDfB / MARUM | `https://gdfbgis.marum.de/download?shortname=2918_05_1594&format=pdf` | Direct PDF Download (linked from WMS) | **`Kopfdaten` + vector PDF `Schichten`** (`Tiefe [m]`, lithology, `Ansatzhöhe`, `Endteufe`) | `EPSG:4647` | `© GDfB` / `CC BY` via Bremen WMS | `HTTP 200`, `798 ms`, `56,017 B` vector PDF; `bohrprofil_html` timed out (`9,795 ms`); `format=xml/bml` returned `HTTP 422`. |
| **HB** | GeoInformation Bremen | `https://gdi2.geo.bremen.de/inspire/download/inspire_ge_bohrdaten/data/inspire_ge_bohrdaten.zip` | INSPIRE Download (ZIP/GML) | `Kopfdaten` only (`ge:boreholeLength`, `ge:elevation`; `ge:logElement` nil) | `EPSG:4258` | `CC BY` (`Freie Hansestadt Bremen`) | `HTTP 200`, `3,200 ms`, `3.09 MB` ZIP (`109.5 MB` GML with `83,090` `ge:Borehole` features). |
| **HB** | GeoInformation Bremen | `https://gdi2.geo.bremen.de/inspire/download/Bohrdatenbank_von_Bremen/data/Bohrdatenbank_HB_BHV.zip` | Restricted Download | Full DB | — | Restricted | `HTTP 401 Unauthorized`, `391 ms` (access control; not usable). |
| **MV** | LUNG MV | `https://www.umweltkarten.mv-regierung.de/script/mv_a7_lbds_wfs.php` (and `..._wms.php`) | Legacy WFS & WMS | Decommissioned | — | — | **`HTTP 410 Gone`**, `219 ms` (WFS) and `509 ms` (WMS). Catalogue link in GDI-DE is dead. |
| **MV** | LUNG MV | `https://umweltportal.mv-regierung.de/download/geologie/LBDS/bohrdaten_dl.zip` | Bulk Download (`GeoPackage`) | **`Kopfdaten`** (`RW`, `HW`, `ZCOORDB` GOK, `ZCOORDE` Endteufe, `STRAT_EH`, `LONGNAME`) | `EPSG:5650` (ETRS89 / UTM 33N with zone prefix `33`) | `CC BY-SA 3.0 DE` (`© LUNG MV (CC BY-SA 3.0)` per `agb_lung_de.pdf`) | `HTTP 200`, `1,840 ms`, `8.29 MB` ZIP containing `bohrdaten_dl.gpkg` (`41.6 MB`, `122,429` `Bohrungen`). `SVZ_URL` links inside table (`lbds_svz_overview.php`) return `HTTP 410 Gone`. |
| **BB** | LBGR / GeoBasis-BB | `https://ogc-api.geobasis-bb.de/datasets/bpk` (`bpk_m_sch`, `bpk_o_sch`) | OGC API Features (GeoJSON) | `Kopfdaten` + PNG link (`Schichtenverzeichnis_grafisch`) | `EPSG:4326` / `EPSG:25833` | `dl-de/by-2.0` (`LBGR Brandenburg`) | `HTTP 200`, `422 ms` (landing/collections), `items?limit=1`: `HTTP 200`, returns same attributes as existing `bpk_wfs`. |
| **BB** | LBGR Brandenburg | `https://inspire.brandenburg.de/services/ge-core_bpk_wfs` (`ge:Borehole`) | INSPIRE WFS 2.0.0 | `Kopfdaten` only (`ge:boreholeLength`, `ge:elevation`, `ge:logElement` nil) | `EPSG:25833` | `dl-de/by-2.0` (`LBGR Brandenburg`) | `HTTP 200`, `422 ms` (Capabilities); `GetFeature` (`COUNT=1`): `HTTP 200`, `731 ms`, `4,277 B`. |
| **BE** | SenMVKU Berlin | `https://gdi.berlin.de/services/wfs/bohrungen` (`bohrungen:bohrungen`) | WFS 2.0.0 (already integrated as `wfs-kopf`) | `Kopfdaten` only (`gok_m_nhn`, `endteufe_m`, PDF request instruction) | `EPSG:25833` | `dl-de/zero-2.0` (`Geoportal Berlin / Geologische Bohrdaten`) | Already integrated in `bohrdaten.py`; `GBL-INSPIRE_Berlin.zip` (`44.2 MB`, `HTTP 206`) also has `Kopfdaten` only. Full `Schichten` only via GeolDG application to SenMVKU. |
| **BY** | LfU Bayern | `https://www.umweltatlas.bayern.de/` & BGR GBL (`SGD=by`, `BIS-BY`) | Web Portal + BGR GBL WMS / `boreholefeatureinfo` | `Kopfdaten` via BGR GBL WMS; `Schichten` via BGR proxy (`boreholefeatureinfo/rest/by/detail/de`) | `EPSG:25832` | Portal / BGR AGB (`© Bayerisches Landesamt für Umwelt`) | Portal `HTTP 200` (`936 ms`); direct LfU WFS `/gdi/wfs/geologie/bohrungen` returns `HTTP 400` (not offered); BGR GBL WMS `GetFeatureInfo` returns `BIS-BY` `Kopfdaten` (`HTTP 200`, `651 ms`). |
| **SN** | LfULG Sachsen | `https://www.umwelt.sachsen.de/umwelt/geologie/11583.htm` & BGR GBL (`SGD=sn`, `BDSN`) | Web Portal + BGR GBL WMS / `boreholefeatureinfo` | `Kopfdaten` via BGR GBL WMS; `Schichten` in portal / BGR viewer | `EPSG:25832` | Portal / BGR AGB (`© LfULG Sachsen`) | `bohrdaten.sachsen.de` DNS NXDOMAIN (`98 ms`); `umwelt.sachsen.de` `HTTP 200` (`1,064 ms`); `wms_lfulg_geologie_bohrungen` `HTTP 404` (`415 ms`); BGR GBL WMS returns `BDSN` `Kopfdaten` (`HTTP 200`). |
| **NI** | LBEG Niedersachsen | `https://nibis.lbeg.de/cardomap3/` & BGR GBL (`SGD=ni`, `BDN`) & BGR OAF | Web Portal + BGR GBL WMS + BGR OAF Prototype | `Kopfdaten` via BGR GBL WMS; `Schichten` in BGR OAF (`servicestest.bgr.de`) for test subset | `EPSG:25832` / `CRS84` | Portal (`© LBEG`) / BGR AGB | `nibis.lbeg.de/cardomap3/` `HTTP 200` (`10,826 ms`); `ogc.ashx` WFS returns OGC ServiceException (`413 ms`); BGR GBL returns `BDN` `Kopfdaten` + `boreholeWebLink`. |
| **SH** | LfU Schleswig-Holstein | `https://umweltportal.schleswig-holstein.de/` & BGR GBL (`SGD=sh`, `BDSH`) | Web Portal + BGR GBL WMS + `GBL-INSPIRE_Schleswig_Holstein.zip` | `Kopfdaten` via BGR GBL WMS (`surfaceLevel`, `totalLength`); no open `Schichten` WFS | `EPSG:25832` | Portal (`© LfU SH`) / BGR AGB | Portal `HTTP 200` (`522 ms`); `GBL-INSPIRE_Schleswig_Holstein.zip` `HTTP 206` (`115.2 MB`); BGR GBL returns `BDSH` `Kopfdaten`. |
| **ST** | LAGB Sachsen-Anhalt | `https://lagb.sachsen-anhalt.de/` & BGR GBL (`SGD=st`, `SABIS`) | Web Portal + BGR GBL WMS + `GBL-INSPIRE_Saxony_Anhalt.zip` | `Kopfdaten` via BGR GBL WMS (incl. `boreholeWebLink` to LAGB viewer); `Schichten` (`layerData=0`) restricted | `EPSG:25832` | Portal (`© LAGB`) / BGR AGB | Portal `HTTP 200` (`1,301 ms`); `GBL-INSPIRE_Saxony_Anhalt.zip` `HTTP 206` (`32.3 MB`); BGR GBL returns `SABIS` `Kopfdaten`. |
| **TH** | TLUBN Thüringen | `https://tlubn.thueringen.de/geologie/` & BGR GBL (`SGD=th`, `BDTH`) | Web Portal (CAPTCHA-gated) + BGR GBL WMS | `Kopfdaten` via BGR GBL WMS and `GBL-INSPIRE_Thuringia.zip` (`33.1 MB`) | `EPSG:25832` | Portal (`© TLUBN`) / BGR AGB | `tlubn.thueringen.de` and `geoportal-th.de` return `HTTP 200` (`402 ms`) with a `Link11 - CAPTCHA` anti-bot gate (blocked for automated clients); BGR GBL WMS works without gate (`HTTP 200`). |
| **HE** | HLNUG Hessen | `https://geologie.hessen.de/mapapps/resources/apps/geologie/index.html` | Interactive Web Viewer (`map.apps`) | Interactive viewing only; `Schichten` via GeolDG inquiry to HLNUG | `EPSG:25832` | Portal (`© HLNUG Hessen`) | `HTTP 200` (`1,198 ms`, HTML/JS viewer shell); not part of BGR GBL (`SGD=he` has 0 features in GBL); no public WFS or bulk download in GDI-DE CSW. |
| **RP** | LGB Rheinland-Pfalz | `https://www.lgb-rlp.de/karten-und-produkte/online-karten.html` | Interactive Web Portal | Interactive viewing / inquiry only | `EPSG:25832` | Portal (`© LGB Rheinland-Pfalz`) | Portal `HTTP 200` (`1,002 ms`); `mapserver.lgb-rlp.de/cgi-bin/geologie_bohrpunkte` `HTTP 404` (`526 ms`); not in BGR GBL (`SGD=rp` has 0 features). |
| **SL** | LUA / LVGL Saarland | `https://geoportal.saarland.de/` | Interactive Web Portal | Interactive viewing / inquiry only | `EPSG:25832` | Portal (`© LVGL / LUA Saarland`) | Portal `HTTP 200` (`1,831 ms`); not in BGR GBL (`SGD=sl` has 0 features); no Bohrdaten WFS in GDI-DE CSW. |
| **DE-BGR** | BGR (Bund + 13 Länder) | `https://services.bgr.de/wms/geologie/gbl/` (Layer `0` `Einzelbohrungen Info`) & `.../arcgis/rest/services/geologie/gbl/MapServer/4` | OGC WMS 1.3.0 (`GetFeatureInfo` XML) & ArcGIS REST | **`Kopfdaten` across 13 Länder** (`BY, SN, NI, SH, ST, TH, MV, HB, HH, BE, BB, BW, NW`): `gml_ID`, `point` (`EPSG:25832`), `surfaceLevel`, `totalLength`, `layerData`, `boreholeWebLink` | `EPSG:25832` / `EPSG:3857` | BGR AGB (`https://www.bgr.bund.de/agb`, free viewing/info service; state attribution in `organisationName`) | WMS Capabilities `HTTP 200` (`234 ms`); WMS `GetFeatureInfo` (`INFO_FORMAT=text/xml`, Layer `0`): `HTTP 200`, `651 ms`, returns structured `<FeatureInfoResponse><FIELDS .../>` XML. |
| **DE-BGR** | BGR (Bund Prototype) | `https://servicestest.bgr.de/bmloaf/datasets/BoreholeML_3.1.0` | OGC API Features (BoreholeML 3.1 XML) | `Kopfdaten` + `Schichten` (`bml:Interval`) for test subsets in `NI` and `BB` | `CRS84` (`EPSG:4326`) | Test prototype (`BGR BoreholeML - Prototyp 4`) | `HTTP 200`, `281 ms` (landing); `items?bbox=...` in Hannover (`NI`) and Potsdam (`BB`): `HTTP 200`, `620 ms`, returns BoreholeML 3.1 with 10 `Schichten`. |
| **DE-BGR** | BGR (INSPIRE ATOM) | `https://services.bgr.de/atomfeeds/dataset_d3844378-5373-4b5f-bcf8-31ffc9d220db.xml` (`GBL-INSPIRE_*.zip`) | INSPIRE Download (ATOM + GML ZIPs) | `Kopfdaten` only (`ge:Borehole`, `ge:logElement` nil) for 10 Länder (`BY, HH, SN, SH, TH, ST, MV, BE, BW, NW`) | `EPSG:25832` | BGR AGB (`https://www.bgr.bund.de/agb`) | Feed `HTTP 200` (`297 ms`); ZIP downloads `HTTP 206` (`24.9 MB` MV to `115.2 MB` SH); `NI, HB, HE, RP, SL, BB` return `HTTP 404` (not in feed). |

---

## 2. Evaluation of Options (a)–(e)

Before comparing new architecture options for the remaining Länder, **Hamburg (`HH`)** is a special case:
its official service `https://geodienste.hamburg.de/HH_WFS_BoreholeML3` already speaks **BoreholeML 3.0
over WFS 2.0.0** (`bml:Borehole`, `dl-de/by-2.0`) and works out of the box with the existing
`wfs-boreholeml` pipeline in [`bohrdaten.py`](../services/geodaten/geodaten/bohrdaten.py) and
[`boreholeml.py`](../services/geodaten/geodaten/boreholeml.py). Switching `HH` in `dienste.json`
upgrades Hamburg from `portal-bohrungen` (`ungeprueft`) to `wfs-boreholeml` (`geprueft`) with zero code
changes.

For the remaining 13 Länder without a BoreholeML WFS (`SH, NI, HB, HE, RP, BY, SL, MV, SN, ST, TH` plus
`BE` and `BB`), we evaluate options **(a)** through **(e)**:

### Comparison Table

| Criterion | (a) Custom WFS / OGC API Features (`wfs-inspire` / `oaf-boreholeml`) | (b) `WMS-GetFeatureInfo` as automated hint (`bohrdaten_wms.py`) | (c) User file import with field mapping (`bohrdaten_datei.py`) | (d) Automated INSPIRE ATOM / ZIP downloads (`GBL-INSPIRE`) | (e) Keep `portal-bohrungen` link only |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Covered Länder (beyond `HH` in `wfs-boreholeml`)** | `BB` (INSPIRE WFS / OAF, `Kopfdaten` only — already covered by `bpk_wfs`); `NI` & `BB` subsets on `servicestest.bgr.de` (test data only) | **13 Länder** via BGR GBL WMS (`BY, SN, NI, SH, ST, TH, MV, HB, HH, BE, BB, BW, NW`) + **Bremen (`HB`)** via `wms_bohrdatenbank` (incl. PDF profile URL) | **`MV`** (`bohrdaten_dl.gpkg`), **`HB`** (`inspire_ge_bohrdaten.zip`), **`HH`** (`Bohrarchiv_HH.rar`), plus any user-exported CSV / GeoPackage / BoreholeML / INSPIRE-GML from state requests | 10 Länder in `GBL-INSPIRE_*.zip` (`BY, HH, SN, SH, TH, ST, MV, BE, BW, NW`) + `HB` (`inspire_ge_bohrdaten.zip`) — all `Kopfdaten` only | `HE`, `RP`, `SL` (neither WFS/WMS nor BGR GBL available), and manual GeolDG inquiries for full `Schichten` |
| **Data Depth** | `Kopfdaten` (`BB`); `Schichten` only on experimental BGR test server | `Kopfdaten` (`id`, `name`, `rechtswert`, `hochwert`, `gok_m_nn`, `endteufe_m`, `hat_schichtenverzeichnis`, `bohrprofil_url`), `schichten: []` | `Kopfdaten` (MV, HB, INSPIRE) or `Kopfdaten` + `Schichten` (if user imports BoreholeML XML or layer CSV) | `Kopfdaten` only (`ge:logElement` is `xsi:nil="true"` in all GBL-INSPIRE files) | None in app (manual browser jump to state portal) |
| **User Workflow** | Fully automatic from project coordinates (`rechtswert`, `hochwert`) | **Fully automatic from project coordinates** (`rechtswert`, `hochwert`, `radius_m`) | Requires manual download, unzip, and file upload by user | Requires downloading 25–115 MB ZIP per Land (300–600 MB unpacked GML) | Manual search in external web browser |
| **License & Liability** | `BB`: `dl-de/by-2.0`; BGR OAF test server has no production license / SLA | **High clarity:** `HB` WMS is `CC BY`; BGR GBL WMS is a public OGC View Service (`Darstellungsdienst`) queried live without redistributing bulk databases; provenance & attribution stored in `herkunft` | **High clarity:** user supplies file downloaded under state terms (`CC BY-SA 3.0` in MV, `CC BY` in HB, `dl-de/by-2.0` in HH, or individual GeolDG delivery) | **Problematic:** BGR `GBL-INSPIRE_*.zip` files are governed by BGR AGB (`https://www.bgr.bund.de/agb`), prohibiting bulk redistribution, and waste >100 MB bandwidth for `Kopfdaten` | Unchanged (user acts in state portal) |
| **Implementation Effort** | Medium (`bohrdaten_oaf.py` + BoreholeML 3.1 namespace & CRS84 transformation) | **Low (~180 LoC):** standalone `bohrdaten_wms.py` using stdlib `xml.etree.ElementTree` + `netz.abrufen`, later 10-line hook in `bohrdaten.py` & `dienste.json` | **Low–Medium (~220 LoC):** standalone `bohrdaten_datei.py` (`sqlite3` for `.gpkg`, `csv`, `xml.etree.ElementTree` for GML/BML) + UI upload wiring | High (ATOM parser, multi-100 MB streaming GML parser, local spatial index cache) | Zero |
| **Geotechnical & Provenance Risks** | Test server `servicestest.bgr.de` may return incomplete or test-only records | Must never invent `Schichten`; `schichten` stays `[]`, `issues` explicitly warns that only `Kopfdaten` are present; WMS BBOX/pixel tolerance must filter hits by exact distance (`radius_m`) | User CSVs have varying column names and CRS (`EPSG:5650` in MV has `33` zone prefix); any imported layers must get `confidence = 0.5` | Huge GML files in `EPSG:4258` or `EPSG:25832` without `Schichten` | User gets no automated `Gegenprobe` (`doppelte()`) or `Vorerkundung` hint |
| **Offline Testability** | Good (saved JSON/XML fixture) | **Excellent:** deterministic XML (`FeatureInfoResponse`) and GML (`FeatureCollection`) fixtures without network calls | **Excellent:** deterministic in-memory SQLite `.gpkg` / CSV / GML fixtures | Poor (requires mocked multi-file ATOM + ZIP streams) | N/A |

### Detailed Assessment of Options (a)–(e)

#### Option (a): New Service Type for Custom WFS / OGC API Features
- **Where it applies:**
  1. **Hamburg (`HH`)** does **not** need a new service type: its `HH_WFS_BoreholeML3` uses the standard
     `http://www.infogeo.de/boreholeml/3.0` schema and `EPSG:5555` (`boreholeml.HORIZONTAL` already maps
     `5555 -> 25832`).
  2. **Brandenburg (`BB`)** offers `ge-core_bpk_wfs` (INSPIRE GML) and `ogc-api.geobasis-bb.de/datasets/bpk`
     (OGC API Features), but both expose the exact same `Kopfdaten` + raster PNG URL already integrated
     via `bpk_wfs` (`wfs-kopf`).
  3. **BGR OGC API Features (`servicestest.bgr.de/bmloaf/datasets/BoreholeML_3.1.0`)** is technically
     promising because it delivers BoreholeML 3.1 (`https://schemas.bgr.de/boreholeml/3.1`) with full
     `bml:Interval` layers for parts of `NI` and `BB`. However, the service metadata explicitly labels
     it `"BGR BoreholeML - Prototyp 4 / Testdaten in MS SQL Server"` on `servicestest.bgr.de`, and its
      coordinates are 2D `CRS84` (`lon/lat`) rather than `EPSG:25832`.
- **Verdict:** Activate `HH` immediately in existing `wfs-boreholeml`; defer a BoreholeML 3.1 OAF adapter
  until BGR promotes `bmloaf` from `servicestest.bgr.de` to production `services.bgr.de`.

#### Option (b): `WMS-GetFeatureInfo` as Automated "Hinweis, dass dort gebohrt wurde" (`bohrdaten_wms.py`)
- **Where it applies:**
  1. **BGR GBL WMS (`https://services.bgr.de/wms/geologie/gbl/`, Layer `0` `Einzelbohrungen Info`)**:
     covers **13 Länder** (`BY`, `SN`, `NI`, `SH`, `ST`, `TH`, `MV`, `HB`, `HH`, `BE`, `BB`, `BW`, `NW`),
     including `TH` (where the state portal `tlubn.thueringen.de` blocks automated requests with a
     Link11 CAPTCHA) and `BY`, `SN`, `NI`, `SH`, `ST`, `MV` (which have no active public WFS).
     A WMS 1.3.0 `GetFeatureInfo` call with `INFO_FORMAT=text/xml` returns an ESRI
     `<FeatureInfoResponse>` containing `<FIELDS .../>` elements with:
     - `gml_ID` (e.g. `BIS-BY_7835BG000657`) and `shortName` (`7835BG000657`)
     - `point="POINT (691496.631 5335507.964)"` (exact `EPSG:25832` Easting/Northing!)
     - `surfaceLevel="516,2"` (`gok_m_nn = 516.2`) and `totalLength="15,8"` (`endteufe_m = 15.8`)
     - `SGD="by"` (identifying the Land) and `organisationName="LfU: Bayerisches Landesamt für Umwelt"`
     - `layerData="1"`, `layerDataLegalAvail`, `layerDataTechAvail` (telling the engineer whether the
       state archive holds a `Schichtenverzeichnis` worth requesting) and `boreholeWebLink`.
  2. **Bremen WMS (`https://geodienste.bremen.de/wms_bohrdatenbank`, Layer `Bohrpunkte_Bremen`)**:
     A WMS 1.1.1 `GetFeatureInfo` call with `INFO_FORMAT=application/vnd.ogc.gml` under `CC BY` returns
     `<gml:featureMember>` elements with `shortname`, `longname`, `hoehe_bohransatz` (`gok_m_nn`),
     `endtiefe` (`endteufe_m`), `x_4647` / `y_4647` (`EPSG:4647`, where `rechtswert = x_4647 - 32_000_000`
     gives `EPSG:25832`), and `bohrprofil_pdf_url` (`https://gdfbgis.marum.de/download?shortname=...&format=pdf`),
     giving the user a one-click download of the vector PDF `Bohrprofil` with `Schichten`!
- **Risks & Mitigations:**
  - WMS `GetFeatureInfo` queries a pixel `(I, J)` inside a bounding box (`BBOX`, `WIDTH`, `HEIGHT`). By
    centering the `BBOX` on `(rechtswert, hochwert)` with half-width `radius_m` and querying the center
    pixel `(50, 50)` on a `101×101` canvas, the server returns boreholes near the center; the parser
    then computes the exact Euclidean distance from the returned point coordinates (`point` or
    `x_4647`/`y_4647`) and filters strictly by `abstand_m <= radius_m`.
  - **Review 2026-11-07 (Claude):** with `101×101` pixels the BGR WMS returned only Bohrungen within ~40 m of
    the centre (tolerance in pixels); a known Bohrung 150 m away was missing at a radius of 500 m. The prototype
    now asks a `5×5` image (centre pixel `(2, 2)` covers the radius: 29–31 hits, the known one included; `3×3`
    returned nothing), and an answer that reaches `FEATURE_COUNT` (50) is listed in `unvollstaendig`
    instead of being cut silently (central München reaches it at 500 m).
  - `schichten` is always `[]` (never invented), and `issues` explicitly states that WMS
    `GetFeatureInfo` provides `Kopfdaten` only (`"WMS-GetFeatureInfo liefert nur Kopfdaten..."`).
  - Any personal clerk names or phone/email attributes in `<FIELDS>` (`individualName`, `voice`,
    `electronicMailAdress`) are ignored by the parser.
- **Verdict:** **Rank #1 recommendation for the prototype (`bohrdaten_wms.py`).** Best ratio of utility
  (13 Länder automated online from project coordinates + Bremen PDF links), legal clarity (standard OGC
  View Service `GetFeatureInfo`), and low implementation complexity.

#### Option (c): Import of a User-Downloaded File (`bohrdaten_datei.py`)
- **Where it applies:**
  - **Mecklenburg-Vorpommern (`MV`)**: `bohrdaten_dl.zip` (`bohrdaten_dl.gpkg`, `CC BY-SA 3.0`,
    `122,429` boreholes in `EPSG:5650` where `RW` has the `33` zone prefix: `rechtswert_25833 = RW - 33_000_000`).
  - **Bremen (`HB`)**: `inspire_ge_bohrdaten.zip` (`CC BY`, `83,090` `ge:Borehole` features).
  - **Hamburg (`HH`)**: `Bohrarchiv_HH.rar` (`dl-de/by-2.0`).
  - Any Land (`HE`, `RP`, `BY`, `SH`, `ST`, `TH`, `BE`) when the user receives a BoreholeML XML, CSV, or
    GeoPackage export from the `Landesamt` after submitting a project inquiry under GeolDG.
- **Verdict:** **Rank #2 recommendation (follow-up module `bohrdaten_datei.py`).** Essential for `MV`
  offline bulk data and user-supplied GeolDG exports, but requires manual file handling by the user.

#### Option (d): INSPIRE Download Services (ATOM Feeds / `GBL-INSPIRE_*.zip`)
- **Where it applies:** BGR's ATOM feed (`dataset_d3844378-5373-4b5f-bcf8-31ffc9d220db.xml`) offers
  `GBL-INSPIRE_*.zip` for 10 Länder (`BY, HH, SN, SH, TH, ST, MV, BE, BW, NW`), and Bremen offers
  `inspire_ge_bohrdaten.zip`.
- **Why not recommended for automated app download:**
  1. Every single `ge:Borehole` in `GBL-INSPIRE_*.zip` and `inspire_ge_bohrdaten.zip` has
     `<ge:logElement xsi:nil="true" nilReason="other:unpopulated"/>` — i.e., **zero `Schichten`**, only
     `Kopfdaten`.
  2. Each state ZIP is `24.9 MB` to `115.2 MB` compressed (`100–500 MB` unpacked XML). Downloading
     100 MB of XML just to extract `Kopfdaten` within a 500 m radius is orders of magnitude slower than
     querying the exact same `Kopfdaten` in `650 ms` via Option (b) (`WMS-GetFeatureInfo`).
  3. BGR's `GBL-INSPIRE` feed is subject to BGR AGB (`https://www.bgr.bund.de/agb`), which restricts
     automated mirroring/redistribution.

#### Option (e): Keep `portal-bohrungen` Link Only (With Reason)
- **Where it applies:**
  - **Hessen (`HE`)**, **Rheinland-Pfalz (`RP`)**, and **Saarland (`SL`)**: none of these three Länder
    expose a public WFS, WMS `GetFeatureInfo`, bulk download, or BGR GBL layer (`SGD` `he`, `rp`, `sl`
    have `0` records in BGR GBL). Their portals (`geologie.hessen.de`, `lgb-rlp.de`,
    `geoportal.saarland.de`) only support interactive browser viewing or formal GeolDG data requests.
  - For **full `Schichtenverzeichnisse`** in `BY`, `SN`, `NI`, `SH`, `ST`, `TH`, `MV`, `BE`, `BB`: while
    Option (b) supplies automated `Kopfdaten` (`GOK`, `Endteufe`, `Lage`, `hat_schichtenverzeichnis`) for
    the `Gegenprobe` (`doppelte()`), the detailed `Schichten` remain accessible only via the linked state
    portal or a GeolDG request (`Antrag nach GeolDG`).

---

## 3. Ranked Recommendations and Prototype Specification

### Ranked Action Plan

1. **Immediate configuration upgrade (0 LoC, after `dienste.json` lock is released):** **done 2026-11-07** (entry `HH`,
   checked by Claude with the app's code: 151 Bohrungen within 300 m of the Rathaus, Schichten and groundwater).
   - Switch **Hamburg (`HH`)** in [`services/geodaten/geodaten/dienste.json`](../services/geodaten/geodaten/dienste.json)
     from `typ: "portal-bohrungen"` to `typ: "wfs-boreholeml"`,
     `url: "https://geodienste.hamburg.de/HH_WFS_BoreholeML3"`, `feature_type: "bml:Borehole"`,
     `epsg: 25832`, `lizenz: "dl-de/by-2.0"`,
     `namensnennung: "© Freie und Hansestadt Hamburg, Behörde für Umwelt, Klima, Energie und Agrarwirtschaft (BUKEA)"`,
     `status: "geprueft"`.
   - Update the `MV` hint in `dienste.json` to note that `mv_a7_lbds_wfs.php` is `HTTP 410 Gone` and point
     to `https://umweltportal.mv-regierung.de/download/geologie/LBDS/bohrdaten_dl.zip` (`CC BY-SA 3.0`).
2. **Rank #1 Prototype (implemented in this task): Option (b) — [`bohrdaten_wms.py`](../services/geodaten/geodaten/bohrdaten_wms.py)**
   - Standalone module `services/geodaten/geodaten/bohrdaten_wms.py` with offline unit tests in
     [`tests/test_bohrdaten_wms.py`](../tests/test_bohrdaten_wms.py).
   - Supports both:
     - **ESRI WMS `FeatureInfoResponse` XML (`INFO_FORMAT=text/xml`)** as delivered by the nationwide
       **BGR GBL WMS** (`https://services.bgr.de/wms/geologie/gbl/`, Layer `0` `Einzelbohrungen Info`)
       for **13 Länder** (`BY`, `SN`, `NI`, `SH`, `ST`, `TH`, `MV`, `HB`, `HH`, `BE`, `BB`, `BW`, `NW`), and
     - **OGC GML `FeatureCollection` (`INFO_FORMAT=application/vnd.ogc.gml`)** as delivered by
       **Bremen's `wms_bohrdatenbank`** (`https://geodienste.bremen.de/wms_bohrdatenbank`, Layer
       `Bohrpunkte_Bremen`, `CC BY`), including automatic coordinate conversion from `EPSG:4647`
       (`x_4647 - 32_000_000`) to `EPSG:25832` and extraction of `bohrprofil_pdf_url`
       (`https://gdfbgis.marum.de/download?shortname=...&format=pdf`).
   - Returns the exact canonical structure of [`bohrdaten.py`](../services/geodaten/geodaten/bohrdaten.py):
     - Hit list from `abfragen_wms(...)` with `id`, `name`, `rechtswert`, `hochwert`, `epsg`,
       `abstand_m`, `gok_m_nn`, `endteufe_m`, `hat_schichtenverzeichnis`, `bohrprofil_url`, and
       `herkunft` (`quelle: "WMS-GetFeatureInfo"`, `dienst`, `land`, `url`, `lizenz`, `namensnennung`,
       `abgerufen`) — directly compatible with `bohrdaten.doppelte()`.
     - Document conversion via `zu_bohrung_kopf(...)` returning a `Bohrung` dictionary with
       `schichten: []` (never inventing layers), `quelle: "WMS-GetFeatureInfo"`, and a clear warning in
       `issues`.
3. **Rank #2 Follow-up: Option (c) — `bohrdaten_datei.py`**
   - Add a file importer for user-downloaded `.gpkg` (`MV` `bohrdaten_dl.gpkg`), `.gml` (`HB`
     `inspire_ge_bohrdaten.gml`), `.xml` (BoreholeML), and `.csv` files with explicit column mapping and
     `confidence = 0.5` for any archive layers.
4. **Rank #3 Follow-up: Option (e) for `HE`, `RP`, `SL`**
   - Retain `portal-bohrungen` links for Hessen, Rheinland-Pfalz, and Saarland, as no public machine-readable
     service exists.

### Files Changed When Integrating `bohrdaten_wms.py` (After Approval)

- `services/geodaten/geodaten/bohrdaten_wms.py` *(created in this task)*
- `tests/test_bohrdaten_wms.py` *(created in this task)*
- `services/geodaten/geodaten/dienste.json` *(after parallel task completes: switch `HH` to `wfs-boreholeml`, add `wms-kopf` entries for `HB` and `DE-BGR` / state fallbacks, update `MV` hint)*
- `services/geodaten/geodaten/bohrdaten.py` *(after approval: dispatch `typ == "wms-kopf"` in `abfragen()` to `bohrdaten_wms.abfragen_wms()`)*

Up: [Index](README.md)

Related: [07 Coordinates](07_coordinates.md) · [14 Licensing](14_licensing.md) · [21 Step app and norms](21_app_schritte_normen.md) · [23 Open data integration](23_open_data_integration.md)
