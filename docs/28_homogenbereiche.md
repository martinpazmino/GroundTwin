---
title: "28 Homogenbereiche (VOB/C): Einheiten per Gewerk, Kennwerte, IFC"
date: 2026-11-11
tags: [homogenbereiche, vob-c, din-18300, ifc, model, norms]
aliases: [Homogenbereiche, VOB/C, Kennwerte matrix]
status: built
---

# 28 Homogenbereiche (VOB/C): Einheiten per Gewerk, Kennwerte, IFC

The layer model ([18](18_layer_modeler.md)) builds geological **Einheiten**. A tender under VOB/C does not ask for
Einheiten but for **Homogenbereiche**: ground that behaves alike *for one Gewerk*, with the Kennwerte its ATV asks for
(DIN 18300 Erdarbeiten, DIN 18301 Bohrarbeiten …). The same Schicht can belong to one Homogenbereich for Erdarbeiten
and to another for Bohrarbeiten. This note describes the second way to build the IFC: from Homogenbereiche.

> [!NOTE]
> - The planner assigns the Einheiten to Homogenbereiche, per ATV (step *Einheiten*, folded section
>   *Homogenbereiche (VOB/C)*). For each ATV a proposal with reasons merges Einheiten that behave alike for that
>   Gewerk (§5); it is applied only on a click.
> - What the layer descriptions say about the asked Kennwerte is shown per Bereich and written to the IFC; laboratory
>   values stay open (§6).
> - The IFC carries the assignment as Pset `CPset_Homogenbereich_<ATV>` on every Einheit and on every Bodenschicht of
>   the Bohrsäulen.
> - On request the model consists of the Homogenbereiche only: the same closed bodies, grouped per Bereich.
> - The Kennwerte each ATV asks for come from the matrix the user supplied (Abbildung 8, §2). It was read cell by cell
>   and must be checked against the edition of the ATV in force.

## 1. What a Homogenbereich is here

- Per ATV (Gewerk) a mapping `Einheit → Bereich` (name up to 40 characters, e.g. `B1`). Equal names form one Bereich;
  an empty field means no Bereich.
- Several ATV can be filled at the same time (`{ATV: {Einheit: Bereich}}`, project field `homogenbereiche`).
- A Bereich does not have to be contiguous: Sand above and below a Kies lens can be one Bereich.
- The Kennwerte themselves (values) are in the Gutachten. The model says *which* Kennwerte the ATV asks for per
  Bereich; reading the values from the text of the Gutachten is a later step ([Architecture](ARCHITECTURE_BAUGRUNDMODELL.md),
  open item *Kennwerte/Homogenbereiche tables*).

## 2. The matrix of the Kennwerte per ATV

Source: Abbildung 8 *Matrix mit den erforderlichen Kennwerten zur Baugrundbeschreibung für die jeweiligen ATV der VOB
Teil C für „Boden“* (chapter 6 *Beschreibung von Homogenbereichen in der VOB/C*, p. 29 of a publication), given by the
user on 2026-11-11 as an image. Stored in
[`services/modeler/baugrundmodell/homogenbereiche.json`](../services/modeler/baugrundmodell/homogenbereiche.json).

**How it was read**: the median grey value of each cell (23 rows × 11 columns): about 211 = required (grey), about 169
= *ergänzend für Vortriebe mit Schildmaschinen* (dark grey, DIN 18312 only), about 235 = a lighter grey without a
legend entry (DIN 18312 and DIN 18313, row 5 Dichte: stored as required, marked *prüfen*), 255 = not required. The cell
DIN 18320 / Bodengruppe holds the text *DIN 18915* (Landschaftsbau: Bodengruppen after DIN 18915 instead of DIN 18196).

**Check**: the column DIN 18300 gives 13 Kennwerte, the list of the ATV DIN 18300 for Boden (ortsübliche Bezeichnung,
Korngrößenverteilung, Massenanteile Steine/Blöcke/große Blöcke, Dichte, undrainierte Scherfestigkeit, Wassergehalt,
Plastizitätszahl, Konsistenzzahl, Lagerungsdichte, organischer Anteil, Bodengruppe).

