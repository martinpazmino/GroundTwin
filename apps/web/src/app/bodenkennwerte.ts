// Bodenkennwerte aus dem Gutachten (Issue #18): Kennwert-Tabellen des Berichts je Einheit zuordnen. Ein Vorschlag nach
// Name, Bodenart und Bodengruppe wird mit einem Klick übernommen; danach je Einheit änderbar. Die Werte gehen als
// CPset_Bodenkennwerte_Gutachten (<Kennwert>_min/_max) ins IFC. Eingeklappt, offen mit Zuordnung.
import { html, nothing } from "lit";
import { live } from "lit/directives/live.js";
import { api, type Bodenkennwerte } from "./api";
import { hilfe } from "./hilfe";
import { S, aendern, neu, versuchen } from "./store";

const NAMEN: Record<string, string> = {
  wichte: "γ [kN/m³]", wichte_auftrieb: "γ′ [kN/m³]", reibungswinkel: "φ′ [°]", kohaesion: "c′ [kN/m²]",
  kohaesion_undrainiert: "cu [kN/m²]", steifemodul: "Es [MN/m²]",
};
let daten: Bodenkennwerte | null = null;
let fuer = "";
let auf: boolean | null = null;

async function holen() {
  const sig = S.sig;
  if (!sig) return;
  const kennung = `${sig}|${S.modell?.schluessel ?? ""}|${JSON.stringify(S.z?.bodenkennwerte ?? {})}`;
  if (fuer === kennung) return;
  fuer = kennung;
  daten = (await versuchen(() => api.bodenkennwerte(sig))) ?? null;
  neu();
}

function setzen(z: Record<string, string> | null) {
  return aendern([{ op: "bodenkennwerte", zuordnung: z }]);
}

const zahl = (x: number) => x.toLocaleString("de-DE", { maximumFractionDigits: 2 });

function werteText(w: Bodenkennwerte["zeilen"][number]["werte"]) {
  return Object.entries(w).map(([k, v]) => html`<span class="kw" title=${v.text}>${NAMEN[k] ?? k}
    ${v.min !== undefined ? (v.min === v.max ? zahl(v.min) : `${zahl(v.min)}–${zahl(v.max!)}`) : v.text}${v.hinweis ? " ⚑" : ""}</span>`);
}

/** Abschnitt im Schritt Einheiten (linke Spalte), nur wenn das Gutachten Kennwert-Tabellen hat. */
export function bodenkennwerteTeil() {
  if (!S.modell?.bericht) return nothing;
  void holen();
  const d = daten && !daten.fehler ? daten : null;
  if (!d || !d.zeilen.length) return nothing;
  const z = S.z?.bodenkennwerte ?? {};
  const offen = auf ?? Object.keys(z).length > 0;
  const vorschlag = Object.fromEntries(Object.entries(d.vorschlag).filter(([, v]) => v.ref).map(([e, v]) => [e, v.ref!]));
  const zeile = (ref: string) => d.zeilen.find((r) => r.ref === ref);
  return html`
    <details class="erweitert karte bodenkennwerte" .open=${live(offen)}
      @toggle=${(ev: Event) => { auf = (ev.target as HTMLDetailsElement).open; neu(); }}>
      <summary>Bodenkennwerte aus dem Gutachten <span class="leise klein">${d.zeilen.length} Zeilen${
        Object.keys(z).length ? `, ${Object.keys(z).length} zugeordnet` : ""}</span></summary>
      <p class="klein leise">Werte des Gutachters (Tabelle im Bericht), nicht von GroundTwin festgelegt.
        ${hilfe("bodenkennwerte")}</p>
      ${!Object.keys(z).length && Object.keys(vorschlag).length ? html`
        <div class="hb-vorschlag"><p class="klein"><b>Vorschlag</b></p>
          <table class="tabelle kompakt"><tbody>${d.einheiten.map((e) => html`<tr><td><b>${e}</b></td>
            <td>${d.vorschlag[e]?.ref ? zeile(d.vorschlag[e].ref!)?.bezeichnung || "(ohne Bezeichnung)" : "–"}</td>
            <td class="leise klein">${d.vorschlag[e]?.grund ?? ""}</td></tr>`)}</tbody></table>
          <button @click=${() => setzen(vorschlag)}>Vorschlag übernehmen</button>
        </div>` : nothing}
      <table class="tabelle kompakt">
        <thead><tr><th>Einheit</th><th>Zeile im Gutachten</th></tr></thead>
        <tbody>${d.einheiten.map((e) => html`<tr><td>${e}</td><td>
          <select @change=${(ev: Event) => {
            const v = (ev.target as HTMLSelectElement).value;
            const neu_ = { ...z };
            if (v) neu_[e] = v; else delete neu_[e];
            void setzen(Object.keys(neu_).length ? neu_ : null);
          }}>
            <option value="" .selected=${!z[e]}>– keine –</option>
            ${d.zeilen.map((r) => html`<option value=${r.ref} .selected=${z[e] === r.ref}>
              S. ${r.seite + 1}: ${(r.bezeichnung || "(ohne Bezeichnung)").slice(0, 60)}</option>`)}
          </select>
          ${z[e] && zeile(z[e]) ? html`<div class="klein">${werteText(zeile(z[e])!.werte)}</div>` : nothing}
        </td></tr>`)}</tbody>
      </table>
      <details class="klein"><summary>Alle Zeilen aus dem Gutachten</summary>
        <table class="tabelle kompakt"><tbody>${d.zeilen.map((r) => html`<tr>
          <td class="leise">S. ${r.seite + 1}</td><td>${r.bezeichnung || "(ohne Bezeichnung)"}</td>
          <td>${werteText(r.werte)}${r.hinweise.length ? html`<div class="leise">⚑ ${r.hinweise.join("; ")}</div>` : nothing}</td>
        </tr>`)}</tbody></table>
      </details>
    </details>`;
}
