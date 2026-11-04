// Schritt 3 · Lage: Unterlage (Lageplan oder Laengsschnitt) hochladen, kalibrieren (Strecke messen -> Massstab,
// Bezugspunkt mit Koordinate, Drehung bzw. Hoehenmassstab), sperren, dann die Bohrungen im Viewer daraufziehen.
// Ohne Koordinaten: Reihe mit Abstaenden oder Stationen. Dazu der Durchmesser der Bohrsaeulen und das Gelaende
// (DGM-Dateien des Nutzers): Vergleich GOK - DGM und fehlende GOK auf Klick (docs/23 §2.4).
import { html, nothing } from "lit";
import { live } from "lit/directives/live.js";
import { api, type GelaendeZeile, type SgdTreffer, type Zustand } from "./api";
import { hilfe } from "./hilfe";
import { epsgAuswahl, lagePruefen, systemText } from "./epsg";
import { S, aendern, melden, naechsteOhneLage, neu, versuchen, viewerAktualisieren, zustandUebernehmen } from "./store";
import { kalibrierungText, massstabszahl } from "../viewer/lage";
import type { Bildpunkt } from "../viewer/lage";
import type { Kalibrierung, Massstab } from "../viewer/kanal";

const zahl = (v: number | null | undefined, s = 2) =>
  v === null || v === undefined || !Number.isFinite(v) ? "" : v.toLocaleString("de-DE", { minimumFractionDigits: s, maximumFractionDigits: s });
const eingabe = (e: Event) => {
  const t = (e.target as HTMLInputElement).value.trim().replace(",", ".");
  return t === "" ? null : Number(t);
};

interface Entwurf {
  schluessel: string;                         // Unterlage + gespeicherte Kalibrierung, aus der er entstand
  massArt: "strecke" | "n";
  p1: Bildpunkt | null; p2: Bildpunkt | null; meter: number | null; n: number | null;
  hoeheArt: "gleich" | "n" | "strecke";
  h1: Bildpunkt | null; h2: Bildpunkt | null; hoeheMeter: number | null; hoeheN: number | null;
  bezug: Bildpunkt | null; x: number | null; y: number | null;
  drehung: number; epsg: number | null;
}

let e: Entwurf | null = null;
let waehlt = "";                              // welcher Punkt gerade im Plan gewaehlt wird
let neueArt: "plan" | "schnitt" = "plan";
let dgmEpsg: number | null | undefined;               // System der DGM-Dateien (undefined = das des Projekts)
let sgdRadius = 250;                                  // m um die Mitte des Projekts
let dgmRand = 100;                                    // m um die Bohrungen (DGM vom Land)
let gebaeudeRand = 100;                               // m um die Bohrungen (LoD2-Gebäude)
const sgdWahl = new Set<string>();                    // "dienst/id" der Bohrungen, die übernommen werden sollen

function schluessel(z: Zustand) {
  const u = z.unterlage;
  return u ? `${u.sha}/${u.seite}/${u.art}/${JSON.stringify(u.kalibrierung)}` : "";
}

/** Entwurf aus der gespeicherten Kalibrierung (neu, wenn sich Unterlage oder Kalibrierung auf dem Server aendern). */
function entwurf(z: Zustand): Entwurf | null {
  const u = z.unterlage;
  if (!u) return (e = null);
  if (e && e.schluessel === schluessel(z)) return e;
  const k = u.kalibrierung;
  const strecke = (m: Massstab | null | undefined) => (m && !("n" in m) ? m : null);
  const s = strecke(k?.massstab);
  const h = strecke(k?.hoehe);
  e = {
    schluessel: schluessel(z),
    massArt: k?.massstab && "n" in k.massstab ? "n" : "strecke",
    p1: s ? { u: s.u1, v: s.v1 } : null, p2: s ? { u: s.u2, v: s.v2 } : null, meter: s?.meter ?? null,
    n: k?.massstab && "n" in k.massstab ? k.massstab.n : null,
    hoeheArt: !k?.hoehe ? "gleich" : "n" in k.hoehe ? "n" : "strecke",
    h1: h ? { u: h.u1, v: h.v1 } : null, h2: h ? { u: h.u2, v: h.v2 } : null, hoeheMeter: h?.meter ?? null,
    hoeheN: k?.hoehe && "n" in k.hoehe ? k.hoehe.n : null,
    bezug: k?.bezug ? { u: k.bezug.u, v: k.bezug.v } : null, x: k?.bezug?.x ?? null, y: k?.bezug?.y ?? null,
    drehung: k?.drehung ?? 0, epsg: k?.epsg ?? z.viewer.epsg ?? null,
  };
  return e;
}

/** Vollstaendiger Entwurf -> Kalibrierung (sonst null). */
function kalibrierung(z: Zustand, gesperrt = false): Kalibrierung | null {
  const d = e;
  const u = z.unterlage;
  if (!d || !u) return null;
  let massstab: Massstab | null = null;
  if (d.massArt === "n" && d.n && d.n > 0) massstab = { n: d.n };
  if (d.massArt === "strecke" && d.p1 && d.p2 && d.meter && d.meter > 0) {
    massstab = { u1: d.p1.u, v1: d.p1.v, u2: d.p2.u, v2: d.p2.v, meter: d.meter };
  }
  if (!massstab || !d.bezug || d.x === null || d.y === null) return null;
  let hoehe: Massstab | null = null;
  if (u.art === "schnitt" && d.hoeheArt === "n" && d.hoeheN && d.hoeheN > 0) hoehe = { n: d.hoeheN };
  if (u.art === "schnitt" && d.hoeheArt === "strecke" && d.h1 && d.h2 && d.hoeheMeter && d.hoeheMeter > 0) {
    hoehe = { u1: d.h1.u, v1: d.h1.v, u2: d.h2.u, v2: d.h2.v, meter: d.hoeheMeter };
  }
  return { massstab, hoehe, bezug: { ...d.bezug, x: d.x, y: d.y }, drehung: u.art === "plan" ? d.drehung : 0,
           epsg: u.art === "plan" ? d.epsg : null, gesperrt };
}

/** Vorschau im Viewer und Hilfsmarken nach jeder Eingabe. */
function vorschau() {
  const z = S.z!;
  S.entwurf = kalibrierung(z);
  const v = S.viewer;
  if (v && e) {
    v.editor.hilfsmarken({ strecke: e.massArt === "strecke" ? [e.p1, e.p2] : [], hoehe: e.hoeheArt === "strecke" ? [e.h1, e.h2] : [],
                           bezug: e.bezug });
    if (S.entwurf) v.editor.vorschau(S.entwurf);
  }
  neu();
}

