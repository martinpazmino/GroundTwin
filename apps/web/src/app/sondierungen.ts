// Sondierungen DPH/CPT im Schritt Bohrungen (Issue #27 Teil 2, docs/05 §6): eigene Gruppe in der Liste, Detail mit
// Kurve (N10 als Treppe, CPT q_c/f_s als Linie), GOK, Lage, geprüft und entfernen, rechts die Seite im PDF mit dem
// Diagramm markiert. Die gelesenen Werte bleiben, wie sie im PDF stehen; geändert werden nur Lage, GOK und Prüfvermerk.
import { html, nothing, svg } from "lit";
import { live } from "lit/directives/live.js";
import { api, type Sondierung, type SondierungDetail, type SondierungWert } from "./api";
import { hilfe } from "./hilfe";
import { S, aendern, neu, versuchen } from "./store";

let gewaehlt = "";
const details = new Map<string, SondierungDetail>();
let seite: { schluessel: string; daten: Awaited<ReturnType<typeof api.seite>> } | null = null;
let laedt = "";
let zoom = 0.5;

const zahl = (v: number | null | undefined, s = 2) =>
  v === null || v === undefined ? "" : v.toLocaleString("de-DE", { minimumFractionDigits: s, maximumFractionDigits: s });

export const sondierungGewaehlt = () => (S.z?.sondierungen ?? []).find((s) => s.id === gewaehlt) ?? null;
export function sondierungAbwaehlen() { gewaehlt = ""; }

async function waehlen(sid: string) {
  gewaehlt = sid;
  S.bid = "";
  neu();
  await laden(sid, true);
}

async function laden(sid: string, frisch = false) {
  if (!S.sig || (!frisch && details.has(sid))) return;
  const d = await versuchen(() => api.sondierung(S.sig, sid));
  if (d) { details.set(sid, d); neu(); }
}

function setzen(s: Sondierung, feld: string, wert: unknown) {
  details.delete(s.id);
  return aendern([{ op: "sondierung", sondierung: s.id, feld, wert }]).then(() => laden(s.id, true));
}

function zeichen(s: Sondierung) {
  if (s.entfernt) return html`<span class="zeichen raus" title="nicht im Projekt">–</span>`;
  if (!s.werte_n) return html`<span class="zeichen warn" title="ohne Werte (nur Code und Seite gelesen)">⚠</span>`;
  if (s.geprueft) return html`<span class="zeichen ok" title="geprüft">✓</span>`;
  return html`<span class="zeichen" title="noch zu prüfen">○</span>`;
}

/** Gruppe unter der Bohrungsliste; nichts, wenn das Gutachten keine Sondierungen hat. */
export function sondierungListe() {
  const alle = S.z?.sondierungen ?? [];
  if (!alle.length) return nothing;
  const [gep, ges] = S.z!.pruefstand.sondierungen ?? [0, 0];
  return html`
    <h4 class="sondierungen-kopf">Sondierungen <span class="leise klein">${gep}/${ges} geprüft</span> ${hilfe("sondierungen")}</h4>
    <ul class="bliste" role="listbox" aria-label="Sondierungen">
      ${alle.map((s) => html`
        <li role="option" aria-selected=${String(s.id === gewaehlt)} class=${`${s.id === gewaehlt ? "aktiv" : ""} ${s.entfernt ? "raus" : ""}`}
          @click=${() => waehlen(s.id)}>
          ${zeichen(s)}
          <span class="name">${s.code}</span>
          <span class="wert klein">${s.art}${s.werte_n ? ` · ${s.werte_n}` : ""}</span>
        </li>`)}
    </ul>`;
}

function werteVon(w: SondierungWert): [number, number, number | null, boolean] {
  const v = w[2] as number | { wert: number; zensiert: boolean } | null;
  if (v && typeof v === "object") return [Number(w[0]), Number(w[1]), v.wert, v.zensiert];
  return [Number(w[0]), Number(w[1]), v === null || v === undefined ? null : Number(v), false];
}

