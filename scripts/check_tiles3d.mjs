// Pruefung des 3D-Tiles-Exports (docs/21 §5.2): offizieller Validator von CesiumGS und Lage im echten CesiumJS.
//
//   npm install --prefix <werkzeuge> 3d-tiles-validator@0.6.1 cesium@1.147.0      (einmal, ausserhalb des Repos)
//   node scripts/check_tiles3d.mjs <tileset-ordner> <werkzeuge> [erwartet.json] [bild.png]
//
// <tileset-ordner>: entpackter Export (tileset.json, *.glb). erwartet.json: [{code, lon, lat, h_ell}] - Lage und
// ellipsoidische Hoehe von Punkten auf der Oberkante, unabhaengig berechnet (PROJ). Ohne Datei: drei Bohrungen des
// Berliner Beispiels (GOK 36,25 / 36,25 / 35,65 m NHN + GCG2016, Lage aus PROJ). Cesium tastet dort die Hoehe des
// Modells ab (sampleHeightMostDetailed); erlaubt sind 2 cm.
import { createRequire } from "node:module";
import { createServer } from "node:http";
import { execFileSync } from "node:child_process";
import { readFileSync, existsSync, statSync } from "node:fs";
import { extname, join, resolve } from "node:path";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PFAD ?? "playwright");
const [ordner, werkzeuge, erwartetDatei, bild] = process.argv.slice(2);
if (!ordner || !werkzeuge) {
  console.error("node scripts/check_tiles3d.mjs <tileset-ordner> <werkzeuge> [erwartet.json] [bild.png]");
  process.exit(2);
}
const BERLIN = [
  { code: "422C-460", lon: 13.449672912775217, lat: 52.50500275154702, h_ell: 75.5 },
  { code: "422C-461", lon: 13.449612718883937, lat: 52.505289675902624, h_ell: 75.499 },
  { code: "422C-5525", lon: 13.450581526014542, lat: 52.506189781995815, h_ell: 74.896 },
];
const erwartet = erwartetDatei ? JSON.parse(readFileSync(erwartetDatei, "utf8")) : BERLIN;
const ergebnisse = [];
const pruefe = (name, ok, info = "") => { ergebnisse.push(ok); console.log(`${ok ? "OK  " : "FEHL"} ${name}${info ? ` – ${info}` : ""}`); };

// 1. offizieller Validator (prueft auch jedes GLB mit dem glTF-Validator)
const bericht = join(resolve(ordner), "validator_bericht.json");
try {
  execFileSync(join(werkzeuge, "node_modules", ".bin", "3d-tiles-validator"),
    ["--tilesetFile", join(resolve(ordner), "tileset.json"), "--reportFile", bericht], { stdio: "pipe" });
} catch { /* der Bericht sagt, was fehlt */ }
const b = JSON.parse(readFileSync(bericht, "utf8"));
pruefe("3d-tiles-validator: keine Fehler, keine Warnungen", b.numErrors === 0 && b.numWarnings === 0,
  `${b.numErrors} Fehler, ${b.numWarnings} Warnungen, ${b.numInfos} Hinweise`);

// 2. Cesium: Seite mit dem Tileset, Hoehen an den erwarteten Punkten
const cesium = join(werkzeuge, "node_modules", "cesium", "Build", "Cesium");
const SEITE = `<!doctype html><html><head><meta charset="utf-8"><script>window.CESIUM_BASE_URL="/cesium/";</script>
<script src="/cesium/Cesium.js"></script><link href="/cesium/Widgets/widgets.css" rel="stylesheet">
<style>html,body,#c{margin:0;width:100%;height:100%;overflow:hidden}</style></head><body><div id="c"></div><script>
(async () => { try {
  const viewer = new Cesium.Viewer("c", { baseLayer: false, baseLayerPicker: false, geocoder: false, homeButton: false,
    sceneModePicker: false, navigationHelpButton: false, animation: false, timeline: false, fullscreenButton: false,
    infoBox: false, selectionIndicator: false });
  viewer.scene.globe.show = false;
  const tileset = await Cesium.Cesium3DTileset.fromUrl("/tiles/tileset.json");
  viewer.scene.primitives.add(tileset);
  await viewer.zoomTo(tileset, new Cesium.HeadingPitchRange(Cesium.Math.toRadians(30), Cesium.Math.toRadians(-35), 0));
  await new Promise((r) => { const f = () => tileset.tilesLoaded ? r() : setTimeout(f, 200); f(); });
  const erwartet = ${JSON.stringify(erwartet)};
  const h = await viewer.scene.sampleHeightMostDetailed(erwartet.map((p) => Cesium.Cartographic.fromDegrees(p.lon, p.lat)));
  window.ergebnis = erwartet.map((p, i) => ({ code: p.code, soll: p.h_ell, ist: h[i] ? h[i].height : null }));
} catch (err) { window.ergebnis = { fehler: String(err && err.stack || err) }; } })();
</script></body></html>`;
const ARTEN = { ".js": "text/javascript", ".json": "application/json", ".glb": "model/gltf-binary", ".css": "text/css",
                ".wasm": "application/wasm", ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml" };
const server = createServer((anf, ant) => {
  const pfad = decodeURIComponent(anf.url.split("?")[0]);
  const datei = pfad === "/" ? null : pfad.startsWith("/tiles/") ? join(resolve(ordner), pfad.slice(7))
    : pfad.startsWith("/cesium/") ? join(cesium, pfad.slice(8)) : null;
  if (pfad === "/") { ant.writeHead(200, { "Content-Type": "text/html" }); ant.end(SEITE); return; }
  if (!datei || !existsSync(datei) || statSync(datei).isDirectory()) { ant.writeHead(404); ant.end(); return; }
  ant.writeHead(200, { "Content-Type": ARTEN[extname(datei)] ?? "application/octet-stream" });
  ant.end(readFileSync(datei));
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const browser = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
const fehler = [];
page.on("pageerror", (e) => fehler.push(String(e)));
try {
  await page.goto(`http://127.0.0.1:${server.address().port}/`);
  await page.waitForFunction(() => window.ergebnis, null, { timeout: 240000 });
  const erg = await page.evaluate(() => window.ergebnis);
  if (erg.fehler) pruefe("Cesium lädt das Tileset", false, erg.fehler);
  else {
    for (const p of erg) {
      pruefe(`Cesium: Oberkante bei ${p.code} auf der erwarteten ellipsoidischen Höhe (±2 cm)`,
        p.ist !== null && Math.abs(p.ist - p.soll) <= 0.02, `soll ${p.soll.toFixed(3)} m, ist ${p.ist?.toFixed(3)} m`);
    }
  }
  if (bild) await page.screenshot({ path: bild });
} finally {
  await browser.close();
  server.close();
}
const ok = ergebnisse.filter(Boolean).length;
console.log(`\n${ok}/${ergebnisse.length} Pruefungen bestanden · Seitenfehler: ${fehler.length ? fehler.join(" | ") : "keine"}`);
process.exitCode = ok === ergebnisse.length && !fehler.length ? 0 : 1;
