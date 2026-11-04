// Schritt 1 · Gutachten: PDF hochladen (Fortschritt je Seite), Beispiel waehlen oder ein Projekt weiterfuehren.
import { html, nothing } from "lit";
import { api, type DienstAmOrt } from "./api";
import { hilfe } from "./hilfe";
import { karteWaehlen } from "./karte";
import { S, melden, neu, oeffnen, projekteLaden, versuchen } from "./store";

let gewaehlt: File[] = [];
let ocr = true;
let ziehen = false;
const ort = { x: "", y: "", epsg: 25832, name: "" };      // Standort ohne Gutachten (docs/23 §2.3)
let ortDienste: DienstAmOrt[] | null = null;              // was die Laender am Punkt aus der Karte liefern
const UTM: [number, string][] = [[25832, "ETRS89 / UTM 32N"], [25833, "ETRS89 / UTM 33N"],
  [4647, "ETRS89 / UTM 32N (zE-N)"], [5650, "ETRS89 / UTM 33N (zE-N)"]];

async function warten(aid: string) {
  for (;;) {
    const a = await versuchen(() => api.auftrag(aid));
    if (!a) return;
    S.auftrag = a;
    neu();
    if (a.fertig) {
      S.auftrag = null;
      for (const f of a.fehler) melden(f, "fehler", 10000);
      if (a.projekt) {
        gewaehlt = [];
        await oeffnen(a.projekt, "bohrungen");
      } else neu();
      return;
    }
    await new Promise((r) => setTimeout(r, 600));
  }
}

/** Offenes Standort-Projekt: ein Gutachten dazu nimmt dessen Bohrungen der Länder, DGM und Gebäude mit. */
const zumStandort = () => (S.z?.standort ? S.sig : "");

async function auswerten() {
  if (!gewaehlt.length) return;
  const a = await versuchen(() => api.gutachten(gewaehlt, ocr && !!S.info?.ocr, zumStandort()));
  if (a) await warten(a.id);
}

async function standortAnlegen() {
  const x = Number(ort.x.replace(",", ".")), y = Number(ort.y.replace(",", "."));
  if (!Number.isFinite(x) || !Number.isFinite(y) || !ort.x || !ort.y) {
    melden("Rechtswert und Hochwert als Zahlen eingeben.", "warn");
    return;
  }
  const r = await versuchen(() => api.standort(x, y, ort.epsg, ort.name), "Standort wird angelegt …");
  if (!r) return;
  await oeffnen(r.projekt, r.vorhanden ? undefined : "lage");    // vorhanden: Name und Schritt bleiben
  if (r.vorhanden) melden(`Den Standort gibt es schon: „${S.z?.name}“ geöffnet.`);
}

async function ausDerKarte() {
  let p = null;
  try {
    p = await karteWaehlen();
  } catch (err) {
    melden(`Karte: ${(err as Error).message}`, "fehler", 8000);
  }
  if (!p) return;
  ort.x = String(p.x);
  ort.y = String(p.y);
  ort.epsg = p.epsg;
  ortDienste = p.dienste;
  neu();
}

