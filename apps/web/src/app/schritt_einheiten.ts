// Schritt 4 · Einheiten: wie die Schichten zwischen den Bohrungen verbunden werden (automatisch korreliert oder
// vorgegeben), Profil aller Bohrungen nach Einheit, Beschreibungen je Einheit; die Einstellungen des Modells liegen
// eingeklappt unter „Erweitert“ (offen, sobald eine vom Standard abweicht).
import { html, nothing } from "lit";
import { live } from "lit/directives/live.js";
import { hilfe } from "./hilfe";
import { analyseTeil } from "./analyse";
import { einheitenProfil } from "./profil";
import { S, aendern, gehe, neu } from "./store";

const zahl = (v: number | null | undefined, s = 1) =>
  v === null || v === undefined ? "–" : v.toLocaleString("de-DE", { minimumFractionDigits: s, maximumFractionDigits: s });

let gewaehlt = "";
let vorgabe: { name: string; bodenarten: string }[] | null = null;   // Bearbeitung (vor dem Uebernehmen)
let vorgabeFuer = "";
let erweitertAuf = false;                       // Einstellungen des Modells: vom Nutzer geöffnet

/** Woher die Oberkante kommt: DGM (an den Bohrungen auf die GOK) oder aus den GOK der Bohrungen. */
function gelaendeText(g: Record<string, unknown> | undefined) {
  if (!g || g.quelle !== "DGM") return "aus den GOK der Bohrungen";
  return `aus dem DGM (an den Bohrungen auf die GOK, GOK − DGM bis ${zahl(Number(g.gok_minus_dgm_max_m), 2)} m)`;
}

function einstellungen() {
  const e = S.z!.einstellungen;
  const setzen = (feld: string, w: unknown) => aendern([{ op: "einstellungen", [feld]: w }]);
  const autoFeld = (feld: "puffer" | "raster" | "basis", titel: string, einheit: string, standard: number, h: Parameters<typeof hilfe>[0]) => {
    const w = e[feld];
    return html`
      <div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${w === null} @change=${(ev: Event) =>
          setzen(feld, (ev.target as HTMLInputElement).checked ? null : standard)}> ${titel} automatisch</label>${hilfe(h)}
        ${w === null ? nothing : html`<input type="number" step="any" class="kurz" .value=${live(String(w))}
          @change=${(ev: Event) => setzen(feld, Number((ev.target as HTMLInputElement).value))}> ${einheit}`}
      </div>`;
  };
  const p = S.modell?.bericht?.parameter ?? {};
  // offen, sobald eine Einstellung vom Standard abweicht (ui/projekt.py, Einstellungen)
  const eigene = e.methode !== "idw" || e.puffer !== null || e.raster !== null || e.basis !== null || !e.gok_relativ
    || !e.gelaende_dgm;
  return html`
    <details class="erweitert karte" ?open=${erweitertAuf || eigene}
      @toggle=${(ev: Event) => { erweitertAuf = (ev.target as HTMLDetailsElement).open; }}>
      <summary>Erweitert <span class="leise klein">Interpolation · Puffer · Raster · Basis · Gelände</span></summary>
      <div class="einstellung">
        <span>Interpolation ${hilfe("methode")}</span>
        <label class="inline"><input type="radio" name="methode" .checked=${e.methode === "idw"} @change=${() => setzen("methode", "idw")}> IDW</label>
        <label class="inline"><input type="radio" name="methode" .checked=${e.methode === "tps"} @change=${() => setzen("methode", "tps")}> Dünnplatten-Spline</label>
        <label class="inline" title=${S.info?.implizit ? "GemPy: je Fläche ein Skalarfeld, Orientierung aus den Kontakten (docs/27)" : "GemPy ist auf diesem Server nicht installiert (requirements-analyse.txt)"}><input
          type="radio" name="methode" ?disabled=${!S.info?.implizit && e.methode !== "implizit"} .checked=${e.methode === "implizit"}
          @change=${() => setzen("methode", "implizit")}> Implizit (GemPy)</label>
      </div>
      ${e.methode === "implizit" ? orientierungTeil() : nothing}
      ${autoFeld("puffer", "Puffer", "m", Number(p.puffer_m ?? 20), "puffer")}
      ${autoFeld("raster", "Raster", "m", Number(p.raster_m ?? 5), "raster")}
      ${autoFeld("basis", "Modellbasis", "m NHN", Math.floor(Number(p.basis_nhn ?? 0)), "basis")}
      <div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${e.gok_relativ} @change=${(ev: Event) =>
          setzen("gok_relativ", (ev.target as HTMLInputElement).checked)}> fehlende GOK: Gelände = 0 m</label>${hilfe("gok_relativ")}
      </div>
      ${S.z!.gelaende ? html`<div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${e.gelaende_dgm} @change=${(ev: Event) =>
          setzen("gelaende_dgm", (ev.target as HTMLInputElement).checked)}> Gelände aus dem DGM</label>${hilfe("gelaende_dgm")}
      </div>` : nothing}
      ${p.raster_m !== undefined ? html`<p class="leise klein">gerechnet: Puffer ${zahl(Number(p.puffer_m), 0)} m · Raster ${zahl(Number(p.raster_m))} m ·
        Basis ${zahl(Number(p.basis_nhn), 2)} m NHN · Fläche ${zahl(Number(p.flaeche_m2) / 1e4, 2)} ha ·
        Gelände ${gelaendeText(p.gelaende as unknown as Record<string, unknown> | undefined)}</p>` : nothing}
    </details>`;
}