async function punkt(welcher: "p1" | "p2" | "h1" | "h2" | "bezug") {
  const v = S.viewer;
  if (!v || !e) return;
  waehlt = welcher;
  neu();
  const p = await v.editor.bildpunktWaehlen();
  waehlt = "";
  if (!p || !e || S.z?.unterlage?.kalibrierung?.gesperrt) {       // abgebrochen (Esc, Sperren, Ziehen)
    neu();
    return;
  }
  e[welcher] = p;
  vorschau();
}

async function uebernehmen(sperren: boolean) {
  S.viewer?.editor.waehlenAbbrechen();                  // offene Punktwahl blockiert sonst das Ziehen
  const k = kalibrierung(S.z!, sperren);
  if (!k) {
    melden("Für die Kalibrierung fehlen Maßstab oder Bezugspunkt.", "warn");
    return;
  }
  if (await aendern([{ op: "kalibrierung", wert: k }])) {
    S.entwurf = null;
    melden(sperren ? "Plan kalibriert und gesperrt – jetzt die Bohrungen ziehen." : "Kalibrierung übernommen.", "ok");
    await S.viewer?.ansicht(S.z?.unterlage?.art === "schnitt" ? "sued" : "oben");     // Plan in neuer Groesse zeigen
  }
}

async function sperre(an: boolean) {
  const u = S.z!.unterlage;
  if (!u?.kalibrierung) return;
  await aendern([{ op: "kalibrierung", wert: { ...u.kalibrierung, gesperrt: an } }]);
}

async function hochladen(ev: Event) {
  const input = ev.target as HTMLInputElement;
  const f = input.files?.[0];
  input.value = "";
  if (!f) return;
  const z = await versuchen(() => api.unterlage(S.sig, f, neueArt, 0), "Unterlage wird gelesen …");
  if (z) {
    zustandUebernehmen(z);
    S.entwurf = null;
    neu();
    await viewerAktualisieren();
    await S.viewer?.lageModus(true);
    await S.viewer?.ansicht(z.unterlage?.art === "schnitt" ? "sued" : "oben");
  }
}

async function seiteOderArt(seite: number, art: string) {
  const z = await versuchen(() => api.unterlageSeite(S.sig, seite, art), "Seite wird gelesen …");
  if (z) {
    zustandUebernehmen(z);
    S.entwurf = null;
    neu();
    await viewerAktualisieren();
    await S.viewer?.ansicht(art === "schnitt" ? "sued" : "oben");
  }
}

async function unterlageEntfernen() {
  if (!confirm("Unterlage mit ihrer Kalibrierung entfernen? Gesetzte Bohrungen behalten ihre Lage.")) return;
  const z = await versuchen(() => api.unterlageEntfernen(S.sig));
  if (z) {
    zustandUebernehmen(z);
    S.entwurf = null;
    neu();
    await viewerAktualisieren();
  }
}

// ------------------------------------------------------------------ Teile
const abschnitt = (titel: unknown, inhalt: unknown, offen = true) =>
  html`<details class="abschnitt" ?open=${offen}><summary>${titel}</summary><div class="abschnitt-inhalt">${inhalt}</div></details>`;

function punktKnopf(titel: string, welcher: "p1" | "p2" | "h1" | "h2" | "bezug", p: Bildpunkt | null, aus: boolean) {
  return html`<button class=${`punkt ${waehlt === welcher ? "aktiv" : ""} ${p ? "gesetzt" : ""}`} ?disabled=${aus}
    @click=${() => punkt(welcher)}>${waehlt === welcher ? "… im Plan klicken" : p ? `${titel} ✓` : titel}</button>`;
}

/** Passt der Bezugspunkt zum gewaehlten System? (Hinweis, keine Sperre) */
function systemPruefung(d: Entwurf) {
  const p = lagePruefen(d.epsg, d.x, d.y);
  return p ? html`<p class=${`klein ${p.ok ? "ok" : "warn"}`}>${p.ok ? "✓" : "⚠"} ${p.text}</p>` : nothing;
}

