// Ground Analysis (docs/27, Phase G2) im Schritt Einheiten unter „Erweitert“: Kreuzprobe (sagt das Modell eine Bohrung
// voraus, die es nicht gesehen hat?), Unsicherheit je Einheit und die virtuelle Bohrung an einem Punkt. Liest nur das
// gerechnete Modell; geändert wird nichts. Gerechnet wird erst auf Klick (je nach Größe einige Sekunden).
import { html, nothing } from "lit";
import { api, type AnalyseErgebnis, type Grundwasser, type KreuzMethode, type VirtuelleBohrung } from "./api";
import { hilfe } from "./hilfe";
import { S, neu, versuchen } from "./store";

const zahl = (v: number | null | undefined, s = 2) =>
  v === null || v === undefined ? "–" : v.toLocaleString("de-DE", { minimumFractionDigits: s, maximumFractionDigits: s });
const NAME: Record<string, string> = { idw: "IDW", tps: "Dünnplatten-Spline", implizit: "implizit (GemPy)" };

let ergebnis: AnalyseErgebnis | null = null;     // zum Modell mit diesem Schlüssel
let fuer = "";
let auf = false;
let punkt: { x: string; y: string } = { x: "", y: "" };
let virtuell: VirtuelleBohrung | null = null;

async function rechnen() {
  const sig = S.sig;
  if (!sig) return;
  const a = await versuchen(() => api.analyse(sig, 100), "Kreuzprobe und Unsicherheit werden gerechnet …");
  if (!a) return;
  ergebnis = a;
  fuer = S.modell?.schluessel ?? "";
  virtuell = null;
  if (a.mitte && !punkt.x) punkt = { x: String(a.mitte[0]), y: String(a.mitte[1]) };
  neu();
}

async function bohren() {
  const sig = S.sig;
  const x = Number(punkt.x.replace(",", ".")), y = Number(punkt.y.replace(",", "."));
  if (!sig || !Number.isFinite(x) || !Number.isFinite(y)) return;
  const v = await versuchen(() => api.analysePunkt(sig, x, y), "Virtuelle Bohrung …");
  if (v) { virtuell = v; neu(); }
}

function kreuzTabelle(a: AnalyseErgebnis) {
  const k = a.kreuzprobe!;
  return html`
    <table class="tabelle kompakt">
      <thead><tr><th>Methode</th><th title="mittlerer Fehler der Schichtgrenzen an der weggelassenen Bohrung">mittl. Fehler [m]</th>
        <th>max. [m]</th><th>Grenzen</th></tr></thead>
      <tbody>${Object.entries(k.methoden).map(([name, v]: [string, KreuzMethode]) => html`
        <tr class=${name === k.methode_modell ? "gewaehlt" : ""}>
          <td>${NAME[name] ?? name}${name === k.methode_modell ? html` <span class="leise klein">(Modell)</span>` : nothing}${name === k.beste ? html` <b title="sagt die Bohrungen am besten voraus">★</b>` : nothing}</td>
          <td class="zahl">${zahl(v.gesamt.mae)}</td><td class="zahl">${zahl(v.gesamt.max)}</td><td class="zahl">${v.gesamt.n}</td>
        </tr>`)}</tbody>
    </table>`;
}

function einheitenTabelle(a: AnalyseErgebnis) {
  const u = a.unsicherheit!;
  const kreuz = a.kreuzprobe!.methoden[a.kreuzprobe!.methode_modell];
  return html`
    <table class="tabelle kompakt">
      <thead><tr><th>Einheit</th>
        <th title="mittlerer Fehler der Unterkante in der Kreuzprobe">Kreuzprobe [m]</th>
        <th title="Streuung der Unterkante im Mittel über die Fläche (± σ)">σ Unterkante [m]</th>
        <th title="95 % der Fläche liegen darunter">σ 95 % [m]</th>
        <th title="falsch als vorhanden / fehlend vorhergesagt">Ausdehnung</th>
        <th title="Volumen mit 5 %- und 95 %-Wert aus der Messung der Grenzen">Volumen [m³]</th>
        <th title="größte Abweichung der Unterkante zur anderen Interpolation">anders interpoliert [m]</th></tr></thead>
      <tbody>${u.einheiten.map((e, j) => {
        const kp = kreuz?.einheiten[j];
        const falsch = kp ? kp.praesenz.falsch_vorhanden + kp.praesenz.falsch_fehlend : 0;
        return html`<tr>
          <td>${e.name}</td>
          <td class="zahl">${kp?.n ? zahl(kp.mae) : html`<span class="leise">–</span>`}</td>
          <td class="zahl">${e.unterkante_bezifferbar ? zahl(e.sigma_mittel_m) : html`<span class="leise" title="keine Bohrung erreicht die Unterkante">offen</span>`}</td>
          <td class="zahl">${e.unterkante_bezifferbar ? zahl(e.sigma_p95_m) : "–"}</td>
          <td class="zahl ${falsch ? "warn" : ""}">${falsch ? `${falsch} ×` : "✓"}</td>
          <td class="zahl klein">${Math.round(e.volumen_m3.modell).toLocaleString("de-DE")}${e.volumen_m3.p5 !== null
            ? html`<br><span class="leise">${Math.round(e.volumen_m3.p5).toLocaleString("de-DE")}–${Math.round(e.volumen_m3.p95!).toLocaleString("de-DE")}</span>` : nothing}</td>
          <td class="zahl">${zahl(e.methoden_differenz_m.max)}</td>
        </tr>`;
      })}</tbody>
    </table>`;
}

