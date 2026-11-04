// Karte als Pop-up (docs/21 §4.7): nur zum Orientieren - ein Klick setzt den Standort. Hintergrund basemap.de (BKG,
// amtlich, CC BY 4.0) oder OpenStreetMap; Leaflet und die Kacheln laden erst, wenn die Karte aufgeht (der Ausschnitt
// geht dann an diesen Server). Den Punkt rechnet der Server nach ETRS89/UTM um (geodaten/utm.py, gegen PROJ < 1 mm)
// und sagt, was die Dienste der Laender dort liefern.
import { api, type StandortPunkt } from "./api";

const BASEMAP = "https://sgx.geodatenzentrum.de/wmts_basemapde/tile/1.0.0/de_basemapde_web_raster_farbe/default/" +
  "GLOBAL_WEBMERCATOR/{z}/{y}/{x}.png";
const OSM = "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
const DEUTSCHLAND: [number, number] = [51.16, 10.45];

let zuletzt: { laenge: number; breite: number; zoom: number } | null = null;    // naechstes Oeffnen: dort weiter

const text = (s: string) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);
const zahl = (v: number) => v.toLocaleString("de-DE", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

/** Karte oeffnen; Rueckgabe der gewaehlte Punkt (Uebernehmen) oder null (Abbrechen, Esc). */
export async function karteWaehlen(): Promise<StandortPunkt | null> {
  const [{ default: L }] = await Promise.all([import("leaflet"), import("leaflet/dist/leaflet.css")]);
  return new Promise((fertig) => {
    const dlg = document.createElement("dialog");
    dlg.className = "karte-dialog";
    dlg.setAttribute("aria-label", "Standort auf der Karte wählen");
    dlg.innerHTML = `
      <header><strong>Standort auf der Karte wählen</strong>
        <button type="button" class="symbol schliessen" aria-label="Karte schließen">✕</button></header>
      <div class="karte-flaeche"></div>
      <footer>
        <div class="karte-info klein" aria-live="polite">In die Karte klicken: der Punkt wird der Standort (zum Orientieren,
          auf wenige Meter genau). Mausrad zoomt, Ziehen verschiebt.</div>
        <div class="zeile"><span class="fueller"></span>
          <button type="button" class="abbrechen">Abbrechen</button>
          <button type="button" class="primaer uebernehmen" disabled>Punkt übernehmen</button></div>
      </footer>`;
    document.body.append(dlg);
    dlg.showModal();
    const info = dlg.querySelector<HTMLDivElement>(".karte-info")!;
    const uebernehmen = dlg.querySelector<HTMLButtonElement>(".uebernehmen")!;
    const karte = L.map(dlg.querySelector<HTMLDivElement>(".karte-flaeche")!, { zoomControl: true, attributionControl: true })
      .setView(zuletzt ? [zuletzt.breite, zuletzt.laenge] : DEUTSCHLAND, zuletzt?.zoom ?? 6);
    const jahr = new Date().getFullYear();
    const basemap = L.tileLayer(BASEMAP, {
      maxZoom: 18, attribution: `© <a href="https://basemap.de" target="_blank" rel="noopener">GeoBasis-DE / BKG (${jahr})</a> ` +
        `<a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>` }).addTo(karte);
    const osm = L.tileLayer(OSM, {
      maxZoom: 19, attribution: `© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap-Mitwirkende</a>` });
    L.control.layers({ "basemap.de (BKG)": basemap, "OpenStreetMap": osm }, {}, { position: "topright" }).addTo(karte);
    L.control.scale({ imperial: false }).addTo(karte);
    const marke = L.circleMarker(DEUTSCHLAND, { radius: 8, color: "#10210a", weight: 2, fillColor: "#a2c513", fillOpacity: 0.95 });
    let punkt: StandortPunkt | null = null;
    let nr = 0;

    karte.on("click", async (ev) => {
      const meine = ++nr;
      marke.setLatLng(ev.latlng).addTo(karte);
      punkt = null;
      uebernehmen.disabled = true;
      info.textContent = "wird umgerechnet …";
      try {
        const p = await api.standortPunkt(Number(ev.latlng.lng.toFixed(7)), Number(ev.latlng.lat.toFixed(7)));
        if (meine !== nr) return;                                    // inzwischen woanders geklickt
        punkt = p;
        uebernehmen.disabled = false;
        info.innerHTML = `<b>Rechtswert ${zahl(p.x)} · Hochwert ${zahl(p.y)} · EPSG:${p.epsg}</b>
          <ul class="dienste">${p.dienste.map((d) => `<li class="${d.art}">${text(d.text)}</li>`).join("")}</ul>
          <span class="leise">Gebiete der Dienste als Rechteck: nahe einer Landesgrenze ohne Gewähr.</span>`;
      } catch (err) {
        if (meine !== nr) return;
        info.innerHTML = `<span class="warnung">${text((err as Error).message)}</span>`;
      }
    });

    const ende = (wert: StandortPunkt | null) => {
      const m = karte.getCenter();
      zuletzt = wert ? { laenge: wert.laenge, breite: wert.breite, zoom: Math.max(karte.getZoom(), 14) }
        : { laenge: m.lng, breite: m.lat, zoom: karte.getZoom() };
      karte.remove();
      dlg.close();
      dlg.remove();
      fertig(wert);
    };
    dlg.querySelector(".schliessen")!.addEventListener("click", () => ende(null));
    dlg.querySelector(".abbrechen")!.addEventListener("click", () => ende(null));
    uebernehmen.addEventListener("click", () => ende(punkt));
    dlg.addEventListener("cancel", (ev) => { ev.preventDefault(); ende(null); });   // Esc
    requestAnimationFrame(() => karte.invalidateSize());                           // Groesse erst nach showModal bekannt
  });
}