function kalibrierenTeil(z: Zustand) {
  const u = z.unterlage!;
  const d = entwurf(z)!;
  const gesperrt = !!u.kalibrierung?.gesperrt;
  const plan = u.art === "plan";
  const px = d.p1 && d.p2 ? Math.hypot(d.p2.u - d.p1.u, d.p2.v - d.p1.v) : null;
  const k = kalibrierung(z);
  const n = k ? massstabszahl(k.massstab, u.mm_pro_px) : null;
  const mitLage = z.viewer.bohrungen.filter((b) => b.x !== null && (plan ? !/Plan|Viewer/.test(b.quelle) : b.gok_bekannt));
  return html`
    <p class=${`status ${u.kalibrierung ? (gesperrt ? "ok" : "") : "warn"}`}>
      ${u.kalibrierung ? html`${gesperrt ? "🔒 gesperrt · " : ""}${kalibrierungText(u)}${plan ? ` · ${systemText(u.kalibrierung.epsg)}` : ""}` : "nicht kalibriert"}
      ${S.entwurf && JSON.stringify({ ...S.entwurf, gesperrt: false }) !== JSON.stringify({ ...(u.kalibrierung ?? {}), gesperrt: false })
        ? html`<br><span class="leise">Vorschau: ${kalibrierungText(u, S.entwurf)} (noch nicht übernommen)</span>` : nothing}
    </p>
    ${gesperrt ? html`
      <p class="leise klein">Der Plan liegt fest. ${plan ? "Bohrungen unten mit „Punkte setzen“ in den Plan klicken oder im Viewer ziehen – nur in x/y"
        : "Bohrungen im Viewer ziehen – entlang der Station; die Höhe nur ohne GOK aus dem PDF"}.</p>
      <button @click=${() => sperre(false)}>🔓 Entsperren (neu kalibrieren)</button>` : html`
      <fieldset class="gruppe">
        <legend>1 · Maßstab ${hilfe("massstab")}</legend>
        <div class="umschalter">
          <label><input type="radio" name="massart" .checked=${d.massArt === "strecke"} @change=${() => { d.massArt = "strecke"; vorschau(); }}> Strecke messen</label>
          <label><input type="radio" name="massart" .checked=${d.massArt === "n"} @change=${() => { d.massArt = "n"; vorschau(); }}> 1:n eingeben</label>
        </div>
        ${d.massArt === "strecke" ? html`
          <div class="zeile">${punktKnopf("Punkt 1", "p1", d.p1, false)}${punktKnopf("Punkt 2", "p2", d.p2, false)}</div>
          <div class="zeile">
            <span class="leise klein">${px ? `gemessen ${zahl(px, 0)} px` : "zwei Punkte anklicken"}</span>
            <label class="inline">wahre Länge <input type="number" step="0.01" min="0" class="kurz" .value=${live(d.meter === null ? "" : String(d.meter))}
              @input=${(ev: Event) => { d.meter = eingabe(ev); vorschau(); }}> m</label>
          </div>` : html`
          <label class="inline">Maßstab 1: <input type="number" step="1" min="1" class="kurz" .value=${live(d.n === null ? "" : String(d.n))}
            @input=${(ev: Event) => { d.n = eingabe(ev); vorschau(); }}></label>`}
        ${n ? html`<p class="leise klein">ergibt 1:${Math.round(n).toLocaleString("de-DE")}</p>` : nothing}
      </fieldset>
      ${plan ? nothing : html`
        <fieldset class="gruppe">
          <legend>Höhenmaßstab ${hilfe("hoehe")}</legend>
          <div class="umschalter">
            <label><input type="radio" name="hoeheart" .checked=${d.hoeheArt === "gleich"} @change=${() => { d.hoeheArt = "gleich"; vorschau(); }}> wie Länge</label>
            <label><input type="radio" name="hoeheart" .checked=${d.hoeheArt === "n"} @change=${() => { d.hoeheArt = "n"; vorschau(); }}> 1:n</label>
            <label><input type="radio" name="hoeheart" .checked=${d.hoeheArt === "strecke"} @change=${() => { d.hoeheArt = "strecke"; vorschau(); }}> messen</label>
          </div>
          ${d.hoeheArt === "n" ? html`<label class="inline">Höhe 1: <input type="number" step="1" min="1" class="kurz"
              .value=${live(d.hoeheN === null ? "" : String(d.hoeheN))} @input=${(ev: Event) => { d.hoeheN = eingabe(ev); vorschau(); }}></label>` : nothing}
          ${d.hoeheArt === "strecke" ? html`
            <div class="zeile">${punktKnopf("Höhe oben", "h1", d.h1, false)}${punktKnopf("Höhe unten", "h2", d.h2, false)}</div>
            <label class="inline">Höhenunterschied <input type="number" step="0.01" min="0" class="kurz"
              .value=${live(d.hoeheMeter === null ? "" : String(d.hoeheMeter))} @input=${(ev: Event) => { d.hoeheMeter = eingabe(ev); vorschau(); }}> m</label>` : nothing}
        </fieldset>`}
      <fieldset class="gruppe">
        <legend>2 · Bezugspunkt ${hilfe("bezug")}</legend>
        <div class="zeile">${punktKnopf("Punkt im Plan wählen", "bezug", d.bezug, false)}</div>
        <div class="zeile">
          <label class="feld schmal"><span>${plan ? "Rechtswert" : "Station [m]"}</span>
            <input type="number" step="0.01" .value=${live(d.x === null ? "" : String(d.x))} @input=${(ev: Event) => { d.x = eingabe(ev); vorschau(); }}></label>
          <label class="feld schmal"><span>${plan ? "Hochwert" : "Höhe [m NHN]"}</span>
            <input type="number" step="0.01" .value=${live(d.y === null ? "" : String(d.y))} @input=${(ev: Event) => { d.y = eingabe(ev); vorschau(); }}></label>
        </div>
        ${plan ? html`
          <label class="feld breit"><span>Koordinatensystem (EPSG) ${hilfe("epsg")}</span>
            ${epsgAuswahl(d.epsg, (c) => { d.epsg = c; vorschau(); })}</label>
          ${systemPruefung(d)}` : nothing}
        ${mitLage.length ? html`
          <label class="inline klein">oder von Bohrung
            <select @change=${(ev: Event) => {
              const b = z.viewer.bohrungen.find((x) => x.id === (ev.target as HTMLSelectElement).value);
              if (b) { d.x = b.x; d.y = plan ? b.y : b.gok; vorschau(); }
            }}>
              <option value="">–</option>
              ${mitLage.map((b) => html`<option value=${b.id}>${b.code}</option>`)}
            </select></label>` : nothing}
      </fieldset>
      ${plan ? html`
        <fieldset class="gruppe">
          <legend>3 · Drehung ${hilfe("drehung")}</legend>
          <div class="zeile">
            <label class="inline"><input type="number" step="0.1" class="kurz" .value=${live(String(d.drehung))}
              @input=${(ev: Event) => { d.drehung = eingabe(ev) ?? 0; vorschau(); }}> ° gegen den Uhrzeigersinn</label>
          </div>
        </fieldset>` : nothing}
      <div class="zeile knopfzeile">
        <button ?disabled=${!k} @click=${() => uebernehmen(false)}>Übernehmen</button>
        <button class="primaer" ?disabled=${!k} @click=${() => uebernehmen(true)}>🔒 Übernehmen und sperren</button>
        ${hilfe("sperren")}
      </div>
      ${u.kalibrierung ? html`<button class="link klein" @click=${() => aendern([{ op: "kalibrierung", wert: null }])}>Kalibrierung zurücksetzen</button>` : nothing}`}`;
}

function unterlageTeil(z: Zustand) {
  const u = z.unterlage;
  if (!u) {
    return html`
      <p class="leise klein">Lageplan (von oben) oder Längsschnitt (von der Seite) als PDF – er liegt im Viewer unter den Bohrungen.</p>
      <div class="umschalter">
        <label><input type="radio" name="neueart" .checked=${neueArt === "plan"} @change=${() => { neueArt = "plan"; }}> Lageplan</label>
        <label><input type="radio" name="neueart" .checked=${neueArt === "schnitt"} @change=${() => { neueArt = "schnitt"; }}> Längsschnitt</label>
      </div>
      <label class="datei-knopf"><input type="file" accept=".pdf,application/pdf" @change=${hochladen}>PDF wählen …</label>`;
  }
  return html`
    <p><b>${u.name}</b> <span class="leise">· ${u.art === "plan" ? "Lageplan" : "Längsschnitt"}</span></p>
    <div class="zeile">
      ${(u.seiten ?? 1) > 1 ? html`<label class="inline">Seite <select @change=${(ev: Event) => seiteOderArt(Number((ev.target as HTMLSelectElement).value), u.art)}>
          ${Array.from({ length: u.seiten }, (_, i) => html`<option value=${i} .selected=${i === u.seite}>${i + 1}</option>`)}
        </select></label>` : nothing}
      <label class="inline">Ansicht <select @change=${(ev: Event) => seiteOderArt(u.seite, (ev.target as HTMLSelectElement).value)}>
        <option value="plan" .selected=${u.art === "plan"}>Lageplan</option>
        <option value="schnitt" .selected=${u.art === "schnitt"}>Längsschnitt</option>
      </select></label>
    </div>
    <label class="inline">Deckkraft ${hilfe("deckkraft")}
      <input type="range" min="0.1" max="1" step="0.05" .value=${String(S.viewer?.editor.deckkraft ?? 0.85)}
        @input=${(ev: Event) => { if (S.viewer) { S.viewer.editor.deckkraft = Number((ev.target as HTMLInputElement).value); S.viewer.editor.bildSichtbarkeit(); } }}></label>
    <button class="link klein" @click=${unterlageEntfernen}>Unterlage entfernen</button>`;
}

