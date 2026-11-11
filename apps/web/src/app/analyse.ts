// Ground Analysis (docs/27, Phase G2) im Schritt Einheiten unter „Erweitert“: Kreuzprobe (sagt das Modell eine Bohrung
// voraus, die es nicht gesehen hat?), Unsicherheit je Einheit und die virtuelle Bohrung an einem Punkt. Liest nur das
// gerechnete Modell; geändert wird nichts. Gerechnet wird erst auf Klick (je nach Größe einige Sekunden).
import { html, nothing } from "lit";
import { api, type AnalyseErgebnis, type KreuzMethode, type VirtuelleBohrung } from "./api";
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
