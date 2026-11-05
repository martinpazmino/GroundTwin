const __vite__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["./leaflet-CIGW-MKW.css","./store-BPmb1nGN.js","./preload-helper-Ct5FWWRu.js"])))=>i.map(i=>d[i]);
import"./viewer-DAT6rRHi.js";import{_ as we}from"./preload-helper-Ct5FWWRu.js";/* empty css            */import{b as a,A as c,w as H,D as fn}from"./lit-element-BS0sz3Y2.js";import{a as $,S as s,n as p,v as z,m as D,o as V,p as nn,s as ne,b as pe,c as Me,d as m,z as P,e as me,f as $n,g as R,h as kn,i as wn,j as re}from"./store-BPmb1nGN.js";import{l as k,m as vn,k as Ee}from"./lage-DO2kEoSP.js";import"./three.core-Dd2BBCN2.js";const tn=a`<span class="ungeprueft" title="Adresse eingetragen, nicht gegen den Dienst geprüft">ungeprüft</span>`;function an(e,t="Dienste am Standort"){return a`<ul class="dienste klein" aria-label=${t}>${e.map(n=>a`<li class=${n.art}>
    ${n.url?a`<a href=${n.url} target="_blank" rel="noopener noreferrer">${n.text}</a>`:n.text}
    ${n.status==="ungeprueft"?tn:c}</li>`)}</ul>`}function zn(e){if(!e?.length)return c;const t=[...new Set(e.map(n=>n.land).filter(n=>n!=="Deutschland"))];return a`<div class="portale" role="note">
    <p class="klein">Kein Datendienst für ${t.length?t.join(", "):"diesen Ort"} – die Bohrungen im Portal ansehen:</p>
    <ul class="dienste klein" aria-label="Portale der Länder">${e.map(n=>a`<li>
      <a href=${n.url} target="_blank" rel="noopener noreferrer">${n.titel}</a> <span class="leise">(${n.land})</span>
      ${n.status==="ungeprueft"?tn:c}
      ${n.hinweis?a`<div class="leise">${n.hinweis}</div>`:c}</li>`)}</ul>
  </div>`}const ve={ocr:["OCR für Scans","Liest gescannte PDFs und Text, der nur als Linien gezeichnet ist (SHX). Langsamer; bei Vektor-PDFs nicht nötig."],beispiele:["Beispiele","Fertig ausgewertete Gutachten zum Ausprobieren. Echte Daten: Berlin (georeferenziert) und Talheim (ohne Koordinaten). Dazu Standorte ohne Gutachten, die zeigen, was die Länder liefern: Dortmund (NRW, Bohrungen mit Schichtdaten), Karlsruhe (Baden-Württemberg, Schichten oft ohne Petrographie) und Berlin (nur Kopfdaten: Gelände und Gebäude, kein Schichtenmodell). Die Bohrungen fragt der Schritt Lage auf Klick beim Land ab (Netz nötig)."],karte:["Karte","Eine Karte zum Orientieren: ein Klick setzt den Standort; Rechts- und Hochwert in ETRS89/UTM rechnet die App aus (Zone 32 westlich von 12° Ost, sonst 33) und sagt, was die Dienste der Länder dort liefern. Hintergrund basemap.de (amtlich, © GeoBasis-DE / BKG, CC BY 4.0) oder OpenStreetMap. Die Kacheln laden erst beim Öffnen – der Kartenausschnitt geht an diesen Server. Auf wenige Meter genau (Karte in WGS84): für eine Vorerkundung genug."],pruefstand:["Prüfstand","Wie viele Bohrungen und Schichten Sie geprüft haben. Eine Korrektur zählt als geprüft. Der Stand wird beim Einchecken festgehalten."],alle_pruefen:["Alle geprüft","Markiert alle Schichten aller Bohrungen im Modell als geprüft – nur wenn Sie alles mit dem Gutachten verglichen haben. Zurücknehmen ist jederzeit möglich."],warnung:["Warnung","Eine Schicht, deren Bodenart nicht erkannt wurde (unklassifiziert). Bodenart wählen, den Vorschlag nach Norm übernehmen oder die Schicht als geprüft markieren."],bodenart:["Bodenart","Klasse für das Modell; Farbe nach DIN 4023 (Kies gelb, Sand orange, Schluff oliv, Ton violett …). Gleiche Bodenarten werden zu Einheiten verbunden."],norm:["Deutung nach Norm","Die Beschreibung aus dem PDF gelesen nach DIN 4023 / DIN EN ISO 14688-1: Hauptanteil, Nebenanteile (schwach ' / stark ¯), Kurzzeichen, Bodengruppe nach DIN 18196 (nur wenn genannt), Konsistenz. Steht auch im IFC (CPset_Bodenansprache)."],vorschlag:["Vorschlag nach Norm","Für eine unklassifizierte Schicht schlägt die Normen-Datenbank eine Bodenart aus der Beschreibung vor. Sie wird nur übernommen, wenn Sie klicken; danach gilt die Schicht als korrigiert."],geprueft:["Geprüft","Haken: Schicht mit dem Gutachten verglichen. Steht im IFC (Geprueft) und im Prüfstand."],tiefe:["Tiefe","Ober- und Unterkante in m unter Geländeoberkante (GOK). Geändertes wird als korrigiert markiert."],gok:["GOK","Ansatzhöhe der Bohrung in m NHN. Aus dem PDF oder hier eingetragen (manuell). Ohne GOK bei allen Bohrungen rechnet das Modell relativ (Gelände = 0 m)."],koordinaten:["Koordinaten","Rechts- und Hochwert der Bohrung; leer lassen, wenn die Lage im Schritt Lage auf dem Plan gesetzt wird."],entfernen:["Entfernen","Die Bohrung kommt nicht ins Modell (sie bleibt in der Liste unter „Entfernt“ und lässt sich wiederherstellen)."],quelle:["Quelle im PDF","Die Seite des Gutachtens, auf der die Bohrung erkannt wurde; der Rahmen zeigt die gewählte Schicht."],lage_art:["Art der Lage","Koordinaten: Bohrungen mit Rechts-/Hochwert (aus dem PDF, eingetragen oder auf dem Lageplan gesetzt). Reihe: ohne Koordinaten nebeneinander mit Abständen bzw. Stationen aus dem Längsschnitt."],unterlage:["Unterlage","Lageplan (Draufsicht) oder Längsschnitt (Seitenansicht) als PDF. Er liegt im Viewer unter den Bohrungen; nach dem Kalibrieren werden die Bohrungen daraufgezogen."],massstab:["Maßstab","Zwei Punkte auf dem Plan anklicken, deren Abstand Sie kennen (Maßstabsleiste, Bemaßung, zwei Bohrungen), und die wahre Länge in m eintragen. Oder den Maßstab 1:n direkt angeben."],bezug:["Bezugspunkt","Ein Punkt im Plan mit bekannter Koordinate (Koordinatenkreuz, Bohrung mit Koordinaten): anklicken und Rechts-/Hochwert eintragen – im Längsschnitt Station und Höhe NHN."],drehung:["Drehung","Winkel, um den der Plan gegen Norden gedreht ist (gegen den Uhrzeigersinn positiv). Nordpfeil nach oben = 0°; Nordpfeil 10° nach links geneigt = 10°."],hoehe:["Höhenmaßstab","Längsschnitte sind oft überhöht (z. B. Länge 1:500, Höhe 1:100). Ohne Angabe gilt der Längenmaßstab."],epsg:["Koordinatensystem (EPSG)","System der Rechts-/Hochwerte aus der Liste wählen: in Deutschland meist ETRS89 / UTM 32N (25832), im Osten 33N (25833), ältere Pläne Gauß-Krüger (Rechtswert 7-stellig, erste Ziffer = Zone); dazu Schweiz und Österreich. Passen die Werte nicht zum System (Ziffernzahl, Zonenkennung), erscheint ein Hinweis. Steht im IFC (IfcMapConversion)."],sperren:["Sperren","Schloss zu: der Plan liegt fest und ändert sich nicht mehr; jetzt die Bohrungen ziehen. Auf dem Lageplan nur in x/y, im Längsschnitt entlang der Station – in der Höhe nur, wenn das PDF keine GOK hat."],deckkraft:["Deckkraft","Wie stark der Plan die Szene überdeckt."],ohne_lage:["Ohne Lage","Bohrungen ohne Koordinaten: anklicken und dann in den gesperrten Plan klicken (Punkte setzen) – oder mit der Maus aus der Liste auf den Plan ziehen."],punkte:["Punkte setzen","Modus an, dann in den gesperrten Lageplan klicken: die gewählte Bohrung bekommt die Lage, danach ist die nächste ohne Lage dran (oder einen Chip anklicken). Mit „freien Punkt“ entsteht ein Punkt ◆, den Sie in der Liste einer Bohrung zuordnen. ✕ löscht einen Punkt bzw. die gesetzte Lage – im Viewer ebenso: Marke anklicken, Entf. Esc beendet den Modus."],reihe:["Reihe","Bohrungen in einer Linie. Abstand zum Vorgänger je Bohrung eintragen (BK1 → BK2 10 m, BK2 → BK3 15 m) oder eine Station; ohne Eintrag gilt der Standardabstand. Reihenfolge mit den Pfeilen."],standardabstand:["Standardabstand","Abstand zwischen Bohrungen, für die nichts eingetragen ist (nur zur Anschauung, im Modell als schematisch markiert)."],boreholeml:["BoreholeML","Austauschformat der Geologischen Dienste der Länder (Version 3.2). Exportiert werden nur vollständig geprüfte Bohrungen mit Lage in ETRS89/UTM und GOK in m NHN; Petrographie, Genese, Konsistenz, Lagerung, Kalk und Feuchte über die amtlichen Codelisten, die Beschreibung aus dem Gutachten im Klartext. Die Organisation steht als Absender in der Datei. Welche Bohrungen ausgelassen wurden und warum, steht oben in der Datei. Umgekehrt lassen sich BoreholeML-Dateien wie ein Gutachten hochladen (Bohrungen der Länder)."],sgd:["Bohrungen der Länder","Bohrungen aus den Datenbanken der Geologischen Dienste um die Mitte des Projekts: Berlin und Brandenburg mit Kopfdaten und dem Schichtenverzeichnis als Grafik, NRW und Baden-Württemberg in BoreholeML mit den freigegebenen Schichtdaten. Abgefragt wird nur auf Klick – die Anfrage sendet die Lage des Projekts an den Dienst. Bohrungen des Gutachtens, die auch beim Land liegen, zeigen die Abweichung von Lage und GOK (Gegenprobe). Übernommene Bohrungen tragen Quelle, Lizenz und Datum, erscheinen als Raute und gehen nicht in den BoreholeML-Export. Länder ohne Datendienst nennt die Abfrage mit dem Link zu ihrem Portal und der Bohrpunktkarte der BGR („ungeprüft“: Adresse eingetragen, nicht gegen den Dienst getestet). Welches Land: aus den Ländergrenzen (VG2500 des BKG); an einer Grenze beide. Die Adressen pflegt das Werkzeug „Dienste der Länder“ (Menü ⋯)."],gelaende:["Gelände (DGM)","Digitales Geländemodell der Vermessungsverwaltung (Open Data, meist DGM1 mit 1 m Raster) für das Baufeld herunterladen und hier laden: XYZ, ASCII-Raster oder GeoTIFF, mehrere Kacheln auch als ZIP. Die App vergleicht die GOK aus dem PDF mit dem Gelände: liegen alle Bohrungen gleich viel höher oder tiefer, stimmen Lage, EPSG oder Höhenbezug nicht. Fehlende GOK schlägt sie vor – übernommen wird nur auf Klick, markiert als „DGM“ (auch im IFC)."],dgm_land:["DGM vom Land","Holt das DGM1 (1 m) für den Ausschnitt um die Bohrungen plus Rand direkt beim Dienst des Landes (WCS): bisher Brandenburg mit Berlin und NRW. Nur auf Klick – die Anfrage sendet den Ausschnitt an den Dienst. Quelle, Lizenz und Namensnennung bleiben am DGM und gehen ins IFC. Baden-Württemberg liefert über seinen Dienst nur ganze Meter, Bayern hat keinen freien Dienst: dort die DGM1-Kacheln als Datei laden."],gebaeude:["Gebäude (LoD2)","3D-Gebäudemodelle LoD2 der Länder als Umgebung des Baugrundmodells: Berlin, Brandenburg und NRW geben sie als CityGML-Kacheln von 1 × 1 km heraus, in ETRS89/UTM mit Höhen in m NHN – derselbe Rahmen wie das Modell. Nur auf Klick werden die Kacheln um die Bohrungen (plus Rand) geladen; Gebäude, deren Grundriss den Ausschnitt berührt, kommen ins IFC (IfcBuildingElementProxy mit Wänden und Dach, Quelle und Lizenz je Gebäude) und in den Viewer (Knopf „Gebäude“). Bestand, nicht erkundet."],standort:["Standort ohne Gutachten","Ein Projekt an einem Punkt (ETRS89/UTM, aus der Karte oder eingetragen): im Schritt Lage fragt es die Bohrungen der Länder um den Punkt ab, holt das DGM und die Gebäude – ein Lageplan ist nicht nötig, der Punkt ist schon georeferenziert. Übernommene Bohrungen mit Schichtdaten (NRW, Baden-Württemberg) ergeben ein Modell – eine Vorerkundung: Archivdaten unbekannter Güte, ohne Sondierungen, oft alt oder weit weg. Kommt später das Gutachten, entsteht ein neues Projekt, das die Bohrungen der Länder, DGM und Gebäude mitnimmt (gemischt)."],reifegrad:["Reifegrad","Woraus das Modell besteht: Gutachten (nur Bohrungen aus dem PDF), Vorerkundung (nur Bohrungen aus Datenbanken der Länder oder BoreholeML-Dateien) oder gemischt. Er steht in der App, im Viewer, im Prüfbericht und im IFC (CPset_Baugrundmodell.Reifegrad); jede Bohrung trägt ihre Herkunft mit Quelle und Lizenz (CPset_Herkunft)."],gelaende_dgm:["Gelände aus dem DGM","Mit DGM folgt die Oberkante des Modells dem Gelände statt der Interpolation zwischen den GOK. An jeder Bohrung bleibt sie genau auf der GOK; deren Abweichung vom DGM klingt bis zur Reichweite (halber Bohrabstand, höchstens 25 m) ab. Im IFC liegt das Gelände um das Modell als IfcGeographicElement (TERRAIN), im Viewer mit dem Knopf „Gelände“ ein- und ausblendbar. Deckt das DGM das Modellgebiet nicht ganz ab, bleibt die Oberkante aus den GOK (mit Hinweis)."],dgm_epsg:["System der DGM-Datei","XYZ- und ASCII-Dateien enthalten kein Koordinatensystem: das System der Kacheln wählen (meist dasselbe wie das Projekt, z. B. 25832). Ein GeoTIFF bringt es selbst mit."],durchmesser:["Durchmesser","Dicke der Bohrsäulen im Viewer und im IFC (Darstellung, nicht der Bohrdurchmesser im Feld). Automatisch wächst er mit der Modellgröße, damit Säulen auf langen Trassen sichtbar bleiben."],einheiten:["Einheiten","Modelleinheiten verbinden gleiche Bodenarten zwischen den Bohrungen (Sand 1, Kies, Sand 2). Umbenennen oder Bodenarten zusammenlegen (z. B. „Sand, Kies“ als eine Einheit); Reihenfolge von oben nach unten."],methode:["Interpolation","IDW: gewichtetes Mittel der Nachbarbohrungen, ruhig und sicher. Dünnplatten-Spline: glatte Flächen mit Trend, gut bei geneigten Schichten."],puffer:["Puffer","Wie weit das Modell über die Bohrungen hinausreicht. Automatisch: halber Bohrabstand (5–100 m)."],raster:["Raster","Maschenweite der Schichtflächen. Automatisch: Gebietsgröße/40, bei großen Modellen gröber (höchstens 30 000 Knoten)."],basis:["Modellbasis","Unterkante des Modells in m NHN. Automatisch: tiefste Endteufe."],gok_relativ:["Fehlende GOK","Hat keine Bohrung eine GOK, rechnet das Modell relativ (Gelände = 0 m) – markiert im IFC."],auto:["Automatisch nachführen","Jede Änderung (Tabelle, Lage, Einheiten) rechnet das Modell sofort neu."],einchecken:["Einchecken","Hält den Prüfstand fest (Zeit, Zähler, Fingerabdruck des Modells, Kommentar). Das exportierte IFC trägt ihn (CPset_Baugrundmodell.Pruefstand)."],tiles3d:["3D Tiles für Cesium","Das Baugrundmodell als 3D Tiles 1.1 (tileset.json und glTF) für CesiumJS, Cesium for Unreal oder QGIS 3D: Baugrundmodell, Gelände und Gebäude je eine Kachel. Jeder Punkt wird exakt aus ETRS89/UTM umgerechnet, die Höhen ellipsoidisch mit dem Quasigeoid GCG2016 des BKG (CC BY 4.0; beim ersten Export einmal 1 MB geladen). ETRS89 ist nicht in WGS84/ITRF überführt (rund 0,9 m). Quellen und Lizenzen stehen in LIESMICH.txt."],geoldg:["Geologiedatengesetz (GeolDG)","Wer bohrt oder bohren lässt, muss die Untersuchung beim Geologischen Dienst des Landes anzeigen und die Daten übermitteln: Anzeige spätestens zwei Wochen vor Beginn (§ 8), Fachdaten wie das Schichtenverzeichnis spätestens drei Monate nach Abschluss (§ 9), Bewertungsdaten wie Gutachten und räumliche Modelle mit Dokumentation auf Verlangen (§ 10). Die Liste zeigt je Bohrung, was GroundTwin liefert (Lage, GOK, Endteufe, geprüfte Schichten) und was aus dem Bohrprotokoll kommt (Bohrverfahren, Ausbau, Proben, Messungen, Labor). Das Paket enthält BoreholeML, IFC, Prüfbericht, Modelldokumentation und eine Prüfliste zum Ergänzen. Hilfe, keine Rechtsberatung: Form und Weg legt die zuständige Behörde fest."],geoldg_abschluss:["Abschluss der Untersuchung","Die Untersuchung gilt mit Ablauf der Dauer als abgeschlossen, die in der Anzeige angegeben wurde – außer eine Fortdauer wurde rechtzeitig angezeigt (§ 15 Abs. 1). Ab dann laufen drei Monate für die Fachdaten; ist eine Behörde verpflichtet, etwa als Auftraggeber, sechs Monate für die Bewertungsdaten (§ 10 Abs. 2 Satz 2). Die Daten bleiben im Projekt."],export:["Export","IFC 4.3 mit Prüfstand, Bodenansprache je Schicht und Beschreibungen je Einheit; dazu Prüfbericht und die Daten als JSON."],ueberhoehung:["Überhöhung","Höhen im Viewer mal Faktor, damit dünne Schichten sichtbar werden. Die Koordinaten bleiben echt."]};let x=null,ze=null;function se(){x?.remove(),x=null,ze=null}function Sn(e,t){e.preventDefault(),e.stopPropagation();const n=e.currentTarget;if(ze===n){se();return}se();const[i,l]=ve[t];x=document.createElement("div"),x.className="hilfe-blase",x.setAttribute("role","tooltip"),x.innerHTML="<strong></strong><p></p>",x.querySelector("strong").textContent=i,x.querySelector("p").textContent=l,document.body.append(x);const r=n.getBoundingClientRect(),o=x.getBoundingClientRect(),d=Math.min(Math.max(8,r.left+r.width/2-o.width/2),window.innerWidth-o.width-8),h=r.bottom+8+o.height>window.innerHeight?r.top-o.height-8:r.bottom+8;Object.assign(x.style,{left:`${d}px`,top:`${h}px`}),ze=n}document.addEventListener("click",e=>{x&&!x.contains(e.target)&&se()});document.addEventListener("keydown",e=>{e.key==="Escape"&&se()});const g=e=>a`<button type="button" class="hilfe" title=${ve[e][0]} aria-label=${`Hilfe: ${ve[e][0]}`}
    @click=${t=>Sn(t,e)}>?</button>`,Bn="https://sgx.geodatenzentrum.de/wmts_basemapde/tile/1.0.0/de_basemapde_web_raster_farbe/default/GLOBAL_WEBMERCATOR/{z}/{y}/{x}.png",yn="https://tile.openstreetmap.org/{z}/{x}/{y}.png",Ae=[51.16,10.45];let Z=null;const te=e=>e.replace(/[&<>"]/g,t=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[t]),Ne=e=>e.toLocaleString("de-DE",{minimumFractionDigits:1,maximumFractionDigits:1});async function Dn(){const[{default:e}]=await Promise.all([we(()=>import("./leaflet-src-7ah4FPQk.js").then(t=>t.l),[],import.meta.url),we(()=>Promise.resolve({}),__vite__mapDeps([0]),import.meta.url)]);return new Promise(t=>{const n=document.createElement("dialog");n.className="karte-dialog",n.setAttribute("aria-label","Standort auf der Karte wählen"),n.innerHTML=`
      <header><strong>Standort auf der Karte wählen</strong>
        <button type="button" class="symbol schliessen" aria-label="Karte schließen">✕</button></header>
      <div class="karte-flaeche"></div>
      <footer>
        <div class="karte-info klein" aria-live="polite">In die Karte klicken: der Punkt wird der Standort (zum Orientieren,
          auf wenige Meter genau). Mausrad zoomt, Ziehen verschiebt.</div>
        <div class="zeile"><span class="fueller"></span>
          <button type="button" class="abbrechen">Abbrechen</button>
          <button type="button" class="primaer uebernehmen" disabled>Punkt übernehmen</button></div>
      </footer>`,document.body.append(n),n.showModal();const i=n.querySelector(".karte-info"),l=n.querySelector(".uebernehmen"),r=e.map(n.querySelector(".karte-flaeche"),{zoomControl:!0,attributionControl:!0}).setView(Z?[Z.breite,Z.laenge]:Ae,Z?.zoom??6),o=new Date().getFullYear(),d=e.tileLayer(Bn,{maxZoom:18,attribution:`© <a href="https://basemap.de" target="_blank" rel="noopener">GeoBasis-DE / BKG (${o})</a> <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>`}).addTo(r),h=e.tileLayer(yn,{maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap-Mitwirkende</a>'});e.control.layers({"basemap.de (BKG)":d,OpenStreetMap:h},{},{position:"topright"}).addTo(r),e.control.scale({imperial:!1}).addTo(r);const u=e.circleMarker(Ae,{radius:8,color:"#10210a",weight:2,fillColor:"#a2c513",fillOpacity:.95});let B=null,v=0;r.on("click",async M=>{const b=++v;u.setLatLng(M.latlng).addTo(r),B=null,l.disabled=!0,i.textContent="wird umgerechnet …";try{const _=await $.standortPunkt(Number(M.latlng.lng.toFixed(7)),Number(M.latlng.lat.toFixed(7)));if(b!==v)return;B=_,l.disabled=!1,i.innerHTML=`<b>Rechtswert ${Ne(_.x)} · Hochwert ${Ne(_.y)} · EPSG:${_.epsg}</b>
          <ul class="dienste">${_.dienste.map(E=>`<li class="${E.art}">${/^https?:\/\//.test(E.url??"")?`<a href="${te(E.url)}" target="_blank" rel="noopener noreferrer">${te(E.text)}</a>`:te(E.text)}${E.status==="ungeprueft"?' <span class="ungeprueft">ungeprüft</span>':""}</li>`).join("")}</ul>
          <span class="leise">Das Land aus den Ländergrenzen (VG2500 des BKG, auf rund 150 m); Portale als Link.</span>`}catch(_){if(b!==v)return;i.innerHTML=`<span class="warnung">${te(_.message)}</span>`}});const N=M=>{const b=r.getCenter();Z=M?{laenge:M.laenge,breite:M.breite,zoom:Math.max(r.getZoom(),14)}:{laenge:b.lng,breite:b.lat,zoom:r.getZoom()},r.remove(),n.close(),n.remove(),t(M)};n.querySelector(".schliessen").addEventListener("click",()=>N(null)),n.querySelector(".abbrechen").addEventListener("click",()=>N(null)),l.addEventListener("click",()=>N(B)),n.addEventListener("cancel",M=>{M.preventDefault(),N(null)}),requestAnimationFrame(()=>r.invalidateSize())})}let A=[],Se=!0,ie=!1;const S={x:"",y:"",epsg:25832,name:""};let C=null;const Gn=[[25832,"ETRS89 / UTM 32N"],[25833,"ETRS89 / UTM 33N"],[4647,"ETRS89 / UTM 32N (zE-N)"],[5650,"ETRS89 / UTM 33N (zE-N)"]];async function rn(e){for(;;){const t=await z(()=>$.auftrag(e));if(!t)return;if(s.auftrag=t,p(),t.fertig){s.auftrag=null;for(const n of t.fehler)D(n,"fehler",1e4);t.projekt?(A=[],await V(t.projekt,"bohrungen")):p();return}await new Promise(n=>setTimeout(n,600))}}const sn=()=>s.z?.standort?s.sig:"";async function Mn(){if(!A.length)return;const e=await z(()=>$.gutachten(A,Se&&!!s.info?.ocr,sn()));e&&await rn(e.id)}async function Ln(){const e=Number(S.x.replace(",",".")),t=Number(S.y.replace(",","."));if(!Number.isFinite(e)||!Number.isFinite(t)||!S.x||!S.y){D("Rechtswert und Hochwert als Zahlen eingeben.","warn");return}const n=await z(()=>$.standort(e,t,S.epsg,S.name),"Standort wird angelegt …");n&&(await V(n.projekt,n.vorhanden?void 0:"lage"),n.vorhanden&&D(`Den Standort gibt es schon: „${s.z?.name}“ geöffnet.`))}async function xn(){let e=null;try{e=await Dn()}catch(t){D(`Karte: ${t.message}`,"fehler",8e3)}e&&(S.x=String(e.x),S.y=String(e.y),S.epsg=e.epsg,C=e.dienste,p())}function _n(){const e=(n,i,l)=>a`
    <label class="feld"><span>${i}</span><input type="text" inputmode=${n==="name"?"text":"decimal"}
      aria-label=${i} placeholder=${l} .value=${S[n]} @input=${r=>{S[n]=r.target.value,n!=="name"&&C&&(C=null),p()}}></label>`,t=!!(S.x.trim()&&S.y.trim());return a`
    <section class="weg" aria-labelledby="weg-standort">
      <div class="weg-symbol" aria-hidden="true">◎</div>
      <h2 id="weg-standort">Standort</h2>
      <p class="weg-text">Noch kein Gutachten? Ein Punkt auf der Karte genügt: Bohrungen der Länder rund um den Punkt –
        eine <b>Vorerkundung</b>, kein Ersatz für das Gutachten. ${g("standort")}</p>
      <button class=${t?"":"primaer gross-knopf"} @click=${xn}>🗺 Auf der Karte wählen</button>
      ${t?a`<div class="punkt-wahl">
        <p class="klein"><b>${S.x} / ${S.y}</b> · EPSG:${S.epsg}</p>
        ${C?an(C):c}
        ${e("name","Name (frei)","z. B. Marl Nord")}
        <button class="primaer gross-knopf" @click=${Ln}>Projekt am Standort anlegen →</button>
      </div>`:c}
      <details class="still">
        <summary>Koordinaten eingeben</summary>
        <div class="raster-2">
          ${e("x","Rechtswert","z. B. 368130")}
          ${e("y","Hochwert","z. B. 5724400")}
          <label class="feld"><span>System</span>
            <select aria-label="System des Standorts" @change=${n=>{S.epsg=Number(n.target.value),C=null,p()}}>
              ${Gn.map(([n,i])=>a`<option value=${n} ?selected=${S.epsg===n}>${n} · ${i}</option>`)}
            </select></label>
        </div>
        <p class="leise klein">ETRS89/UTM, nur Deutschland. ${g("karte")}</p>
      </details>
    </section>`}async function Ke(e){const t=await z(()=>$.beispiel(e),"Beispiel wird geöffnet …");t?.projekt?await V(t.projekt,t.schritt??"bohrungen"):t?.auftrag&&await rn(t.auftrag)}function Te(e){A=[...e??[]].filter(t=>/\.(pdf|json|xml)$/i.test(t.name)),e?.length&&!A.length&&D("Bitte PDF-Dateien wählen (oder eine Extraktion als JSON, Bohrungen als BoreholeML).","warn"),p()}async function Pn(e,t){confirm(`Projekt „${t}“ mit allen Korrekturen löschen? Das Gutachten selbst bleibt unberührt.`)&&(await z(()=>$.loeschen(e)),await nn())}function En(){const e=s.auftrag,t=!!s.info?.ocr;return a`
    <section class="weg" aria-labelledby="weg-gutachten">
      <div class="weg-symbol" aria-hidden="true">⇪</div>
      <h2 id="weg-gutachten">Gutachten</h2>
      <p class="weg-text">Das Bodengutachten als PDF – Vektor oder Scan. Die Bohrungen werden erkannt; Sie prüfen sie,
        sehen sie in 3D und vergleichen sie mit den Bohrungen der Länder.</p>
      ${sn()?a`<p class="hinweis-standort">Zum Standort <b>${s.z.name}</b>: Bohrungen der Länder (mit Prüfstand),
        DGM und Gebäude kommen in das neue Projekt mit – es ist dann <b>gemischt</b>, beide Quellen bleiben getrennt.</p>`:c}
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
        <label class=${`ablage ${ie?"ueber":""} ${A.length?"bereit":""}`}
          @dragover=${n=>{n.preventDefault(),ie=!0,p()}}
          @dragleave=${()=>{ie=!1,p()}}
          @drop=${n=>{n.preventDefault(),ie=!1,Te(n.dataTransfer?.files)}}>
          <input type="file" accept=".pdf,application/pdf,.json,application/json,.xml,application/xml,text/xml" multiple @change=${n=>Te(n.target.files)}>
          <strong>${A.length?A.map(n=>n.name).join(", "):"PDF hierher ziehen oder klicken"}</strong>
          <span class="leise klein">${A.length?`${A.length} Datei(en) bereit`:"mehrere Dateien möglich (z. B. Anlagen 2–4)"}</span>
        </label>
        <button class="primaer gross-knopf" ?disabled=${!A.length} @click=${Mn}>Auswerten →</button>
        <details class="still">
          <summary>Optionen</summary>
          <div class="zeile">
            <label class="schalter" title=${t?"":"nicht installiert: pip install -r requirements-ocr.txt"}>
              <input type="checkbox" .checked=${Se&&t} ?disabled=${!t} @change=${n=>{Se=n.target.checked}}>
              OCR für Scans ${t?"":"(nicht installiert)"}
            </label>${g("ocr")}
          </div>
          <p class="leise klein">Auch eine Extraktion als JSON oder Bohrungen als BoreholeML (XML) lassen sich laden.</p>
        </details>`}
    </section>`}const Re=5;function Oe(e){return e.map(t=>a`
    <tr>
      <td><button class="link" @click=${()=>V(t.signatur)}>${t.name}</button>${t.standort?a` <span class="abzeichen vorerkundung" title="Standort ohne Gutachten">Standort</span>`:c}
        <div class="leise klein">${t.dokumente.join(", ")}</div></td>
      <td class="zahl" title=${t.fremd?`davon ${t.fremd} aus den Datenbanken der Länder`:""}>${t.bohrungen}</td>
      <td class="zahl">${t.geprueft}${t.eincheckungen?a` · <span title="eingecheckt">✓${t.eincheckungen}</span>`:c}</td>
      <td class="leise klein">${t.geaendert}</td>
      <td><button class="symbol" title="Projekt löschen" aria-label="Projekt löschen" @click=${()=>Pn(t.signatur,t.name)}>🗑</button></td>
    </tr>`)}function An(){if(!s.projekte.length)return c;const e=a`<thead><tr><th>Projekt</th><th>Bohrungen</th><th>geprüft</th><th>geändert</th><th></th></tr></thead>`,t=s.projekte.slice(Re);return a`
    <section class="zuletzt">
      <h3>Zuletzt bearbeitet</h3>
      <table class="tabelle kompakt">${e}<tbody>${Oe(s.projekte.slice(0,Re))}</tbody></table>
      ${t.length?a`<details class="still"><summary>Alle ${s.projekte.length} Projekte</summary>
        <table class="tabelle kompakt">${e}<tbody>${Oe(t)}</tbody></table></details>`:c}
    </section>`}function Nn(){const e=s.auftrag,t=s.info?.beispiele??[];return a`
    <details class="still beispiele">
      <summary>Beispiele ausprobieren</summary>
      <div class="zwei-spalten">
        <div>
          <h4 class="klein">Gutachten ${g("beispiele")}</h4>
          <ul class="auswahl-liste">
            ${t.filter(n=>!n.standort).map(n=>a`
              <li><button class="link" ?disabled=${!!e} @click=${()=>Ke(n.name)}>${n.titel}</button></li>`)}
          </ul>
        </div>
        <div>
          <h4 class="klein">Standort <span class="leise">(Bohrungen der Länder: Abfrage im Schritt Lage, mit Netz)</span></h4>
          <ul class="auswahl-liste">
            ${t.filter(n=>n.standort).map(n=>a`
              <li><button class="link" ?disabled=${!!e} @click=${()=>Ke(n.name)}>${n.titel}</button></li>`)}
          </ul>
        </div>
      </div>
    </details>`}function Kn(){return a`
    <div class="seite-mitte start">
      <header class="start-titel">
        <h1>Baugrund verstehen.</h1>
        <p>Bohrungen aus dem Gutachten oder vom Standort – geprüft, in 3D, im Vergleich mit den Bohrungen der Länder.</p>
      </header>
      <div class="wege">
        ${En()}
        ${_n()}
      </div>
      ${An()}
      ${Nn()}
      ${s.info?a`<p class="leise klein impressum">GroundTwin ${s.info.version} ·
        <a href="dienste.html" target="_blank" rel="noopener">Dienste der Länder</a> ·
        <a href="viewer.html" target="_blank" rel="noopener">Viewer allein</a> · freie Software unter
        <a href=${`${s.info.quellcode}/blob/main/LICENSE`} target="_blank" rel="noopener">${s.info.lizenz}</a> ·
        <a href=${s.info.quellcode} target="_blank" rel="noopener">Quellcode</a><br>Die App extrahiert und schlägt vor;
        die Interpretation und Freigabe bleibt beim Geotechniker.</p>`:c}
    </div>`}const ae="Deutschland · ETRS89 / UTM (amtlich)",I="Deutschland · Gauß-Krüger (alt)",le=[{code:25832,name:"ETRS89 / UTM Zone 32N",gruppe:ae,e:[22e4,101e4],n:[503e4,614e4],hinweis:"Rechtswert 6-stellig, die meisten Länder"},{code:25833,name:"ETRS89 / UTM Zone 33N",gruppe:ae,e:[15e4,7e5],n:[509e4,613e4],hinweis:"Rechtswert 6-stellig, Osten (Berlin, Brandenburg, Sachsen, MV)"},{code:4647,name:"ETRS89 / UTM 32N mit Zone (32…)",gruppe:ae,e:[3223e4,33e6],n:[52e5,614e4],hinweis:"Rechtswert 8-stellig, beginnt mit 32"},{code:5650,name:"ETRS89 / UTM 33N mit Zone (33…)",gruppe:ae,e:[3315e4,3354e4],n:[52e5,613e4],hinweis:"Rechtswert 8-stellig, beginnt mit 33"},{code:31466,name:"DHDN / Gauß-Krüger Zone 2",gruppe:I,e:[23e5,27e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 2"},{code:31467,name:"DHDN / Gauß-Krüger Zone 3",gruppe:I,e:[33e5,37e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 3"},{code:31468,name:"DHDN / Gauß-Krüger Zone 4",gruppe:I,e:[43e5,47e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 4"},{code:31469,name:"DHDN / Gauß-Krüger Zone 5",gruppe:I,e:[531e4,57e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 5"},{code:2398,name:"Krassowski (42/83) / Gauß-Krüger Zone 4",gruppe:I,e:[43e5,47e5],n:[52e5,613e4],hinweis:"neue Länder vor ETRS89, Rechtswert beginnt mit 4"},{code:2399,name:"Krassowski (42/83) / Gauß-Krüger Zone 5",gruppe:I,e:[53e5,57e5],n:[52e5,613e4],hinweis:"neue Länder vor ETRS89, Rechtswert beginnt mit 5"},{code:3068,name:"DHDN / Soldner Berlin",gruppe:"Deutschland · andere",e:[-4e4,9e4],n:[-4e4,8e4],hinweis:"Berlin, alte Katasterkoordinaten (5-stellig)"},{code:2056,name:"CH1903+ / LV95",gruppe:"Schweiz",e:[245e4,287e4],n:[103e4,134e4],hinweis:"E 2 xxx xxx, N 1 xxx xxx"},{code:21781,name:"CH1903 / LV03",gruppe:"Schweiz",e:[45e4,87e4],n:[3e4,34e4],hinweis:"Y 6-stellig, X 5–6-stellig (alt)"},{code:31254,name:"MGI / Austria GK West",gruppe:"Österreich",e:[-11e4,17e4],n:[11e4,34e4],hinweis:"Rechtswert um 0 (±), Hochwert ohne 5 000 000"},{code:31255,name:"MGI / Austria GK Central",gruppe:"Österreich",e:[-16e4,17e4],n:[9e4,46e4],hinweis:"Rechtswert um 0 (±), Hochwert ohne 5 000 000"},{code:31256,name:"MGI / Austria GK East",gruppe:"Österreich",e:[-16e4,1e5],n:[1e5,48e4],hinweis:"Rechtswert um 0 (±), Hochwert ohne 5 000 000"},{code:31257,name:"MGI / Austria GK M28 (BMN)",gruppe:"Österreich",e:[4e4,32e4],n:[11e4,34e4],hinweis:"Bundesmeldenetz West"},{code:31258,name:"MGI / Austria GK M31 (BMN)",gruppe:"Österreich",e:[29e4,62e4],n:[9e4,46e4],hinweis:"Bundesmeldenetz Mitte"},{code:31259,name:"MGI / Austria GK M34 (BMN)",gruppe:"Österreich",e:[59e4,85e4],n:[1e5,48e4],hinweis:"Bundesmeldenetz Ost"},{code:32632,name:"WGS 84 / UTM Zone 32N",gruppe:"GPS (WGS 84)",e:[22e4,101e4],n:[503e4,614e4],hinweis:"wie ETRS89 / UTM 32N (Abweichung < 1 m)"},{code:32633,name:"WGS 84 / UTM Zone 33N",gruppe:"GPS (WGS 84)",e:[15e4,7e5],n:[509e4,613e4],hinweis:"wie ETRS89 / UTM 33N (Abweichung < 1 m)"}],Tn=new Map(le.map(e=>[e.code,e]));function Le(e){return e?Tn.get(e)??null:null}function xe(e){if(!e)return"ohne System (lokal)";const t=Le(e);return t?`EPSG ${e} · ${t.name}`:`EPSG ${e} (nicht in der Liste)`}const ln=(e,t,n)=>t>=e.e[0]&&t<=e.e[1]&&n>=e.n[0]&&n<=e.n[1];function Rn(e,t){return e===null||t===null||!Number.isFinite(e)||!Number.isFinite(t)?[]:le.filter(n=>n.gruppe!=="GPS (WGS 84)"&&ln(n,e,t))}function on(e,t,n){if(t===null||n===null||!Number.isFinite(t)||!Number.isFinite(n))return null;const i=Rn(t,n),l=i.slice(0,3).map(o=>`${o.code} (${o.name})`).join(", ");if(!e)return i.length?{ok:!1,text:`Kein System gewählt – die Werte passen zu ${l}.`}:null;const r=Le(e);return r?ln(r,t,n)?{ok:!0,text:`passt zu EPSG ${e} (${r.hinweis})`}:{ok:!1,text:i.length?`Rechts-/Hochwert passen nicht zu EPSG ${e} (${r.hinweis}), aber zu ${l}.`:"Rechts-/Hochwert passen zu keinem System der Liste – Ziffern prüfen (z. B. fehlende Zonenkennung)."}:{ok:!1,text:`EPSG ${e} ist nicht in der Liste – bitte prüfen.`}}function _e(e,t,n="Koordinatensystem"){const i=[...new Set(le.map(r=>r.gruppe))],l=e!==null&&!Le(e);return a`
    <select class="epsg" aria-label=${n} title=${xe(e)}
      @change=${r=>{const o=r.target.value;t(o===""?null:Number(o))}}>
      <option value="" .selected=${e===null}>– ohne (lokal) –</option>
      ${l?a`<option value=${String(e)} .selected=${!0}>EPSG ${e} – nicht in der Liste ⚠</option>`:c}
      ${i.map(r=>a`
        <optgroup label=${r}>
          ${le.filter(o=>o.gruppe===r).map(o=>a`
            <option value=${String(o.code)} .selected=${o.code===e}>${o.code} · ${o.name}</option>`)}
        </optgroup>`)}
    </select>`}const Y=(e,t=2)=>e.toLocaleString("de-DE",{minimumFractionDigits:t,maximumFractionDigits:t});function un(e){for(const t of[.5,1,2,5,10,20,50,100])if(e/t<=12)return t;return 200}function On(e,t){const n=Math.max(1,...e.map(u=>u.bis)),i=12,l=(t.hoehe-i-14)/n,r=34,o=46,d=un(n),h=[];for(let u=0;u<=n+1e-9;u+=d)h.push(u);return a`<svg class="saeule" viewBox="0 0 150 ${t.hoehe}" width="150" height=${t.hoehe} role="img" aria-label="Bohrsäule">
    <defs>
      <pattern id="schraffur-warn" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
        <rect width="6" height="6" fill="#e6e6e6"></rect><line x1="0" y1="0" x2="0" y2="6" stroke="#f0a33a" stroke-width="3"></line>
      </pattern>
    </defs>
    ${h.map(u=>H`
      <line x1=${r-5} x2=${r} y1=${i+u*l} y2=${i+u*l} class="achse"></line>
      <text x=${r-7} y=${i+u*l+3} class="achse-text" text-anchor="end">${Y(u,d<1?1:0)}</text>`)}
    <line x1=${r} x2=${r} y1=${i} y2=${i+n*l} class="achse"></line>
    ${e.map(u=>H`
      <g class=${`schicht ${u.k===t.gewaehlt?"gewaehlt":""} ${u.warn?"warn":""}`} @click=${()=>t.waehlen?.(u.k)}>
        <title>${u.titel}</title>
        <rect x=${r+4} y=${i+u.von*l} width=${o} height=${Math.max(1,(u.bis-u.von)*l)}
          fill=${u.warn?"url(#schraffur-warn)":u.farbe}></rect>
        ${u.geprueft?H`<text x=${r+o+9} y=${i+(u.von+u.bis)/2*l+4} class="haken">✓</text>`:c}
        ${(u.bis-u.von)*l>11?H`<text x=${r+o+22} y=${i+u.bis*l-2} class="tiefe">${Y(u.bis)}</text>`:c}
      </g>`)}
  </svg>`}function Fn(e,t){const n=[...e.bohrungen].sort((b,_)=>b.x-_.x||b.y-_.y);if(!n.length)return c;const i=new Map(e.einheiten.map(b=>[b.name,b.farbe])),l=Math.max(...n.map(b=>b.gok)),r=Math.min(...n.map(b=>b.endteufe_nhn)),o=22,d=44,h=Math.max(38,Math.min(70,900/n.length)),u=d+n.length*h+10,B=(t.hoehe-o-10)/Math.max(1,l-r),v=b=>o+(l-b)*B,N=un(l-r),M=[];for(let b=Math.ceil(r/N)*N;b<=l+1e-9;b+=N)M.push(b);return a`<svg class="einheitenprofil" viewBox="0 0 ${u} ${t.hoehe}" width=${u} height=${t.hoehe} role="img"
      aria-label="Einheiten je Bohrung">
    ${M.map(b=>H`
      <line x1=${d-4} x2=${u} y1=${v(b)} y2=${v(b)} class="raster"></line>
      <text x=${d-6} y=${v(b)+3} class="achse-text" text-anchor="end">${Y(b,N<1?1:0)}</text>`)}
    ${n.map((b,_)=>{const E=d+_*h+h*.2,be=h*.6;return H`
        <text x=${E+be/2} y=${o-8} class="code" text-anchor="middle">${b.code}</text>
        ${b.einheiten.filter(L=>L.status==="vorhanden"&&L.ok_modell-L.uk_modell>.001).map(L=>H`
          <rect x=${E} y=${v(L.ok_modell)} width=${be} height=${Math.max(.8,(L.ok_modell-L.uk_modell)*B)}
            fill=${i.get(L.einheit)??"#ccc"} class=${`einheit ${t.gewaehlt===L.einheit?"gewaehlt":""}`}
            @click=${()=>t.waehlen?.(L.einheit)}>
            <title>${b.code}: ${L.einheit} ${Y(L.ok_modell)} bis ${Y(L.uk_modell)} m NHN</title>
          </rect>`)}
        <line x1=${E-3} x2=${E+be+3} y1=${v(b.endteufe_nhn)} y2=${v(b.endteufe_nhn)} class="endteufe"></line>`})}
  </svg>`}const oe=(e,t=2)=>e==null?"":e.toLocaleString("de-DE",{minimumFractionDigits:t,maximumFractionDigits:t}),Be=e=>{const t=e.target.value.trim().replace(",",".");return t===""?null:Number(t)},jn=[["boden","Böden"],["organisch","Organisch"],["geologisch","Geologische Benennung"],["fels","Fels"],["anthropogen","Anthropogen"],["unbekannt","Nicht klassifiziert"]];let ue=null,fe="",K=.5,Fe=!1;function cn(){return s.z?.plausibilitaet??[]}function dn(e){return cn().find(t=>t.id===e)?.befunde??[]}function ce(e){const t=ne(),n=t.findIndex(l=>l.id===s.bid),i=t[Math.min(t.length-1,Math.max(0,n+e))];i&&pe(i.id)}function hn(){const e=ne(),t=Me(e.findIndex(n=>n.id===s.bid));t&&pe(t)}async function gn(){const e=s.bid;if(!await m([{op:"bohrung_pruefen",id:e,wert:!0}],{leise:!0}))return;const t=Me(ne().findIndex(n=>n.id===e));t&&t!==e&&await pe(t)}async function je(e){const t=s.z.pruefstand,n=e?`Alle Schichten aller ${t.bohrungen[1]} Bohrungen als geprüft markieren?`:"Die Prüfung aller Bohrungen zurücknehmen?";confirm(n)&&await m([{op:"alle_pruefen",wert:e}])}window.addEventListener("keydown",e=>{if(s.schritt!=="bohrungen"||e.ctrlKey||e.metaKey||e.altKey||e.target?.closest?.("input, select, textarea, [contenteditable]"))return;const n=e.key.toLowerCase();if(e.key==="ArrowDown"||n==="j")ce(1);else if(e.key==="ArrowUp"||n==="k")ce(-1);else if(n==="n")hn();else if(n==="g")gn();else return;e.preventDefault()});async function Hn(e,t){const n=Number(e.id.split(":")[0]),i=(t[0]?.quelle.seite??e.seite)-1,l=`${s.sig}/${n}/${i}`;if(ue?.schluessel===l||fe===l||!s.z?.dokumente[n]?.pdf)return;fe=l;const r=await z(()=>$.seite(s.sig,n,i));fe="",r&&(ue={schluessel:l,daten:r},p())}function In(e){return e.entfernt?a`<span class="zeichen raus" title="nicht im Modell">–</span>`:e.offen>0?a`<span class="zeichen warn" title=${`${e.offen} Schicht(en) nicht klassifiziert`}>⚠</span>`:e.schichten_n&&e.schichten_geprueft===e.schichten_n?a`<span class="zeichen ok" title="alle Schichten geprüft">✓</span>`:a`<span class="zeichen" title="noch zu prüfen">○</span>`}function Un(e){const t=dn(e.id);if(!t.length)return c;const n=t.some(l=>l.stufe==="warnung"),i=t.map(l=>`${l.stufe==="warnung"?"Warnung":"Hinweis"}: ${l.text}`).join(`
`);return a`<span class=${`klein ${n?"warn":"leise"}`} title=${i}>${n?"⚠":"ℹ"}\u00a0${t.length}</span>`}function Wn(e){const t=dn(e.id);if(!t.length)return c;const n=t.filter(r=>r.stufe==="warnung").length,i=t.filter(r=>r.stufe==="hinweis").length,l=[n?`${n} Warnung(en)`:"",i?`${i} Hinweis(e)`:""].filter(Boolean).join(", ");return a`
    <details class="still" ?open=${n>0}>
      <summary class=${n?"warn":""}>${n?"⚠":"ℹ"} Plausibilität (${t.length}): ${l}</summary>
      <ul class="dienste klein">
        ${t.map(r=>a`
          <li class=${r.stufe==="warnung"?"warn":"leise"}>
            ${r.stufe==="warnung"?"⚠ Warnung":"ℹ Hinweis"}: ${r.text}
          </li>`)}
      </ul>
    </details>`}function Cn(){const e=s.z.bohrungen,t=ne(),n=e.filter(i=>i.entfernt);return a`
    <aside class="bohrliste-app">
      <input class="suche" type="search" placeholder="Bohrung suchen …" .value=${s.filter}
        @input=${i=>{s.filter=i.target.value,p()}}>
      <ul class="bliste" role="listbox" aria-label="Bohrungen">
        ${t.map(i=>a`
          <li role="option" aria-selected=${String(i.id===s.bid)} class=${i.id===s.bid?"aktiv":""}
            @click=${()=>pe(i.id)}>
            ${In(i)}
            <span class="name">${i.code} ${Un(i)}</span>
            <span class="wert">${i.schichten_geprueft}/${i.schichten_n}</span>
            <button class="symbol leise-knopf" title="Aus dem Modell entfernen" aria-label=${`${i.code} entfernen`}
              @click=${l=>{l.stopPropagation(),m([{op:"entfernen",id:i.id}])}}>🗑</button>
          </li>`)}
      </ul>
      ${n.length?a`
        <details class="entfernt" ?open=${Fe} @toggle=${i=>{Fe=i.target.open}}>
          <summary>Entfernt / nicht im Modell (${n.length}) ${g("entfernen")}</summary>
          <ul class="bliste">
            ${n.map(i=>a`
              <li class="raus">
                <span class="name">${i.code}</span>
                <span class="wert klein">${i.doppelt_in?"doppelt":i.schichten_n?"":"ohne Schichten"}</span>
                <button class="link klein" ?disabled=${!i.schichten_n} @click=${()=>m([{op:"wiederherstellen",id:i.id}])}>wiederherstellen</button>
              </li>`)}
          </ul>
        </details>`:c}
      <p class="leise klein tasten">↑/↓ blättern · N nächste offene · G alle Schichten geprüft und weiter</p>
    </aside>`}function Vn(){const e=s.z.pruefstand,[t,n]=e.bohrungen,[i,l]=e.schichten,r=cn().flatMap(h=>h.befunde),o=r.filter(h=>h.stufe==="warnung").length,d=r.filter(h=>h.stufe==="hinweis").length;return a`
    <div class="pruefleiste">
      <div class="balken"><span>Bohrungen geprüft <b>${t}/${n}</b></span><progress max=${n||1} value=${t}></progress></div>
      <div class="balken"><span>Schichten geprüft <b>${i}/${l}</b></span><progress max=${l||1} value=${i}></progress></div>
      <span class=${`plakette ${e.unklassifiziert_offen?"warn":"ok"}`}>
        ${e.unklassifiziert_offen?`⚠ ${e.unklassifiziert_offen} Schicht(en) nicht klassifiziert`:"✓ keine offenen Warnungen"}</span>
      ${g("warnung")}
      <span class=${`klein ${o?"warn":"leise"}`}>Plausibilität: ${o} Warnungen, ${d} Hinweise</span>
      <span class="fueller"></span>
      ${g("pruefstand")}
      <button @click=${()=>je(!0)} ?disabled=${t===n&&i===l}>✓ Alle Bohrungen geprüft</button>
      <button class="leise-knopf" @click=${()=>je(!1)} ?disabled=${!i}>Zurücknehmen</button>
      ${g("alle_pruefen")}
    </div>`}function j(e,t,n){return a`<label class="feld"><span>${e}${n?g(n):c}</span>${t}</label>`}function Zn(e){const t=on(e.epsg,e.x,e.y);return t&&!t.ok?a`<p class="hinweise warn">⚠ ${t.text}</p>`:c}function qn(e){const t=ne(),n=t.findIndex(l=>l.id===e.id),i=l=>r=>m([{op:"bohrung",id:e.id,feld:l,wert:Be(r)}]);return a`
    <div class="detail-kopf">
      <div class="titelzeile">
        <h2>${e.code}</h2>
        <span class="leise">${e.dokument} · Seite ${e.seite}${e.doppelt_in?` · doppelt (auch in ${e.doppelt_in})`:""}</span>
        <span class="fueller"></span>
        <button title="Vorherige Bohrung (↑)" ?disabled=${n<=0} @click=${()=>ce(-1)}>↑ Vorherige</button>
        <button title="Nächste Bohrung (↓)" ?disabled=${n>=t.length-1} @click=${()=>ce(1)}>↓ Nächste</button>
        <button title="Nächste Bohrung mit offenen Schichten (N)" ?disabled=${!Me(n)} @click=${hn}>⚠ Nächste offene</button>
      </div>
      <div class="felder">
        ${j("GOK [m NHN]",a`<input type="number" step="0.01" .value=${k(e.gok===null?"":String(e.gok))}
            placeholder="unbekannt" @change=${i("gok")}>
            <small class=${e.gok_quelle==="manuell"||e.gok_quelle==="DGM"?"manuell":"leise"}>${e.gok_quelle||"fehlt"}</small>`,"gok")}
        ${j("Endteufe [m]",a`<output>${oe(e.endteufe)}</output>`)}
        ${j("Rechtswert",a`<input type="number" step="0.01" .value=${k(e.x===null?"":String(e.x))} @change=${i("x")}>`,"koordinaten")}
        ${j("Hochwert",a`<input type="number" step="0.01" .value=${k(e.y===null?"":String(e.y))} @change=${i("y")}>`)}
        ${j("Koordinatensystem (EPSG)",_e(e.epsg,l=>m([{op:"bohrung",id:e.id,feld:"epsg",wert:l}])),"epsg")}
        ${j("Ø Säule [m]",a`<input type="number" step="0.1" min="0" class="kurz" placeholder=${`auto ${oe(s.z.durchmesser??s.z.durchmesser_auto,1)}`}
            .value=${k(e.durchmesser===null?"":String(e.durchmesser))} @change=${i("durchmesser")}>`,"durchmesser")}
        ${j("Grundwasser",a`<output>${e.grundwasser||"–"}</output>`)}
      </div>
      ${Zn(e)}
      ${Wn(e)}
      ${e.hinweise.length?a`<p class="hinweise">ℹ ${e.hinweise.join(" · ")}</p>`:c}
    </div>`}function Jn(e,t){const n=s.z.klassen,i=n.some(l=>l.klasse===t.bodenart);return a`
    <span class="farbfeld" style=${`background:${t.farbe}`}></span>
    <select aria-label="Bodenart" @change=${l=>m([{op:"schicht",id:e.id,k:t.k,feld:"bodenart",wert:l.target.value}])}>
      ${i?c:a`<option .selected=${!0} value=${t.bodenart}>${t.bodenart}</option>`}
      ${jn.map(([l,r])=>a`
        <optgroup label=${r}>
          ${n.filter(o=>o.art===l).map(o=>a`
            <option value=${o.klasse} .selected=${o.klasse===t.bodenart}>${o.name}${o.din4023?` (${o.din4023})`:""}</option>`)}
        </optgroup>`)}
    </select>`}function Qn(e,t){return a`
    <table class="tabelle schichten">
      <thead><tr>
        <th title="geprüft">✓ ${g("geprueft")}</th><th>von [m] ${g("tiefe")}</th><th>bis [m]</th>
        <th>Bodenart ${g("bodenart")}</th><th>Beschreibung (PDF)</th><th>nach Norm ${g("norm")}</th>
      </tr></thead>
      <tbody>
        ${t.map(n=>a`
          <tr class=${[n.offen?"warn":"",n.korrigiert?"korrigiert":"",n.k===s.k?"gewaehlt":""].join(" ")}
            @click=${()=>{s.k=n.k,p()}}>
            <td><input type="checkbox" .checked=${k(n.geprueft)} aria-label="geprüft"
              @change=${i=>m([{op:"schicht",id:e.id,k:n.k,feld:"geprueft",wert:i.target.checked}],{leise:!0})}></td>
            <td><input type="number" step="0.01" min="0" class="tief" .value=${k(String(n.von))}
              @change=${i=>m([{op:"schicht",id:e.id,k:n.k,feld:"oben",wert:Be(i)}])}></td>
            <td><input type="number" step="0.01" min="0" class="tief" .value=${k(String(n.bis))}
              @change=${i=>m([{op:"schicht",id:e.id,k:n.k,feld:"unten",wert:Be(i)}])}></td>
            <td class="bodenart">${Jn(e,n)}
              ${n.offen?a`<div class="warnung">⚠ nicht klassifiziert</div>`:c}
              ${n.korrigiert?a`<div class="leise klein">korrigiert</div>`:c}</td>
            <td class="beschreibung">${n.beschreibung||a`<span class="leise">– keine Beschreibung –</span>`}
              ${n.hinweise.length?a`<div class="leise klein">${n.hinweise.join(" · ")}</div>`:c}</td>
            <td class="norm">
              ${n.norm.benennung?a`<div>${n.norm.benennung}</div>`:c}
              ${n.norm.din4023?a`<code title="Kurzzeichen nach DIN 4023">${n.norm.din4023}</code>`:c}
              ${n.norm.bodengruppe?a` <code title="Bodengruppe nach DIN 18196">${n.norm.bodengruppe}</code>`:c}
              ${[n.norm.konsistenz,n.norm.lagerung,n.norm.kalk,n.norm.bodenfarbe].filter(Boolean).length?a`<div class="leise klein">${[n.norm.konsistenz,n.norm.lagerung,n.norm.kalk,n.norm.bodenfarbe].filter(Boolean).join(" · ")}</div>`:c}
              ${n.norm.hinweise.length?a`<div class="klein hinweis-norm" title=${n.norm.hinweise.join(`
`)}>ℹ ${n.norm.hinweise[0]}${n.norm.hinweise.length>1?` (+${n.norm.hinweise.length-1})`:""}</div>`:c}
              ${n.vorschlag?a`
                <button class="vorschlag" @click=${i=>{i.stopPropagation(),m([{op:"vorschlag",id:e.id,k:n.k}])}}
                  title=${`Vorschlag nach Norm: ${n.vorschlag.benennung}${n.vorschlag.sicher?"":" (unsicher)"}`}>
                  → ${n.vorschlag.klasse} übernehmen</button>${g("vorschlag")}`:c}
            </td>
          </tr>`)}
      </tbody>
    </table>`}function Yn(e,t){Hn(e,t);const n=Number(e.id.split(":")[0]),i=!!s.z.dokumente[n]?.pdf,l=ue?.schluessel===`${s.sig}/${n}/${(t[0]?.quelle.seite??e.seite)-1}`?ue.daten:null,r=t.find(u=>u.k===s.k)??null,o=(u,B)=>{if(!u||!l)return c;const v=l.px_je_pt*K;return a`<div class=${`bbox ${B}`} style=${`left:${u[0]*v}px;top:${u[1]*v}px;width:${(u[2]-u[0])*v}px;height:${(u[3]-u[1])*v}px`}></div>`},d=t.map(u=>u.quelle.bbox).filter(u=>!!u&&u.length===4),h=d.length?[Math.min(...d.map(u=>u[0])),Math.min(...d.map(u=>u[1])),Math.max(...d.map(u=>u[2])),Math.max(...d.map(u=>u[3]))]:null;return a`
    <aside class="quelle-spalte">
      <div class="saeule-rahmen">
        ${On(t.map(u=>({k:u.k,von:u.von,bis:u.bis,farbe:u.farbe,warn:u.offen,geprueft:u.geprueft,titel:`${oe(u.von)}–${oe(u.bis)} m: ${u.bodenart}${u.beschreibung?` – ${u.beschreibung}`:""}`})),{hoehe:420,gewaehlt:s.k,waehlen:u=>{s.k=u,p()}})}
      </div>
      ${i?a`<div class="pdf-rahmen">
        <div class="pdf-kopf"><b>Quelle im PDF</b> ${g("quelle")}
          <span class="fueller"></span>
          ${i?a`<button class="symbol" title="kleiner" @click=${()=>{K=Math.max(.25,K/1.4),p()}}>−</button>
            <button class="symbol" title="größer" @click=${()=>{K=Math.min(1.5,K*1.4),p()}}>+</button>`:c}
        </div>
        ${l?a`
          ${Xn(h,l.px_je_pt*K)}
          <div class="pdf-seite">
            <div class="pdf-flaeche" style=${`width:${l.breite_pt*l.px_je_pt*K}px;height:${l.hoehe_pt*l.px_je_pt*K}px`}>
              <img src=${l.url} alt=${`Seite ${l.seite+1}`} draggable="false">
              ${o(h,"saeule-bbox")}
              ${o(r?.quelle.bbox,"schicht-bbox")}
            </div>
          </div>`:a`<p class="leise klein">Seite wird geladen …</p>`}
      </div>`:c}
    </aside>`}let He="";function Xn(e,t){const n=`${s.bid}/${K}`;return!e||He===n?c:(requestAnimationFrame(()=>{const i=document.querySelector(".pdf-seite");i&&(i.scrollLeft=Math.max(0,e[0]*t-i.clientWidth/3),i.scrollTop=Math.max(0,e[1]*t-40),He=n)}),c)}function et(){const e=s.z,t=s.details.get(s.bid),n=e.bohrungen.find(r=>r.id===s.bid),i=n?Number(n.id.split(":")[0]):0,l=!e.dokumente[i]?.pdf;return a`
    <div class=${`schritt-bohrungen ${l?"ohne-pdf":""}`}>
      ${Vn()}
      ${Cn()}
      <section class="bohrung-detail">
        ${n?a`
          ${qn(n)}
          ${t?a`
            ${Qn(n,t.schichten)}
            <div class="detail-fuss">
              <button class="primaer" title="Alle Schichten dieser Bohrung als geprüft markieren und zur nächsten offenen (G)"
                @click=${gn}>✓ Alle Schichten geprüft – weiter</button>
              <button class="leise-knopf" ?disabled=${!n.schichten_geprueft}
                @click=${()=>m([{op:"bohrung_pruefen",id:n.id,wert:!1}])}>Prüfung zurücknehmen</button>
              <span class="fueller"></span>
              <button class="gefahr" @click=${()=>m([{op:"entfernen",id:n.id}])}>🗑 Aus dem Modell entfernen</button>
            </div>`:a`<p class="leise">Schichten werden geladen …</p>`}`:a`<p class="leise">Links eine Bohrung wählen.</p>`}
      </section>
      ${n&&t?Yn(n,t.schichten):a`<aside class="quelle-spalte"></aside>`}
    </div>`}const w=(e,t=2)=>e==null||!Number.isFinite(e)?"":e.toLocaleString("de-DE",{minimumFractionDigits:t,maximumFractionDigits:t}),G=e=>{const t=e.target.value.trim().replace(",",".");return t===""?null:Number(t)};let f=null,de="",J="plan",X,ye=250,De=100,Ge=100;const O=new Set;function Ie(e){const t=e.unterlage;return t?`${t.sha}/${t.seite}/${t.art}/${JSON.stringify(t.kalibrierung)}`:""}function pn(e){const t=e.unterlage;if(!t)return f=null;if(f&&f.schluessel===Ie(e))return f;const n=t.kalibrierung,i=o=>o&&!("n"in o)?o:null,l=i(n?.massstab),r=i(n?.hoehe);return f={schluessel:Ie(e),massArt:n?.massstab&&"n"in n.massstab?"n":"strecke",p1:l?{u:l.u1,v:l.v1}:null,p2:l?{u:l.u2,v:l.v2}:null,meter:l?.meter??null,n:n?.massstab&&"n"in n.massstab?n.massstab.n:null,hoeheArt:n?.hoehe?"n"in n.hoehe?"n":"strecke":"gleich",h1:r?{u:r.u1,v:r.v1}:null,h2:r?{u:r.u2,v:r.v2}:null,hoeheMeter:r?.meter??null,hoeheN:n?.hoehe&&"n"in n.hoehe?n.hoehe.n:null,bezug:n?.bezug?{u:n.bezug.u,v:n.bezug.v}:null,x:n?.bezug?.x??null,y:n?.bezug?.y??null,drehung:n?.drehung??0,epsg:n?.epsg??e.viewer.epsg??null},f}function Pe(e,t=!1){const n=f,i=e.unterlage;if(!n||!i)return null;let l=null;if(n.massArt==="n"&&n.n&&n.n>0&&(l={n:n.n}),n.massArt==="strecke"&&n.p1&&n.p2&&n.meter&&n.meter>0&&(l={u1:n.p1.u,v1:n.p1.v,u2:n.p2.u,v2:n.p2.v,meter:n.meter}),!l||!n.bezug||n.x===null||n.y===null)return null;let r=null;return i.art==="schnitt"&&n.hoeheArt==="n"&&n.hoeheN&&n.hoeheN>0&&(r={n:n.hoeheN}),i.art==="schnitt"&&n.hoeheArt==="strecke"&&n.h1&&n.h2&&n.hoeheMeter&&n.hoeheMeter>0&&(r={u1:n.h1.u,v1:n.h1.v,u2:n.h2.u,v2:n.h2.v,meter:n.hoeheMeter}),{massstab:l,hoehe:r,bezug:{...n.bezug,x:n.x,y:n.y},drehung:i.art==="plan"?n.drehung:0,epsg:i.art==="plan"?n.epsg:null,gesperrt:t}}function y(){const e=s.z;s.entwurf=Pe(e);const t=s.viewer;t&&f&&(t.editor.hilfsmarken({strecke:f.massArt==="strecke"?[f.p1,f.p2]:[],hoehe:f.hoeheArt==="strecke"?[f.h1,f.h2]:[],bezug:f.bezug}),s.entwurf&&t.editor.vorschau(s.entwurf)),p()}async function nt(e){const t=s.viewer;if(!t||!f)return;de=e,p();const n=await t.editor.bildpunktWaehlen();if(de="",!n||!f||s.z?.unterlage?.kalibrierung?.gesperrt){p();return}f[e]=n,y()}async function Ue(e){s.viewer?.editor.waehlenAbbrechen();const t=Pe(s.z,e);if(!t){D("Für die Kalibrierung fehlen Maßstab oder Bezugspunkt.","warn");return}await m([{op:"kalibrierung",wert:t}])&&(s.entwurf=null,D(e?"Plan kalibriert und gesperrt – jetzt die Bohrungen ziehen.":"Kalibrierung übernommen.","ok"),await s.viewer?.ansicht(s.z?.unterlage?.art==="schnitt"?"sued":"oben"))}async function tt(e){const t=s.z.unterlage;t?.kalibrierung&&await m([{op:"kalibrierung",wert:{...t.kalibrierung,gesperrt:e}}])}async function it(e){const t=e.target,n=t.files?.[0];if(t.value="",!n)return;const i=await z(()=>$.unterlage(s.sig,n,J,0),"Unterlage wird gelesen …");i&&(P(i),s.entwurf=null,p(),await me(),await s.viewer?.lageModus(!0),await s.viewer?.ansicht(i.unterlage?.art==="schnitt"?"sued":"oben"))}async function We(e,t){const n=await z(()=>$.unterlageSeite(s.sig,e,t),"Seite wird gelesen …");n&&(P(n),s.entwurf=null,p(),await me(),await s.viewer?.ansicht(t==="schnitt"?"sued":"oben"))}async function at(){if(!confirm("Unterlage mit ihrer Kalibrierung entfernen? Gesetzte Bohrungen behalten ihre Lage."))return;const e=await z(()=>$.unterlageEntfernen(s.sig));e&&(P(e),s.entwurf=null,p(),await me())}const T=(e,t,n=!0)=>a`<details class="abschnitt" ?open=${n}><summary>${e}</summary><div class="abschnitt-inhalt">${t}</div></details>`;function q(e,t,n,i){return a`<button class=${`punkt ${de===t?"aktiv":""} ${n?"gesetzt":""}`} ?disabled=${i}
    @click=${()=>nt(t)}>${de===t?"… im Plan klicken":n?`${e} ✓`:e}</button>`}function rt(e){const t=on(e.epsg,e.x,e.y);return t?a`<p class=${`klein ${t.ok?"ok":"warn"}`}>${t.ok?"✓":"⚠"} ${t.text}</p>`:c}function st(e){const t=e.unterlage,n=pn(e),i=!!t.kalibrierung?.gesperrt,l=t.art==="plan",r=n.p1&&n.p2?Math.hypot(n.p2.u-n.p1.u,n.p2.v-n.p1.v):null,o=Pe(e),d=o?vn(o.massstab,t.mm_pro_px):null,h=e.viewer.bohrungen.filter(u=>u.x!==null&&(l?!/Plan|Viewer/.test(u.quelle):u.gok_bekannt));return a`
    <p class=${`status ${t.kalibrierung?i?"ok":"":"warn"}`}>
      ${t.kalibrierung?a`${i?"🔒 gesperrt · ":""}${Ee(t)}${l?` · ${xe(t.kalibrierung.epsg)}`:""}`:"nicht kalibriert"}
      ${s.entwurf&&JSON.stringify({...s.entwurf,gesperrt:!1})!==JSON.stringify({...t.kalibrierung??{},gesperrt:!1})?a`<br><span class="leise">Vorschau: ${Ee(t,s.entwurf)} (noch nicht übernommen)</span>`:c}
    </p>
    ${i?a`
      <p class="leise klein">Der Plan liegt fest. ${l?"Bohrungen unten mit „Punkte setzen“ in den Plan klicken oder im Viewer ziehen – nur in x/y":"Bohrungen im Viewer ziehen – entlang der Station; die Höhe nur ohne GOK aus dem PDF"}.</p>
      <button @click=${()=>tt(!1)}>🔓 Entsperren (neu kalibrieren)</button>`:a`
      <fieldset class="gruppe">
        <legend>1 · Maßstab ${g("massstab")}</legend>
        <div class="umschalter">
          <label><input type="radio" name="massart" .checked=${n.massArt==="strecke"} @change=${()=>{n.massArt="strecke",y()}}> Strecke messen</label>
          <label><input type="radio" name="massart" .checked=${n.massArt==="n"} @change=${()=>{n.massArt="n",y()}}> 1:n eingeben</label>
        </div>
        ${n.massArt==="strecke"?a`
          <div class="zeile">${q("Punkt 1","p1",n.p1,!1)}${q("Punkt 2","p2",n.p2,!1)}</div>
          <div class="zeile">
            <span class="leise klein">${r?`gemessen ${w(r,0)} px`:"zwei Punkte anklicken"}</span>
            <label class="inline">wahre Länge <input type="number" step="0.01" min="0" class="kurz" .value=${k(n.meter===null?"":String(n.meter))}
              @input=${u=>{n.meter=G(u),y()}}> m</label>
          </div>`:a`
          <label class="inline">Maßstab 1: <input type="number" step="1" min="1" class="kurz" .value=${k(n.n===null?"":String(n.n))}
            @input=${u=>{n.n=G(u),y()}}></label>`}
        ${d?a`<p class="leise klein">ergibt 1:${Math.round(d).toLocaleString("de-DE")}</p>`:c}
      </fieldset>
      ${l?c:a`
        <fieldset class="gruppe">
          <legend>Höhenmaßstab ${g("hoehe")}</legend>
          <div class="umschalter">
            <label><input type="radio" name="hoeheart" .checked=${n.hoeheArt==="gleich"} @change=${()=>{n.hoeheArt="gleich",y()}}> wie Länge</label>
            <label><input type="radio" name="hoeheart" .checked=${n.hoeheArt==="n"} @change=${()=>{n.hoeheArt="n",y()}}> 1:n</label>
            <label><input type="radio" name="hoeheart" .checked=${n.hoeheArt==="strecke"} @change=${()=>{n.hoeheArt="strecke",y()}}> messen</label>
          </div>
          ${n.hoeheArt==="n"?a`<label class="inline">Höhe 1: <input type="number" step="1" min="1" class="kurz"
              .value=${k(n.hoeheN===null?"":String(n.hoeheN))} @input=${u=>{n.hoeheN=G(u),y()}}></label>`:c}
          ${n.hoeheArt==="strecke"?a`
            <div class="zeile">${q("Höhe oben","h1",n.h1,!1)}${q("Höhe unten","h2",n.h2,!1)}</div>
            <label class="inline">Höhenunterschied <input type="number" step="0.01" min="0" class="kurz"
              .value=${k(n.hoeheMeter===null?"":String(n.hoeheMeter))} @input=${u=>{n.hoeheMeter=G(u),y()}}> m</label>`:c}
        </fieldset>`}
      <fieldset class="gruppe">
        <legend>2 · Bezugspunkt ${g("bezug")}</legend>
        <div class="zeile">${q("Punkt im Plan wählen","bezug",n.bezug,!1)}</div>
        <div class="zeile">
          <label class="feld schmal"><span>${l?"Rechtswert":"Station [m]"}</span>
            <input type="number" step="0.01" .value=${k(n.x===null?"":String(n.x))} @input=${u=>{n.x=G(u),y()}}></label>
          <label class="feld schmal"><span>${l?"Hochwert":"Höhe [m NHN]"}</span>
            <input type="number" step="0.01" .value=${k(n.y===null?"":String(n.y))} @input=${u=>{n.y=G(u),y()}}></label>
        </div>
        ${l?a`
          <label class="feld breit"><span>Koordinatensystem (EPSG) ${g("epsg")}</span>
            ${_e(n.epsg,u=>{n.epsg=u,y()})}</label>
          ${rt(n)}`:c}
        ${h.length?a`
          <label class="inline klein">oder von Bohrung
            <select @change=${u=>{const B=e.viewer.bohrungen.find(v=>v.id===u.target.value);B&&(n.x=B.x,n.y=l?B.y:B.gok,y())}}>
              <option value="">–</option>
              ${h.map(u=>a`<option value=${u.id}>${u.code}</option>`)}
            </select></label>`:c}
      </fieldset>
      ${l?a`
        <fieldset class="gruppe">
          <legend>3 · Drehung ${g("drehung")}</legend>
          <div class="zeile">
            <label class="inline"><input type="number" step="0.1" class="kurz" .value=${k(String(n.drehung))}
              @input=${u=>{n.drehung=G(u)??0,y()}}> ° gegen den Uhrzeigersinn</label>
          </div>
        </fieldset>`:c}
      <div class="zeile knopfzeile">
        <button ?disabled=${!o} @click=${()=>Ue(!1)}>Übernehmen</button>
        <button class="primaer" ?disabled=${!o} @click=${()=>Ue(!0)}>🔒 Übernehmen und sperren</button>
        ${g("sperren")}
      </div>
      ${t.kalibrierung?a`<button class="link klein" @click=${()=>m([{op:"kalibrierung",wert:null}])}>Kalibrierung zurücksetzen</button>`:c}`}`}function lt(e){const t=e.unterlage;return t?a`
    <p><b>${t.name}</b> <span class="leise">· ${t.art==="plan"?"Lageplan":"Längsschnitt"}</span></p>
    <div class="zeile">
      ${(t.seiten??1)>1?a`<label class="inline">Seite <select @change=${n=>We(Number(n.target.value),t.art)}>
          ${Array.from({length:t.seiten},(n,i)=>a`<option value=${i} .selected=${i===t.seite}>${i+1}</option>`)}
        </select></label>`:c}
      <label class="inline">Ansicht <select @change=${n=>We(t.seite,n.target.value)}>
        <option value="plan" .selected=${t.art==="plan"}>Lageplan</option>
        <option value="schnitt" .selected=${t.art==="schnitt"}>Längsschnitt</option>
      </select></label>
    </div>
    <label class="inline">Deckkraft ${g("deckkraft")}
      <input type="range" min="0.1" max="1" step="0.05" .value=${String(s.viewer?.editor.deckkraft??.85)}
        @input=${n=>{s.viewer&&(s.viewer.editor.deckkraft=Number(n.target.value),s.viewer.editor.bildSichtbarkeit())}}></label>
    <button class="link klein" @click=${at}>Unterlage entfernen</button>`:a`
      <p class="leise klein">Lageplan (von oben) oder Längsschnitt (von der Seite) als PDF – er liegt im Viewer unter den Bohrungen.</p>
      <div class="umschalter">
        <label><input type="radio" name="neueart" .checked=${J==="plan"} @change=${()=>{J="plan"}}> Lageplan</label>
        <label><input type="radio" name="neueart" .checked=${J==="schnitt"} @change=${()=>{J="schnitt"}}> Längsschnitt</label>
      </div>
      <label class="datei-knopf"><input type="file" accept=".pdf,application/pdf" @change=${it}>PDF wählen …</label>`}function ot(e){const t=e.unterlage,n=!t||!!t.kalibrierung?.gesperrt,i=e.viewer.bohrungen.filter(o=>o.x===null),l=e.lage_modus==="reihe",r=!l&&t?.art==="plan"&&!!t.kalibrierung?.gesperrt;return a`
    ${n?c:a`<p class="warnung">Erst kalibrieren und sperren (🔒) – dann Punkte setzen oder Bohrungen ziehen.</p>`}
    ${r?ut(e):c}
    ${i.length?a`
      <p class="klein">Ohne Lage (${i.length}) – ${r?"anklicken = als Nächste setzen, oder":""} in den Viewer ziehen
        ${g("ohne_lage")}</p>
      <div class="parkplatz">
        ${i.map(o=>a`<span class=${`park ${n?"":"gesperrt"} ${s.punktModus&&s.naechste===o.id?"aktiv":""}`}
          title=${r?"Klick: als nächste Bohrung setzen · Ziehen: direkt in den Viewer":"In den Viewer ziehen"}
          @pointerdown=${d=>s.viewer?.editor.ziehenStart(d,o.id,!0)}
          @click=${()=>{r&&he(!0,o.id)}}>${o.code}</span>`)}
      </div>`:a`<p class="leise klein">Alle Bohrungen im Modell haben eine Lage.</p>`}
    ${r?ct(e):c}
    ${l?dt(e):c}`}function he(e,t){s.punktModus=e,t!==void 0?s.naechste=t:e&&!s.naechste&&(s.naechste=$n()),s.viewer?.editor.punktModusSetzen(e),p()}function ut(e){const t=e.viewer.bohrungen.filter(i=>i.x===null),n=e.viewer.bohrungen.filter(i=>i.x!==null);return a`
    <div class="zeile">
      <button class=${s.punktModus?"primaer":""} @click=${()=>he(!s.punktModus)}>
        ${s.punktModus?"● Punkte setzen – Klick in den Plan":"＋ Punkte im Plan setzen"}</button>
      ${s.punktModus?a`<button class="leise-knopf" @click=${()=>he(!1)}>Fertig (Esc)</button>`:c}
      ${g("punkte")}
    </div>
    ${s.punktModus?a`
      <label class="feld breit"><span>Nächster Klick setzt</span>
        <select class="naechste" @change=${i=>{s.naechste=i.target.value,p()}}>
          <option value="" .selected=${!s.naechste}>– freien Punkt (später zuordnen) –</option>
          ${t.length?a`<optgroup label="Ohne Lage">
            ${t.map(i=>a`<option value=${i.id} .selected=${s.naechste===i.id}>${i.code}</option>`)}</optgroup>`:c}
          ${n.length?a`<optgroup label="Mit Lage (neu setzen)">
            ${n.map(i=>a`<option value=${i.id} .selected=${s.naechste===i.id}>${i.code}</option>`)}</optgroup>`:c}
        </select></label>
      <p class="leise klein">Danach ist automatisch die nächste Bohrung ohne Lage dran.</p>`:c}`}function ct(e){const t=e.viewer.bohrungen.filter(r=>r.x!==null&&/Plan|Viewer/.test(r.quelle)),n=e.viewer.bohrungen,i=n.filter(r=>r.x===null);if(!t.length&&!e.punkte.length)return c;const l=(r,o)=>a`<span class="leise klein">R ${w(r)}<br>H ${w(o)}</span>`;return a`
    <p class="klein">Gesetzte Punkte (${t.length+e.punkte.length})</p>
    <table class="tabelle kompakt punkte">
      <tbody>
        ${e.punkte.map(r=>a`
          <tr class=${`frei ${s.viewer?.editor.punktGewaehlt===r.id?"gewaehlt":""}`}>
            <td><button class="link" title="Im Viewer wählen" @click=${()=>{s.viewer?.editor.punktWaehlen(r.id),p()}}>◆ ${r.id}</button></td>
            <td>${l(r.x,r.y)}</td>
            <td><select aria-label=${`${r.id} zuordnen`} @change=${o=>{const d=o.target.value;d&&m([{op:"punkt_zuordnen",punkt:r.id,bohrung:d}])}}>
              <option value="" selected>– Bohrung zuordnen –</option>
              ${i.length?a`<optgroup label="Ohne Lage">${i.map(o=>a`<option value=${o.id}>${o.code}</option>`)}</optgroup>`:c}
              <optgroup label="Mit Lage (ersetzen)">${n.filter(o=>o.x!==null).map(o=>a`<option value=${o.id}>${o.code}</option>`)}</optgroup>
            </select></td>
            <td><button class="symbol" title="Punkt löschen" @click=${()=>m([{op:"punkt_loeschen",punkt:r.id}])}>✕</button></td>
          </tr>`)}
        ${t.map(r=>a`
          <tr class=${s.viewer?.editor.ausgewaehlt===r.id?"gewaehlt":""}>
            <td><button class="link" title="Im Viewer wählen" @click=${()=>{s.viewer?.nadelWaehlen(r.id),p()}}>● ${r.code}</button></td>
            <td>${l(r.x,r.y)}</td>
            <td><select aria-label=${`${r.code} umhängen`} @change=${o=>{const d=o.target.value;d==="-"?m([{op:"lage_loesen",id:r.id}]):d&&d!==r.id&&m([{op:"lage_umhaengen",id:r.id,nach:d}])}}>
              <option value=${r.id} selected>${r.code}</option>
              <option value="-">– Zuordnung lösen (freier Punkt) –</option>
              ${i.length?a`<optgroup label="Andere Bohrung (ohne Lage)">${i.map(o=>a`<option value=${o.id}>${o.code}</option>`)}</optgroup>`:c}
            </select></td>
            <td><button class="symbol" title="Lage entfernen (Bohrung wieder ohne Lage)" @click=${()=>m([{op:"lage_entfernen",id:r.id}])}>✕</button></td>
          </tr>`)}
      </tbody>
    </table>`}function dt(e){const t=e.reihe.map(i=>i.id),n=(i,l)=>{const r=[...t],[o]=r.splice(i,1);r.splice(Math.max(0,Math.min(r.length,i+l)),0,o),m([{op:"reihe",reihenfolge:r}],{leise:!0})};return a`
    <div class="zeile">
      <label class="inline">Standardabstand ${g("standardabstand")}
        <input type="number" step="1" min="1" class="kurz" .value=${k(String(e.reihe_standard))}
          @change=${i=>m([{op:"reihe",standard:G(i)}])}> m</label>
    </div>
    <table class="tabelle kompakt reihe">
      <thead><tr><th></th><th>Bohrung</th><th>Abstand [m] ${g("reihe")}</th><th>Station [m]</th></tr></thead>
      <tbody>
        ${e.reihe.map((i,l)=>a`
          <tr>
            <td class="pfeile"><button class="symbol" ?disabled=${l===0} title="nach vorn" @click=${()=>n(l,-1)}>▲</button><button class="symbol"
              ?disabled=${l===t.length-1} title="nach hinten" @click=${()=>n(l,1)}>▼</button></td>
            <td>${i.code}</td>
            <td><input type="number" step="0.1" min="0" class="kurz" ?disabled=${l===0} .value=${k(i.abstand===null?"":String(i.abstand))}
              @change=${r=>m([{op:"reihe",abstand:{[i.id]:G(r)}}],{leise:!0})}></td>
            <td><input type="number" step="0.1" class="kurz" .value=${k(String(i.station))} title=${i.quelle_text}
              @change=${r=>m([{op:"reihe",station:{[i.id]:G(r)}}],{leise:!0})}></td>
          </tr>`)}
      </tbody>
    </table>`}async function ht(e){const t=e.target,n=[...t.files??[]];if(t.value="",!n.length)return;const i=X===void 0?s.z?.viewer.epsg??null:X,l=await z(()=>$.dgm(s.sig,n,i),"DGM wird gelesen …");if(l){P(l),p();const r=l.gelaende?.pruefung?.warnungen.length??0;D(r?"DGM geladen – Hinweise zum Vergleich beachten.":"DGM geladen.",r?"warn":"ok")}}async function gt(){const e=await z(()=>$.dgmAbruf(s.sig,De),"DGM wird beim Land abgerufen …");if(e){P(e),p();const t=e.gelaende?.pruefung?.warnungen.length??0;D(t?"DGM vom Land geladen – Hinweise zum Vergleich beachten.":"DGM vom Land geladen.",t?"warn":"ok")}}function Ce(e){return e.lage_modus!=="koordinaten"?c:a`
    <div class="zeile">
      <label class="inline">Rand <input type="number" min="0" max="1000" step="25" class="kurz" aria-label="Rand um die Bohrungen"
        .value=${k(String(De))} @change=${t=>{De=G(t)??100}}> m</label>
      <button @click=${gt} title="Sendet den Ausschnitt um die Bohrungen an den Dienst des Landes">
        DGM vom Land abrufen</button>${g("dgm_land")}
    </div>
    <p class="leise klein">Brandenburg mit Berlin und NRW (DGM1, WCS). Sendet den Ausschnitt um die Bohrungen an den Dienst.</p>`}async function pt(){if(!confirm("DGM aus dem Projekt entfernen? Übernommene GOK bleiben (Quelle DGM)."))return;const e=await z(()=>$.dgmEntfernen(s.sig));e&&(P(e),p())}const $e={ok:["✓","ok"],abweichung:["⚠ weicht ab","warn"],ohne_gok:["GOK fehlt",""],aus_dgm:["aus dem DGM","leise"],ausserhalb:["außerhalb","leise"],ohne_lage:["ohne Lage","leise"],anderes_system:["anderes EPSG","warn"]},Ve=e=>e===null?"":Math.abs(e)<.005?w(0):`${e>0?"+":""}${w(e)}`;function mt(e){const t=e.gelaende,n=h=>a`<label class="datei-knopf"><input type="file" multiple aria-label="DGM-Dateien"
    accept=".xyz,.txt,.csv,.asc,.tif,.tiff,.zip,.gz" @change=${ht}>${h}</label>`,i=X===void 0?e.viewer.epsg??null:X,l=a`<label class="feld breit"><span>System der Datei (XYZ, ASCII) ${g("dgm_epsg")}</span>
    ${_e(i,h=>{X=h,p()},"System der DGM-Datei")}</label>`;if(!t)return a`
      <p class="leise klein">DGM-Kachel(n) des Landes (Open Data, z. B. DGM1) als XYZ, ASCII-Raster oder GeoTIFF, auch als
        ZIP – Höhen in m NHN. Damit prüft die App die GOK, schlägt fehlende vor und legt das Gelände ins Modell.</p>
      ${Ce(e)}
      ${l}
      ${n("DGM-Dateien wählen …")}`;const r=t.info,o=t.pruefung,d=r.quelle;return a`
    <p><b>${r.name}</b><br><span class="leise klein">${xe(r.epsg)} · Raster ${w(r.dx,1)} m ·
      ${r.spalten.toLocaleString("de-DE")} × ${r.zeilen.toLocaleString("de-DE")} · ${w(r.zmin,1)} – ${w(r.zmax,1)} m NHN</span></p>
    ${d?a`<p class="leise klein">${d.anbieter} · <a href=${d.beleg} target="_blank" rel="noopener">${d.lizenz}</a> ·
      ${d.namensnennung} · abgerufen ${d.abgerufen}</p>`:c}
    ${t.fehler?a`<p class="warnung klein">${t.fehler}</p>`:c}
    ${o?a`
      <table class="tabelle kompakt gelaende">
        <thead><tr><th>Bohrung</th><th class="zahl">GOK</th><th class="zahl">DGM</th><th class="zahl">Δ [m]</th><th></th></tr></thead>
        <tbody>
          ${o.zeilen.map(h=>a`
            <tr class=${$e[h.status][1]}>
              <td><button class="link" title="Im Viewer wählen" @click=${()=>{s.viewer?.nadelWaehlen(h.id),p()}}>${h.code}</button></td>
              <td class="zahl">${w(h.gok)}</td>
              <td class="zahl">${w(h.dgm)}</td>
              <td class="zahl">${Ve(h.differenz)}</td>
              <td class=${`klein ${$e[h.status][1]}`}>${h.status==="ohne_gok"?a`<button class="klein" title="GOK aus dem DGM übernehmen (Quelle DGM)"
                    @click=${()=>m([{op:"gok_aus_dgm",ids:[h.id]}])}>übernehmen</button>`:$e[h.status][0]}</td>
            </tr>`)}
        </tbody>
      </table>
      ${o.verglichen?a`<p class="leise klein">${o.verglichen} verglichen · Median ${Ve(o.median)} m ·
        größte Abweichung ${w(o.max)} m (unauffällig bis ${w(o.toleranz,1)} m)</p>`:c}
      ${o.warnungen.map(h=>a`<p class="warnung klein">⚠ ${h}</p>`)}
      ${o.vorschlaege>1?a`<button @click=${()=>m([{op:"gok_aus_dgm"}])}>
        Alle ${o.vorschlaege} fehlenden GOK aus dem DGM übernehmen</button>`:c}`:c}
    ${Ce(e)}
    ${l}
    <div class="zeile">${n("Andere DGM-Dateien …")}
      <button class="link klein" @click=${pt}>DGM entfernen</button></div>`}async function bt(){const e=await z(()=>$.sgdAbfrage(s.sig,ye),"Dienste der Länder werden abgefragt …");if(!e?.sgd)return;P(e),O.clear(),p();const t=e.sgd;D(`${t.treffer.length} Bohrungen der Länder im Umkreis von ${w(t.radius,0)} m`+(t.fehler.length?` – ${t.fehler.length} Dienst(e) ohne Antwort`:""),t.fehler.length?"warn":"ok")}async function ft(){const e=[...O].map(n=>({dienst:n.slice(0,n.indexOf("/")),id:n.slice(n.indexOf("/")+1)})),t=await z(()=>$.sgdUebernehmen(s.sig,e),"Schichtdaten werden beim Land geholt …");if(t){P(t.zustand),O.clear();for(const n of t.meldungen)D(n,"ok");await me(),p()}}function $t(e){const t=e.treffer.filter(r=>!r.uebernehmbar&&!r.uebernommen&&!r.gutachten);if(!t.length)return c;const n=r=>e.quellen.find(o=>o.dienst===r)?.land??r,i=r=>{const o=t.filter(d=>d.schichten===r);return o.length?`${o.length} (${[...new Set(o.map(d=>n(d.dienst)))].join(", ")})`:""},l=[i("grafik")&&`${i("grafik")} nur mit Kopfdaten: das Land gibt das Schichtenverzeichnis nur als Bild heraus (Profil ↗), nicht als Daten`,i("keine")&&`${i("keine")} ohne Schichtenverzeichnis`,i("ohne Petrographie")&&`${i("ohne Petrographie")} mit Schichten ohne Petrographie`].filter(Boolean);return a`<p class="leise klein sgd-warum">Nicht übernehmbar: ${l.join("; ")}. Ohne Schichten entsteht kein Modell –
    sie zu erfinden wäre falsch. Lage, GOK und Teufe sehen Sie hier; die Schichten im Profil des Landes. Übernehmbar sind
    Bohrungen mit Schichtdaten in BoreholeML (NRW, Baden-Württemberg).</p>`}function kt(e){return e.gutachten?a`<span class="ok" title="Dieselbe Bohrung im Gutachten">= ${e.gutachten}</span>`:e.uebernommen?a`<span class="ok">✓ im Projekt</span>`:e.schichten==="boreholeml"?a`${e.schichten_n} Schichten`:e.schichten==="grafik"&&e.profil?a`<a href=${e.profil} target="_blank" rel="noopener">Profil ↗</a>`:a`<span class="leise">${e.schichten==="ohne Petrographie"?"ohne Petrographie":"keine Schichten"}</span>`}async function wt(){const e=await z(()=>$.gebaeudeAbruf(s.sig,Ge),"Gebäude werden beim Land abgerufen …");e&&(P(e),p(),D(`${e.gebaeude?.anzahl??0} Gebäude geladen – im Modell als Umgebung.`,"ok"))}async function vt(){const e=await z(()=>$.gebaeudeEntfernen(s.sig));e&&(P(e),p())}function zt(e){if(e.lage_modus!=="koordinaten")return a`<p class="leise klein">Nur mit Lage nach Koordinaten.</p>`;const t=e.gebaeude,n=a`
    <div class="zeile">
      <label class="inline">Rand <input type="number" min="0" max="1000" step="25" class="kurz" aria-label="Rand der Gebäude"
        .value=${k(String(Ge))} @change=${l=>{Ge=G(l)??100}}> m</label>
      <button @click=${wt} title="Lädt die Kacheln (1 × 1 km) um die Bohrungen beim Land">
        ${t?"Gebäude neu abrufen":"Gebäude vom Land abrufen"}</button>${g("gebaeude")}
    </div>`;if(!t)return a`
      <p class="leise klein">3D-Gebäudemodelle LoD2 von Berlin, Brandenburg und NRW (CityGML, m NHN) als Umgebung im Modell und
        im IFC. Lädt die Kacheln von 1 × 1 km um die Bohrungen – das verrät die Lage des Projekts auf etwa 1 km.</p>
      ${n}`;const i=t.quelle;return a`
    <p><b>${t.anzahl.toLocaleString("de-DE")} Gebäude</b> · ${t.flaechen.toLocaleString("de-DE")} Flächen ·
      ${i.kacheln} Kachel${i.kacheln===1?"":"n"} <span class="leise klein">· abgerufen ${i.abgerufen}</span></p>
    ${i.dienste.map(l=>a`<p class="leise klein">${l.anbieter} · <a href=${l.beleg} target="_blank" rel="noopener">${l.lizenz}</a> ·
      ${l.namensnennung}</p>`)}
    ${i.ohne_kachel.length?a`<p class="leise klein">ohne Kachel beim Land: ${i.ohne_kachel.join(", ")}</p>`:c}
    ${i.fehler.map(l=>a`<p class="warnung klein">⚠ ${l}</p>`)}
    ${t.hinweis?a`<p class="warnung klein">⚠ ${t.hinweis}</p>`:c}
    <p class="leise klein">Im Viewer mit dem Knopf „Gebäude“ ein- und ausblendbar.</p>
    ${n}
    <button class="link klein" @click=${vt}>Gebäude entfernen</button>`}function St(e){if(e.lage_modus==="reihe")return a`<p class="leise klein">Nur mit Lage nach Koordinaten.</p>`;const t=e.sgd,n=a`
    <p class="leise klein">Bohrungen aus den Datenbanken der Geologischen Dienste um die Mitte des Projekts.
      <b>Die Abfrage sendet die Lage des Projekts an den Dienst des Landes.</b></p>
    <div class="zeile">
      <label class="inline">Umkreis <input type="number" min="10" max="2000" step="50" class="kurz" aria-label="Umkreis der Abfrage"
        .value=${k(String(ye))} @change=${d=>{ye=G(d)??250}}> m</label>
      <button @click=${bt}>${t?"Neu abfragen":"Abfragen"}</button>
    </div>`;if(!t)return n;const i=t.gegenprobe,l=i.anzahl>0&&(i.lage_max??0)<=1&&(i.gok_max??0)<=.5,r=t.treffer.slice(0,60),o=t.treffer.filter(d=>d.uebernehmbar).length;return a`
    ${n}
    <p class="klein">${t.treffer.length} Bohrungen im Umkreis von ${w(t.radius,0)} m · ${t.zeit}</p>
    ${i.anzahl?a`<p class=${`klein ${l?"ok":"warnung"}`}>${l?"✓":"⚠"} ${i.anzahl} Bohrungen des Gutachtens auch
      beim Land: Lage ≤ ${w(i.lage_max)} m${i.gok_max!==null?a`, GOK ≤ ${w(i.gok_max)} m`:c}${l?"":" – Lage und GOK prüfen"}</p>`:c}
    ${t.fehler.map(d=>a`<p class="warnung klein">${d.dienst}: ${d.fehler}</p>`)}
    ${zn(t.portale)}
    ${r.length?a`
      <table class="tabelle kompakt sgd">
        <thead><tr><th></th><th>Bohrung</th><th class="zahl">Abstand</th><th class="zahl">GOK</th><th class="zahl">Teufe</th><th>Schichten</th></tr></thead>
        <tbody>
          ${r.map(d=>{const h=`${d.dienst}/${d.id}`;return a`<tr class=${d.gutachten?"doppelt":""}>
              <td>${d.uebernehmbar?a`<input type="checkbox" aria-label=${`${d.name} übernehmen`} .checked=${O.has(h)}
                @change=${u=>{u.target.checked?O.add(h):O.delete(h),p()}}>`:c}</td>
              <td title=${`${d.dienst} · ID ${d.id}${d.datum?` · ${d.datum}`:""}`}>${d.name}</td>
              <td class="zahl">${w(d.abstand,0)}</td>
              <td class="zahl">${w(d.gok)}</td>
              <td class="zahl">${w(d.teufe,1)}</td>
              <td class="klein">${kt(d)}</td>
            </tr>`})}
        </tbody>
      </table>
      ${t.treffer.length>r.length?a`<p class="leise klein">… und ${t.treffer.length-r.length} weitere (Umkreis verkleinern)</p>`:c}`:c}
    ${o?a`<button class="primaer" ?disabled=${!O.size} @click=${ft}>
      Ausgewählte übernehmen (${O.size})</button>
      <p class="leise klein">Nur Bohrungen mit Schichtdaten in BoreholeML (NRW, Baden-Württemberg); sie kommen mit Quelle und Lizenz ins Projekt.</p>`:c}
    ${$t(t)}
    ${t.quellen.map(d=>a`<p class="leise klein">Quelle: ${d.namensnennung} · <a href=${d.beleg} target="_blank" rel="noopener">Dienst</a></p>`)}
    <button class="link klein" @click=${async()=>{const d=await z(()=>$.sgdVerwerfen(s.sig));d&&(P(d),p())}}>Abfrage verwerfen</button>`}function Bt(e){const t=s.viewer;t&&(!e.unterlage||e.unterlage.kalibrierung?.gesperrt||!f?t.editor.hilfsmarken({}):t.editor.hilfsmarken({strecke:f.massArt==="strecke"?[f.p1,f.p2]:[],hoehe:f.hoeheArt==="strecke"?[f.h1,f.h2]:[],bezug:f.bezug}))}let Ze=!1;function yt(e){const t=e.standort;return T(a`Standort ${g("standort")}`,a`
    <p class="klein"><b>${w(t.x,1)} / ${w(t.y,1)}</b> · EPSG:${t.epsg}</p>
    <p class="leise klein">Georeferenziert über den Punkt: kein Lageplan, keine Kalibrierung – die Bohrungen der Länder
      kommen mit ihren Koordinaten. Ein Gutachten dazu (Schritt Start) wird ein neues Projekt mit Lageplan.</p>
    ${an(t.dienste)}`)}let qe=!1;function Dt(e){const t=e.viewer.bohrungen.length,n=e.viewer.bohrungen.filter(i=>i.x===null).length;return e.standort?a`<p class="stand-satz ok">Standort ${Math.round(e.standort.x)} / ${Math.round(e.standort.y)} · EPSG:${e.standort.epsg}
      ${t?a` · ${t} Bohrungen der Länder`:a` · <span class="leise">Bohrungen der Länder unten abfragen</span>`}</p>`:t?n?a`<p class="stand-satz warn">${n} von ${t} Bohrungen ohne Lage – auf dem Plan setzen oder Koordinaten eingeben</p>`:a`<p class="stand-satz ok">✓ Alle ${t} Bohrungen haben eine Lage${e.lage_modus==="reihe"?" (Reihe)":""}
      – jetzt mit den Bohrungen der Länder vergleichen</p>`:c}function Gt(){const e=s.z;pn(e),Bt(e);const t=e.lage_modus!=="reihe"&&e.unterlage?.art==="plan"&&!!e.unterlage.kalibrierung?.gesperrt;s.punktModus&&!t&&(s.punktModus=!1),s.viewer?.editor.punktModusSetzen(s.punktModus),Ze||(Ze=!0,window.addEventListener("keydown",r=>{r.key==="Escape"&&s.schritt==="lage"&&s.punktModus&&he(!1)}));const n=e.viewer.bohrungen.length>0&&e.viewer.bohrungen.every(r=>r.x!==null),i=e.lage_modus==="koordinaten"&&n&&!e.unterlage,l=qe||!!(e.gelaende||e.gebaeude);return a`
    <div class="app-panel links">
      ${Dt(e)}
      ${e.standort?yt(e):a`
        ${T(a`Lage der Bohrungen ${g("lage_art")}`,a`
          <div class="umschalter">
            <label><input type="radio" name="lagemodus" .checked=${e.lage_modus==="koordinaten"}
              @change=${()=>m([{op:"lage_modus",wert:"koordinaten"}])}> Koordinaten (Lageplan)</label>
            <label><input type="radio" name="lagemodus" .checked=${e.lage_modus==="reihe"}
              @change=${()=>m([{op:"lage_modus",wert:"reihe"}])}> Reihe (Längsschnitt)</label>
          </div>`)}
        ${T(a`Unterlage ${g("unterlage")}`,lt(e),!i)}
        ${e.unterlage?T(a`Kalibrieren`,st(e)):c}
        ${T(a`Bohrungen setzen`,ot(e),!i)}`}
      ${T(a`Vergleich mit Bohrungen der Länder${e.sgd?.gegenprobe.anzahl?" ✓":""} ${g("sgd")}`,St(e))}
      <details class="erweitert" ?open=${l}
        @toggle=${r=>{qe=r.target.open}}>
        <summary>Erweitert <span class="leise klein">Gelände · Gebäude · Darstellung</span></summary>
        ${T(a`Gelände (DGM)${e.gelaende?.pruefung?.warnungen.length?" ⚠":e.gelaende?" ✓":""} ${g("gelaende")}`,mt(e),!!e.gelaende)}
        ${T(a`Gebäude (LoD2)${e.gebaeude?" ✓":""} ${g("gebaeude")}`,zt(e),!!e.gebaeude)}
        ${T(a`Darstellung`,a`
          <label class="inline">Ø Bohrsäulen ${g("durchmesser")}
            <input type="number" step="0.1" min="0" class="kurz" placeholder=${`auto ${w(e.durchmesser_auto,1)}`}
              .value=${k(e.durchmesser===null?"":String(e.durchmesser))}
              @change=${r=>m([{op:"durchmesser",wert:G(r)}])}> m</label>
          <p class="leise klein">Je Bohrung im Schritt Bohrungen (Ø Säule). Leer = automatisch nach Modellgröße.</p>`,!1)}
      </details>
      ${e.hinweise.length?a`<div class="hinweisliste">${e.hinweise.map(r=>a`<p class="klein">ℹ ${r}</p>`)}</div>`:c}
    </div>`}const F=(e,t=1)=>e==null?"–":e.toLocaleString("de-DE",{minimumFractionDigits:t,maximumFractionDigits:t});let U="",ke=null,Je="",Qe=!1;function Mt(e){return!e||e.quelle!=="DGM"?"aus den GOK der Bohrungen":`aus dem DGM (an den Bohrungen auf die GOK, GOK − DGM bis ${F(Number(e.gok_minus_dgm_max_m),2)} m)`}function Lt(){const e=s.z.einstellungen,t=(r,o)=>m([{op:"einstellungen",[r]:o}]),n=(r,o,d,h,u)=>{const B=e[r];return a`
      <div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${B===null} @change=${v=>t(r,v.target.checked?null:h)}> ${o} automatisch</label>${g(u)}
        ${B===null?c:a`<input type="number" step="any" class="kurz" .value=${k(String(B))}
          @change=${v=>t(r,Number(v.target.value))}> ${d}`}
      </div>`},i=s.modell?.bericht?.parameter??{},l=e.methode!=="idw"||e.puffer!==null||e.raster!==null||e.basis!==null||!e.gok_relativ||!e.gelaende_dgm;return a`
    <details class="erweitert karte" ?open=${Qe||l}
      @toggle=${r=>{Qe=r.target.open}}>
      <summary>Erweitert <span class="leise klein">Interpolation · Puffer · Raster · Basis · Gelände</span></summary>
      <div class="einstellung">
        <span>Interpolation ${g("methode")}</span>
        <label class="inline"><input type="radio" name="methode" .checked=${e.methode==="idw"} @change=${()=>t("methode","idw")}> IDW</label>
        <label class="inline"><input type="radio" name="methode" .checked=${e.methode==="tps"} @change=${()=>t("methode","tps")}> Dünnplatten-Spline</label>
      </div>
      ${n("puffer","Puffer","m",Number(i.puffer_m??20),"puffer")}
      ${n("raster","Raster","m",Number(i.raster_m??5),"raster")}
      ${n("basis","Modellbasis","m NHN",Math.floor(Number(i.basis_nhn??0)),"basis")}
      <div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${e.gok_relativ} @change=${r=>t("gok_relativ",r.target.checked)}> fehlende GOK: Gelände = 0 m</label>${g("gok_relativ")}
      </div>
      ${s.z.gelaende?a`<div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${e.gelaende_dgm} @change=${r=>t("gelaende_dgm",r.target.checked)}> Gelände aus dem DGM</label>${g("gelaende_dgm")}
      </div>`:c}
      ${i.raster_m!==void 0?a`<p class="leise klein">gerechnet: Puffer ${F(Number(i.puffer_m),0)} m · Raster ${F(Number(i.raster_m))} m ·
        Basis ${F(Number(i.basis_nhn),2)} m NHN · Fläche ${F(Number(i.flaeche_m2)/1e4,2)} ha ·
        Gelände ${Mt(i.gelaende)}</p>`:c}
    </details>`}function xt(){const e=s.modell?.bericht;if(!e)return c;const t=s.z.vorgabe??e.vorlage_einheiten,n=JSON.stringify(t);(!ke||Je!==n)&&(ke=t.map(r=>({name:r.name,bodenarten:r.bodenarten.join(", ")})),Je=n);const i=ke,l=()=>m([{op:"vorgabe",wert:i.filter(r=>r.name.trim()).map(r=>({name:r.name.trim(),bodenarten:r.bodenarten.split(",").map(o=>o.trim()).filter(Boolean)}))}]);return a`
    <section class="karte">
      <h3>Einheiten festlegen ${g("einheiten")}</h3>
      <p class="leise klein">${s.z.vorgabe?"Vorgegeben (eigene Einheiten).":"Automatisch korreliert – hier umbenennen oder Bodenarten zusammenlegen."}</p>
      <table class="tabelle kompakt vorgabe">
        <colgroup><col class="pfeil"><col><col><col class="weg"></colgroup>
        <thead><tr><th></th><th>Einheit</th><th>Bodenarten (mit Komma)</th><th></th></tr></thead>
        <tbody>
          ${i.map((r,o)=>a`
            <tr>
              <td class="pfeile"><button class="symbol" ?disabled=${o===0} @click=${()=>{i.splice(o-1,0,...i.splice(o,1)),p()}}>▲</button><button
                class="symbol" ?disabled=${o===i.length-1} @click=${()=>{i.splice(o+1,0,...i.splice(o,1)),p()}}>▼</button></td>
              <td><input .value=${k(r.name)} @input=${d=>{r.name=d.target.value}}></td>
              <td><input .value=${k(r.bodenarten)} @input=${d=>{r.bodenarten=d.target.value}}></td>
              <td><button class="symbol" title="Zeile löschen" @click=${()=>{i.splice(o,1),p()}}>✕</button></td>
            </tr>`)}
        </tbody>
      </table>
      <div class="zeile knopfzeile">
        <button class="link" @click=${()=>{i.push({name:"",bodenarten:""}),p()}}>+ Zeile</button>
        <span class="fueller"></span>
        <button ?disabled=${!s.z.vorgabe} @click=${()=>m([{op:"vorgabe",wert:null}])}>Automatisch korrelieren</button>
        <button class="primaer" @click=${l}>Mit diesen Einheiten rechnen</button>
      </div>
    </section>`}function _t(){const e=s.modell,t=e?.bericht,n=t?.einheiten.find(i=>i.name===U);return a`
    <div class="schritt-einheiten">
      <div class="spalte">
        ${xt()}
        ${Lt()}
      </div>
      <div class="spalte breit">
        ${s.rechnet?a`<div class="karte"><div class="kreisel klein"></div> Modell wird gerechnet …</div>`:c}
        ${e?.fehler?a`<div class="karte warnung">Noch kein Modell: ${e.fehler}
          <button class="link" @click=${()=>R("lage")}>→ Lage setzen</button></div>`:c}
        ${t?a`
          <section class="karte">
            <h3>Einheiten (${t.einheiten.length})</h3>
            <table class="tabelle einheiten">
              <thead><tr><th></th><th>Einheit</th><th>Bodenarten</th><th>Volumen [m³]</th><th>max. Mächtigkeit [m]</th>
                <th title="in Bohrungen vorhanden / fehlt / unter der Endteufe">✓ / – / ?</th><th>Hinweise</th></tr></thead>
              <tbody>
                ${t.einheiten.map(i=>a`
                  <tr class=${i.name===U?"gewaehlt":""} @click=${()=>{U=U===i.name?"":i.name,p()}}>
                    <td><span class="farbfeld" style=${`background:${i.farbe}`}></span></td>
                    <td><b>${i.name}</b></td>
                    <td>${i.bodenarten.join(", ")}</td>
                    <td class="zahl">${Math.round(i.volumen_m3).toLocaleString("de-DE")}</td>
                    <td class="zahl">${F(i.maechtigkeit_max_m,2)}</td>
                    <td class="zahl">${i.bohrungen.vorhanden.length} / ${i.bohrungen.fehlt.length} / ${i.bohrungen.unbekannt.length}</td>
                    <td class="klein">${i.hinweise.join("; ")}</td>
                  </tr>`)}
              </tbody>
            </table>
          </section>
          <section class="karte profil-karte">
            <h3>Einheiten je Bohrung <span class="leise klein">(m NHN, Klick wählt die Einheit)</span></h3>
            <div class="profil-scroll">${Fn(t,{hoehe:380,gewaehlt:U,waehlen:i=>{U=i,p()}})}</div>
          </section>
          ${n?a`
            <section class="karte">
              <h3><span class="farbfeld" style=${`background:${n.farbe}`}></span> ${n.name}: Beschreibungen aus dem PDF</h3>
              <table class="tabelle kompakt">
                <thead><tr><th>Bohrung</th><th>Tiefe [m]</th><th>Bodenart</th><th>Beschreibung</th></tr></thead>
                <tbody>${n.schichten.map(i=>a`
                  <tr><td>${i.bohrung}</td><td class="zahl">${F(i.von,2)}–${F(i.bis,2)}</td><td>${i.bodenart??"unklassifiziert"}</td>
                    <td>${i.beschreibung||a`<span class="leise">–</span>`}</td></tr>`)}</tbody>
              </table>
            </section>`:c}`:c}
      </div>
    </div>`}let ge="";async function Pt(){const e=await z(()=>$.einchecken(s.sig,ge));e&&(P(e.zustand),ge="",D(`Eingecheckt: v${e.eintrag.nr} · ${e.eintrag.stand.bohrungen[0]}/${e.eintrag.stand.bohrungen[1]} Bohrungen geprüft`,"ok"),p())}const mn=new Set([25831,25832,25833,4647,5650]);let Q=(()=>{try{return localStorage.getItem("groundtwin.organisation")??""}catch{return""}})();function Et(){const e=s.z,t=e.bohrungen.filter(l=>l.modell),n=t.filter(l=>l.schichten_n>0&&l.schichten_geprueft===l.schichten_n&&l.x!==null&&l.y!==null&&l.epsg!==null&&mn.has(l.epsg)&&l.gok!==null&&e.lage_modus==="koordinaten"),i=`${$.exportUrl(s.sig,"boreholeml")}?organisation=${encodeURIComponent(Q)}`;return a`
    <label class="feld breit"><span>Organisation (Absender) ${g("boreholeml")}</span>
      <input type="text" aria-label="Organisation für BoreholeML" placeholder="z. B. Ingenieurbüro …" .value=${Q}
        @input=${l=>{Q=l.target.value;try{localStorage.setItem("groundtwin.organisation",Q)}catch{}p()}}></label>
    ${n.length?a`<a class="knopf" href=${i} download>Bohrungen für den Geologischen Dienst (BoreholeML 3.2)</a>`:a`<span class="knopf aus" title="Erst alle Schichten prüfen; Lage in ETRS89/UTM und GOK nötig">Bohrungen für den Geologischen Dienst (BoreholeML 3.2)</span>`}
    <p class="leise klein">${n.length} von ${t.length} Bohrungen exportierbar (vollständig geprüft, ETRS89/UTM, GOK).</p>`}let ee=!1;async function At(){if(!ee){ee=!0,p();try{const e=await fetch($.exportUrl(s.sig,"3dtiles"));if(!e.ok){const i=await e.text();let l=i;try{l=JSON.parse(i).detail??i}catch{}D(`3D Tiles: ${l}`,"fehler",1e4);return}const t=/filename\*=UTF-8''([^;]+)/.exec(e.headers.get("content-disposition")??"")?.[1],n=document.createElement("a");n.href=URL.createObjectURL(await e.blob()),n.download=t?decodeURIComponent(t):"baugrundmodell_3dtiles.zip",n.click(),setTimeout(()=>URL.revokeObjectURL(n.href),1e4),D("3D Tiles exportiert (tileset.json + GLB, Höhen ellipsoidisch mit GCG2016).","ok")}finally{ee=!1,p()}}}function Nt(){const e=s.z;return e.lage_modus==="koordinaten"&&e.viewer.epsg!==null&&mn.has(e.viewer.epsg)?a`<button class="knopf" ?disabled=${ee} @click=${At}>${ee?"3D Tiles werden erstellt …":"Baugrundmodell für Cesium (3D Tiles, ZIP)"}</button>${g("tiles3d")}`:a`<span class="knopf aus" title="Nur mit Lage nach Koordinaten in ETRS89/UTM">Baugrundmodell für Cesium (3D Tiles, ZIP)</span>`}const Kt={anzeige:"Anzeige",fachdaten:"Fachdaten",bewertungsdaten:"Bewertungsdaten"},Tt=e=>e.split("-").reverse().join(".");function Rt(e){return!e.bis||e.tage===null?e.regel:`bis ${Tt(e.bis)} (${e.tage>0?`noch ${e.tage} Tage`:e.tage===0?"heute":"verstrichen"})`}function Ot(){const e=s.z.geoldg,t=e.zusammenfassung,n=(r,o)=>m([{op:"geoldg",[r]:o}],{leise:!0}),i=`${$.exportUrl(s.sig,"geoldg")}?organisation=${encodeURIComponent(Q)}`,l=e.punkte.filter(r=>r.quelle==="protokoll").map(r=>r.titel.replace(/, falls durchgeführt$/,""));return a`
    <section class="abschnitt-flach geoldg">
      <h3>Geologischer Dienst (GeolDG) ${g("geoldg")}</h3>
      <div class="zeile">
        <label class="inline">Beginn <input type="date" aria-label="Beginn der Untersuchung" .value=${e.angaben.beginn}
          @change=${r=>n("beginn",r.target.value)}></label>
        <label class="inline">Abschluss <input type="date" aria-label="Abschluss der Untersuchung" .value=${e.angaben.abschluss}
          @change=${r=>n("abschluss",r.target.value)}></label>${g("geoldg_abschluss")}
      </div>
      <label class="inline"><input type="checkbox" aria-label="Auftraggeber ist eine Behörde" .checked=${e.angaben.behoerde}
        @change=${r=>n("behoerde",r.target.checked)}> Auftraggeber ist eine Behörde</label>
      <ul class="fristen">${e.fristen.map(r=>a`
        <li class=${r.tage!==null&&r.tage<0?"warn":""} data-frist=${r.id}><b>${Kt[r.id]}</b>
          <a href=${r.url} target="_blank" rel="noopener">${r.beleg}</a>: ${Rt(r)}</li>`)}</ul>
      ${e.vorerkundung?a`
        <p class="klein">Noch keine eigene Bohrung: die geplante Erkundung spätestens zwei Wochen vor Beginn anzeigen
          (<a href=${e.anzeige_inhalt.url} target="_blank" rel="noopener">§ 8</a>). ${e.anzeige_inhalt.aus_der_app}</p>`:t.eigene?a`
        <p class="klein geoldg-stand">${t.eigene} eigene Bohrungen: für <b>${t.bereit}</b> liefert GroundTwin Lage, GOK, Endteufe
          und das geprüfte Schichtenverzeichnis, <b>${t.boreholeml}</b> davon im BoreholeML.${t.fremd?` ${t.fremd} Bohrungen der Länder liegen dem Land schon vor.`:""}</p>
        ${t.offen.length?a`<details class="protokoll"><summary class="warnung">⚠ ${t.offen.length} Bohrung(en) offen</summary>
          <ul>${t.offen.map(r=>a`<li><b>${r.code}</b>: ${r.was}</li>`)}</ul></details>`:c}
        <p class="klein leise">Aus dem Bohrprotokoll ergänzen (Spalten in pruefliste.csv): ${l.join(" · ")}.</p>
        <a class="knopf" href=${i} download>Paket für den Geologischen Dienst (ZIP)</a>`:c}
      <p class="leise klein">${e.quelle.hinweis}</p>
    </section>`}let Ye=!1;function Ft(){const e=s.z,t=s.modell,n=t?.bericht,i=e.pruefstand,l=e.eincheckungen[e.eincheckungen.length-1],r=[["ifc","Baugrundmodell (IFC 4.3)"],["bericht","Prüfbericht (JSON)"]],o=[["einheiten","Einheiten-Vorlage (JSON)"],["extraktion","Extraktion (JSON)"],["eingabe","Modell-Eingabe mit Korrekturen (JSON)"],["projekt","Projektstand (JSON)"]],d=Ye||!!(e.geoldg?.angaben.beginn||e.geoldg?.angaben.abschluss);return a`
    <div class="app-panel rechts">
      <section class="abschnitt-flach">
        <h3>Modell</h3>
        ${e.reifegrad.stufe!=="Gutachten"?a`<p class=${`reife ${e.reifegrad.stufe==="Vorerkundung"?"vorerkundung":"gemischt"}`}>
          <b>${e.reifegrad.stufe}</b> – ${e.reifegrad.stufe==="Vorerkundung"?"Bohrungen aus Datenbanken der Länder, kein Gutachten: eine erste Vorstellung für die Planung der Erkundung.":Object.entries(e.reifegrad.anzahl).map(([h,u])=>`${u} ${h}`).join(", ")+": Bohrungen ohne Gutachten sind nicht gegen ein PDF geprüft."}
          ${g("reifegrad")}</p>`:c}
        ${s.rechnet?a`<p><span class="kreisel klein"></span> wird gerechnet …</p>`:c}
        ${t?.fehler?a`<p class="warnung">Noch kein Modell: ${t.fehler}</p>
          <button class="link" @click=${()=>R("lage")}>→ Lage setzen</button>`:c}
        ${n?a`
          <ul class="kennzahlen">
            <li><b>${n.einheiten.length}</b> Einheiten</li>
            <li><b>${n.bohrungen.length}</b> Bohrungen im Modell</li>
            <li class=${n.epsg?"":"warn"}>${n.epsg?`EPSG:${n.epsg}`:"lokales System"}</li>
            <li class=${n.pruefungen.alle_koerper_geschlossen?"ok":"warn"}>${n.pruefungen.alle_koerper_geschlossen?"Körper geschlossen":"Körper offen"}</li>
            <li class=${n.pruefungen.max_abweichung_an_bohrungen_m<.01?"ok":"warn"}>Abweichung an Bohrungen ${n.pruefungen.max_abweichung_an_bohrungen_m.toFixed(3)} m</li>
          </ul>`:c}
        <div class="zeile">
          <label class="inline"><input type="checkbox" .checked=${e.auto} @change=${h=>m([{op:"auto",wert:h.target.checked}],{leise:!0})}>
            automatisch nachführen</label>${g("auto")}
          <span class="fueller"></span>
          <button ?disabled=${s.rechnet} @click=${()=>kn()}>Neu rechnen</button>
        </div>
      </section>

      <section class="abschnitt-flach">
        <h3>Prüfstand ${g("pruefstand")}</h3>
        <div class="balken"><span>Bohrungen <b>${i.bohrungen[0]}/${i.bohrungen[1]}</b></span><progress max=${i.bohrungen[1]||1} value=${i.bohrungen[0]}></progress></div>
        <div class="balken"><span>Schichten <b>${i.schichten[0]}/${i.schichten[1]}</b></span><progress max=${i.schichten[1]||1} value=${i.schichten[0]}></progress></div>
        <p class="klein">${i.unklassifiziert_offen?a`<span class="warnung">⚠ ${i.unklassifiziert_offen} Schicht(en) nicht klassifiziert</span>
          <button class="link" @click=${()=>R("bohrungen")}>prüfen</button>`:a`<span class="ok">✓ keine offenen Warnungen</span>`}
          · ${i.korrigiert} korrigiert · ${i.manuelle_lage} Lagen manuell · ${i.entfernt} entfernt</p>
        <p class=${`klein ${l&&!e.seit_einchecken_geaendert?"ok":"warn"}`}>
          ${l?`Eingecheckt: ${e.eingecheckt}${e.seit_einchecken_geaendert?" · seitdem geändert":""}`:"noch nicht eingecheckt"}</p>
        <div class="zeile">
          <input class="breit" placeholder="Kommentar (z. B. BK1–BK5 mit Anlage 2 verglichen)" .value=${ge}
            @input=${h=>{ge=h.target.value}}>
        </div>
        <div class="zeile"><button class="primaer" @click=${Pt}>✓ Stand einchecken</button>${g("einchecken")}</div>
        ${e.eincheckungen.length?a`
          <details class="protokoll"><summary>Protokoll (${e.eincheckungen.length})</summary>
            <ul>${[...e.eincheckungen].reverse().map(h=>a`
              <li><b>v${h.nr}</b> ${h.zeit} · ${h.stand.bohrungen[0]}/${h.stand.bohrungen[1]} Bohrungen, ${h.stand.schichten[0]}/${h.stand.schichten[1]} Schichten
                ${h.kommentar?a`<div class="leise klein">${h.kommentar}</div>`:c}</li>`)}</ul>
          </details>`:c}
      </section>

      <section class="abschnitt-flach">
        <h3>Export ${g("export")}</h3>
        <div class="export-liste">
          ${r.map(([h,u])=>a`<a class=${`knopf ${h==="ifc"?"primaer":""}`} href=${$.exportUrl(s.sig,h)}
            download>${u}</a>`)}
        </div>
      </section>

      <details class="erweitert" ?open=${d}
        @toggle=${h=>{Ye=h.target.open}}>
        <summary>Erweitert <span class="leise klein">Exporte · Cesium · BoreholeML · GeolDG · Darstellung</span></summary>
        <section class="abschnitt-flach">
          <h3>Weitere Exporte</h3>
          <div class="export-liste">
            ${o.map(([h,u])=>a`<a class="knopf" href=${$.exportUrl(s.sig,h)} download>${u}</a>`)}
            ${Nt()}
            ${Et()}
          </div>
        </section>
        ${Ot()}
        <section class="abschnitt-flach">
          <h3>Darstellung</h3>
          <label class="inline">Überhöhung ${g("ueberhoehung")}
            <select @change=${async h=>{const u=Number(h.target.value);await s.viewer?.ueberhoehen(u),await m([{op:"ueberhoehung",wert:u}],{leise:!0})}}>
              ${[1,2,5,10,20].map(h=>a`<option value=${h} .selected=${e.ueberhoehung===h}>${h}×</option>`)}
            </select></label>
        </section>
      </details>

      ${t&&(t.hinweise.length||t.nicht_im_modell.length)?a`
        <section class="abschnitt-flach">
          <h3>Hinweise</h3>
          ${t.nicht_im_modell.length?a`<p class="klein"><b>Nicht im Modell:</b> ${t.nicht_im_modell.map(h=>`${h.code} (${h.grund})`).join(", ")}</p>`:c}
          ${t.hinweise.map(h=>a`<p class="klein">ℹ ${h}</p>`)}
        </section>`:c}
    </div>`}const Xe={gutachten:"",bohrungen:"Weiter: Lage",lage:"Weiter: Einheiten",einheiten:"Weiter: Modell",modell:""};function jt(e){const t=s.z;if(!t)return"";const n=t.pruefstand;return e==="gutachten"?"ok":e==="bohrungen"?n.unklassifiziert_offen?"warn":n.bohrungen[0]===n.bohrungen[1]&&n.bohrungen[1]?"ok":"":e==="lage"?t.viewer.bohrungen.filter(l=>l.x===null).length?"warn":"ok":e==="einheiten"||e==="modell"?s.modell?.fehler?"warn":s.modell?.bericht?"ok":"":""}function Ht(){const e=s.z;return a`
    <header class="kopf">
      <div class="marke" @click=${()=>R("gutachten")} title="Start">
        <span class="logo">⛰</span>
        <span><b>GroundTwin</b> · Baugrundmodell</span>
      </div>
      <nav class="schritte" aria-label="Schritte">
        ${re.map(t=>{const n=t.id!=="gutachten"&&!e,i=jt(t.id);return a`
            <button class=${`schritt-knopf ${s.schritt===t.id?"aktiv":""} ${i}`} ?disabled=${n}
              aria-current=${s.schritt===t.id?"step":"false"} @click=${()=>R(t.id)} title=${t.kurz}>
              <span class="nr">${i==="ok"&&s.schritt!==t.id?"✓":i==="warn"?"!":t.nr}</span>
              <span class="titel">${t.titel}</span>
            </button>`})}
      </nav>
      <div class="projekt">
        ${e&&e.reifegrad.stufe!=="Gutachten"?a`<span class=${`abzeichen ${e.reifegrad.stufe==="Vorerkundung"?"vorerkundung":"gemischt"}`}
          title=${e.reifegrad.stufe==="Vorerkundung"?"Bohrungen aus Datenbanken der Länder, kein Gutachten":"Gutachten und Bohrungen der Länder"}>${e.reifegrad.stufe}</span>`:c}
        ${e?a`<span class="projektname" title=${e.dokumente.map(t=>t.datei).join(", ")}>${e.name}</span>
          <details class="menue">
            <summary title="Projekt">⋯</summary>
            <div class="menue-inhalt" @click=${It}>
              <button @click=${()=>R("gutachten")}>Anderes Projekt öffnen</button>
              <button @click=${Ut}>Alle Korrekturen verwerfen …</button>
              <a href="viewer.html" target="_blank" rel="noopener">Viewer allein öffnen</a>
              <a href="dienste.html" target="_blank" rel="noopener">Dienste der Länder (Werkzeug)</a>
              ${s.info?a`<a href=${s.info.quellcode} target="_blank" rel="noopener">Quellcode (${s.info.lizenz})</a>`:c}
            </div>
          </details>`:c}
      </div>
    </header>`}function It(e){e.currentTarget.closest("details")?.removeAttribute("open")}document.addEventListener("click",e=>{for(const t of document.querySelectorAll("details.menue[open]"))t.contains(e.target)||t.removeAttribute("open")});async function Ut(){if(!s.sig||!confirm("Alle Korrekturen, Lagen, Prüfhaken und Eincheckungen dieses Projekts verwerfen – auch übernommene Bohrungen der Länder, DGM und Gebäude? Der Name bleibt."))return;const e=await z(()=>$.zuruecksetzen(s.sig));e&&await V(s.sig,e.standort?"lage":"bohrungen")}function Wt(){if(s.schritt==="gutachten")return c;const e=re.findIndex(l=>l.id===s.schritt),t=re[e-1],n=re[e+1],i=s.z?.pruefstand;return a`
    <footer class="fuss">
      ${t?a`<button @click=${()=>R(t.id)}>← ${t.titel}</button>`:c}
      <span class="fuss-status">${i?`${i.bohrungen[0]}/${i.bohrungen[1]} Bohrungen · ${i.schichten[0]}/${i.schichten[1]} Schichten geprüft`:""}
        ${i?.unklassifiziert_offen?a` · <span class="warnung">⚠ ${i.unklassifiziert_offen} nicht klassifiziert</span>`:c}</span>
      <span class="fueller"></span>
      ${n&&Xe[s.schritt]?a`<button class="primaer" @click=${()=>R(n.id)}>${Xe[s.schritt]} →</button>`:c}
    </footer>`}function Ct(){return s.schritt==="gutachten"||!s.z?Kn():s.schritt==="bohrungen"?et():s.schritt==="lage"?Gt():s.schritt==="einheiten"?_t():Ft()}function Vt(){return a`
    ${Ht()}
    <main class=${`inhalt schritt-${s.schritt}`}>
      <section id="schritt" class="schritt">${Ct()}</section>
    </main>
    ${Wt()}
    <div class="meldungen" aria-live="polite">
      ${s.meldungen.map(e=>a`<div class=${`meldung ${e.art}`}>${e.text}</div>`)}
    </div>
    ${s.beschaeftigt?a`<div class="beschaeftigt"><div class="kreisel"></div><span>${s.beschaeftigt}</span></div>`:c}`}const en=document.getElementById("app");let W=null;function Zt(){fn(Vt(),en);const e=en.querySelector("main");W||(W=document.createElement("div"),W.id="buehne",W.className="buehne"),W.parentElement!==e&&e.append(W),document.body.dataset.schritt=s.schritt}wn(Zt);async function bn(){const[e,t,n]=location.hash.replace(/^#\/?/,"").split("/").map(decodeURIComponent);if(e&&e!==s.sig){if(await V(e,t||void 0),n&&s.schritt==="bohrungen"){const{bohrungWaehlen:i}=await we(async()=>{const{bohrungWaehlen:l}=await import("./store-BPmb1nGN.js").then(r=>r.k);return{bohrungWaehlen:l}},__vite__mapDeps([1,2]),import.meta.url);await i(n)}}else e||await R("gutachten")}window.addEventListener("hashchange",()=>void bn());s.info=await z(()=>$.info())??null;p();await nn();await bn();window.app=s;