function vorschlagTeil(a: AnalyseErgebnis) {
  const v = a.vorschlaege ?? [];
  if (!v.length) return nothing;
  return html`
    <h4>Wo die nächste Bohrung am meisten bringt ${hilfe("erkundung")}</h4>
    <table class="tabelle kompakt vorschlag">
      <thead><tr><th>#</th><th>Rechtswert</th><th>Hochwert</th><th>Grund</th><th title="nächste vorhandene Bohrung">Abstand [m]</th><th></th></tr></thead>
      <tbody>${v.map((p, i) => html`<tr>
        <td>${i + 1}</td><td class="zahl">${zahl(p.x, 1)}</td><td class="zahl">${zahl(p.y, 1)}</td><td class="klein">${p.grund}</td>
        <td class="zahl">${zahl(p.abstand_naechste_bohrung_m, 0)}</td>
        <td><button class="link" @click=${() => { punkt = { x: String(p.x), y: String(p.y) }; bohren(); }}>virtuell bohren</button></td></tr>`)}</tbody>
    </table>
    <p class="leise klein">Ein Vorschlag aus der Unsicherheit des Modells – Zugang, Leitungen und Baufeld kennt es nicht.</p>`;
}

function virtuellTeil(a: AnalyseErgebnis) {
  const v = virtuell;
  return html`
    <h4>Virtuelle Bohrung ${hilfe("virtuell")}</h4>
    <div class="zeile knopfzeile">
      <label class="inline">Rechtswert <input class="mittel" .value=${punkt.x} @input=${(ev: Event) => { punkt.x = (ev.target as HTMLInputElement).value; }}></label>
      <label class="inline">Hochwert <input class="mittel" .value=${punkt.y} @input=${(ev: Event) => { punkt.y = (ev.target as HTMLInputElement).value; }}></label>
      <button @click=${bohren}>Bohren</button>
    </div>
    <p class="leise klein">Im System der Bohrungen${a.epsg ? ` (EPSG ${a.epsg})` : ""}; vorbelegt mit der Mitte des Modells.</p>
    ${v?.fehler ? html`<p class="warn">${v.fehler}</p>` : nothing}
    ${v && !v.fehler ? html`
      <p class="klein">GOK ${zahl(v.gok_nhn)} m NHN · ${zahl(v.abstand_m, 1)} m von ${v.naechste_bohrung} · <span class="leise">${v.herkunft}</span></p>
      <table class="tabelle kompakt virtuell">
        <thead><tr><th>Tiefe [m]</th><th>Einheit</th><th>Unterkante [m NHN]</th><th>± σ [m]</th><th>95 % [m NHN]</th></tr></thead>
        <tbody>${v.schichten!.map((s) => html`<tr>
          <td class="zahl">${zahl(s.tiefe_oben_m)}–${zahl(s.tiefe_unten_m)}</td><td>${s.einheit}</td>
          <td class="zahl">${zahl(s.unten_nhn)}${s.unterkante_offen ? html` <span class="leise klein">offen</span>` : nothing}</td>
          <td class="zahl">${zahl(s.sigma_unten_m)}</td>
          <td class="zahl klein">${s.unten_95_nhn ? `${zahl(s.unten_95_nhn[0])} … ${zahl(s.unten_95_nhn[1])}` : "–"}</td></tr>`)}</tbody>
      </table>
      ${v.hinweise!.map((h) => html`<p class="leise klein">${h}</p>`)}` : nothing}`;
}

