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
>   *Homogenbereiche (VOB/C)*). Nothing is proposed silently: the only proposal is one Bereich per Einheit.
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

## 5. The other tables (DIN 4023 Tabelle 2 and 3)

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
values are a display of those names. Tabelle 3 is kept as a reference (`geologische_benennungen`) including the
Benennungen without a model class of their own (Hangschutt Lx, Wiesenkalk Wk, Bänderton Bt, Kreidestein Krst, Kalktuff
Kltf); they are not recognised in descriptions yet. Anthropogene Böden (A) have no colour in the table; Auffüllung stays
grey (display).

---

Up: [Index](README.md)

Related: [18 Layer modeler](18_layer_modeler.md) · [21 Step app and norms](21_app_schritte_normen.md) ·
[Architecture](ARCHITECTURE_BAUGRUNDMODELL.md) · [11 Decisions](11_decisions.md) · [Glossary](glossary.md)
