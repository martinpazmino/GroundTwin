---
title: "25. Federal State DGM1 & LoD2 Service Research"
---

# 25. Federal State DGM1 & LoD2 Service Research

> Research and live verification (`2026-11-06`) of public Digital Terrain Model (`DGM1`) and 3D building (`LoD2`) services for the 13 German federal states (*Länder*) that previously had only `portal-dgm` or `portal-gebaeude` entries in [`services/geodaten/geodaten/dienste.json`](../services/geodaten/geodaten/dienste.json). See [23. Open Geodata Integration](23_open_data_integration.md) for the service architecture.

---

## 1. Scope and Verification Method

GroundTwin currently supports two automated raster/building service types in `services/geodaten/geodaten/`:

- **`wcs-dgm`** ([`dgm_dienst.py`](../services/geodaten/geodaten/dgm_dienst.py)): OGC Web Coverage Service 2.0.1 (`GetCapabilities`, `DescribeCoverage`, `GetCoverage` with `FORMAT=image/tiff` and `SUBSET={ax_x}({x0},{x1})` / `SUBSET={ax_y}({y0},{y1})`). Requires metric grid spacing (`raster_m <= 2.0`), ETRS89/UTM (`EPSG:25832` or `EPSG:25833`), and floating-point heights in metres (`Float32` GeoTIFF) suitable for `GOK` verification within `±0.5 m`.
- **`lod2-kacheln`** ([`gebaeude.py`](../services/geodaten/geodaten/gebaeude.py)): Direct HTTP/HTTPS download of `1×1 km` CityGML (`.gml` or `.zip`) tiles addressed by 3-digit UTM kilometer coordinates `{e}` and `{n}` (`int(math.floor(x / 1000.0))`).

All 13 *Länder* without active `wcs-dgm` / `lod2-kacheln` connections (**SH, HH, NI, HB, HE, RP, BW (LoD2), BY, SL, MV, SN, ST, TH**) were researched via the official state geoportals, GDI-DE (`gdk.gdi-de.org`), MetaVer (`metaver.de`), INSPIRE Atom feeds, Metalink (`.meta4`) descriptors, and STAC APIs, and tested live from this workstation on `2026-11-06` using `geodaten.netz` (`certifi` TLS bundle).

---

## 2. Overview Table: `Land × (DGM1, LoD2)`