| ATV | Gewerk | Kennwerte (rows) |
|---|---|---|
| DIN 18300 | Erdarbeiten | 1, 2, 3a–c, 5, 7, 9, 10b, 11b, 13, 16, 19 |
| DIN 18300 GK 1 | Erdarbeiten, GK 1 (DIN 4020) | 3a–c, 10a, 11a, 13, 19 |
| DIN 18301 | Bohrarbeiten | 1, 2, 3a–c, 6, 7, 9, 10b, 11b, 13, 18, 19 |
| DIN 18304 | Ramm-, Rüttel- und Pressarbeiten | 1, 2, 3a–c, 9, 10b, 11b, 13, 19 |
| DIN 18311 | Nassbaggerarbeiten | 1, 2, 3a–c, 7, 9, 11a, 13, 14, 16, 17, 19 |
| DIN 18312 | Untertagebauarbeiten | 1, 2, 3a–c, 5 (prüfen), 7, 9, 10b, 11b, 13, 18, 19; Schild: 4, 6, 8, 16 |
| DIN 18313 | Schlitzwandarbeiten | 1, 2, 3a–c, 5 (prüfen), 7, 9, 10b, 11b, 13, 14, 16, 19 |
| DIN 18319 | Rohrvortriebsarbeiten | 1, 2, 3a–c, 4, 5, 7, 8, 9, 10b, 11b, 12, 13, 16, 17, 18, 19 |
| DIN 18320 | Landschaftsbauarbeiten | 3a–c, 19 (DIN 18915) |
| DIN 18321 | Düsenstrahlarbeiten | 1, 2, 3a–c, 7, 9, 10b, 11b, 13, 16, 19 |
| DIN 18324 | Horizontalspülbohrarbeiten | 1, 2, 3a–c, 4, 5, 7, 9, 10b, 11b, 12, 13, 14, 15, 16, 17, 18, 19 |

Rows: 1 ortsübliche Bezeichnung · 2 Korngrößenverteilung · 3a/3b/3c Massenanteil an Steinen > 63–200 / > 200–630 /
> 630 mm · 4 mineralogische Zusammensetzung der Steine und Blöcke · 5 Dichte · 6 Kohäsion · 7 undrainierte
Scherfestigkeit · 8 Sensitivität · 9 Wassergehalt · 10a Plastizität · 10b Plastizitätszahl · 11a Konsistenz ·
11b Konsistenzzahl · 12 Durchlässigkeit · 13 Lagerungsdichte · 14 Kalkgehalt · 15 Sulfatgehalt · 16 organischer Anteil ·
17 Benennung und Beschreibung organischer Böden · 18 Abrasivität · 19 Bodengruppe.

## 3. In the IFC

Module [`baugrundmodell/homogenbereiche.py`](../services/modeler/baugrundmodell/homogenbereiche.py), used by
`ifc_schreiben(..., homogenbereiche=, nur_homogenbereiche=)`.

**Model of Einheiten (default)**: every `IfcGeotechnicalStratum` of the model and of the Bohrsäulen gets, per ATV with
an assignment, a Pset `CPset_Homogenbereich_<ATV>` (e.g. `CPset_Homogenbereich_DIN18300`): `ATV`, `Gewerk`,
`Homogenbereich` (or *nicht zugeordnet*), `Einheiten_im_Bereich`, `Kennwerte_erforderlich`, `Quelle_Kennwerte`.

A Bodenschicht of a Bohrung is assigned by **height**, not by its Abschnitt: at each Bohrung the Schicht goes to the
Einheiten whose model interval overlaps it by more than 1 cm. A Schicht can lie in two Einheiten (Sand above and below a
Kies lens that this Bohrung does not show). Then the Pset names both Bereiche (`B2 / B3`) with a `Hinweis`; nothing is
cut or hidden.

**Model of Homogenbereiche** (`nur_homogenbereiche=<ATV>`, in the app *IFC-Modell: Homogenbereiche <ATV>*):

- the `IfcGeomodel` is called *Homogenbereiche <ATV> (<Gewerk>)*; one `IfcGeotechnicalStratum` per Bereich, whose
  representation holds the closed `IfcTriangulatedFaceSet` of each of its Einheiten (same geometry, grouped);
