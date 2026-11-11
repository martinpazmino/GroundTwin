// End-to-End-Pruefung der Schritt-App (Chromium/Playwright, ohne Bildschirm) gegen den laufenden Server.
//   A  Talheim: Warnung = unklassifizierte Schicht, blaettern (Pfeil, N), G = alle Schichten geprueft und weiter,
//      Schicht klassifizieren, Bohrung entfernen und wiederherstellen, alle Bohrungen geprueft
//   B  Berlin: Vorschlag nach Norm fuer eine unklassifizierte Schicht uebernehmen; B2 Gelaende (DGM-Datei): Vergleich
//      GOK - DGM, fehlende GOK uebernehmen, systematische Abweichung, DGM entfernen; B3 Bohrungen der Laender: echte
//      Abfrage beim Dienst Berlin (Netz), Gegenprobe mit den fuenf Bohrungen des Gutachtens; B4 DGM vom Land (echter
//      WCS, Netz): GOK-Vergleich, Modell mit Gelaende aus dem DGM, Gelaende im Viewer ein/aus; B5 Gebaeude (LoD2) vom
//      Land (echte Kacheln Berlin, Netz): im IFC und im Viewer (alles im Bild, Kamera ausserhalb), ein/aus; 3D Tiles
//      fuer Cesium (Quasigeoid vom PROJ-CDN, Netz) als ZIP
//   C  Lageplan (scripts/testplan.py): Strecke messen -> Massstab, Bezugspunkt, Drehung, sperren, Bohrungen ohne Lage
//      aus der Liste auf ihren Kreis ziehen; C2 dasselbe ohne eine einzige Koordinate und mit echten Hoehen (Vorschau im
//      Bild, EPSG-Liste, offene Punktwahl, Nullpunkt, kein Flackern); C3 Punkte setzen, zuordnen, loeschen, Direktaufruf
//   D  Laengsschnitt: 1:500/1:100, Bezugspunkt (Station/Hoehe), sperren, Bohrungen auf ihre Saeule ziehen (GOK aus dem
//      PDF bleibt), Einheit umbenennen, Modell im Viewer, einchecken, IFC mit Bodenansprache; BoreholeML ohne
//      Koordinaten gesperrt
//   E  PDF-Beispiel: Extraktion mit Fortschritt, Quelle der Schicht im PDF
//   F  Standort ohne Gutachten (echter Dienst NRW, Netz): Projekt am Punkt, Bohrungen der Laender uebernehmen (ganz
//      im Lageplan, Nullpunkt bleibt am Standort), Modell als Vorerkundung in Kopf, Modell-Schritt, Bericht und
//      Viewer, Modell ganz im Bild mit der Kamera ausserhalb; Start mit zwei Wegen, Erweitertes eingeklappt
//   G  Werkzeug „Dienste der Länder“: alle 16 Laender je Thema, Eintrag bearbeiten und verwerfen (nie speichern)
//
//   python -m server --port 8511 --kein-browser --arbeit <leerer-ordner>     (in einem zweiten Terminal)
//   python scripts/testplan.py <plaene>
//   node scripts/check_app.mjs http://localhost:8511 <plaene> <ausgabe>
// Server mit Anmeldung (Container, docs/22): GEO_AGENT_PASSWORT (und GEO_AGENT_BENUTZER) wie beim Server setzen.
import { createRequire } from "node:module";
import { mkdirSync, readFileSync } from "node:fs";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PFAD ?? "playwright");
const [url, plaene, aus = "check_app"] = process.argv.slice(2);
mkdirSync(aus, { recursive: true });
const wPlan = JSON.parse(readFileSync(`${plaene}/wahrheit_plan.json`, "utf8")).bohrungen;
const wSchnitt = JSON.parse(readFileSync(`${plaene}/wahrheit_schnitt.json`, "utf8")).bohrungen;

const browser = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const anmeldung = process.env.GEO_AGENT_PASSWORT
  ? { httpCredentials: { username: process.env.GEO_AGENT_BENUTZER || "pruefung", password: process.env.GEO_AGENT_PASSWORT } }
  : {};
const page = await browser.newPage({ viewport: { width: 1600, height: 950 }, ...anmeldung });
const fehler = [];
const pruefungen = [];
page.on("pageerror", (e) => fehler.push(String(e.stack || e)));
page.on("console", (m) => m.type() === "error" && !/favicon/.test(m.text()) && fehler.push(m.text()));
page.on("dialog", (d) => d.accept());

/** Pruefung ausgelassen, weil ein Dienst des Landes nicht erreichbar war: die erwartete 502 des Servers ist kein Seitenfehler. */
function ausgelassen(text) {
  console.log(`AUS  ${text}`);
  const i = fehler.findLastIndex((f) => /status of 502/.test(f));
  if (i >= 0) fehler.splice(i, 1);
}

function pruefe(name, ok, info = "") {
  pruefungen.push({ name, ok: !!ok });
  console.log(`${ok ? "OK  " : "FEHL"} ${name}${info ? ` – ${info}` : ""}`);
}
const stand = () => page.evaluate(() => {
  const a = window.app;
  return { schritt: a.schritt, bid: a.bid, z: a.z, rechnet: a.rechnet,
           modell: a.modell && { fehler: a.modell.fehler, ifc: a.modell.ifc, einheiten: a.modell.bericht?.einheiten.map((e) => e.name) } };
});
const ruhe = (ms = 800) => page.waitForTimeout(ms);
const bohrung = async (code) => (await stand()).z.bohrungen.find((b) => b.code === code);
const warte = (f, arg, timeout = 120000) => page.waitForFunction(f, arg, { timeout, polling: 250 });
/** Das Modell des aktuellen Stands ist im Viewer (geladen, nicht mehr gerechnet). Nicht „noch einmal geladen“: kommt
 *  es aus dem Zwischenspeicher (zweiter Lauf), hat es der Viewer schon im Schritt Lage geladen. */
const modellDa = () => {
  const a = window.app, b = window.baugrund, ifc = a?.modell?.ifc;
  const laedt = document.getElementById("laden")?.hidden === false;     // Ladeanzeige des Viewers
  const aktuell = a?.modell?.zustand?.modell?.schluessel === a?.z?.modell?.schluessel;   // Modell zum jetzigen Stand
  return !!ifc && aktuell && !a.rechnet && !laedt && !!b?.geladen && b.geladeneIfc?.at(-1) === ifc.split("/").pop();
};
/** Huelle ganz im Bild (alle Ecken in NDC)? "modell": das Modell, die Kamera ausserhalb; "lage": die Bohrungen im
 *  Lage-Editor. Mit nurOk nur wahr/falsch (fuer warte). */
const huelleImBild = ([welche, nurOk]) => {
  const v = window.viewer;
  const m = v.modell();
  const box = welche === "modell" ? (m && m.object.visible ? m.box : null) : v.editor.kiste();
  if (!box || box.isEmpty()) return nurOk ? false : { ok: false, rand: null };
  const kam = v.world.camera.three;
  kam.updateMatrixWorld();
  let rand = 0;
  for (const x of [box.min.x, box.max.x]) for (const y of [box.min.y, box.max.y]) for (const z of [box.min.z, box.max.z]) {
    const ecke = box.min.clone().set(x, y, z).project(kam);
    rand = Math.max(rand, Math.abs(ecke.x), Math.abs(ecke.y));
  }
  const innen = box.containsPoint(kam.position);
  const ok = rand <= 1.02 && (welche !== "modell" || !innen);
  return nurOk ? ok : { ok, rand: Math.round(rand * 100) / 100, innen };
};
const schirm = (px) => page.evaluate(([u, v]) => window.viewer.editor.bildZuSchirm(u, v), px);
const markenPunkt = (code) => page.evaluate((c) => {
  const e = window.viewer.editor;
  const s = [...e.nadeln.values()].find((n) => n.daten.code === c);
  return s ? e.markenPunkt(s.daten.id) : null;
}, code);

async function startseite() {
  await page.goto(url);
  await page.waitForSelector(".ablage", { timeout: 60000 });
}

/** Eingeklappten Teil oeffnen (details mit dieser Ueberschrift und alle darueber): „Erweitert“, „Beispiele“ … */
async function aufklappen(text) {
  const n = await page.evaluate((t) => {
    let k = 0;
    for (const s of document.querySelectorAll("details > summary")) {
      if (!(s.textContent ?? "").includes(t)) continue;
      k += 1;
      for (let d = s.parentElement; d; d = d.parentElement?.closest("details") ?? null) d.open = true;
    }
    return k;
  }, text);
  if (!n) throw new Error(`nichts zum Aufklappen: ${text}`);
  await ruhe(200);
}

