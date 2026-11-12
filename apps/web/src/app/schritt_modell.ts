// Schritt 5 · Modell: das Baugrundmodell im Viewer (Vollbild), rechts Pruefstand, Einchecken, Export und Hinweise.
import { analyseViewerTeil } from "./analyse";
import { html, nothing } from "lit";
import { api, type GeoldgFrist } from "./api";
import { hilfe } from "./hilfe";
import { S, aendern, gehe, modellRechnen, versuchen, zustandUebernehmen, neu, melden } from "./store";

let kommentar = "";

async function einchecken() {
  const r = await versuchen(() => api.einchecken(S.sig, kommentar));
  if (r) {
    zustandUebernehmen(r.zustand);
    kommentar = "";
    melden(`Eingecheckt: v${r.eintrag.nr} · ${r.eintrag.stand.bohrungen[0]}/${r.eintrag.stand.bohrungen[1]} Bohrungen geprüft`, "ok");
    neu();
  }
}

// BoreholeML (docs/23 §2.1): nur vollstaendig gepruefte Bohrungen mit ETRS89/UTM und GOK; Organisation des Absenders
const UTM = new Set([25831, 25832, 25833, 4647, 5650]);
let organisation = (() => { try { return localStorage.getItem("groundtwin.organisation") ?? ""; } catch { return ""; } })();

function boreholemlTeil() {
  const z = S.z!;
  const imModell = z.bohrungen.filter((b) => b.modell);
  const bereit = imModell.filter((b) => b.schichten_n > 0 && b.schichten_geprueft === b.schichten_n && b.x !== null && b.y !== null &&
    b.epsg !== null && UTM.has(b.epsg) && b.gok !== null && z.lage_modus === "koordinaten");
  const url = `${api.exportUrl(S.sig, "boreholeml")}?organisation=${encodeURIComponent(organisation)}`;
  return html`
    <label class="feld breit"><span>Organisation (Absender) ${hilfe("boreholeml")}</span>
      <input type="text" aria-label="Organisation für BoreholeML" placeholder="z. B. Ingenieurbüro …" .value=${organisation}
        @input=${(ev: Event) => { organisation = (ev.target as HTMLInputElement).value;
                                  try { localStorage.setItem("groundtwin.organisation", organisation); } catch { /* ohne Speicher */ }
                                  neu(); }}></label>
    ${bereit.length ? html`<a class="knopf" href=${url} download>Bohrungen für den Geologischen Dienst (BoreholeML 3.2)</a>`
      : html`<span class="knopf aus" title="Erst alle Schichten prüfen; Lage in ETRS89/UTM und GOK nötig">Bohrungen für den Geologischen Dienst (BoreholeML 3.2)</span>`}
    <p class="leise klein">${bereit.length} von ${imModell.length} Bohrungen exportierbar (vollständig geprüft, ETRS89/UTM, GOK).</p>`;
}

// 3D Tiles fuer Cesium (D87): per fetch, damit ein Fehler (Lage ohne UTM, Quasigeoid ohne Netz) als Meldung kommt
let tilesLaeuft = false;

async function dreiDTiles() {
  if (tilesLaeuft) return;
  tilesLaeuft = true;
  neu();
  try {
    const r = await fetch(api.exportUrl(S.sig, "3dtiles"));
    if (!r.ok) {
      const text = await r.text();
      let detail = text;
      try { detail = JSON.parse(text).detail ?? text; } catch { /* kein JSON */ }
      melden(`3D Tiles: ${detail}`, "fehler", 10000);
      return;
    }
    const name = /filename\*=UTF-8''([^;]+)/.exec(r.headers.get("content-disposition") ?? "")?.[1];
    const a = document.createElement("a");
    a.href = URL.createObjectURL(await r.blob());
    a.download = name ? decodeURIComponent(name) : "baugrundmodell_3dtiles.zip";
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 10000);
    melden("3D Tiles exportiert (tileset.json + GLB, Höhen ellipsoidisch mit GCG2016).", "ok");
  } finally {
    tilesLaeuft = false;
    neu();
  }
}

