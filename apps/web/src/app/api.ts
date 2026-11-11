// Schnittstelle zum Server (server/api.py). Alle Aenderungen gehen als Liste von Operationen an
// /api/projekt/<signatur>/aendern (ui/projekt.aendern); die Antwort ist der neue Stand des Projekts.
import type { Kalibrierung, Nadel, Punkt, Unterlage } from "../viewer/kanal";

export interface Bohrung {
  id: string; code: string; dokument: string; seite: number;
  modell: boolean; entfernt: boolean; geprueft: boolean;
  gok: number | null; gok_pdf: boolean; gok_quelle: string; endteufe: number | null;
  x: number | null; y: number | null; epsg: number | null; lage_aus: string;
  schichten_n: number; schichten_geprueft: number; unklassifiziert: number; offen: number; korrigiert: number;
  konfidenz_min: number | null; grundwasser: string; durchmesser: number | null; doppelt_in: string | null;
  hinweise: string[];
}

export interface Norm {
  benennung: string; din4023: string; iso14688: string; bodengruppe: string | null; konsistenz: string | null;
  lagerung: string | null; kalk: string | null; feuchte: string | null; bodenfarbe: string | null;
  klasse: string | null; farbe: string; farbname: string; sicher: boolean; hinweise: string[];
}

export interface Schicht {
  k: number; von: number; bis: number; bodenart: string; farbe: string;
  geprueft: boolean; korrigiert: boolean; unklassifiziert: boolean; offen: boolean;
  konfidenz: number | null; beschreibung: string; hinweise: string[];
  quelle: { dokument: string; seite: number; bbox: number[] | null; methode: string | null };
  norm: Norm;
  vorschlag: { klasse: string; benennung: string; din4023: string; sicher: boolean; hinweise: string[] } | null;
}

export interface Klasse { klasse: string; name: string; art: string; farbe: string; farbname: string; din4023: string; iso14688: string; beleg: string }

export interface Eincheckung {
  nr: number; zeit: string; modell: string | null; kommentar: string;
  stand: { bohrungen: [number, number]; schichten: [number, number]; unklassifiziert?: number; unklassifiziert_offen?: number;
           korrigiert: number; manuelle_lage: number; entfernt?: number };
}

export interface Pruefstand {
  bohrungen: [number, number]; schichten: [number, number]; unklassifiziert: number; unklassifiziert_offen: number;
  korrigiert: number; manuelle_lage: number; entfernt: number;
}

export interface ReiheZeile { id: string; nr: number; code: string; abstand: number | null; station: number; quelle: string; quelle_text: string }

export interface GelaendeZeile {
  id: string; code: string; gok: number | null; dgm: number | null; differenz: number | null;
  status: "ok" | "abweichung" | "ohne_gok" | "aus_dgm" | "ausserhalb" | "ohne_lage" | "anderes_system";
}

/** LoD2-Gebäude der Länder (docs/23 P4): Kacheln, Dienste mit Lizenz; die Geometrie liegt nur im IFC. */
export interface Gebaeude {
  anzahl: number; flaechen: number; epsg: number; geladen: string; stand: string;
  quelle: {
    dienste: { dienst: string; land: string; titel: string; anbieter: string; lizenz: string; lizenz_url: string;
               namensnennung: string; beleg: string }[];
    abgerufen: string; ausschnitt: [number, number, number, number]; kacheln: number; ohne_kachel: string[]; fehler: string[];
  };
  hinweis?: string;                                  // anderes System als die Bohrungen: nicht im Modell
}

/** Dienst des Landes, von dem das DGM stammt (docs/23 §2.4): Lizenz und Namensnennung gehen ins IFC. */
export interface DgmQuelle {
  dienst: string; land: string; titel: string; anbieter: string; lizenz: string; lizenz_url: string;
  namensnennung: string; beleg: string; abgerufen: string; ausschnitt: [number, number, number, number]; raster_m: number;
}

