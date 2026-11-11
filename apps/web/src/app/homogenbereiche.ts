// Homogenbereiche nach VOB/C (docs/28): Einheiten je Gewerk (ATV) zu Homogenbereichen zusammenfassen, die Kennwerte
// zeigen, die die ATV verlangt, und das IFC wahlweise nur aus Homogenbereichen schreiben. Eingeklappt, offen mit Daten.
import { html, nothing } from "lit";
import { live } from "lit/directives/live.js";
import { api, type HbDaten } from "./api";
import { hilfe } from "./hilfe";
import { S, aendern, neu, versuchen } from "./store";

let daten: HbDaten | null = null;
let laedt = false;
let atv = "DIN 18300";
let auf: boolean | null = null;                   // vom Nutzer auf-/zugeklappt; null = offen, wenn Daten da sind

async function laden() {
  if (daten || laedt) return;
  laedt = true;
  daten = (await versuchen(() => api.homogenbereicheDaten())) ?? null;
  laedt = false;
  neu();
}

function setzen(zuordnung: Record<string, string> | null) {
  return aendern([{ op: "homogenbereiche", atv, zuordnung }]);
}

/** Abschnitt im Schritt Einheiten (linke Spalte). */
export function homogenbereicheTeil() {
  const b = S.modell?.bericht;
  if (!b) return nothing;
  const alle = S.z?.homogenbereiche ?? {};
  const je = alle[atv] ?? {};
  const einheiten = b.einheiten.map((e) => e.name);
  const offen = auf ?? Object.keys(alle).length > 0;
  if (offen) void laden();
  const kw = daten ? daten.kennwerte.filter((k) => daten!.matrix[atv]?.[k.nr]) : [];
  // Bereiche in Modellreihenfolge mit ihren Einheiten
  const bereiche: { name: string; einheiten: string[] }[] = [];
  for (const e of einheiten) {
    const n = je[e];
    if (!n) continue;
    let g = bereiche.find((x) => x.name === n);
    if (!g) bereiche.push((g = { name: n, einheiten: [] }));
    g.einheiten.push(e);
  }
  const fremd = Object.keys(je).filter((e) => !einheiten.includes(e));
  const ohne = einheiten.filter((e) => !je[e]);
  return html`
    <details class="erweitert karte homogenbereiche" .open=${live(offen)}
      @toggle=${(ev: Event) => { auf = (ev.target as HTMLDetailsElement).open; if (auf) void laden(); }}>
      <summary>Homogenbereiche (VOB/C) <span class="leise klein">${Object.keys(alle).length
        ? Object.keys(alle).join(", ") : "Einheiten je Gewerk zuordnen"}</span></summary>
      <div class="einstellung">
        <span>Gewerk (ATV) ${hilfe("homogenbereiche")}</span>
        <select @change=${(e: Event) => { atv = (e.target as HTMLSelectElement).value; neu(); }}>
          ${(daten?.atv ?? [{ code: "DIN 18300", gewerk: "Erdarbeiten" }]).map((a) => html`
            <option value=${a.code} .selected=${a.code === atv}>${a.code} ${a.gewerk}${alle[a.code] ? " ✓" : ""}</option>`)}
        </select>
      </div>
      <table class="tabelle kompakt hb-zuordnung">
        <thead><tr><th>Einheit</th><th>Homogenbereich</th></tr></thead>
        <tbody>${b.einheiten.map((e) => html`<tr>
          <td><span class="farbfeld" style=${`background:${e.farbe}`}></span> ${e.name}</td>
          <td><input class="kurz" list="hb-namen" placeholder="–" .value=${live(je[e.name] ?? "")}
            @change=${(ev: Event) => {
              const w = (ev.target as HTMLInputElement).value.trim();
              const neuJe = { ...je };
              if (w) neuJe[e.name] = w; else delete neuJe[e.name];
              void setzen(Object.keys(neuJe).length ? neuJe : null);
            }}></td></tr>`)}</tbody>
      </table>
      <datalist id="hb-namen">${bereiche.map((g) => html`<option value=${g.name}></option>`)}</datalist>
      <div class="zeile knopfzeile">
        <button class="link" @click=${() => setzen(Object.fromEntries(einheiten.map((e, i) => [e, `B${i + 1}`])))}
          title="Je Einheit ein eigener Bereich (B1, B2, … von oben); zusammenfassen durch gleiche Namen">Vorschlag: je Einheit ein Bereich</button>
        ${Object.keys(je).length ? html`<button class="link" @click=${() => setzen(null)}>Zuordnung ${atv} löschen</button>` : nothing}
      </div>
      ${fremd.length ? html`<p class="warn klein">Zugeordnet, aber nicht mehr im Modell: ${fremd.join(", ")}</p>` : nothing}
      ${bereiche.length ? html`
        <p class="klein">${bereiche.map((g) => html`<b>${g.name}</b>: ${g.einheiten.join(", ")}<br>`)}
          ${ohne.length ? html`<span class="warn">ohne Bereich: ${ohne.join(", ")}</span>` : nothing}</p>` : nothing}
      ${kw.length ? html`
        <h4>Kennwerte für ${atv} (${kw.length})</h4>
        <ul class="klein hb-kennwerte">${kw.map((k) => {
          const art = daten!.matrix[atv][k.nr];
          return html`<li>${k.nr} ${k.name}${art !== "erforderlich" ? html` <span class="leise">(${art})</span>` : nothing}</li>`;
        })}</ul>
        <p class="leise klein">Die Werte stehen im Gutachten; das IFC nennt je Bereich, welche anzugeben sind.
          Quelle der Matrix: ${daten!.quelle}</p>` : nothing}
      <div class="einstellung">
        <span>IFC-Modell</span>
        <label class="inline"><input type="radio" name="hb-modell" .checked=${!S.z?.hb_modell}
          @change=${() => aendern([{ op: "hb_modell", wert: null }])}> Einheiten</label>
        ${Object.keys(alle).map((c) => html`<label class="inline"><input type="radio" name="hb-modell"
          .checked=${S.z?.hb_modell === c} @change=${() => aendern([{ op: "hb_modell", wert: c }])}>
          Homogenbereiche ${c}</label>`)}
      </div>
      <p class="leise klein">Mit Einheiten trägt jede Einheit und jede Bodenschicht der Bohrsäulen ein Pset je ATV
        (CPset_Homogenbereich_…). Mit Homogenbereichen besteht das Modell aus den Bereichen (gleiche Körper, je Bereich
        zusammengefasst).</p>
    </details>`;
}