function tilesTeil() {
  const z = S.z!;
  const bereit = z.lage_modus === "koordinaten" && z.viewer.epsg !== null && UTM.has(z.viewer.epsg);
  return bereit
    ? html`<button class="knopf" ?disabled=${tilesLaeuft} @click=${dreiDTiles}>${tilesLaeuft ? "3D Tiles werden erstellt …"
        : "Baugrundmodell für Cesium (3D Tiles, ZIP)"}</button>${hilfe("tiles3d")}`
    : html`<span class="knopf aus" title="Nur mit Lage nach Koordinaten in ETRS89/UTM">Baugrundmodell für Cesium (3D Tiles, ZIP)</span>`;
}

// GeolDG (docs/21 §5.3): Fristen aus Beginn und Abschluss der Untersuchung, je eigene Bohrung was die App liefert,
// das Paket fuer den Geologischen Dienst (Fachdaten BoreholeML, Bewertungsdaten Modell + Dokumentation, Pruefliste)
const FRIST: Record<GeoldgFrist["id"], string> = { anzeige: "Anzeige", fachdaten: "Fachdaten", bewertungsdaten: "Bewertungsdaten" };
const datumDe = (iso: string) => iso.split("-").reverse().join(".");

function fristText(f: GeoldgFrist) {
  if (!f.bis || f.tage === null) return f.regel;
  return `bis ${datumDe(f.bis)} (${f.tage > 0 ? `noch ${f.tage} Tage` : f.tage === 0 ? "heute" : "verstrichen"})`;
}

function geoldgTeil() {
  const g = S.z!.geoldg;
  const zs = g.zusammenfassung;
  const setzen = (feld: "beginn" | "abschluss" | "behoerde", wert: string | boolean) =>
    aendern([{ op: "geoldg", [feld]: wert }], { leise: true });
  const url = `${api.exportUrl(S.sig, "geoldg")}?organisation=${encodeURIComponent(organisation)}`;
  const protokoll = g.punkte.filter((p) => p.quelle === "protokoll").map((p) => p.titel.replace(/, falls durchgeführt$/, ""));
  return html`
    <section class="abschnitt-flach geoldg">
      <h3>Geologischer Dienst (GeolDG) ${hilfe("geoldg")}</h3>
      <div class="zeile">
        <label class="inline">Beginn <input type="date" aria-label="Beginn der Untersuchung" .value=${g.angaben.beginn}
          @change=${(e: Event) => setzen("beginn", (e.target as HTMLInputElement).value)}></label>
        <label class="inline">Abschluss <input type="date" aria-label="Abschluss der Untersuchung" .value=${g.angaben.abschluss}
          @change=${(e: Event) => setzen("abschluss", (e.target as HTMLInputElement).value)}></label>${hilfe("geoldg_abschluss")}
      </div>
      <label class="inline"><input type="checkbox" aria-label="Auftraggeber ist eine Behörde" .checked=${g.angaben.behoerde}
        @change=${(e: Event) => setzen("behoerde", (e.target as HTMLInputElement).checked)}> Auftraggeber ist eine Behörde</label>
      <ul class="fristen">${g.fristen.map((f) => html`
        <li class=${f.tage !== null && f.tage < 0 ? "warn" : ""} data-frist=${f.id}><b>${FRIST[f.id]}</b>
          <a href=${f.url} target="_blank" rel="noopener">${f.beleg}</a>: ${fristText(f)}</li>`)}</ul>
      ${g.vorerkundung ? html`
        <p class="klein">Noch keine eigene Bohrung: die geplante Erkundung spätestens zwei Wochen vor Beginn anzeigen
          (<a href=${g.anzeige_inhalt.url} target="_blank" rel="noopener">§ 8</a>). ${g.anzeige_inhalt.aus_der_app}</p>`
      : zs.eigene ? html`
        <p class="klein geoldg-stand">${zs.eigene} eigene Bohrungen: für <b>${zs.bereit}</b> liefert GroundTwin Lage, GOK, Endteufe
          und das geprüfte Schichtenverzeichnis, <b>${zs.boreholeml}</b> davon im BoreholeML.${zs.fremd
          ? ` ${zs.fremd} Bohrungen der Länder liegen dem Land schon vor.` : ""}</p>
        ${zs.offen.length ? html`<details class="protokoll"><summary class="warnung">⚠ ${zs.offen.length} Bohrung(en) offen</summary>
          <ul>${zs.offen.map((o) => html`<li><b>${o.code}</b>: ${o.was}</li>`)}</ul></details>` : nothing}
        <p class="klein leise">Aus dem Bohrprotokoll ergänzen (Spalten in pruefliste.csv): ${protokoll.join(" · ")}.</p>
        <a class="knopf" href=${url} download>Paket für den Geologischen Dienst (ZIP)</a>` : nothing}
      <p class="leise klein">${g.quelle.hinweis}</p>
    </section>`;
}

