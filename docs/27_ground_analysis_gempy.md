---
title: "27 Ground Analysis: GemPy and the analysis of the Baugrundmodell (plan)"
date: 2026-11-10
tags: [ground-analysis, gempy, implicit-modelling, uncertainty, cross-validation, orientations, plan]
aliases: [Ground Analysis, GemPy integration, N4 implicit model]
status: g3-built
---

# 27 Ground Analysis: GemPy and the analysis of the Baugrundmodell (plan)

A new component, **Ground Analysis**, answers the question the layer model ([18](18_layer_modeler.md)) leaves open:
*how far can the model be trusted between the Bohrungen?* This note covers:

- what [GemPy](https://github.com/gempy-project/gempy) offers and what it needs;
- what was measured with it on this project's data;
- how to solve the missing dip of the layers;
- the component, its place in the system and the phases.

> [!IMPORTANT]
> **Status 2026-11-11: phases G1, G2 and G3 are built.**
> - G1 is in [`services/analyse`](../services/analyse) (package `baugrundanalyse`): Kreuzprobe, Unsicherheit and
>   virtuelle Bohrung, without GemPy (§6.1).
> - G2 puts them in the app, step *Einheiten → Erweitert* (§6.2).
> - G3 adds the implicit method with GemPy as an optional third interpolation (§6.3).
>
> G4 (structures set by the engineer) is not built.

> [!NOTE]
> Summary:
> - **GemPy fits as an optional third interpolation method, not as a replacement of the layer model.** On clean
>   layered data it predicts a held-out Bohrung better than IDW. On noisy urban data it is no better than IDW and
>   cannot keep the contacts exact. On a plain inclined plane the thin-plate spline already used is exact (§3).
> - **The missing dip is not a blocker.** GemPy needs one orientation per structural group, and its own borehole
>   tutorial sets a single horizontal one. Measured: with a horizontal orientation the contacts are still reproduced
>   within 2 cm, and a plane fitted through the contacts of an Einheit gives the dip where three Bohrungen that are
>   not in a line exist (§4).
> - **Each Einheit must be its own structural group.** With all Einheiten in one group, GemPy cannot let a layer
>   pinch out: contacts were missed by up to 18 m (§3.2).
> - **The first value of Ground Analysis needs no GemPy at all**: a leave-one-out cross-check and an uncertainty
>   estimate per Einheit, with the interpolators the modeler already has. GemPy comes second, measured against that
>   yardstick (§6).
> - **Licence**: GemPy and its engine are EUPL-1.2, which names the AGPL v3 as a compatible licence. The core install
>   is small: `gempy`, `gempy_engine`, numpy, pydantic.

## 1. What GemPy is (read 2026-11-10, commit `8283735`, release 2026.0.3)

GemPy builds an *implicit* model: for each structural group it interpolates one scalar field in 3D from two kinds of
input, and every layer boundary of that group is an iso-surface of the field.

| Input | Meaning | Minimum |
|---|---|---|
| Surface points | points on the **base** of a unit (x, y, z) | 2 per unit |
| Orientations | a point with the direction perpendicular to the layering (pole vector, or azimuth and dip) | 1 per structural group |
| Structural frame | units ordered into groups; relation of a group to those below: `ERODE`, `ONLAP`, `FAULT` | set by the modeller |

What the packages give (all EUPL-1.2 unless noted):

| Package | Content | Needed here |
|---|---|---|
| `gempy` + `gempy_engine` | data classes, the interpolator (numpy; PyTorch optional), octrees, dual-contouring meshes, evaluation at any points (`compute_model_at`), topography, sections, save/load as JSON, a nugget optimiser | yes (optional install) |
| `gempy_viewer` | plots with matplotlib and PyVista | no: the app has its own viewer |
| `subsurface` + `structural_elements_from_borehole_set` | borehole import from tables | no: the Bohrungen are already structured; the import creates **no** orientations |
| `gempy_plugins` | kriging of properties (gstools), gravity | later (Kennwerte) |
| `gempy_probability` | probabilistic models (Pyro); last release 2024.1.1 | later; heavy, and older than the engine |

Useful functions found in the code:

- `create_orientations_from_surface_points_coords`: a plane fit (SVD) through chosen surface points, returning an
  orientation. This is the official answer to "contacts but no dip".
- `nugget` per surface point: lets the surface pass *near* a point, not through it.
- `StackRelationType.ERODE` / `ONLAP`: a younger group cuts the older ones (channels, Rinnen) or lies onto them.

## 2. Why it matters for this project

The layer model N3 is a layer cake: one surface per Einheit over a common TIN, interpolated in 2D (IDW or thin-plate
spline), trimmed from top to bottom, exact at every contact. Its known limits are in [18 §8](18_layer_modeler.md#8-limits-and-next-steps):

- no faults, no bodies that repeat or overhang;
- uncertainty only as the distance to the nearest Bohrung;
- the extent of a lens is an indicator interpolation, not geology.

GemPy was already named for this as level **N4** in the
[architecture §7.1](ARCHITECTURE_BAUGRUNDMODELL.md#71-ladder-of-levels-each-one-is-deliverable). The use case of D99 (a
Gutachten shown and checked for plausibility) gains most from the second point: an honest statement of uncertainty.

## 3. Experiment (2026-11-10)

Data:

- four synthetic cases of the modeler (`geneigt`, `auskeilen`, `linse`, `demo`: 9 to 12 Bohrungen, 4 to 7 Einheiten);
- one real surface: the base of the Auffüllung in 36 Bohrungen within 150 m of the Hamburg Rathaus (BoreholeML WFS of
  the Geologisches Landesamt, dl-de/by-2.0).

GemPy 2026.0.3, numpy backend, default kernel (cubic, range 1.7, c_o 10).

### 3.1 Leave-one-out: predict the contact of a Bohrung from the others

Mean absolute error in metres. "Plane" is the orientation fitted through all contacts, "local" four planes fitted
through five neighbours each.

| Surface | Points | IDW | TPS | GemPy horizontal | GemPy plane | GemPy local |
|---|---|---|---|---|---|---|
| `geneigt`, base Sand (an inclined plane, 3 m relief) | 9 | 0.78 | **0.00** | 0.11 | 0.02 | 0.02 |
| `demo`, base Auffüllung (2.3 m relief) | 12 | 0.46 | 0.19 | **0.14** | 0.17 | 0.20 |
| Hamburg, base Auffüllung (real, 15.8 m relief) | 36 | **3.22** | 3.69 | 5.37 | 5.29 | 5.27 |

One call takes 25 to 60 ms.

The Hamburg surface is not one surface but two populations: 8 Bohrungen at −8 to −10 m NHN (filled water courses)
and 28 at −2 to +6 m NHN. Predicting the mean of the others gives 4.45 m. Findings on it:

- With the default nugget GemPy was **not exact at the Bohrungen themselves**: up to 13 m off. Close points with very
  different elevations make the implicit surface fold, so a vertical line crosses it more than once.
- With a nugget of 0.01 the leave-one-out error fell to 3.24 m, the level of IDW, and the deviation at the Bohrungen
  to 4.1 m. Smoothing helps the prediction but gives up the exact contacts.
- No method predicts this surface. The honest output is the uncertainty, not a better interpolator.

### 3.2 The whole layer pile

Deviation at the exact contacts of all Bohrungen, read from GemPy along each Bohrung in steps of 2 cm.

| Case | (A) all Einheiten in one group | (B) one group per Einheit, `ERODE` |
|---|---|---|
| `geneigt` (27 contacts) | median 0.04 m, max 0.68 m | max **0.02 m** |
| `auskeilen` (30; the Torf pinches out) | median 5.17 m, max **18.00 m**; order of the units wrong in 9 of 9 Bohrungen | max **0.02 m** |
| `linse` (18) | max 0.02 m | max 0.02 m |
| `demo` (37; lens, pinch-out, units below the Endteufe) | max 10.51 m; 12 units present where the Bohrung has none | max 0.02 m; **4 contacts without their unit; 6 units present where the Bohrung has none** |

Reading:

- (A) cannot work for a Baugrund: all boundaries of a group are iso-surfaces of the same field, so they never meet
  and a layer cannot reach thickness zero.
- (B) reproduces the contacts. It still needs the lens logic of N3 (the presence indicator) for Einheiten that are
  missing in some Bohrungen: the `demo` case shows it.
- Time: under 1 s for 12 Bohrungen and 7 Einheiten; meshes by dual contouring in 2.3 s.

### 3.3 GemPy on the mesh of the layer model

Evaluated at the 1,700 nodes of the `demo` TIN, in columns every 0.25 m (188,700 points, 6 fields): **7.6 s**. The base
of the Auffüllung differs from the IDW surface of N3 by 0.24 m in the median, 0.94 m at the 95th percentile and 1.34 m
at most. That difference between two defensible methods is itself a measure of how uncertain the surface is away from
the Bohrungen.

GemPy's own meshes are open surfaces, not closed solids. The IFC needs closed solids (M17), so the meshes are not
used: GemPy only supplies elevations at the nodes of the existing TIN.

## 4. The missing dip of the layers

A Bohrprofil gives contacts, not dips. GemPy needs at least one orientation per structural group, so with one group
per Einheit (§3.2) that is one orientation per Einheit. Sources, in the order they are tried:

| # | Source of the orientation | When | Evidence |
|---|---|---|---|
| 1 | **Plane through the contacts of the Einheit** (SVD, GemPy's own function) | at least 3 contacts that are not in a line | `geneigt`: leave-one-out 0.02 m against 0.11 m with a horizontal one |
| 2 | **Horizontal** (pole vector 0, 0, 1) at the centroid of the contacts | fewer than 3 contacts, contacts in a line, or a fitted dip above a limit (30° proposed) | what GemPy's borehole tutorial does; contacts still within 0.02 m (§3.2) |
| 3 | **Terrain-parallel** for the top Einheiten (Auffüllung, Mutterboden) | a DGM is loaded | the normal of the DGM at the centroid; follows 18 §3 point 6 |
| 4 | **Entered by the engineer**: Fallrichtung and Fallwinkel per Einheit | the Gutachten states it, or a Längsschnitt or a geological map shows it | manual, under *Erweitert* |

Rules:

- The orientation is a weak prior: the contacts decide the surface where there are Bohrungen, the orientation only
  where there are none. So a wrong assumption shows at the edge of the model, not at the Bohrungen.
- Bohrungen in a line (a Trasse) fix the dip along the line only. Across it the orientation stays horizontal, and the
  report says so.
- The source is recorded per Einheit (`orientierung_quelle`: Kontakte / horizontal / DGM / Eingabe) in the report and
  the IFC. An assumed value is marked, never hidden.
- The uncertainty run (§5) varies the dip, so the effect of the assumption is visible as a number.

Later sources, not in the first phases: the layer lines drawn in the Längsschnitt (N2 Geoslice, apparent dips) and
Streichen/Fallen from geological maps.

## 5. The component "Ground Analysis"

A package of its own, next to the modeler: `services/analyse` (package `baugrundanalyse`). It reads the model
(`baugrundmodell.Modell`: Einheiten, contacts, TIN) and never changes the Bohrungen.

| Function | Question it answers | Needs GemPy |
|---|---|---|
| **Kreuzprobe** (leave-one-out per Einheit and method) | How well does the model predict a Bohrung it has not seen? Which method fits this site? | no |
| **Unsicherheit** (Monte Carlo over contact depth, dip and method) | How far can each surface move? Standard deviation per node and Einheit | no (better with it) |
| **Virtuelle Bohrung** | What does the model expect at this point (a planned foundation), with which spread? | no |
| **Methodenvergleich** | Where do IDW, TPS and the implicit model disagree, and by how much (difference per node, volume per Einheit with a range)? | optional |
| **Implizites Modell** (GemPy as the third method) | Layers with a 3D structure: Rinnen (`ERODE`), onlap, later faults | yes |
| later: Grundwasserfläche, Kennwerte per Einheit (kriging) | 18 §8 point 5 | `gempy_plugins` |

Design decisions:

- **GemPy is an interpolator on the existing mesh.** The adapter turns the contacts into surface points, builds one
  group per Einheit, computes the model along a column at each TIN node and returns the same array as N3 (`flaechen`:
  surfaces × nodes). Trimming, lens extent, closed solids and the IFC writer stay as they are.
- **The invariants stay checked.** The deviation at every contact is measured after each run. Above 5 cm, the Einheit
  falls back to the thin-plate spline, with a note in the report. A surface that folds (more than one crossing in a
  column) is rejected the same way.
- **Optional dependency.** `requirements-analyse.txt` (`gempy`, pinned in `constraints.txt`); imported only when the
  method is chosen. Without it the app runs as today and the choice *implizit* is greyed out with the reason. Docker:
  a build argument `ANALYSE=1`.
- **Nothing silent.** The IFC and the report carry the method, the source of each orientation and the measured
  cross-check error (`method` already allows `gempy` in the [architecture](ARCHITECTURE_BAUGRUNDMODELL.md) data model).

### 5.1 Place in the system

```
PDF / Länder ─► Bohrungen (reviewed) ─► Einheiten ─► baugrundmodell.bauen ─► Modell ─► IFC, viewer, exports
                                             │              ▲                  │
                                             │   methode: idw | tps | implizit │
                                             │              │                  ▼
                                             └────► baugrundanalyse ◄──────────┘
                                                    Kreuzprobe · Unsicherheit · Virtuelle Bohrung · Vergleich
                                                    implizit.py (GemPy, optional)
```

| Layer | Change |
|---|---|
| `services/analyse/baugrundanalyse/` | `kreuzprobe.py`, `unsicherheit.py`, `virtuell.py`, `vergleich.py`, `orientierung.py`, `implizit.py`; tests in `services/analyse/tests` |
| `services/modeler` | `bauen(methode="implizit")` calls the adapter through a hook; no import of GemPy in the modeler itself |
| `ui/projekt.py` | settings `analyse` (method, orientation per Einheit, number of runs) through `aendern(op)`; results cached by the model signature |
| `server/` | `POST /api/analyse/kreuzprobe`, `/unsicherheit`, `/virtuell`; long runs as a job with progress, like the extraction |
| `apps/web` | step **Einheiten → Erweitert → Ground Analysis** (D99: a new function goes under *Erweitert*): method, orientation table, buttons, result table. Viewer: colour by uncertainty, difference of two methods, a click sets a virtuelle Bohrung |
| IFC | `CPset_Modell`: method, cross-check error per Einheit; per Einheit `Orientierung_Quelle`; uncertainty as a property per solid (min, mean, max standard deviation) |

## 6. Phases

| Phase | Content | Accepted when | GemPy |
|---|---|---|---|
| **G1 Kreuzprobe and Unsicherheit** (**built**, §6.1) | leave-one-out per Einheit for IDW and TPS; Monte Carlo over the contact depths (σ by contact type: exact, free, censored) and over the method; virtuelle Bohrung; result in the report | the synthetic cases give the errors of §3.1 (IDW 0.78 m, TPS 0.00 m on `geneigt`); a run on 12 Bohrungen under 10 s; tests offline | no |
| **G2 App** (**built**, §6.2) | section *Ground Analysis* under *Erweitert*, result table, viewer colour by uncertainty, virtuelle Bohrung by click; `apps/web/dist` | end-to-end check extended; nothing changes for a project that never opens the section | no |
| **G3 Implicit method** (**built**, §6.3) | `implizit.py` and `orientierung.py`; `methode="implizit"`; fallback per Einheit; optional install | contacts within 5 cm on `geneigt`, `auskeilen`, `linse`; `demo` passes with the lens indicator; folded surfaces rejected; the regression of the modeler unchanged for IDW and TPS; IFC valid, unit METRE | yes |
| **G4 Structures** | groups set by the engineer: a Rinne that erodes (`ERODE`), onlap; orientation entered per Einheit; dip in the Monte Carlo | a synthetic Rinne case that N3 cannot represent and GemPy does, with the contacts exact | yes |
| **G5 Later** | faults, Kennwerte fields, Grundwasserfläche, `gempy_probability` once it follows the engine | each justified by a real case | yes |

G1 and G2 stand on their own and give the yardstick for G3: the implicit method is kept only where the Kreuzprobe
shows it predicts better on real projects.

### 6.1 G1 as built (2026-11-10)

`python -m baugrundanalyse <extraktion.json> [...] [--einheiten e.json] [--methode idw|tps] [--laeufe n] [--punkt x y]
[--bericht analyse.json]`, with `services/modeler` on the search path. Tests: `cd services/analyse && python -m pytest
tests` (15, offline; part of `python -m agenten pruefen` and of the CI).

**Kreuzprobe** (`kreuzprobe.py`). For each Bohrung the layer model is computed without it, with the same Einheiten,
contacts and rules (free boundaries, censoring, trimming, extent), and read at its position. Compared are measured
values only:

- exact bases: error per Einheit, per Bohrung and overall, for IDW and for the spline;
- presence: how often an Einheit is predicted present or missing against the Bohrung;
- Bohrungen that end inside an Einheit: whether the predicted base stays below the Endteufe;
- the GOK, when no DGM is used.

It needs three Bohrungen. Hints it gives: the other method predicts at least 20 % better; an Einheit is predicted
wrongly present or missing; **Bohrungen their neighbours do not let expect**. For the last one, each of the three
Bohrungen with the largest error is tested on its own: it is flagged when its error is above 0.5 m and above three
times the median error of the others, computed *without* it. A wrong Bohrung also spoils the prediction of its
neighbours, so comparing against the errors with it would hide it. The hint asks (*Linse, Rinne oder Fehler in Tiefen
oder Lage?*): the cross-check cannot tell geology from a data error.

**Unsicherheit** (`unsicherheit.py`). Two parts per node and Einheit, σ² = σ²(Messung) + σ²(Abstand):

- *Messung*: Monte Carlo. Every exact boundary is shifted by a normal distribution (0.10 m by default; the order of
  the boundaries in a Bohrung is kept) and the layer model is computed again. At the Bohrungen only this part is left.
- *Abstand*: the errors e of the Kreuzprobe at the distance d to the nearest Bohrung that reaches the base give
  c = median(e²/d) / 0.455 (a linear variogram; the median, so that one Bohrung does not decide everything), and
  σ² = c · d at a node. With fewer than five errors for an Einheit, the value of all Einheiten together is used.

This changes the plan in one point: a Monte Carlo over the contact depths alone gave about 0.06 m everywhere, also far
from any Bohrung, which would have looked exact and been wrong. The distance part comes from the measured prediction
error of the same model. Also reported: the volume per Einheit with its 5 % and 95 % values (measurement part only)
and the difference to the other interpolation method. An Einheit whose base no Bohrung reaches gets no number. The
assumptions are part of the result.

**Virtuelle Bohrung** (`virtuell.py`). The model read at a point (linear in the triangle of the mesh, so with the
DGM top, the trimming and the limited extent of lenses): Einheiten with depths, thickness, σ of the base and its
95 % range, the nearest Bohrung and its distance. Outside the model it refuses. It is marked as *Modell, keine Messung*.

Measured:

| Case | Bohrungen | Kreuzprobe IDW / TPS (mean error) | Time: Kreuzprobe, Unsicherheit (100 runs) |
|---|---|---|---|
| `geneigt` | 9 | 0.66 m / 0.00 m (Sand: 0.78 m / 0.00 m, as in §3.1) | 0.01 s, 0.5 s |
| `demo` | 12 | 0.51 m / 0.24 m | 0.06 s, 1.0 s |
| `trasse` (5 km) | 51 | 0.38 m / 0.08 m | 0.7 s, 11 s |
| Hamburg Rathaus (real, 38 Bohrungen, 26 Einheiten) | 38 | 3.24 m / 3.70 m | 2.4 s, 4.2 s (50 runs) |

- A Bohrung of `geneigt` with all boundaries 3 m too deep is found with the spline (its error 3.00 m, the others
  0.00 m without it). With IDW it is not: IDW itself is 0.6 to 1.6 m off on inclined layers.
- Hamburg: the Kreuzprobe names one Bohrung 76 m beside the prediction of its neighbours, and reports 188 wrong
  predictions of presence in 26 Einheiten. That is the honest picture of an automatic correlation on inner-city fill.
- A mutation probe of the three modules: the tests reject 55 of 66 simple operator changes; the rest are limits at
  exactly a threshold.

### 6.2 G2 as built (2026-11-10)

- **Server** (`server/arbeitsplatz.py`): `analyse(sig, laeufe)` and `virtuelle_bohrung(sig, x, y)`.
  - Both use the model already computed for the step (the same key as the IFC), and keep the analysis per model key
    (six models).
  - Routes: `POST /api/projekt/{sig}/analyse` and `/analyse/punkt`.
  - Nothing in the project is changed. Under three Bohrungen, or without a model, the answer is a `fehler` text.
- **App** (`apps/web/src/app/analyse.ts`): a folded section *Ground Analysis* at the end of the Einheiten step. It is
  computed only on a click (*Analyse rechnen*: 100 runs) and shows:
  - the Kreuzprobe per method;
  - the hints;
  - per Einheit: the cross-check error, σ of the base (mean and 95 %), the presence errors, the volume with its
    5–95 % range and the difference to the other interpolation;
  - a virtuelle Bohrung at a Rechtswert/Hochwert, prefilled with the centre of the model.

  When the model changes, the section says so instead of showing old numbers.
- **Tests**: `tests/test_analyse_app.py` (the demo project: Kreuzprobe, Unsicherheit and the virtuelle Bohrung through
  the API; the project unchanged; refused without a model). The end-to-end check of the app has one more check:
  55 instead of 54.
- **Not yet**: colour by σ in the viewer, and a click in the viewer that sets the virtuelle Bohrung. Both need σ per
  node in the IFC or a second channel to the viewer.

### 6.3 G3 as built (2026-11-11)

**Design.** GemPy is a third interpolator of the layer model. It is not a separate model.

- The modeler has a registry, `flaechen.ERWEITERUNGEN`, and never imports GemPy.
  [`baugrundanalyse/implizit.py`](../services/analyse/baugrundanalyse/implizit.py) registers `"implizit"` when GemPy
  is installed.
- Each surface (GOK without a DGM, then each base) gets its own scalar field: one group with one element, so every
  Einheit can pinch out (§3.2).
- The field is read in vertical columns at the nodes of the TIN. The crossing is found in three passes, 24, 12 and
  12 steps: at most 3.5 cm from 48/16/16, in half the time.
- Everything else stays the layer model: free boundaries, censoring, trimming, extent of lenses, closed solids, IFC.

**Orientation** (D106, `orientierung()`):

- 3 or more contacts not in a line: the plane through them.
- Contacts in a line (a Trasse): the dip along the line, horizontal across it.
- Steeper than 30°, or fewer than 3 contacts: horizontal.

The report carries the source, the dip and the dip direction per Einheit (`parameter.orientierung`). The IFC names
the method.

**Checks per surface:**

- exactly one crossing per column, and at most 5 cm off at the data;
- otherwise that surface is computed by the thin-plate spline, with a hint naming why (folded, or off at the
  Bohrungen);
- the data values are set exactly afterwards.

**Ground Analysis:**

- The Kreuzprobe adds the method of the model, so for an implicit model it compares IDW, TPS and implizit.
- The Monte Carlo of the Unsicherheit uses the spline as a stand-in: 100 runs with GemPy take minutes. This is stated
  in the assumptions.

**Optional install:**

- `requirements-analyse.txt` (`gempy`, `gempy_engine`, `python-dotenv`, pinned in `constraints.txt`);
- Docker `--build-arg ANALYSE=1`;
- a CI job of its own (*Ground Analysis mit GemPy*).

Without GemPy, the choice *Implizit (GemPy)* in *Einheiten → Erweitert* is greyed out with the reason, and a project
set to it says so instead of computing.

**Measured** (mean / maximum error of the Kreuzprobe in m; model and Kreuzprobe times with GemPy):

| Case | IDW | TPS | implizit | Model, Kreuzprobe |
|---|---|---|---|---|
| `geneigt` | 0.66 / 1.21 | 0.00 / 0.00 | 0.00 / 0.01 | 6 s, 6 s |
| `auskeilen` | 0.69 / 1.57 | 0.22 / 1.24 | 0.22 / 1.19 | 8 s, 26 s |
| `linse` | 0.42 / 2.25 | 0.15 / 2.25 | 0.15 / 2.24 | 6 s, 12 s |
| `demo` | 0.51 / 1.95 | 0.24 / 1.84 | 0.24 / 1.70 | 12 s, 39 s |

All four: contacts exact (0.000 m), all solids closed, the IFC valid in METRE (test).

**Reading.** On layer-cake data the implicit method equals the spline: the same mean error, a slightly smaller
maximum. It costs 10 to 100 times the time. It earns its place only where the spline cannot follow the geometry:
structures of G4 (an eroding Rinne, onlap). So it stays optional and is never the default (D105). Which method fits a
site is the job of the Kreuzprobe.

## 7. Risks

| Risk | Answer |
|---|---|
| GemPy is not exact at noisy data, and its surfaces can fold (§3.1) | check after every run; fallback per Einheit; never the default method |
| A layer cake forced into one group gives wrong models that look plausible (§3.2) | the adapter always builds one group per Einheit unless the engineer groups them |
| An assumed dip is taken for a measured one | source per Einheit in the UI, the report and the IFC; dip varied in the uncertainty run |
| A new heavy dependency | optional; core install is `gempy`, `gempy_engine`, numpy, pydantic; no PyTorch, no viewer |
| The uncertainty looks more exact than it is | it is a spread under stated assumptions (σ per contact type, methods compared), shown with those assumptions; with one or two Bohrungen no Kreuzprobe is given |
| API changes (GemPy v3 is recent; versions by date) | pinned version; the adapter is the only file that imports it; its tests run only when GemPy is installed |

## 8. Licence

GemPy and `gempy_engine` are under the EUPL-1.2 (package metadata and `LICENSE`). The appendix of the EUPL lists the
GNU AGPL v3 among the compatible licences of Article 5. The project uses GemPy as an optional dependency and copies
no code, so a line in `THIRD_PARTY_LICENSES.md` is all that is needed when G3 is built.

## 9. Sources (read 2026-11-10)

- [gempy-project/gempy](https://github.com/gempy-project/gempy), commit `8283735`:
  - `gempy/API/initialization_API.py` (`structural_elements_from_borehole_set`);
  - `gempy/modules/data_manipulation/orientations_from_surface_points.py`;
  - `examples/examples/real/_hidden/mik.py` (boreholes with one horizontal orientation);
  - `WhatsNewGemPy3.md`, `LICENSE`.
- PyPI: `gempy` 2026.0.3, `gempy_engine` 2026.0.3.post1, `gempy_viewer` 2026.0.5, `gempy_plugins` 2026.0.3,
  `gempy_probability` 2024.1.1, `subsurface` 2024.2.2.
- Experiment of this note: run in the session of 2026-11-10 with the modeler of this repository; the cases become
  the tests of G1 and G3.

Up: [Index](README.md)

Related: [18 Layer modeler](18_layer_modeler.md) · [Architecture §7](ARCHITECTURE_BAUGRUNDMODELL.md#7-baugrundmodell-generating-the-geometry) · [21 Step app](21_app_schritte_normen.md) · [14 Licensing](14_licensing.md) · [11 Decisions](11_decisions.md)
