// Werkzeug „Dienste der Länder“ (docs/21 §4.8, D98): das Register services/geodaten/geodaten/dienste.json als Matrix
// Land × Thema, ein Eintrag zum Bearbeiten, Prüfen gegen den echten Dienst, Speichern mit dem gelesenen Stand (sonst
// Konflikt statt stillem Überschreiben). Im Netz mit Passwort nur lesen und die gespeicherten Einträge prüfen.
import "../viewer/viewer.css";
import "../app/app.css";
import "./dienste.css";
import { html, nothing, render } from "lit";

interface Dienst {
  id: string; land: string; art: string; titel: string; anbieter: string; url: string;
  laender?: string[]; status?: string; geprueft?: string; aktiv?: boolean; hinweis?: string; lizenz?: string;
  lizenz_url?: string; namensnennung?: string; beleg?: string; [weitere: string]: unknown;
}
interface Register {
  datei: string; version: string; bearbeiten: boolean; grund: string; format: string; stand: string; beschreibung: string;
  laender: string[]; themen: Record<string, string>;
  arten: Record<string, { thema: string; angebunden: boolean; pflicht: string[] }>; dienste: Dienst[];
}
interface Pruefung { id: string; ok: boolean; meldung: string; dauer_ms: number; gefunden: string[] }
type Sicht = "alle" | "angebunden" | "links" | "ungeprueft" | "fehler";

const ART_NAME: Record<string, string> = {
  "wfs-kopf": "WFS – nur Kopfdaten", "wfs-boreholeml": "WFS – BoreholeML mit Schichten", "wcs-dgm": "WCS – DGM",
  "lod2-kacheln": "LoD2-Kacheln", "portal-bohrungen": "Portal (Link)", "portal-dgm": "Portal (Link)",
  "portal-gebaeude": "Portal (Link)",
};
// Felder, die das Formular zeigt; alles andere steht unter „Technische Angaben“ (JSON)
const FORMULAR = ["id", "land", "laender", "art", "status", "geprueft", "aktiv", "titel", "anbieter", "url", "hinweis",
  "lizenz", "lizenz_url", "namensnennung", "beleg"];
const PFLICHT = ["id", "land", "art", "titel", "anbieter", "url"];

const Z = {
  reg: null as Register | null,
  entwurf: [] as Dienst[],
  gespeichert: "",                          // JSON des gespeicherten Stands: geändert = anders als dieser
  wahl: -1,                                 // Index im Entwurf
  technik: "",                              // Text der technischen Angaben (darf beim Tippen ungültig sein)
  technikFehler: "",
  sicht: "alle" as Sicht,
  suche: "",
  pruefungen: new Map<string, Pruefung | "laeuft">(),
  alle: null as null | { fertig: number; gesamt: number },
  fehler: "",                               // Antwort des Servers beim Speichern
  meldung: "",
};

// ------------------------------------------------------------------ Server
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
const mitJson = (methode: string, daten: unknown): RequestInit =>
  ({ method: methode, headers: { "Content-Type": "application/json" }, body: JSON.stringify(daten) });

async function laden() {
  try {
    uebernehmen(await anfrage<Register>("/api/dienste"));
  } catch (err) {
    Z.fehler = `Register nicht lesbar: ${(err as Error).message}`;
  }
  zeichnen();
}

function uebernehmen(reg: Register, behalte = "") {
  Z.reg = reg;
  Z.entwurf = structuredClone(reg.dienste);
  Z.gespeichert = JSON.stringify(reg.dienste);
  Z.wahl = behalte ? Z.entwurf.findIndex((d) => d.id === behalte) : -1;
  technikSetzen();
}

const geaendert = () => !!Z.reg && JSON.stringify(Z.entwurf) !== Z.gespeichert;

async function speichern() {
  if (!Z.reg) return;
  const behalte = Z.entwurf[Z.wahl]?.id ?? "";
  try {
    uebernehmen(await anfrage<Register>("/api/dienste", mitJson("PUT", { dienste: Z.entwurf, version: Z.reg.version })), behalte);
    Z.fehler = "";
    melden("Gespeichert – die App fragt ab jetzt mit diesem Stand.");
  } catch (err) {
    Z.fehler = (err as Error).message;
  }
  zeichnen();
}