export function analyseTeil() {
  const m = S.modell;
  if (!m?.bericht) return nothing;
  const aktuell = ergebnis && fuer === m.schluessel ? ergebnis : null;
  const veraltet = ergebnis && !aktuell;
  const a = aktuell;
  return html`
    <details class="erweitert karte analyse" ?open=${auf || !!a}
      @toggle=${(ev: Event) => { auf = (ev.target as HTMLDetailsElement).open; }}>
      <summary>Ground Analysis ${hilfe("analyse")} <span class="leise klein">Kreuzprobe · Unsicherheit · virtuelle Bohrung</span></summary>
      <div class="zeile knopfzeile">
        <button class=${a ? "" : "primaer"} @click=${rechnen}>${a ? "Neu rechnen" : "Analyse rechnen"}</button>
        ${veraltet ? html`<span class="warn klein">Das Modell hat sich geändert – neu rechnen.</span>` : nothing}
      </div>
      ${a?.fehler ? html`<p class="warn">${a.fehler}</p>` : nothing}
      ${a && !a.fehler ? html`
        <h4>Kreuzprobe <span class="leise klein">(${a.kreuzprobe!.bohrungen} Bohrungen, je eine weggelassen)</span></h4>
        ${kreuzTabelle(a)}
        ${[...a.kreuzprobe!.hinweise, ...a.unsicherheit!.hinweise].map((h) => html`<p class="hinweis klein">⚑ ${h}</p>`)}
        <h4>Unsicherheit je Einheit <span class="leise klein">(${a.unsicherheit!.laeufe} Läufe, ${NAME[a.unsicherheit!.methode] ?? a.unsicherheit!.methode})</span></h4>
        ${einheitenTabelle(a)}
        <details class="klein"><summary class="leise">Annahmen</summary>
          <ul>${a.unsicherheit!.annahmen.map((x) => html`<li>${x}</li>`)}</ul></details>
        ${vorschlagTeil(a)}
        ${virtuellTeil(a)}` : nothing}
    </details>`;
}


// ------------------------------------------------------------------ im Viewer (Schritt Modell, unter Erweitert)
let viewerEinheit = 0;
let viewerAn = "";                                // Name der gezeigten Einheit ("" = keine)
let viewerFuer = "";                              // Schluessel des Modells, zu dem sie gehoert

const esc = (s: string) => s.replace(/[<>&"]/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;" })[c]!);

async function flaecheZeigen() {
  const sig = S.sig;
  if (!sig || !S.viewer) return;
  const f = await versuchen(() => api.analyseFlaeche(sig, viewerEinheit), "Unsicherheit wird gerechnet …");
  if (!f) return;
  if (f.fehler) { S.viewer.meldung(f.fehler, 6000); return; }
  S.viewer.unsicherheit({ name: f.name!, punkte: f.punkte!, dreiecke: f.dreiecke!, sigma: f.sigma!, sigma_max: f.sigma_max! });
  viewerAn = f.name!;
  viewerFuer = S.modell?.schluessel ?? "";
  if (f.hinweis) S.viewer.meldung(f.hinweis, 6000);
  neu();
}

function flaecheWeg() {
  S.viewer?.unsicherheit(null);
  viewerAn = "";
  neu();
}

let wasser: Grundwasser | null = null;            // gezeigte Grundwasserflaeche (null = keine)
let wasserFuer = "";

async function wasserZeigen() {
  const sig = S.sig;
  if (!sig || !S.viewer) return;
  const g = await versuchen(() => api.analyseGrundwasser(sig), "Grundwasserfläche …");
  if (!g) return;
  if (g.fehler) { S.viewer.meldung(g.fehler, 6000); return; }
  wasser = g;
  wasserFuer = S.modell?.schluessel ?? "";
  S.viewer.grundwasser(g.flaeche ?? null);
  if (!g.flaeche) S.viewer.meldung(g.hinweise?.[0] ?? "keine Grundwasserfläche", 6000);
  neu();
}

function wasserWeg() {
  S.viewer?.grundwasser(null);
  wasser = null;
  neu();
}