function bohrungenTeil(z: Zustand) {
  const u = z.unterlage;
  const frei = !u || !!u.kalibrierung?.gesperrt;
  const ohne = z.viewer.bohrungen.filter((b) => b.x === null);
  const reihe = z.lage_modus === "reihe";
  const punkte = !reihe && u?.art === "plan" && !!u.kalibrierung?.gesperrt;
  return html`
    ${!frei ? html`<p class="warnung">Erst kalibrieren und sperren (🔒) – dann Punkte setzen oder Bohrungen ziehen.</p>` : nothing}
    ${punkte ? punkteTeil(z) : nothing}
    ${ohne.length ? html`
      <p class="klein">Ohne Lage (${ohne.length}) – ${punkte ? "anklicken = als Nächste setzen, oder" : ""} in den Viewer ziehen
        ${hilfe("ohne_lage")}</p>
      <div class="parkplatz">
        ${ohne.map((b) => html`<span class=${`park ${frei ? "" : "gesperrt"} ${S.punktModus && S.naechste === b.id ? "aktiv" : ""}`}
          title=${punkte ? "Klick: als nächste Bohrung setzen · Ziehen: direkt in den Viewer" : "In den Viewer ziehen"}
          @pointerdown=${(ev: PointerEvent) => S.viewer?.editor.ziehenStart(ev, b.id, true)}
          @click=${() => { if (punkte) punktModus(true, b.id); }}>${b.code}</span>`)}
      </div>` : html`<p class="leise klein">Alle Bohrungen im Modell haben eine Lage.</p>`}
    ${punkte ? punktListe(z) : nothing}
    ${reihe ? reiheTeil(z) : nothing}`;
}

/** Punktmodus an/aus; mit Bohrung: sie bekommt den naechsten Punkt. */
function punktModus(an: boolean, naechste?: string) {
  S.punktModus = an;
  if (naechste !== undefined) S.naechste = naechste;
  else if (an && !S.naechste) S.naechste = naechsteOhneLage();
  S.viewer?.editor.punktModusSetzen(an);
  neu();
}

/** Punkte setzen: Modus, welche Bohrung der naechste Klick bekommt (danach automatisch die naechste ohne Lage). */
function punkteTeil(z: Zustand) {
  const ohne = z.viewer.bohrungen.filter((b) => b.x === null);
  const mit = z.viewer.bohrungen.filter((b) => b.x !== null);
  return html`
    <div class="zeile">
      <button class=${S.punktModus ? "primaer" : ""} @click=${() => punktModus(!S.punktModus)}>
        ${S.punktModus ? "● Punkte setzen – Klick in den Plan" : "＋ Punkte im Plan setzen"}</button>
      ${S.punktModus ? html`<button class="leise-knopf" @click=${() => punktModus(false)}>Fertig (Esc)</button>` : nothing}
      ${hilfe("punkte")}
    </div>
    ${S.punktModus ? html`
      <label class="feld breit"><span>Nächster Klick setzt</span>
        <select class="naechste" @change=${(ev: Event) => { S.naechste = (ev.target as HTMLSelectElement).value; neu(); }}>
          <option value="" .selected=${!S.naechste}>– freien Punkt (später zuordnen) –</option>
          ${ohne.length ? html`<optgroup label="Ohne Lage">
            ${ohne.map((b) => html`<option value=${b.id} .selected=${S.naechste === b.id}>${b.code}</option>`)}</optgroup>` : nothing}
          ${mit.length ? html`<optgroup label="Mit Lage (neu setzen)">
            ${mit.map((b) => html`<option value=${b.id} .selected=${S.naechste === b.id}>${b.code}</option>`)}</optgroup>` : nothing}
        </select></label>
      <p class="leise klein">Danach ist automatisch die nächste Bohrung ohne Lage dran.</p>` : nothing}`;
}

/** Gesetzte Punkte: Bohrungen mit Lage vom Plan und freie Punkte; zuordnen, umhaengen, loeschen. */
function punktListe(z: Zustand) {
  const vomPlan = z.viewer.bohrungen.filter((b) => b.x !== null && /Plan|Viewer/.test(b.quelle));
  const alle = z.viewer.bohrungen;
  const ohne = alle.filter((b) => b.x === null);
  if (!vomPlan.length && !z.punkte.length) return nothing;
  const lage = (x: number | null, y: number | null) => html`<span class="leise klein">R ${zahl(x)}<br>H ${zahl(y)}</span>`;
  return html`
    <p class="klein">Gesetzte Punkte (${vomPlan.length + z.punkte.length})</p>
    <table class="tabelle kompakt punkte">
      <tbody>
        ${z.punkte.map((pt) => html`
          <tr class=${`frei ${S.viewer?.editor.punktGewaehlt === pt.id ? "gewaehlt" : ""}`}>
            <td><button class="link" title="Im Viewer wählen" @click=${() => { S.viewer?.editor.punktWaehlen(pt.id); neu(); }}>◆ ${pt.id}</button></td>
            <td>${lage(pt.x, pt.y)}</td>
            <td><select aria-label=${`${pt.id} zuordnen`} @change=${(ev: Event) => {
                const ziel = (ev.target as HTMLSelectElement).value;
                if (ziel) void aendern([{ op: "punkt_zuordnen", punkt: pt.id, bohrung: ziel }]);
              }}>
              <option value="" selected>– Bohrung zuordnen –</option>
              ${ohne.length ? html`<optgroup label="Ohne Lage">${ohne.map((b) => html`<option value=${b.id}>${b.code}</option>`)}</optgroup>` : nothing}
              <optgroup label="Mit Lage (ersetzen)">${alle.filter((b) => b.x !== null).map((b) => html`<option value=${b.id}>${b.code}</option>`)}</optgroup>
            </select></td>
            <td><button class="symbol" title="Punkt löschen" @click=${() => aendern([{ op: "punkt_loeschen", punkt: pt.id }])}>✕</button></td>
          </tr>`)}
        ${vomPlan.map((b) => html`
          <tr class=${S.viewer?.editor.ausgewaehlt === b.id ? "gewaehlt" : ""}>
            <td><button class="link" title="Im Viewer wählen" @click=${() => { void S.viewer?.nadelWaehlen(b.id); neu(); }}>● ${b.code}</button></td>
            <td>${lage(b.x, b.y)}</td>
            <td><select aria-label=${`${b.code} umhängen`} @change=${(ev: Event) => {
                const ziel = (ev.target as HTMLSelectElement).value;
                if (ziel === "-") void aendern([{ op: "lage_loesen", id: b.id }]);
                else if (ziel && ziel !== b.id) void aendern([{ op: "lage_umhaengen", id: b.id, nach: ziel }]);
              }}>
              <option value=${b.id} selected>${b.code}</option>
              <option value="-">– Zuordnung lösen (freier Punkt) –</option>
              ${ohne.length ? html`<optgroup label="Andere Bohrung (ohne Lage)">${ohne.map((o) => html`<option value=${o.id}>${o.code}</option>`)}</optgroup>` : nothing}
            </select></td>
            <td><button class="symbol" title="Lage entfernen (Bohrung wieder ohne Lage)" @click=${() => aendern([{ op: "lage_entfernen", id: b.id }])}>✕</button></td>
          </tr>`)}
      </tbody>
    </table>`;
}