function verwerfen() {
  if (!Z.reg || !confirm("Alle nicht gespeicherten Änderungen verwerfen?")) return;
  uebernehmen(Z.reg, Z.entwurf[Z.wahl]?.id ?? "");
  Z.fehler = "";
  zeichnen();
}

async function pruefen(i: number) {
  const d = Z.entwurf[i];
  if (!d || !Z.reg) return;
  const schluessel = d.id || `#${i}`;
  Z.pruefungen.set(schluessel, "laeuft");
  zeichnen();
  try {
    const body = Z.reg.bearbeiten ? { eintrag: d } : { id: d.id };       // im Netz nur gespeicherte Einträge
    Z.pruefungen.set(schluessel, await anfrage<Pruefung>("/api/dienste/pruefen", mitJson("POST", body)));
  } catch (err) {
    Z.pruefungen.set(schluessel, { id: d.id, ok: false, meldung: (err as Error).message, dauer_ms: 0, gefunden: [] });
  }
  zeichnen();
}

async function allePruefen() {
  const liste = sichtbare().map(({ i }) => i);
  Z.alle = { fertig: 0, gesamt: liste.length };
  zeichnen();
  const warteschlange = [...liste];
  const arbeiter = async () => {
    for (let i = warteschlange.shift(); i !== undefined; i = warteschlange.shift()) {
      await pruefen(i);
      Z.alle!.fertig += 1;
      zeichnen();
    }
  };
  await Promise.all([arbeiter(), arbeiter(), arbeiter(), arbeiter()]);
  const fehl = liste.filter((i) => (Z.pruefungen.get(Z.entwurf[i]?.id) as Pruefung | undefined)?.ok === false).length;
  Z.alle = null;
  melden(fehl ? `${liste.length} geprüft, ${fehl} nicht erreichbar oder unvollständig` : `${liste.length} geprüft, alle erreichbar`);
  zeichnen();
}

// ------------------------------------------------------------------ Bearbeiten
function thema(d: Dienst) {
  return Z.reg?.arten[d.art]?.thema ?? "";
}
function angebunden(d: Dienst) {
  return !!Z.reg?.arten[d.art]?.angebunden;
}

function technikSetzen() {
  const d = Z.entwurf[Z.wahl];
  Z.technikFehler = "";
  if (!d) {
    Z.technik = "";
    return;
  }
  const rest = Object.fromEntries(Object.entries(d).filter(([k]) => !FORMULAR.includes(k)));
  Z.technik = Object.keys(rest).length ? JSON.stringify(rest, null, 1) : "{}";
}

function waehlen(i: number) {
  Z.wahl = Z.wahl === i ? -1 : i;
  technikSetzen();
  zeichnen();
  if (Z.wahl >= 0) document.querySelector(".editor")?.scrollIntoView({ block: "nearest", behavior: "smooth" });
}

function setzen(feld: string, wert: unknown) {
  const d = Z.entwurf[Z.wahl];
  if (!d) return;
  const bekannt = (n: unknown) => !!Z.reg?.laender.includes(String(n)) && n !== "Deutschland";
  if (feld === "land" && (!d.laender || (d.laender.length === 1 && d.laender[0] === d.land))) {
    if (bekannt(wert)) d.laender = [String(wert)];                  // folgt dem Land, solange es eines ist
    else delete d.laender;                                          // Deutschland: alle, vom Server ergänzt
    technikSetzen();
  }
  if (wert === "" || wert === undefined) delete d[feld];
  else d[feld] = wert;
  if (feld === "art" && !d.id) d.id = vorschlagId(d.land, String(wert));
  zeichnen();
}

function technikAendern(text: string) {
  Z.technik = text;
  const d = Z.entwurf[Z.wahl];
  try {
    const neu = JSON.parse(text || "{}");
    if (typeof neu !== "object" || neu === null || Array.isArray(neu)) throw new Error("ein Objekt { … } erwartet");
    for (const k of Object.keys(d)) if (!FORMULAR.includes(k)) delete d[k];
    Object.assign(d, neu);
    Z.technikFehler = "";
  } catch (err) {
    Z.technikFehler = (err as Error).message;
  }
  zeichnen();
}