/** Gelaendemodell (DGM aus Dateien des Nutzers oder vom Dienst des Landes, docs/23) und Vergleich GOK - DGM. */
export interface Gelaende {
  info: { name: string; dateien: string[]; epsg: number | null; dx: number; dy: number; zeilen: number; spalten: number;
          ausdehnung: [number, number, number, number]; zmin: number | null; zmax: number | null; abdeckung: number; geladen: string;
          quelle: DgmQuelle | null };
  pruefung: { zeilen: GelaendeZeile[]; verglichen: number; median: number | null; max: number | null; vorschlaege: number;
              warnungen: string[]; toleranz: number } | null;
  fehler: string;
}

/** Bohrung eines Landes aus der Abfrage (docs/23 §2.2). */
export interface SgdTreffer {
  dienst: string; id: string; name: string; x: number; y: number; gok: number | null; teufe: number | null;
  datum: string | null; schichten: "boreholeml" | "grafik" | "keine" | "ohne Petrographie" | "portal"; schichten_n: number | null;
  profil: string | null; abstand: number; gutachten?: string; abweichung_lage?: number; abweichung_gok?: number | null;
  uebernommen: boolean; uebernehmbar: boolean;
}

export interface Sgd {
  mitte: [number, number]; epsg: number; radius: number; zeit: string; dienste: string[]; treffer: SgdTreffer[];
  fehler: { dienst: string; fehler: string }[];
  quellen: { dienst: string; titel: string; land: string; lizenz: string; namensnennung: string; beleg: string }[];
  gegenprobe: { anzahl: number; lage_max: number | null; gok_max: number | null };
  /** Länder im Umkreis ohne Datendienst: ihr Portal (Link, „ungeprueft“ = nicht gegen den Dienst getestet). */
  portale?: { dienst: string; land: string; titel: string; url: string; hinweis: string; status: string }[];
}

/** Dienst eines Landes an einem Punkt (Karte, Standort): was er dort liefert; ein Portal mit Adresse (Link). */
export interface DienstAmOrt {
  dienst: string; art: "bohrungen" | "dgm" | "gebaeude"; land: string; text: string; url?: string; status?: string;
}

/** Klick in die Karte: Punkt in ETRS89/UTM und die Dienste der Länder dort. */
export interface StandortPunkt { x: number; y: number; epsg: number; laenge: number; breite: number; dienste: DienstAmOrt[] }

/** Pruefliste nach GeolDG (docs/21 §5.3): Fristen, je eigene Bohrung was die App hat, Hinweise mit Beleg. */
export type GeoldgStatus = "ok" | "markiert" | "offen";
export interface GeoldgFrist {
  id: "anzeige" | "fachdaten" | "bewertungsdaten"; titel: string; regel: string; beleg: string; url: string;
  bezug: "beginn" | "abschluss"; bis: string | null; tage: number | null;
}
export interface Geoldg {
  quelle: { titel: string; url: string; gelesen: string; hinweis: string };
  angaben: { beginn: string; abschluss: string; behoerde: boolean };
  heute: string; fristen: GeoldgFrist[]; abschluss: { text: string; beleg: string; url: string };
  punkte: { id: string; titel: string; beleg: string; quelle: "app" | "protokoll" }[];
  bohrungen: { code: string; art: string; punkte: Record<string, [GeoldgStatus, string]>; bereit: boolean; boreholeml: string }[];
  fremd: { code: string; herkunft: string }[];
  zusammenfassung: { eigene: number; bereit: number; boreholeml: number; fremd: number; offen: { code: string; was: string }[] };
  vorerkundung: boolean;
  anzeige_inhalt: { beleg: string; url: string; punkte: string[]; aus_der_app: string };
  hinweise: { text: string; beleg: string; url: string }[];
}

export interface Einstellungen {
  methode: string; puffer: number | null; raster: number | null; basis: number | null; gok_relativ: boolean;
  gelaende_dgm: boolean;                            // Oberkante des Modells aus dem DGM (an den Bohrungen auf die GOK)
}