function reiheTeil(z: Zustand) {
  const ids = z.reihe.map((r) => r.id);
  const schieben = (i: number, um: number) => {
    const neu_ = [...ids];
    const [x] = neu_.splice(i, 1);
    neu_.splice(Math.max(0, Math.min(neu_.length, i + um)), 0, x);
    void aendern([{ op: "reihe", reihenfolge: neu_ }], { leise: true });
  };
  return html`
    <div class="zeile">
      <label class="inline">Standardabstand ${hilfe("standardabstand")}
        <input type="number" step="1" min="1" class="kurz" .value=${live(String(z.reihe_standard))}
          @change=${(ev: Event) => aendern([{ op: "reihe", standard: eingabe(ev) }])}> m</label>
    </div>
    <table class="tabelle kompakt reihe">
      <thead><tr><th></th><th>Bohrung</th><th>Abstand [m] ${hilfe("reihe")}</th><th>Station [m]</th></tr></thead>
      <tbody>
        ${z.reihe.map((r, i) => html`
          <tr>
            <td class="pfeile"><button class="symbol" ?disabled=${i === 0} title="nach vorn" @click=${() => schieben(i, -1)}>▲</button><button class="symbol"
              ?disabled=${i === ids.length - 1} title="nach hinten" @click=${() => schieben(i, 1)}>▼</button></td>
            <td>${r.code}</td>
            <td><input type="number" step="0.1" min="0" class="kurz" ?disabled=${i === 0} .value=${live(r.abstand === null ? "" : String(r.abstand))}
              @change=${(ev: Event) => aendern([{ op: "reihe", abstand: { [r.id]: eingabe(ev) } }], { leise: true })}></td>
            <td><input type="number" step="0.1" class="kurz" .value=${live(String(r.station))} title=${r.quelle_text}
              @change=${(ev: Event) => aendern([{ op: "reihe", station: { [r.id]: eingabe(ev) } }], { leise: true })}></td>
          </tr>`)}
      </tbody>
    </table>`;
}

// ------------------------------------------------------------------ Gelaende (DGM)
async function dgmHochladen(ev: Event) {
  const input = ev.target as HTMLInputElement;
  const dateien = [...(input.files ?? [])];
  input.value = "";
  if (!dateien.length) return;
  const epsg = dgmEpsg === undefined ? S.z?.viewer.epsg ?? null : dgmEpsg;
  const z = await versuchen(() => api.dgm(S.sig, dateien, epsg), "DGM wird gelesen …");
  if (z) {
    zustandUebernehmen(z);
    neu();
    const warnungen = z.gelaende?.pruefung?.warnungen.length ?? 0;
    melden(warnungen ? "DGM geladen – Hinweise zum Vergleich beachten." : "DGM geladen.", warnungen ? "warn" : "ok");
  }
}

async function dgmAbrufen() {
  const z = await versuchen(() => api.dgmAbruf(S.sig, dgmRand), "DGM wird beim Land abgerufen …");
  if (z) {
    zustandUebernehmen(z);
    neu();
    const warnungen = z.gelaende?.pruefung?.warnungen.length ?? 0;
    melden(warnungen ? "DGM vom Land geladen – Hinweise zum Vergleich beachten." : "DGM vom Land geladen.", warnungen ? "warn" : "ok");
  }
}

/** Abruf beim Land: nur auf Klick, der Knopf sagt, was gesendet wird (D88). */
function dgmVomLand(z: Zustand) {
  if (z.lage_modus !== "koordinaten") return nothing;
  return html`
    <div class="zeile">
      <label class="inline">Rand <input type="number" min="0" max="1000" step="25" class="kurz" aria-label="Rand um die Bohrungen"
        .value=${live(String(dgmRand))} @change=${(ev: Event) => { dgmRand = eingabe(ev) ?? 100; }}> m</label>
      <button @click=${dgmAbrufen} title="Sendet den Ausschnitt um die Bohrungen an den Dienst des Landes">
        DGM vom Land abrufen</button>${hilfe("dgm_land")}
    </div>
    <p class="leise klein">Brandenburg mit Berlin und NRW (DGM1, WCS). Sendet den Ausschnitt um die Bohrungen an den Dienst.</p>`;
}

async function dgmEntfernen() {
  if (!confirm("DGM aus dem Projekt entfernen? Übernommene GOK bleiben (Quelle DGM).")) return;
  const z = await versuchen(() => api.dgmEntfernen(S.sig));
  if (z) {
    zustandUebernehmen(z);
    neu();
  }
}

const STATUS: Record<GelaendeZeile["status"], [string, string]> = {
  ok: ["✓", "ok"], abweichung: ["⚠ weicht ab", "warn"], ohne_gok: ["GOK fehlt", ""], aus_dgm: ["aus dem DGM", "leise"],
  ausserhalb: ["außerhalb", "leise"], ohne_lage: ["ohne Lage", "leise"], anderes_system: ["anderes EPSG", "warn"],
};

const mitVorzeichen = (v: number | null) =>
  v === null ? "" : Math.abs(v) < 0.005 ? zahl(0) : `${v > 0 ? "+" : ""}${zahl(v)}`;   // kein "-0,00"