function standortKarte() {
  const feld = (k: "x" | "y" | "name", titel: string, platz: string) => html`
    <label class="feld"><span>${titel}</span><input type="text" inputmode=${k === "name" ? "text" : "decimal"}
      aria-label=${titel} placeholder=${platz} .value=${ort[k]} @input=${(e: Event) => {
        ort[k] = (e.target as HTMLInputElement).value;
        if (k !== "name" && ortDienste) { ortDienste = null; neu(); }       // die Liste galt dem Punkt aus der Karte
      }}></label>`;
  return html`
    <section class="karte">
      <h3>Standort ohne Gutachten ${hilfe("standort")}</h3>
      <p class="leise klein">Ein Punkt statt eines PDFs: Bohrungen der Länder, DGM und Gebäude um den Standort. Das Modell
        ist eine <b>Vorerkundung</b> – kein Ersatz für das Gutachten.</p>
      <div class="zeile"><button @click=${ausDerKarte}>🗺 Auf der Karte wählen</button>${hilfe("karte")}
        <span class="leise klein">oder Rechts- und Hochwert eintragen</span></div>
      <div class="raster-2">
        ${feld("x", "Rechtswert", "z. B. 368130")}
        ${feld("y", "Hochwert", "z. B. 5724400")}
        <label class="feld"><span>System</span>
          <select aria-label="System des Standorts" @change=${(e: Event) => { ort.epsg = Number((e.target as HTMLSelectElement).value);
            ortDienste = null; neu(); }}>
            ${UTM.map(([c, n]) => html`<option value=${c} ?selected=${ort.epsg === c}>${c} · ${n}</option>`)}
          </select></label>
        ${feld("name", "Name (frei)", "z. B. Marl Nord")}
      </div>
      ${ortDienste ? html`<ul class="dienste klein" aria-label="Dienste am Standort">
        ${ortDienste.map((d) => html`<li class=${d.art}>${d.text}</li>`)}</ul>` : nothing}
      <button class="primaer" @click=${standortAnlegen}>Projekt am Standort anlegen →</button>
    </section>`;
}

async function beispiel(name: string) {
  const r = await versuchen(() => api.beispiel(name), "Beispiel wird geöffnet …");
  if (r?.projekt) await oeffnen(r.projekt, r.schritt ?? "bohrungen");     // Standort: im Schritt Lage
  else if (r?.auftrag) await warten(r.auftrag);
}

function dateienSetzen(liste: FileList | null | undefined) {
  gewaehlt = [...(liste ?? [])].filter((f) => /\.(pdf|json|xml)$/i.test(f.name));
  if (liste?.length && !gewaehlt.length) melden("Bitte PDF-Dateien wählen (oder eine Extraktion als JSON, Bohrungen als BoreholeML).", "warn");
  neu();
}

async function entfernen(sig: string, name: string) {
  if (!confirm(`Projekt „${name}“ mit allen Korrekturen löschen? Das Gutachten selbst bleibt unberührt.`)) return;
  await versuchen(() => api.loeschen(sig));
  await projekteLaden();
}