- main Pset `CPset_Homogenbereich_<ATV>` with the volume, Bodenarten, Benennungen, colour and order; `CPset_Modelleinheiten`
  lists the Einheiten; the Pset of another ATV is kept only where all Einheiten of the Bereich share one Bereich there;
- an Einheit without a Bereich stays a stratum of its own, named *… (ohne Homogenbereich)*, and the model hints list it;
- `CPset_Baugrundmodell` says `Modellart` and `Homogenbereiche_ATV`.

Checked: IFC without validation errors, unit METRE, all bodies closed, volume of a Bereich = sum of its Einheiten.

## 4. In the app

- Step *Einheiten*, folded section **Homogenbereiche (VOB/C)** (open when it holds data): choose the ATV; one field per
  Einheit; *Vorschlag: je Einheit ein Bereich* (B1, B2, … from the top); *Zuordnung löschen*. Below: the Bereiche with
  their Einheiten, Einheiten without a Bereich, names that are no longer in the model, and the Kennwerte of the ATV
  with the source of the matrix.
- *IFC-Modell*: Einheiten, or Homogenbereiche of one ATV with an assignment. The geometry is not recomputed; only the IFC
  is written anew (its file name includes the assignment).
- The viewer lists the Bereiche (*Homogenbereiche (n)*) with their volume.
- Project ops: `{"op": "homogenbereiche", "atv", "zuordnung"}` (null removes the ATV), `{"op": "hb_modell", "wert"}`
  (refused without an assignment for that ATV; reset when the assignment is removed). `GET /api/homogenbereiche`
  returns the matrix with its source.
- Tests: `services/modeler/tests/test_homogenbereiche.py`, `tests/test_homogenbereiche_app.py`.

## 5. Proposal per Anwendungsfall (2026-11-11)

When the chosen ATV has no assignment yet, the section shows a **proposal for that ATV**, with a reason per Bereich; it
is applied only with *Vorschlag übernehmen* (or the link *Vorschlag für <ATV>*) and can then be changed per Einheit.
`GET /api/projekt/{sig}/homogenbereiche/vorschlag?atv=…` (`hb.vorschlag_fuer`) changes nothing.

Rule (general, from the data, not one per ATV):

1. **Verhalten** of each Einheit from its Bodenarten (`normen.json`, field `art`): nichtbindig (Kies, Sand, Steine,
   Blöcke), bindig (Schluff, Ton and the geological fine-grained soils such as Geschiebemergel, Löß, Lehm, Klei),
   organisch, anthropogen (Auffüllung), befestigt (Beton, Asphalt, Schwarzdecke, Pflaster: bound layers, never merged
   with fill), Fels (also `Fels (Tonstein)`). An Einheit with mixed or unknown Bodenarten stays a Bereich of its own.
2. **How fine** follows from the Kennwerte the ATV asks for (matrix §2):
   - at most 7 Kennwerte (DIN 18300 GK 1, DIN 18320): *grob*, only the Verhalten;
   - Mineralogie or Abrasivität asked (rows 4 or 18: DIN 18301, 18312, 18319, 18324): *fein*, also the Bodengruppe
     (else Hauptbodenart) and Steine/Blöcke (in at least half of the Schichten) apart;
   - otherwise *standard*: also the Bodengruppe DIN 18196, the one named most often in the descriptions of the Einheit
     (`normen.deuten`) if at least half of its Schichten name it, else the Hauptbodenart.
   Anthropogen, befestigt, organisch and Fels are grouped by Verhalten at every level.
3. Einheiten with the same key form one Bereich; names B1, B2, … in the order of the uppermost Einheit.

On the demo: DIN 18300 → Sand 1 + Sand 2 together, Kies apart; DIN 18300 GK 1 and DIN 18320 → Sand 1 + Kies + Sand 2
and Geschiebemergel + Ton together. Tests: `test_vorschlag_je_anwendungsfall` in both test files.

Limits: the proposal knows only what the Gutachten descriptions say (Bodenart, Bodengruppe, Steine). Kennwerte values,
Konsistenz, Lagerungsdichte or the Gutachter's own Homogenbereiche are not used; the planner decides.

## 6. Kennwerte from the descriptions (2026-11-11)