| Land | Theme | Finding & Official Source (*Fundstelle*) | Protocol / Format | Tested URL / Endpoint | License | Live Check (`2026-11-06`) | Status in `dienste.json` |
|---|---|---|---|---|---|---|---|
| **SH** (Schleswig-Holstein) | **DGM1** | LVermGeo SH INSPIRE Download Service ([Atom feed](https://service.gdi-sh.de/INSPIRE_Atom/EL/SH_INSPIREDOWNLOAD_AII_EL_DGM1.xml)) | INSPIRE Atom + `1×1 km` GeoTIFF (`EPSG:25832`, `{jahr}` in filename) | `https://service.gdi-sh.de/INSPIRE_Atom/EL/SH_INSPIREDOWNLOAD_AII_EL_DGM1.xml` (tiles: `.../EL/data/dgm1_32_{e}_{n}_1_sh_{jahr}.tif`) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (`© GeoBasis-DE/LVermGeo SH`) | `2026-11-06`, HTTP `200`, `297 ms` (Atom feed) | Portal (`SH-DGM` `ungeprueft`; needs `atom-kacheln` due to `{jahr}`) |
| **SH** (Schleswig-Holstein) | **LoD2** | LVermGeo SH Massendownload Client (`geodaten.schleswig-holstein.de`) | Custom GeoJSON index + CityGML tiles (`EPSG:25832`) | `https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/dl-lod2.html` | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (`© GeoBasis-DE/LVermGeo SH`) | `2026-11-06`, TLS error (`SSLCertVerificationError: unable to get local issuer certificate`), `266 ms` | `geprueft_nicht_aufgenommen` (missing intermediate TLS cert + `{jahr}`) |
| **HH** (Hamburg) | **DGM1** | Transparenzportal Hamburg / LGV ([CKAN record](https://transparenz.hamburg.de/)) | City-wide ZIP archive (`GeoTIFF` / `XYZ`, `EPSG:25832`, 1.3 GB) | `https://archiv.transparenz.hamburg.de/hmbtgarchive/HMDK/dgm1_hh_2022-04-30_258334_snap_1.zip` | [dl-de/by-2.0](https://www.govdata.de/dl-de/by-2-0) (`Freie und Hansestadt Hamburg, LGV`) | `2026-11-06`, HTTP `200`, `594 ms` | Portal (`HH-DGM` `ungeprueft`; city-wide archive, no WCS/tile URL) |
| **HH** (Hamburg) | **LoD2** | Transparenzportal Hamburg / LGV (`3d-gebaeudemodell-lod2-de-hamburg2`) | City-wide ZIP (`CityGML`, 628 MB) & Cesium 3D Tiles | `https://daten-hamburg.de/opendata/3d_stadtmodell_lod2/LoD2-DE_HH_2026-04-28.zip` (3D Tiles: `https://daten-hamburg.de/gdi3d/datasource-data/LoD2/tileset.json`) | [dl-de/by-2.0](https://www.govdata.de/dl-de/by-2-0) (`Freie und Hansestadt Hamburg, LGV`) | `2026-11-06`, HTTP `200`, `359 ms` (ZIP) / HTTP `200`, `250 ms` (3D Tiles) | Portal (`HH-LOD2` `ungeprueft`; city-wide archive, not `1×1 km` tiles) |
| **NI** (Niedersachsen) | **DGM1** | LGLN OpenGeoData WCS (`ni_dgm1`) ([Capabilities](https://opendata.geoservices.lgln.niedersachsen.de/dgm_wcs?SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCapabilities)) & [STAC API](https://dgm.stac.lgln.niedersachsen.de/collections/dgm1) | **`wcs-dgm`** (WCS 2.0.1, `Float32` GeoTIFF, `1.0 m`, `EPSG:25832`) | `https://opendata.geoservices.lgln.niedersachsen.de/dgm_wcs` | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (`© LGLN ({jahr}), CC BY 4.0`) | `2026-11-06`, HTTP `200`, `594 ms` (Capabilities) / `1750 ms` (`pruefen_live`) / `7562 ms` (`GetCoverage` 20×20 m Hannover: `55.42..56.17 m`) | **Added as `NI-DGM1`** (`wcs-dgm`, `geprueft: 2026-11-06`, `aktiv: false`*) |
| **NI** (Niedersachsen) | **LoD2** | LGLN OpenGeoData S3 via [STAC API](https://lod.stac.lgln.niedersachsen.de/collections/lod2) | **`lod2-kacheln`** (`1×1 km` CityGML `.gml`, `EPSG:25832`) | `https://lod2.s3.eu-de.cloud-object-storage.appdomain.cloud/LoD2_32_{e}_{n}_1_ni.gml` | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (`© LGLN ({jahr}), CC BY 4.0`) | `2026-11-06`, HTTP `206`, `313 ms` (`pruefen_live` tile `504/5827`) / HTTP `200`, `453 ms` (Hannover tile `550/5802`, 14 buildings in 200×200 m) | **Added as `NI-LOD2-GML`** (`lod2-kacheln`, `geprueft: 2026-11-06`, `aktiv: false`*) |
| **HB** (Bremen) | **DGM1** | Landesamt GeoInformation Bremen via [MetaVer CSW](https://metaver.de/csw) (`BBD9398C-9F3F-4D53-AE04-9E9C2658A2A8`) | City-wide ZIP (`ASCII XYZ`, `EPSG:25832`) | `https://gdi2.geo.bremen.de/inspire/download/DGM/data/Gitternetz_DGM1_2017_HB_ASCII_XYZ.zip` (BHV: `..._2015_BHV_ASCII_XYZ.zip`) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (`Quelle: Landesamt GeoInformation Bremen`) | `2026-11-06`, HTTP `206`, `344 ms` (HB) / HTTP `206`, `172 ms` (BHV) | Portal (`HB-DGM` `ungeprueft`; city-wide XYZ archive) |
| **HB** (Bremen) | **LoD2** | Landesamt GeoInformation Bremen via [MetaVer CSW](https://metaver.de/csw) (`07447560-2EF9-4ADC-9BF5-39A5A11A6535`) | City-wide ZIP (`CityGML`, `EPSG:25832`) & Cesium 3D Tiles | `https://gdi2.geo.bremen.de/inspire/download/LoD/data/LOD2_CITYGML_HB.zip` (BHV: `..._BHV.zip`) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (`Quelle: Landesamt GeoInformation Bremen`) | `2026-11-06`, HTTP `206`, `234 ms` (`LOD2_CITYGML_HB.zip`) | Portal (`HB-LOD2` `ungeprueft`; city-wide archive) |
| **HE** (Hessen) | **DGM1** | HVBG Geodaten-Shop ([ISO 19139 Metadata](https://www.geoportal.hessen.de/mapbender/php/mod_dataISOMetadata.php?outputFormat=iso19139&id=dbf48a95-b44d-48b3-a5b4-981e4c1bd8e6)) | Intershop Downloadcenter (ZIP tiles) & WMS (`inspire-hessen.de`, no WCS) | `https://gds.hessen.de/INTERSHOP/web/WFS/HLBG-Geodaten-Site/de_DE/-/EUR/ViewDownloadcenter-Start?path=3D-Daten/Digitales%20Gel%C3%A4ndemodell%20(DGM1)` | [dl-de/zero-2.0](https://www.govdata.de/dl-de/zero-2-0) (`HVBG`) | `2026-11-06`, HTTP `200`, `297 ms` (Downloadcenter); `inspire-hessen.de/raster/wms/dgm1/ows?SERVICE=WCS`: HTTP `200` `ServiceException` (`375 ms`) | `geprueft_nicht_aufgenommen` (WMS only; Downloadcenter uses session IDs `;pgid=...`) |
| **HE** (Hessen) | **LoD2** | HVBG Geodaten-Shop ([ISO 19139 Metadata](https://www.geoportal.hessen.de/mapbender/php/mod_dataISOMetadata.php?outputFormat=iso19139&id=d7997493-bdf2-4025-86e9-45c5432cdb4f)) | Intershop Downloadcenter (ZIP tiles, `CityGML`) | `https://gds.hessen.de/INTERSHOP/web/WFS/HLBG-Geodaten-Site/de_DE/-/EUR/ViewDownloadcenter-Start?path=3D-Daten/3D-Geb%C3%A4udemodelle/3D-Geb%C3%A4udemodelle%20LoD2` | [dl-de/zero-2.0](https://www.govdata.de/dl-de/zero-2-0) (`HVBG`) | `2026-11-06`, HTTP `200`, `390 ms` (Downloadcenter) | Portal (`HE-LOD2` `ungeprueft`; dynamic Intershop session URLs) |
| **RP** (Rheinland-Pfalz) | **DGM1** | LVermGeo RLP OpenData ([Metalink](https://geobasis-rlp.de/data/dgm1/current/meta4/dgm1_tif_07.meta4) & [Product JSON](https://geoshop.rlp.de/files/anpassungen/hvd/products/dgm1.json)) | Metalink v4 + `1×1 km` GeoTIFF (`EPSG:25832`, `{jahr}` in filename) | `https://geobasis-rlp.de/data/dgm1/current/meta4/dgm1_tif_07.meta4` (tiles: `.../current/tif/dgm1_32_{e}_{n}_1_rp_{jahr}.tif`) | [dl-de/by-2.0](https://www.govdata.de/dl-de/by-2-0) (`© GeoBasis-DE / LVermGeoRP {jahr}`) | `2026-11-06`, HTTP `200`, `313 ms` (`.meta4`) / HTTP `200`, `312 ms` (`dgm1.json`) | Portal (`RP-DGM` `ungeprueft`; needs `metalink-kacheln` due to `{jahr}`) |
| **RP** (Rheinland-Pfalz) | **LoD2** | LVermGeo RLP OpenData ([Metalink](https://geobasis-rlp.de/data/geb3dlo/current/meta4/geb3dlo_gml_07.meta4) & [Product JSON](https://geoshop.rlp.de/files/anpassungen/hvd/products/geb3dlo.json)) | `2×2 km` CityGML tiles (`.gml`, even km grid, `EPSG:25832`) | `https://geobasis-rlp.de/data/geb3dlo/current/gml/LoD2_32_{e}_{n}_2_RP.gml` | [dl-de/by-2.0](https://www.govdata.de/dl-de/by-2-0) (`© GeoBasis-DE / LVermGeoRP {jahr}`) | `2026-11-06`, HTTP `206`, `172 ms` (`pruefen_live` tile `378/5534`) / HTTP `200`, `422 ms` (Mainz tile `446/5538`) | `geprueft_nicht_aufgenommen` (`kachel_km: 2`; `gebaeude.py:170` hardcodes `km=1`) |
| **BW** (Baden-Württemberg) | **LoD2** | LGL OpenGeodata BW ([Product Config](https://opengeodata.lgl-bw.de/assets/config/local/odp-products.json)) | Interactive Vector-Tile Grid (`zwei_km_gitter`) + `2×2 km` CityGML ZIPs (`EPSG:25832`) | `https://opengeodata.lgl-bw.de/assets/config/local/odp-products.json` (`pattern: LoD2_\d+_(\d+_\d+)_\d+_bw\.zip`) | [dl-de/by-2.0](https://www.govdata.de/dl-de/by-2-0) (`© LGL-BW, www.lgl-bw.de`) | `2026-11-06`, HTTP `200`, `531 ms` (`odp-products.json`) / HTTP `200`, `312 ms` (`config.json`) | Portal (`BW-LOD2` `ungeprueft`; tile URLs come from vector-tile feature attributes) |
| **BY** (Bayern) | **DGM1** | LDBV OpenData Bayern ([Metalink](https://geodaten.bayern.de/odd/a/dgm/dgm1/meta/metalink/09.meta4)) | Direct `1×1 km` GeoTIFF tiles (`.tif`, `EPSG:25832`) + Metalink v4 | `https://download1.bayernwolke.de/a/dgm/dgm1/{e}_{n}.tif` | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (`Datenquelle: Bayerische Vermessungsverwaltung – www.geodaten.bayern.de`) | `2026-11-06`, HTTP `200`, `343 ms` (Munich tile `691_5334.tif`) / HTTP `200`, `328 ms` (`09.meta4`) | Portal (`BY-DGM` `ungeprueft`; needs `dgm-kacheln` service type) |
| **BY** (Bayern) | **LoD2** | LDBV OpenData Bayern ([Metalink](https://geodaten.bayern.de/odd/a/lod2/citygml/meta/metalink/09.meta4)) | `2×2 km` CityGML tiles (`.gml`, even km grid, `EPSG:25832`) | `https://download1.bayernwolke.de/a/lod2/citygml/{e}_{n}.gml` | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (`Datenquelle: Bayerische Vermessungsverwaltung – www.geodaten.bayern.de`) | `2026-11-06`, HTTP `206`, `156 ms` (`pruefen_live` tile `676/5420`) / HTTP `200`, `422 ms` (Munich tile `690_5334.gml`) | `geprueft_nicht_aufgenommen` (`kachel_km: 2`; `gebaeude.py:170` hardcodes `km=1`) |
| **SL** (Saarland) | **DGM1** | LVGL Saarland Geoportal / Shop (`Freie Geobasisdaten`) | Interactive Shop / Portal (`shop.lvgl.saarland.de`) | `https://www.shop.lvgl.saarland.de/cloud/freiegeobasisdaten` | Unclear from public machine-readable metadata (portal states free geobasis data; verify with LVGL before redistribution) | `2026-11-06`, HTTP `200`, `1796 ms` (shop page) | Portal (`SL-DGM` `ungeprueft`; no WCS or static tile URL found) |
| **SL** (Saarland) | **LoD2** | LVGL Saarland Geoportal / Shop (`Saarland 3D`) | Interactive Shop / Portal (`geoportal.saarland.de`) | `https://geoportal.saarland.de/` | Unclear from public machine-readable metadata (verify with LVGL before redistribution) | `2026-11-06`, HTTP `200`, `1812 ms` (portal page) | Portal (`SL-LOD2` `ungeprueft`; no static tile URL found) |
| **MV** (Mecklenburg-Vorpommern) | **DGM1** | LAiV MV WCS (`mv_dgm`) ([Capabilities](https://www.geodaten-mv.de/dienste/dgm_wcs?SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCapabilities)) & [INSPIRE Atom](https://www.geodaten-mv.de/dienste/dgm_atom?type=service&id=af263468-065b-4e92-a2c0-7b1734955200) | **`wcs-dgm`** (WCS 2.0.1, `Float32` GeoTIFF, `1.0 m`, `EPSG:25833`) | `https://www.geodaten-mv.de/dienste/dgm_wcs` | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.de) (`© GeoBasis-DE/M-V ({jahr})`) | `2026-11-06`, HTTP `200`, `500 ms` (Capabilities) / `297 ms` (`pruefen_live`) / `344 ms` (`GetCoverage` 20×20 m Rostock: `16.36..16.71 m`) | **Added as `MV-DGM1`** (`wcs-dgm`, `geprueft: 2026-11-06`, `aktiv: false`*) |
| **MV** (Mecklenburg-Vorpommern) | **LoD2** | LAiV MV INSPIRE Download Service ([Atom Dataset Feed](https://www.geodaten-mv.de/dienste/gebaeude_atom?type=dataset&id=8397b554-5cb9-4274-8be8-c20490d9a6e8)) | `2×2 km` CityGML ZIP tiles (`EPSG:25833`, even km grid) | `https://www.geodaten-mv.de/dienste/gebaeude_download?index=0&dataset=8397b554-5cb9-4274-8be8-c20490d9a6e8&file=lod2_33_{e}_{n}_2_gml.zip` | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.de) (`© GeoBasis-DE/M-V (Jahr der letzten Datenlieferung)`) | `2026-11-06`, HTTP `200`, `485 ms` (`pruefen_live` tile `334/5974`) / HTTP `200`, `594 ms` (Rostock tile `312/5996`) | `geprueft_nicht_aufgenommen` (`kachel_km: 2`; `gebaeude.py:170` hardcodes `km=1`) |
| **SN** (Sachsen) | **DGM1** | GeoSN Batch-Download ([Product Page](https://www.geodaten.sachsen.de/batch-download-4719.html)) | Nextcloud/WebDAV `2×2 km` GeoTIFF ZIP tiles (`EPSG:25833`) | `https://geocloud.landesvermessung.sachsen.de/public.php/dav/files/JCcXyifaNdLDnxZ/dgm1_33{e}_{n}_2_sn_tiff.zip` | [dl-de/by-2.0](https://www.govdata.de/dl-de/by-2-0) (`© GeoBasis-DE / GeoSN ({jahr}), dl-de/by-2-0`) | `2026-11-06`, HTTP `200`, `578 ms` (Dresden tile `410_5656`) | Portal (`SN-DGM` `ungeprueft`; needs `dgm-kacheln` service type) |
| **SN** (Sachsen) | **LoD2** | GeoSN Batch-Download ([Product Page](https://www.geodaten.sachsen.de/batch-download-4719.html)) | Nextcloud/WebDAV `2×2 km` CityGML ZIP tiles (`EPSG:25833`, even km grid) | `https://geocloud.landesvermessung.sachsen.de/public.php/dav/files/AyJqXpJAZJXomCb/lod2_33{e}_{n}_2_sn_citygml.zip` | [dl-de/by-2.0](https://www.govdata.de/dl-de/by-2-0) (`© GeoBasis-DE / GeoSN ({jahr}), dl-de/by-2-0`) | `2026-11-06`, HTTP `206`, `593 ms` (`pruefen_live` tile `390/5642`) / HTTP `200`, `500 ms` (Dresden tile `410_5656`) | `geprueft_nicht_aufgenommen` (`kachel_km: 2`; `gebaeude.py:170` hardcodes `km=1`) |
| **ST** (Sachsen-Anhalt) | **DGM1** | LVermGeo ST WCS (`Coverage1`) ([Capabilities](https://www.geodatenportal.sachsen-anhalt.de/ows_WCS_ST_DGM1?SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCapabilities)) | WCS 2.0.1 returning MIME `multipart/related` (GML + GeoTIFF, `EPSG:25832`) | `https://www.geodatenportal.sachsen-anhalt.de/ows_WCS_ST_DGM1` | [dl-de/by-2.0](https://www.govdata.de/dl-de/by-2-0) (`© GeoBasis-DE / LVermGeo ST`) | `2026-11-06`, HTTP `200`, `407 ms` (Capabilities & DescribeCoverage) / HTTP `200`, `484 ms` (`GetCoverage` returns `multipart/related; boundary="wcs"`) | `geprueft_nicht_aufgenommen` (`dgm_dienst._laden` cannot parse MIME multipart wrapper yet) |
| **ST** (Sachsen-Anhalt) | **LoD2** | LVermGeo ST INSPIRE Download Service ([Atom Dataset Feed](https://geodatenportal.sachsen-anhalt.de/arcgisinspire/rest/directories/web/INSPIRE_ALKIS/ALKIS_LOD2_BU/datasetlod2.xml)) | INSPIRE Atom + per-municipality ZIP (`INSPIRE Building3D GML`, `EPSG:4258`) | `https://geodatenportal.sachsen-anhalt.de/arcgisinspire/rest/directories/web/INSPIRE_ALKIS/ALKIS_LOD2_BU/servicelod2.xml` | [dl-de/by-2.0](https://www.govdata.de/dl-de/by-2-0) (`© GeoBasis-DE / LVermGeo ST`) | `2026-11-06`, HTTP `200`, `406 ms` (`servicelod2.xml`) / HTTP `200`, `1110 ms` (`datasetlod2.xml`) | Portal (`ST-LOD2` `ungeprueft`; municipality ZIPs in `EPSG:4258`, not UTM grid tiles) |
| **TH** (Thüringen) | **DGM1** | TLBG Geoportal / Geoproxy (`DGM`, `INSPIREel`) | WMS only (`geoproxy.geoportal-th.de`); portal gated by Friendly Captcha | `https://www.geoproxy.geoportal-th.de/geoproxy/services/DGM` | [dl-de/by-2.0](https://www.govdata.de/dl-de/by-2-0) (`© GDI-Th`, per WMS Capabilities) | `2026-11-06`, HTTP `200`, `484 ms` (`SERVICE=WCS` returns `<WMS_Capabilities>`); `www.geoportal-th.de` returns Friendly Captcha challenge (`890 ms`) | `geprueft_nicht_aufgenommen` (no WCS; download portal gated by anti-bot challenge) |
| **TH** (Thüringen) | **LoD2** | TLBG Geoportal (`Download-Offene-Geodaten-Thüringen`) | Portal gated by Link11 / Friendly Captcha (`friendly-challenge@0.9.11`) | `https://www.geoportal-th.de/de-de/Downloadbereiche/Download-Offene-Geodaten-Th%C3%BCringen` | Unclear without bypassing CAPTCHA (WMS metadata indicates `dl-de/by-2.0`) | `2026-11-06`, HTTP `200`, `890 ms` (serves anti-bot challenge page; not bypassed per safety rules) | Portal (`TH-LOD2` `ungeprueft`; gated by CAPTCHA challenge) |

*\*Note on `aktiv: false` for `NI-DGM1`, `NI-LOD2-GML`, and `MV-DGM1`:* These three services are fully verified against `dgm_dienst._laden`, `gebaeude._laden`, `dienste.pruefen_live`, and `scripts/dienste_pruefen.py`. They are stored with `"aktiv": false` in `dienste.json` because [`tests/test_bohrdaten.py`](../tests/test_bohrdaten.py) (line 173) and [`tests/test_gebaeude.py`](../tests/test_gebaeude.py) (line 125) assert the exact string `"angebunden: Berlin, Brandenburg, Nordrhein-Westfalen; im Portal des Landes: "` from `bohrdaten.ohne_dienst()`. Updating those two test assertions allows flipping `"aktiv"` to `true` immediately.

---

## 3. Proposed New Service Types and Code Extensions (Sorted by Utility)

Many *Länder* publish their `DGM1` and `LoD2` datasets as Open Data without registration, but slight protocol differences prevent [`dgm_dienst.py`](../services/geodaten/geodaten/dgm_dienst.py) or [`gebaeude.py`](../services/geodaten/geodaten/gebaeude.py) from reading them today. Below are the proposed extensions, ranked by how many additional *Länder* each change unlocks.

### 3.1 Pass `kachel_km` to `kacheln()` in `lod2-kacheln` — Unlocks **4 Länder (BY, RP, MV, SN)**

- **Coverage:** **Bayern (`BY`)**, **Rheinland-Pfalz (`RP`)**, **Mecklenburg-Vorpommern (`MV`)**, and **Sachsen (`SN`)**.
- **Problem:** [`dienste.py`](../services/geodaten/geodaten/dienste.py) already defines `"kachel_km"` as a required field of `lod2-kacheln`, and `dienste.pruefen_live()` (line 146) correctly rounds the test coordinate to multiples of `kachel_km` (` int(math.floor(x / 1000.0 / km)) * km`). However, [`gebaeude.py`](../services/geodaten/geodaten/gebaeude.py) line 170 calls `for e, n in kacheln(x0n, y0n, x1n, y1n):` without passing `km=int(d.get("kachel_km") or 1)`. Because `kacheln()` defaults to `km=1`, any query covering an odd kilometer coordinate requests non-existent odd tiles (`HTTP 404`) from 2×2 km tile servers.
- **How the code would read it:** Pass `km=int(d.get("kachel_km") or 1)` in `gebaeude._laden()` (`gebaeude.py:170`). No new service type is required; the four services in `geprueft_nicht_aufgenommen` (`BY`, `RP`, `MV`, `SN`) can immediately move into `dienste` as `lod2-kacheln` with `"kachel_km": 2`.

### 3.2 New Service Type `dgm-kacheln` (Direct HTTP GeoTIFF / ZIP Tile Templates) — Unlocks **2 Länder (BY, SN)**

- **Coverage:** **Bayern (`BY`)** (`1×1 km` `.tif` in `EPSG:25832`) and **Sachsen (`SN`)** (`2×2 km` `.zip` containing `.tif` in `EPSG:25833`).
- **Problem:** Neither Bayern nor Sachsen operates a public `wcs-dgm` endpoint, but both provide deterministic static URLs with kilometer placeholders `{e}` and `{n}`:
  - `BY`: `https://download1.bayernwolke.de/a/dgm/dgm1/{e}_{n}.tif` (`kachel_km: 1`, `format: "tif"`)
  - `SN`: `https://geocloud.landesvermessung.sachsen.de/public.php/dav/files/JCcXyifaNdLDnxZ/dgm1_33{e}_{n}_2_sn_tiff.zip` (`kachel_km: 2`, `format: "zip"`)
- **How the code would read it:** In `dgm_dienst.py`, add support for `art == "dgm-kacheln"` with fields `url` (containing `{e}` and `{n}`), `system` (`25832` / `25833`), `format` (`"tif"` or `"zip"`), `kachel_km` (`1` or `2`), and `raster_m` (`1.0`). For a query bounding box `(x0, y0, x1, y1)`, compute the intersecting tiles via `gebaeude.kacheln(x0, y0, x1, y1, km=d["kachel_km"])`, fetch the GeoTIFF (extracting `.tif` from `.zip` in memory if `format == "zip"`), and pass only pixels inside `(x0, y0, x1, y1)` to `gelaende.lesen()` — or read the raster window directly via `tifffile` / `imagecodecs` so memory usage stays small even for `2×2 km` tiles.

### 3.3 New Service Type `index-kacheln` (Metalink `.meta4` / INSPIRE Atom / STAC Tile Discovery) — Unlocks **3 Länder for DGM1 (SH, RP, NI-STAC) and 1 Land for LoD2 (BW)**

- **Coverage:** **Schleswig-Holstein (`SH`)** DGM1 (INSPIRE Atom), **Rheinland-Pfalz (`RP`)** DGM1 (Metalink `.meta4`), **Niedersachsen (`NI`)** DGM1/LoD2 (STAC API), and **Baden-Württemberg (`BW`)** LoD2.
- **Problem:** Several states include the survey year `{jahr}` or lot number in each `1×1 km` tile filename (e.g., `dgm1_32_568_6018_1_sh_2023.tif` in SH, `dgm1_32_446_5538_1_rp_2023.tif` in RP), so the URL cannot be formed from `{e}` and `{n}` alone without looking up the filename in an XML/JSON index.
- **How the code would read it:**
  - **Metalink / Atom (`RP`, `SH`):** Download and cache the `.meta4` or Atom XML feed (typically 0.5–3 MB), regex-index all `<url>` / `<link rel="section" href="...">` entries by their `(e, n)` kilometer pair (`dgm1_\d+_(\d+)_(\d+)_1_`), and then fetch the exact tile URL for the requested `kacheln()`.
  - **STAC (`NI`):** Query `GET {stac_url}/items?bbox={lon0},{lat0},{lon1},{lat1}` and download the asset `href` from the returned GeoJSON feature collection.

### 3.4 MIME `multipart/related` Unpacking in `wcs-dgm` — Unlocks **1 Land (ST DGM1)**

- **Coverage:** **Sachsen-Anhalt (`ST`)** (`https://www.geodatenportal.sachsen-anhalt.de/ows_WCS_ST_DGM1`, `CoverageId=Coverage1`).
- **Problem:** When `dgm_dienst._laden()` requests `FORMAT=image/tiff` from Sachsen-Anhalt's ArcGIS WCS 2.0.1 server, the server responds with `Content-Type: multipart/related; boundary="wcs"; start="GML-Part"; type="text/xml"`, placing a `<gmlcov:RectifiedGridCoverage>` XML part before the binary GeoTIFF (`II*\x00...`). Passing the raw HTTP body to `gelaende.lesen("dgm.tif", daten)` fails because the payload does not start with a TIFF header.
- **How the code would read it:** In `dgm_dienst._laden()`, before calling `gelaende.lesen("dgm.tif", daten)`, check if `daten` starts with `--` (MIME boundary) and contains `b"II*\x00"` or `b"MM\x00*"` after a `\r\n\r\n` part header; if so, slice out the binary TIFF part (up to the closing `\r\n--` boundary) and pass it to `gelaende.lesen()`.

---

## 4. Appendix: Full Output of `python scripts/dienste_pruefen.py`

```text
Python 3.11.0 · Windows 10 · OpenSSL 1.1.1q  5 Jul 2022 · certifi 2025.01.31
ok    DE-BGR   portal-bohrungen boreholemap.bgr.de           2 KB in 1.8 s
ok    SH       portal-bohrungen www.schleswig-holstein.de    275 KB in 1.4 s
ok    SH-DGM   portal-dgm      opendata.schleswig-holstein.de 149 KB in 1.4 s
ok    SH-LOD2  portal-gebaeude opendata.schleswig-holstein.de 149 KB in 1.1 s
ok    HH       portal-bohrungen www.hamburg.de               300 KB in 1.0 s
ok    HH-DGM   portal-dgm      transparenz.hamburg.de       45 KB in 0.5 s
ok    HH-LOD2  portal-gebaeude transparenz.hamburg.de       45 KB in 0.7 s
ok    NI       portal-bohrungen nibis.lbeg.de                Server antwortet (HTTP 401), Zertifikat gültig
ok    NI-DGM   portal-dgm      ni-lgln-opengeodata.hub.arcgis.com 88 KB in 2.5 s
ok    NI-DGM1  wcs-dgm         opendata.geoservices.lgln.niedersachsen.de 9 KB in 0.7 s
ok    NI-LOD2  portal-gebaeude ni-lgln-opengeodata.hub.arcgis.com 88 KB in 0.6 s
ok    NI-LOD2-GML lod2-kacheln    lod2.s3.eu-de.cloud-object-storage.appdomain.cloud 337 KB in 1.8 s
ok    HB       portal-bohrungen www.gdfb.de                  75 KB in 0.6 s
ok    HB-DGM   portal-dgm      geoportal.bremen.de          Server antwortet (HTTP 404), Zertifikat gültig
ok    HB-LOD2  portal-gebaeude geoportal.bremen.de          Server antwortet (HTTP 404), Zertifikat gültig
ok    NW       wfs-boreholeml  www.bml3.nrw.de              16 KB in 0.4 s
ok    NW-DGM1  wcs-dgm         www.wcs.nrw.de               11 KB in 0.4 s
ok    NW-LOD2  lod2-kacheln    www.opengeodata.nrw.de       876 Byte in 1.4 s
ok    HE       portal-bohrungen geologie.hessen.de           4 KB in 1.7 s
ok    HE-DGM   portal-dgm      gds.hessen.de                14 KB in 1.0 s
ok    HE-LOD2  portal-gebaeude gds.hessen.de                14 KB in 0.7 s
ok    RP       portal-bohrungen www.lgb-rlp.de               130 KB in 0.7 s
ok    RP-DGM   portal-dgm      lvermgeo.rlp.de              124 KB in 0.5 s
ok    RP-LOD2  portal-gebaeude lvermgeo.rlp.de              124 KB in 0.6 s
ok    BW       wfs-boreholeml  services.lgrb-bw.de          26 KB in 0.5 s
ok    BW-DGM   portal-dgm      opengeodata.lgl-bw.de        56 KB in 0.6 s
ok    BW-LOD2  portal-gebaeude opengeodata.lgl-bw.de        56 KB in 0.5 s
ok    BY       portal-bohrungen www.umweltatlas.bayern.de    12 KB in 0.9 s
ok    BY-DGM   portal-dgm      geodaten.bayern.de           105 Byte in 0.3 s
ok    BY-LOD2  portal-gebaeude geodaten.bayern.de           105 Byte in 0.3 s
ok    SL       portal-bohrungen geoportal.saarland.de        29 KB in 1.7 s
ok    SL-DGM   portal-dgm      geoportal.saarland.de        29 KB in 1.7 s
ok    SL-LOD2  portal-gebaeude geoportal.saarland.de        29 KB in 1.6 s
ok    BE       wfs-kopf        gdi.berlin.de                94 KB in 0.8 s
ok    BE-LOD2  lod2-kacheln    gdi.berlin.de                501 Byte in 0.3 s
ok    BB       wfs-kopf        inspire.brandenburg.de       33 KB in 0.7 s
ok    BB-DGM1  wcs-dgm         isk.geobasis-bb.de           9 KB in 0.4 s
ok    BB-LOD2  lod2-kacheln    data.geobasis-bb.de          3 KB in 0.4 s
ok    MV       portal-bohrungen www.umweltkarten.mv-regierung.de 798 Byte in 0.8 s
ok    MV-DGM   portal-dgm      www.geoportal-mv.de          41 KB in 1.4 s
ok    MV-DGM1  wcs-dgm         www.geodaten-mv.de           12 KB in 0.8 s
ok    MV-LOD2  portal-gebaeude www.geoportal-mv.de          41 KB in 0.6 s
ok    SN       portal-bohrungen www.lfulg.sachsen.de         89 KB in 0.7 s
ok    SN-DGM   portal-dgm      www.geodaten.sachsen.de      83 KB in 0.7 s
ok    SN-LOD2  portal-gebaeude www.geodaten.sachsen.de      83 KB in 1.0 s
ok    ST       portal-bohrungen lagb.sachsen-anhalt.de       155 KB in 1.7 s
ok    ST-DGM   portal-dgm      www.lvermgeo.sachsen-anhalt.de 565 KB in 1.7 s
ok    ST-LOD2  portal-gebaeude www.lvermgeo.sachsen-anhalt.de 565 KB in 1.6 s
ok    TH       portal-bohrungen tlubn.thueringen.de          44 KB in 0.6 s
ok    TH-DGM   portal-dgm      www.geoportal-th.de          44 KB in 1.0 s
ok    TH-LOD2  portal-gebaeude www.geoportal-th.de          44 KB in 1.1 s
alle Dienste erreichbar
```

Up: [Index](README.md)