const KUERZEL: Record<string, string> = {
  "Schleswig-Holstein": "SH", Hamburg: "HH", Niedersachsen: "NI", Bremen: "HB", "Nordrhein-Westfalen": "NW", Hessen: "HE",
  "Rheinland-Pfalz": "RP", "Baden-Württemberg": "BW", Bayern: "BY", Saarland: "SL", Berlin: "BE", Brandenburg: "BB",
  "Mecklenburg-Vorpommern": "MV", Sachsen: "SN", "Sachsen-Anhalt": "ST", "Thüringen": "TH", Deutschland: "DE",
};

function vorschlagId(land: string, art: string) {
  const basis = `${KUERZEL[land] ?? "XX"}${art.endsWith("dgm") ? "-DGM" : art.includes("lod2") || art.endsWith("gebaeude") ? "-LOD2" : ""}`;
  const vorhanden = new Set(Z.entwurf.map((d) => d.id));
  if (!vorhanden.has(basis)) return basis;
  for (let n = 2; ; n++) if (!vorhanden.has(`${basis}-${n}`)) return `${basis}-${n}`;
}

function neuerEintrag(land = "Bayern", themaId = "bohrungen") {
  const art = `portal-${themaId}`;
  const d: Dienst = { id: vorschlagId(land, art), land, laender: land === "Deutschland" ? undefined : [land], art,
    status: "ungeprueft", titel: "", anbieter: "", url: "https://", hinweis: "", lizenz: "", namensnennung: "", beleg: "" };
  if (!d.laender) delete d.laender;
  Z.entwurf.push(d);
  Z.wahl = Z.entwurf.length - 1;
  Z.sicht = "alle";
  Z.suche = "";
  technikSetzen();
  zeichnen();
  window.setTimeout(() => document.querySelector<HTMLInputElement>(".editor input[name=titel]")?.focus(), 30);
}

function entfernen() {
  const d = Z.entwurf[Z.wahl];
  if (!d || !confirm(`Eintrag ${d.id || "(ohne Kennung)"} entfernen? (Erst „Speichern“ schreibt die Datei.)`)) return;
  Z.entwurf.splice(Z.wahl, 1);
  Z.wahl = -1;
  technikSetzen();
  zeichnen();
}

function alsGeprueft() {
  const d = Z.entwurf[Z.wahl];
  if (!d) return;
  d.status = "geprueft";
  d.geprueft = new Date().toISOString().slice(0, 10);
  zeichnen();
}

function herunterladen() {
  if (!Z.reg) return;
  const { format, stand, beschreibung } = Z.reg;
  const blob = new Blob([JSON.stringify({ format, stand, beschreibung, dienste: Z.entwurf }, null, 1) + "\n"],
    { type: "application/json" });
  const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(blob), download: "dienste.json" });
  a.click();
  window.setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

let meldungZeit = 0;
function melden(text: string) {
  Z.meldung = text;
  window.clearTimeout(meldungZeit);
  meldungZeit = window.setTimeout(() => {
    Z.meldung = "";
    zeichnen();
  }, 4500);
}

// ------------------------------------------------------------------ Ansicht
function pruefungVon(d: Dienst, i: number) {
  return Z.pruefungen.get(d.id || `#${i}`);
}

function passt(d: Dienst, i: number) {
  const p = pruefungVon(d, i);
  if (Z.sicht === "angebunden" && !angebunden(d)) return false;
  if (Z.sicht === "links" && angebunden(d)) return false;
  if (Z.sicht === "ungeprueft" && d.status === "geprueft") return false;
  if (Z.sicht === "fehler" && !(p && p !== "laeuft" && !p.ok)) return false;
  const s = Z.suche.trim().toLowerCase();
  return !s || [d.id, d.titel, d.anbieter, d.url, d.land, d.hinweis].some((w) => String(w ?? "").toLowerCase().includes(s));
}

function sichtbare() {
  return Z.entwurf.map((d, i) => ({ d, i })).filter(({ d, i }) => passt(d, i));
}

