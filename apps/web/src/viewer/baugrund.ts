// Inhalt eines Baugrundmodells (IFC4X3 aus services/modeler) in einem Fragments-Modell finden.
// Description unterscheidet die Ebenen: "Modelleinheit k/n" (IfcGeomodel) und "Bohrsaeule" (IfcBorehole);
// das Gelaende um das Modell (aus dem DGM) ist ein IfcGeographicElement TERRAIN.
import type { FragmentsModel } from "@thatopen/fragments";

export type Psets = Record<string, Record<string, unknown>>;

export interface Einheit {
  localId: number;
  name: string;
  reihenfolge: number;
  farbe: string;
  volumen: number;
  psets: Psets;
}

export interface Inhalt {
  einheiten: Einheit[];
  bohrsaeulen: number[];
  bohrungen: number[];
  gelaende: number[];
  gebaeude: number[];
  modellname: string;
  modell: Record<string, unknown>;
}

type Wert = { value?: unknown };
type Datensatz = Record<string, unknown>;

const wert = (d: Datensatz, k: string): unknown => (d[k] as Wert | undefined)?.value;

export function psets(d: Datensatz): Psets {
  const out: Psets = {};
  for (const ps of (d.IsDefinedBy as Datensatz[] | undefined) ?? []) {
    const name = String(wert(ps, "Name") ?? "Pset");
    const props: Record<string, unknown> = {};
    for (const p of (ps.HasProperties as Datensatz[] | undefined) ?? []) {
      props[String(wert(p, "Name"))] = wert(p, "NominalValue");
    }
    out[name] = props;
  }
  return out;
}

export async function inhalt(model: FragmentsModel): Promise<Inhalt> {
  const kat = await model.getItemsOfCategories([/GEOTECHNICALSTRATUM/, /BOREHOLE/, /GEOMODEL/, /GEOGRAPHICELEMENT/,
                                                 /BUILDINGELEMENTPROXY/]);
  const strata = kat.IFCGEOTECHNICALSTRATUM ?? [];
  const kurz = strata.length
    ? await model.getItemsData(strata, { attributesDefault: false, attributes: ["Name", "Description"] })
    : [];
  const einheitIds: number[] = [];
  const bohrsaeulen: number[] = [];
  for (const d of kurz as Datensatz[]) {
    const id = Number(wert(d, "_localId"));
    // Koerper des Modells: Einheiten, oder Homogenbereiche (docs/28) samt Einheiten ohne Bereich
    (/^(Modelleinheit|Homogenbereich|Einheit ohne Homogenbereich)/.test(String(wert(d, "Description") ?? ""))
      ? einheitIds : bohrsaeulen).push(id);
  }
  const mitPsets = { attributesDefault: true, relations: { IsDefinedBy: { attributes: true, relations: true } } };
  const daten = einheitIds.length ? await model.getItemsData(einheitIds, mitPsets) : [];
  const einheiten = daten.map((d, i): Einheit => {
    const ps = psets(d as Datensatz);
    // Haupt-Pset: Modelleinheit, sonst der Homogenbereich der ATV, nach der das Modell gebaut ist (mit Volumen)
    const me = ps.CPset_Modelleinheit
      ?? Object.entries(ps).find(([n, w]) => n.startsWith("CPset_Homogenbereich_") && w.Volumen_m3 !== undefined)?.[1] ?? {};
    return {
      localId: Number(wert(d as Datensatz, "_localId")),
      name: String(wert(d as Datensatz, "Name") ?? `Einheit ${i + 1}`),
      reihenfolge: Number(me.Reihenfolge ?? i + 1),
      farbe: String(me.Farbe ?? "#cccccc"),
      volumen: Number(me.Volumen_m3 ?? 0),
      psets: ps,
    };
  });
  einheiten.sort((a, b) => a.reihenfolge - b.reihenfolge);
  const gm = kat.IFCGEOMODEL?.length ? (await model.getItemsData(kat.IFCGEOMODEL.slice(0, 1), mitPsets))[0] : undefined;
  return {
    einheiten,
    bohrsaeulen,
    bohrungen: kat.IFCBOREHOLE ?? [],
    gelaende: kat.IFCGEOGRAPHICELEMENT ?? [],
    gebaeude: kat.IFCBUILDINGELEMENTPROXY ?? [],                 // LoD2-Gebaeude der Umgebung
    modellname: gm ? String(wert(gm as Datensatz, "Name")) : "",
    modell: gm ? (psets(gm as Datensatz).CPset_Baugrundmodell ?? {}) : {},
  };
}

export async function eigenschaften(model: FragmentsModel, localId: number) {
  const [d] = await model.getItemsData([localId], {
    attributesDefault: true,
    relations: { IsDefinedBy: { attributes: true, relations: true }, Decomposes: { attributes: true, relations: false } },
  });
  const datensatz = d as Datensatz;
  const eltern = (datensatz.Decomposes as Datensatz[] | undefined)?.[0];
  return {
    name: String(wert(datensatz, "Name") ?? localId),
    klasse: String(wert(datensatz, "_category") ?? ""),
    beschreibung: String(wert(datensatz, "Description") ?? ""),
    teilVon: eltern ? String(wert(eltern, "Name") ?? "") : "",
    psets: psets(datensatz),
  };
}