function gelaendeTeil(z: Zustand) {
  const g = z.gelaende;
  const datei = (text: string) => html`<label class="datei-knopf"><input type="file" multiple aria-label="DGM-Dateien"
    accept=".xyz,.txt,.csv,.asc,.tif,.tiff,.zip,.gz" @change=${dgmHochladen}>${text}</label>`;
  const system = dgmEpsg === undefined ? z.viewer.epsg ?? null : dgmEpsg;
  const wahl = html`<label class="feld breit"><span>System der Datei (XYZ, ASCII) ${hilfe("dgm_epsg")}</span>
    ${epsgAuswahl(system, (c) => { dgmEpsg = c; neu(); }, "System der DGM-Datei")}</label>`;
  if (!g) {
    return html`
      <p class="leise klein">DGM-Kachel(n) des Landes (Open Data, z. B. DGM1) als XYZ, ASCII-Raster oder GeoTIFF, auch als
        ZIP – Höhen in m NHN. Damit prüft die App die GOK, schlägt fehlende vor und legt das Gelände ins Modell.</p>
      ${dgmVomLand(z)}
      ${wahl}
      ${datei("DGM-Dateien wählen …")}`;
  }
  const i = g.info;
  const pr = g.pruefung;
  const q = i.quelle;
  return html`
    <p><b>${i.name}</b><br><span class="leise klein">${systemText(i.epsg)} · Raster ${zahl(i.dx, 1)} m ·
      ${i.spalten.toLocaleString("de-DE")} × ${i.zeilen.toLocaleString("de-DE")} · ${zahl(i.zmin, 1)} – ${zahl(i.zmax, 1)} m NHN</span></p>
    ${q ? html`<p class="leise klein">${q.anbieter} · <a href=${q.beleg} target="_blank" rel="noopener">${q.lizenz}</a> ·
      ${q.namensnennung} · abgerufen ${q.abgerufen}</p>` : nothing}
    ${g.fehler ? html`<p class="warnung klein">${g.fehler}</p>` : nothing}
    ${pr ? html`
      <table class="tabelle kompakt gelaende">
        <thead><tr><th>Bohrung</th><th class="zahl">GOK</th><th class="zahl">DGM</th><th class="zahl">Δ [m]</th><th></th></tr></thead>
        <tbody>
          ${pr.zeilen.map((r) => html`
            <tr class=${STATUS[r.status][1]}>
              <td><button class="link" title="Im Viewer wählen" @click=${() => { void S.viewer?.nadelWaehlen(r.id); neu(); }}>${r.code}</button></td>
              <td class="zahl">${zahl(r.gok)}</td>
              <td class="zahl">${zahl(r.dgm)}</td>
              <td class="zahl">${mitVorzeichen(r.differenz)}</td>
              <td class=${`klein ${STATUS[r.status][1]}`}>${r.status === "ohne_gok"
                ? html`<button class="klein" title="GOK aus dem DGM übernehmen (Quelle DGM)"
                    @click=${() => aendern([{ op: "gok_aus_dgm", ids: [r.id] }])}>übernehmen</button>`
                : STATUS[r.status][0]}</td>
            </tr>`)}
        </tbody>
      </table>
      ${pr.verglichen ? html`<p class="leise klein">${pr.verglichen} verglichen · Median ${mitVorzeichen(pr.median)} m ·
        größte Abweichung ${zahl(pr.max)} m (unauffällig bis ${zahl(pr.toleranz, 1)} m)</p>` : nothing}
      ${pr.warnungen.map((w) => html`<p class="warnung klein">⚠ ${w}</p>`)}
      ${pr.vorschlaege > 1 ? html`<button @click=${() => aendern([{ op: "gok_aus_dgm" }])}>
        Alle ${pr.vorschlaege} fehlenden GOK aus dem DGM übernehmen</button>` : nothing}` : nothing}
    ${dgmVomLand(z)}
    ${wahl}
    <div class="zeile">${datei("Andere DGM-Dateien …")}
      <button class="link klein" @click=${dgmEntfernen}>DGM entfernen</button></div>`;
}

// ------------------------------------------------------------------ Bohrungen der Laender (SGD)
async function sgdAbfragen() {
  const z = await versuchen(() => api.sgdAbfrage(S.sig, sgdRadius), "Dienste der Länder werden abgefragt …");
  if (!z?.sgd) return;
  zustandUebernehmen(z);
  sgdWahl.clear();
  neu();
  const s = z.sgd;
  melden(`${s.treffer.length} Bohrungen der Länder im Umkreis von ${zahl(s.radius, 0)} m` +
         (s.fehler.length ? ` – ${s.fehler.length} Dienst(e) ohne Antwort` : ""), s.fehler.length ? "warn" : "ok");
}

async function sgdUebernehmen() {
  const auswahl = [...sgdWahl].map((k) => ({ dienst: k.slice(0, k.indexOf("/")), id: k.slice(k.indexOf("/") + 1) }));
  const r = await versuchen(() => api.sgdUebernehmen(S.sig, auswahl), "Schichtdaten werden beim Land geholt …");
  if (!r) return;
  zustandUebernehmen(r.zustand);
  sgdWahl.clear();
  for (const m of r.meldungen) melden(m, "ok");
  await viewerAktualisieren();
  neu();
}

/** Warum eine Bohrung des Landes nicht ins Modell kann - sonst sieht man sie in der Liste und weiss nicht, warum. */
function nichtUebernehmbar(s: NonNullable<Zustand["sgd"]>) {
  const offen = s.treffer.filter((t) => !t.uebernehmbar && !t.uebernommen && !t.gutachten);
  if (!offen.length) return nothing;
  const land = (d: string) => s.quellen.find((q) => q.dienst === d)?.land ?? d;
  const zahlen = (art: SgdTreffer["schichten"]) => {
    const liste = offen.filter((t) => t.schichten === art);
    return liste.length ? `${liste.length} (${[...new Set(liste.map((t) => land(t.dienst)))].join(", ")})` : "";
  };
  const teile = [
    zahlen("grafik") && `${zahlen("grafik")} nur mit Kopfdaten: das Land gibt das Schichtenverzeichnis nur als Bild heraus (Profil ↗), nicht als Daten`,
    zahlen("keine") && `${zahlen("keine")} ohne Schichtenverzeichnis`,
    zahlen("ohne Petrographie") && `${zahlen("ohne Petrographie")} mit Schichten ohne Petrographie`,
  ].filter(Boolean);
  return html`<p class="leise klein sgd-warum">Nicht übernehmbar: ${teile.join("; ")}. Ohne Schichten entsteht kein Modell –
    sie zu erfinden wäre falsch. Lage, GOK und Teufe sehen Sie hier; die Schichten im Profil des Landes. Übernehmbar sind
    Bohrungen mit Schichtdaten in BoreholeML (NRW, Baden-Württemberg).</p>`;
}