let erweitertAuf = false;                       // vom Nutzer geöffnet (bleibt beim Neuzeichnen)

export function schrittModell() {
  const z = S.z!;
  const m = S.modell;
  const b = m?.bericht;
  const st = z.pruefstand;
  const letzter = z.eincheckungen[z.eincheckungen.length - 1];
  // vorn das Modell (IFC) und der Prüfbericht; alle weiteren Ausgaben unter „Erweitert“
  const exporte: [string, string][] = [["ifc", "Baugrundmodell (IFC 4.3)"], ["bericht", "Prüfbericht (JSON)"]];
  const weitere: [string, string][] = [["einheiten", "Einheiten-Vorlage (JSON)"], ["extraktion", "Extraktion (JSON)"],
    ["eingabe", "Modell-Eingabe mit Korrekturen (JSON)"], ["projekt", "Projektstand (JSON)"]];
  const erweitert = erweitertAuf || !!(z.geoldg?.angaben.beginn || z.geoldg?.angaben.abschluss);   // GeolDG in Arbeit
  return html`
    <div class="app-panel rechts">
      <section class="abschnitt-flach">
        <h3>Modell</h3>
        ${z.reifegrad.stufe !== "Gutachten" ? html`<p class=${`reife ${z.reifegrad.stufe === "Vorerkundung" ? "vorerkundung" : "gemischt"}`}>
          <b>${z.reifegrad.stufe}</b> – ${z.reifegrad.stufe === "Vorerkundung"
            ? "Bohrungen aus Datenbanken der Länder, kein Gutachten: eine erste Vorstellung für die Planung der Erkundung."
            : Object.entries(z.reifegrad.anzahl).map(([h, n]) => `${n} ${h}`).join(", ") + ": Bohrungen ohne Gutachten sind nicht gegen ein PDF geprüft."}
          ${hilfe("reifegrad")}</p>` : nothing}
        ${S.rechnet ? html`<p><span class="kreisel klein"></span> wird gerechnet …</p>` : nothing}
        ${m?.fehler ? html`<p class="warnung">Noch kein Modell: ${m.fehler}</p>
          <button class="link" @click=${() => gehe("lage")}>→ Lage setzen</button>` : nothing}
        ${b ? html`
          <ul class="kennzahlen">
            <li><b>${b.einheiten.length}</b> Einheiten</li>
            <li><b>${b.bohrungen.length}</b> Bohrungen im Modell</li>
            <li class=${b.epsg ? "" : "warn"}>${b.epsg ? `EPSG:${b.epsg}` : "lokales System"}</li>
            <li class=${b.pruefungen.alle_koerper_geschlossen ? "ok" : "warn"}>${b.pruefungen.alle_koerper_geschlossen ? "Körper geschlossen" : "Körper offen"}</li>
            <li class=${b.pruefungen.max_abweichung_an_bohrungen_m < 0.01 ? "ok" : "warn"}>Abweichung an Bohrungen ${b.pruefungen.max_abweichung_an_bohrungen_m.toFixed(3)} m</li>
          </ul>` : nothing}
        <div class="zeile">
          <label class="inline"><input type="checkbox" .checked=${z.auto} @change=${(e: Event) => aendern([{ op: "auto", wert: (e.target as HTMLInputElement).checked }], { leise: true })}>
            automatisch nachführen</label>${hilfe("auto")}
          <span class="fueller"></span>
          <button ?disabled=${S.rechnet} @click=${() => modellRechnen()}>Neu rechnen</button>
        </div>
      </section>

      <section class="abschnitt-flach">
        <h3>Prüfstand ${hilfe("pruefstand")}</h3>
        <div class="balken"><span>Bohrungen <b>${st.bohrungen[0]}/${st.bohrungen[1]}</b></span><progress max=${st.bohrungen[1] || 1} value=${st.bohrungen[0]}></progress></div>
        <div class="balken"><span>Schichten <b>${st.schichten[0]}/${st.schichten[1]}</b></span><progress max=${st.schichten[1] || 1} value=${st.schichten[0]}></progress></div>
        <p class="klein">${st.unklassifiziert_offen ? html`<span class="warnung">⚠ ${st.unklassifiziert_offen} Schicht(en) nicht klassifiziert</span>
          <button class="link" @click=${() => gehe("bohrungen")}>prüfen</button>` : html`<span class="ok">✓ keine offenen Warnungen</span>`}
          · ${st.korrigiert} korrigiert · ${st.manuelle_lage} Lagen manuell · ${st.entfernt} entfernt</p>
        <p class=${`klein ${letzter && !z.seit_einchecken_geaendert ? "ok" : "warn"}`}>
          ${letzter ? `Eingecheckt: ${z.eingecheckt}${z.seit_einchecken_geaendert ? " · seitdem geändert" : ""}` : "noch nicht eingecheckt"}</p>
        <div class="zeile">
          <input class="breit" placeholder="Kommentar (z. B. BK1–BK5 mit Anlage 2 verglichen)" .value=${kommentar}
            @input=${(e: Event) => { kommentar = (e.target as HTMLInputElement).value; }}>
        </div>
        <div class="zeile"><button class="primaer" @click=${einchecken}>✓ Stand einchecken</button>${hilfe("einchecken")}</div>
        ${z.eincheckungen.length ? html`
          <details class="protokoll"><summary>Protokoll (${z.eincheckungen.length})</summary>
            <ul>${[...z.eincheckungen].reverse().map((e) => html`
              <li><b>v${e.nr}</b> ${e.zeit} · ${e.stand.bohrungen[0]}/${e.stand.bohrungen[1]} Bohrungen, ${e.stand.schichten[0]}/${e.stand.schichten[1]} Schichten
                ${e.kommentar ? html`<div class="leise klein">${e.kommentar}</div>` : nothing}</li>`)}</ul>
          </details>` : nothing}
      </section>

      <section class="abschnitt-flach">
        <h3>Export ${hilfe("export")}</h3>
        <div class="export-liste">
          ${exporte.map(([art, titel]) => html`<a class=${`knopf ${art === "ifc" ? "primaer" : ""}`} href=${api.exportUrl(S.sig, art)}
            download>${titel}</a>`)}
        </div>
      </section>

      <details class="erweitert" ?open=${erweitert}
        @toggle=${(e: Event) => { erweitertAuf = (e.target as HTMLDetailsElement).open; }}>
        <summary>Erweitert <span class="leise klein">Exporte · Cesium · BoreholeML · GeolDG · Ground Analysis · Darstellung</span></summary>
        <section class="abschnitt-flach">
          <h3>Weitere Exporte</h3>
          <div class="export-liste">
            ${weitere.map(([art, titel]) => html`<a class="knopf" href=${api.exportUrl(S.sig, art)} download>${titel}</a>`)}
            ${tilesTeil()}
            ${boreholemlTeil()}
          </div>
        </section>
        ${geoldgTeil()}
        ${analyseViewerTeil()}
        <section class="abschnitt-flach">
          <h3>Darstellung</h3>
          <label class="inline">Überhöhung ${hilfe("ueberhoehung")}
            <select @change=${async (e: Event) => {
              const f = Number((e.target as HTMLSelectElement).value);
              await S.viewer?.ueberhoehen(f);                // erst der Viewer (Kamera passt sich an), dann der Stand
              await aendern([{ op: "ueberhoehung", wert: f }], { leise: true });
            }}>
              ${[1, 2, 5, 10, 20].map((f) => html`<option value=${f} .selected=${z.ueberhoehung === f}>${f}×</option>`)}
            </select></label>
        </section>
      </details>

      ${m && (m.hinweise.length || m.nicht_im_modell.length) ? html`
        <section class="abschnitt-flach">
          <h3>Hinweise</h3>
          ${m.nicht_im_modell.length ? html`<p class="klein"><b>Nicht im Modell:</b> ${m.nicht_im_modell.map((x) => `${x.code} (${x.grund})`).join(", ")}</p>` : nothing}
          ${m.hinweise.map((h) => html`<p class="klein">ℹ ${h}</p>`)}
        </section>` : nothing}
    </div>`;
}