The extraction reads the Bohrprofile, not the Kennwerte tables of the Gutachten text. What the layer descriptions say
is still used, per Homogenbereich (without an assignment: per Einheit), `hb.kennwerte_bereich`:

| Kennwert | From the description | Kind |
|---|---|---|
| 1 ortsübliche Bezeichnung | Benennung after the norm (`normen.deuten`) | Ansprache |
| 3a, 3b Steine, Blöcke | "steinig", "Blöcke" named | named only, no Massenanteil |
| 10a Plastizität | from the Bodengruppe (TL/UL leicht, TM/UM mittel, TA/UA ausgeprägt) | derived |
| 11a Konsistenz | weich, steif … | Ansprache |
| 13 Lagerungsdichte | locker, mitteldicht … | Ansprache |
| 14 Kalkgehalt | kalkfrei … | Ansprache |
| 16 organischer Anteil | humos, organisch, torfig named | named only, no Glühverlust |
| 17 organische Böden | Benennung of Torf, Mudde, Mutterboden | Ansprache |
| 19 Bodengruppe | DIN 18196 where named | as written |

Each entry carries the share of the Schichten that name it (`steif (5/8), weich (1/8)`). Everything else (2
Korngrößenverteilung, 3c, 4, 5 Dichte, 6, 7 undrainierte Scherfestigkeit, 8, 9 Wassergehalt, 10b, 11b, 12, 15, 18) is a
laboratory or table value and stays **offen**; nothing is estimated.

- App: under the Kennwerte of the ATV, *Aus den Beschreibungen*: per Bereich how many of the asked Kennwerte are
  addressed, and the table. `GET /api/projekt/{sig}/homogenbereiche/kennwerte?atv=…`.
- IFC: in `CPset_Homogenbereich_<ATV>` one property `Kennwert_<nr>_<name>` per addressed Kennwert, `Kennwerte_offen`
  and `Kennwerte_Herkunft`.
- **Measured on the real examples** (DIN 18300, 13 Kennwerte): Talheim, whose descriptions follow the norm (34 of 65
  Schichten with Konsistenz, 8 with Bodengruppe): up to 4 of 13 per Einheit. Berlin V-67b (short field descriptions):
  1 or 2 of 13. The descriptions cover the Ansprache, never the numbers a tender needs; those need the text of the
  Gutachten.

## 7. The real examples through Ground Analysis and Homogenbereiche (2026-11-11, not blind)

The two real examples in `data/beispiele` are training data (their PDFs were open during development), so this is a
run on real data, not a blind test.

| | Berlin V-67b (5 Bohrungen in the model, georeferenced) | Talheim (8 Bohrungen, Reihe) |
|---|---|---|
| Kreuzprobe, mean error | IDW 0.78 m, spline 0.80 m (10 contacts) | 5.99 m (19 contacts) |
| Flagged Bohrungen | 422C-461 (2.3 m) and 422C-460 (1.6 m) against 0.2 m for the others | none |
| σ of the bases | 0.5–0.9 m (95 %) | 5–10 m |
| Grundwasser | 2 levels, 32.45–32.65 m NHN | 3 levels, surface above the terrain at half of the nodes |
| Proposal DIN 18300 | Sand 1–3 → B1, Kies 1–2 → B2, Auffüllung → B3 | Mutterboden, Schwarzdecke, Auffüllung, Schluff, Tonstein each apart |

- **Berlin** behaves as on synthetic data. Two Bohrungen are flagged as not expected from their neighbours; the hint
  asks to check their depths and Lage. Why they differ was not examined.
- **Talheim** has no coordinates: the Bohrungen stand in a row with assumed spacing on sloping ground. The numbers are
  not a property of the ground. The analysis now says so (*schematische Lage … nur zur Anschauung*); before, it gave
  them without a warning.
- The run found two faults in the proposal, fixed: `Fels (Tonstein)` counted as unknown, and Schwarzdecke was merged
  with Auffüllung. A Bodengruppe named in 1 of 9 Schichten no longer decides the Bereich.

## 8. The other tables (DIN 4023 Tabelle 2 and 3)