/** Gespeicherten Stand verwerfen (Menue): jede Pruefung beginnt ohne Korrekturen, auch beim zweiten Lauf. */
async function zuruecksetzen() {
  await page.locator(".menue summary").click();
  await page.getByRole("button", { name: /Alle Korrekturen verwerfen/ }).click();
  await warte(() => window.app?.z?.version === 0 && window.app.schritt === "bohrungen" && document.querySelector(".schichten"));
  await ruhe();
}

async function beispiel(titel) {
  await startseite();
  await aufklappen("Beispiele ausprobieren");
  await page.getByRole("button", { name: titel }).click();
  await warte(() => window.app?.schritt && window.app.schritt !== "gutachten" && window.app.z);
  await zuruecksetzen();
}

async function hochladen(datei) {
  await startseite();
  await page.locator('.ablage input[type="file"]').setInputFiles(datei);
  await page.getByRole("button", { name: /Auswerten/ }).click();
  await warte(() => window.app?.schritt && window.app.schritt !== "gutachten" && window.app.z);
  await zuruecksetzen();
}

async function ziehen(von, nach) {
  await page.mouse.move(von.x, von.y);
  await page.mouse.down();
  await page.mouse.move((von.x + nach.x) / 2, (von.y + nach.y) / 2, { steps: 6 });
  await page.mouse.move(nach.x, nach.y, { steps: 6 });
  await page.mouse.up();
}

async function punktKlick(knopf, px) {
  await page.getByRole("button", { name: knopf }).click();
  await ruhe(300);
  const p = await schirm(px);
  await page.mouse.click(p.x, p.y);
  await ruhe(400);
}

async function zuLage() {
  await page.getByRole("button", { name: /Weiter: Lage/ }).click();
  await warte(() => window.baugrund?.lage?.nadeln > 0 && window.viewer?.editor?.aktiv);
  await ruhe(1500);
}

async function unterlageHochladen(datei, art) {
  if (art === "schnitt") await page.getByLabel("Längsschnitt", { exact: true }).check();
  await page.locator('.datei-knopf input[accept*="pdf"]').setInputFiles(datei);
  await warte(() => window.baugrund?.lage?.unterlage?.sichtbar);
  await ruhe(2000);
}