function sgdSchichten(t: SgdTreffer) {
  if (t.gutachten) return html`<span class="ok" title="Dieselbe Bohrung im Gutachten">= ${t.gutachten}</span>`;
  if (t.uebernommen) return html`<span class="ok">✓ im Projekt</span>`;
  if (t.schichten === "boreholeml") return html`${t.schichten_n} Schichten`;
  if (t.schichten === "grafik" && t.profil) return html`<a href=${t.profil} target="_blank" rel="noopener">Profil ↗</a>`;
  return html`<span class="leise">${t.schichten === "ohne Petrographie" ? "ohne Petrographie" : "keine Schichten"}</span>`;
}

// ------------------------------------------------------------------ Gebaeude der Laender (LoD2)
async function gebaeudeAbrufen() {
  const z = await versuchen(() => api.gebaeudeAbruf(S.sig, gebaeudeRand), "Gebäude werden beim Land abgerufen …");
  if (z) {
    zustandUebernehmen(z);
    neu();
    melden(`${z.gebaeude?.anzahl ?? 0} Gebäude geladen – im Modell als Umgebung.`, "ok");
  }
}

async function gebaeudeEntfernen() {
  const z = await versuchen(() => api.gebaeudeEntfernen(S.sig));
  if (z) {
    zustandUebernehmen(z);
    neu();
  }
}

/** LoD2 der Länder: Kacheln 1 × 1 km, nur auf Klick; der Knopf sagt, was gesendet wird (D88). */
function gebaeudeTeil(z: Zustand) {
  if (z.lage_modus !== "koordinaten") return html`<p class="leise klein">Nur mit Lage nach Koordinaten.</p>`;
  const g = z.gebaeude;
  const abruf = html`
    <div class="zeile">
      <label class="inline">Rand <input type="number" min="0" max="1000" step="25" class="kurz" aria-label="Rand der Gebäude"
        .value=${live(String(gebaeudeRand))} @change=${(ev: Event) => { gebaeudeRand = eingabe(ev) ?? 100; }}> m</label>
      <button @click=${gebaeudeAbrufen} title="Lädt die Kacheln (1 × 1 km) um die Bohrungen beim Land">
        ${g ? "Gebäude neu abrufen" : "Gebäude vom Land abrufen"}</button>${hilfe("gebaeude")}
    </div>`;
  if (!g) {
    return html`
      <p class="leise klein">3D-Gebäudemodelle LoD2 von Berlin, Brandenburg und NRW (CityGML, m NHN) als Umgebung im Modell und
        im IFC. Lädt die Kacheln von 1 × 1 km um die Bohrungen – das verrät die Lage des Projekts auf etwa 1 km.</p>
      ${abruf}`;
  }
  const q = g.quelle;
  return html`
    <p><b>${g.anzahl.toLocaleString("de-DE")} Gebäude</b> · ${g.flaechen.toLocaleString("de-DE")} Flächen ·
      ${q.kacheln} Kachel${q.kacheln === 1 ? "" : "n"} <span class="leise klein">· abgerufen ${q.abgerufen}</span></p>
    ${q.dienste.map((d) => html`<p class="leise klein">${d.anbieter} · <a href=${d.beleg} target="_blank" rel="noopener">${d.lizenz}</a> ·
      ${d.namensnennung}</p>`)}
    ${q.ohne_kachel.length ? html`<p class="leise klein">ohne Kachel beim Land: ${q.ohne_kachel.join(", ")}</p>` : nothing}
    ${q.fehler.map((f) => html`<p class="warnung klein">⚠ ${f}</p>`)}
    ${g.hinweis ? html`<p class="warnung klein">⚠ ${g.hinweis}</p>` : nothing}
    <p class="leise klein">Im Viewer mit dem Knopf „Gebäude“ ein- und ausblendbar.</p>
    ${abruf}
    <button class="link klein" @click=${gebaeudeEntfernen}>Gebäude entfernen</button>`;
}

function sgdTeil(z: Zustand) {
  if (z.lage_modus === "reihe") return html`<p class="leise klein">Nur mit Lage nach Koordinaten.</p>`;
  const s = z.sgd;
  const kopf = html`
    <p class="leise klein">Bohrungen aus den Datenbanken der Geologischen Dienste um die Mitte des Projekts.
      <b>Die Abfrage sendet die Lage des Projekts an den Dienst des Landes.</b></p>
    <div class="zeile">
      <label class="inline">Umkreis <input type="number" min="10" max="2000" step="50" class="kurz" aria-label="Umkreis der Abfrage"
        .value=${live(String(sgdRadius))} @change=${(ev: Event) => { sgdRadius = eingabe(ev) ?? 250; }}> m</label>
      <button @click=${sgdAbfragen}>${s ? "Neu abfragen" : "Abfragen"}</button>
    </div>`;
  if (!s) return kopf;
  const gp = s.gegenprobe;
  const gpOk = gp.anzahl > 0 && (gp.lage_max ?? 0) <= 1 && (gp.gok_max ?? 0) <= 0.5;
  const zeigen = s.treffer.slice(0, 60);
  const waehlbar = s.treffer.filter((t) => t.uebernehmbar).length;
  return html`
    ${kopf}
    <p class="klein">${s.treffer.length} Bohrungen im Umkreis von ${zahl(s.radius, 0)} m · ${s.zeit}</p>
    ${gp.anzahl ? html`<p class=${`klein ${gpOk ? "ok" : "warnung"}`}>${gpOk ? "✓" : "⚠"} ${gp.anzahl} Bohrungen des Gutachtens auch
      beim Land: Lage ≤ ${zahl(gp.lage_max)} m${gp.gok_max !== null ? html`, GOK ≤ ${zahl(gp.gok_max)} m` : nothing}${gpOk ? "" : " – Lage und GOK prüfen"}</p>` : nothing}
    ${s.fehler.map((f) => html`<p class="warnung klein">${f.dienst}: ${f.fehler}</p>`)}
    ${zeigen.length ? html`
      <table class="tabelle kompakt sgd">
        <thead><tr><th></th><th>Bohrung</th><th class="zahl">Abstand</th><th class="zahl">GOK</th><th class="zahl">Teufe</th><th>Schichten</th></tr></thead>
        <tbody>
          ${zeigen.map((t) => {
            const k = `${t.dienst}/${t.id}`;
            return html`<tr class=${t.gutachten ? "doppelt" : ""}>
              <td>${t.uebernehmbar ? html`<input type="checkbox" aria-label=${`${t.name} übernehmen`} .checked=${sgdWahl.has(k)}
                @change=${(ev: Event) => { if ((ev.target as HTMLInputElement).checked) sgdWahl.add(k); else sgdWahl.delete(k); neu(); }}>` : nothing}</td>
              <td title=${`${t.dienst} · ID ${t.id}${t.datum ? ` · ${t.datum}` : ""}`}>${t.name}</td>
              <td class="zahl">${zahl(t.abstand, 0)}</td>
              <td class="zahl">${zahl(t.gok)}</td>
              <td class="zahl">${zahl(t.teufe, 1)}</td>
              <td class="klein">${sgdSchichten(t)}</td>
            </tr>`;
          })}
        </tbody>
      </table>
      ${s.treffer.length > zeigen.length ? html`<p class="leise klein">… und ${s.treffer.length - zeigen.length} weitere (Umkreis verkleinern)</p>` : nothing}` : nothing}
    ${waehlbar ? html`<button class="primaer" ?disabled=${!sgdWahl.size} @click=${sgdUebernehmen}>
      Ausgewählte übernehmen (${sgdWahl.size})</button>
      <p class="leise klein">Nur Bohrungen mit Schichtdaten in BoreholeML (NRW, Baden-Württemberg); sie kommen mit Quelle und Lizenz ins Projekt.</p>` : nothing}
    ${nichtUebernehmbar(s)}
    ${s.quellen.map((q) => html`<p class="leise klein">Quelle: ${q.namensnennung} · <a href=${q.beleg} target="_blank" rel="noopener">Dienst</a></p>`)}
    <button class="link klein" @click=${async () => { const z2 = await versuchen(() => api.sgdVerwerfen(S.sig)); if (z2) { zustandUebernehmen(z2); neu(); } }}>Abfrage verwerfen</button>`;
}