function zaehlen() {
  const e = Z.entwurf;
  const fehler = e.filter((d, i) => {
    const p = pruefungVon(d, i);
    return p && p !== "laeuft" && !p.ok;
  }).length;
  return { alle: e.length, angebunden: e.filter(angebunden).length, links: e.filter((d) => !angebunden(d)).length,
    ungeprueft: e.filter((d) => d.status !== "geprueft").length, fehler };
}

function chip(d: Dienst, i: number, zeile: string) {
  const p = pruefungVon(d, i);
  const fremd = d.land !== zeile && zeile !== "Deutschland";
  // eigene Namen (chip-…): app.css kennt .ungeprueft, .aus und .link schon (lesson X40)
  const klasse = ["chip", angebunden(d) ? "chip-angebunden" : "chip-portal", d.status === "geprueft" ? "chip-geprueft" : "chip-offen",
    d.aktiv === false ? "chip-aus" : "", Z.wahl === i ? "chip-gewaehlt" : "", p && p !== "laeuft" ? (p.ok ? "chip-ok" : "chip-kaputt") : ""]
    .filter(Boolean).join(" ");
  const titel = `${d.titel || "(ohne Titel)"}\n${angebunden(d) ? "angebunden: die App fragt selbst ab" : "Link zum Portal"} · `
    + `${d.status === "geprueft" ? `geprüft ${d.geprueft ?? ""}` : "ungeprüft"}${d.aktiv === false ? " · abgeschaltet" : ""}`
    + `${fremd ? `\nDienst von ${d.land}` : ""}${p && p !== "laeuft" ? `\nPrüfung: ${p.meldung}` : ""}`;
  return html`<button class=${klasse} title=${titel} @click=${() => waehlen(i)} aria-pressed=${Z.wahl === i}>
    <span class="punkt" aria-hidden="true"></span>${d.id || "neu"}${fremd ? html`<span class="fremd">↗</span>` : nothing}
    ${p === "laeuft" ? html`<span class="pruef laeuft" aria-label="wird geprüft">…</span>`
      : p ? html`<span class=${`pruef ${p.ok ? "ja" : "nein"}`}>${p.ok ? "✓" : "✗"}</span>` : nothing}</button>`;
}

function matrix() {
  const reg = Z.reg!;
  const themen = Object.entries(reg.themen);
  const filter = Z.sicht !== "alle" || Z.suche.trim() !== "";
  const zeilen = reg.laender.map((land) => {
    const zellen = themen.map(([th]) => sichtbare().filter(({ d }) => thema(d) === th && (land === "Deutschland"
      ? d.land === "Deutschland" : d.land !== "Deutschland" && (d.laender?.length ? d.laender.includes(land) : d.land === land))));
    return { land, zellen };
  }).filter((z) => !filter || z.zellen.some((c) => c.length));
  return html`
    <table class="matrix">
      <thead><tr><th scope="col">Land</th>${themen.map(([, name]) => html`<th scope="col">${name}</th>`)}</tr></thead>
      <tbody>
        ${zeilen.map(({ land, zellen }) => html`<tr>
          <th scope="row">${land}</th>
          ${zellen.map((zelle, k) => html`<td>
            <div class="zelle">${zelle.map(({ d, i }) => chip(d, i, land))}
              ${reg.bearbeiten ? html`<button class="plus" title=${`Neuer Eintrag: ${land}, ${themen[k][1]}`}
                aria-label=${`Neuer Eintrag ${land} ${themen[k][1]}`} @click=${() => neuerEintrag(land, themen[k][0])}>+</button>` : nothing}
              ${!zelle.length && !reg.bearbeiten ? html`<span class="leer">–</span>` : nothing}
            </div></td>`)}
        </tr>`)}
        ${!zeilen.length ? html`<tr><td colspan=${themen.length + 1} class="leise">Kein Eintrag passt zum Filter.</td></tr>` : nothing}
      </tbody>
    </table>`;
}