The user also gave DIN 4023 *Tabelle 2* (Kurzformen, Zeichen und Farben für Felsarten nach DIN EN ISO 14689) and
*Tabelle 3* (… für gebräuchliche, geologische Benennungen von Boden und Fels). They correct colours in
[`normen.json`](../services/modeler/baugrundmodell/normen.json) that were so far only a display choice (`beleg:
darstellung`):

| Entry | Before | Now (table) |
|---|---|---|
| Schluffstein (Ust) | dunkeloliv | oliv (Tab. 2) |
| Tonstein (Tst) | dunkelviolett | violett (Tab. 2) |
| Mergelstein (Mst) | graugrün | violettblau (Tab. 2) |
| Kalkstein (Kst) | blau | dunkelblau (Tab. 2) |
| Geschiebemergel (Mg) | graugrün | violettblau (Tab. 3) |
| Geschiebelehm (Lg) | gelbgrün | grau (Tab. 3) |
| Löß (Lö), Lößlehm (Löl) | hellocker, ocker | oliv (Tab. 3) |
| Lehm (L, Verwitterungs-/Hanglehm) | gelbbraun | grau (Tab. 3) |
| Klei (Kl) | dunkelviolett | lila (Tab. 3) |

Sandstein, Konglomerat, Brekzie, Mutterboden and Mudde were confirmed. The colour names come from the tables; the hex
values are a display of those names. Tabelle 3 is kept as a reference (`geologische_benennungen`) with the model
class of each Benennung. The five that had no class were added and are recognised in descriptions: Hangschutt (Lx),
Wiesenkalk with Seekalk, Seekreide and Kalkmudde (Wk), Bänderton (Bt) as geological classes; Kreidestein (Krst) and
Kalktuff (Kltf) as Felsarten. Anthropogene Böden (A) have no colour in the table; Auffüllung stays
grey (display).

---

## 9. Kennwerte from the report tables (Issue #18, 2026-11-19, training PDFs, not blind)

§6 reads only what the layer descriptions say. Many Gutachten also give a table of soil parameters (Bodenkennwerte):
Wichte, Wichte unter Auftrieb, Reibungswinkel, Kohäsion, undränierte Kohäsion, Steifemodul. A separate extraction
stage reads them; `prototyp_v4.py` is untouched.

**Extraction** (`services/extractor/kennwerte.py`, called by `ui/pipeline.py`, result in `kennwerte` of the document).
Two general forms, recognised by where the words are on the page:

- **Table with columns.** Header cells name a parameter (by word or symbol: γ, γ′, φ′, c′, cu, Es). They may be split
  over two lines ("Reibungs-" / "winkel") or turned upright. Three or more of them must stand side by side.
- **Value rows.** Numbers in the columns at about the same height form a row; a big jump ends the table.
- **Row label.** The text left of the first parameter column, assigned to the nearest value row. A label spanning two
  rows (steif / halbfest) goes to both; one spanning three or more is a note and is left out. Words inside the value
  columns ("Material") count as label, not as value.
- **Unit.** The unit word in the header nearest to the centre of the column.
- **List per Schicht.** One parameter per row with its value to the right, grouped under the nearest heading above
  ("Schicht 2 – Auffüllung", "Homogenbereich B3").
- **Values.** Ranges `11 - 20`, a thousands point `10.000`, a decimal comma. The Steifemodul is kept in MN/m²
  (kN/m² ÷ 1000). A value outside the usual range gets a hint (⚑, marked, kept). What is not a number (`18√t`) stays
  text. Bodengruppen (DIN 18196) and a name in brackets are taken from the label.
- **Limits.** Scanned report pages are read by OCR since 2026-11-19 (§10b). Laboratory tables (grain size,
  water content, Atterberg limits) are not read yet.

**Assignment to the Einheiten** (`services/modeler/baugrundmodell/bodenkennwerte.py`). The proposal gives each Einheit
the row whose label holds its full name (3), its name or Bodenart as a noun (2: "Sand, kiesig" names Sand, not Kies),
or its most frequent Bodengruppe (1). When rows score the same, there is no proposal: the Einheit is marked and chosen
by hand. Nothing is taken over without a click. Project op `bodenkennwerte` ({Einheit: `Datei#Index`}); unknown
references are dropped. App: step Einheiten, folded section *Bodenkennwerte aus dem Gutachten*; API
`GET /api/projekt/{sig}/bodenkennwerte`.