export interface Zustand {
  signatur: string; name: string; version: number; schritt: string;
  dokumente: { index: number; datei: string; seiten: number | null; pdf: boolean }[];
  lage_modus: "koordinaten" | "reihe"; erzeugt: boolean; auto: boolean;
  durchmesser: number | null; durchmesser_auto: number; ueberhoehung: number;
  einstellungen: Einstellungen;
  unterlage: (Unterlage & { seite: number; seiten: number; sha: string }) | null;
  reihe: ReiheZeile[]; reihe_standard: number;
  vorgabe: { name: string; bodenarten: string[] }[] | null;
  eincheckungen: Eincheckung[]; pruefstand: Pruefstand; eingecheckt: string | null; seit_einchecken_geaendert: boolean;
  bohrungen: Bohrung[]; klassen: Klasse[];
  hinweise: string[]; nicht_im_modell: { id?: string; code: string; dokument: string; grund: string }[];
  modell: { schluessel: string; aktuell: boolean; ifc: string | null };
  punkte: Punkt[];                                    // freie Punkte auf dem Plan (noch keiner Bohrung zugeordnet)
  gelaende: Gelaende | null;                          // DGM und Vergleich mit der GOK (Schritt Lage)
  sgd: Sgd | null;                                    // letzte Abfrage der Bohrungen der Länder
  gebaeude: Gebaeude | null;                          // LoD2-Gebäude der Länder um das Projekt (Kopf)
  standort: { x: number; y: number; epsg: number; dienste: DienstAmOrt[] } | null;   // Projekt an einem Punkt, ohne Gutachten
  reifegrad: Reifegrad;
  geoldg: Geoldg;                                     // Übermittlung an den Geologischen Dienst (GeolDG)
  viewer: { bohrungen: Nadel[]; ursprung: [number, number]; epsg: number | null; modus: "koordinaten" | "reihe";
            punkte: Punkt[] };
}

export interface EinheitBericht {
  name: string; bodenarten: string[]; farbe: string; volumen_m3: number; maechtigkeit_max_m: number; geschlossen: boolean;
  bohrungen: { vorhanden: string[]; fehlt: string[]; unbekannt: string[] };
  schichten: { bohrung: string; von: number; bis: number; bodenart: string | null; beschreibung: string }[];
  hinweise: string[];
}

export interface Bericht {
  epsg: number | null; ursprung: [number, number]; parameter: Record<string, number | string>;
  einheiten: EinheitBericht[];
  bohrungen: { code: string; x: number; y: number; gok: number; lage: string; hoehe: string; endteufe_nhn: number;
               einheiten: { einheit: string; status: string; ok_modell: number; uk_modell: number }[]; hinweise: string[] }[];
  ausgeschlossen: { code: string; dokument: string; grund: string }[];
  pruefungen: { max_abweichung_an_bohrungen_m: number; alle_koerper_geschlossen: boolean };
  hinweise: string[];
  vorlage_einheiten: { name: string; bodenarten: string[] }[];
}

export interface ModellErgebnis {
  schluessel: string; fehler: string; bericht: Bericht | null; ifc: string | null;
  hinweise: string[]; nicht_im_modell: { code: string; dokument: string; grund: string }[]; zustand: Zustand;
}

export interface Auftrag {
  id: string; dateien: string[]; fertig: boolean; fehler: string[]; projekt: string | null;
  stand: { datei: string; nr: number; dateien: number; seite: number; seiten: number; klasse: string };
}

export interface ProjektKurz {
  signatur: string; name: string; dokumente: string[]; bohrungen: number; geprueft: number; eincheckungen: number;
  geaendert: string; schritt: string; standort: boolean;
  fremd?: number;                                        // davon Bohrungen der Laender (fremd.json)
}

/** Reife des Projekts (docs/23 §2.3): Gutachten, Vorerkundung (nur Daten der Länder) oder gemischt. */
export interface Reifegrad { stufe: "Gutachten" | "Vorerkundung" | "gemischt"; anzahl: Record<string, number> }

