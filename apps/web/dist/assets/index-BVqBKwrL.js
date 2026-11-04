const __vite__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["./leaflet-CIGW-MKW.css","./store-Boho82ME.js","./preload-helper-Ct5FWWRu.js"])))=>i.map(i=>d[i]);
import"./viewer-DAT6rRHi.js";import{_ as ke}from"./preload-helper-Ct5FWWRu.js";import{b as a,A as u,w as j,l as k,m as cn,k as Pe,D as un}from"./lage-aaRnPTcx.js";import{a as $,S as s,n as g,o as V,v,m as G,p as Qe,s as ne,b as ge,c as De,d as m,z as P,e as pe,f as dn,g as T,h as hn,i as gn,j as ae}from"./store-Boho82ME.js";import"./three.core-Dd2BBCN2.js";const we={ocr:["OCR für Scans","Liest gescannte PDFs und Text, der nur als Linien gezeichnet ist (SHX). Langsamer; bei Vektor-PDFs nicht nötig."],beispiele:["Beispiele","Fertig ausgewertete Gutachten zum Ausprobieren. Echte Daten: Berlin (georeferenziert) und Talheim (ohne Koordinaten). Dazu Standorte ohne Gutachten, die zeigen, was die Länder liefern: Dortmund (NRW, Bohrungen mit Schichtdaten), Karlsruhe (Baden-Württemberg, Schichten oft ohne Petrographie) und Berlin (nur Kopfdaten: Gelände und Gebäude, kein Schichtenmodell). Die Bohrungen fragt der Schritt Lage auf Klick beim Land ab (Netz nötig)."],karte:["Karte","Eine Karte zum Orientieren: ein Klick setzt den Standort; Rechts- und Hochwert in ETRS89/UTM rechnet die App aus (Zone 32 westlich von 12° Ost, sonst 33) und sagt, was die Dienste der Länder dort liefern. Hintergrund basemap.de (amtlich, © GeoBasis-DE / BKG, CC BY 4.0) oder OpenStreetMap. Die Kacheln laden erst beim Öffnen – der Kartenausschnitt geht an diesen Server. Auf wenige Meter genau (Karte in WGS84): für eine Vorerkundung genug."],pruefstand:["Prüfstand","Wie viele Bohrungen und Schichten Sie geprüft haben. Eine Korrektur zählt als geprüft. Der Stand wird beim Einchecken festgehalten."],alle_pruefen:["Alle geprüft","Markiert alle Schichten aller Bohrungen im Modell als geprüft – nur wenn Sie alles mit dem Gutachten verglichen haben. Zurücknehmen ist jederzeit möglich."],warnung:["Warnung","Eine Schicht, deren Bodenart nicht erkannt wurde (unklassifiziert). Bodenart wählen, den Vorschlag nach Norm übernehmen oder die Schicht als geprüft markieren."],bodenart:["Bodenart","Klasse für das Modell; Farbe nach DIN 4023 (Kies gelb, Sand orange, Schluff oliv, Ton violett …). Gleiche Bodenarten werden zu Einheiten verbunden."],norm:["Deutung nach Norm","Die Beschreibung aus dem PDF gelesen nach DIN 4023 / DIN EN ISO 14688-1: Hauptanteil, Nebenanteile (schwach ' / stark ¯), Kurzzeichen, Bodengruppe nach DIN 18196 (nur wenn genannt), Konsistenz. Steht auch im IFC (CPset_Bodenansprache)."],vorschlag:["Vorschlag nach Norm","Für eine unklassifizierte Schicht schlägt die Normen-Datenbank eine Bodenart aus der Beschreibung vor. Sie wird nur übernommen, wenn Sie klicken; danach gilt die Schicht als korrigiert."],geprueft:["Geprüft","Haken: Schicht mit dem Gutachten verglichen. Steht im IFC (Geprueft) und im Prüfstand."],tiefe:["Tiefe","Ober- und Unterkante in m unter Geländeoberkante (GOK). Geändertes wird als korrigiert markiert."],gok:["GOK","Ansatzhöhe der Bohrung in m NHN. Aus dem PDF oder hier eingetragen (manuell). Ohne GOK bei allen Bohrungen rechnet das Modell relativ (Gelände = 0 m)."],koordinaten:["Koordinaten","Rechts- und Hochwert der Bohrung; leer lassen, wenn die Lage im Schritt Lage auf dem Plan gesetzt wird."],entfernen:["Entfernen","Die Bohrung kommt nicht ins Modell (sie bleibt in der Liste unter „Entfernt“ und lässt sich wiederherstellen)."],quelle:["Quelle im PDF","Die Seite des Gutachtens, auf der die Bohrung erkannt wurde; der Rahmen zeigt die gewählte Schicht."],lage_art:["Art der Lage","Koordinaten: Bohrungen mit Rechts-/Hochwert (aus dem PDF, eingetragen oder auf dem Lageplan gesetzt). Reihe: ohne Koordinaten nebeneinander mit Abständen bzw. Stationen aus dem Längsschnitt."],unterlage:["Unterlage","Lageplan (Draufsicht) oder Längsschnitt (Seitenansicht) als PDF. Er liegt im Viewer unter den Bohrungen; nach dem Kalibrieren werden die Bohrungen daraufgezogen."],massstab:["Maßstab","Zwei Punkte auf dem Plan anklicken, deren Abstand Sie kennen (Maßstabsleiste, Bemaßung, zwei Bohrungen), und die wahre Länge in m eintragen. Oder den Maßstab 1:n direkt angeben."],bezug:["Bezugspunkt","Ein Punkt im Plan mit bekannter Koordinate (Koordinatenkreuz, Bohrung mit Koordinaten): anklicken und Rechts-/Hochwert eintragen – im Längsschnitt Station und Höhe NHN."],drehung:["Drehung","Winkel, um den der Plan gegen Norden gedreht ist (gegen den Uhrzeigersinn positiv). Nordpfeil nach oben = 0°; Nordpfeil 10° nach links geneigt = 10°."],hoehe:["Höhenmaßstab","Längsschnitte sind oft überhöht (z. B. Länge 1:500, Höhe 1:100). Ohne Angabe gilt der Längenmaßstab."],epsg:["Koordinatensystem (EPSG)","System der Rechts-/Hochwerte aus der Liste wählen: in Deutschland meist ETRS89 / UTM 32N (25832), im Osten 33N (25833), ältere Pläne Gauß-Krüger (Rechtswert 7-stellig, erste Ziffer = Zone); dazu Schweiz und Österreich. Passen die Werte nicht zum System (Ziffernzahl, Zonenkennung), erscheint ein Hinweis. Steht im IFC (IfcMapConversion)."],sperren:["Sperren","Schloss zu: der Plan liegt fest und ändert sich nicht mehr; jetzt die Bohrungen ziehen. Auf dem Lageplan nur in x/y, im Längsschnitt entlang der Station – in der Höhe nur, wenn das PDF keine GOK hat."],deckkraft:["Deckkraft","Wie stark der Plan die Szene überdeckt."],ohne_lage:["Ohne Lage","Bohrungen ohne Koordinaten: anklicken und dann in den gesperrten Plan klicken (Punkte setzen) – oder mit der Maus aus der Liste auf den Plan ziehen."],punkte:["Punkte setzen","Modus an, dann in den gesperrten Lageplan klicken: die gewählte Bohrung bekommt die Lage, danach ist die nächste ohne Lage dran (oder einen Chip anklicken). Mit „freien Punkt“ entsteht ein Punkt ◆, den Sie in der Liste einer Bohrung zuordnen. ✕ löscht einen Punkt bzw. die gesetzte Lage – im Viewer ebenso: Marke anklicken, Entf. Esc beendet den Modus."],reihe:["Reihe","Bohrungen in einer Linie. Abstand zum Vorgänger je Bohrung eintragen (BK1 → BK2 10 m, BK2 → BK3 15 m) oder eine Station; ohne Eintrag gilt der Standardabstand. Reihenfolge mit den Pfeilen."],standardabstand:["Standardabstand","Abstand zwischen Bohrungen, für die nichts eingetragen ist (nur zur Anschauung, im Modell als schematisch markiert)."],boreholeml:["BoreholeML","Austauschformat der Geologischen Dienste der Länder (Version 3.2). Exportiert werden nur vollständig geprüfte Bohrungen mit Lage in ETRS89/UTM und GOK in m NHN; Petrographie, Genese, Konsistenz, Lagerung, Kalk und Feuchte über die amtlichen Codelisten, die Beschreibung aus dem Gutachten im Klartext. Die Organisation steht als Absender in der Datei. Welche Bohrungen ausgelassen wurden und warum, steht oben in der Datei. Umgekehrt lassen sich BoreholeML-Dateien wie ein Gutachten hochladen (Bohrungen der Länder)."],sgd:["Bohrungen der Länder","Bohrungen aus den Datenbanken der Geologischen Dienste um die Mitte des Projekts: Berlin und Brandenburg mit Kopfdaten und dem Schichtenverzeichnis als Grafik, NRW und Baden-Württemberg in BoreholeML mit den freigegebenen Schichtdaten. Abgefragt wird nur auf Klick – die Anfrage sendet die Lage des Projekts an den Dienst. Bohrungen des Gutachtens, die auch beim Land liegen, zeigen die Abweichung von Lage und GOK (Gegenprobe). Übernommene Bohrungen tragen Quelle, Lizenz und Datum, erscheinen als Raute und gehen nicht in den BoreholeML-Export."],gelaende:["Gelände (DGM)","Digitales Geländemodell der Vermessungsverwaltung (Open Data, meist DGM1 mit 1 m Raster) für das Baufeld herunterladen und hier laden: XYZ, ASCII-Raster oder GeoTIFF, mehrere Kacheln auch als ZIP. Die App vergleicht die GOK aus dem PDF mit dem Gelände: liegen alle Bohrungen gleich viel höher oder tiefer, stimmen Lage, EPSG oder Höhenbezug nicht. Fehlende GOK schlägt sie vor – übernommen wird nur auf Klick, markiert als „DGM“ (auch im IFC)."],dgm_land:["DGM vom Land","Holt das DGM1 (1 m) für den Ausschnitt um die Bohrungen plus Rand direkt beim Dienst des Landes (WCS): bisher Brandenburg mit Berlin und NRW. Nur auf Klick – die Anfrage sendet den Ausschnitt an den Dienst. Quelle, Lizenz und Namensnennung bleiben am DGM und gehen ins IFC. Baden-Württemberg liefert über seinen Dienst nur ganze Meter, Bayern hat keinen freien Dienst: dort die DGM1-Kacheln als Datei laden."],gebaeude:["Gebäude (LoD2)","3D-Gebäudemodelle LoD2 der Länder als Umgebung des Baugrundmodells: Berlin, Brandenburg und NRW geben sie als CityGML-Kacheln von 1 × 1 km heraus, in ETRS89/UTM mit Höhen in m NHN – derselbe Rahmen wie das Modell. Nur auf Klick werden die Kacheln um die Bohrungen (plus Rand) geladen; Gebäude, deren Grundriss den Ausschnitt berührt, kommen ins IFC (IfcBuildingElementProxy mit Wänden und Dach, Quelle und Lizenz je Gebäude) und in den Viewer (Knopf „Gebäude“). Bestand, nicht erkundet."],standort:["Standort ohne Gutachten","Ein Projekt an einem Punkt (ETRS89/UTM, aus der Karte oder eingetragen): im Schritt Lage fragt es die Bohrungen der Länder um den Punkt ab, holt das DGM und die Gebäude – ein Lageplan ist nicht nötig, der Punkt ist schon georeferenziert. Übernommene Bohrungen mit Schichtdaten (NRW, Baden-Württemberg) ergeben ein Modell – eine Vorerkundung: Archivdaten unbekannter Güte, ohne Sondierungen, oft alt oder weit weg. Kommt später das Gutachten, entsteht ein neues Projekt, das die Bohrungen der Länder, DGM und Gebäude mitnimmt (gemischt)."],reifegrad:["Reifegrad","Woraus das Modell besteht: Gutachten (nur Bohrungen aus dem PDF), Vorerkundung (nur Bohrungen aus Datenbanken der Länder oder BoreholeML-Dateien) oder gemischt. Er steht in der App, im Viewer, im Prüfbericht und im IFC (CPset_Baugrundmodell.Reifegrad); jede Bohrung trägt ihre Herkunft mit Quelle und Lizenz (CPset_Herkunft)."],gelaende_dgm:["Gelände aus dem DGM","Mit DGM folgt die Oberkante des Modells dem Gelände statt der Interpolation zwischen den GOK. An jeder Bohrung bleibt sie genau auf der GOK; deren Abweichung vom DGM klingt bis zur Reichweite (halber Bohrabstand, höchstens 25 m) ab. Im IFC liegt das Gelände um das Modell als IfcGeographicElement (TERRAIN), im Viewer mit dem Knopf „Gelände“ ein- und ausblendbar. Deckt das DGM das Modellgebiet nicht ganz ab, bleibt die Oberkante aus den GOK (mit Hinweis)."],dgm_epsg:["System der DGM-Datei","XYZ- und ASCII-Dateien enthalten kein Koordinatensystem: das System der Kacheln wählen (meist dasselbe wie das Projekt, z. B. 25832). Ein GeoTIFF bringt es selbst mit."],durchmesser:["Durchmesser","Dicke der Bohrsäulen im Viewer und im IFC (Darstellung, nicht der Bohrdurchmesser im Feld). Automatisch wächst er mit der Modellgröße, damit Säulen auf langen Trassen sichtbar bleiben."],einheiten:["Einheiten","Modelleinheiten verbinden gleiche Bodenarten zwischen den Bohrungen (Sand 1, Kies, Sand 2). Umbenennen oder Bodenarten zusammenlegen (z. B. „Sand, Kies“ als eine Einheit); Reihenfolge von oben nach unten."],methode:["Interpolation","IDW: gewichtetes Mittel der Nachbarbohrungen, ruhig und sicher. Dünnplatten-Spline: glatte Flächen mit Trend, gut bei geneigten Schichten."],puffer:["Puffer","Wie weit das Modell über die Bohrungen hinausreicht. Automatisch: halber Bohrabstand (5–100 m)."],raster:["Raster","Maschenweite der Schichtflächen. Automatisch: Gebietsgröße/40, bei großen Modellen gröber (höchstens 30 000 Knoten)."],basis:["Modellbasis","Unterkante des Modells in m NHN. Automatisch: tiefste Endteufe."],gok_relativ:["Fehlende GOK","Hat keine Bohrung eine GOK, rechnet das Modell relativ (Gelände = 0 m) – markiert im IFC."],auto:["Automatisch nachführen","Jede Änderung (Tabelle, Lage, Einheiten) rechnet das Modell sofort neu."],einchecken:["Einchecken","Hält den Prüfstand fest (Zeit, Zähler, Fingerabdruck des Modells, Kommentar). Das exportierte IFC trägt ihn (CPset_Baugrundmodell.Pruefstand)."],tiles3d:["3D Tiles für Cesium","Das Baugrundmodell als 3D Tiles 1.1 (tileset.json und glTF) für CesiumJS, Cesium for Unreal oder QGIS 3D: Baugrundmodell, Gelände und Gebäude je eine Kachel. Jeder Punkt wird exakt aus ETRS89/UTM umgerechnet, die Höhen ellipsoidisch mit dem Quasigeoid GCG2016 des BKG (CC BY 4.0; beim ersten Export einmal 1 MB geladen). ETRS89 ist nicht in WGS84/ITRF überführt (rund 0,9 m). Quellen und Lizenzen stehen in LIESMICH.txt."],geoldg:["Geologiedatengesetz (GeolDG)","Wer bohrt oder bohren lässt, muss die Untersuchung beim Geologischen Dienst des Landes anzeigen und die Daten übermitteln: Anzeige spätestens zwei Wochen vor Beginn (§ 8), Fachdaten wie das Schichtenverzeichnis spätestens drei Monate nach Abschluss (§ 9), Bewertungsdaten wie Gutachten und räumliche Modelle mit Dokumentation auf Verlangen (§ 10). Die Liste zeigt je Bohrung, was GroundTwin liefert (Lage, GOK, Endteufe, geprüfte Schichten) und was aus dem Bohrprotokoll kommt (Bohrverfahren, Ausbau, Proben, Messungen, Labor). Das Paket enthält BoreholeML, IFC, Prüfbericht, Modelldokumentation und eine Prüfliste zum Ergänzen. Hilfe, keine Rechtsberatung: Form und Weg legt die zuständige Behörde fest."],geoldg_abschluss:["Abschluss der Untersuchung","Die Untersuchung gilt mit Ablauf der Dauer als abgeschlossen, die in der Anzeige angegeben wurde – außer eine Fortdauer wurde rechtzeitig angezeigt (§ 15 Abs. 1). Ab dann laufen drei Monate für die Fachdaten; ist eine Behörde verpflichtet, etwa als Auftraggeber, sechs Monate für die Bewertungsdaten (§ 10 Abs. 2 Satz 2). Die Daten bleiben im Projekt."],export:["Export","IFC 4.3 mit Prüfstand, Bodenansprache je Schicht und Beschreibungen je Einheit; dazu Prüfbericht und die Daten als JSON."],ueberhoehung:["Überhöhung","Höhen im Viewer mal Faktor, damit dünne Schichten sichtbar werden. Die Koordinaten bleiben echt."]};let L=null,ve=null;function re(){L?.remove(),L=null,ve=null}function pn(e,t){e.preventDefault(),e.stopPropagation();const n=e.currentTarget;if(ve===n){re();return}re();const[i,l]=we[t];L=document.createElement("div"),L.className="hilfe-blase",L.setAttribute("role","tooltip"),L.innerHTML="<strong></strong><p></p>",L.querySelector("strong").textContent=i,L.querySelector("p").textContent=l,document.body.append(L);const r=n.getBoundingClientRect(),o=L.getBoundingClientRect(),d=Math.min(Math.max(8,r.left+r.width/2-o.width/2),window.innerWidth-o.width-8),p=r.bottom+8+o.height>window.innerHeight?r.top-o.height-8:r.bottom+8;Object.assign(L.style,{left:`${d}px`,top:`${p}px`}),ve=n}document.addEventListener("click",e=>{L&&!L.contains(e.target)&&re()});document.addEventListener("keydown",e=>{e.key==="Escape"&&re()});const h=e=>a`<button type="button" class="hilfe" title=${we[e][0]} aria-label=${`Hilfe: ${we[e][0]}`}
    @click=${t=>pn(t,e)}>?</button>`,mn="https://sgx.geodatenzentrum.de/wmts_basemapde/tile/1.0.0/de_basemapde_web_raster_farbe/default/GLOBAL_WEBMERCATOR/{z}/{y}/{x}.png",bn="https://tile.openstreetmap.org/{z}/{x}/{y}.png",Ee=[51.16,10.45];let Z=null;const Ne=e=>e.replace(/[&<>"]/g,t=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[t]),Ae=e=>e.toLocaleString("de-DE",{minimumFractionDigits:1,maximumFractionDigits:1});async function fn(){const[{default:e}]=await Promise.all([ke(()=>import("./leaflet-src-7ah4FPQk.js").then(t=>t.l),[],import.meta.url),ke(()=>Promise.resolve({}),__vite__mapDeps([0]),import.meta.url)]);return new Promise(t=>{const n=document.createElement("dialog");n.className="karte-dialog",n.setAttribute("aria-label","Standort auf der Karte wählen"),n.innerHTML=`
      <header><strong>Standort auf der Karte wählen</strong>
        <button type="button" class="symbol schliessen" aria-label="Karte schließen">✕</button></header>
      <div class="karte-flaeche"></div>
      <footer>
        <div class="karte-info klein" aria-live="polite">In die Karte klicken: der Punkt wird der Standort (zum Orientieren,
          auf wenige Meter genau). Mausrad zoomt, Ziehen verschiebt.</div>
        <div class="zeile"><span class="fueller"></span>
          <button type="button" class="abbrechen">Abbrechen</button>
          <button type="button" class="primaer uebernehmen" disabled>Punkt übernehmen</button></div>
      </footer>`,document.body.append(n),n.showModal();const i=n.querySelector(".karte-info"),l=n.querySelector(".uebernehmen"),r=e.map(n.querySelector(".karte-flaeche"),{zoomControl:!0,attributionControl:!0}).setView(Z?[Z.breite,Z.laenge]:Ee,Z?.zoom??6),o=new Date().getFullYear(),d=e.tileLayer(mn,{maxZoom:18,attribution:`© <a href="https://basemap.de" target="_blank" rel="noopener">GeoBasis-DE / BKG (${o})</a> <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>`}).addTo(r),p=e.tileLayer(bn,{maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap-Mitwirkende</a>'});e.control.layers({"basemap.de (BKG)":d,OpenStreetMap:p},{},{position:"topright"}).addTo(r),e.control.scale({imperial:!1}).addTo(r);const c=e.circleMarker(Ee,{radius:8,color:"#10210a",weight:2,fillColor:"#a2c513",fillOpacity:.95});let z=null,S=0;r.on("click",async D=>{const b=++S;c.setLatLng(D.latlng).addTo(r),z=null,l.disabled=!0,i.textContent="wird umgerechnet …";try{const _=await $.standortPunkt(Number(D.latlng.lng.toFixed(7)),Number(D.latlng.lat.toFixed(7)));if(b!==S)return;z=_,l.disabled=!1,i.innerHTML=`<b>Rechtswert ${Ae(_.x)} · Hochwert ${Ae(_.y)} · EPSG:${_.epsg}</b>
          <ul class="dienste">${_.dienste.map(F=>`<li class="${F.art}">${Ne(F.text)}</li>`).join("")}</ul>
          <span class="leise">Gebiete der Dienste als Rechteck: nahe einer Landesgrenze ohne Gewähr.</span>`}catch(_){if(b!==S)return;i.innerHTML=`<span class="warnung">${Ne(_.message)}</span>`}});const A=D=>{const b=r.getCenter();Z=D?{laenge:D.laenge,breite:D.breite,zoom:Math.max(r.getZoom(),14)}:{laenge:b.lng,breite:b.lat,zoom:r.getZoom()},r.remove(),n.close(),n.remove(),t(D)};n.querySelector(".schliessen").addEventListener("click",()=>A(null)),n.querySelector(".abbrechen").addEventListener("click",()=>A(null)),l.addEventListener("click",()=>A(z)),n.addEventListener("cancel",D=>{D.preventDefault(),A(null)}),requestAnimationFrame(()=>r.invalidateSize())})}let N=[],ze=!0,te=!1;const x={x:"",y:"",epsg:25832,name:""};let W=null;const $n=[[25832,"ETRS89 / UTM 32N"],[25833,"ETRS89 / UTM 33N"],[4647,"ETRS89 / UTM 32N (zE-N)"],[5650,"ETRS89 / UTM 33N (zE-N)"]];async function Ye(e){for(;;){const t=await v(()=>$.auftrag(e));if(!t)return;if(s.auftrag=t,g(),t.fertig){s.auftrag=null;for(const n of t.fehler)G(n,"fehler",1e4);t.projekt?(N=[],await V(t.projekt,"bohrungen")):g();return}await new Promise(n=>setTimeout(n,600))}}const Xe=()=>s.z?.standort?s.sig:"";async function kn(){if(!N.length)return;const e=await v(()=>$.gutachten(N,ze&&!!s.info?.ocr,Xe()));e&&await Ye(e.id)}async function wn(){const e=Number(x.x.replace(",",".")),t=Number(x.y.replace(",","."));if(!Number.isFinite(e)||!Number.isFinite(t)||!x.x||!x.y){G("Rechtswert und Hochwert als Zahlen eingeben.","warn");return}const n=await v(()=>$.standort(e,t,x.epsg,x.name),"Standort wird angelegt …");n&&(await V(n.projekt,n.vorhanden?void 0:"lage"),n.vorhanden&&G(`Den Standort gibt es schon: „${s.z?.name}“ geöffnet.`))}async function vn(){let e=null;try{e=await fn()}catch(t){G(`Karte: ${t.message}`,"fehler",8e3)}e&&(x.x=String(e.x),x.y=String(e.y),x.epsg=e.epsg,W=e.dienste,g())}function zn(){const e=(t,n,i)=>a`
    <label class="feld"><span>${n}</span><input type="text" inputmode=${t==="name"?"text":"decimal"}
      aria-label=${n} placeholder=${i} .value=${x[t]} @input=${l=>{x[t]=l.target.value,t!=="name"&&W&&(W=null,g())}}></label>`;return a`
    <section class="karte">
      <h3>Standort ohne Gutachten ${h("standort")}</h3>
      <p class="leise klein">Ein Punkt statt eines PDFs: Bohrungen der Länder, DGM und Gebäude um den Standort. Das Modell
        ist eine <b>Vorerkundung</b> – kein Ersatz für das Gutachten.</p>
      <div class="zeile"><button @click=${vn}>🗺 Auf der Karte wählen</button>${h("karte")}
        <span class="leise klein">oder Rechts- und Hochwert eintragen</span></div>
      <div class="raster-2">
        ${e("x","Rechtswert","z. B. 368130")}
        ${e("y","Hochwert","z. B. 5724400")}
        <label class="feld"><span>System</span>
          <select aria-label="System des Standorts" @change=${t=>{x.epsg=Number(t.target.value),W=null,g()}}>
            ${$n.map(([t,n])=>a`<option value=${t} ?selected=${x.epsg===t}>${t} · ${n}</option>`)}
          </select></label>
        ${e("name","Name (frei)","z. B. Marl Nord")}
      </div>
      ${W?a`<ul class="dienste klein" aria-label="Dienste am Standort">
        ${W.map(t=>a`<li class=${t.art}>${t.text}</li>`)}</ul>`:u}
      <button class="primaer" @click=${wn}>Projekt am Standort anlegen →</button>
    </section>`}async function Ke(e){const t=await v(()=>$.beispiel(e),"Beispiel wird geöffnet …");t?.projekt?await V(t.projekt,t.schritt??"bohrungen"):t?.auftrag&&await Ye(t.auftrag)}function Te(e){N=[...e??[]].filter(t=>/\.(pdf|json|xml)$/i.test(t.name)),e?.length&&!N.length&&G("Bitte PDF-Dateien wählen (oder eine Extraktion als JSON, Bohrungen als BoreholeML).","warn"),g()}async function Sn(e,t){confirm(`Projekt „${t}“ mit allen Korrekturen löschen? Das Gutachten selbst bleibt unberührt.`)&&(await v(()=>$.loeschen(e)),await Qe())}function Bn(){const e=s.auftrag,t=!!s.info?.ocr;return a`
    <div class="seite-mitte">
      <section class="karte gross">
        <h2>Bodengutachten auswerten</h2>
        <p class="leise">Bohrprofile, Schichtenverzeichnisse oder ganze Gutachten als PDF – Vektor oder Scan. Die Bohrungen
          werden erkannt; im nächsten Schritt prüfen und korrigieren Sie sie.</p>
        ${Xe()?a`<p class="hinweis-standort">Zum Standort <b>${s.z.name}</b>: Bohrungen der Länder (mit Prüfstand),
          DGM und Gebäude kommen in das neue Projekt mit – es ist dann <b>gemischt</b>, beide Quellen bleiben getrennt.</p>`:u}
        ${e?a`
          <div class="fortschritt-karte" aria-live="polite">
            <div class="kreisel klein"></div>
            <div>
              <strong>${e.stand.datei||e.dateien[0]}</strong>
              <span class="leise">Datei ${e.stand.nr}/${e.stand.dateien||e.dateien.length}
                ${e.stand.seiten?a` · Seite ${e.stand.seite}/${e.stand.seiten}${e.stand.klasse?` · ${e.stand.klasse}`:""}`:" · wird geöffnet …"}</span>
              <progress max=${e.stand.seiten||1} value=${e.stand.seite}></progress>
            </div>
          </div>`:a`
          <label class=${`ablage ${te?"ueber":""}`}
            @dragover=${n=>{n.preventDefault(),te=!0,g()}}
            @dragleave=${()=>{te=!1,g()}}
            @drop=${n=>{n.preventDefault(),te=!1,Te(n.dataTransfer?.files)}}>
            <input type="file" accept=".pdf,application/pdf,.json,application/json,.xml,application/xml,text/xml" multiple @change=${n=>Te(n.target.files)}>
            <span class="ablage-icon">⇪</span>
            <strong>${N.length?N.map(n=>n.name).join(", "):"PDF hierher ziehen oder klicken"}</strong>
            <span class="leise">${N.length?`${N.length} Datei(en) bereit`:"mehrere Dateien möglich (z. B. Anlagen 2–4) · auch eine Extraktion als JSON oder Bohrungen als BoreholeML (XML)"}</span>
          </label>
          <div class="zeile">
            <label class="schalter" title=${t?"":"nicht installiert: pip install -r requirements-ocr.txt"}>
              <input type="checkbox" .checked=${ze&&t} ?disabled=${!t} @change=${n=>{ze=n.target.checked}}>
              OCR für Scans ${t?"":"(nicht installiert)"}
            </label>${h("ocr")}
            <span class="fueller"></span>
            <button class="primaer" ?disabled=${!N.length} @click=${kn}>Auswerten →</button>
          </div>`}
      </section>

      ${zn()}

      <div class="zwei-spalten">
        <section class="karte">
          <h3>Beispiele ${h("beispiele")}</h3>
          <ul class="auswahl-liste">
            ${(s.info?.beispiele??[]).filter(n=>!n.standort).map(n=>a`
              <li><button class="link" ?disabled=${!!e} @click=${()=>Ke(n.name)}>${n.titel}</button></li>`)}
          </ul>
          <h4 class="klein">Standort ohne Gutachten <span class="leise">(Bohrungen der Länder: Abfrage im Schritt Lage, mit Netz)</span></h4>
          <ul class="auswahl-liste">
            ${(s.info?.beispiele??[]).filter(n=>n.standort).map(n=>a`
              <li><button class="link" ?disabled=${!!e} @click=${()=>Ke(n.name)}>${n.titel}</button></li>`)}
          </ul>
        </section>
        <section class="karte">
          <h3>Zuletzt bearbeitet</h3>
          ${s.projekte.length?a`
            <table class="tabelle kompakt">
              <thead><tr><th>Projekt</th><th>Bohrungen</th><th>geprüft</th><th>geändert</th><th></th></tr></thead>
              <tbody>
                ${s.projekte.map(n=>a`
                  <tr>
                    <td><button class="link" @click=${()=>V(n.signatur)}>${n.name}</button>${n.standort?a` <span class="abzeichen vorerkundung" title="Standort ohne Gutachten">Standort</span>`:u}
                      <div class="leise klein">${n.dokumente.join(", ")}</div></td>
                    <td class="zahl" title=${n.fremd?`davon ${n.fremd} aus den Datenbanken der Länder`:""}>${n.bohrungen}</td>
                    <td class="zahl">${n.geprueft}${n.eincheckungen?a` · <span title="eingecheckt">✓${n.eincheckungen}</span>`:u}</td>
                    <td class="leise klein">${n.geaendert}</td>
                    <td><button class="symbol" title="Projekt löschen" aria-label="Projekt löschen" @click=${()=>Sn(n.signatur,n.name)}>🗑</button></td>
                  </tr>`)}
              </tbody>
            </table>`:a`<p class="leise">Noch keine Projekte. Ein Projekt entsteht beim ersten Auswerten und wird automatisch gesichert.</p>`}
        </section>
      </div>
      ${s.info?a`<p class="leise klein impressum">GroundTwin ${s.info.version} · freie Software unter
        <a href=${`${s.info.quellcode}/blob/main/LICENSE`} target="_blank" rel="noopener">${s.info.lizenz}</a> ·
        <a href=${s.info.quellcode} target="_blank" rel="noopener">Quellcode</a> · die App extrahiert und schlägt vor;
        die Interpretation und Freigabe bleibt beim Geotechniker.</p>`:u}
    </div>`}const ie="Deutschland · ETRS89 / UTM (amtlich)",H="Deutschland · Gauß-Krüger (alt)",se=[{code:25832,name:"ETRS89 / UTM Zone 32N",gruppe:ie,e:[22e4,101e4],n:[503e4,614e4],hinweis:"Rechtswert 6-stellig, die meisten Länder"},{code:25833,name:"ETRS89 / UTM Zone 33N",gruppe:ie,e:[15e4,7e5],n:[509e4,613e4],hinweis:"Rechtswert 6-stellig, Osten (Berlin, Brandenburg, Sachsen, MV)"},{code:4647,name:"ETRS89 / UTM 32N mit Zone (32…)",gruppe:ie,e:[3223e4,33e6],n:[52e5,614e4],hinweis:"Rechtswert 8-stellig, beginnt mit 32"},{code:5650,name:"ETRS89 / UTM 33N mit Zone (33…)",gruppe:ie,e:[3315e4,3354e4],n:[52e5,613e4],hinweis:"Rechtswert 8-stellig, beginnt mit 33"},{code:31466,name:"DHDN / Gauß-Krüger Zone 2",gruppe:H,e:[23e5,27e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 2"},{code:31467,name:"DHDN / Gauß-Krüger Zone 3",gruppe:H,e:[33e5,37e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 3"},{code:31468,name:"DHDN / Gauß-Krüger Zone 4",gruppe:H,e:[43e5,47e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 4"},{code:31469,name:"DHDN / Gauß-Krüger Zone 5",gruppe:H,e:[531e4,57e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 5"},{code:2398,name:"Krassowski (42/83) / Gauß-Krüger Zone 4",gruppe:H,e:[43e5,47e5],n:[52e5,613e4],hinweis:"neue Länder vor ETRS89, Rechtswert beginnt mit 4"},{code:2399,name:"Krassowski (42/83) / Gauß-Krüger Zone 5",gruppe:H,e:[53e5,57e5],n:[52e5,613e4],hinweis:"neue Länder vor ETRS89, Rechtswert beginnt mit 5"},{code:3068,name:"DHDN / Soldner Berlin",gruppe:"Deutschland · andere",e:[-4e4,9e4],n:[-4e4,8e4],hinweis:"Berlin, alte Katasterkoordinaten (5-stellig)"},{code:2056,name:"CH1903+ / LV95",gruppe:"Schweiz",e:[245e4,287e4],n:[103e4,134e4],hinweis:"E 2 xxx xxx, N 1 xxx xxx"},{code:21781,name:"CH1903 / LV03",gruppe:"Schweiz",e:[45e4,87e4],n:[3e4,34e4],hinweis:"Y 6-stellig, X 5–6-stellig (alt)"},{code:31254,name:"MGI / Austria GK West",gruppe:"Österreich",e:[-11e4,17e4],n:[11e4,34e4],hinweis:"Rechtswert um 0 (±), Hochwert ohne 5 000 000"},{code:31255,name:"MGI / Austria GK Central",gruppe:"Österreich",e:[-16e4,17e4],n:[9e4,46e4],hinweis:"Rechtswert um 0 (±), Hochwert ohne 5 000 000"},{code:31256,name:"MGI / Austria GK East",gruppe:"Österreich",e:[-16e4,1e5],n:[1e5,48e4],hinweis:"Rechtswert um 0 (±), Hochwert ohne 5 000 000"},{code:31257,name:"MGI / Austria GK M28 (BMN)",gruppe:"Österreich",e:[4e4,32e4],n:[11e4,34e4],hinweis:"Bundesmeldenetz West"},{code:31258,name:"MGI / Austria GK M31 (BMN)",gruppe:"Österreich",e:[29e4,62e4],n:[9e4,46e4],hinweis:"Bundesmeldenetz Mitte"},{code:31259,name:"MGI / Austria GK M34 (BMN)",gruppe:"Österreich",e:[59e4,85e4],n:[1e5,48e4],hinweis:"Bundesmeldenetz Ost"},{code:32632,name:"WGS 84 / UTM Zone 32N",gruppe:"GPS (WGS 84)",e:[22e4,101e4],n:[503e4,614e4],hinweis:"wie ETRS89 / UTM 32N (Abweichung < 1 m)"},{code:32633,name:"WGS 84 / UTM Zone 33N",gruppe:"GPS (WGS 84)",e:[15e4,7e5],n:[509e4,613e4],hinweis:"wie ETRS89 / UTM 33N (Abweichung < 1 m)"}],Gn=new Map(se.map(e=>[e.code,e]));function Me(e){return e?Gn.get(e)??null:null}function Le(e){if(!e)return"ohne System (lokal)";const t=Me(e);return t?`EPSG ${e} · ${t.name}`:`EPSG ${e} (nicht in der Liste)`}const en=(e,t,n)=>t>=e.e[0]&&t<=e.e[1]&&n>=e.n[0]&&n<=e.n[1];function yn(e,t){return e===null||t===null||!Number.isFinite(e)||!Number.isFinite(t)?[]:se.filter(n=>n.gruppe!=="GPS (WGS 84)"&&en(n,e,t))}function nn(e,t,n){if(t===null||n===null||!Number.isFinite(t)||!Number.isFinite(n))return null;const i=yn(t,n),l=i.slice(0,3).map(o=>`${o.code} (${o.name})`).join(", ");if(!e)return i.length?{ok:!1,text:`Kein System gewählt – die Werte passen zu ${l}.`}:null;const r=Me(e);return r?en(r,t,n)?{ok:!0,text:`passt zu EPSG ${e} (${r.hinweis})`}:{ok:!1,text:i.length?`Rechts-/Hochwert passen nicht zu EPSG ${e} (${r.hinweis}), aber zu ${l}.`:"Rechts-/Hochwert passen zu keinem System der Liste – Ziffern prüfen (z. B. fehlende Zonenkennung)."}:{ok:!1,text:`EPSG ${e} ist nicht in der Liste – bitte prüfen.`}}function xe(e,t,n="Koordinatensystem"){const i=[...new Set(se.map(r=>r.gruppe))],l=e!==null&&!Me(e);return a`
    <select class="epsg" aria-label=${n} title=${Le(e)}
      @change=${r=>{const o=r.target.value;t(o===""?null:Number(o))}}>
      <option value="" .selected=${e===null}>– ohne (lokal) –</option>
      ${l?a`<option value=${String(e)} .selected=${!0}>EPSG ${e} – nicht in der Liste ⚠</option>`:u}
      ${i.map(r=>a`
        <optgroup label=${r}>
          ${se.filter(o=>o.gruppe===r).map(o=>a`
            <option value=${String(o.code)} .selected=${o.code===e}>${o.code} · ${o.name}</option>`)}
        </optgroup>`)}
    </select>`}const Y=(e,t=2)=>e.toLocaleString("de-DE",{minimumFractionDigits:t,maximumFractionDigits:t});function tn(e){for(const t of[.5,1,2,5,10,20,50,100])if(e/t<=12)return t;return 200}function Dn(e,t){const n=Math.max(1,...e.map(c=>c.bis)),i=12,l=(t.hoehe-i-14)/n,r=34,o=46,d=tn(n),p=[];for(let c=0;c<=n+1e-9;c+=d)p.push(c);return a`<svg class="saeule" viewBox="0 0 150 ${t.hoehe}" width="150" height=${t.hoehe} role="img" aria-label="Bohrsäule">
    <defs>
      <pattern id="schraffur-warn" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
        <rect width="6" height="6" fill="#e6e6e6"></rect><line x1="0" y1="0" x2="0" y2="6" stroke="#f0a33a" stroke-width="3"></line>
      </pattern>
    </defs>
    ${p.map(c=>j`
      <line x1=${r-5} x2=${r} y1=${i+c*l} y2=${i+c*l} class="achse"></line>
      <text x=${r-7} y=${i+c*l+3} class="achse-text" text-anchor="end">${Y(c,d<1?1:0)}</text>`)}
    <line x1=${r} x2=${r} y1=${i} y2=${i+n*l} class="achse"></line>
    ${e.map(c=>j`
      <g class=${`schicht ${c.k===t.gewaehlt?"gewaehlt":""} ${c.warn?"warn":""}`} @click=${()=>t.waehlen?.(c.k)}>
        <title>${c.titel}</title>
        <rect x=${r+4} y=${i+c.von*l} width=${o} height=${Math.max(1,(c.bis-c.von)*l)}
          fill=${c.warn?"url(#schraffur-warn)":c.farbe}></rect>
        ${c.geprueft?j`<text x=${r+o+9} y=${i+(c.von+c.bis)/2*l+4} class="haken">✓</text>`:u}
        ${(c.bis-c.von)*l>11?j`<text x=${r+o+22} y=${i+c.bis*l-2} class="tiefe">${Y(c.bis)}</text>`:u}
      </g>`)}
  </svg>`}function Mn(e,t){const n=[...e.bohrungen].sort((b,_)=>b.x-_.x||b.y-_.y);if(!n.length)return u;const i=new Map(e.einheiten.map(b=>[b.name,b.farbe])),l=Math.max(...n.map(b=>b.gok)),r=Math.min(...n.map(b=>b.endteufe_nhn)),o=22,d=44,p=Math.max(38,Math.min(70,900/n.length)),c=d+n.length*p+10,z=(t.hoehe-o-10)/Math.max(1,l-r),S=b=>o+(l-b)*z,A=tn(l-r),D=[];for(let b=Math.ceil(r/A)*A;b<=l+1e-9;b+=A)D.push(b);return a`<svg class="einheitenprofil" viewBox="0 0 ${c} ${t.hoehe}" width=${c} height=${t.hoehe} role="img"
      aria-label="Einheiten je Bohrung">
    ${D.map(b=>j`
      <line x1=${d-4} x2=${c} y1=${S(b)} y2=${S(b)} class="raster"></line>
      <text x=${d-6} y=${S(b)+3} class="achse-text" text-anchor="end">${Y(b,A<1?1:0)}</text>`)}
    ${n.map((b,_)=>{const F=d+_*p+p*.2,me=p*.6;return j`
        <text x=${F+me/2} y=${o-8} class="code" text-anchor="middle">${b.code}</text>
        ${b.einheiten.filter(M=>M.status==="vorhanden"&&M.ok_modell-M.uk_modell>.001).map(M=>j`
          <rect x=${F} y=${S(M.ok_modell)} width=${me} height=${Math.max(.8,(M.ok_modell-M.uk_modell)*z)}
            fill=${i.get(M.einheit)??"#ccc"} class=${`einheit ${t.gewaehlt===M.einheit?"gewaehlt":""}`}
            @click=${()=>t.waehlen?.(M.einheit)}>
            <title>${b.code}: ${M.einheit} ${Y(M.ok_modell)} bis ${Y(M.uk_modell)} m NHN</title>
          </rect>`)}
        <line x1=${F-3} x2=${F+me+3} y1=${S(b.endteufe_nhn)} y2=${S(b.endteufe_nhn)} class="endteufe"></line>`})}
  </svg>`}const le=(e,t=2)=>e==null?"":e.toLocaleString("de-DE",{minimumFractionDigits:t,maximumFractionDigits:t}),Se=e=>{const t=e.target.value.trim().replace(",",".");return t===""?null:Number(t)},Ln=[["boden","Böden"],["organisch","Organisch"],["geologisch","Geologische Benennung"],["fels","Fels"],["anthropogen","Anthropogen"],["unbekannt","Nicht klassifiziert"]];let oe=null,be="",K=.5,Re=!1;function ce(e){const t=ne(),n=t.findIndex(l=>l.id===s.bid),i=t[Math.min(t.length-1,Math.max(0,n+e))];i&&ge(i.id)}function an(){const e=ne(),t=De(e.findIndex(n=>n.id===s.bid));t&&ge(t)}async function rn(){const e=s.bid;if(!await m([{op:"bohrung_pruefen",id:e,wert:!0}],{leise:!0}))return;const t=De(ne().findIndex(n=>n.id===e));t&&t!==e&&await ge(t)}async function Oe(e){const t=s.z.pruefstand,n=e?`Alle Schichten aller ${t.bohrungen[1]} Bohrungen als geprüft markieren?`:"Die Prüfung aller Bohrungen zurücknehmen?";confirm(n)&&await m([{op:"alle_pruefen",wert:e}])}window.addEventListener("keydown",e=>{if(s.schritt!=="bohrungen"||e.ctrlKey||e.metaKey||e.altKey||e.target?.closest?.("input, select, textarea, [contenteditable]"))return;const n=e.key.toLowerCase();if(e.key==="ArrowDown"||n==="j")ce(1);else if(e.key==="ArrowUp"||n==="k")ce(-1);else if(n==="n")an();else if(n==="g")rn();else return;e.preventDefault()});async function xn(e,t){const n=Number(e.id.split(":")[0]),i=(t[0]?.quelle.seite??e.seite)-1,l=`${s.sig}/${n}/${i}`;if(oe?.schluessel===l||be===l||!s.z?.dokumente[n]?.pdf)return;be=l;const r=await v(()=>$.seite(s.sig,n,i));be="",r&&(oe={schluessel:l,daten:r},g())}function _n(e){return e.entfernt?a`<span class="zeichen raus" title="nicht im Modell">–</span>`:e.offen>0?a`<span class="zeichen warn" title=${`${e.offen} Schicht(en) nicht klassifiziert`}>⚠</span>`:e.schichten_n&&e.schichten_geprueft===e.schichten_n?a`<span class="zeichen ok" title="alle Schichten geprüft">✓</span>`:a`<span class="zeichen" title="noch zu prüfen">○</span>`}function Pn(){const e=s.z.bohrungen,t=ne(),n=e.filter(i=>i.entfernt);return a`
    <aside class="bohrliste-app">
      <input class="suche" type="search" placeholder="Bohrung suchen …" .value=${s.filter}
        @input=${i=>{s.filter=i.target.value,g()}}>
      <ul class="bliste" role="listbox" aria-label="Bohrungen">
        ${t.map(i=>a`
          <li role="option" aria-selected=${String(i.id===s.bid)} class=${i.id===s.bid?"aktiv":""}
            @click=${()=>ge(i.id)}>
            ${_n(i)}
            <span class="name">${i.code}</span>
            <span class="wert">${i.schichten_geprueft}/${i.schichten_n}</span>
            <button class="symbol leise-knopf" title="Aus dem Modell entfernen" aria-label=${`${i.code} entfernen`}
              @click=${l=>{l.stopPropagation(),m([{op:"entfernen",id:i.id}])}}>🗑</button>
          </li>`)}
      </ul>
      ${n.length?a`
        <details class="entfernt" ?open=${Re} @toggle=${i=>{Re=i.target.open}}>
          <summary>Entfernt / nicht im Modell (${n.length}) ${h("entfernen")}</summary>
          <ul class="bliste">
            ${n.map(i=>a`
              <li class="raus">
                <span class="name">${i.code}</span>
                <span class="wert klein">${i.doppelt_in?"doppelt":i.schichten_n?"":"ohne Schichten"}</span>
                <button class="link klein" ?disabled=${!i.schichten_n} @click=${()=>m([{op:"wiederherstellen",id:i.id}])}>wiederherstellen</button>
              </li>`)}
          </ul>
        </details>`:u}
      <p class="leise klein tasten">↑/↓ blättern · N nächste offene · G alle Schichten geprüft und weiter</p>
    </aside>`}function En(){const e=s.z.pruefstand,[t,n]=e.bohrungen,[i,l]=e.schichten;return a`
    <div class="pruefleiste">
      <div class="balken"><span>Bohrungen geprüft <b>${t}/${n}</b></span><progress max=${n||1} value=${t}></progress></div>
      <div class="balken"><span>Schichten geprüft <b>${i}/${l}</b></span><progress max=${l||1} value=${i}></progress></div>
      <span class=${`plakette ${e.unklassifiziert_offen?"warn":"ok"}`}>
        ${e.unklassifiziert_offen?`⚠ ${e.unklassifiziert_offen} Schicht(en) nicht klassifiziert`:"✓ keine offenen Warnungen"}</span>
      ${h("warnung")}
      <span class="fueller"></span>
      ${h("pruefstand")}
      <button @click=${()=>Oe(!0)} ?disabled=${t===n&&i===l}>✓ Alle Bohrungen geprüft</button>
      <button class="leise-knopf" @click=${()=>Oe(!1)} ?disabled=${!i}>Zurücknehmen</button>
      ${h("alle_pruefen")}
    </div>`}function I(e,t,n){return a`<label class="feld"><span>${e}${n?h(n):u}</span>${t}</label>`}function Nn(e){const t=nn(e.epsg,e.x,e.y);return t&&!t.ok?a`<p class="hinweise warn">⚠ ${t.text}</p>`:u}function An(e){const t=ne(),n=t.findIndex(l=>l.id===e.id),i=l=>r=>m([{op:"bohrung",id:e.id,feld:l,wert:Se(r)}]);return a`
    <div class="detail-kopf">
      <div class="titelzeile">
        <h2>${e.code}</h2>
        <span class="leise">${e.dokument} · Seite ${e.seite}${e.doppelt_in?` · doppelt (auch in ${e.doppelt_in})`:""}</span>
        <span class="fueller"></span>
        <button title="Vorherige Bohrung (↑)" ?disabled=${n<=0} @click=${()=>ce(-1)}>↑ Vorherige</button>
        <button title="Nächste Bohrung (↓)" ?disabled=${n>=t.length-1} @click=${()=>ce(1)}>↓ Nächste</button>
        <button title="Nächste Bohrung mit offenen Schichten (N)" ?disabled=${!De(n)} @click=${an}>⚠ Nächste offene</button>
      </div>
      <div class="felder">
        ${I("GOK [m NHN]",a`<input type="number" step="0.01" .value=${k(e.gok===null?"":String(e.gok))}
            placeholder="unbekannt" @change=${i("gok")}>
            <small class=${e.gok_quelle==="manuell"||e.gok_quelle==="DGM"?"manuell":"leise"}>${e.gok_quelle||"fehlt"}</small>`,"gok")}
        ${I("Endteufe [m]",a`<output>${le(e.endteufe)}</output>`)}
        ${I("Rechtswert",a`<input type="number" step="0.01" .value=${k(e.x===null?"":String(e.x))} @change=${i("x")}>`,"koordinaten")}
        ${I("Hochwert",a`<input type="number" step="0.01" .value=${k(e.y===null?"":String(e.y))} @change=${i("y")}>`)}
        ${I("Koordinatensystem (EPSG)",xe(e.epsg,l=>m([{op:"bohrung",id:e.id,feld:"epsg",wert:l}])),"epsg")}
        ${I("Ø Säule [m]",a`<input type="number" step="0.1" min="0" class="kurz" placeholder=${`auto ${le(s.z.durchmesser??s.z.durchmesser_auto,1)}`}
            .value=${k(e.durchmesser===null?"":String(e.durchmesser))} @change=${i("durchmesser")}>`,"durchmesser")}
        ${I("Grundwasser",a`<output>${e.grundwasser||"–"}</output>`)}
      </div>
      ${Nn(e)}
      ${e.hinweise.length?a`<p class="hinweise">ℹ ${e.hinweise.join(" · ")}</p>`:u}
    </div>`}function Kn(e,t){const n=s.z.klassen,i=n.some(l=>l.klasse===t.bodenart);return a`
    <span class="farbfeld" style=${`background:${t.farbe}`}></span>
    <select aria-label="Bodenart" @change=${l=>m([{op:"schicht",id:e.id,k:t.k,feld:"bodenart",wert:l.target.value}])}>
      ${i?u:a`<option .selected=${!0} value=${t.bodenart}>${t.bodenart}</option>`}
      ${Ln.map(([l,r])=>a`
        <optgroup label=${r}>
          ${n.filter(o=>o.art===l).map(o=>a`
            <option value=${o.klasse} .selected=${o.klasse===t.bodenart}>${o.name}${o.din4023?` (${o.din4023})`:""}</option>`)}
        </optgroup>`)}
    </select>`}function Tn(e,t){return a`
    <table class="tabelle schichten">
      <thead><tr>
        <th title="geprüft">✓ ${h("geprueft")}</th><th>von [m] ${h("tiefe")}</th><th>bis [m]</th>
        <th>Bodenart ${h("bodenart")}</th><th>Beschreibung (PDF)</th><th>nach Norm ${h("norm")}</th>
      </tr></thead>
      <tbody>
        ${t.map(n=>a`
          <tr class=${[n.offen?"warn":"",n.korrigiert?"korrigiert":"",n.k===s.k?"gewaehlt":""].join(" ")}
            @click=${()=>{s.k=n.k,g()}}>
            <td><input type="checkbox" .checked=${k(n.geprueft)} aria-label="geprüft"
              @change=${i=>m([{op:"schicht",id:e.id,k:n.k,feld:"geprueft",wert:i.target.checked}],{leise:!0})}></td>
            <td><input type="number" step="0.01" min="0" class="tief" .value=${k(String(n.von))}
              @change=${i=>m([{op:"schicht",id:e.id,k:n.k,feld:"oben",wert:Se(i)}])}></td>
            <td><input type="number" step="0.01" min="0" class="tief" .value=${k(String(n.bis))}
              @change=${i=>m([{op:"schicht",id:e.id,k:n.k,feld:"unten",wert:Se(i)}])}></td>
            <td class="bodenart">${Kn(e,n)}
              ${n.offen?a`<div class="warnung">⚠ nicht klassifiziert</div>`:u}
              ${n.korrigiert?a`<div class="leise klein">korrigiert</div>`:u}</td>
            <td class="beschreibung">${n.beschreibung||a`<span class="leise">– keine Beschreibung –</span>`}
              ${n.hinweise.length?a`<div class="leise klein">${n.hinweise.join(" · ")}</div>`:u}</td>
            <td class="norm">
              ${n.norm.benennung?a`<div>${n.norm.benennung}</div>`:u}
              ${n.norm.din4023?a`<code title="Kurzzeichen nach DIN 4023">${n.norm.din4023}</code>`:u}
              ${n.norm.bodengruppe?a` <code title="Bodengruppe nach DIN 18196">${n.norm.bodengruppe}</code>`:u}
              ${[n.norm.konsistenz,n.norm.lagerung,n.norm.kalk,n.norm.bodenfarbe].filter(Boolean).length?a`<div class="leise klein">${[n.norm.konsistenz,n.norm.lagerung,n.norm.kalk,n.norm.bodenfarbe].filter(Boolean).join(" · ")}</div>`:u}
              ${n.norm.hinweise.length?a`<div class="klein hinweis-norm" title=${n.norm.hinweise.join(`
`)}>ℹ ${n.norm.hinweise[0]}${n.norm.hinweise.length>1?` (+${n.norm.hinweise.length-1})`:""}</div>`:u}
              ${n.vorschlag?a`
                <button class="vorschlag" @click=${i=>{i.stopPropagation(),m([{op:"vorschlag",id:e.id,k:n.k}])}}
                  title=${`Vorschlag nach Norm: ${n.vorschlag.benennung}${n.vorschlag.sicher?"":" (unsicher)"}`}>
                  → ${n.vorschlag.klasse} übernehmen</button>${h("vorschlag")}`:u}
            </td>
          </tr>`)}
      </tbody>
    </table>`}function Rn(e,t){xn(e,t);const n=Number(e.id.split(":")[0]),i=!!s.z.dokumente[n]?.pdf,l=oe?.schluessel===`${s.sig}/${n}/${(t[0]?.quelle.seite??e.seite)-1}`?oe.daten:null,r=t.find(c=>c.k===s.k)??null,o=(c,z)=>{if(!c||!l)return u;const S=l.px_je_pt*K;return a`<div class=${`bbox ${z}`} style=${`left:${c[0]*S}px;top:${c[1]*S}px;width:${(c[2]-c[0])*S}px;height:${(c[3]-c[1])*S}px`}></div>`},d=t.map(c=>c.quelle.bbox).filter(c=>!!c&&c.length===4),p=d.length?[Math.min(...d.map(c=>c[0])),Math.min(...d.map(c=>c[1])),Math.max(...d.map(c=>c[2])),Math.max(...d.map(c=>c[3]))]:null;return a`
    <aside class="quelle-spalte">
      <div class="saeule-rahmen">
        ${Dn(t.map(c=>({k:c.k,von:c.von,bis:c.bis,farbe:c.farbe,warn:c.offen,geprueft:c.geprueft,titel:`${le(c.von)}–${le(c.bis)} m: ${c.bodenart}${c.beschreibung?` – ${c.beschreibung}`:""}`})),{hoehe:420,gewaehlt:s.k,waehlen:c=>{s.k=c,g()}})}
      </div>
      ${i?a`<div class="pdf-rahmen">
        <div class="pdf-kopf"><b>Quelle im PDF</b> ${h("quelle")}
          <span class="fueller"></span>
          ${i?a`<button class="symbol" title="kleiner" @click=${()=>{K=Math.max(.25,K/1.4),g()}}>−</button>
            <button class="symbol" title="größer" @click=${()=>{K=Math.min(1.5,K*1.4),g()}}>+</button>`:u}
        </div>
        ${l?a`
          ${On(p,l.px_je_pt*K)}
          <div class="pdf-seite">
            <div class="pdf-flaeche" style=${`width:${l.breite_pt*l.px_je_pt*K}px;height:${l.hoehe_pt*l.px_je_pt*K}px`}>
              <img src=${l.url} alt=${`Seite ${l.seite+1}`} draggable="false">
              ${o(p,"saeule-bbox")}
              ${o(r?.quelle.bbox,"schicht-bbox")}
            </div>
          </div>`:a`<p class="leise klein">Seite wird geladen …</p>`}
      </div>`:u}
    </aside>`}let Fe="";function On(e,t){const n=`${s.bid}/${K}`;return!e||Fe===n?u:(requestAnimationFrame(()=>{const i=document.querySelector(".pdf-seite");i&&(i.scrollLeft=Math.max(0,e[0]*t-i.clientWidth/3),i.scrollTop=Math.max(0,e[1]*t-40),Fe=n)}),u)}function Fn(){const e=s.z,t=s.details.get(s.bid),n=e.bohrungen.find(r=>r.id===s.bid),i=n?Number(n.id.split(":")[0]):0,l=!e.dokumente[i]?.pdf;return a`
    <div class=${`schritt-bohrungen ${l?"ohne-pdf":""}`}>
      ${En()}
      ${Pn()}
      <section class="bohrung-detail">
        ${n?a`
          ${An(n)}
          ${t?a`
            ${Tn(n,t.schichten)}
            <div class="detail-fuss">
              <button class="primaer" title="Alle Schichten dieser Bohrung als geprüft markieren und zur nächsten offenen (G)"
                @click=${rn}>✓ Alle Schichten geprüft – weiter</button>
              <button class="leise-knopf" ?disabled=${!n.schichten_geprueft}
                @click=${()=>m([{op:"bohrung_pruefen",id:n.id,wert:!1}])}>Prüfung zurücknehmen</button>
              <span class="fueller"></span>
              <button class="gefahr" @click=${()=>m([{op:"entfernen",id:n.id}])}>🗑 Aus dem Modell entfernen</button>
            </div>`:a`<p class="leise">Schichten werden geladen …</p>`}`:a`<p class="leise">Links eine Bohrung wählen.</p>`}
      </section>
      ${n&&t?Rn(n,t.schichten):a`<aside class="quelle-spalte"></aside>`}
    </div>`}const w=(e,t=2)=>e==null||!Number.isFinite(e)?"":e.toLocaleString("de-DE",{minimumFractionDigits:t,maximumFractionDigits:t}),y=e=>{const t=e.target.value.trim().replace(",",".");return t===""?null:Number(t)};let f=null,ue="",J="plan",X,Be=250,Ge=100,ye=100;const R=new Set;function Ie(e){const t=e.unterlage;return t?`${t.sha}/${t.seite}/${t.art}/${JSON.stringify(t.kalibrierung)}`:""}function sn(e){const t=e.unterlage;if(!t)return f=null;if(f&&f.schluessel===Ie(e))return f;const n=t.kalibrierung,i=o=>o&&!("n"in o)?o:null,l=i(n?.massstab),r=i(n?.hoehe);return f={schluessel:Ie(e),massArt:n?.massstab&&"n"in n.massstab?"n":"strecke",p1:l?{u:l.u1,v:l.v1}:null,p2:l?{u:l.u2,v:l.v2}:null,meter:l?.meter??null,n:n?.massstab&&"n"in n.massstab?n.massstab.n:null,hoeheArt:n?.hoehe?"n"in n.hoehe?"n":"strecke":"gleich",h1:r?{u:r.u1,v:r.v1}:null,h2:r?{u:r.u2,v:r.v2}:null,hoeheMeter:r?.meter??null,hoeheN:n?.hoehe&&"n"in n.hoehe?n.hoehe.n:null,bezug:n?.bezug?{u:n.bezug.u,v:n.bezug.v}:null,x:n?.bezug?.x??null,y:n?.bezug?.y??null,drehung:n?.drehung??0,epsg:n?.epsg??e.viewer.epsg??null},f}function _e(e,t=!1){const n=f,i=e.unterlage;if(!n||!i)return null;let l=null;if(n.massArt==="n"&&n.n&&n.n>0&&(l={n:n.n}),n.massArt==="strecke"&&n.p1&&n.p2&&n.meter&&n.meter>0&&(l={u1:n.p1.u,v1:n.p1.v,u2:n.p2.u,v2:n.p2.v,meter:n.meter}),!l||!n.bezug||n.x===null||n.y===null)return null;let r=null;return i.art==="schnitt"&&n.hoeheArt==="n"&&n.hoeheN&&n.hoeheN>0&&(r={n:n.hoeheN}),i.art==="schnitt"&&n.hoeheArt==="strecke"&&n.h1&&n.h2&&n.hoeheMeter&&n.hoeheMeter>0&&(r={u1:n.h1.u,v1:n.h1.v,u2:n.h2.u,v2:n.h2.v,meter:n.hoeheMeter}),{massstab:l,hoehe:r,bezug:{...n.bezug,x:n.x,y:n.y},drehung:i.art==="plan"?n.drehung:0,epsg:i.art==="plan"?n.epsg:null,gesperrt:t}}function B(){const e=s.z;s.entwurf=_e(e);const t=s.viewer;t&&f&&(t.editor.hilfsmarken({strecke:f.massArt==="strecke"?[f.p1,f.p2]:[],hoehe:f.hoeheArt==="strecke"?[f.h1,f.h2]:[],bezug:f.bezug}),s.entwurf&&t.editor.vorschau(s.entwurf)),g()}async function In(e){const t=s.viewer;if(!t||!f)return;ue=e,g();const n=await t.editor.bildpunktWaehlen();if(ue="",!n||!f||s.z?.unterlage?.kalibrierung?.gesperrt){g();return}f[e]=n,B()}async function je(e){s.viewer?.editor.waehlenAbbrechen();const t=_e(s.z,e);if(!t){G("Für die Kalibrierung fehlen Maßstab oder Bezugspunkt.","warn");return}await m([{op:"kalibrierung",wert:t}])&&(s.entwurf=null,G(e?"Plan kalibriert und gesperrt – jetzt die Bohrungen ziehen.":"Kalibrierung übernommen.","ok"),await s.viewer?.ansicht(s.z?.unterlage?.art==="schnitt"?"sued":"oben"))}async function jn(e){const t=s.z.unterlage;t?.kalibrierung&&await m([{op:"kalibrierung",wert:{...t.kalibrierung,gesperrt:e}}])}async function Hn(e){const t=e.target,n=t.files?.[0];if(t.value="",!n)return;const i=await v(()=>$.unterlage(s.sig,n,J,0),"Unterlage wird gelesen …");i&&(P(i),s.entwurf=null,g(),await pe(),await s.viewer?.lageModus(!0),await s.viewer?.ansicht(i.unterlage?.art==="schnitt"?"sued":"oben"))}async function He(e,t){const n=await v(()=>$.unterlageSeite(s.sig,e,t),"Seite wird gelesen …");n&&(P(n),s.entwurf=null,g(),await pe(),await s.viewer?.ansicht(t==="schnitt"?"sued":"oben"))}async function Un(){if(!confirm("Unterlage mit ihrer Kalibrierung entfernen? Gesetzte Bohrungen behalten ihre Lage."))return;const e=await v(()=>$.unterlageEntfernen(s.sig));e&&(P(e),s.entwurf=null,g(),await pe())}const E=(e,t,n=!0)=>a`<details class="abschnitt" ?open=${n}><summary>${e}</summary><div class="abschnitt-inhalt">${t}</div></details>`;function q(e,t,n,i){return a`<button class=${`punkt ${ue===t?"aktiv":""} ${n?"gesetzt":""}`} ?disabled=${i}
    @click=${()=>In(t)}>${ue===t?"… im Plan klicken":n?`${e} ✓`:e}</button>`}function Cn(e){const t=nn(e.epsg,e.x,e.y);return t?a`<p class=${`klein ${t.ok?"ok":"warn"}`}>${t.ok?"✓":"⚠"} ${t.text}</p>`:u}function Wn(e){const t=e.unterlage,n=sn(e),i=!!t.kalibrierung?.gesperrt,l=t.art==="plan",r=n.p1&&n.p2?Math.hypot(n.p2.u-n.p1.u,n.p2.v-n.p1.v):null,o=_e(e),d=o?cn(o.massstab,t.mm_pro_px):null,p=e.viewer.bohrungen.filter(c=>c.x!==null&&(l?!/Plan|Viewer/.test(c.quelle):c.gok_bekannt));return a`
    <p class=${`status ${t.kalibrierung?i?"ok":"":"warn"}`}>
      ${t.kalibrierung?a`${i?"🔒 gesperrt · ":""}${Pe(t)}${l?` · ${Le(t.kalibrierung.epsg)}`:""}`:"nicht kalibriert"}
      ${s.entwurf&&JSON.stringify({...s.entwurf,gesperrt:!1})!==JSON.stringify({...t.kalibrierung??{},gesperrt:!1})?a`<br><span class="leise">Vorschau: ${Pe(t,s.entwurf)} (noch nicht übernommen)</span>`:u}
    </p>
    ${i?a`
      <p class="leise klein">Der Plan liegt fest. ${l?"Bohrungen unten mit „Punkte setzen“ in den Plan klicken oder im Viewer ziehen – nur in x/y":"Bohrungen im Viewer ziehen – entlang der Station; die Höhe nur ohne GOK aus dem PDF"}.</p>
      <button @click=${()=>jn(!1)}>🔓 Entsperren (neu kalibrieren)</button>`:a`
      <fieldset class="gruppe">
        <legend>1 · Maßstab ${h("massstab")}</legend>
        <div class="umschalter">
          <label><input type="radio" name="massart" .checked=${n.massArt==="strecke"} @change=${()=>{n.massArt="strecke",B()}}> Strecke messen</label>
          <label><input type="radio" name="massart" .checked=${n.massArt==="n"} @change=${()=>{n.massArt="n",B()}}> 1:n eingeben</label>
        </div>
        ${n.massArt==="strecke"?a`
          <div class="zeile">${q("Punkt 1","p1",n.p1,!1)}${q("Punkt 2","p2",n.p2,!1)}</div>
          <div class="zeile">
            <span class="leise klein">${r?`gemessen ${w(r,0)} px`:"zwei Punkte anklicken"}</span>
            <label class="inline">wahre Länge <input type="number" step="0.01" min="0" class="kurz" .value=${k(n.meter===null?"":String(n.meter))}
              @input=${c=>{n.meter=y(c),B()}}> m</label>
          </div>`:a`
          <label class="inline">Maßstab 1: <input type="number" step="1" min="1" class="kurz" .value=${k(n.n===null?"":String(n.n))}
            @input=${c=>{n.n=y(c),B()}}></label>`}
        ${d?a`<p class="leise klein">ergibt 1:${Math.round(d).toLocaleString("de-DE")}</p>`:u}
      </fieldset>
      ${l?u:a`
        <fieldset class="gruppe">
          <legend>Höhenmaßstab ${h("hoehe")}</legend>
          <div class="umschalter">
            <label><input type="radio" name="hoeheart" .checked=${n.hoeheArt==="gleich"} @change=${()=>{n.hoeheArt="gleich",B()}}> wie Länge</label>
            <label><input type="radio" name="hoeheart" .checked=${n.hoeheArt==="n"} @change=${()=>{n.hoeheArt="n",B()}}> 1:n</label>
            <label><input type="radio" name="hoeheart" .checked=${n.hoeheArt==="strecke"} @change=${()=>{n.hoeheArt="strecke",B()}}> messen</label>
          </div>
          ${n.hoeheArt==="n"?a`<label class="inline">Höhe 1: <input type="number" step="1" min="1" class="kurz"
              .value=${k(n.hoeheN===null?"":String(n.hoeheN))} @input=${c=>{n.hoeheN=y(c),B()}}></label>`:u}
          ${n.hoeheArt==="strecke"?a`
            <div class="zeile">${q("Höhe oben","h1",n.h1,!1)}${q("Höhe unten","h2",n.h2,!1)}</div>
            <label class="inline">Höhenunterschied <input type="number" step="0.01" min="0" class="kurz"
              .value=${k(n.hoeheMeter===null?"":String(n.hoeheMeter))} @input=${c=>{n.hoeheMeter=y(c),B()}}> m</label>`:u}
        </fieldset>`}
      <fieldset class="gruppe">
        <legend>2 · Bezugspunkt ${h("bezug")}</legend>
        <div class="zeile">${q("Punkt im Plan wählen","bezug",n.bezug,!1)}</div>
        <div class="zeile">
          <label class="feld schmal"><span>${l?"Rechtswert":"Station [m]"}</span>
            <input type="number" step="0.01" .value=${k(n.x===null?"":String(n.x))} @input=${c=>{n.x=y(c),B()}}></label>
          <label class="feld schmal"><span>${l?"Hochwert":"Höhe [m NHN]"}</span>
            <input type="number" step="0.01" .value=${k(n.y===null?"":String(n.y))} @input=${c=>{n.y=y(c),B()}}></label>
        </div>
        ${l?a`
          <label class="feld breit"><span>Koordinatensystem (EPSG) ${h("epsg")}</span>
            ${xe(n.epsg,c=>{n.epsg=c,B()})}</label>
          ${Cn(n)}`:u}
        ${p.length?a`
          <label class="inline klein">oder von Bohrung
            <select @change=${c=>{const z=e.viewer.bohrungen.find(S=>S.id===c.target.value);z&&(n.x=z.x,n.y=l?z.y:z.gok,B())}}>
              <option value="">–</option>
              ${p.map(c=>a`<option value=${c.id}>${c.code}</option>`)}
            </select></label>`:u}
      </fieldset>
      ${l?a`
        <fieldset class="gruppe">
          <legend>3 · Drehung ${h("drehung")}</legend>
          <div class="zeile">
            <label class="inline"><input type="number" step="0.1" class="kurz" .value=${k(String(n.drehung))}
              @input=${c=>{n.drehung=y(c)??0,B()}}> ° gegen den Uhrzeigersinn</label>
          </div>
        </fieldset>`:u}
      <div class="zeile knopfzeile">
        <button ?disabled=${!o} @click=${()=>je(!1)}>Übernehmen</button>
        <button class="primaer" ?disabled=${!o} @click=${()=>je(!0)}>🔒 Übernehmen und sperren</button>
        ${h("sperren")}
      </div>
      ${t.kalibrierung?a`<button class="link klein" @click=${()=>m([{op:"kalibrierung",wert:null}])}>Kalibrierung zurücksetzen</button>`:u}`}`}function Vn(e){const t=e.unterlage;return t?a`
    <p><b>${t.name}</b> <span class="leise">· ${t.art==="plan"?"Lageplan":"Längsschnitt"}</span></p>
    <div class="zeile">
      ${(t.seiten??1)>1?a`<label class="inline">Seite <select @change=${n=>He(Number(n.target.value),t.art)}>
          ${Array.from({length:t.seiten},(n,i)=>a`<option value=${i} .selected=${i===t.seite}>${i+1}</option>`)}
        </select></label>`:u}
      <label class="inline">Ansicht <select @change=${n=>He(t.seite,n.target.value)}>
        <option value="plan" .selected=${t.art==="plan"}>Lageplan</option>
        <option value="schnitt" .selected=${t.art==="schnitt"}>Längsschnitt</option>
      </select></label>
    </div>
    <label class="inline">Deckkraft ${h("deckkraft")}
      <input type="range" min="0.1" max="1" step="0.05" .value=${String(s.viewer?.editor.deckkraft??.85)}
        @input=${n=>{s.viewer&&(s.viewer.editor.deckkraft=Number(n.target.value),s.viewer.editor.bildSichtbarkeit())}}></label>
    <button class="link klein" @click=${Un}>Unterlage entfernen</button>`:a`
      <p class="leise klein">Lageplan (von oben) oder Längsschnitt (von der Seite) als PDF – er liegt im Viewer unter den Bohrungen.</p>
      <div class="umschalter">
        <label><input type="radio" name="neueart" .checked=${J==="plan"} @change=${()=>{J="plan"}}> Lageplan</label>
        <label><input type="radio" name="neueart" .checked=${J==="schnitt"} @change=${()=>{J="schnitt"}}> Längsschnitt</label>
      </div>
      <label class="datei-knopf"><input type="file" accept=".pdf,application/pdf" @change=${Hn}>PDF wählen …</label>`}function Zn(e){const t=e.unterlage,n=!t||!!t.kalibrierung?.gesperrt,i=e.viewer.bohrungen.filter(o=>o.x===null),l=e.lage_modus==="reihe",r=!l&&t?.art==="plan"&&!!t.kalibrierung?.gesperrt;return a`
    ${n?u:a`<p class="warnung">Erst kalibrieren und sperren (🔒) – dann Punkte setzen oder Bohrungen ziehen.</p>`}
    ${r?qn(e):u}
    ${i.length?a`
      <p class="klein">Ohne Lage (${i.length}) – ${r?"anklicken = als Nächste setzen, oder":""} in den Viewer ziehen
        ${h("ohne_lage")}</p>
      <div class="parkplatz">
        ${i.map(o=>a`<span class=${`park ${n?"":"gesperrt"} ${s.punktModus&&s.naechste===o.id?"aktiv":""}`}
          title=${r?"Klick: als nächste Bohrung setzen · Ziehen: direkt in den Viewer":"In den Viewer ziehen"}
          @pointerdown=${d=>s.viewer?.editor.ziehenStart(d,o.id,!0)}
          @click=${()=>{r&&de(!0,o.id)}}>${o.code}</span>`)}
      </div>`:a`<p class="leise klein">Alle Bohrungen im Modell haben eine Lage.</p>`}
    ${r?Jn(e):u}
    ${l?Qn(e):u}`}function de(e,t){s.punktModus=e,t!==void 0?s.naechste=t:e&&!s.naechste&&(s.naechste=dn()),s.viewer?.editor.punktModusSetzen(e),g()}function qn(e){const t=e.viewer.bohrungen.filter(i=>i.x===null),n=e.viewer.bohrungen.filter(i=>i.x!==null);return a`
    <div class="zeile">
      <button class=${s.punktModus?"primaer":""} @click=${()=>de(!s.punktModus)}>
        ${s.punktModus?"● Punkte setzen – Klick in den Plan":"＋ Punkte im Plan setzen"}</button>
      ${s.punktModus?a`<button class="leise-knopf" @click=${()=>de(!1)}>Fertig (Esc)</button>`:u}
      ${h("punkte")}
    </div>
    ${s.punktModus?a`
      <label class="feld breit"><span>Nächster Klick setzt</span>
        <select class="naechste" @change=${i=>{s.naechste=i.target.value,g()}}>
          <option value="" .selected=${!s.naechste}>– freien Punkt (später zuordnen) –</option>
          ${t.length?a`<optgroup label="Ohne Lage">
            ${t.map(i=>a`<option value=${i.id} .selected=${s.naechste===i.id}>${i.code}</option>`)}</optgroup>`:u}
          ${n.length?a`<optgroup label="Mit Lage (neu setzen)">
            ${n.map(i=>a`<option value=${i.id} .selected=${s.naechste===i.id}>${i.code}</option>`)}</optgroup>`:u}
        </select></label>
      <p class="leise klein">Danach ist automatisch die nächste Bohrung ohne Lage dran.</p>`:u}`}function Jn(e){const t=e.viewer.bohrungen.filter(r=>r.x!==null&&/Plan|Viewer/.test(r.quelle)),n=e.viewer.bohrungen,i=n.filter(r=>r.x===null);if(!t.length&&!e.punkte.length)return u;const l=(r,o)=>a`<span class="leise klein">R ${w(r)}<br>H ${w(o)}</span>`;return a`
    <p class="klein">Gesetzte Punkte (${t.length+e.punkte.length})</p>
    <table class="tabelle kompakt punkte">
      <tbody>
        ${e.punkte.map(r=>a`
          <tr class=${`frei ${s.viewer?.editor.punktGewaehlt===r.id?"gewaehlt":""}`}>
            <td><button class="link" title="Im Viewer wählen" @click=${()=>{s.viewer?.editor.punktWaehlen(r.id),g()}}>◆ ${r.id}</button></td>
            <td>${l(r.x,r.y)}</td>
            <td><select aria-label=${`${r.id} zuordnen`} @change=${o=>{const d=o.target.value;d&&m([{op:"punkt_zuordnen",punkt:r.id,bohrung:d}])}}>
              <option value="" selected>– Bohrung zuordnen –</option>
              ${i.length?a`<optgroup label="Ohne Lage">${i.map(o=>a`<option value=${o.id}>${o.code}</option>`)}</optgroup>`:u}
              <optgroup label="Mit Lage (ersetzen)">${n.filter(o=>o.x!==null).map(o=>a`<option value=${o.id}>${o.code}</option>`)}</optgroup>
            </select></td>
            <td><button class="symbol" title="Punkt löschen" @click=${()=>m([{op:"punkt_loeschen",punkt:r.id}])}>✕</button></td>
          </tr>`)}
        ${t.map(r=>a`
          <tr class=${s.viewer?.editor.ausgewaehlt===r.id?"gewaehlt":""}>
            <td><button class="link" title="Im Viewer wählen" @click=${()=>{s.viewer?.nadelWaehlen(r.id),g()}}>● ${r.code}</button></td>
            <td>${l(r.x,r.y)}</td>
            <td><select aria-label=${`${r.code} umhängen`} @change=${o=>{const d=o.target.value;d==="-"?m([{op:"lage_loesen",id:r.id}]):d&&d!==r.id&&m([{op:"lage_umhaengen",id:r.id,nach:d}])}}>
              <option value=${r.id} selected>${r.code}</option>
              <option value="-">– Zuordnung lösen (freier Punkt) –</option>
              ${i.length?a`<optgroup label="Andere Bohrung (ohne Lage)">${i.map(o=>a`<option value=${o.id}>${o.code}</option>`)}</optgroup>`:u}
            </select></td>
            <td><button class="symbol" title="Lage entfernen (Bohrung wieder ohne Lage)" @click=${()=>m([{op:"lage_entfernen",id:r.id}])}>✕</button></td>
          </tr>`)}
      </tbody>
    </table>`}function Qn(e){const t=e.reihe.map(i=>i.id),n=(i,l)=>{const r=[...t],[o]=r.splice(i,1);r.splice(Math.max(0,Math.min(r.length,i+l)),0,o),m([{op:"reihe",reihenfolge:r}],{leise:!0})};return a`
    <div class="zeile">
      <label class="inline">Standardabstand ${h("standardabstand")}
        <input type="number" step="1" min="1" class="kurz" .value=${k(String(e.reihe_standard))}
          @change=${i=>m([{op:"reihe",standard:y(i)}])}> m</label>
    </div>
    <table class="tabelle kompakt reihe">
      <thead><tr><th></th><th>Bohrung</th><th>Abstand [m] ${h("reihe")}</th><th>Station [m]</th></tr></thead>
      <tbody>
        ${e.reihe.map((i,l)=>a`
          <tr>
            <td class="pfeile"><button class="symbol" ?disabled=${l===0} title="nach vorn" @click=${()=>n(l,-1)}>▲</button><button class="symbol"
              ?disabled=${l===t.length-1} title="nach hinten" @click=${()=>n(l,1)}>▼</button></td>
            <td>${i.code}</td>
            <td><input type="number" step="0.1" min="0" class="kurz" ?disabled=${l===0} .value=${k(i.abstand===null?"":String(i.abstand))}
              @change=${r=>m([{op:"reihe",abstand:{[i.id]:y(r)}}],{leise:!0})}></td>
            <td><input type="number" step="0.1" class="kurz" .value=${k(String(i.station))} title=${i.quelle_text}
              @change=${r=>m([{op:"reihe",station:{[i.id]:y(r)}}],{leise:!0})}></td>
          </tr>`)}
      </tbody>
    </table>`}async function Yn(e){const t=e.target,n=[...t.files??[]];if(t.value="",!n.length)return;const i=X===void 0?s.z?.viewer.epsg??null:X,l=await v(()=>$.dgm(s.sig,n,i),"DGM wird gelesen …");if(l){P(l),g();const r=l.gelaende?.pruefung?.warnungen.length??0;G(r?"DGM geladen – Hinweise zum Vergleich beachten.":"DGM geladen.",r?"warn":"ok")}}async function Xn(){const e=await v(()=>$.dgmAbruf(s.sig,Ge),"DGM wird beim Land abgerufen …");if(e){P(e),g();const t=e.gelaende?.pruefung?.warnungen.length??0;G(t?"DGM vom Land geladen – Hinweise zum Vergleich beachten.":"DGM vom Land geladen.",t?"warn":"ok")}}function Ue(e){return e.lage_modus!=="koordinaten"?u:a`
    <div class="zeile">
      <label class="inline">Rand <input type="number" min="0" max="1000" step="25" class="kurz" aria-label="Rand um die Bohrungen"
        .value=${k(String(Ge))} @change=${t=>{Ge=y(t)??100}}> m</label>
      <button @click=${Xn} title="Sendet den Ausschnitt um die Bohrungen an den Dienst des Landes">
        DGM vom Land abrufen</button>${h("dgm_land")}
    </div>
    <p class="leise klein">Brandenburg mit Berlin und NRW (DGM1, WCS). Sendet den Ausschnitt um die Bohrungen an den Dienst.</p>`}async function et(){if(!confirm("DGM aus dem Projekt entfernen? Übernommene GOK bleiben (Quelle DGM)."))return;const e=await v(()=>$.dgmEntfernen(s.sig));e&&(P(e),g())}const fe={ok:["✓","ok"],abweichung:["⚠ weicht ab","warn"],ohne_gok:["GOK fehlt",""],aus_dgm:["aus dem DGM","leise"],ausserhalb:["außerhalb","leise"],ohne_lage:["ohne Lage","leise"],anderes_system:["anderes EPSG","warn"]},Ce=e=>e===null?"":Math.abs(e)<.005?w(0):`${e>0?"+":""}${w(e)}`;function nt(e){const t=e.gelaende,n=p=>a`<label class="datei-knopf"><input type="file" multiple aria-label="DGM-Dateien"
    accept=".xyz,.txt,.csv,.asc,.tif,.tiff,.zip,.gz" @change=${Yn}>${p}</label>`,i=X===void 0?e.viewer.epsg??null:X,l=a`<label class="feld breit"><span>System der Datei (XYZ, ASCII) ${h("dgm_epsg")}</span>
    ${xe(i,p=>{X=p,g()},"System der DGM-Datei")}</label>`;if(!t)return a`
      <p class="leise klein">DGM-Kachel(n) des Landes (Open Data, z. B. DGM1) als XYZ, ASCII-Raster oder GeoTIFF, auch als
        ZIP – Höhen in m NHN. Damit prüft die App die GOK, schlägt fehlende vor und legt das Gelände ins Modell.</p>
      ${Ue(e)}
      ${l}
      ${n("DGM-Dateien wählen …")}`;const r=t.info,o=t.pruefung,d=r.quelle;return a`
    <p><b>${r.name}</b><br><span class="leise klein">${Le(r.epsg)} · Raster ${w(r.dx,1)} m ·
      ${r.spalten.toLocaleString("de-DE")} × ${r.zeilen.toLocaleString("de-DE")} · ${w(r.zmin,1)} – ${w(r.zmax,1)} m NHN</span></p>
    ${d?a`<p class="leise klein">${d.anbieter} · <a href=${d.beleg} target="_blank" rel="noopener">${d.lizenz}</a> ·
      ${d.namensnennung} · abgerufen ${d.abgerufen}</p>`:u}
    ${t.fehler?a`<p class="warnung klein">${t.fehler}</p>`:u}
    ${o?a`
      <table class="tabelle kompakt gelaende">
        <thead><tr><th>Bohrung</th><th class="zahl">GOK</th><th class="zahl">DGM</th><th class="zahl">Δ [m]</th><th></th></tr></thead>
        <tbody>
          ${o.zeilen.map(p=>a`
            <tr class=${fe[p.status][1]}>
              <td><button class="link" title="Im Viewer wählen" @click=${()=>{s.viewer?.nadelWaehlen(p.id),g()}}>${p.code}</button></td>
              <td class="zahl">${w(p.gok)}</td>
              <td class="zahl">${w(p.dgm)}</td>
              <td class="zahl">${Ce(p.differenz)}</td>
              <td class=${`klein ${fe[p.status][1]}`}>${p.status==="ohne_gok"?a`<button class="klein" title="GOK aus dem DGM übernehmen (Quelle DGM)"
                    @click=${()=>m([{op:"gok_aus_dgm",ids:[p.id]}])}>übernehmen</button>`:fe[p.status][0]}</td>
            </tr>`)}
        </tbody>
      </table>
      ${o.verglichen?a`<p class="leise klein">${o.verglichen} verglichen · Median ${Ce(o.median)} m ·
        größte Abweichung ${w(o.max)} m (unauffällig bis ${w(o.toleranz,1)} m)</p>`:u}
      ${o.warnungen.map(p=>a`<p class="warnung klein">⚠ ${p}</p>`)}
      ${o.vorschlaege>1?a`<button @click=${()=>m([{op:"gok_aus_dgm"}])}>
        Alle ${o.vorschlaege} fehlenden GOK aus dem DGM übernehmen</button>`:u}`:u}
    ${Ue(e)}
    ${l}
    <div class="zeile">${n("Andere DGM-Dateien …")}
      <button class="link klein" @click=${et}>DGM entfernen</button></div>`}async function tt(){const e=await v(()=>$.sgdAbfrage(s.sig,Be),"Dienste der Länder werden abgefragt …");if(!e?.sgd)return;P(e),R.clear(),g();const t=e.sgd;G(`${t.treffer.length} Bohrungen der Länder im Umkreis von ${w(t.radius,0)} m`+(t.fehler.length?` – ${t.fehler.length} Dienst(e) ohne Antwort`:""),t.fehler.length?"warn":"ok")}async function it(){const e=[...R].map(n=>({dienst:n.slice(0,n.indexOf("/")),id:n.slice(n.indexOf("/")+1)})),t=await v(()=>$.sgdUebernehmen(s.sig,e),"Schichtdaten werden beim Land geholt …");if(t){P(t.zustand),R.clear();for(const n of t.meldungen)G(n,"ok");await pe(),g()}}function at(e){const t=e.treffer.filter(r=>!r.uebernehmbar&&!r.uebernommen&&!r.gutachten);if(!t.length)return u;const n=r=>e.quellen.find(o=>o.dienst===r)?.land??r,i=r=>{const o=t.filter(d=>d.schichten===r);return o.length?`${o.length} (${[...new Set(o.map(d=>n(d.dienst)))].join(", ")})`:""},l=[i("grafik")&&`${i("grafik")} nur mit Kopfdaten: das Land gibt das Schichtenverzeichnis nur als Bild heraus (Profil ↗), nicht als Daten`,i("keine")&&`${i("keine")} ohne Schichtenverzeichnis`,i("ohne Petrographie")&&`${i("ohne Petrographie")} mit Schichten ohne Petrographie`].filter(Boolean);return a`<p class="leise klein sgd-warum">Nicht übernehmbar: ${l.join("; ")}. Ohne Schichten entsteht kein Modell –
    sie zu erfinden wäre falsch. Lage, GOK und Teufe sehen Sie hier; die Schichten im Profil des Landes. Übernehmbar sind
    Bohrungen mit Schichtdaten in BoreholeML (NRW, Baden-Württemberg).</p>`}function rt(e){return e.gutachten?a`<span class="ok" title="Dieselbe Bohrung im Gutachten">= ${e.gutachten}</span>`:e.uebernommen?a`<span class="ok">✓ im Projekt</span>`:e.schichten==="boreholeml"?a`${e.schichten_n} Schichten`:e.schichten==="grafik"&&e.profil?a`<a href=${e.profil} target="_blank" rel="noopener">Profil ↗</a>`:a`<span class="leise">${e.schichten==="ohne Petrographie"?"ohne Petrographie":"keine Schichten"}</span>`}async function st(){const e=await v(()=>$.gebaeudeAbruf(s.sig,ye),"Gebäude werden beim Land abgerufen …");e&&(P(e),g(),G(`${e.gebaeude?.anzahl??0} Gebäude geladen – im Modell als Umgebung.`,"ok"))}async function lt(){const e=await v(()=>$.gebaeudeEntfernen(s.sig));e&&(P(e),g())}function ot(e){if(e.lage_modus!=="koordinaten")return a`<p class="leise klein">Nur mit Lage nach Koordinaten.</p>`;const t=e.gebaeude,n=a`
    <div class="zeile">
      <label class="inline">Rand <input type="number" min="0" max="1000" step="25" class="kurz" aria-label="Rand der Gebäude"
        .value=${k(String(ye))} @change=${l=>{ye=y(l)??100}}> m</label>
      <button @click=${st} title="Lädt die Kacheln (1 × 1 km) um die Bohrungen beim Land">
        ${t?"Gebäude neu abrufen":"Gebäude vom Land abrufen"}</button>${h("gebaeude")}
    </div>`;if(!t)return a`
      <p class="leise klein">3D-Gebäudemodelle LoD2 von Berlin, Brandenburg und NRW (CityGML, m NHN) als Umgebung im Modell und
        im IFC. Lädt die Kacheln von 1 × 1 km um die Bohrungen – das verrät die Lage des Projekts auf etwa 1 km.</p>
      ${n}`;const i=t.quelle;return a`
    <p><b>${t.anzahl.toLocaleString("de-DE")} Gebäude</b> · ${t.flaechen.toLocaleString("de-DE")} Flächen ·
      ${i.kacheln} Kachel${i.kacheln===1?"":"n"} <span class="leise klein">· abgerufen ${i.abgerufen}</span></p>
    ${i.dienste.map(l=>a`<p class="leise klein">${l.anbieter} · <a href=${l.beleg} target="_blank" rel="noopener">${l.lizenz}</a> ·
      ${l.namensnennung}</p>`)}
    ${i.ohne_kachel.length?a`<p class="leise klein">ohne Kachel beim Land: ${i.ohne_kachel.join(", ")}</p>`:u}
    ${i.fehler.map(l=>a`<p class="warnung klein">⚠ ${l}</p>`)}
    ${t.hinweis?a`<p class="warnung klein">⚠ ${t.hinweis}</p>`:u}
    <p class="leise klein">Im Viewer mit dem Knopf „Gebäude“ ein- und ausblendbar.</p>
    ${n}
    <button class="link klein" @click=${lt}>Gebäude entfernen</button>`}function We(e){if(e.lage_modus==="reihe")return a`<p class="leise klein">Nur mit Lage nach Koordinaten.</p>`;const t=e.sgd,n=a`
    <p class="leise klein">Bohrungen aus den Datenbanken der Geologischen Dienste um die Mitte des Projekts.
      <b>Die Abfrage sendet die Lage des Projekts an den Dienst des Landes.</b></p>
    <div class="zeile">
      <label class="inline">Umkreis <input type="number" min="10" max="2000" step="50" class="kurz" aria-label="Umkreis der Abfrage"
        .value=${k(String(Be))} @change=${d=>{Be=y(d)??250}}> m</label>
      <button @click=${tt}>${t?"Neu abfragen":"Abfragen"}</button>
    </div>`;if(!t)return n;const i=t.gegenprobe,l=i.anzahl>0&&(i.lage_max??0)<=1&&(i.gok_max??0)<=.5,r=t.treffer.slice(0,60),o=t.treffer.filter(d=>d.uebernehmbar).length;return a`
    ${n}
    <p class="klein">${t.treffer.length} Bohrungen im Umkreis von ${w(t.radius,0)} m · ${t.zeit}</p>
    ${i.anzahl?a`<p class=${`klein ${l?"ok":"warnung"}`}>${l?"✓":"⚠"} ${i.anzahl} Bohrungen des Gutachtens auch
      beim Land: Lage ≤ ${w(i.lage_max)} m${i.gok_max!==null?a`, GOK ≤ ${w(i.gok_max)} m`:u}${l?"":" – Lage und GOK prüfen"}</p>`:u}
    ${t.fehler.map(d=>a`<p class="warnung klein">${d.dienst}: ${d.fehler}</p>`)}
    ${r.length?a`
      <table class="tabelle kompakt sgd">
        <thead><tr><th></th><th>Bohrung</th><th class="zahl">Abstand</th><th class="zahl">GOK</th><th class="zahl">Teufe</th><th>Schichten</th></tr></thead>
        <tbody>
          ${r.map(d=>{const p=`${d.dienst}/${d.id}`;return a`<tr class=${d.gutachten?"doppelt":""}>
              <td>${d.uebernehmbar?a`<input type="checkbox" aria-label=${`${d.name} übernehmen`} .checked=${R.has(p)}
                @change=${c=>{c.target.checked?R.add(p):R.delete(p),g()}}>`:u}</td>
              <td title=${`${d.dienst} · ID ${d.id}${d.datum?` · ${d.datum}`:""}`}>${d.name}</td>
              <td class="zahl">${w(d.abstand,0)}</td>
              <td class="zahl">${w(d.gok)}</td>
              <td class="zahl">${w(d.teufe,1)}</td>
              <td class="klein">${rt(d)}</td>
            </tr>`})}
        </tbody>
      </table>
      ${t.treffer.length>r.length?a`<p class="leise klein">… und ${t.treffer.length-r.length} weitere (Umkreis verkleinern)</p>`:u}`:u}
    ${o?a`<button class="primaer" ?disabled=${!R.size} @click=${it}>
      Ausgewählte übernehmen (${R.size})</button>
      <p class="leise klein">Nur Bohrungen mit Schichtdaten in BoreholeML (NRW, Baden-Württemberg); sie kommen mit Quelle und Lizenz ins Projekt.</p>`:u}
    ${at(t)}
    ${t.quellen.map(d=>a`<p class="leise klein">Quelle: ${d.namensnennung} · <a href=${d.beleg} target="_blank" rel="noopener">Dienst</a></p>`)}
    <button class="link klein" @click=${async()=>{const d=await v(()=>$.sgdVerwerfen(s.sig));d&&(P(d),g())}}>Abfrage verwerfen</button>`}function ct(e){const t=s.viewer;t&&(!e.unterlage||e.unterlage.kalibrierung?.gesperrt||!f?t.editor.hilfsmarken({}):t.editor.hilfsmarken({strecke:f.massArt==="strecke"?[f.p1,f.p2]:[],hoehe:f.hoeheArt==="strecke"?[f.h1,f.h2]:[],bezug:f.bezug}))}let Ve=!1;function ut(e){const t=e.standort;return E(a`Standort ${h("standort")}`,a`
    <p class="klein"><b>${w(t.x,1)} / ${w(t.y,1)}</b> · EPSG:${t.epsg}</p>
    <p class="leise klein">Georeferenziert über den Punkt: kein Lageplan, keine Kalibrierung – die Bohrungen der Länder
      kommen mit ihren Koordinaten. Ein Gutachten dazu (Schritt Gutachten) wird ein neues Projekt mit Lageplan.</p>
    <ul class="dienste klein" aria-label="Dienste am Standort">${t.dienste.map(n=>a`<li class=${n.art}>${n.text}</li>`)}</ul>`)}function dt(){const e=s.z;sn(e),ct(e);const t=e.lage_modus!=="reihe"&&e.unterlage?.art==="plan"&&!!e.unterlage.kalibrierung?.gesperrt;return s.punktModus&&!t&&(s.punktModus=!1),s.viewer?.editor.punktModusSetzen(s.punktModus),Ve||(Ve=!0,window.addEventListener("keydown",n=>{n.key==="Escape"&&s.schritt==="lage"&&s.punktModus&&de(!1)})),a`
    <div class="app-panel links">
      ${e.standort?ut(e):a`
        ${E(a`Lage der Bohrungen ${h("lage_art")}`,a`
          <div class="umschalter">
            <label><input type="radio" name="lagemodus" .checked=${e.lage_modus==="koordinaten"}
              @change=${()=>m([{op:"lage_modus",wert:"koordinaten"}])}> Koordinaten (Lageplan)</label>
            <label><input type="radio" name="lagemodus" .checked=${e.lage_modus==="reihe"}
              @change=${()=>m([{op:"lage_modus",wert:"reihe"}])}> Reihe (Längsschnitt)</label>
          </div>`)}
        ${E(a`Unterlage ${h("unterlage")}`,Vn(e))}
        ${e.unterlage?E(a`Kalibrieren`,Wn(e)):u}
        ${E(a`Bohrungen setzen`,Zn(e))}`}
      ${e.standort?E(a`Bohrungen der Länder${e.sgd?.gegenprobe.anzahl?" ✓":""} ${h("sgd")}`,We(e)):u}
      ${E(a`Gelände (DGM)${e.gelaende?.pruefung?.warnungen.length?" ⚠":e.gelaende?" ✓":""} ${h("gelaende")}`,nt(e),!!e.gelaende)}
      ${e.standort?u:E(a`Bohrungen der Länder${e.sgd?.gegenprobe.anzahl?" ✓":""} ${h("sgd")}`,We(e),!!e.sgd)}
      ${E(a`Gebäude (LoD2)${e.gebaeude?" ✓":""} ${h("gebaeude")}`,ot(e),!!e.gebaeude)}
      ${E(a`Darstellung`,a`
        <label class="inline">Ø Bohrsäulen ${h("durchmesser")}
          <input type="number" step="0.1" min="0" class="kurz" placeholder=${`auto ${w(e.durchmesser_auto,1)}`}
            .value=${k(e.durchmesser===null?"":String(e.durchmesser))}
            @change=${n=>m([{op:"durchmesser",wert:y(n)}])}> m</label>
        <p class="leise klein">Je Bohrung im Schritt Bohrungen (Ø Säule). Leer = automatisch nach Modellgröße.</p>`,!1)}
      ${e.hinweise.length?a`<div class="hinweisliste">${e.hinweise.map(n=>a`<p class="klein">ℹ ${n}</p>`)}</div>`:u}
    </div>`}const O=(e,t=1)=>e==null?"–":e.toLocaleString("de-DE",{minimumFractionDigits:t,maximumFractionDigits:t});let U="",$e=null,Ze="";function ht(e){return!e||e.quelle!=="DGM"?"aus den GOK der Bohrungen":`aus dem DGM (an den Bohrungen auf die GOK, GOK − DGM bis ${O(Number(e.gok_minus_dgm_max_m),2)} m)`}function gt(){const e=s.z.einstellungen,t=(l,r)=>m([{op:"einstellungen",[l]:r}]),n=(l,r,o,d,p)=>{const c=e[l];return a`
      <div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${c===null} @change=${z=>t(l,z.target.checked?null:d)}> ${r} automatisch</label>${h(p)}
        ${c===null?u:a`<input type="number" step="any" class="kurz" .value=${k(String(c))}
          @change=${z=>t(l,Number(z.target.value))}> ${o}`}
      </div>`},i=s.modell?.bericht?.parameter??{};return a`
    <section class="karte">
      <h3>Modell</h3>
      <div class="einstellung">
        <span>Interpolation ${h("methode")}</span>
        <label class="inline"><input type="radio" name="methode" .checked=${e.methode==="idw"} @change=${()=>t("methode","idw")}> IDW</label>
        <label class="inline"><input type="radio" name="methode" .checked=${e.methode==="tps"} @change=${()=>t("methode","tps")}> Dünnplatten-Spline</label>
      </div>
      ${n("puffer","Puffer","m",Number(i.puffer_m??20),"puffer")}
      ${n("raster","Raster","m",Number(i.raster_m??5),"raster")}
      ${n("basis","Modellbasis","m NHN",Math.floor(Number(i.basis_nhn??0)),"basis")}
      <div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${e.gok_relativ} @change=${l=>t("gok_relativ",l.target.checked)}> fehlende GOK: Gelände = 0 m</label>${h("gok_relativ")}
      </div>
      ${s.z.gelaende?a`<div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${e.gelaende_dgm} @change=${l=>t("gelaende_dgm",l.target.checked)}> Gelände aus dem DGM</label>${h("gelaende_dgm")}
      </div>`:u}
      ${i.raster_m!==void 0?a`<p class="leise klein">gerechnet: Puffer ${O(Number(i.puffer_m),0)} m · Raster ${O(Number(i.raster_m))} m ·
        Basis ${O(Number(i.basis_nhn),2)} m NHN · Fläche ${O(Number(i.flaeche_m2)/1e4,2)} ha ·
        Gelände ${ht(i.gelaende)}</p>`:u}
    </section>`}function pt(){const e=s.modell?.bericht;if(!e)return u;const t=s.z.vorgabe??e.vorlage_einheiten,n=JSON.stringify(t);(!$e||Ze!==n)&&($e=t.map(r=>({name:r.name,bodenarten:r.bodenarten.join(", ")})),Ze=n);const i=$e,l=()=>m([{op:"vorgabe",wert:i.filter(r=>r.name.trim()).map(r=>({name:r.name.trim(),bodenarten:r.bodenarten.split(",").map(o=>o.trim()).filter(Boolean)}))}]);return a`
    <section class="karte">
      <h3>Einheiten festlegen ${h("einheiten")}</h3>
      <p class="leise klein">${s.z.vorgabe?"Vorgegeben (eigene Einheiten).":"Automatisch korreliert – hier umbenennen oder Bodenarten zusammenlegen."}</p>
      <table class="tabelle kompakt vorgabe">
        <colgroup><col class="pfeil"><col><col><col class="weg"></colgroup>
        <thead><tr><th></th><th>Einheit</th><th>Bodenarten (mit Komma)</th><th></th></tr></thead>
        <tbody>
          ${i.map((r,o)=>a`
            <tr>
              <td class="pfeile"><button class="symbol" ?disabled=${o===0} @click=${()=>{i.splice(o-1,0,...i.splice(o,1)),g()}}>▲</button><button
                class="symbol" ?disabled=${o===i.length-1} @click=${()=>{i.splice(o+1,0,...i.splice(o,1)),g()}}>▼</button></td>
              <td><input .value=${k(r.name)} @input=${d=>{r.name=d.target.value}}></td>
              <td><input .value=${k(r.bodenarten)} @input=${d=>{r.bodenarten=d.target.value}}></td>
              <td><button class="symbol" title="Zeile löschen" @click=${()=>{i.splice(o,1),g()}}>✕</button></td>
            </tr>`)}
        </tbody>
      </table>
      <div class="zeile knopfzeile">
        <button class="link" @click=${()=>{i.push({name:"",bodenarten:""}),g()}}>+ Zeile</button>
        <span class="fueller"></span>
        <button ?disabled=${!s.z.vorgabe} @click=${()=>m([{op:"vorgabe",wert:null}])}>Automatisch korrelieren</button>
        <button class="primaer" @click=${l}>Mit diesen Einheiten rechnen</button>
      </div>
    </section>`}function mt(){const e=s.modell,t=e?.bericht,n=t?.einheiten.find(i=>i.name===U);return a`
    <div class="schritt-einheiten">
      <div class="spalte">
        ${gt()}
        ${pt()}
      </div>
      <div class="spalte breit">
        ${s.rechnet?a`<div class="karte"><div class="kreisel klein"></div> Modell wird gerechnet …</div>`:u}
        ${e?.fehler?a`<div class="karte warnung">Noch kein Modell: ${e.fehler}
          <button class="link" @click=${()=>T("lage")}>→ Lage setzen</button></div>`:u}
        ${t?a`
          <section class="karte">
            <h3>Einheiten (${t.einheiten.length})</h3>
            <table class="tabelle einheiten">
              <thead><tr><th></th><th>Einheit</th><th>Bodenarten</th><th>Volumen [m³]</th><th>max. Mächtigkeit [m]</th>
                <th title="in Bohrungen vorhanden / fehlt / unter der Endteufe">✓ / – / ?</th><th>Hinweise</th></tr></thead>
              <tbody>
                ${t.einheiten.map(i=>a`
                  <tr class=${i.name===U?"gewaehlt":""} @click=${()=>{U=U===i.name?"":i.name,g()}}>
                    <td><span class="farbfeld" style=${`background:${i.farbe}`}></span></td>
                    <td><b>${i.name}</b></td>
                    <td>${i.bodenarten.join(", ")}</td>
                    <td class="zahl">${Math.round(i.volumen_m3).toLocaleString("de-DE")}</td>
                    <td class="zahl">${O(i.maechtigkeit_max_m,2)}</td>
                    <td class="zahl">${i.bohrungen.vorhanden.length} / ${i.bohrungen.fehlt.length} / ${i.bohrungen.unbekannt.length}</td>
                    <td class="klein">${i.hinweise.join("; ")}</td>
                  </tr>`)}
              </tbody>
            </table>
          </section>
          <section class="karte profil-karte">
            <h3>Einheiten je Bohrung <span class="leise klein">(m NHN, Klick wählt die Einheit)</span></h3>
            <div class="profil-scroll">${Mn(t,{hoehe:380,gewaehlt:U,waehlen:i=>{U=i,g()}})}</div>
          </section>
          ${n?a`
            <section class="karte">
              <h3><span class="farbfeld" style=${`background:${n.farbe}`}></span> ${n.name}: Beschreibungen aus dem PDF</h3>
              <table class="tabelle kompakt">
                <thead><tr><th>Bohrung</th><th>Tiefe [m]</th><th>Bodenart</th><th>Beschreibung</th></tr></thead>
                <tbody>${n.schichten.map(i=>a`
                  <tr><td>${i.bohrung}</td><td class="zahl">${O(i.von,2)}–${O(i.bis,2)}</td><td>${i.bodenart??"unklassifiziert"}</td>
                    <td>${i.beschreibung||a`<span class="leise">–</span>`}</td></tr>`)}</tbody>
              </table>
            </section>`:u}`:u}
      </div>
    </div>`}let he="";async function bt(){const e=await v(()=>$.einchecken(s.sig,he));e&&(P(e.zustand),he="",G(`Eingecheckt: v${e.eintrag.nr} · ${e.eintrag.stand.bohrungen[0]}/${e.eintrag.stand.bohrungen[1]} Bohrungen geprüft`,"ok"),g())}const ln=new Set([25831,25832,25833,4647,5650]);let Q=(()=>{try{return localStorage.getItem("groundtwin.organisation")??""}catch{return""}})();function ft(){const e=s.z,t=e.bohrungen.filter(l=>l.modell),n=t.filter(l=>l.schichten_n>0&&l.schichten_geprueft===l.schichten_n&&l.x!==null&&l.y!==null&&l.epsg!==null&&ln.has(l.epsg)&&l.gok!==null&&e.lage_modus==="koordinaten"),i=`${$.exportUrl(s.sig,"boreholeml")}?organisation=${encodeURIComponent(Q)}`;return a`
    <label class="feld breit"><span>Organisation (Absender) ${h("boreholeml")}</span>
      <input type="text" aria-label="Organisation für BoreholeML" placeholder="z. B. Ingenieurbüro …" .value=${Q}
        @input=${l=>{Q=l.target.value;try{localStorage.setItem("groundtwin.organisation",Q)}catch{}g()}}></label>
    ${n.length?a`<a class="knopf" href=${i} download>Bohrungen für den Geologischen Dienst (BoreholeML 3.2)</a>`:a`<span class="knopf aus" title="Erst alle Schichten prüfen; Lage in ETRS89/UTM und GOK nötig">Bohrungen für den Geologischen Dienst (BoreholeML 3.2)</span>`}
    <p class="leise klein">${n.length} von ${t.length} Bohrungen exportierbar (vollständig geprüft, ETRS89/UTM, GOK).</p>`}let ee=!1;async function $t(){if(!ee){ee=!0,g();try{const e=await fetch($.exportUrl(s.sig,"3dtiles"));if(!e.ok){const i=await e.text();let l=i;try{l=JSON.parse(i).detail??i}catch{}G(`3D Tiles: ${l}`,"fehler",1e4);return}const t=/filename\*=UTF-8''([^;]+)/.exec(e.headers.get("content-disposition")??"")?.[1],n=document.createElement("a");n.href=URL.createObjectURL(await e.blob()),n.download=t?decodeURIComponent(t):"baugrundmodell_3dtiles.zip",n.click(),setTimeout(()=>URL.revokeObjectURL(n.href),1e4),G("3D Tiles exportiert (tileset.json + GLB, Höhen ellipsoidisch mit GCG2016).","ok")}finally{ee=!1,g()}}}function kt(){const e=s.z;return e.lage_modus==="koordinaten"&&e.viewer.epsg!==null&&ln.has(e.viewer.epsg)?a`<button class="knopf" ?disabled=${ee} @click=${$t}>${ee?"3D Tiles werden erstellt …":"Baugrundmodell für Cesium (3D Tiles, ZIP)"}</button>${h("tiles3d")}`:a`<span class="knopf aus" title="Nur mit Lage nach Koordinaten in ETRS89/UTM">Baugrundmodell für Cesium (3D Tiles, ZIP)</span>`}const wt={anzeige:"Anzeige",fachdaten:"Fachdaten",bewertungsdaten:"Bewertungsdaten"},vt=e=>e.split("-").reverse().join(".");function zt(e){return!e.bis||e.tage===null?e.regel:`bis ${vt(e.bis)} (${e.tage>0?`noch ${e.tage} Tage`:e.tage===0?"heute":"verstrichen"})`}function St(){const e=s.z.geoldg,t=e.zusammenfassung,n=(r,o)=>m([{op:"geoldg",[r]:o}],{leise:!0}),i=`${$.exportUrl(s.sig,"geoldg")}?organisation=${encodeURIComponent(Q)}`,l=e.punkte.filter(r=>r.quelle==="protokoll").map(r=>r.titel.replace(/, falls durchgeführt$/,""));return a`
    <section class="abschnitt-flach geoldg">
      <h3>Geologischer Dienst (GeolDG) ${h("geoldg")}</h3>
      <div class="zeile">
        <label class="inline">Beginn <input type="date" aria-label="Beginn der Untersuchung" .value=${e.angaben.beginn}
          @change=${r=>n("beginn",r.target.value)}></label>
        <label class="inline">Abschluss <input type="date" aria-label="Abschluss der Untersuchung" .value=${e.angaben.abschluss}
          @change=${r=>n("abschluss",r.target.value)}></label>${h("geoldg_abschluss")}
      </div>
      <label class="inline"><input type="checkbox" aria-label="Auftraggeber ist eine Behörde" .checked=${e.angaben.behoerde}
        @change=${r=>n("behoerde",r.target.checked)}> Auftraggeber ist eine Behörde</label>
      <ul class="fristen">${e.fristen.map(r=>a`
        <li class=${r.tage!==null&&r.tage<0?"warn":""} data-frist=${r.id}><b>${wt[r.id]}</b>
          <a href=${r.url} target="_blank" rel="noopener">${r.beleg}</a>: ${zt(r)}</li>`)}</ul>
      ${e.vorerkundung?a`
        <p class="klein">Noch keine eigene Bohrung: die geplante Erkundung spätestens zwei Wochen vor Beginn anzeigen
          (<a href=${e.anzeige_inhalt.url} target="_blank" rel="noopener">§ 8</a>). ${e.anzeige_inhalt.aus_der_app}</p>`:t.eigene?a`
        <p class="klein geoldg-stand">${t.eigene} eigene Bohrungen: für <b>${t.bereit}</b> liefert GroundTwin Lage, GOK, Endteufe
          und das geprüfte Schichtenverzeichnis, <b>${t.boreholeml}</b> davon im BoreholeML.${t.fremd?` ${t.fremd} Bohrungen der Länder liegen dem Land schon vor.`:""}</p>
        ${t.offen.length?a`<details class="protokoll"><summary class="warnung">⚠ ${t.offen.length} Bohrung(en) offen</summary>
          <ul>${t.offen.map(r=>a`<li><b>${r.code}</b>: ${r.was}</li>`)}</ul></details>`:u}
        <p class="klein leise">Aus dem Bohrprotokoll ergänzen (Spalten in pruefliste.csv): ${l.join(" · ")}.</p>
        <a class="knopf" href=${i} download>Paket für den Geologischen Dienst (ZIP)</a>`:u}
      <p class="leise klein">${e.quelle.hinweis}</p>
    </section>`}function Bt(){const e=s.z,t=s.modell,n=t?.bericht,i=e.pruefstand,l=e.eincheckungen[e.eincheckungen.length-1],r=[["ifc","Baugrundmodell (IFC 4.3)"],["bericht","Prüfbericht (JSON)"],["einheiten","Einheiten-Vorlage (JSON)"],["extraktion","Extraktion (JSON)"],["eingabe","Modell-Eingabe mit Korrekturen (JSON)"],["projekt","Projektstand (JSON)"]];return a`
    <div class="app-panel rechts">
      <section class="abschnitt-flach">
        <h3>Modell</h3>
        ${e.reifegrad.stufe!=="Gutachten"?a`<p class=${`reife ${e.reifegrad.stufe==="Vorerkundung"?"vorerkundung":"gemischt"}`}>
          <b>${e.reifegrad.stufe}</b> – ${e.reifegrad.stufe==="Vorerkundung"?"Bohrungen aus Datenbanken der Länder, kein Gutachten: eine erste Vorstellung für die Planung der Erkundung.":Object.entries(e.reifegrad.anzahl).map(([o,d])=>`${d} ${o}`).join(", ")+": Bohrungen ohne Gutachten sind nicht gegen ein PDF geprüft."}
          ${h("reifegrad")}</p>`:u}
        ${s.rechnet?a`<p><span class="kreisel klein"></span> wird gerechnet …</p>`:u}
        ${t?.fehler?a`<p class="warnung">Noch kein Modell: ${t.fehler}</p>
          <button class="link" @click=${()=>T("lage")}>→ Lage setzen</button>`:u}
        ${n?a`
          <ul class="kennzahlen">
            <li><b>${n.einheiten.length}</b> Einheiten</li>
            <li><b>${n.bohrungen.length}</b> Bohrungen im Modell</li>
            <li class=${n.epsg?"":"warn"}>${n.epsg?`EPSG:${n.epsg}`:"lokales System"}</li>
            <li class=${n.pruefungen.alle_koerper_geschlossen?"ok":"warn"}>${n.pruefungen.alle_koerper_geschlossen?"Körper geschlossen":"Körper offen"}</li>
            <li class=${n.pruefungen.max_abweichung_an_bohrungen_m<.01?"ok":"warn"}>Abweichung an Bohrungen ${n.pruefungen.max_abweichung_an_bohrungen_m.toFixed(3)} m</li>
          </ul>`:u}
        <div class="zeile">
          <label class="inline"><input type="checkbox" .checked=${e.auto} @change=${o=>m([{op:"auto",wert:o.target.checked}],{leise:!0})}>
            automatisch nachführen</label>${h("auto")}
          <span class="fueller"></span>
          <button ?disabled=${s.rechnet} @click=${()=>hn()}>Neu rechnen</button>
        </div>
        <label class="inline">Überhöhung ${h("ueberhoehung")}
          <select @change=${async o=>{const d=Number(o.target.value);await s.viewer?.ueberhoehen(d),await m([{op:"ueberhoehung",wert:d}],{leise:!0})}}>
            ${[1,2,5,10,20].map(o=>a`<option value=${o} .selected=${e.ueberhoehung===o}>${o}×</option>`)}
          </select></label>
      </section>

      <section class="abschnitt-flach">
        <h3>Prüfstand ${h("pruefstand")}</h3>
        <div class="balken"><span>Bohrungen <b>${i.bohrungen[0]}/${i.bohrungen[1]}</b></span><progress max=${i.bohrungen[1]||1} value=${i.bohrungen[0]}></progress></div>
        <div class="balken"><span>Schichten <b>${i.schichten[0]}/${i.schichten[1]}</b></span><progress max=${i.schichten[1]||1} value=${i.schichten[0]}></progress></div>
        <p class="klein">${i.unklassifiziert_offen?a`<span class="warnung">⚠ ${i.unklassifiziert_offen} Schicht(en) nicht klassifiziert</span>
          <button class="link" @click=${()=>T("bohrungen")}>prüfen</button>`:a`<span class="ok">✓ keine offenen Warnungen</span>`}
          · ${i.korrigiert} korrigiert · ${i.manuelle_lage} Lagen manuell · ${i.entfernt} entfernt</p>
        <p class=${`klein ${l&&!e.seit_einchecken_geaendert?"ok":"warn"}`}>
          ${l?`Eingecheckt: ${e.eingecheckt}${e.seit_einchecken_geaendert?" · seitdem geändert":""}`:"noch nicht eingecheckt"}</p>
        <div class="zeile">
          <input class="breit" placeholder="Kommentar (z. B. BK1–BK5 mit Anlage 2 verglichen)" .value=${he}
            @input=${o=>{he=o.target.value}}>
        </div>
        <div class="zeile"><button class="primaer" @click=${bt}>✓ Stand einchecken</button>${h("einchecken")}</div>
        ${e.eincheckungen.length?a`
          <details class="protokoll"><summary>Protokoll (${e.eincheckungen.length})</summary>
            <ul>${[...e.eincheckungen].reverse().map(o=>a`
              <li><b>v${o.nr}</b> ${o.zeit} · ${o.stand.bohrungen[0]}/${o.stand.bohrungen[1]} Bohrungen, ${o.stand.schichten[0]}/${o.stand.schichten[1]} Schichten
                ${o.kommentar?a`<div class="leise klein">${o.kommentar}</div>`:u}</li>`)}</ul>
          </details>`:u}
      </section>

      <section class="abschnitt-flach">
        <h3>Export ${h("export")}</h3>
        <div class="export-liste">
          ${r.map(([o,d])=>a`<a class=${`knopf ${o==="ifc"?"primaer":""}`} href=${$.exportUrl(s.sig,o)}
            download>${d}</a>`)}
          ${kt()}
          ${ft()}
        </div>
      </section>

      ${St()}

      ${t&&(t.hinweise.length||t.nicht_im_modell.length)?a`
        <section class="abschnitt-flach">
          <h3>Hinweise</h3>
          ${t.nicht_im_modell.length?a`<p class="klein"><b>Nicht im Modell:</b> ${t.nicht_im_modell.map(o=>`${o.code} (${o.grund})`).join(", ")}</p>`:u}
          ${t.hinweise.map(o=>a`<p class="klein">ℹ ${o}</p>`)}
        </section>`:u}
    </div>`}const qe={gutachten:"",bohrungen:"Weiter: Lage",lage:"Weiter: Einheiten",einheiten:"Weiter: Modell",modell:""};function Gt(e){const t=s.z;if(!t)return"";const n=t.pruefstand;return e==="gutachten"?"ok":e==="bohrungen"?n.unklassifiziert_offen?"warn":n.bohrungen[0]===n.bohrungen[1]&&n.bohrungen[1]?"ok":"":e==="lage"?t.viewer.bohrungen.filter(l=>l.x===null).length?"warn":"ok":e==="einheiten"||e==="modell"?s.modell?.fehler?"warn":s.modell?.bericht?"ok":"":""}function yt(){const e=s.z;return a`
    <header class="kopf">
      <div class="marke" @click=${()=>T("gutachten")} title="Start">
        <span class="logo">⛰</span>
        <span><b>GroundTwin</b> · Baugrundmodell</span>
      </div>
      <nav class="schritte" aria-label="Schritte">
        ${ae.map(t=>{const n=t.id!=="gutachten"&&!e,i=Gt(t.id);return a`
            <button class=${`schritt-knopf ${s.schritt===t.id?"aktiv":""} ${i}`} ?disabled=${n}
              aria-current=${s.schritt===t.id?"step":"false"} @click=${()=>T(t.id)} title=${t.kurz}>
              <span class="nr">${i==="ok"&&s.schritt!==t.id?"✓":i==="warn"?"!":t.nr}</span>
              <span class="titel">${t.titel}</span>
            </button>`})}
      </nav>
      <div class="projekt">
        ${e&&e.reifegrad.stufe!=="Gutachten"?a`<span class=${`abzeichen ${e.reifegrad.stufe==="Vorerkundung"?"vorerkundung":"gemischt"}`}
          title=${e.reifegrad.stufe==="Vorerkundung"?"Bohrungen aus Datenbanken der Länder, kein Gutachten":"Gutachten und Bohrungen der Länder"}>${e.reifegrad.stufe}</span>`:u}
        ${e?a`<span class="projektname" title=${e.dokumente.map(t=>t.datei).join(", ")}>${e.name}</span>
          <details class="menue">
            <summary title="Projekt">⋯</summary>
            <div class="menue-inhalt" @click=${Dt}>
              <button @click=${()=>T("gutachten")}>Anderes Projekt öffnen</button>
              <button @click=${Mt}>Alle Korrekturen verwerfen …</button>
              <a href="viewer.html" target="_blank" rel="noopener">Viewer allein öffnen</a>
              ${s.info?a`<a href=${s.info.quellcode} target="_blank" rel="noopener">Quellcode (${s.info.lizenz})</a>`:u}
            </div>
          </details>`:u}
      </div>
    </header>`}function Dt(e){e.currentTarget.closest("details")?.removeAttribute("open")}document.addEventListener("click",e=>{for(const t of document.querySelectorAll("details.menue[open]"))t.contains(e.target)||t.removeAttribute("open")});async function Mt(){if(!s.sig||!confirm("Alle Korrekturen, Lagen, Prüfhaken und Eincheckungen dieses Projekts verwerfen – auch übernommene Bohrungen der Länder, DGM und Gebäude? Der Name bleibt."))return;const e=await v(()=>$.zuruecksetzen(s.sig));e&&await V(s.sig,e.standort?"lage":"bohrungen")}function Lt(){if(s.schritt==="gutachten")return u;const e=ae.findIndex(l=>l.id===s.schritt),t=ae[e-1],n=ae[e+1],i=s.z?.pruefstand;return a`
    <footer class="fuss">
      ${t?a`<button @click=${()=>T(t.id)}>← ${t.titel}</button>`:u}
      <span class="fuss-status">${i?`${i.bohrungen[0]}/${i.bohrungen[1]} Bohrungen · ${i.schichten[0]}/${i.schichten[1]} Schichten geprüft`:""}
        ${i?.unklassifiziert_offen?a` · <span class="warnung">⚠ ${i.unklassifiziert_offen} nicht klassifiziert</span>`:u}</span>
      <span class="fueller"></span>
      ${n&&qe[s.schritt]?a`<button class="primaer" @click=${()=>T(n.id)}>${qe[s.schritt]} →</button>`:u}
    </footer>`}function xt(){return s.schritt==="gutachten"||!s.z?Bn():s.schritt==="bohrungen"?Fn():s.schritt==="lage"?dt():s.schritt==="einheiten"?mt():Bt()}function _t(){return a`
    ${yt()}
    <main class=${`inhalt schritt-${s.schritt}`}>
      <section id="schritt" class="schritt">${xt()}</section>
    </main>
    ${Lt()}
    <div class="meldungen" aria-live="polite">
      ${s.meldungen.map(e=>a`<div class=${`meldung ${e.art}`}>${e.text}</div>`)}
    </div>
    ${s.beschaeftigt?a`<div class="beschaeftigt"><div class="kreisel"></div><span>${s.beschaeftigt}</span></div>`:u}`}const Je=document.getElementById("app");let C=null;function Pt(){un(_t(),Je);const e=Je.querySelector("main");C||(C=document.createElement("div"),C.id="buehne",C.className="buehne"),C.parentElement!==e&&e.append(C),document.body.dataset.schritt=s.schritt}gn(Pt);async function on(){const[e,t,n]=location.hash.replace(/^#\/?/,"").split("/").map(decodeURIComponent);if(e&&e!==s.sig){if(await V(e,t||void 0),n&&s.schritt==="bohrungen"){const{bohrungWaehlen:i}=await ke(async()=>{const{bohrungWaehlen:l}=await import("./store-Boho82ME.js").then(r=>r.k);return{bohrungWaehlen:l}},__vite__mapDeps([1,2]),import.meta.url);await i(n)}}else e||await T("gutachten")}window.addEventListener("hashchange",()=>void on());s.info=await v(()=>$.info())??null;g();await Qe();await on();window.app=s;