/** Kurve: DPH als Treppe N10 über der Tiefe, CPT q_c (und f_s, wenn da) als Linien. */
function kurve(s: Sondierung, d: SondierungDetail) {
  const B = 300, H = 420, L = 34, O = 22;
  const dph = s.art.toUpperCase().startsWith("DP") || s.art.toUpperCase() === "SRS";
  const tmax = Math.max(s.endtiefe ?? 0, ...d.werte.map((w) => Number(dph ? w[1] : w[0]) || 0), 1);
  const y = (t: number) => O + (t / tmax) * (H - O - 6);
  if (dph) {
    const st = d.werte.map(werteVon);
    const nmax = Math.ceil(Math.max(10, ...st.map((x) => x[2] ?? 0)) / 10) * 10;   // runde Achse: 10, 20, 30 …
    const x = (n: number) => L + (n / nmax) * (B - L - 8);
    const pfad = st.map(([o, u, n]) => n === null ? "" : `M${x(n)},${y(o)} V${y(u)}`).join(" ");
    const verbinder = st.slice(1).map(([o, , n], i) => n === null || st[i][2] === null ? "" : `M${x(st[i][2]!)},${y(o)} H${x(n)}`).join(" ");
    return svg`<svg class="sondierung-kurve" viewBox=${`0 0 ${B} ${H}`} role="img" aria-label=${`${s.code}: N10 über der Tiefe`}>
      ${Array.from({ length: nmax / (nmax > 60 ? 20 : 10) + 1 }, (_, i) => i * (nmax > 60 ? 20 : 10)).map((n) => svg`
        <line x1=${x(n)} x2=${x(n)} y1=${O} y2=${H - 6} class="gitter"/>
        <text x=${x(n)} y=${O - 6} text-anchor="middle">${n}</text>`)}
      ${Array.from({ length: Math.floor(tmax) + 1 }, (_, m) => svg`<text x=${L - 4} y=${y(m) + 3} text-anchor="end">${m}</text>`)}
      <path d=${`${pfad} ${verbinder}`} class="treppe"/>
      ${st.filter((x_) => x_[3]).map(([o, u, n]) => svg`<text x=${x(n ?? 0) + 3} y=${(y(o) + y(u)) / 2 + 3} class="zensiert">&gt;</text>`)}
      <text x=${L} y=${H - 2} class="achse">N10 [Schläge/10 cm] · Tiefe [m]</text>
    </svg>`;
  }
  const pkt = d.werte.map((w) => [Number(w[0]), w[1] === null ? null : Number(w[1]), w[2] === null || w[2] === undefined ? null : Number(w[2])] as const);
  const qmax = Math.max(1, ...pkt.map((p) => p[1] ?? 0));
  const fmax = Math.max(1, ...pkt.map((p) => p[2] ?? 0));
  const xq = (q: number) => L + (q / qmax) * (B - L - 8);
  const xf = (f: number) => L + (f / fmax) * (B - L - 8);
  const linie = (xs: (v: number) => number, i: 1 | 2) =>
    pkt.filter((p) => p[i] !== null).map((p, k) => `${k ? "L" : "M"}${xs(p[i] as number)},${y(p[0])}`).join(" ");
  return svg`<svg class="sondierung-kurve" viewBox=${`0 0 ${B} ${H}`} role="img" aria-label=${`${s.code}: q_c über der Tiefe`}>
    ${Array.from({ length: Math.floor(tmax) + 1 }, (_, m) => svg`<text x=${L - 4} y=${y(m) + 3} text-anchor="end">${m}</text>`)}
    <path d=${linie(xq, 1)} class="qc"/><path d=${linie(xf, 2)} class="fs"/>
    <text x=${L} y=${O - 6} class="achse">q_c bis ${zahl(qmax, 1)}</text>
    <text x=${B - 8} y=${O - 6} text-anchor="end" class="achse fs">f_s bis ${zahl(fmax, 1)}</text>
  </svg>`;
}

function feld(titel: string, inhalt: unknown, zusatz: unknown = nothing) {
  return html`<label class="feld"><span>${titel}</span>${inhalt}${zusatz}</label>`;
}

async function seiteHolen(s: Sondierung) {
  if (s.seite === null || !S.z?.dokumente[s.dokument_index]?.pdf) return;
  const schluessel = `${S.sig}/${s.dokument_index}/${s.seite}`;
  if (seite?.schluessel === schluessel || laedt === schluessel) return;
  laedt = schluessel;
  const d = await versuchen(() => api.seite(S.sig, s.dokument_index, s.seite! - 1));
  laedt = "";
  if (d) { seite = { schluessel, daten: d }; neu(); }
}