function feld(name: string, beschriftung: string, d: Dienst, art: "text" | "url" | "lang" = "text", hinweis = "") {
  const aus = !Z.reg!.bearbeiten;
  const pflicht = PFLICHT.includes(name) || (Z.reg!.arten[d.art]?.pflicht ?? []).includes(name);
  const wert = String(d[name] ?? "");
  const fehlt = pflicht && !wert.trim();
  return html`<label class=${`eingabe ${fehlt ? "fehlt" : ""}`}>
    <span>${beschriftung}${pflicht ? html`<i title="Pflichtangabe">*</i>` : nothing}</span>
    ${art === "lang"
      ? html`<textarea name=${name} rows="3" ?disabled=${aus} .value=${wert}
          @input=${(e: Event) => setzen(name, (e.target as HTMLTextAreaElement).value)}></textarea>`
      : html`<input name=${name} type=${art === "url" ? "url" : "text"} ?disabled=${aus} .value=${wert} spellcheck="false"
          @input=${(e: Event) => setzen(name, (e.target as HTMLInputElement).value)} />`}
    ${hinweis ? html`<small class="leise">${hinweis}</small>` : nothing}
  </label>`;
}

function editor() {
  const reg = Z.reg!;
  const d = Z.entwurf[Z.wahl];
  if (!d) {
    return html`<aside class="editor leer-editor">
      <p class="gross">Eintrag wählen</p>
      <p class="leise">Ein Klick auf einen Eintrag der Tabelle zeigt ihn hier – ${reg.bearbeiten ? "zum Bearbeiten und Prüfen" : "zum Ansehen und Prüfen"}.</p>
      <ul class="legende">
        <li><span class="chip chip-angebunden chip-geprueft"><span class="punkt"></span>BE</span> angebunden: die App fragt den Dienst selbst ab</li>
        <li><span class="chip chip-portal chip-offen"><span class="punkt"></span>BY</span> Link zum Portal (ansehen, herunterladen, anfragen)</li>
        <li><span class="chip chip-portal chip-geprueft"><span class="punkt"></span>…</span> grün umrandet: geprüft (mit Datum)</li>
        <li><span class="chip chip-portal chip-offen"><span class="punkt"></span>…<span class="fremd">↗</span></span> Dienst eines Nachbarlandes, gilt auch hier</li>
      </ul>
    </aside>`;
  }
  const aus = !reg.bearbeiten;
  const p = pruefungVon(d, Z.wahl);
  const fehlen = (reg.arten[d.art]?.pflicht ?? []).filter((k) => d[k] === undefined || d[k] === "" ||
    (Array.isArray(d[k]) && !(d[k] as unknown[]).length));
  const gruppen = [true, false].map((verbunden) => Object.entries(reg.arten).filter(([, a]) => a.angebunden === verbunden));
  return html`<aside class="editor" aria-label="Eintrag">
    <div class="editor-kopf">
      <div>
        <h2>${d.id || "Neuer Eintrag"}</h2>
        <p class="leise klein">${angebunden(d) ? "angebunden – die App fragt selbst ab" : "Link zum Portal"} ·
          ${d.status === "geprueft" ? html`<span class="ok">geprüft ${d.geprueft ?? ""}</span>` : "ungeprüft"}
          ${d.aktiv === false ? html` · <span class="warn">abgeschaltet</span>` : nothing}</p>
      </div>
      <button class="symbol" title="Schließen (Esc)" aria-label="Schließen" @click=${() => waehlen(Z.wahl)}>✕</button>
    </div>
    <div class="adresse">
      <a class="knopf" href=${d.url} target="_blank" rel="noopener noreferrer" ?hidden=${!/^https?:\/\/[^{]+$/.test(d.url)}>Öffnen ↗</a>
      <button class="primaer" @click=${() => pruefen(Z.wahl)} ?disabled=${p === "laeuft"}>
        ${p === "laeuft" ? "Prüft …" : "Prüfen"}</button>
      ${!aus && p && p !== "laeuft" && p.ok && d.status !== "geprueft"
        ? html`<button @click=${alsGeprueft}>Als geprüft markieren</button>` : nothing}
    </div>
    ${p && p !== "laeuft" ? html`<div class=${`ergebnis ${p.ok ? "ja" : "nein"}`} role="status">
      <b>${p.ok ? "✓" : "✗"}</b> ${p.meldung}${p.dauer_ms ? html` <span class="leise">(${(p.dauer_ms / 1000).toFixed(1)} s)</span>` : nothing}
      ${p.gefunden.length ? html`<details><summary>${p.gefunden.length} gefunden</summary><p class="klein">${p.gefunden.join(", ")}</p></details>` : nothing}
    </div>` : nothing}
    <div class="formular">
      ${feld("id", "Kennung", d, "text", "Großbuchstaben, Ziffern, „-“ (z. B. BY-DGM)")}
      <label class="eingabe"><span>Land<i>*</i></span>
        <input name="land" list="laenderliste" ?disabled=${aus} .value=${d.land} spellcheck="false"
          @input=${(e: Event) => setzen("land", (e.target as HTMLInputElement).value)} />
        <datalist id="laenderliste">${reg.laender.map((l) => html`<option value=${l}></option>`)}</datalist>
        <small class="leise">Name zum Anzeigen (z. B. „Brandenburg mit Berlin“); wo der Eintrag gilt:
          ${(d.laender ?? []).length ? (d.laender ?? []).join(", ") : d.land === "Deutschland" ? "alle Länder" : "aus dem Land"}
          (Technische Angaben, „laender“)</small></label>
      <label class="eingabe"><span>Art<i>*</i></span>
        <select ?disabled=${aus} .value=${d.art} @change=${(e: Event) => setzen("art", (e.target as HTMLSelectElement).value)}>
          ${gruppen.map((liste, k) => html`<optgroup label=${k === 0 ? "angebunden (die App fragt ab)" : "nur Link"}>
            ${liste.map(([art, a]) => html`<option value=${art} ?selected=${art === d.art}>${reg.themen[a.thema]} – ${ART_NAME[art] ?? art}</option>`)}
          </optgroup>`)}
        </select></label>
      ${feld("titel", "Titel", d)}
      ${feld("anbieter", "Anbieter", d)}
      ${feld("url", "Adresse", d, "url", d.art === "lod2-kacheln" ? "mit {e} und {n} (Kilometer Ost/Nord der Kachel)" : "")}
      ${feld("hinweis", "Hinweis", d, "lang")}
      ${feld("lizenz", "Lizenz", d)}
      ${feld("lizenz_url", "Lizenz-Adresse", d, "url")}
      ${feld("namensnennung", "Namensnennung", d, "text", "{jahr} wird beim Abruf ersetzt")}
      ${feld("beleg", "Beleg (wo steht das?)", d, "url")}
      <div class="eingabe zwei">
        <label><span>Status</span>
          <select ?disabled=${aus} .value=${d.status === "geprueft" ? "geprueft" : "ungeprueft"}
            @change=${(e: Event) => setzen("status", (e.target as HTMLSelectElement).value)}>
            <option value="ungeprueft" ?selected=${d.status !== "geprueft"}>ungeprüft</option>
            <option value="geprueft" ?selected=${d.status === "geprueft"}>geprüft</option>
          </select></label>
        <label><span>Geprüft am</span>
          <input type="date" ?disabled=${aus} .value=${String(d.geprueft ?? "")}
            @change=${(e: Event) => setzen("geprueft", (e.target as HTMLInputElement).value)} /></label>
      </div>
      <label class="inline schalter"><input type="checkbox" ?disabled=${aus} .checked=${d.aktiv !== false}
        @change=${(e: Event) => setzen("aktiv", (e.target as HTMLInputElement).checked ? undefined : false)} />
        In der App verwenden</label>
      <details class="technik" ?open=${fehlen.length > 0}>
        <summary>Technische Angaben${fehlen.length ? html` – <span class="warn">fehlt: ${fehlen.join(", ")}</span>` : nothing}</summary>
        <p class="leise klein">JSON: Länder, Gebiet, Typen, Systeme, Felder, Coverage … (Länder und Gebiet ergänzt der Server aus dem Land).</p>
        <textarea class="json" rows="10" spellcheck="false" ?disabled=${aus} .value=${Z.technik}
          @input=${(e: Event) => technikAendern((e.target as HTMLTextAreaElement).value)}></textarea>
        ${Z.technikFehler ? html`<p class="warn klein">Kein gültiges JSON: ${Z.technikFehler}</p>` : nothing}
      </details>
      ${aus ? nothing : html`<div class="zeile"><span class="fueller"></span>
        <button class="gefahr" @click=${entfernen}>Eintrag entfernen …</button></div>`}
    </div>
  </aside>`;
}