// Orientierung je Einheit fuer die implizite Methode: berechnet (Quelle im Bericht) oder eingegeben (docs/27 G4)
type Orientierung = { einheit: string; quelle: string; fallen_grad: number | null; fallrichtung_grad?: number | null };
function orientierungTeil() {
  const b = S.modell?.bericht;
  const liste = ((b?.parameter as unknown as Record<string, unknown>)?.orientierung ?? []) as Orientierung[];
  if (!b || !liste.length) return html`<p class="leise klein">Orientierung je Einheit: nach dem Rechnen hier eingebbar.</p>`;
  const eingabe = { ...(S.z!.einstellungen.orientierung ?? {}) };
  const setzen = (name: string, feld: "fallrichtung" | "fallwinkel", roh: string) => {
    const alt = eingabe[name] ?? { fallrichtung: NaN, fallwinkel: NaN };
    const w = roh.trim() === "" ? NaN : Number(roh.replace(",", "."));
    const neu = { ...alt, [feld]: w };
    if (Number.isNaN(neu.fallrichtung) && Number.isNaN(neu.fallwinkel)) delete eingabe[name];
    else if (Number.isNaN(neu.fallrichtung) || Number.isNaN(neu.fallwinkel)) { eingabe[name] = neu; return; }   // zweiten Wert abwarten
    else eingabe[name] = neu;
    const fertig = Object.fromEntries(Object.entries(eingabe).filter(([, v]) => !Number.isNaN(v.fallrichtung) && !Number.isNaN(v.fallwinkel)));
    void aendern([{ op: "einstellungen", orientierung: Object.keys(fertig).length ? fertig : null }]);
  };
  const feld = (name: string, art: "fallrichtung" | "fallwinkel", wert: number | undefined, titel: string) => html`
    <input type="number" step="any" min="0" max=${art === "fallwinkel" ? 80 : 360} class="kurz" title=${titel}
      placeholder="–" .value=${live(wert === undefined || Number.isNaN(wert) ? "" : String(wert))}
      @change=${(ev: Event) => setzen(name, art, (ev.target as HTMLInputElement).value)}>`;
  return html`
    <div class="einstellung">
      <span>Orientierung je Einheit ${hilfe("orientierung")}</span>
      <table class="klein orientierung">
        <thead><tr><th>Einheit</th><th>berechnet</th><th>Fallrichtung °</th><th>Fallwinkel °</th></tr></thead>
        <tbody>${liste.map((o) => html`<tr>
          <td>${o.einheit}</td>
          <td class="leise">${o.quelle === "Eingabe" ? "Eingabe" : o.fallen_grad === null ? o.quelle
            : `${zahl(o.fallen_grad, 1)}°${o.fallrichtung_grad != null ? ` nach ${zahl(o.fallrichtung_grad, 0)}°` : ""} (${o.quelle})`}</td>
          <td>${feld(o.einheit, "fallrichtung", eingabe[o.einheit]?.fallrichtung, "Fallrichtung: Azimut von Nord im Uhrzeigersinn")}</td>
          <td>${feld(o.einheit, "fallwinkel", eingabe[o.einheit]?.fallwinkel, "Fallwinkel gegen die Horizontale, 0–80°")}</td>
        </tr>`)}</tbody>
      </table>
    </div>`;
}