**IFC.** `CPset_Bodenkennwerte_Gutachten` on the Einheit, with:

- `<Kennwert>_min` / `_max` (the DAUB Teil 3 naming of [30 §6.1](30_groundtwin_analysis_research.md));
- `<Kennwert>_Text` where no number was readable;
- `Quelle` (file, page), `Bezeichnung_im_Gutachten`, `Zuordnung` and `Art`.

GroundTwin never writes `_char`: the characteristic value is the Gutachter's ([29](29_groundtwin_analysis.md)).

**Measured on the training PDFs (rows read / rows in the report):**

| PDF | Result |
|---|---|
| Halle | 4/4 table, labels with Bodengruppen and name (Auffüllung, Auelehm, Niederterrasse, Felszersatz). Wichte unter Auftrieb 1–12 kN/m³ is marked as outside the usual range; this is what the report says. |
| Berlin | 6/6 table; the labels are depth ranges (m NHN); Es = 18√t stays text. |
| Talheim | 5/5 table. Verwitterungslehm steif / halbfest are two rows with one label. |
| Rednitzhembach | 4/4 table with the Material column as label. |
| Hausham | 2/2 lists (Schicht 2, Schicht 3). |
| Triefenstein | 1/1 Homogenbereich list (B3) with cu. |
| Wachenroth (scanned, OCR, §10b) | 3/3 rows of Tabelle 9 (Oberboden, Sand schluffig, Sandstein), marked as OCR. |
| Marl, Wesel, A7367 | no Kennwert table; nothing read, nothing invented. |

**Height ranges** (2026-11-19).

- A label like `GOK bis +32,0` or `+32,0 bis +30,0` (numbers with a sign, on a page that speaks of m NHN) gives
  `hoehe_oben` / `hoehe_unten`. Depths without a sign (`0,2-1,8`) are not read as heights.
- The proposal then compares the Einheiten by position: per Einheit, the share of its thickness at the Bohrungen
  (model top/base from the report, clipped at the Endteufe; relative heights do not count) that lies in the row's
  range.
- From half on, this counts like a name (2 + share; a full name stays ahead). When the two largest shares are
  within 20 points, there is no proposal: the Einheit is marked "liegt in zwei Höhenbereichen".

Proposal on the examples:

- Talheim: Schluff → *Fließerden: Schluff, tonig …*. Fels (Tonstein) has two equal rows, so it is chosen by hand.
- Berlin, by height:

  | Einheit | Row | Share |
  |---|---|---|
  | Auffuellung | `GOK bis +32,0` | 100 % |
  | Sand 1 | `GOK bis +32,0` | 94 % |
  | Kies 1 | `+32,0 bis +30,0` | 97 % |
  | Sand 2 | `+30,0 bis +21,0` | 61 % |
  | Kies 2 | `+30,0 bis +21,0` | 100 % |
  | Sand 3 | none: 51 % / 49 % between two rows, chosen by hand | |

**Open:**

- read the Homogenbereich tables (Bereich ↔ Bodengruppen) for #21 — done, §10;
- laboratory tables;
- a blind test before any figure is quoted.

## 9b. Laboratory sheets of the annexes (Issue #18, 2026-11-19, training PDFs, not blind)

The annexes of many Gutachten carry the laboratory sheets: Wassergehalt, Zustandsgrenzen, Korngrößenverteilung,
Glühverlust, CBR, Proctor and so on. A separate stage reads them; `prototyp_v4.py` is untouched.

**Extraction** (`services/extractor/labor.py`, `labor` of the document). The rules are general rules of the forms:

- **Sample.** A Bohrung code with a depth range (`Entnahmestelle: BS 5` / `Tiefe: 2,5 - 3,5`, `BK2 (5,0-6,0m)`).
  `BS 1 + 2` is a Mischprobe and is marked.