try {
  // ---------------------------------------------------------------- A: Talheim
  await beispiel(/Talheim/);
  let z = (await stand()).z;
  pruefe("Warnung = unklassifizierte Schichten", z.pruefstand.unklassifiziert_offen === 2 &&
    (await page.locator(".pruefleiste .plakette.warn").textContent()).includes("2"), JSON.stringify(z.pruefstand));
  const erste = (await stand()).bid;
  await page.keyboard.press("ArrowDown");
  await ruhe(500);
  const zweite = (await stand()).bid;
  pruefe("Pfeil ↓ blättert zur nächsten Bohrung", zweite && zweite !== erste);
  await page.getByRole("button", { name: /Nächste offene/ }).click();
  await ruhe(500);
  const s1 = await stand();
  pruefe("„Nächste offene“ wählt eine Bohrung mit offenen Schichten",
    s1.z.bohrungen.find((b) => b.id === s1.bid)?.schichten_geprueft < s1.z.bohrungen.find((b) => b.id === s1.bid)?.schichten_n);
  const vorG = s1.bid;
  await page.locator("body").click({ position: { x: 5, y: 300 } });
  await page.keyboard.press("g");
  await warte((id) => window.app.bid !== id, vorG, 30000).catch(() => {});
  await ruhe(600);
  const nachG = await stand();
  const b = nachG.z.bohrungen.find((x) => x.id === vorG);
  pruefe("G: alle Schichten geprüft und weiter", b.schichten_geprueft === b.schichten_n && nachG.bid !== vorG,
    `${b.code} ${b.schichten_geprueft}/${b.schichten_n} → ${nachG.z.bohrungen.find((x) => x.id === nachG.bid)?.code}`);
  // unklassifizierte Schicht von BK1 klassifizieren
  await page.locator(".bliste li", { hasText: "BK1" }).first().click();
  await warte(() => document.querySelector(".schichten tr.warn"));
  await page.locator(".schichten tr.warn select").first().selectOption("Schluff");
  await warte(() => window.app.z.pruefstand.unklassifiziert_offen === 1, null, 30000).catch(() => {});
  z = (await stand()).z;
  pruefe("Bodenart gewählt: Warnung weg, Schicht korrigiert", z.pruefstand.unklassifiziert_offen === 1 && z.pruefstand.korrigiert === 1,
    JSON.stringify(z.pruefstand));
  await page.screenshot({ path: `${aus}/A1_bohrungen.png` });
  // entfernen und wiederherstellen
  await page.locator(".bliste li", { hasText: "GWM1" }).first().hover();
  await page.getByRole("button", { name: "GWM1 entfernen" }).click();
  await warte(() => window.app.z.bohrungen.find((b) => b.code === "GWM1")?.entfernt, null, 30000);
  await page.locator("details.entfernt summary").click();
  await page.locator("details.entfernt li", { hasText: "GWM1" }).getByRole("button", { name: "wiederherstellen" }).click();
  await warte(() => !window.app.z.bohrungen.find((b) => b.code === "GWM1")?.entfernt, null, 30000);
  pruefe("Bohrung entfernen und wiederherstellen", !(await bohrung("GWM1")).entfernt);
  await page.getByRole("button", { name: /Alle Bohrungen geprüft/ }).click();
  await warte(() => window.app.z.pruefstand.bohrungen[0] === window.app.z.pruefstand.bohrungen[1], null, 30000);
  z = (await stand()).z;
  pruefe("Alle Bohrungen geprüft (global)", z.pruefstand.schichten[0] === z.pruefstand.schichten[1] && z.pruefstand.unklassifiziert_offen === 0,
    `${z.pruefstand.bohrungen} · ${z.pruefstand.schichten}`);

  // ---------------------------------------------------------------- B: Berlin, Vorschlag nach Norm
  await beispiel(/^Berlin V-67b/);
  await page.locator(".bliste li", { hasText: "S2a" }).first().click();
  await warte(() => [...document.querySelectorAll(".vorschlag")].length > 0, null, 30000);
  await page.locator(".vorschlag").first().click();
  await warte(() => window.app.z.bohrungen.find((b) => b.code === "S2a")?.korrigiert > 0, null, 30000);
  const s2a = await bohrung("S2a");
  pruefe("Vorschlag nach Norm übernommen (Grobaand → Sand)", s2a.korrigiert === 1, `${s2a.unklassifiziert} weiter unklassifiziert`);
  await page.screenshot({ path: `${aus}/B1_vorschlag.png` });

  // ---------------------------------------------------------------- B2: Gelaende (DGM-Datei des Nutzers)
  await hochladen(`${plaene}/berlin_ohne_gok_extraktion.json`);
  await zuLage();
  // Gelaende liegt unter „Erweitert“ (eingeklappt, bis Gelaende oder Gebaeude geladen sind)
  pruefe("Lage: Gelände, Gebäude und Darstellung eingeklappt unter „Erweitert“, Vergleich mit den Ländern offen",
    await page.evaluate(() => {
      const e = document.querySelector(".app-panel details.erweitert");
      const vergleich = [...document.querySelectorAll(".app-panel details.abschnitt")]
        .find((d) => d.querySelector("summary")?.textContent?.includes("Bohrungen der Länder"));
      return !!e && !e.open && !!e.querySelector("summary")?.textContent?.includes("Erweitert") && !!vergleich?.open &&
        !vergleich.closest("details.erweitert");
    }));
  await aufklappen("Gelände (DGM)");
  await page.getByLabel("DGM-Dateien").setInputFiles(`${plaene}/dgm_berlin.xyz`);
  await warte(() => window.app.z.gelaende?.pruefung, null, 60000);
  let gz = (await stand()).z.gelaende;
  const status = Object.fromEntries(gz.pruefung.zeilen.map((r) => [r.code, r.status]));
  pruefe("DGM geladen: GOK der Bohrungen mit Lage passt (≤ 0,5 m), fehlende GOK erkannt",
    gz.info.epsg === 25833 && status["422C-5527"] === "ohne_gok" && status.S2a === "ohne_lage" &&
    ["422C-460", "422C-461", "422C-5525", "422C-5526"].every((c) => status[c] === "ok") && !gz.pruefung.warnungen.length,
    JSON.stringify(status));
  await page.locator("table.gelaende tr", { hasText: "422C-5527" }).getByRole("button", { name: "übernehmen" }).click();
  await warte(() => window.app.z.bohrungen.find((b) => b.code === "422C-5527")?.gok_quelle === "DGM", null, 30000);
  const g5527 = await bohrung("422C-5527");
  pruefe("Fehlende GOK auf Klick aus dem DGM übernommen (Quelle DGM)", g5527.gok_quelle === "DGM" && g5527.gok > 30,
    `${g5527.gok} m NHN`);
  await page.screenshot({ path: `${aus}/B2_gelaende.png` });
  await page.getByLabel("DGM-Dateien").setInputFiles(`${plaene}/dgm_berlin_hoch.xyz`);
  await warte(() => window.app.z.gelaende?.pruefung?.warnungen.length > 0, null, 60000);
  const warnText = await page.locator("table.gelaende ~ p.warnung").first().textContent();
  pruefe("DGM 3 m höher: systematische Abweichung gewarnt", /im Mittel 3,\d\d m unter dem DGM/.test(warnText), warnText);
  await page.getByRole("button", { name: "DGM entfernen" }).click();
  await warte(() => window.app.z.gelaende === null, null, 30000);
  pruefe("DGM entfernt, übernommene GOK bleibt", (await bohrung("422C-5527")).gok_quelle === "DGM");

  // ---------------------------------------------------------------- B3: Bohrungen der Laender (echter Dienst Berlin)
  await aufklappen("Bohrungen der Länder");
  await page.getByRole("button", { name: "Abfragen" }).click();
  await warte(() => window.app.z.sgd, null, 90000);
  const sgd = (await stand()).z.sgd;
  const zeilenSgd = await page.locator("table.sgd tbody tr").count();
  // nur ein Netzproblem des Dienstes laesst die Pruefung aus (wie die Live-Tests in tests/test_bohrdaten.py);
  // jeder andere Fehler (HTTP 4xx, ExceptionReport, Lesefehler) faellt durch
  const netzBerlin = sgd.fehler.find((f) => f.dienst === "BE" && /^(keine Antwort|nicht erreichbar|HTTP 5\d\d)/.test(f.fehler));
  if (netzBerlin) console.log(`AUS  Bohrungen der Länder: Dienst Berlin nicht erreichbar (${netzBerlin.fehler}) – Prüfung ausgelassen`);
  else {
    pruefe("Bohrungen der Länder: Gegenprobe – die fünf Bohrungen des Gutachtens auch beim Land (≤ 0,1 m)",
      sgd.gegenprobe.anzahl === 5 && sgd.gegenprobe.lage_max <= 0.1 && zeilenSgd > 5 && sgd.quellen.some((q) => q.lizenz === "dl-de/zero-2.0"),
      `${sgd.treffer.length} Treffer · ${JSON.stringify(sgd.gegenprobe)} · Fehler ${JSON.stringify(sgd.fehler)}`);
    // Berlin gibt nur Kopfdaten und das Profil als Bild heraus: die Liste sagt, warum keine davon ins Modell kann
    const warum = (await page.locator("p.sgd-warum").count()) ? await page.locator("p.sgd-warum").innerText() : "";
    pruefe("Bohrungen der Länder: nicht übernehmbare mit Grund (Berlin: nur Kopfdaten, Profil als Bild)",
      /\(Berlin\) nur mit Kopfdaten/.test(warum) && !(await page.locator("table.sgd tbody input[type=checkbox]").count()),
      warum.replace(/\s+/g, " ").slice(0, 120));
  }
  await page.screenshot({ path: `${aus}/B3_laender.png` });

  // ---------------------------------------------------------------- B4: DGM vom Land (echter WCS Brandenburg mit Berlin)
  await aufklappen("Gelände (DGM)");                                    // nach "DGM entfernen" zu
  await page.getByRole("button", { name: "DGM vom Land abrufen" }).click();
  await warte(() => window.app.z.gelaende?.info?.quelle || window.app.meldungen.some((m) => m.art === "fehler"), null, 150000);
  gz = (await stand()).z.gelaende;
  const fehlerLand = (await page.evaluate(() => window.app.meldungen.filter((m) => m.art === "fehler").map((m) => m.text))).join("; ");
  if (!gz?.info?.quelle && /Dienst des Landes: .*(keine Antwort|nicht erreichbar|HTTP 5\d\d)/.test(fehlerLand)) {
    ausgelassen(`DGM vom Land: Dienst nicht erreichbar (${fehlerLand}) – Prüfungen ausgelassen`);
  } else {
    const st = Object.fromEntries((gz?.pruefung?.zeilen ?? []).map((r) => [r.code, r.status]));
    pruefe("DGM vom Land (WCS Brandenburg mit Berlin, 1 m): GOK-Vergleich markiert 422C-5526 (1 m unter dem DGM)",
      gz?.info?.quelle?.dienst === "BB-DGM1" && gz.info.dx === 1 && st["422C-5526"] === "abweichung" &&
      ["422C-460", "422C-461", "422C-5525"].every((c) => st[c] === "ok"), `${JSON.stringify(st)} ${fehlerLand}`);
    await page.screenshot({ path: `${aus}/B4_dgm_land.png` });
    await page.getByRole("button", { name: /Weiter: Einheiten/ }).click();
    await warte(() => document.querySelector("table.einheiten"), null, 180000);
    await page.getByRole("button", { name: /Weiter: Modell/ }).click();
    await warte(() => window.app.schritt === "modell" && window.app.modell?.ifc, null, 240000);
    await warte(modellDa, null, 240000);
    await ruhe(2000);
    const v = await page.evaluate(() => ({ gelaende: window.baugrund.gelaende,
                                           quelle: window.app.modell?.bericht?.parameter?.gelaende?.quelle }));
    pruefe("Modell mit Gelände aus dem DGM, Gelände um das Modell im Viewer", v.gelaende === 1 && v.quelle === "DGM", JSON.stringify(v));
    await page.screenshot({ path: `${aus}/B4_gelaende_modell.png` });
    await page.locator('bim-button[label="Gelände"]').click();
    await warte(() => window.baugrund.gelaendeSichtbar === false, null, 10000).catch(() => {});
    pruefe("Gelände im Viewer ausblendbar", await page.evaluate(() => window.baugrund.gelaendeSichtbar === false));
  }

  // ---------------------------------------------------------------- B5: Gebaeude (LoD2) vom Land (echte Kacheln Berlin)
  if ((await page.evaluate(() => window.app.schritt)) !== "lage") {
    await page.locator("nav.schritte button", { hasText: "Lage" }).click();
    await warte(() => window.app.schritt === "lage", null, 60000);
  }
  await aufklappen("Gebäude (LoD2)");
  const letzteMeldung = await page.evaluate(() => Math.max(0, ...window.app.meldungen.map((m) => m.id)));
  await page.getByRole("button", { name: "Gebäude vom Land abrufen" }).click();
  await warte((n) => window.app.z.gebaeude || window.app.meldungen.some((m) => m.id > n && m.art === "fehler"), letzteMeldung, 240000);
  const zg = (await stand()).z.gebaeude;
  const fehlerGeb = (await page.evaluate((n) => window.app.meldungen.filter((m) => m.id > n && m.art === "fehler").map((m) => m.text),
    letzteMeldung)).join("; ");
  if (!zg && /Dienst des Landes: .*(keine Antwort|nicht erreichbar|HTTP 5\d\d)/.test(fehlerGeb)) {
    ausgelassen(`Gebäude vom Land: Dienst nicht erreichbar (${fehlerGeb}) – Prüfungen ausgelassen`);
  } else {
    pruefe("Gebäude (LoD2) vom Land: Kacheln Berlin, Lizenz dl-de/zero-2.0",
      zg?.anzahl > 10 && zg.quelle.dienste[0]?.dienst === "BE-LOD2" && zg.quelle.dienste[0]?.lizenz === "dl-de/zero-2.0",
      `${zg?.anzahl} Gebäude · ${zg?.quelle?.kacheln} Kacheln ${fehlerGeb}`);
    await page.locator("nav.schritte button", { hasText: "Modell" }).click();
    await warte(() => window.app.schritt === "modell" && window.app.modell?.ifc, null, 240000);
    await warte(modellDa, null, 240000);
    await ruhe(2000);
    const vg = await page.evaluate(() => ({ gebaeude: window.baugrund.gebaeude, gelaende: window.baugrund.gelaende }));
    pruefe("Gebäude im Modell und im Viewer (IfcBuildingElementProxy)", vg.gebaeude === zg.anzahl, JSON.stringify(vg));
    // die Gebaeude kamen im Lage-Schritt dazu: die dort gemerkte Ansicht stand mitten in einem (fuenffach hoch)
    await warte(huelleImBild, ["modell", true], 20000).catch(() => null);
    const bg = await page.evaluate(huelleImBild, ["modell", false]);
    pruefe("Gebäude: Modell mit Umgebung ganz im Bild, Kamera außerhalb", bg.ok, JSON.stringify(bg));
    await page.screenshot({ path: `${aus}/B5_gebaeude.png` });
    await page.locator('bim-button[label="Gebäude"]').click();
    await warte(() => window.baugrund.gebaeudeSichtbar === false, null, 10000).catch(() => {});
    pruefe("Gebäude im Viewer ausblendbar", await page.evaluate(() => window.baugrund.gebaeudeSichtbar === false));

    // 3D Tiles fuer Cesium (P6, D87): ZIP mit Tileset und je einem GLB fuer Modell, Gelaende und Gebaeude; das
    // Quasigeoid GCG2016 kommt beim ersten Mal vom PROJ-CDN (Netz) - nicht erreichbar: ausgelassen
    const letzte3d = await page.evaluate(() => Math.max(0, ...window.app.meldungen.map((m) => m.id)));
    const download = page.waitForEvent("download", { timeout: 240000 }).catch(() => null);
    await aufklappen("Erweitert");                                     // weitere Exporte im Schritt Modell
    await page.getByRole("button", { name: /Baugrundmodell für Cesium/ }).click();
    // die Wartenden enden mit dem Rennen (window.__ende3d): sonst fragte eine Seite nach dem naechsten Laden noch nach
    // window.app, solange es das Element #app ist (Seitenfehler)
    const meldung = warte((n) => window.__ende3d || window.app?.meldungen?.find((m) => m.id > n && m.art === "fehler"),
      letzte3d, 240000).then(async (h) => ({ fehler: (await h.jsonValue())?.text })).catch(() => null);   // nie unbehandelt
    const ausgang = (await Promise.race([download.then((d) => (d ? { d } : null)), meldung])) ?? { fehler: "kein Download" };
    await page.evaluate(() => { window.__ende3d = true; });
    if (ausgang.fehler && /Quasigeoid GCG2016 nicht geladen/.test(ausgang.fehler)) {
      ausgelassen(`3D Tiles: PROJ-CDN nicht erreichbar (${ausgang.fehler}) – Prüfung ausgelassen`);
    } else {
      const roh = ausgang.d ? readFileSync(await ausgang.d.path()).toString("latin1") : "";
      const dateien = ["tileset.json", "baugrundmodell.glb", "gelaende.glb", "gebaeude.glb", "LIESMICH.txt"];
      pruefe("3D Tiles für Cesium: ZIP mit Tileset, Modell, Gelände und Gebäude", !!ausgang.d && roh.startsWith("PK") &&
        dateien.every((d) => roh.includes(d)) && /_3dtiles\.zip$/.test(ausgang.d.suggestedFilename()),
        ausgang.fehler ?? `${ausgang.d.suggestedFilename()} · ${Math.round(roh.length / 1024)} KB`);
    }
  }

  // ---------------------------------------------------------------- C: Lageplan kalibrieren und Bohrungen setzen
  await hochladen(`${plaene}/plan_extraktion.json`);
  await zuLage();
  await unterlageHochladen(`${plaene}/plan.pdf`, "plan");
  await punktKlick("Punkt 1", wPlan["B 1"].px);
  await punktKlick("Punkt 2", wPlan["B 4"].px);
  const meter = Math.hypot(wPlan["B 4"].x - wPlan["B 1"].x, wPlan["B 4"].y - wPlan["B 1"].y);
  await page.locator("label.inline", { hasText: "wahre Länge" }).locator("input").fill(meter.toFixed(3));
  await punktKlick("Punkt im Plan wählen", wPlan["B 1"].px);
  await page.locator("label", { hasText: "Rechtswert" }).locator("input").fill(String(wPlan["B 1"].x));
  await page.locator("label", { hasText: "Hochwert" }).locator("input").fill(String(wPlan["B 1"].y));
  await page.locator("fieldset", { hasText: "Drehung" }).locator('input[type="number"]').first().fill("10");
  await ruhe(500);
  await page.getByRole("button", { name: /Übernehmen und sperren/ }).click();
  await warte(() => window.baugrund?.lage?.unterlage?.gesperrt, null, 30000);
  await ruhe(1500);
  const lageText = (await page.evaluate(() => window.baugrund.lage)).text;
  pruefe("Plan kalibriert (Strecke, Bezugspunkt, Drehung) und gesperrt", /1:500 · Drehung 10,0°/.test(lageText), lageText);
  for (const code of ["B 6", "BS 9"]) {
    const park = page.locator(".park", { hasText: new RegExp(`^${code}$`) });
    const kiste = await park.boundingBox();
    const ziel = await schirm(wPlan[code].px);
    await ziehen({ x: kiste.x + kiste.width / 2, y: kiste.y + kiste.height / 2 }, ziel);
    await warte((c) => window.app.z.bohrungen.find((b) => b.code === c)?.x !== null, code, 30000);
    await ruhe(800);
  }
  const fehlerLage = [];
  for (const code of ["B 6", "BS 9"]) {
    const x = await bohrung(code);
    fehlerLage.push(Math.hypot(x.x - wPlan[code].x, x.y - wPlan[code].y));
  }
  pruefe("Bohrungen ohne Lage auf den Plan gezogen (Fehler ≤ 0,5 m)", Math.max(...fehlerLage) <= 0.5,
    fehlerLage.map((f) => f.toFixed(2)).join(" / ") + " m");
  await page.screenshot({ path: `${aus}/C1_plan.png` });

  // ---------------------------------------------------------------- C2: Lageplan, keine Bohrung mit Koordinaten
  // Fall aus der Praxis (RKS ohne Lage): der Plan springt beim Kalibrieren Millionen Meter - die Vorschau bleibt im
  // Bild; EPSG aus der Liste mit Hinweis; eine offene Punktwahl blockiert das Ziehen nicht; Nullpunkt vom
  // Bezugspunkt; im Lage-Modus kein Wechsel zwischen Bild mit und ohne Postproduktion (Flackern).
  await hochladen(`${plaene}/plan_ohne_lage_extraktion.json`);
  await zuLage();
  await unterlageHochladen(`${plaene}/plan.pdf`, "plan");
  await punktKlick("Punkt 1", wPlan["B 1"].px);
  await punktKlick("Punkt 2", wPlan["B 4"].px);
  await page.locator("label.inline", { hasText: "wahre Länge" }).locator("input").fill(meter.toFixed(3));
  await punktKlick("Punkt im Plan wählen", wPlan["B 1"].px);
  const rechtswert = page.locator("label", { hasText: "Rechtswert" }).locator("input");
  const epsgHinweis = page.locator("fieldset", { hasText: "Bezugspunkt" }).locator("p.klein");
  await rechtswert.fill("74848.9");
  await page.locator("label", { hasText: "Hochwert" }).locator("input").fill(String(wPlan["B 1"].y));
  await page.locator("fieldset", { hasText: "Bezugspunkt" }).locator("select.epsg").selectOption("25832");
  await ruhe(300);
  const falsch = await epsgHinweis.textContent();
  await rechtswert.fill(String(wPlan["B 1"].x));
  await page.locator("fieldset", { hasText: "Drehung" }).locator('input[type="number"]').first().fill("10");
  await ruhe(800);
  const richtig = await epsgHinweis.textContent();
  pruefe("EPSG aus der Liste, Hinweis wenn Rechts-/Hochwert nicht passen", /keinem System/.test(falsch) && /passt zu EPSG 25832/.test(richtig),
    `${falsch.trim()} | ${richtig.trim()}`);
  const imBild = () => page.evaluate(() => {
    const r = window.viewer.world.renderer.three.domElement.getBoundingClientRect();
    const p = window.viewer.editor.bildZuSchirm(2000, 1500);                 // Planmitte
    return !!p && p.x > r.left && p.x < r.right && p.y > r.top && p.y < r.bottom;
  });
  pruefe("Vorschau: Plan bleibt nach dem Eintragen der Koordinate im Bild", await imBild());
  await page.locator("button.punkt", { hasText: /Punkt im Plan wählen/ }).click();     // Punktwahl offen lassen
  await page.getByRole("button", { name: /Übernehmen und sperren/ }).click();
  await warte(() => window.baugrund?.lage?.unterlage?.gesperrt, null, 30000);
  await ruhe(1500);
  const gesperrt = await page.evaluate(() => ({ waehlt: document.body.classList.contains("waehlt"),
                                                ursprung: [window.viewer.rahmen.e0, window.viewer.rahmen.n0] }));
  pruefe("Sperren: Punktwahl beendet, Nullpunkt vom Bezugspunkt",
    !gesperrt.waehlt && Math.hypot(gesperrt.ursprung[0] - wPlan["B 1"].x, gesperrt.ursprung[1] - wPlan["B 1"].y) < 100,
    JSON.stringify(gesperrt));
  await page.evaluate(() => {
    const r = window.viewer.world.renderer;
    window.__bilder = { einfach: 0, post: 0 };
    const upd = r.postproduction.update.bind(r.postproduction);
    r.postproduction.update = (...a) => { window.__bilder.post += 1; return upd(...a); };
    r.onAfterUpdate.add(() => { window.__bilder.einfach += 1; });
  });
  // Plan verschieben (Kamera) und Maus darueber bewegen: alle Bilder ohne Postproduktion
  const flaeche = await page.evaluate(() => { const r = window.viewer.world.renderer.three.domElement.getBoundingClientRect(); return { x: r.left + r.width * 0.75, y: r.top + r.height * 0.85 }; });
  await page.mouse.move(flaeche.x, flaeche.y);
  await page.mouse.down();
  for (let i = 1; i <= 10; i++) {
    await page.mouse.move(flaeche.x - i * 6, flaeche.y - i * 2);
    await ruhe(40);
  }
  await page.mouse.up();
  for (let i = 0; i < 10; i++) {
    await page.mouse.move(flaeche.x - 80 + i * 9, flaeche.y - 40);
    await ruhe(40);
  }
  await ruhe(800);
  const bilder = await page.evaluate(() => window.__bilder);
  pruefe("Lage-Modus: Bilder ohne Postproduktion (kein Flackern)", bilder.einfach > 0 && bilder.post === 0, JSON.stringify(bilder));
  const fehlerOhne = [];
  let sichtbar = true;
  for (const code of ["B 1", "B 7", "BS 10"]) {
    const park = page.locator(".park", { hasText: new RegExp(`^${code}$`) });
    const kiste = await park.boundingBox();
    const ziel = await schirm(wPlan[code].px);
    await ziehen({ x: kiste.x + kiste.width / 2, y: kiste.y + kiste.height / 2 }, ziel);
    await warte((c) => window.app.z.bohrungen.find((b) => b.code === c)?.x !== null, code, 30000);
    await ruhe(1500);
    const x = await bohrung(code);
    fehlerOhne.push(Math.hypot(x.x - wPlan[code].x, x.y - wPlan[code].y));
    sichtbar &&= (await imBild()) && !!(await markenPunkt(code));
  }
  pruefe("ohne Koordinaten: aus der Liste auf den Plan gezogen, Plan bleibt im Bild (Fehler ≤ 0,5 m)",
    sichtbar && Math.max(...fehlerOhne) <= 0.5, fehlerOhne.map((f) => f.toFixed(2)).join(" / ") + " m");
  await page.screenshot({ path: `${aus}/C2_ohne_lage.png` });

  // ---------------------------------------------------------------- C3: Punkte setzen, zuordnen, loeschen
  const klickAuf = async (code) => {
    const p = await schirm(wPlan[code].px);
    await page.mouse.click(p.x, p.y);
    await ruhe(1500);
  };
  const abwPlan = async (code) => { const b = await bohrung(code); return b.x === null ? Infinity : Math.hypot(b.x - wPlan[code].x, b.y - wPlan[code].y); };
  const freie = async () => (await stand()).z.punkte.length;
  await page.getByRole("button", { name: /Punkte im Plan setzen/ }).click();
  await ruhe(400);
  const p1Code = await page.locator("select.naechste option:checked").textContent();
  await klickAuf(p1Code.trim());
  const p2Code = await page.locator("select.naechste option:checked").textContent();
  await klickAuf(p2Code.trim());
  const abwKlick = [await abwPlan(p1Code.trim()), await abwPlan(p2Code.trim())];
  pruefe("Punkte setzen: je Klick eine Bohrung, danach die nächste ohne Lage (≤ 0,5 m)",
    Math.max(...abwKlick) <= 0.5 && p1Code.trim() !== p2Code.trim(), `${p1Code.trim()} ${abwKlick[0].toFixed(2)} m, ${p2Code.trim()} ${abwKlick[1].toFixed(2)} m`);
  await page.locator("select.naechste").selectOption("");                    // freier Punkt
  await klickAuf("B 4");
  const vorZuordnen = await freie();
  const sichtbarFrei = await page.locator(".punktmarke:not([hidden])").count();
  await page.locator("table.punkte tr.frei select").first().selectOption((await bohrung("B 4")).id);
  await warte((c) => window.app.z.bohrungen.find((b) => b.code === c)?.x !== null, "B 4", 30000);
  await ruhe(800);
  pruefe("Freier Punkt ◆ gesetzt und einer Bohrung zugeordnet", vorZuordnen === 1 && sichtbarFrei === 1 && (await freie()) === 0 &&
    (await abwPlan("B 4")) <= 0.5, `B 4 ${(await abwPlan("B 4")).toFixed(2)} m`);
  await page.locator(".park", { hasText: /^B 5$/ }).click();                // Chip = naechste Bohrung
  await ruhe(300);
  await klickAuf("B 5");
  await page.locator("table.punkte tr").filter({ has: page.locator("button.link", { hasText: new RegExp(`^● ${p1Code.trim()}$`) }) })
    .locator("button.symbol").click();
  await warte((c) => window.app.z.bohrungen.find((b) => b.code === c)?.x === null, p1Code.trim(), 30000);
  await page.locator("select.naechste").selectOption("");
  await klickAuf("B 8");
  const mb = await page.locator(".punktmarke").first().boundingBox();
  await page.mouse.click(mb.x + 6, mb.y + mb.height / 2);
  await ruhe(300);
  await page.keyboard.press("Delete");
  await ruhe(1500);
  const vorSchieben = await freie();
  const fl = await page.evaluate(() => { const r = window.viewer.world.renderer.three.domElement.getBoundingClientRect(); return { x: r.left + r.width * 0.7, y: r.top + r.height * 0.8 }; });
  await page.mouse.move(fl.x, fl.y);
  await page.mouse.down();
  await page.mouse.move(fl.x - 80, fl.y - 30, { steps: 8 });
  await page.mouse.up();
  await ruhe(1200);
  pruefe("Chip als nächste, ✕ in der Liste und Entf im Viewer löschen; Verschieben setzt keinen Punkt",
    (await abwPlan("B 5")) <= 0.5 && (await bohrung(p1Code.trim())).x === null && vorSchieben === 0 && (await freie()) === 0);
  await page.screenshot({ path: `${aus}/C3_punkte.png` });
  await page.keyboard.press("Escape");
  // direkt geoeffnet (#/<projekt>/lage): der orthografische Rahmen stand verkehrt (Bild um 180 Grad gedreht)
  const sigOhne = (await stand()).z.signatur;
  await page.goto("about:blank");                                            // neu laden, nicht nur die Adresse aendern
  await page.goto(`${url}/#/${sigOhne}/lage`);
  await warte(() => window.baugrund?.lage?.unterlage?.sichtbar && window.viewer?.editor?.aktiv);
  await ruhe(2500);
  const direkt = await page.evaluate(() => {
    const o = window.viewer.world.camera.threeOrtho;
    const r = window.viewer.world.renderer.three.domElement.getBoundingClientRect();
    const p = window.viewer.editor.bildZuSchirm(2000, 1500);
    return { rechts: o.right > o.left, oben: o.top > o.bottom, imBild: !!p && p.x > r.left && p.x < r.right && p.y > r.top && p.y < r.bottom };
  });
  pruefe("Direkt geöffnet: orthografischer Rahmen richtig herum, Plan im Bild", direkt.rechts && direkt.oben && direkt.imBild,
    JSON.stringify(direkt));

  // ---------------------------------------------------------------- D: Laengsschnitt
  await hochladen(`${plaene}/schnitt_extraktion.json`);
  pruefe("ohne Koordinaten: Lage = Reihe", (await stand()).z.lage_modus === "reihe");
  await zuLage();
  await unterlageHochladen(`${plaene}/schnitt.pdf`, "schnitt");
  await page.getByLabel("1:n eingeben").check();
  await page.locator("label.inline", { hasText: "Maßstab 1:" }).locator("input").fill("500");
  await page.locator("fieldset", { hasText: "Höhenmaßstab" }).getByLabel("1:n").check();
  await page.locator("label.inline", { hasText: "Höhe 1:" }).locator("input").fill("100");
  await punktKlick("Punkt im Plan wählen", wSchnitt["B 1"].px_top);
  await page.locator("label", { hasText: "Station [m]" }).locator("input").fill("0");
  await page.locator("label", { hasText: "Höhe [m NHN]" }).locator("input").fill(String(wSchnitt["B 1"].gok));
  await page.getByRole("button", { name: /Übernehmen und sperren/ }).click();
  await warte(() => window.baugrund?.lage?.unterlage?.gesperrt, null, 30000);
  await ruhe(1500);
  const schnittText = (await page.evaluate(() => window.baugrund.lage)).text;
  pruefe("Längsschnitt kalibriert (Länge 1:500, Höhe 1:100)", /Länge 1:500 · Höhe 1:100/.test(schnittText), schnittText);
  for (const code of ["B 2", "B 3", "B 4", "B 5", "B 6"]) {
    const von = await markenPunkt(code);
    const ziel = await schirm(wSchnitt[code].px_top);
    if (!von) continue;
    await ziehen(von, { x: ziel.x, y: ziel.y + 25 });         // auch nach unten: die GOK aus dem PDF darf sich nicht aendern
    await warte(([c, s]) => Math.abs((window.app.z.reihe.find((r) => r.code === c)?.station ?? -1) - s) < 1, [code, wSchnitt[code].station], 30000).catch(() => {});
    await ruhe(600);
  }
  z = (await stand()).z;
  const stationFehler = ["B 2", "B 3", "B 4", "B 5", "B 6"].map((c) => Math.abs(z.reihe.find((r) => r.code === c).station - wSchnitt[c].station));
  pruefe("Stationen aus dem Schnitt gezogen (Fehler ≤ 0,2 m)", Math.max(...stationFehler) <= 0.2, stationFehler.map((f) => f.toFixed(2)).join(" / "));
  const gokGleich = ["B 2", "B 3"].every((c) => Math.abs(z.bohrungen.find((b) => b.code === c).gok - wSchnitt[c].gok) < 1e-6);
  pruefe("GOK aus dem PDF bleibt beim Ziehen (nur Station)", gokGleich);
  await page.screenshot({ path: `${aus}/D1_schnitt.png` });
  await page.getByRole("button", { name: /Weiter: Einheiten/ }).click();
  await warte(() => document.querySelector("table.einheiten"), null, 180000);
  // Eingabefeld der Einheit "Kies" (Werte stehen nicht im Text der Zeile: Index ueber value suchen)
  const zeile = await page.evaluate(() => [...document.querySelectorAll("table.vorgabe tbody tr")]
    .findIndex((tr) => tr.querySelector("input")?.value === "Kies"));
  await page.locator("table.vorgabe tbody tr").nth(Math.max(0, zeile)).locator("input").first().fill("Kieslinse");
  await page.getByRole("button", { name: "Mit diesen Einheiten rechnen" }).click();
  await warte(() => window.app.modell?.bericht?.einheiten.some((e) => e.name === "Kieslinse") && !window.app.rechnet, null, 180000);
  pruefe("Einheit umbenannt (Vorgabe) und neu gerechnet", (await stand()).modell.einheiten.includes("Kieslinse"));
  await page.screenshot({ path: `${aus}/D2_einheiten.png` });
  // Ground Analysis (docs/27 G2): unter Erweitert, erst auf Klick; Kreuzprobe, Unsicherheit, virtuelle Bohrung
  await page.locator("details.analyse > summary").click();
  await page.getByRole("button", { name: "Analyse rechnen" }).click();
  await warte(() => document.querySelectorAll("details.analyse table").length >= 2 || document.querySelector("details.analyse p.warn"), null, 120000);
  await page.getByRole("button", { name: "Bohren", exact: true }).click();
  await warte(() => document.querySelector("details.analyse table.virtuell") || document.querySelector("details.analyse p.warn"), null, 60000);
  const ga = await page.evaluate(() => {
    const d = document.querySelector("details.analyse");
    return { tabellen: d.querySelectorAll("table").length, warn: d.querySelector("p.warn")?.textContent ?? "",
             vorschlaege: d.querySelectorAll("table.vorschlag tbody tr").length,
             sigma: [...d.querySelectorAll("table.virtuell tbody tr td:nth-child(4)")].map((x) => x.textContent) };
  });
  pruefe("Ground Analysis: Kreuzprobe, Unsicherheit, Erkundungsvorschlag und virtuelle Bohrung mit ± σ", ga.tabellen >= 3 && !ga.warn && ga.vorschlaege >= 1
    && ga.sigma.some((s) => /\d/.test(s)), JSON.stringify(ga));
  await page.locator("details.analyse").screenshot({ path: `${aus}/D3_analyse.png` });
  await page.getByRole("button", { name: /Weiter: Modell/ }).click();
  await warte(() => window.baugrund?.geladen && !window.app.rechnet, null, 240000);
  await ruhe(3000);
  const st = await page.evaluate(() => ({ einheiten: window.baugrund.einheiten, marken: window.baugrund.marken }));
  pruefe("Modell im Viewer", st.einheiten.includes("Kieslinse"), JSON.stringify(st));
  await page.locator(".app-panel input.breit").fill("E2E-Prüfung");
  await page.getByRole("button", { name: /Stand einchecken/ }).click();
  await warte(() => window.app.z.eincheckungen.length === 1, null, 30000);
  pruefe("Stand eingecheckt", (await stand()).z.eingecheckt?.startsWith("v1"));
  const sig = (await stand()).z.signatur;
  const ifc = await page.evaluate(async (s) => (await fetch(`/api/projekt/${s}/export/ifc`)).text(), sig);
  pruefe("IFC: Bodenansprache je Schicht, Beschreibungen je Einheit, Prüfstand",
    ifc.includes("CPset_Bodenansprache") && ifc.includes("'Beschreibungen'") && ifc.includes("Kieslinse") && ifc.includes("IFCLABEL('v1 "), `${(ifc.length / 1e6).toFixed(1)} MB`);
  // ueber den Anfrage-Kontext, nicht fetch in der Seite: ein erwartetes 400 waere sonst ein Konsolenfehler
  const bml = (await page.request.get(`${url}/api/projekt/${sig}/export/boreholeml`)).status();
  await aufklappen("Erweitert");                                       // BoreholeML und GeolDG: unter „Erweitert“
  const bmlText = await page.locator(".export-liste p.klein").textContent();
  pruefe("BoreholeML: ohne Koordinaten gesperrt (Knopf aus, Server 400)",
    bml === 400 && (await page.locator(".export-liste .knopf.aus", { hasText: "BoreholeML" }).count()) === 1 &&
    /^0 von \d+ Bohrungen/.test(bmlText), `${bml} · ${bmlText}`);
  // Ground Analysis im Viewer (docs/27 G2): Unterkante nach sigma gefaerbt, virtuelle Bohrung per Klick
  await page.getByRole("button", { name: "Unsicherheit zeigen" }).click();
  await warte(() => window.viewer?.world.scene.three.children.some((o) => o.name === "Unsicherheit"), null, 120000);
  const legende = await page.locator(".sigma-legende").innerText();
  await page.getByRole("button", { name: /Punkt im Viewer wählen/ }).click();
  await ruhe(400);
  // Ziel: ein Knoten der gezeigten Flaeche nahe ihrer Mitte, auf den Bildschirm projiziert (die Mitte der Leinwand
  // kann je nach Kamera neben dem Modell liegen)
  const ziel = await page.evaluate(() => {
    const w = window.viewer.world;
    const netz = w.scene.three.children.find((o) => o.name === "Unsicherheit");
    const pos = netz.geometry.getAttribute("position");
    netz.geometry.computeBoundingBox();
    const mitte = netz.geometry.boundingBox.getCenter(netz.position.clone());
    let best = 0, d = Infinity;
    for (let i = 0; i < pos.count; i++) {
      const dd = (pos.getX(i) - mitte.x) ** 2 + (pos.getZ(i) - mitte.z) ** 2;
      if (dd < d) { d = dd; best = i; }
    }
    const v = mitte.clone().set(pos.getX(best), pos.getY(best), pos.getZ(best)).project(w.camera.three);
    const r = w.renderer.three.domElement.getBoundingClientRect();
    return { x: r.left + (v.x + 1) / 2 * r.width, y: r.top + (1 - v.y) / 2 * r.height };
  });
  await page.mouse.click(ziel.x, ziel.y);
  await warte(() => document.getElementById("auswahl-name")?.textContent === "Virtuelle Bohrung", null, 60000).catch(() => {});
  const tafel = await page.locator("#auswahl-inhalt").innerText().catch(() => "");
  pruefe("Ground Analysis im Viewer: Unterkante nach σ gefärbt, virtuelle Bohrung per Klick",
    /σ Unterkante/.test(legende) && /Modell \(virtuelle Bohrung/.test(tafel) && /±/.test(tafel), `${legende.split("\n")[0]} · ${tafel.slice(0, 60)} · ${await page.locator("#meldung").innerText().catch(() => "")}`);
  await page.screenshot({ path: `${aus}/D4_analyse_viewer.png` });
  await page.getByRole("button", { name: "Unsicherheit ausblenden" }).click();
  // Grundwasserflaeche (docs/27 G5): mit Staenden blau im Viewer, ohne Staende ehrlich "keine"
  await page.getByRole("button", { name: "Grundwasserfläche zeigen" }).click();
  await page.locator(".grundwasser").waitFor({ timeout: 60000 }).catch(() => {});
  const gw = await page.locator(".grundwasser").innerText().catch(() => "");
  const gwNetz = await page.evaluate(() => window.viewer?.world.scene.three.children.some((o) => o.name === "Grundwasser"));
  const gemessen = Number((gw.match(/(\d+) gemessene/) ?? [])[1] ?? -1);
  pruefe("Grundwasserfläche: Stände gezählt, Fläche nur mit Ständen, Hinweis Bohrzeit",
    gemessen >= 0 && gwNetz === gemessen > 0 && /Bemessungswasserstand|keine Bohrung/.test(gw), gw.slice(0, 120));
  if (gwNetz) await page.getByRole("button", { name: "Grundwasser ausblenden" }).click();
  // GeolDG (P6, D96): Abschluss der Untersuchung -> Frist der Fachdaten; Paket mit Pruefliste und Modell (ohne
  // Koordinaten kein BoreholeML: das steht im LIESMICH)
  const abschluss = page.getByLabel("Abschluss der Untersuchung", { exact: true });     // nicht der Knopf "Hilfe: …"
  await abschluss.fill("2026-09-30");
  await abschluss.dispatchEvent("change");
  await warte(() => window.app.z.geoldg.angaben.abschluss === "2026-09-30", null, 30000).catch(() => {});
  await ruhe(500);
  const frist = (await page.locator('.fristen li[data-frist="fachdaten"]').textContent()).replace(/\s+/g, " ").trim();
  const ladenGeoldg = page.waitForEvent("download", { timeout: 240000 });
  await page.getByRole("link", { name: /Paket für den Geologischen Dienst/ }).click();
  const paketGeoldg = await ladenGeoldg;
  const rohGeoldg = readFileSync(await paketGeoldg.path()).toString("latin1");
  pruefe("GeolDG: Frist der Fachdaten aus dem Abschluss, Paket mit Prüfliste und Modell",
    /bis 30\.12\.2026/.test(frist) && rohGeoldg.startsWith("PK") && /_geoldg\.zip$/.test(paketGeoldg.suggestedFilename()) &&
    ["LIESMICH.txt", "pruefliste.csv", "bewertungsdaten_GeolDG_10/modelldokumentation.txt"].every((d) => rohGeoldg.includes(d)),
    `${frist} · ${paketGeoldg.suggestedFilename()} · ${Math.round(rohGeoldg.length / 1024)} KB`);
  await page.screenshot({ path: `${aus}/D3_modell.png` });

  // ---------------------------------------------------------------- E: PDF mit Extraktion
  await startseite();
  await aufklappen("Beispiele ausprobieren");
  await page.getByRole("button", { name: /Bohrprofil-PDF/ }).click();
  const fortschritt = await warte(() => document.querySelector(".fortschritt-karte"), null, 30000).then(() => true).catch(() => false);
  await warte(() => window.app?.schritt === "bohrungen" && document.querySelector(".schichten"), null, 300000);
  await page.locator(".schichten tbody tr").first().click();
  const bild = await warte(() => {
    const i = document.querySelector(".pdf-seite img");
    return i && i.complete && i.naturalWidth > 0 && document.querySelector(".bbox.schicht-bbox");
  }, null, 60000).then(() => true).catch(() => false);
  pruefe("PDF ausgewertet (Fortschritt) und Schicht im PDF markiert", bild, `Fortschritt sichtbar: ${fortschritt}`);
  await page.screenshot({ path: `${aus}/E1_quelle.png` });

  // ---------------------------------------------------------------- F: Standort ohne Gutachten (echter Dienst NRW, Marl)
  // Beispiel Dortmund: Projekt am Punkt im Schritt Lage, ohne Lageplan-Abschnitte (der Punkt ist georeferenziert)
  await startseite();
  // Start: zwei gleich grosse Wege, alles Weitere eingeklappt
  pruefe("Start: zwei Wege (Gutachten, Standort), Beispiele und Koordinaten eingeklappt",
    await page.evaluate(() => {
      const wege = [...document.querySelectorAll(".wege > .weg h2")].map((h) => h.textContent?.trim());
      const zu = (t) => [...document.querySelectorAll("details.still")].some((d) => d.textContent?.includes(t) && !d.open);
      return wege.join("|") === "Gutachten|Standort" && zu("Beispiele ausprobieren") && zu("Koordinaten eingeben");
    }));
  await aufklappen("Beispiele ausprobieren");
  await page.getByRole("button", { name: /Standort Dortmund \(NRW\)/ }).click();
  await warte(() => window.app.z?.standort && window.app.schritt === "lage", null, 60000);
  await ruhe(800);
  const titelF = (await page.locator(".app-panel details.abschnitt summary").allInnerTexts()).map((s) => s.replace(/[?\s]+$/u, "").trim());
  const zd = (await stand()).z;
  pruefe("Beispiel Standort Dortmund: im Schritt Lage, ohne Lageplan, NRW mit Schichtdaten",
    titelF[0] === "Standort" && !titelF.some((s) => /Unterlage|Bohrungen setzen|Lage der Bohrungen/.test(s)) &&
    zd.standort.epsg === 25832 && zd.standort.dienste.some((d) => d.dienst === "NW" && /Schichtdaten/.test(d.text)),
    JSON.stringify(titelF));
  // Karte als Pop-up: ein Klick in die Mitte (Deutschland) setzt Rechts-/Hochwert und System
  await startseite();
  await page.getByRole("button", { name: /Auf der Karte wählen/ }).click();
  await page.waitForSelector(".karte-dialog .leaflet-container", { timeout: 60000 });
  const karteBox = await page.locator(".karte-flaeche").boundingBox();
  await page.mouse.click(karteBox.x + karteBox.width / 2, karteBox.y + karteBox.height / 2);
  await warte(() => !document.querySelector(".karte-dialog .uebernehmen")?.disabled, null, 30000).catch(() => {});
  const karteInfo = (await page.locator(".karte-info").innerText()).replace(/\s+/g, " ");
  await page.getByRole("button", { name: "Punkt übernehmen" }).click();
  await ruhe(400);
  await aufklappen("Koordinaten eingeben");
  const rw = Number(await page.getByLabel("Rechtswert").inputValue());
  const hw = Number(await page.getByLabel("Hochwert").inputValue());
  pruefe("Karte als Pop-up: Klick setzt Rechts-/Hochwert (ETRS89/UTM) und zeigt die Dienste am Ort",
    rw > 150000 && rw < 850000 && hw > 5200000 && hw < 6150000 && (await page.getByLabel("System des Standorts").inputValue()) === "25832" &&
    !(await page.locator(".karte-dialog").count()) && /Bohrungen/.test(karteInfo), `${rw} / ${hw} · ${karteInfo.slice(0, 90)}`);
  await page.getByLabel("Rechtswert").fill("368130");
  await page.getByLabel("Hochwert").fill("5724400");
  await page.getByLabel("System des Standorts").selectOption("25832");
  await page.getByLabel("Name (frei)").fill("E2E Standort Marl");
  await page.getByRole("button", { name: /Projekt am Standort anlegen/ }).click();
  await warte(() => window.app.z?.standort && window.app.schritt !== "gutachten", null, 60000);
  // gibt es den Standort schon (zweiter Lauf), oeffnet er sich nur: verwerfen, dann wie neu im Schritt Lage
  await page.locator(".menue summary").click();
  await page.getByRole("button", { name: /Alle Korrekturen verwerfen/ }).click();
  await warte(() => window.app?.z?.version === 0 && window.app.schritt === "lage" && !window.app.z.bohrungen.length, null, 60000);
  const kopfAbzeichen = await page.locator(".kopf .abzeichen.vorerkundung").count();
  await aufklappen("Bohrungen der Länder");
  await page.getByRole("button", { name: "Abfragen" }).click();
  await warte(() => window.app.z.sgd, null, 180000);
  const sgdF = (await stand()).z.sgd;
  const netzNrw = sgdF.fehler.find((f) => f.dienst === "NW" && /^(keine Antwort|nicht erreichbar|HTTP 5\d\d)/.test(f.fehler));
  if (netzNrw) {
    ausgelassen(`Standort: Dienst NRW nicht erreichbar (${netzNrw.fehler}) – Prüfungen ausgelassen`);
  } else {
    const kaestchen = page.locator("table.sgd tbody input[type=checkbox]");
    const n = await kaestchen.count();
    for (let i = 0; i < n; i++) await kaestchen.nth(i).check();
    await page.getByRole("button", { name: /Ausgewählte übernehmen/ }).click();
    await warte(() => window.app.z.bohrungen.length >= 3, null, 180000);
    const zf = (await stand()).z;
    pruefe("Standort ohne Gutachten: Projekt am Punkt, Bohrungen der Länder übernommen, Vorerkundung im Kopf",
      kopfAbzeichen === 1 && zf.reifegrad.stufe === "Vorerkundung" && zf.bohrungen.every((b) => b.code.startsWith("NW-")),
      `${zf.bohrungen.length} Bohrungen · ${n} übernehmbar`);
    // Nullpunkt am Standort (auf 100 m), die Kamera passt auf den ersten Inhalt: alle Bohrungen im Lageplan
    await warte(huelleImBild, ["lage", true], 20000).catch(() => null);
    const bl = await page.evaluate(huelleImBild, ["lage", false]);
    pruefe("Standort: übernommene Bohrungen ganz im Lageplan, Nullpunkt bleibt am Standort",
      bl.ok && zf.viewer.ursprung[0] === 368100 && zf.viewer.ursprung[1] === 5724400,
      `${JSON.stringify(bl)} · Nullpunkt ${zf.viewer.ursprung}`);
    await page.locator("nav.schritte button", { hasText: "Modell" }).click();
    await warte(() => window.app.schritt === "modell" && window.app.modell?.ifc, null, 240000);
    await warte(modellDa, null, 240000);
    await ruhe(1500);
    const vf = await page.evaluate(() => ({ viewer: window.baugrund.reifegrad, bericht: window.app.modell?.bericht?.reifegrad,
                                            band: !document.querySelector("#reifegrad")?.hidden,
                                            panel: !!document.querySelector(".app-panel .reife.vorerkundung") }));
    pruefe("Modell aus Bohrungen der Länder: Vorerkundung im Bericht, im Modell-Schritt und als Band im Viewer",
      vf.viewer === "Vorerkundung" && vf.bericht === "Vorerkundung" && vf.band && vf.panel, JSON.stringify(vf));
    // nach dem Lage-Schritt: ganzes Modell schraeg, die Kamera nicht darin (That Opens Orbit setzte 300 m als Grenze)
    await warte(huelleImBild, ["modell", true], 20000).catch(() => null);
    const bm = await page.evaluate(huelleImBild, ["modell", false]);
    pruefe("Standort: Modell ganz im Bild, Kamera außerhalb", bm.ok, JSON.stringify(bm));
    await page.screenshot({ path: `${aus}/F_standort.png` });
  }

  // ---------------------------------------------------------------- H: Homogenbereiche (VOB/C, docs/28)
  {
    const post = (pfad, daten) => page.request.post(url + pfad, { data: daten }).then((r) => r.json());   // mit Anmeldung
    const hsig = (await post("/api/beispiel", { name: "demo" })).projekt;
    await post(`/api/projekt/${hsig}/aendern`, { ops: [{ op: "homogenbereiche", atv: "DIN 18300", zuordnung: null }] });
    await page.goto(`${url}/#/${hsig}/einheiten`);
    await page.reload();
    await page.waitForSelector("table.einheiten", { timeout: 240000 });
    await ruhe(800);
    const hb = page.locator("details.homogenbereiche");
    if (!(await hb.evaluate((d) => d.open))) await hb.locator("summary").click();
    await page.getByRole("button", { name: /Vorschlag: je Einheit/ }).click();
    await page.waitForFunction(() => Object.keys(window.app?.z?.homogenbereiche?.["DIN 18300"] ?? {}).length > 0, null, { timeout: 30000 });
    const felder = page.locator("table.hb-zuordnung input");
    const zweiter = await felder.nth(1).inputValue();
    await felder.nth(2).fill(zweiter);
    await felder.nth(2).press("Tab");
    await page.waitForFunction((b) => Object.values(window.app?.z?.homogenbereiche?.["DIN 18300"] ?? {}).filter((x) => x === b).length === 2,
      zweiter, { timeout: 30000 });
    const kennwerte = await page.locator("ul.hb-kennwerte li").count();
    const nEinheiten = await felder.count();
    await page.getByLabel(/Homogenbereiche DIN 18300/).check();
    await page.waitForFunction(() => window.app?.z?.hb_modell === "DIN 18300", null, { timeout: 30000 });
    await page.screenshot({ path: `${aus}/H_homogenbereiche.png` });
    await page.goto(`${url}/#/${hsig}/modell`);
    await page.reload();
    await warte(() => window.baugrund?.geladen && !window.app?.rechnet && window.baugrund.einheiten.length > 0, null, 240000);
    const v = await page.evaluate(() => ({ einheiten: window.baugrund.einheiten,
      liste: window.baugrund.modellname.startsWith("Homogenbereiche DIN 18300") }));
    pruefe("Homogenbereiche DIN 18300: Zuordnung, 13 Kennwerte, IFC aus Bereichen im Viewer",
      kennwerte === 13 && v.einheiten.includes(zweiter) && v.einheiten.length === nEinheiten - 1 && v.liste,
      JSON.stringify({ kennwerte, ...v }));
    await page.screenshot({ path: `${aus}/H_modell.png` });
    await post(`/api/projekt/${hsig}/aendern`, { ops: [{ op: "homogenbereiche", atv: "DIN 18300", zuordnung: null }] });
  }

  // ---------------------------------------------------------------- G: Werkzeug „Dienste der Länder“ (ohne Speichern)
  await page.goto(`${url}/dienste.html`);
  await page.waitForSelector("table.matrix .chip", { timeout: 60000 });
  const matrix = await page.evaluate(() => {
    const zeilen = [...document.querySelectorAll("table.matrix tbody tr")];
    const luecken = zeilen.filter((z) => z.querySelector("th")?.textContent !== "Deutschland")
      .filter((z) => [...z.querySelectorAll("td")].some((td) => !td.querySelector(".chip"))).map((z) => z.querySelector("th")?.textContent);
    return { zeilen: zeilen.length, luecken, bearbeiten: window.werkzeug?.reg?.bearbeiten, datei: window.werkzeug?.reg?.datei };
  });
  pruefe("Dienste der Länder: alle 16 Länder × Bohrungen, Gelände, Gebäude (dazu bundesweit)",
    matrix.zeilen === 17 && !matrix.luecken.length && /dienste\.json$/.test(matrix.datei ?? ""), JSON.stringify(matrix));
  await page.locator("table.matrix").getByRole("button", { name: "BY", exact: true }).click();
  await page.waitForSelector(".editor h2", { timeout: 10000 });
  if (matrix.bearbeiten) {
    const hinweis = page.locator(".editor textarea[name=hinweis]");
    const vorher = await hinweis.inputValue();
    await hinweis.fill(`${vorher} (E2E)`);
    const leiste = await page.locator(".speicherleiste").isVisible();
    await page.locator(".speicherleiste").getByRole("button", { name: "Verwerfen" }).click();        // Dialog: angenommen
    await ruhe(300);
    pruefe("Dienste der Länder: Eintrag bearbeiten zeigt „nicht gespeichert“, Verwerfen stellt ihn wieder her",
      leiste && !(await page.locator(".speicherleiste").count()) && (await hinweis.inputValue()) === vorher &&
      (await page.locator(".editor h2").textContent())?.trim() === "BY");
  } else {
    pruefe("Dienste der Länder: im Netz nur lesen (Hinweis, Felder gesperrt)",
      (await page.locator(".nur-lesen").count()) === 1 && (await page.locator(".editor input[name=titel]").isDisabled()));
  }
  await page.screenshot({ path: `${aus}/G_dienste.png` });
} finally {
  const fehlgeschlagen = pruefungen.filter((p) => !p.ok);
  console.log(`\n${pruefungen.length - fehlgeschlagen.length}/${pruefungen.length} Pruefungen bestanden`);
  console.log("Seitenfehler:", fehler.length ? fehler : "keine");
  await browser.close();
  if (fehler.length || fehlgeschlagen.length) process.exitCode = 1;
}