/** Hilfsmarken (Strecke, Bezugspunkt) nur beim Kalibrieren; gesperrt zeigt der Plan nur die Bohrungen. */
function hilfsmarkenNachziehen(z: Zustand) {
  const v = S.viewer;
  if (!v) return;
  if (!z.unterlage || z.unterlage.kalibrierung?.gesperrt || !e) v.editor.hilfsmarken({});
  else v.editor.hilfsmarken({ strecke: e.massArt === "strecke" ? [e.p1, e.p2] : [], hoehe: e.hoeheArt === "strecke" ? [e.h1, e.h2] : [],
                              bezug: e.bezug });
}

let escGebunden = false;

/** Projekt an einem Punkt (ohne Gutachten): georeferenziert über den Punkt - kein Lageplan, keine Kalibrierung. */
function standortTeil(z: Zustand) {
  const s = z.standort!;
  return abschnitt(html`Standort ${hilfe("standort")}`, html`
    <p class="klein"><b>${zahl(s.x, 1)} / ${zahl(s.y, 1)}</b> · EPSG:${s.epsg}</p>
    <p class="leise klein">Georeferenziert über den Punkt: kein Lageplan, keine Kalibrierung – die Bohrungen der Länder
      kommen mit ihren Koordinaten. Ein Gutachten dazu (Schritt Gutachten) wird ein neues Projekt mit Lageplan.</p>
    <ul class="dienste klein" aria-label="Dienste am Standort">${s.dienste.map((d) => html`<li class=${d.art}>${d.text}</li>`)}</ul>`);
}

export function schrittLage() {
  const z = S.z!;
  entwurf(z);
  hilfsmarkenNachziehen(z);
  const planGesperrt = z.lage_modus !== "reihe" && z.unterlage?.art === "plan" && !!z.unterlage.kalibrierung?.gesperrt;
  if (S.punktModus && !planGesperrt) S.punktModus = false;
  S.viewer?.editor.punktModusSetzen(S.punktModus);
  if (!escGebunden) {
    escGebunden = true;
    window.addEventListener("keydown", (ev) => {
      if (ev.key === "Escape" && S.schritt === "lage" && S.punktModus) punktModus(false);
    });
  }
  return html`
    <div class="app-panel links">
      ${z.standort ? standortTeil(z) : html`
        ${abschnitt(html`Lage der Bohrungen ${hilfe("lage_art")}`, html`
          <div class="umschalter">
            <label><input type="radio" name="lagemodus" .checked=${z.lage_modus === "koordinaten"}
              @change=${() => aendern([{ op: "lage_modus", wert: "koordinaten" }])}> Koordinaten (Lageplan)</label>
            <label><input type="radio" name="lagemodus" .checked=${z.lage_modus === "reihe"}
              @change=${() => aendern([{ op: "lage_modus", wert: "reihe" }])}> Reihe (Längsschnitt)</label>
          </div>`)}
        ${abschnitt(html`Unterlage ${hilfe("unterlage")}`, unterlageTeil(z))}
        ${z.unterlage ? abschnitt(html`Kalibrieren`, kalibrierenTeil(z)) : nothing}
        ${abschnitt(html`Bohrungen setzen`, bohrungenTeil(z))}`}
      ${z.standort ? abschnitt(html`Bohrungen der Länder${z.sgd?.gegenprobe.anzahl ? " ✓" : ""} ${hilfe("sgd")}`, sgdTeil(z)) : nothing}
      ${abschnitt(html`Gelände (DGM)${z.gelaende?.pruefung?.warnungen.length ? " ⚠" : z.gelaende ? " ✓" : ""} ${hilfe("gelaende")}`,
        gelaendeTeil(z), !!z.gelaende)}
      ${z.standort ? nothing : abschnitt(html`Bohrungen der Länder${z.sgd?.gegenprobe.anzahl ? " ✓" : ""} ${hilfe("sgd")}`, sgdTeil(z), !!z.sgd)}
      ${abschnitt(html`Gebäude (LoD2)${z.gebaeude ? " ✓" : ""} ${hilfe("gebaeude")}`, gebaeudeTeil(z), !!z.gebaeude)}
      ${abschnitt(html`Darstellung`, html`
        <label class="inline">Ø Bohrsäulen ${hilfe("durchmesser")}
          <input type="number" step="0.1" min="0" class="kurz" placeholder=${`auto ${zahl(z.durchmesser_auto, 1)}`}
            .value=${live(z.durchmesser === null ? "" : String(z.durchmesser))}
            @change=${(ev: Event) => aendern([{ op: "durchmesser", wert: eingabe(ev) }])}> m</label>
        <p class="leise klein">Je Bohrung im Schritt Bohrungen (Ø Säule). Leer = automatisch nach Modellgröße.</p>`, false)}
      ${z.hinweise.length ? html`<div class="hinweisliste">${z.hinweise.map((h) => html`<p class="klein">ℹ ${h}</p>`)}</div>` : nothing}
    </div>`;
}