/** Ground Analysis (docs/27 G2): Kreuzprobe und Unsicherheit zum gerechneten Modell. */
export interface Fehlermass { n: number; mae: number | null; rmse: number | null; max: number | null; bias: number | null }
export interface KreuzMethode {
  gesamt: Fehlermass;
  einheiten: (Fehlermass & { name: string; praesenz: { richtig: number; falsch_vorhanden: number; falsch_fehlend: number };
              endteufe_verletzt: { bohrung: string; um_m: number }[] })[];
  bohrungen: { code: string; abstand_naechste_m: number; n: number; mae: number | null; max: number | null; auffaellig: boolean }[];
  gelaende: Fehlermass | null;
  auffaellig: { bohrung: string; fehler_m: number; median_der_anderen_ohne_sie_m: number }[];
}
export interface UnsicherheitEinheit {
  name: string; unterkante_bezifferbar: boolean; c_m2_je_m: number | null; kreuz_fehler: number; c_aus: string | null;
  sigma_mittel_m: number | null; sigma_p95_m: number | null; sigma_max_m: number | null; sigma_messung_mittel_m: number | null;
  volumen_m3: { modell: number; p5: number | null; p95: number | null };
  methoden_differenz_m: { gegen: string; median: number | null; p95: number | null; max: number | null };
}
export interface AnalyseErgebnis {
  fehler: string; schluessel?: string; epsg?: number | null; mitte?: [number, number];
  bohrungen?: { code: string; x: number; y: number }[];
  kreuzprobe?: { methode_modell: string; bohrungen: number; beste: string | null; hinweise: string[];
                 methoden: Record<string, KreuzMethode> };
  unsicherheit?: { laeufe: number; methode: string; sigma_exakt_m: number; einheiten: UnsicherheitEinheit[];
                   hinweise: string[]; annahmen: string[] };
  sigma_max_m?: number | null;
  vorschlaege?: { x: number; y: number; wert_m: number; lage_m: number; ausdehnung_m: number;
                  abstand_naechste_bohrung_m: number; grund: string }[];
}
export interface VirtuelleBohrung {
  fehler: string; x?: number; y?: number; gok_nhn?: number; endteufe_m?: number; naechste_bohrung?: string; abstand_m?: number;
  schichten?: { einheit: string; bodenarten: string[]; oben_nhn: number; unten_nhn: number; tiefe_oben_m: number;
                tiefe_unten_m: number; maechtigkeit_m: number; sigma_unten_m: number | null; unten_95_nhn: [number, number] | null;
                unterkante_offen: boolean }[];
  hinweise?: string[]; herkunft?: string;
}

export type Op = Record<string, unknown> & { op: string };
export type { Kalibrierung };

async function anfrage<T>(pfad: string, init?: RequestInit): Promise<T> {
  const r = await fetch(pfad, init);
  if (!r.ok) {
    let text = `${r.status} ${r.statusText}`;
    try {
      const j = await r.json();
      text = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail);
    } catch { /* kein JSON */ }
    throw new Error(text);
  }
  return (await r.json()) as T;
}

const json = (daten: unknown): RequestInit => ({ method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(daten) });