function wasserTeil() {
  if (wasser && wasserFuer !== (S.modell?.schluessel ?? "")) { S.viewer?.grundwasser(null); wasser = null; }   // Modell neu
  const g = wasser;
  const z = (x: number, s = 2) => x.toLocaleString("de-DE", { minimumFractionDigits: s, maximumFractionDigits: s });
  return html`
    <div class="zeile">
      <button @click=${wasserZeigen}>Grundwasserfläche zeigen</button>${hilfe("grundwasser")}
      ${g ? html`<button class="link" @click=${wasserWeg}>Grundwasser ausblenden</button>` : nothing}
    </div>
    ${g ? html`<div class="klein grundwasser">
      <p>${g.gemessen} gemessene${g.trocken ? `, ${g.trocken} trockene` : ""} von ${g.staende?.length ?? 0} Bohrungen
        ${g.flaeche ? html` · ${z(g.flaeche.z_min)} bis ${z(g.flaeche.z_max)} m NHN` : nothing}
        ${g.kreuzprobe ? html` · Kreuzprobe ⌀ ${z(g.kreuzprobe.mae_m)} m, max. ${z(g.kreuzprobe.max_m)} m` : nothing}</p>
      ${(g.hinweise ?? []).length ? html`<ul class="hinweise">${g.hinweise!.map((h) => html`<li>${h}</li>`)}</ul>` : nothing}
    </div>` : nothing}`;
}

async function punktImViewer() {
  const sig = S.sig;
  const v = S.viewer;
  if (!sig || !v) return;
  const p = await v.punktWaehlen();
  if (!p) return;
  const b = await versuchen(() => api.analysePunkt(sig, p.e, p.n), "Virtuelle Bohrung …");
  if (!b) return;
  if (b.fehler) { v.meldung(b.fehler, 6000); return; }
  const z = (x: number | null | undefined, s = 2) => (x === null || x === undefined ? "–" : x.toLocaleString("de-DE", { minimumFractionDigits: s, maximumFractionDigits: s }));
  const zeilen = b.schichten!.map((s) => `<tr><td>${z(s.tiefe_oben_m)}–${z(s.tiefe_unten_m)} m</td><td>${esc(s.einheit)}</td>
    <td>${s.sigma_unten_m === null ? (s.unterkante_offen ? "offen" : "–") : `± ${z(s.sigma_unten_m)} m`}</td></tr>`).join("");
  v.tafel(`Virtuelle Bohrung`, `<p>${z(b.x, 1)} / ${z(b.y, 1)} · GOK ${z(b.gok_nhn)} m NHN · ${z(b.abstand_m, 1)} m von ${esc(b.naechste_bohrung ?? "")}</p>
    <table><tr><th>Tiefe</th><th>Einheit</th><th>Unterkante</th></tr>${zeilen}</table>
    <p><i>${esc(b.herkunft ?? "")}</i></p>`);
}

/** Abschnitt im Schritt Modell (unter Erweitert): Unsicherheit einer Unterkante im Viewer, virtuelle Bohrung per Klick. */
export function analyseViewerTeil() {
  const b = S.modell?.bericht;
  if (!b || S.modell?.fehler) return nothing;
  if (viewerEinheit >= b.einheiten.length) viewerEinheit = 0;
  if (viewerAn && viewerFuer !== (S.modell?.schluessel ?? "")) { S.viewer?.unsicherheit(null); viewerAn = ""; }   // Modell neu
  return html`
    <section class="abschnitt-flach analyse-viewer">
      <h3>Ground Analysis im Viewer ${hilfe("analyse")}</h3>
      <div class="zeile">
        <select @change=${(e: Event) => { viewerEinheit = Number((e.target as HTMLSelectElement).value); }}>
          ${b.einheiten.map((x, j) => html`<option value=${j} .selected=${j === viewerEinheit}>${x.name}</option>`)}
        </select>
        <button @click=${flaecheZeigen}>Unsicherheit zeigen</button>
        ${viewerAn ? html`<button class="link" @click=${flaecheWeg}>Unsicherheit ausblenden</button>` : nothing}
      </div>
      ${viewerAn ? html`<p class="leise klein">Gezeigt: Unterkante ${viewerAn}, gefärbt nach σ (grün sicher, rot unsicher).</p>` : nothing}
      <div class="zeile"><button @click=${punktImViewer}>Virtuelle Bohrung: Punkt im Viewer wählen</button>${hilfe("virtuell")}</div>
      ${wasserTeil()}
    </section>`;
}