function seite() {
  const reg = Z.reg;
  if (!reg) {
    return html`<div class="werkzeug-rahmen"><p class=${Z.fehler ? "warn" : "leise"}>${Z.fehler || "Register wird geladen …"}</p></div>`;
  }
  const n = zaehlen();
  const sichten: [Sicht, string, number][] = [["alle", "Alle", n.alle], ["angebunden", "Angebunden", n.angebunden],
    ["links", "Links", n.links], ["ungeprueft", "Ungeprüft", n.ungeprueft], ["fehler", "Nicht erreichbar", n.fehler]];
  return html`
    <header class="werkzeug-kopf">
      <a class="marke" href="index.html" title="Zur App"><span class="logo">⛰</span><span><b>GroundTwin</b> · Werkzeuge</span></a>
      <span class="fueller"></span>
      <a class="knopf" href="index.html">← Zur App</a>
    </header>
    <div class="werkzeug-rahmen">
      <section class="einleitung">
        <h1>Dienste der Länder</h1>
        <p class="gross">Wo die App Bohrungen, Gelände und Gebäude jedes Landes findet – angebunden (die App fragt selbst ab)
          oder als Link zum Portal des Landes.</p>
        <p class="leise klein">Datei <code>${reg.datei}</code> · Stand ${reg.stand} · ${reg.format}</p>
        ${reg.bearbeiten ? nothing : html`<p class="nur-lesen" role="note">Nur lesen – ${reg.grund}</p>`}
      </section>
      <div class="werkzeugleiste">
        <div class="segmente" role="group" aria-label="Ansicht">
          ${sichten.map(([id, name, zahl]) => html`<button class=${Z.sicht === id ? "aktiv" : ""} aria-pressed=${Z.sicht === id}
            ?disabled=${id === "fehler" && !zahl} @click=${() => { Z.sicht = id; zeichnen(); }}>${name} <span class="zahl">${zahl}</span></button>`)}
        </div>
        <input type="search" class="register-suche" placeholder="Suchen: Kennung, Titel, Adresse …" aria-label="Suchen" .value=${Z.suche}
          @input=${(e: Event) => { Z.suche = (e.target as HTMLInputElement).value; zeichnen(); }} />
        <span class="fueller"></span>
        <button @click=${allePruefen} ?disabled=${!!Z.alle} title="Jeden sichtbaren Eintrag einmal ansprechen">
          ${Z.alle ? `Prüft ${Z.alle.fertig}/${Z.alle.gesamt} …` : "Alle prüfen"}</button>
        <button @click=${herunterladen} title="Den Stand dieser Seite als dienste.json herunterladen">Als Datei</button>
        ${reg.bearbeiten ? html`<button class="primaer" @click=${() => neuerEintrag()}>+ Neuer Eintrag</button>` : nothing}
      </div>
      ${Z.fehler ? html`<div class="speicherfehler" role="alert"><b>Nicht gespeichert:</b> ${Z.fehler}</div>` : nothing}
      <div class="arbeitsflaeche">
        <div class="tabelle">${matrix()}</div>
        ${editor()}
      </div>
    </div>
    ${geaendert() ? html`<div class="speicherleiste" role="region" aria-label="Ungespeicherte Änderungen">
      <span>Änderungen nicht gespeichert</span>
      <button @click=${verwerfen}>Verwerfen</button>
      <button class="primaer" @click=${speichern}>Speichern</button>
    </div>` : nothing}
    ${Z.meldung ? html`<div class="werkzeug-meldung" role="status">${Z.meldung}</div>` : nothing}`;
}

const wurzel = document.getElementById("werkzeug")!;
function zeichnen() {
  render(seite(), wurzel);
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && Z.wahl >= 0 && !(e.target as HTMLElement).closest?.("textarea")) waehlen(Z.wahl);
});
window.addEventListener("beforeunload", (e) => {
  if (geaendert()) e.preventDefault();
});

zeichnen();
await laden();
(window as unknown as { werkzeug: typeof Z }).werkzeug = Z;     // fuer die Pruefungen (scripts/check_app.mjs)