function vorgabeTeil() {
  const b = S.modell?.bericht;
  if (!b) return nothing;
  const quelle = S.z!.vorgabe ?? b.vorlage_einheiten;
  const kennung = JSON.stringify(quelle);
  if (!vorgabe || vorgabeFuer !== kennung) {
    vorgabe = quelle.map((v) => ({ name: v.name, bodenarten: v.bodenarten.join(", ") }));
    vorgabeFuer = kennung;
  }
  const v = vorgabe;
  const uebernehmen = () => aendern([{ op: "vorgabe", wert: v.filter((x) => x.name.trim()).map((x) => ({
    name: x.name.trim(), bodenarten: x.bodenarten.split(",").map((t) => t.trim()).filter(Boolean) })) }]);
  return html`
    <section class="karte">
      <h3>Einheiten festlegen ${hilfe("einheiten")}</h3>
      <p class="leise klein">${S.z!.vorgabe ? "Vorgegeben (eigene Einheiten)." : "Automatisch korreliert – hier umbenennen oder Bodenarten zusammenlegen."}</p>
      <table class="tabelle kompakt vorgabe">
        <colgroup><col class="pfeil"><col><col><col class="weg"></colgroup>
        <thead><tr><th></th><th>Einheit</th><th>Bodenarten (mit Komma)</th><th></th></tr></thead>
        <tbody>
          ${v.map((x, i) => html`
            <tr>
              <td class="pfeile"><button class="symbol" ?disabled=${i === 0} @click=${() => { v.splice(i - 1, 0, ...v.splice(i, 1)); neu(); }}>▲</button><button
                class="symbol" ?disabled=${i === v.length - 1} @click=${() => { v.splice(i + 1, 0, ...v.splice(i, 1)); neu(); }}>▼</button></td>
              <td><input .value=${live(x.name)} @input=${(ev: Event) => { x.name = (ev.target as HTMLInputElement).value; }}></td>
              <td><input .value=${live(x.bodenarten)} @input=${(ev: Event) => { x.bodenarten = (ev.target as HTMLInputElement).value; }}></td>
              <td><button class="symbol" title="Zeile löschen" @click=${() => { v.splice(i, 1); neu(); }}>✕</button></td>
            </tr>`)}
        </tbody>
      </table>
      <div class="zeile knopfzeile">
        <button class="link" @click=${() => { v.push({ name: "", bodenarten: "" }); neu(); }}>+ Zeile</button>
        <span class="fueller"></span>
        <button ?disabled=${!S.z!.vorgabe} @click=${() => aendern([{ op: "vorgabe", wert: null }])}>Automatisch korrelieren</button>
        <button class="primaer" @click=${uebernehmen}>Mit diesen Einheiten rechnen</button>
      </div>
    </section>`;
}

export function schrittEinheiten() {
  const m = S.modell;
  const b = m?.bericht;
  const einheit = b?.einheiten.find((e) => e.name === gewaehlt);
  return html`
    <div class="schritt-einheiten">
      <div class="spalte">
        ${vorgabeTeil()}
        ${einstellungen()}
      </div>
      <div class="spalte breit">
        ${S.rechnet ? html`<div class="karte"><div class="kreisel klein"></div> Modell wird gerechnet …</div>` : nothing}
        ${m?.fehler ? html`<div class="karte warnung">Noch kein Modell: ${m.fehler}
          <button class="link" @click=${() => gehe("lage")}>→ Lage setzen</button></div>` : nothing}
        ${b ? html`
          <section class="karte">
            <h3>Einheiten (${b.einheiten.length})</h3>
            <table class="tabelle einheiten">
              <thead><tr><th></th><th>Einheit</th><th>Bodenarten</th><th>Volumen [m³]</th><th>max. Mächtigkeit [m]</th>
                <th title="in Bohrungen vorhanden / fehlt / unter der Endteufe">✓ / – / ?</th><th>Hinweise</th></tr></thead>
              <tbody>
                ${b.einheiten.map((e) => html`
                  <tr class=${e.name === gewaehlt ? "gewaehlt" : ""} @click=${() => { gewaehlt = gewaehlt === e.name ? "" : e.name; neu(); }}>
                    <td><span class="farbfeld" style=${`background:${e.farbe}`}></span></td>
                    <td><b>${e.name}</b></td>
                    <td>${e.bodenarten.join(", ")}</td>
                    <td class="zahl">${Math.round(e.volumen_m3).toLocaleString("de-DE")}</td>
                    <td class="zahl">${zahl(e.maechtigkeit_max_m, 2)}</td>
                    <td class="zahl">${e.bohrungen.vorhanden.length} / ${e.bohrungen.fehlt.length} / ${e.bohrungen.unbekannt.length}</td>
                    <td class="klein">${e.hinweise.join("; ")}</td>
                  </tr>`)}
              </tbody>
            </table>
          </section>
          <section class="karte profil-karte">
            <h3>Einheiten je Bohrung <span class="leise klein">(m NHN, Klick wählt die Einheit)</span></h3>
            <div class="profil-scroll">${einheitenProfil(b, { hoehe: 380, gewaehlt, waehlen: (n) => { gewaehlt = n; neu(); } })}</div>
          </section>
          ${einheit ? html`
            <section class="karte">
              <h3><span class="farbfeld" style=${`background:${einheit.farbe}`}></span> ${einheit.name}: Beschreibungen aus dem PDF</h3>
              <table class="tabelle kompakt">
                <thead><tr><th>Bohrung</th><th>Tiefe [m]</th><th>Bodenart</th><th>Beschreibung</th></tr></thead>
                <tbody>${einheit.schichten.map((s) => html`
                  <tr><td>${s.bohrung}</td><td class="zahl">${zahl(s.von, 2)}–${zahl(s.bis, 2)}</td><td>${s.bodenart ?? "unklassifiziert"}</td>
                    <td>${s.beschreibung || html`<span class="leise">–</span>`}</td></tr>`)}</tbody>
              </table>
            </section>` : nothing}
          ${analyseTeil()}` : nothing}
      </div>
    </div>`;
}