export function schrittGutachten() {
  const a = S.auftrag;
  const ocrDa = !!S.info?.ocr;
  return html`
    <div class="seite-mitte">
      <section class="karte gross">
        <h2>Bodengutachten auswerten</h2>
        <p class="leise">Bohrprofile, Schichtenverzeichnisse oder ganze Gutachten als PDF – Vektor oder Scan. Die Bohrungen
          werden erkannt; im nächsten Schritt prüfen und korrigieren Sie sie.</p>
        ${zumStandort() ? html`<p class="hinweis-standort">Zum Standort <b>${S.z!.name}</b>: Bohrungen der Länder (mit Prüfstand),
          DGM und Gebäude kommen in das neue Projekt mit – es ist dann <b>gemischt</b>, beide Quellen bleiben getrennt.</p>` : nothing}
        ${a ? html`
          <div class="fortschritt-karte" aria-live="polite">
            <div class="kreisel klein"></div>
            <div>
              <strong>${a.stand.datei || a.dateien[0]}</strong>
              <span class="leise">Datei ${a.stand.nr}/${a.stand.dateien || a.dateien.length}
                ${a.stand.seiten ? html` · Seite ${a.stand.seite}/${a.stand.seiten}${a.stand.klasse ? ` · ${a.stand.klasse}` : ""}` : " · wird geöffnet …"}</span>
              <progress max=${a.stand.seiten || 1} value=${a.stand.seite}></progress>
            </div>
          </div>` : html`
          <label class=${`ablage ${ziehen ? "ueber" : ""}`}
            @dragover=${(e: DragEvent) => { e.preventDefault(); ziehen = true; neu(); }}
            @dragleave=${() => { ziehen = false; neu(); }}
            @drop=${(e: DragEvent) => { e.preventDefault(); ziehen = false; dateienSetzen(e.dataTransfer?.files); }}>
            <input type="file" accept=".pdf,application/pdf,.json,application/json,.xml,application/xml,text/xml" multiple @change=${(e: Event) => dateienSetzen((e.target as HTMLInputElement).files)}>
            <span class="ablage-icon">⇪</span>
            <strong>${gewaehlt.length ? gewaehlt.map((f) => f.name).join(", ") : "PDF hierher ziehen oder klicken"}</strong>
            <span class="leise">${gewaehlt.length ? `${gewaehlt.length} Datei(en) bereit` : "mehrere Dateien möglich (z. B. Anlagen 2–4) · auch eine Extraktion als JSON oder Bohrungen als BoreholeML (XML)"}</span>
          </label>
          <div class="zeile">
            <label class="schalter" title=${ocrDa ? "" : "nicht installiert: pip install -r requirements-ocr.txt"}>
              <input type="checkbox" .checked=${ocr && ocrDa} ?disabled=${!ocrDa} @change=${(e: Event) => { ocr = (e.target as HTMLInputElement).checked; }}>
              OCR für Scans ${ocrDa ? "" : "(nicht installiert)"}
            </label>${hilfe("ocr")}
            <span class="fueller"></span>
            <button class="primaer" ?disabled=${!gewaehlt.length} @click=${auswerten}>Auswerten →</button>
          </div>`}
      </section>

      ${standortKarte()}

      <div class="zwei-spalten">
        <section class="karte">
          <h3>Beispiele ${hilfe("beispiele")}</h3>
          <ul class="auswahl-liste">
            ${(S.info?.beispiele ?? []).filter((b) => !b.standort).map((b) => html`
              <li><button class="link" ?disabled=${!!a} @click=${() => beispiel(b.name)}>${b.titel}</button></li>`)}
          </ul>
          <h4 class="klein">Standort ohne Gutachten <span class="leise">(Bohrungen der Länder: Abfrage im Schritt Lage, mit Netz)</span></h4>
          <ul class="auswahl-liste">
            ${(S.info?.beispiele ?? []).filter((b) => b.standort).map((b) => html`
              <li><button class="link" ?disabled=${!!a} @click=${() => beispiel(b.name)}>${b.titel}</button></li>`)}
          </ul>
        </section>
        <section class="karte">
          <h3>Zuletzt bearbeitet</h3>
          ${S.projekte.length ? html`
            <table class="tabelle kompakt">
              <thead><tr><th>Projekt</th><th>Bohrungen</th><th>geprüft</th><th>geändert</th><th></th></tr></thead>
              <tbody>
                ${S.projekte.map((p) => html`
                  <tr>
                    <td><button class="link" @click=${() => oeffnen(p.signatur)}>${p.name}</button>${p.standort
                      ? html` <span class="abzeichen vorerkundung" title="Standort ohne Gutachten">Standort</span>` : nothing}
                      <div class="leise klein">${p.dokumente.join(", ")}</div></td>
                    <td class="zahl" title=${p.fremd ? `davon ${p.fremd} aus den Datenbanken der Länder` : ""}>${p.bohrungen}</td>
                    <td class="zahl">${p.geprueft}${p.eincheckungen ? html` · <span title="eingecheckt">✓${p.eincheckungen}</span>` : nothing}</td>
                    <td class="leise klein">${p.geaendert}</td>
                    <td><button class="symbol" title="Projekt löschen" aria-label="Projekt löschen" @click=${() => entfernen(p.signatur, p.name)}>🗑</button></td>
                  </tr>`)}
              </tbody>
            </table>` : html`<p class="leise">Noch keine Projekte. Ein Projekt entsteht beim ersten Auswerten und wird automatisch gesichert.</p>`}
        </section>
      </div>
      ${S.info ? html`<p class="leise klein impressum">GroundTwin ${S.info.version} · freie Software unter
        <a href=${`${S.info.quellcode}/blob/main/LICENSE`} target="_blank" rel="noopener">${S.info.lizenz}</a> ·
        <a href=${S.info.quellcode} target="_blank" rel="noopener">Quellcode</a> · die App extrahiert und schlägt vor;
        die Interpretation und Freigabe bleibt beim Geotechniker.</p>` : nothing}
    </div>`;
}