export const api = {
  info: () => anfrage<{ version: string; ocr: boolean; implizit?: boolean; lizenz: string; quellcode: string;
                        beispiele: { name: string; titel: string; standort?: boolean }[] }>("/api/info"),
  projekte: () => anfrage<ProjektKurz[]>("/api/projekte"),
  beispiel: (name: string) =>
    anfrage<{ projekt?: string; auftrag?: string; schritt?: "gutachten" | "bohrungen" | "lage" | "einheiten" | "modell" }>(
      "/api/beispiel", json({ name })),
  gutachten(dateien: File[], ocr: boolean, standort = "") {
    const f = new FormData();
    for (const d of dateien) f.append("dateien", d, d.name);
    f.append("ocr", String(ocr));
    if (standort) f.append("standort", standort);     // Bohrungen der Länder, DGM und Gebäude des Standorts kommen mit
    return anfrage<Auftrag>("/api/gutachten", { method: "POST", body: f });
  },
  standort: (x: number, y: number, epsg: number, name: string) =>
    anfrage<{ projekt: string; vorhanden: boolean }>("/api/standort", json({ x, y, epsg, name })),
  standortPunkt: (laenge: number, breite: number, epsg?: number) =>
    anfrage<StandortPunkt>(`/api/standort/punkt?laenge=${laenge}&breite=${breite}${epsg ? `&epsg=${epsg}` : ""}`),
  auftrag: (id: string) => anfrage<Auftrag>(`/api/auftrag/${id}`),
  zustand: (sig: string) => anfrage<Zustand>(`/api/projekt/${sig}`),
  aendern: (sig: string, ops: Op[]) => anfrage<{ meldungen: string[]; zustand: Zustand }>(`/api/projekt/${sig}/aendern`, json({ ops })),
  zuruecksetzen: (sig: string) => anfrage<Zustand>(`/api/projekt/${sig}/zuruecksetzen`, { method: "POST" }),
  loeschen: (sig: string) => anfrage<{ ok: boolean }>(`/api/projekt/${sig}`, { method: "DELETE" }),
  bohrung: (sig: string, bid: string) => anfrage<{ bohrung: Bohrung; schichten: Schicht[] }>(`/api/projekt/${sig}/bohrung/${encodeURIComponent(bid)}`),
  seite: (sig: string, dokument: number, seite: number) =>
    anfrage<{ url: string; px_je_pt: number; breite_pt: number; hoehe_pt: number; seite: number; seiten: number | null }>(
      `/api/projekt/${sig}/seite/${dokument}/${seite}`),
  unterlage(sig: string, datei: File, art: string, seite: number) {
    const f = new FormData();
    f.append("datei", datei, datei.name);
    f.append("art", art);
    f.append("seite", String(seite));
    return anfrage<Zustand>(`/api/projekt/${sig}/unterlage`, { method: "POST", body: f });
  },
  unterlageSeite: (sig: string, seite: number, art: string) => anfrage<Zustand>(`/api/projekt/${sig}/unterlage/seite`, json({ seite, art })),
  unterlageEntfernen: (sig: string) => anfrage<Zustand>(`/api/projekt/${sig}/unterlage`, { method: "DELETE" }),
  dgm(sig: string, dateien: File[], epsg: number | null) {
    const f = new FormData();
    for (const d of dateien) f.append("dateien", d, d.name);
    f.append("epsg", epsg === null ? "" : String(epsg));
    return anfrage<Zustand>(`/api/projekt/${sig}/dgm`, { method: "POST", body: f });
  },
  dgmAbruf: (sig: string, rand: number) => anfrage<Zustand>(`/api/projekt/${sig}/dgm/abruf`, json({ rand })),
  dgmEntfernen: (sig: string) => anfrage<Zustand>(`/api/projekt/${sig}/dgm`, { method: "DELETE" }),
  gebaeudeAbruf: (sig: string, rand: number) => anfrage<Zustand>(`/api/projekt/${sig}/gebaeude/abruf`, json({ rand })),
  gebaeudeEntfernen: (sig: string) => anfrage<Zustand>(`/api/projekt/${sig}/gebaeude`, { method: "DELETE" }),
  sgdAbfrage: (sig: string, radius: number) => anfrage<Zustand>(`/api/projekt/${sig}/sgd/abfrage`, json({ radius })),
  sgdUebernehmen: (sig: string, auswahl: { dienst: string; id: string }[]) =>
    anfrage<{ meldungen: string[]; zustand: Zustand }>(`/api/projekt/${sig}/sgd/uebernehmen`, json({ auswahl })),
  sgdVerwerfen: (sig: string) => anfrage<Zustand>(`/api/projekt/${sig}/sgd`, { method: "DELETE" }),
  modell: (sig: string) => anfrage<ModellErgebnis>(`/api/projekt/${sig}/modell`, { method: "POST" }),
  analyse: (sig: string, laeufe = 100) => anfrage<AnalyseErgebnis>(`/api/projekt/${sig}/analyse`, json({ laeufe })),
  analysePunkt: (sig: string, x: number, y: number) => anfrage<VirtuelleBohrung>(`/api/projekt/${sig}/analyse/punkt`, json({ x, y })),
  einchecken: (sig: string, kommentar: string) => anfrage<{ eintrag: Eincheckung; zustand: Zustand }>(`/api/projekt/${sig}/einchecken`, json({ kommentar })),
  exportUrl: (sig: string, art: string) => `/api/projekt/${sig}/export/${art}`,
};