- **Test.** Recognised from the norm or the title: 17892-1, -4, -11, -12, 18127, 18128, 18129, CBR.
- **Value.**
  - An explicit result `Name = Zahl` comes before `Name | Einheit | Zahl`.
  - A chart axis (`Wassergehalt w [%] | 24.0`) is not a result.
  - On a table with several samples, or a sheet without `=` (Glühverlust), the result is the last number of the
    sample's row (forms put the result in the last column).
  - `T/U/S/G [%]: 13.1/16.9/69.8/0.3`; a `-` means the fraction is not given.
  - A kf from the grain size curve (Beyer) is read but marked "aus der Kornverteilung, nicht gemessen".
- **Merging.** The same sample on several sheets is merged.
- **Checks.** Values outside the possible range and IP ≠ wL − wP are marked.
- **Not read.** Chemical analyses (Prüfbericht, Eluat, PAK …) are not soil mechanics and stay out.

**Model** (`baugrundmodell/labor.py`):

- Each sample hangs on the Schicht of its Bohrung with the largest overlap of its depth range. A sample across a
  boundary is marked; a Mischprobe hangs at each of its Bohrungen.
- Per Einheit or Bereich: n, min, max and mean per value. These are measured values, never characteristic ones.
- They fill the Kennwerte of the ATV before the Ansprache, marked `Labor:`:

  | Kennwert | From |
  |---|---|
  | 2 | T/U/S/G |
  | 5 | Trockendichte |
  | 9 | Wassergehalt |
  | 10b | Plastizitätszahl |
  | 11b | Konsistenzzahl |
  | 12 | kf |
  | 14 | Kalkgehalt |
  | 16 | Glühverlust |

- IFC: `CPset_Laborwerte` on the Einheit with `<Wert>_min/_max/_mean/_n` (DAUB naming).
- App: in the section *Bodenkennwerte aus dem Gutachten*, the values per Einheit; samples on no Schicht of the model
  are listed.

**Measured on the training PDFs:**

| PDF | Sheets → samples | What was read |
|---|---|---|
| Marl | 14 → 11 | Wassergehalt table 5, Zustandsgrenzen 3, Korngröße 5 (two Mischproben, one with kf after Beyer), Glühverlust 1; every value checked against the sheet |
| Talheim | 5 CBR | Trockendichte, Wassergehalt, CBR |
| Wachenroth, Triefenstein | — | chemical analyses only, rightly not read |
| other PDFs | — | no laboratory sheets |

Talheim end to end: four samples in Fels (Tonstein), one in Schluff. Kennwert 9 of DIN 18300 for the Tonstein
becomes "Labor: 11,1–16,9 % (n = 4, Mittel 14,4)".

## 10. The Gutachter's own Homogenbereiche (Issue #21, 2026-11-19, training PDFs, not blind)

Many Gutachten already define Homogenbereiche. The proposal now starts from them and shows where the model and the
Gutachten differ.

**Extraction** (`services/extractor/homogenbereiche_text.py`, separate stage, `homogenbereiche_gutachten` of the
document). Three general forms:

- **Table:** a cell `Homogenbereich X` with the Bodengruppen and a name in brackets to its left, read word by word.
  The row band runs to the middle of the neighbouring headers.
- **Section:** a heading `Homogenbereich X – Name`, then `Bodengruppen nach DIN 18196: …` and
  `Ortsübliche Bezeichnung: …`, also across a page break, until the next numbered section of the report.
- **Sentence:** "Der Oberboden bildet den Homogenbereich O1", "In den Homogenbereich B3 werden die … klassifiziert",
  "Sandbett und Auffüllungen werden den Homogenbereichen B1 und B2 zugeteilt". A plural heading
  `Homogenbereiche B1/B2` gives both codes.

Further rules:

- Bodengruppen in square brackets are Auffüllungen of that kind (DIN 18196) and are kept apart.
- The ATV are the DIN 183xx named on the pages of the section; none named → empty, with a hint.

**Proposal** (`hb.gutachten_bereiche`, `hb.vorschlag_aus_gutachten`). Each Einheit goes to the Bereich that names it.
The checks run in this order:

1. full name;
2. name or Bodenart as a noun, with synonyms such as Mutterboden / Oberboden / Humus;
3. its Bodengruppe;
4. the main group of its Bodenart (Sand → S…), the weakest hint.