function quelle(s: Sondierung, d: SondierungDetail | undefined) {
  void seiteHolen(s);
  const sb = seite?.schluessel === `${S.sig}/${s.dokument_index}/${s.seite}` ? seite.daten : null;
  const bb = d?.beleg?.bbox;
  return html`
    <aside class="quelle-spalte">
      <div class="saeule-rahmen">${d ? kurve(s, d) : html`<p class="leise klein">Werte werden geladen …</p>`}</div>
      ${!S.z?.dokumente[s.dokument_index]?.pdf || s.seite === null ? nothing : html`<div class="pdf-rahmen">
        <div class="pdf-kopf"><b>Quelle im PDF</b> <span class="leise klein">S. ${s.seite}</span>
          <span class="fueller"></span>
          <button class="symbol" title="kleiner" @click=${() => { zoom = Math.max(0.25, zoom / 1.4); neu(); }}>−</button>
          <button class="symbol" title="größer" @click=${() => { zoom = Math.min(1.5, zoom * 1.4); neu(); }}>+</button>
        </div>
        ${!sb ? html`<p class="leise klein">Seite wird geladen …</p>` : html`
          <div class="pdf-seite">
            <div class="pdf-flaeche" style=${`width:${sb.breite_pt * sb.px_je_pt * zoom}px;height:${sb.hoehe_pt * sb.px_je_pt * zoom}px`}>
              <img src=${sb.url} alt=${`Seite ${s.seite}`} draggable="false">
              ${bb && bb.length === 4 ? html`<div class="bbox saeule-bbox" style=${`left:${bb[0] * sb.px_je_pt * zoom}px;top:${bb[1] * sb.px_je_pt * zoom}px;width:${(bb[2] - bb[0]) * sb.px_je_pt * zoom}px;height:${(bb[3] - bb[1]) * sb.px_je_pt * zoom}px`}></div>` : nothing}
            </div>
          </div>`}
      </div>`}
    </aside>`;
}

/** Mitte und rechte Spalte, wenn eine Sondierung gewählt ist. */
export function sondierungDetail() {
  const s = sondierungGewaehlt();
  if (!s) return null;
  const d = details.get(s.id);
  if (!d) void laden(s.id);
  const zahlFeld = (f: "gok" | "x" | "y", v: number | null, schritt: string) => html`<input type="number" step=${schritt}
    .value=${live(v === null ? "" : String(v))} @change=${(e: Event) => setzen(s, f, (e.target as HTMLInputElement).value.trim() || null)}>`;
  return html`
    <section class="bohrung-detail sondierung-detail">
      <div class="kopfzeile">
        <h3>${s.code} <span class="leise klein">${s.art} · ${s.form}${s.seite ? ` · S. ${s.seite}` : ""} · ${s.dokument}</span></h3>
      </div>
      <div class="felder">
        ${feld("GOK [m NHN]", zahlFeld("gok", s.gok, "0.01"), html`<span class="leise klein">${s.gok_quelle}</span>`)}
        ${feld("Endtiefe [m]", html`<output>${zahl(s.endtiefe)}</output>`, html`<span class="leise klein">${s.endtiefe_aus}</span>`)}
        ${feld("Rechtswert", zahlFeld("x", s.x, "0.01"))}
        ${feld("Hochwert", zahlFeld("y", s.y, "0.01"), s.lage_aus ? html`<span class="leise klein">${s.lage_aus}</span>` : nothing)}
        ${feld("Werte", html`<output>${s.werte_n}${s.n10_max !== null ? ` · N10 max ${s.n10_max}` : ""}${s.zensiert ? ` · ${s.zensiert} über der Achse` : ""}</output>`)}
        ${feld("Quelle", html`<output>${s.quelle}${s.konfidenz !== null ? ` · Konfidenz ${zahl(s.konfidenz)}` : ""}</output>`)}
      </div>
      ${s.hinweise.length ? html`<p class="hinweise">ℹ ${s.hinweise.join(" · ")}</p>` : nothing}
      <p class="klein leise">Lage: Rechts-/Hochwert eingeben oder im Schritt Lage einen Punkt auf dem gesperrten Plan setzen.
        Die Werte bleiben, wie sie im PDF stehen.</p>
      <div class="detail-fuss">
        <button class="primaer" ?disabled=${s.geprueft || s.entfernt} @click=${() => setzen(s, "geprueft", true)}>✓ Geprüft</button>
        <button class="leise-knopf" ?disabled=${!s.geprueft} @click=${() => setzen(s, "geprueft", false)}>Prüfung zurücknehmen</button>
        <span class="fueller"></span>
        ${s.entfernt
          ? html`<button @click=${() => setzen(s, "modell", true)}>wiederherstellen</button>`
          : html`<button class="gefahr" @click=${() => setzen(s, "modell", false)}>🗑 Aus dem Projekt entfernen</button>`}
      </div>
    </section>
    ${quelle(s, d)}`;
}