When Bereiche score the same, nothing is assigned and the Einheit is listed. The result names the Einheiten without a
Bereich and the Bereiche without an Einheit: these are the differences between model and Gutachten. Bracketed
Bodengruppen count only for an anthropogenic Einheit. In the app (Homogenbereiche, no assignment yet), *Bereiche des
Gutachtens* comes first; a click takes it over, and our own proposal stays below it. The API is
`/homogenbereiche/vorschlag` → field `gutachten`.

**Measured on the training PDFs:**

| PDF | Bereiche read | Notes |
|---|---|---|
| Halle | 4/4 (A–D) | Names and Bodengruppen; the brackets of A as Auffüllung. |
| Hausham | 3/3 | Section form across pages. |
| Triefenstein | 5/5 (A1, O1, B1, B2, B3) | Sentences and a plural heading. |
| Rednitzhembach, Talheim, Berlin, Marl, Wachenroth, Wesel | none | They define no Bereiche in the text; nothing invented. |

End to end, with the Bohrungen in a schematic row:

- **Hausham:** Auffuellung → 2, Kies → 3. Bereich 1 (aufgefüllter Oberboden, 0.1–0.3 m) has no Einheit in the model and
  is shown as a difference.
- **Triefenstein:** Beton → A1, Sand → B1 (Sandbett). Schluff and Kies stay without a Bereich, because the Gutachter
  calls B3 "Lößlehme" with TL/TM; the difference is shown, not hidden.

**Decided (user, 2026-11-22):** Hangschutt and Wiesenkalk get a Bereich of their own in our proposal, for every ATV
and every level (grob, standard, fein); they no longer count as *bindig* (Hangschutt is mixed-grained with Steine,
Wiesenkalk/Seekreide calcareous-organogenic and compressible). Test `test_hangschutt_und_wiesenkalk_eigener_bereich`.

## 10b. Scanned report pages: OCR (Issue #18, 2026-11-19, training PDFs, not blind)

The three extra stages (Kennwerte §9, laboratory sheets §9b, the Gutachter's Homogenbereiche §10) read every page
through `services/extractor/textebene.py`:

- A page with an image and almost no text (< 30 characters) is read with the same OCR as the Bohrprofile
  (`prototyp_v4.ocr_words`: RapidOCR, cache `GEO_OCR_CACHE`). One OCR box is one line.
- Lines and words keep page coordinates, so the rules of the stages apply unchanged.
- The app's OCR setting applies. Without the OCR package, the page stays silent; nothing is invented.

Every result from OCR carries `quelle: "OCR"` and a hint ("aus der OCR …: am PDF prüfen"). OCR values are less
certain and are never silently treated like text-layer values.

The OCR loses umlauts and ß ("gema DIN 18196", "Kohasion", "kN/m?"), so the rules accept both spellings: the
laboratory rules compare folded text, and the units also accept `?`.

Two general rules came out of the OCR case and also hold for the text layer:

- A table row may have only two values when one of them is in the first parameter column. The OCR drops the `-` of
  empty cells.
- A value joins a row only within about one line height (≤ 14 pt), not across a missing row.

**Measured (training PDFs):**

- Wachenroth: pages 1–34 are scanned.
  - Homogenbereiche O (Oberboden), B (gewachsener Baugrund, SU*) and X (Felshorizont, Sandstein), ATV DIN 18300.
  - Kennwerte Tabelle 9: 3/3 rows, all values plausible:

    | Row | γ | γ′ | φ′ | c′ | Es |
    |---|---|---|---|---|---|
    | Oberboden | 16–18 | 6–8 | – | – | – |
    | Sand, schluffig | 18 | 10 | 32.5 | not read | 35 |
    | Sandstein | 22 | 12 | 40 | 50 | 100 |

    The Kohäsion 0 of the sand is lost in the OCR.
- The text-layer PDFs give exactly the same results as before.
- Tests: `tests/test_textebene_ocr.py`, with a fixed stand-in for the OCR, so no OCR package is needed.

Up: [Index](README.md)

Related: [18 Layer modeler](18_layer_modeler.md) · [21 Step app and norms](21_app_schritte_normen.md) ·
[Architecture](ARCHITECTURE_BAUGRUNDMODELL.md) · [11 Decisions](11_decisions.md) · [Glossary](glossary.md)
