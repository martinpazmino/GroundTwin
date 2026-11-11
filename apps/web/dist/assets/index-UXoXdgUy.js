const __vite__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["./leaflet-CIGW-MKW.css","./store-BxtDZSAk.js","./preload-helper-Ct5FWWRu.js"])))=>i.map(i=>d[i]);
import"./viewer-Czjhv0Od.js";import{_ as De}from"./preload-helper-Ct5FWWRu.js";/* empty css            */import{b as a,A as u,w as W,D as xn}from"./lit-element-BS0sz3Y2.js";import{a as f,S as l,n as p,v as w,m as D,o as J,p as dn,s as le,b as we,c as Ae,d as m,z as P,e as ve,f as Nn,g as j,h as En,i as Pn,j as ce}from"./store-BxtDZSAk.js";import{l as k,m as An,k as je}from"./lage-dDtwcw43.js";import"./three.core-Dd2BBCN2.js";const hn=a`<span class="ungeprueft" title="Adresse eingetragen, nicht gegen den Dienst geprüft">ungeprüft</span>`;function gn(e,n="Dienste am Standort"){return a`<ul class="dienste klein" aria-label=${n}>${e.map(t=>a`<li class=${t.art}>
    ${t.url?a`<a href=${t.url} target="_blank" rel="noopener noreferrer">${t.text}</a>`:t.text}
    ${t.status==="ungeprueft"?hn:u}</li>`)}</ul>`}function Kn(e){if(!e?.length)return u;const n=[...new Set(e.map(t=>t.land).filter(t=>t!=="Deutschland"))];return a`<div class="portale" role="note">
    <p class="klein">Kein Datendienst mit Schichtdaten für ${n.length?n.join(", "):"diesen Ort"} – die Bohrungen im Portal ansehen:</p>
    <ul class="dienste klein" aria-label="Portale der Länder">${e.map(t=>a`<li>
      <a href=${t.url} target="_blank" rel="noopener noreferrer">${t.titel}</a> <span class="leise">(${t.land})</span>
      ${t.status==="ungeprueft"?hn:u}
      ${t.hinweis?a`<div class="leise">${t.hinweis}</div>`:u}</li>`)}</ul>
  </div>`}const Me={ocr:["OCR für Scans","Liest gescannte PDFs und Text, der nur als Linien gezeichnet ist (SHX). Langsamer; bei Vektor-PDFs nicht nötig."],beispiele:["Beispiele","Fertig ausgewertete Gutachten zum Ausprobieren. Echte Daten: Berlin (georeferenziert) und Talheim (ohne Koordinaten). Dazu Standorte ohne Gutachten, die zeigen, was die Länder liefern: Dortmund (NRW, Bohrungen mit Schichtdaten), Karlsruhe (Baden-Württemberg, Schichten oft ohne Petrographie) und Berlin (nur Kopfdaten: Gelände und Gebäude, kein Schichtenmodell). Die Bohrungen fragt der Schritt Lage auf Klick beim Land ab (Netz nötig)."],karte:["Karte","Eine Karte zum Orientieren: ein Klick setzt den Standort; Rechts- und Hochwert in ETRS89/UTM rechnet die App aus (Zone 32 westlich von 12° Ost, sonst 33) und sagt, was die Dienste der Länder dort liefern. Hintergrund basemap.de (amtlich, © GeoBasis-DE / BKG, CC BY 4.0) oder OpenStreetMap. Die Kacheln laden erst beim Öffnen – der Kartenausschnitt geht an diesen Server. Auf wenige Meter genau (Karte in WGS84): für eine Vorerkundung genug."],pruefstand:["Prüfstand","Wie viele Bohrungen und Schichten Sie geprüft haben. Eine Korrektur zählt als geprüft. Der Stand wird beim Einchecken festgehalten."],alle_pruefen:["Alle geprüft","Markiert alle Schichten aller Bohrungen im Modell als geprüft – nur wenn Sie alles mit dem Gutachten verglichen haben. Zurücknehmen ist jederzeit möglich."],warnung:["Warnung","Eine Schicht, deren Bodenart nicht erkannt wurde (unklassifiziert). Bodenart wählen, den Vorschlag nach Norm übernehmen oder die Schicht als geprüft markieren."],bodenart:["Bodenart","Klasse für das Modell; Farbe nach DIN 4023 (Kies gelb, Sand orange, Schluff oliv, Ton violett …). Gleiche Bodenarten werden zu Einheiten verbunden."],norm:["Deutung nach Norm","Die Beschreibung aus dem PDF gelesen nach DIN 4023 / DIN EN ISO 14688-1: Hauptanteil, Nebenanteile (schwach ' / stark ¯), Kurzzeichen, Bodengruppe nach DIN 18196 (nur wenn genannt), Konsistenz. Steht auch im IFC (CPset_Bodenansprache)."],vorschlag:["Vorschlag nach Norm","Für eine unklassifizierte Schicht schlägt die Normen-Datenbank eine Bodenart aus der Beschreibung vor. Sie wird nur übernommen, wenn Sie klicken; danach gilt die Schicht als korrigiert."],geprueft:["Geprüft","Haken: Schicht mit dem Gutachten verglichen. Steht im IFC (Geprueft) und im Prüfstand."],tiefe:["Tiefe","Ober- und Unterkante in m unter Geländeoberkante (GOK). Geändertes wird als korrigiert markiert."],gok:["GOK","Ansatzhöhe der Bohrung in m NHN. Aus dem PDF oder hier eingetragen (manuell). Ohne GOK bei allen Bohrungen rechnet das Modell relativ (Gelände = 0 m)."],koordinaten:["Koordinaten","Rechts- und Hochwert der Bohrung; leer lassen, wenn die Lage im Schritt Lage auf dem Plan gesetzt wird."],entfernen:["Entfernen","Die Bohrung kommt nicht ins Modell (sie bleibt in der Liste unter „Entfernt“ und lässt sich wiederherstellen)."],quelle:["Quelle im PDF","Die Seite des Gutachtens, auf der die Bohrung erkannt wurde; der Rahmen zeigt die gewählte Schicht."],lage_art:["Art der Lage","Koordinaten: Bohrungen mit Rechts-/Hochwert (aus dem PDF, eingetragen oder auf dem Lageplan gesetzt). Reihe: ohne Koordinaten nebeneinander mit Abständen bzw. Stationen aus dem Längsschnitt."],unterlage:["Unterlage","Lageplan (Draufsicht) oder Längsschnitt (Seitenansicht) als PDF. Er liegt im Viewer unter den Bohrungen; nach dem Kalibrieren werden die Bohrungen daraufgezogen."],massstab:["Maßstab","Zwei Punkte auf dem Plan anklicken, deren Abstand Sie kennen (Maßstabsleiste, Bemaßung, zwei Bohrungen), und die wahre Länge in m eintragen. Oder den Maßstab 1:n direkt angeben."],bezug:["Bezugspunkt","Ein Punkt im Plan mit bekannter Koordinate (Koordinatenkreuz, Bohrung mit Koordinaten): anklicken und Rechts-/Hochwert eintragen – im Längsschnitt Station und Höhe NHN."],drehung:["Drehung","Winkel, um den der Plan gegen Norden gedreht ist (gegen den Uhrzeigersinn positiv). Nordpfeil nach oben = 0°; Nordpfeil 10° nach links geneigt = 10°."],hoehe:["Höhenmaßstab","Längsschnitte sind oft überhöht (z. B. Länge 1:500, Höhe 1:100). Ohne Angabe gilt der Längenmaßstab."],epsg:["Koordinatensystem (EPSG)","System der Rechts-/Hochwerte aus der Liste wählen: in Deutschland meist ETRS89 / UTM 32N (25832), im Osten 33N (25833), ältere Pläne Gauß-Krüger (Rechtswert 7-stellig, erste Ziffer = Zone); dazu Schweiz und Österreich. Passen die Werte nicht zum System (Ziffernzahl, Zonenkennung), erscheint ein Hinweis. Steht im IFC (IfcMapConversion)."],sperren:["Sperren","Schloss zu: der Plan liegt fest und ändert sich nicht mehr; jetzt die Bohrungen ziehen. Auf dem Lageplan nur in x/y, im Längsschnitt entlang der Station – in der Höhe nur, wenn das PDF keine GOK hat."],deckkraft:["Deckkraft","Wie stark der Plan die Szene überdeckt."],ohne_lage:["Ohne Lage","Bohrungen ohne Koordinaten: anklicken und dann in den gesperrten Plan klicken (Punkte setzen) – oder mit der Maus aus der Liste auf den Plan ziehen."],punkte:["Punkte setzen","Modus an, dann in den gesperrten Lageplan klicken: die gewählte Bohrung bekommt die Lage, danach ist die nächste ohne Lage dran (oder einen Chip anklicken). Mit „freien Punkt“ entsteht ein Punkt ◆, den Sie in der Liste einer Bohrung zuordnen. ✕ löscht einen Punkt bzw. die gesetzte Lage – im Viewer ebenso: Marke anklicken, Entf. Esc beendet den Modus."],reihe:["Reihe","Bohrungen in einer Linie. Abstand zum Vorgänger je Bohrung eintragen (BK1 → BK2 10 m, BK2 → BK3 15 m) oder eine Station; ohne Eintrag gilt der Standardabstand. Reihenfolge mit den Pfeilen."],standardabstand:["Standardabstand","Abstand zwischen Bohrungen, für die nichts eingetragen ist (nur zur Anschauung, im Modell als schematisch markiert)."],boreholeml:["BoreholeML","Austauschformat der Geologischen Dienste der Länder (Version 3.2). Exportiert werden nur vollständig geprüfte Bohrungen mit Lage in ETRS89/UTM und GOK in m NHN; Petrographie, Genese, Konsistenz, Lagerung, Kalk und Feuchte über die amtlichen Codelisten, die Beschreibung aus dem Gutachten im Klartext. Die Organisation steht als Absender in der Datei. Welche Bohrungen ausgelassen wurden und warum, steht oben in der Datei. Umgekehrt lassen sich BoreholeML-Dateien wie ein Gutachten hochladen (Bohrungen der Länder)."],sgd:["Bohrungen der Länder","Bohrungen aus den Datenbanken der Geologischen Dienste um die Mitte des Projekts: Berlin und Brandenburg mit Kopfdaten und dem Schichtenverzeichnis als Grafik, NRW, Baden-Württemberg und Hamburg in BoreholeML mit den freigegebenen Schichtdaten. Abgefragt wird nur auf Klick – die Anfrage sendet die Lage des Projekts an den Dienst. Bohrungen des Gutachtens, die auch beim Land liegen, zeigen die Abweichung von Lage und GOK (Gegenprobe). Übernommene Bohrungen tragen Quelle, Lizenz und Datum, erscheinen als Raute und gehen nicht in den BoreholeML-Export. Für Länder ohne eigenen Dienst zeigen die BGR und Bremen über WMS, wo gebohrt wurde: nur als Hinweis mit Lage, GOK und Teufe, nie im Modell. Länder ohne Datendienst nennt die Abfrage außerdem mit dem Link zu ihrem Portal und der Bohrpunktkarte der BGR („ungeprüft“: Adresse eingetragen, nicht gegen den Dienst getestet). Welches Land: aus den Ländergrenzen (VG2500 des BKG); an einer Grenze beide. Die Adressen pflegt das Werkzeug „Dienste der Länder“ (Menü ⋯)."],gelaende:["Gelände (DGM)","Digitales Geländemodell der Vermessungsverwaltung (Open Data, meist DGM1 mit 1 m Raster) für das Baufeld herunterladen und hier laden: XYZ, ASCII-Raster oder GeoTIFF, mehrere Kacheln auch als ZIP. Die App vergleicht die GOK aus dem PDF mit dem Gelände: liegen alle Bohrungen gleich viel höher oder tiefer, stimmen Lage, EPSG oder Höhenbezug nicht. Fehlende GOK schlägt sie vor – übernommen wird nur auf Klick, markiert als „DGM“ (auch im IFC)."],dgm_land:["DGM vom Land","Holt das DGM1 (1 m) für den Ausschnitt um die Bohrungen plus Rand direkt beim Dienst des Landes (WCS): bisher Brandenburg mit Berlin und NRW. Nur auf Klick – die Anfrage sendet den Ausschnitt an den Dienst. Quelle, Lizenz und Namensnennung bleiben am DGM und gehen ins IFC. Baden-Württemberg liefert über seinen Dienst nur ganze Meter, Bayern hat keinen freien Dienst: dort die DGM1-Kacheln als Datei laden."],gebaeude:["Gebäude (LoD2)","3D-Gebäudemodelle LoD2 der Länder als Umgebung des Baugrundmodells: Berlin, Brandenburg und NRW geben sie als CityGML-Kacheln von 1 × 1 km heraus, in ETRS89/UTM mit Höhen in m NHN – derselbe Rahmen wie das Modell. Nur auf Klick werden die Kacheln um die Bohrungen (plus Rand) geladen; Gebäude, deren Grundriss den Ausschnitt berührt, kommen ins IFC (IfcBuildingElementProxy mit Wänden und Dach, Quelle und Lizenz je Gebäude) und in den Viewer (Knopf „Gebäude“). Bestand, nicht erkundet."],standort:["Standort ohne Gutachten","Ein Projekt an einem Punkt (ETRS89/UTM, aus der Karte oder eingetragen): im Schritt Lage fragt es die Bohrungen der Länder um den Punkt ab, holt das DGM und die Gebäude – ein Lageplan ist nicht nötig, der Punkt ist schon georeferenziert. Übernommene Bohrungen mit Schichtdaten (NRW, Baden-Württemberg) ergeben ein Modell – eine Vorerkundung: Archivdaten unbekannter Güte, ohne Sondierungen, oft alt oder weit weg. Kommt später das Gutachten, entsteht ein neues Projekt, das die Bohrungen der Länder, DGM und Gebäude mitnimmt (gemischt)."],reifegrad:["Reifegrad","Woraus das Modell besteht: Gutachten (nur Bohrungen aus dem PDF), Vorerkundung (nur Bohrungen aus Datenbanken der Länder oder BoreholeML-Dateien) oder gemischt. Er steht in der App, im Viewer, im Prüfbericht und im IFC (CPset_Baugrundmodell.Reifegrad); jede Bohrung trägt ihre Herkunft mit Quelle und Lizenz (CPset_Herkunft)."],grundwasser:["Grundwasserfläche","Eine Fläche durch die gemessenen Wasserstände der Bohrungen (GOK − Tiefe), mit derselben Interpolation wie das Modell; sie geht nicht ins IFC und ändert das Modell nicht. Trockene Bohrungen („kein Grundwasser“) sind Daten: liegt die Fläche dort über der Endteufe, steht der Widerspruch dabei. Gemeldet werden auch eine Fläche über dem Gelände (gespanntes Wasser oder Stände verschiedener Tage) und mehrere Stände in einer Bohrung (der höchste gilt). Ab vier Ständen zeigt eine Kreuzprobe, wie gut sich der Wasserstand zwischen den Bohrungen vorhersagen lässt. Bohrzeit-Wasserstände sind Momentaufnahmen: kein Bemessungswasserstand."],orientierung:["Orientierung je Einheit","Nur für die implizite Methode (GemPy). Ohne Eingabe folgt die Orientierung einer Unterkante aus ihren Kontakten: Ebene durch die Bohrungen, entlang einer Trasse in Linienrichtung, steiler als 30° oder mit weniger als drei Kontakten horizontal. Ist das Einfallen bekannt (Gutachten, geologische Karte, Aufschluss), hier Fallrichtung (Azimut von Nord im Uhrzeigersinn, 0–360°) und Fallwinkel (0–80°) eingeben; dann gilt die Eingabe, auch in der Kreuzprobe, und Bericht und IFC nennen sie als Quelle „Eingabe“. An den Bohrungen bleibt jede Grenze exakt; passt die Eingabe nicht zu den Kontakten (mehr als 5 cm daneben), gilt für diese Fläche der Spline mit Hinweis. Leere Felder = aus den Kontakten."],gelaende_dgm:["Gelände aus dem DGM","Mit DGM folgt die Oberkante des Modells dem Gelände statt der Interpolation zwischen den GOK. An jeder Bohrung bleibt sie genau auf der GOK; deren Abweichung vom DGM klingt bis zur Reichweite (halber Bohrabstand, höchstens 25 m) ab. Im IFC liegt das Gelände um das Modell als IfcGeographicElement (TERRAIN), im Viewer mit dem Knopf „Gelände“ ein- und ausblendbar. Deckt das DGM das Modellgebiet nicht ganz ab, bleibt die Oberkante aus den GOK (mit Hinweis)."],dgm_epsg:["System der DGM-Datei","XYZ- und ASCII-Dateien enthalten kein Koordinatensystem: das System der Kacheln wählen (meist dasselbe wie das Projekt, z. B. 25832). Ein GeoTIFF bringt es selbst mit."],durchmesser:["Durchmesser","Dicke der Bohrsäulen im Viewer und im IFC (Darstellung, nicht der Bohrdurchmesser im Feld). Automatisch wächst er mit der Modellgröße, damit Säulen auf langen Trassen sichtbar bleiben."],einheiten:["Einheiten","Modelleinheiten verbinden gleiche Bodenarten zwischen den Bohrungen (Sand 1, Kies, Sand 2). Umbenennen oder Bodenarten zusammenlegen (z. B. „Sand, Kies“ als eine Einheit); Reihenfolge von oben nach unten."],analyse:["Ground Analysis","Wie weit trägt das Modell zwischen den Bohrungen? Die Kreuzprobe rechnet das Modell ohne je eine Bohrung und vergleicht seine Vorhersage mit ihr (mittlerer Fehler der Schichtgrenzen, für IDW und Spline). Die Unsicherheit verbindet die Messung der Grenzen (± 0,10 m, Monte Carlo) mit diesem Fehler über den Abstand zur nächsten Bohrung. Liest nur das Modell, ändert nichts. Mindestens 3 Bohrungen."],erkundung:["Erkundungsvorschlag","Punkte, an denen eine weitere Bohrung das Modell am meisten verbessert: wo die Unterkanten am stärksten streuen und wo unklar ist, wie weit eine Einheit reicht (Linse, Rinne). Am Beispiel einer Rinne zwischen den Bohrungen senkten zwei Bohrungen an den vorgeschlagenen Stellen den Fehler stärker als zwei zufällige; eine andere Interpolation half dort nicht (docs/27). Ein Vorschlag, keine Planung."],virtuell:["Virtuelle Bohrung","Was das Modell an einem Punkt erwartet: Einheiten mit Tiefen und der Streuung jeder Unterkante (± σ, 95 % etwa ± 2 σ). Eine Vorhersage aus den Nachbarbohrungen, keine Messung."],methode:["Interpolation","IDW: gewichtetes Mittel der Nachbarbohrungen, ruhig und sicher. Dünnplatten-Spline: glatte Flächen mit Trend, gut bei geneigten Schichten. Implizit (GemPy, wenn installiert): je Fläche ein Skalarfeld in 3D mit einer Orientierung aus den Kontakten (Ebene, sonst horizontal; steht im Bericht); langsamer, exakt an den Bohrungen; eine gefaltete Fläche rechnet der Spline (mit Hinweis). Welche Methode die Bohrungen am besten vorhersagt, zeigt die Ground Analysis."],puffer:["Puffer","Wie weit das Modell über die Bohrungen hinausreicht. Automatisch: halber Bohrabstand (5–100 m)."],raster:["Raster","Maschenweite der Schichtflächen. Automatisch: Gebietsgröße/40, bei großen Modellen gröber (höchstens 30 000 Knoten)."],basis:["Modellbasis","Unterkante des Modells in m NHN. Automatisch: tiefste Endteufe."],gok_relativ:["Fehlende GOK","Hat keine Bohrung eine GOK, rechnet das Modell relativ (Gelände = 0 m) – markiert im IFC."],auto:["Automatisch nachführen","Jede Änderung (Tabelle, Lage, Einheiten) rechnet das Modell sofort neu."],einchecken:["Einchecken","Hält den Prüfstand fest (Zeit, Zähler, Fingerabdruck des Modells, Kommentar). Das exportierte IFC trägt ihn (CPset_Baugrundmodell.Pruefstand)."],tiles3d:["3D Tiles für Cesium","Das Baugrundmodell als 3D Tiles 1.1 (tileset.json und glTF) für CesiumJS, Cesium for Unreal oder QGIS 3D: Baugrundmodell, Gelände und Gebäude je eine Kachel. Jeder Punkt wird exakt aus ETRS89/UTM umgerechnet, die Höhen ellipsoidisch mit dem Quasigeoid GCG2016 des BKG (CC BY 4.0; beim ersten Export einmal 1 MB geladen). ETRS89 ist nicht in WGS84/ITRF überführt (rund 0,9 m). Quellen und Lizenzen stehen in LIESMICH.txt."],geoldg:["Geologiedatengesetz (GeolDG)","Wer bohrt oder bohren lässt, muss die Untersuchung beim Geologischen Dienst des Landes anzeigen und die Daten übermitteln: Anzeige spätestens zwei Wochen vor Beginn (§ 8), Fachdaten wie das Schichtenverzeichnis spätestens drei Monate nach Abschluss (§ 9), Bewertungsdaten wie Gutachten und räumliche Modelle mit Dokumentation auf Verlangen (§ 10). Die Liste zeigt je Bohrung, was GroundTwin liefert (Lage, GOK, Endteufe, geprüfte Schichten) und was aus dem Bohrprotokoll kommt (Bohrverfahren, Ausbau, Proben, Messungen, Labor). Das Paket enthält BoreholeML, IFC, Prüfbericht, Modelldokumentation und eine Prüfliste zum Ergänzen. Hilfe, keine Rechtsberatung: Form und Weg legt die zuständige Behörde fest."],geoldg_abschluss:["Abschluss der Untersuchung","Die Untersuchung gilt mit Ablauf der Dauer als abgeschlossen, die in der Anzeige angegeben wurde – außer eine Fortdauer wurde rechtzeitig angezeigt (§ 15 Abs. 1). Ab dann laufen drei Monate für die Fachdaten; ist eine Behörde verpflichtet, etwa als Auftraggeber, sechs Monate für die Bewertungsdaten (§ 10 Abs. 2 Satz 2). Die Daten bleiben im Projekt."],export:["Export","IFC 4.3 mit Prüfstand, Bodenansprache je Schicht und Beschreibungen je Einheit; dazu Prüfbericht und die Daten als JSON."],ueberhoehung:["Überhöhung","Höhen im Viewer mal Faktor, damit dünne Schichten sichtbar werden. Die Koordinaten bleiben echt."]};let x=null,_e=null;function he(){x?.remove(),x=null,_e=null}function Tn(e,n){e.preventDefault(),e.stopPropagation();const t=e.currentTarget;if(_e===t){he();return}he();const[i,s]=Me[n];x=document.createElement("div"),x.className="hilfe-blase",x.setAttribute("role","tooltip"),x.innerHTML="<strong></strong><p></p>",x.querySelector("strong").textContent=i,x.querySelector("p").textContent=s,document.body.append(x);const r=t.getBoundingClientRect(),o=x.getBoundingClientRect(),d=Math.min(Math.max(8,r.left+r.width/2-o.width/2),window.innerWidth-o.width-8),h=r.bottom+8+o.height>window.innerHeight?r.top-o.height-8:r.bottom+8;Object.assign(x.style,{left:`${d}px`,top:`${h}px`}),_e=t}document.addEventListener("click",e=>{x&&!x.contains(e.target)&&he()});document.addEventListener("keydown",e=>{e.key==="Escape"&&he()});const g=e=>a`<button type="button" class="hilfe" title=${Me[e][0]} aria-label=${`Hilfe: ${Me[e][0]}`}
    @click=${n=>Tn(n,e)}>?</button>`,Fn="https://sgx.geodatenzentrum.de/wmts_basemapde/tile/1.0.0/de_basemapde_web_raster_farbe/default/GLOBAL_WEBMERCATOR/{z}/{y}/{x}.png",Rn="https://tile.openstreetmap.org/{z}/{x}/{y}.png",He=[51.16,10.45];let Q=null;const se=e=>e.replace(/[&<>"]/g,n=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[n]),Ie=e=>e.toLocaleString("de-DE",{minimumFractionDigits:1,maximumFractionDigits:1});async function On(){const[{default:e}]=await Promise.all([De(()=>import("./leaflet-src-7ah4FPQk.js").then(n=>n.l),[],import.meta.url),De(()=>Promise.resolve({}),__vite__mapDeps([0]),import.meta.url)]);return new Promise(n=>{const t=document.createElement("dialog");t.className="karte-dialog",t.setAttribute("aria-label","Standort auf der Karte wählen"),t.innerHTML=`
      <header><strong>Standort auf der Karte wählen</strong>
        <button type="button" class="symbol schliessen" aria-label="Karte schließen">✕</button></header>
      <div class="karte-flaeche"></div>
      <footer>
        <div class="karte-info klein" aria-live="polite">In die Karte klicken: der Punkt wird der Standort (zum Orientieren,
          auf wenige Meter genau). Mausrad zoomt, Ziehen verschiebt.</div>
        <div class="zeile"><span class="fueller"></span>
          <button type="button" class="abbrechen">Abbrechen</button>
          <button type="button" class="primaer uebernehmen" disabled>Punkt übernehmen</button></div>
      </footer>`,document.body.append(t),t.showModal();const i=t.querySelector(".karte-info"),s=t.querySelector(".uebernehmen"),r=e.map(t.querySelector(".karte-flaeche"),{zoomControl:!0,attributionControl:!0}).setView(Q?[Q.breite,Q.laenge]:He,Q?.zoom??6),o=new Date().getFullYear(),d=e.tileLayer(Fn,{maxZoom:18,attribution:`© <a href="https://basemap.de" target="_blank" rel="noopener">GeoBasis-DE / BKG (${o})</a> <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>`}).addTo(r),h=e.tileLayer(Rn,{maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap-Mitwirkende</a>'});e.control.layers({"basemap.de (BKG)":d,OpenStreetMap:h},{},{position:"topright"}).addTo(r),e.control.scale({imperial:!1}).addTo(r);const c=e.circleMarker(He,{radius:8,color:"#10210a",weight:2,fillColor:"#a2c513",fillOpacity:.95});let v=null,z=0;r.on("click",async _=>{const b=++z;c.setLatLng(_.latlng).addTo(r),v=null,s.disabled=!0,i.textContent="wird umgerechnet …";try{const E=await f.standortPunkt(Number(_.latlng.lng.toFixed(7)),Number(_.latlng.lat.toFixed(7)));if(b!==z)return;v=E,s.disabled=!1,i.innerHTML=`<b>Rechtswert ${Ie(E.x)} · Hochwert ${Ie(E.y)} · EPSG:${E.epsg}</b>
          <ul class="dienste">${E.dienste.map(A=>`<li class="${A.art}">${/^https?:\/\//.test(A.url??"")?`<a href="${se(A.url)}" target="_blank" rel="noopener noreferrer">${se(A.text)}</a>`:se(A.text)}${A.status==="ungeprueft"?' <span class="ungeprueft">ungeprüft</span>':""}</li>`).join("")}</ul>
          <span class="leise">Das Land aus den Ländergrenzen (VG2500 des BKG, auf rund 150 m); Portale als Link.</span>`}catch(E){if(b!==z)return;i.innerHTML=`<span class="warnung">${se(E.message)}</span>`}});const N=_=>{const b=r.getCenter();Q=_?{laenge:_.laenge,breite:_.breite,zoom:Math.max(r.getZoom(),14)}:{laenge:b.lng,breite:b.lat,zoom:r.getZoom()},r.remove(),t.close(),t.remove(),n(_)};t.querySelector(".schliessen").addEventListener("click",()=>N(null)),t.querySelector(".abbrechen").addEventListener("click",()=>N(null)),s.addEventListener("click",()=>N(v)),t.addEventListener("cancel",_=>{_.preventDefault(),N(null)}),requestAnimationFrame(()=>r.invalidateSize())})}let K=[],Le=!0,oe=!1;const y={x:"",y:"",epsg:25832,name:""};let q=null;const jn=[[25832,"ETRS89 / UTM 32N"],[25833,"ETRS89 / UTM 33N"],[4647,"ETRS89 / UTM 32N (zE-N)"],[5650,"ETRS89 / UTM 33N (zE-N)"]];async function pn(e){for(;;){const n=await w(()=>f.auftrag(e));if(!n)return;if(l.auftrag=n,p(),n.fertig){l.auftrag=null;for(const t of n.fehler)D(t,"fehler",1e4);n.projekt?(K=[],await J(n.projekt,"bohrungen")):p();return}await new Promise(t=>setTimeout(t,600))}}const mn=()=>l.z?.standort?l.sig:"";async function Hn(){if(!K.length)return;const e=await w(()=>f.gutachten(K,Le&&!!l.info?.ocr,mn()));e&&await pn(e.id)}async function In(){const e=Number(y.x.replace(",",".")),n=Number(y.y.replace(",","."));if(!Number.isFinite(e)||!Number.isFinite(n)||!y.x||!y.y){D("Rechtswert und Hochwert als Zahlen eingeben.","warn");return}const t=await w(()=>f.standort(e,n,y.epsg,y.name),"Standort wird angelegt …");t&&(await J(t.projekt,t.vorhanden?void 0:"lage"),t.vorhanden&&D(`Den Standort gibt es schon: „${l.z?.name}“ geöffnet.`))}async function Un(){let e=null;try{e=await On()}catch(n){D(`Karte: ${n.message}`,"fehler",8e3)}e&&(y.x=String(e.x),y.y=String(e.y),y.epsg=e.epsg,q=e.dienste,p())}function Wn(){const e=(t,i,s)=>a`
    <label class="feld"><span>${i}</span><input type="text" inputmode=${t==="name"?"text":"decimal"}
      aria-label=${i} placeholder=${s} .value=${y[t]} @input=${r=>{y[t]=r.target.value,t!=="name"&&q&&(q=null),p()}}></label>`,n=!!(y.x.trim()&&y.y.trim());return a`
    <section class="weg" aria-labelledby="weg-standort">
      <div class="weg-symbol" aria-hidden="true">◎</div>
      <h2 id="weg-standort">Standort</h2>
      <p class="weg-text">Noch kein Gutachten? Ein Punkt auf der Karte genügt: Bohrungen der Länder rund um den Punkt –
        eine <b>Vorerkundung</b>, kein Ersatz für das Gutachten. ${g("standort")}</p>
      <button class=${n?"":"primaer gross-knopf"} @click=${Un}>🗺 Auf der Karte wählen</button>
      ${n?a`<div class="punkt-wahl">
        <p class="klein"><b>${y.x} / ${y.y}</b> · EPSG:${y.epsg}</p>
        ${q?gn(q):u}
        ${e("name","Name (frei)","z. B. Marl Nord")}
        <button class="primaer gross-knopf" @click=${In}>Projekt am Standort anlegen →</button>
      </div>`:u}
      <details class="still">
        <summary>Koordinaten eingeben</summary>
        <div class="raster-2">
          ${e("x","Rechtswert","z. B. 368130")}
          ${e("y","Hochwert","z. B. 5724400")}
          <label class="feld"><span>System</span>
            <select aria-label="System des Standorts" @change=${t=>{y.epsg=Number(t.target.value),q=null,p()}}>
              ${jn.map(([t,i])=>a`<option value=${t} ?selected=${y.epsg===t}>${t} · ${i}</option>`)}
            </select></label>
        </div>
        <p class="leise klein">ETRS89/UTM, nur Deutschland. ${g("karte")}</p>
      </details>
    </section>`}async function Ue(e){const n=await w(()=>f.beispiel(e),"Beispiel wird geöffnet …");n?.projekt?await J(n.projekt,n.schritt??"bohrungen"):n?.auftrag&&await pn(n.auftrag)}function We(e){K=[...e??[]].filter(n=>/\.(pdf|json|xml)$/i.test(n.name)),e?.length&&!K.length&&D("Bitte PDF-Dateien wählen (oder eine Extraktion als JSON, Bohrungen als BoreholeML).","warn"),p()}async function Vn(e,n){confirm(`Projekt „${n}“ mit allen Korrekturen löschen? Das Gutachten selbst bleibt unberührt.`)&&(await w(()=>f.loeschen(e)),await dn())}function Cn(){const e=l.auftrag,n=!!l.info?.ocr;return a`
    <section class="weg" aria-labelledby="weg-gutachten">
      <div class="weg-symbol" aria-hidden="true">⇪</div>
      <h2 id="weg-gutachten">Gutachten</h2>
      <p class="weg-text">Das Bodengutachten als PDF – Vektor oder Scan. Die Bohrungen werden erkannt; Sie prüfen sie,
        sehen sie in 3D und vergleichen sie mit den Bohrungen der Länder.</p>
      ${mn()?a`<p class="hinweis-standort">Zum Standort <b>${l.z.name}</b>: Bohrungen der Länder (mit Prüfstand),
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
        <label class=${`ablage ${oe?"ueber":""} ${K.length?"bereit":""}`}
          @dragover=${t=>{t.preventDefault(),oe=!0,p()}}
          @dragleave=${()=>{oe=!1,p()}}
          @drop=${t=>{t.preventDefault(),oe=!1,We(t.dataTransfer?.files)}}>
          <input type="file" accept=".pdf,application/pdf,.json,application/json,.xml,application/xml,text/xml" multiple @change=${t=>We(t.target.files)}>
          <strong>${K.length?K.map(t=>t.name).join(", "):"PDF hierher ziehen oder klicken"}</strong>
          <span class="leise klein">${K.length?`${K.length} Datei(en) bereit`:"mehrere Dateien möglich (z. B. Anlagen 2–4)"}</span>
        </label>
        <button class="primaer gross-knopf" ?disabled=${!K.length} @click=${Hn}>Auswerten →</button>
        <details class="still">
          <summary>Optionen</summary>
          <div class="zeile">
            <label class="schalter" title=${n?"":"nicht installiert: pip install -r requirements-ocr.txt"}>
              <input type="checkbox" .checked=${Le&&n} ?disabled=${!n} @change=${t=>{Le=t.target.checked}}>
              OCR für Scans ${n?"":"(nicht installiert)"}
            </label>${g("ocr")}
          </div>
          <p class="leise klein">Auch eine Extraktion als JSON oder Bohrungen als BoreholeML (XML) lassen sich laden.</p>
        </details>`}
    </section>`}const Ve=5;function Ce(e){return e.map(n=>a`
    <tr>
      <td><button class="link" @click=${()=>J(n.signatur)}>${n.name}</button>${n.standort?a` <span class="abzeichen vorerkundung" title="Standort ohne Gutachten">Standort</span>`:u}
        <div class="leise klein">${n.dokumente.join(", ")}</div></td>
      <td class="zahl" title=${n.fremd?`davon ${n.fremd} aus den Datenbanken der Länder`:""}>${n.bohrungen}</td>
      <td class="zahl">${n.geprueft}${n.eincheckungen?a` · <span title="eingecheckt">✓${n.eincheckungen}</span>`:u}</td>
      <td class="leise klein">${n.geaendert}</td>
      <td><button class="symbol" title="Projekt löschen" aria-label="Projekt löschen" @click=${()=>Vn(n.signatur,n.name)}>🗑</button></td>
    </tr>`)}function Zn(){if(!l.projekte.length)return u;const e=a`<thead><tr><th>Projekt</th><th>Bohrungen</th><th>geprüft</th><th>geändert</th><th></th></tr></thead>`,n=l.projekte.slice(Ve);return a`
    <section class="zuletzt">
      <h3>Zuletzt bearbeitet</h3>
      <table class="tabelle kompakt">${e}<tbody>${Ce(l.projekte.slice(0,Ve))}</tbody></table>
      ${n.length?a`<details class="still"><summary>Alle ${l.projekte.length} Projekte</summary>
        <table class="tabelle kompakt">${e}<tbody>${Ce(n)}</tbody></table></details>`:u}
    </section>`}function qn(){const e=l.auftrag,n=l.info?.beispiele??[];return a`
    <details class="still beispiele">
      <summary>Beispiele ausprobieren</summary>
      <div class="zwei-spalten">
        <div>
          <h4 class="klein">Gutachten ${g("beispiele")}</h4>
          <ul class="auswahl-liste">
            ${n.filter(t=>!t.standort).map(t=>a`
              <li><button class="link" ?disabled=${!!e} @click=${()=>Ue(t.name)}>${t.titel}</button></li>`)}
          </ul>
        </div>
        <div>
          <h4 class="klein">Standort <span class="leise">(Bohrungen der Länder: Abfrage im Schritt Lage, mit Netz)</span></h4>
          <ul class="auswahl-liste">
            ${n.filter(t=>t.standort).map(t=>a`
              <li><button class="link" ?disabled=${!!e} @click=${()=>Ue(t.name)}>${t.titel}</button></li>`)}
          </ul>
        </div>
      </div>
    </details>`}function Jn(){return a`
    <div class="seite-mitte start">
      <header class="start-titel">
        <h1>Baugrund verstehen.</h1>
        <p>Bohrungen aus dem Gutachten oder vom Standort – geprüft, in 3D, im Vergleich mit den Bohrungen der Länder.</p>
      </header>
      <div class="wege">
        ${Cn()}
        ${Wn()}
      </div>
      ${Zn()}
      ${qn()}
      ${l.info?a`<p class="leise klein impressum">GroundTwin ${l.info.version} ·
        <a href="dienste.html" target="_blank" rel="noopener">Dienste der Länder</a> ·
        <a href="viewer.html" target="_blank" rel="noopener">Viewer allein</a> · freie Software unter
        <a href=${`${l.info.quellcode}/blob/main/LICENSE`} target="_blank" rel="noopener">${l.info.lizenz}</a> ·
        <a href=${l.info.quellcode} target="_blank" rel="noopener">Quellcode</a><br>Die App extrahiert und schlägt vor;
        die Interpretation und Freigabe bleibt beim Geotechniker.</p>`:u}
    </div>`}const ue="Deutschland · ETRS89 / UTM (amtlich)",V="Deutschland · Gauß-Krüger (alt)",ge=[{code:25832,name:"ETRS89 / UTM Zone 32N",gruppe:ue,e:[22e4,101e4],n:[503e4,614e4],hinweis:"Rechtswert 6-stellig, die meisten Länder"},{code:25833,name:"ETRS89 / UTM Zone 33N",gruppe:ue,e:[15e4,7e5],n:[509e4,613e4],hinweis:"Rechtswert 6-stellig, Osten (Berlin, Brandenburg, Sachsen, MV)"},{code:4647,name:"ETRS89 / UTM 32N mit Zone (32…)",gruppe:ue,e:[3223e4,33e6],n:[52e5,614e4],hinweis:"Rechtswert 8-stellig, beginnt mit 32"},{code:5650,name:"ETRS89 / UTM 33N mit Zone (33…)",gruppe:ue,e:[3315e4,3354e4],n:[52e5,613e4],hinweis:"Rechtswert 8-stellig, beginnt mit 33"},{code:31466,name:"DHDN / Gauß-Krüger Zone 2",gruppe:V,e:[23e5,27e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 2"},{code:31467,name:"DHDN / Gauß-Krüger Zone 3",gruppe:V,e:[33e5,37e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 3"},{code:31468,name:"DHDN / Gauß-Krüger Zone 4",gruppe:V,e:[43e5,47e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 4"},{code:31469,name:"DHDN / Gauß-Krüger Zone 5",gruppe:V,e:[531e4,57e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 5"},{code:2398,name:"Krassowski (42/83) / Gauß-Krüger Zone 4",gruppe:V,e:[43e5,47e5],n:[52e5,613e4],hinweis:"neue Länder vor ETRS89, Rechtswert beginnt mit 4"},{code:2399,name:"Krassowski (42/83) / Gauß-Krüger Zone 5",gruppe:V,e:[53e5,57e5],n:[52e5,613e4],hinweis:"neue Länder vor ETRS89, Rechtswert beginnt mit 5"},{code:3068,name:"DHDN / Soldner Berlin",gruppe:"Deutschland · andere",e:[-4e4,9e4],n:[-4e4,8e4],hinweis:"Berlin, alte Katasterkoordinaten (5-stellig)"},{code:2056,name:"CH1903+ / LV95",gruppe:"Schweiz",e:[245e4,287e4],n:[103e4,134e4],hinweis:"E 2 xxx xxx, N 1 xxx xxx"},{code:21781,name:"CH1903 / LV03",gruppe:"Schweiz",e:[45e4,87e4],n:[3e4,34e4],hinweis:"Y 6-stellig, X 5–6-stellig (alt)"},{code:31254,name:"MGI / Austria GK West",gruppe:"Österreich",e:[-11e4,17e4],n:[11e4,34e4],hinweis:"Rechtswert um 0 (±), Hochwert ohne 5 000 000"},{code:31255,name:"MGI / Austria GK Central",gruppe:"Österreich",e:[-16e4,17e4],n:[9e4,46e4],hinweis:"Rechtswert um 0 (±), Hochwert ohne 5 000 000"},{code:31256,name:"MGI / Austria GK East",gruppe:"Österreich",e:[-16e4,1e5],n:[1e5,48e4],hinweis:"Rechtswert um 0 (±), Hochwert ohne 5 000 000"},{code:31257,name:"MGI / Austria GK M28 (BMN)",gruppe:"Österreich",e:[4e4,32e4],n:[11e4,34e4],hinweis:"Bundesmeldenetz West"},{code:31258,name:"MGI / Austria GK M31 (BMN)",gruppe:"Österreich",e:[29e4,62e4],n:[9e4,46e4],hinweis:"Bundesmeldenetz Mitte"},{code:31259,name:"MGI / Austria GK M34 (BMN)",gruppe:"Österreich",e:[59e4,85e4],n:[1e5,48e4],hinweis:"Bundesmeldenetz Ost"},{code:32632,name:"WGS 84 / UTM Zone 32N",gruppe:"GPS (WGS 84)",e:[22e4,101e4],n:[503e4,614e4],hinweis:"wie ETRS89 / UTM 32N (Abweichung < 1 m)"},{code:32633,name:"WGS 84 / UTM Zone 33N",gruppe:"GPS (WGS 84)",e:[15e4,7e5],n:[509e4,613e4],hinweis:"wie ETRS89 / UTM 33N (Abweichung < 1 m)"}],Qn=new Map(ge.map(e=>[e.code,e]));function Ke(e){return e?Qn.get(e)??null:null}function Te(e){if(!e)return"ohne System (lokal)";const n=Ke(e);return n?`EPSG ${e} · ${n.name}`:`EPSG ${e} (nicht in der Liste)`}const bn=(e,n,t)=>n>=e.e[0]&&n<=e.e[1]&&t>=e.n[0]&&t<=e.n[1];function Yn(e,n){return e===null||n===null||!Number.isFinite(e)||!Number.isFinite(n)?[]:ge.filter(t=>t.gruppe!=="GPS (WGS 84)"&&bn(t,e,n))}function fn(e,n,t){if(n===null||t===null||!Number.isFinite(n)||!Number.isFinite(t))return null;const i=Yn(n,t),s=i.slice(0,3).map(o=>`${o.code} (${o.name})`).join(", ");if(!e)return i.length?{ok:!1,text:`Kein System gewählt – die Werte passen zu ${s}.`}:null;const r=Ke(e);return r?bn(r,n,t)?{ok:!0,text:`passt zu EPSG ${e} (${r.hinweis})`}:{ok:!1,text:i.length?`Rechts-/Hochwert passen nicht zu EPSG ${e} (${r.hinweis}), aber zu ${s}.`:"Rechts-/Hochwert passen zu keinem System der Liste – Ziffern prüfen (z. B. fehlende Zonenkennung)."}:{ok:!1,text:`EPSG ${e} ist nicht in der Liste – bitte prüfen.`}}function Fe(e,n,t="Koordinatensystem"){const i=[...new Set(ge.map(r=>r.gruppe))],s=e!==null&&!Ke(e);return a`
    <select class="epsg" aria-label=${t} title=${Te(e)}
      @change=${r=>{const o=r.target.value;n(o===""?null:Number(o))}}>
      <option value="" .selected=${e===null}>– ohne (lokal) –</option>
      ${s?a`<option value=${String(e)} .selected=${!0}>EPSG ${e} – nicht in der Liste ⚠</option>`:u}
      ${i.map(r=>a`
        <optgroup label=${r}>
          ${ge.filter(o=>o.gruppe===r).map(o=>a`
            <option value=${String(o.code)} .selected=${o.code===e}>${o.code} · ${o.name}</option>`)}
        </optgroup>`)}
    </select>`}const te=(e,n=2)=>e.toLocaleString("de-DE",{minimumFractionDigits:n,maximumFractionDigits:n});function $n(e){for(const n of[.5,1,2,5,10,20,50,100])if(e/n<=12)return n;return 200}function Xn(e,n){const t=Math.max(1,...e.map(c=>c.bis)),i=12,s=(n.hoehe-i-14)/t,r=34,o=46,d=$n(t),h=[];for(let c=0;c<=t+1e-9;c+=d)h.push(c);return a`<svg class="saeule" viewBox="0 0 150 ${n.hoehe}" width="150" height=${n.hoehe} role="img" aria-label="Bohrsäule">
    <defs>
      <pattern id="schraffur-warn" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
        <rect width="6" height="6" fill="#e6e6e6"></rect><line x1="0" y1="0" x2="0" y2="6" stroke="#f0a33a" stroke-width="3"></line>
      </pattern>
    </defs>
    ${h.map(c=>W`
      <line x1=${r-5} x2=${r} y1=${i+c*s} y2=${i+c*s} class="achse"></line>
      <text x=${r-7} y=${i+c*s+3} class="achse-text" text-anchor="end">${te(c,d<1?1:0)}</text>`)}
    <line x1=${r} x2=${r} y1=${i} y2=${i+t*s} class="achse"></line>
    ${e.map(c=>W`
      <g class=${`schicht ${c.k===n.gewaehlt?"gewaehlt":""} ${c.warn?"warn":""}`} @click=${()=>n.waehlen?.(c.k)}>
        <title>${c.titel}</title>
        <rect x=${r+4} y=${i+c.von*s} width=${o} height=${Math.max(1,(c.bis-c.von)*s)}
          fill=${c.warn?"url(#schraffur-warn)":c.farbe}></rect>
        ${c.geprueft?W`<text x=${r+o+9} y=${i+(c.von+c.bis)/2*s+4} class="haken">✓</text>`:u}
        ${(c.bis-c.von)*s>11?W`<text x=${r+o+22} y=${i+c.bis*s-2} class="tiefe">${te(c.bis)}</text>`:u}
      </g>`)}
  </svg>`}function et(e,n){const t=[...e.bohrungen].sort((b,E)=>b.x-E.x||b.y-E.y);if(!t.length)return u;const i=new Map(e.einheiten.map(b=>[b.name,b.farbe])),s=Math.max(...t.map(b=>b.gok)),r=Math.min(...t.map(b=>b.endteufe_nhn)),o=22,d=44,h=Math.max(38,Math.min(70,900/t.length)),c=d+t.length*h+10,v=(n.hoehe-o-10)/Math.max(1,s-r),z=b=>o+(s-b)*v,N=$n(s-r),_=[];for(let b=Math.ceil(r/N)*N;b<=s+1e-9;b+=N)_.push(b);return a`<svg class="einheitenprofil" viewBox="0 0 ${c} ${n.hoehe}" width=${c} height=${n.hoehe} role="img"
      aria-label="Einheiten je Bohrung">
    ${_.map(b=>W`
      <line x1=${d-4} x2=${c} y1=${z(b)} y2=${z(b)} class="raster"></line>
      <text x=${d-6} y=${z(b)+3} class="achse-text" text-anchor="end">${te(b,N<1?1:0)}</text>`)}
    ${t.map((b,E)=>{const A=d+E*h+h*.2,ze=h*.6;return W`
        <text x=${A+ze/2} y=${o-8} class="code" text-anchor="middle">${b.code}</text>
        ${b.einheiten.filter(L=>L.status==="vorhanden"&&L.ok_modell-L.uk_modell>.001).map(L=>W`
          <rect x=${A} y=${z(L.ok_modell)} width=${ze} height=${Math.max(.8,(L.ok_modell-L.uk_modell)*v)}
            fill=${i.get(L.einheit)??"#ccc"} class=${`einheit ${n.gewaehlt===L.einheit?"gewaehlt":""}`}
            @click=${()=>n.waehlen?.(L.einheit)}>
            <title>${b.code}: ${L.einheit} ${te(L.ok_modell)} bis ${te(L.uk_modell)} m NHN</title>
          </rect>`)}
        <line x1=${A-3} x2=${A+ze+3} y1=${z(b.endteufe_nhn)} y2=${z(b.endteufe_nhn)} class="endteufe"></line>`})}
  </svg>`}const pe=(e,n=2)=>e==null?"":e.toLocaleString("de-DE",{minimumFractionDigits:n,maximumFractionDigits:n}),xe=e=>{const n=e.target.value.trim().replace(",",".");return n===""?null:Number(n)},nt=[["boden","Böden"],["organisch","Organisch"],["geologisch","Geologische Benennung"],["fels","Fels"],["anthropogen","Anthropogen"],["unbekannt","Nicht klassifiziert"]];let me=null,Se="",F=.5,Ze=!1;function kn(){return l.z?.plausibilitaet??[]}function wn(e){return kn().find(n=>n.id===e)?.befunde??[]}function be(e){const n=le(),t=n.findIndex(s=>s.id===l.bid),i=n[Math.min(n.length-1,Math.max(0,t+e))];i&&we(i.id)}function vn(){const e=le(),n=Ae(e.findIndex(t=>t.id===l.bid));n&&we(n)}async function zn(){const e=l.bid;if(!await m([{op:"bohrung_pruefen",id:e,wert:!0}],{leise:!0}))return;const n=Ae(le().findIndex(t=>t.id===e));n&&n!==e&&await we(n)}async function qe(e){const n=l.z.pruefstand,t=e?`Alle Schichten aller ${n.bohrungen[1]} Bohrungen als geprüft markieren?`:"Die Prüfung aller Bohrungen zurücknehmen?";confirm(t)&&await m([{op:"alle_pruefen",wert:e}])}window.addEventListener("keydown",e=>{if(l.schritt!=="bohrungen"||e.ctrlKey||e.metaKey||e.altKey||e.target?.closest?.("input, select, textarea, [contenteditable]"))return;const t=e.key.toLowerCase();if(e.key==="ArrowDown"||t==="j")be(1);else if(e.key==="ArrowUp"||t==="k")be(-1);else if(t==="n")vn();else if(t==="g")zn();else return;e.preventDefault()});async function tt(e,n){const t=Number(e.id.split(":")[0]),i=(n[0]?.quelle.seite??e.seite)-1,s=`${l.sig}/${t}/${i}`;if(me?.schluessel===s||Se===s||!l.z?.dokumente[t]?.pdf)return;Se=s;const r=await w(()=>f.seite(l.sig,t,i));Se="",r&&(me={schluessel:s,daten:r},p())}function it(e){return e.entfernt?a`<span class="zeichen raus" title="nicht im Modell">–</span>`:e.offen>0?a`<span class="zeichen warn" title=${`${e.offen} Schicht(en) nicht klassifiziert`}>⚠</span>`:e.schichten_n&&e.schichten_geprueft===e.schichten_n?a`<span class="zeichen ok" title="alle Schichten geprüft">✓</span>`:a`<span class="zeichen" title="noch zu prüfen">○</span>`}function at(e){const n=wn(e.id);if(!n.length)return u;const t=n.some(s=>s.stufe==="warnung"),i=n.map(s=>`${s.stufe==="warnung"?"Warnung":"Hinweis"}: ${s.text}`).join(`
`);return a`<span class=${`klein ${t?"warn":"leise"}`} title=${i}>${t?"⚠":"ℹ"}\u00a0${n.length}</span>`}function rt(e){const n=wn(e.id);if(!n.length)return u;const t=n.filter(r=>r.stufe==="warnung").length,i=n.filter(r=>r.stufe==="hinweis").length,s=[t?`${t} Warnung(en)`:"",i?`${i} Hinweis(e)`:""].filter(Boolean).join(", ");return a`
    <details class="still" ?open=${t>0}>
      <summary class=${t?"warn":""}>${t?"⚠":"ℹ"} Plausibilität (${n.length}): ${s}</summary>
      <ul class="dienste klein">
        ${n.map(r=>a`
          <li class=${r.stufe==="warnung"?"warn":"leise"}>
            ${r.stufe==="warnung"?"⚠ Warnung":"ℹ Hinweis"}: ${r.text}
          </li>`)}
      </ul>
    </details>`}function lt(){const e=l.z.bohrungen,n=le(),t=e.filter(i=>i.entfernt);return a`
    <aside class="bohrliste-app">
      <input class="suche" type="search" placeholder="Bohrung suchen …" .value=${l.filter}
        @input=${i=>{l.filter=i.target.value,p()}}>
      <ul class="bliste" role="listbox" aria-label="Bohrungen">
        ${n.map(i=>a`
          <li role="option" aria-selected=${String(i.id===l.bid)} class=${i.id===l.bid?"aktiv":""}
            @click=${()=>we(i.id)}>
            ${it(i)}
            <span class="name">${i.code} ${at(i)}</span>
            <span class="wert">${i.schichten_geprueft}/${i.schichten_n}</span>
            <button class="symbol leise-knopf" title="Aus dem Modell entfernen" aria-label=${`${i.code} entfernen`}
              @click=${s=>{s.stopPropagation(),m([{op:"entfernen",id:i.id}])}}>🗑</button>
          </li>`)}
      </ul>
      ${t.length?a`
        <details class="entfernt" ?open=${Ze} @toggle=${i=>{Ze=i.target.open}}>
          <summary>Entfernt / nicht im Modell (${t.length}) ${g("entfernen")}</summary>
          <ul class="bliste">
            ${t.map(i=>a`
              <li class="raus">
                <span class="name">${i.code}</span>
                <span class="wert klein">${i.doppelt_in?"doppelt":i.schichten_n?"":"ohne Schichten"}</span>
                <button class="link klein" ?disabled=${!i.schichten_n} @click=${()=>m([{op:"wiederherstellen",id:i.id}])}>wiederherstellen</button>
              </li>`)}
          </ul>
        </details>`:u}
      <p class="leise klein tasten">↑/↓ blättern · N nächste offene · G alle Schichten geprüft und weiter</p>
    </aside>`}function st(){const e=l.z.pruefstand,[n,t]=e.bohrungen,[i,s]=e.schichten,r=kn().flatMap(h=>h.befunde),o=r.filter(h=>h.stufe==="warnung").length,d=r.filter(h=>h.stufe==="hinweis").length;return a`
    <div class="pruefleiste">
      <div class="balken"><span>Bohrungen geprüft <b>${n}/${t}</b></span><progress max=${t||1} value=${n}></progress></div>
      <div class="balken"><span>Schichten geprüft <b>${i}/${s}</b></span><progress max=${s||1} value=${i}></progress></div>
      <span class=${`plakette ${e.unklassifiziert_offen?"warn":"ok"}`}>
        ${e.unklassifiziert_offen?`⚠ ${e.unklassifiziert_offen} Schicht(en) nicht klassifiziert`:"✓ keine offenen Warnungen"}</span>
      ${g("warnung")}
      <span class=${`klein ${o?"warn":"leise"}`}>Plausibilität: ${o} Warnungen, ${d} Hinweise</span>
      <span class="fueller"></span>
      ${g("pruefstand")}
      <button @click=${()=>qe(!0)} ?disabled=${n===t&&i===s}>✓ Alle Bohrungen geprüft</button>
      <button class="leise-knopf" @click=${()=>qe(!1)} ?disabled=${!i}>Zurücknehmen</button>
      ${g("alle_pruefen")}
    </div>`}function I(e,n,t){return a`<label class="feld"><span>${e}${t?g(t):u}</span>${n}</label>`}function ot(e){const n=fn(e.epsg,e.x,e.y);return n&&!n.ok?a`<p class="hinweise warn">⚠ ${n.text}</p>`:u}function ut(e){const n=le(),t=n.findIndex(s=>s.id===e.id),i=s=>r=>m([{op:"bohrung",id:e.id,feld:s,wert:xe(r)}]);return a`
    <div class="detail-kopf">
      <div class="titelzeile">
        <h2>${e.code}</h2>
        <span class="leise">${e.dokument} · Seite ${e.seite}${e.doppelt_in?` · doppelt (auch in ${e.doppelt_in})`:""}</span>
        <span class="fueller"></span>
        <button title="Vorherige Bohrung (↑)" ?disabled=${t<=0} @click=${()=>be(-1)}>↑ Vorherige</button>
        <button title="Nächste Bohrung (↓)" ?disabled=${t>=n.length-1} @click=${()=>be(1)}>↓ Nächste</button>
        <button title="Nächste Bohrung mit offenen Schichten (N)" ?disabled=${!Ae(t)} @click=${vn}>⚠ Nächste offene</button>
      </div>
      <div class="felder">
        ${I("GOK [m NHN]",a`<input type="number" step="0.01" .value=${k(e.gok===null?"":String(e.gok))}
            placeholder="unbekannt" @change=${i("gok")}>
            <small class=${e.gok_quelle==="manuell"||e.gok_quelle==="DGM"?"manuell":"leise"}>${e.gok_quelle||"fehlt"}</small>`,"gok")}
        ${I("Endteufe [m]",a`<output>${pe(e.endteufe)}</output>`)}
        ${I("Rechtswert",a`<input type="number" step="0.01" .value=${k(e.x===null?"":String(e.x))} @change=${i("x")}>`,"koordinaten")}
        ${I("Hochwert",a`<input type="number" step="0.01" .value=${k(e.y===null?"":String(e.y))} @change=${i("y")}>`)}
        ${I("Koordinatensystem (EPSG)",Fe(e.epsg,s=>m([{op:"bohrung",id:e.id,feld:"epsg",wert:s}])),"epsg")}
        ${I("Ø Säule [m]",a`<input type="number" step="0.1" min="0" class="kurz" placeholder=${`auto ${pe(l.z.durchmesser??l.z.durchmesser_auto,1)}`}
            .value=${k(e.durchmesser===null?"":String(e.durchmesser))} @change=${i("durchmesser")}>`,"durchmesser")}
        ${I("Grundwasser",a`<output>${e.grundwasser||"–"}</output>`)}
      </div>
      ${ot(e)}
      ${rt(e)}
      ${e.hinweise.length?a`<p class="hinweise">ℹ ${e.hinweise.join(" · ")}</p>`:u}
    </div>`}function ct(e,n){const t=l.z.klassen,i=t.some(s=>s.klasse===n.bodenart);return a`
    <span class="farbfeld" style=${`background:${n.farbe}`}></span>
    <select aria-label="Bodenart" @change=${s=>m([{op:"schicht",id:e.id,k:n.k,feld:"bodenart",wert:s.target.value}])}>
      ${i?u:a`<option .selected=${!0} value=${n.bodenart}>${n.bodenart}</option>`}
      ${nt.map(([s,r])=>a`
        <optgroup label=${r}>
          ${t.filter(o=>o.art===s).map(o=>a`
            <option value=${o.klasse} .selected=${o.klasse===n.bodenart}>${o.name}${o.din4023?` (${o.din4023})`:""}</option>`)}
        </optgroup>`)}
    </select>`}function dt(e,n){return a`
    <table class="tabelle schichten">
      <thead><tr>
        <th title="geprüft">✓ ${g("geprueft")}</th><th>von [m] ${g("tiefe")}</th><th>bis [m]</th>
        <th>Bodenart ${g("bodenart")}</th><th>Beschreibung (PDF)</th><th>nach Norm ${g("norm")}</th>
      </tr></thead>
      <tbody>
        ${n.map(t=>a`
          <tr class=${[t.offen?"warn":"",t.korrigiert?"korrigiert":"",t.k===l.k?"gewaehlt":""].join(" ")}
            @click=${()=>{l.k=t.k,p()}}>
            <td><input type="checkbox" .checked=${k(t.geprueft)} aria-label="geprüft"
              @change=${i=>m([{op:"schicht",id:e.id,k:t.k,feld:"geprueft",wert:i.target.checked}],{leise:!0})}></td>
            <td><input type="number" step="0.01" min="0" class="tief" .value=${k(String(t.von))}
              @change=${i=>m([{op:"schicht",id:e.id,k:t.k,feld:"oben",wert:xe(i)}])}></td>
            <td><input type="number" step="0.01" min="0" class="tief" .value=${k(String(t.bis))}
              @change=${i=>m([{op:"schicht",id:e.id,k:t.k,feld:"unten",wert:xe(i)}])}></td>
            <td class="bodenart">${ct(e,t)}
              ${t.offen?a`<div class="warnung">⚠ nicht klassifiziert</div>`:u}
              ${t.korrigiert?a`<div class="leise klein">korrigiert</div>`:u}</td>
            <td class="beschreibung">${t.beschreibung||a`<span class="leise">– keine Beschreibung –</span>`}
              ${t.hinweise.length?a`<div class="leise klein">${t.hinweise.join(" · ")}</div>`:u}</td>
            <td class="norm">
              ${t.norm.benennung?a`<div>${t.norm.benennung}</div>`:u}
              ${t.norm.din4023?a`<code title="Kurzzeichen nach DIN 4023">${t.norm.din4023}</code>`:u}
              ${t.norm.bodengruppe?a` <code title="Bodengruppe nach DIN 18196">${t.norm.bodengruppe}</code>`:u}
              ${[t.norm.konsistenz,t.norm.lagerung,t.norm.kalk,t.norm.bodenfarbe].filter(Boolean).length?a`<div class="leise klein">${[t.norm.konsistenz,t.norm.lagerung,t.norm.kalk,t.norm.bodenfarbe].filter(Boolean).join(" · ")}</div>`:u}
              ${t.norm.hinweise.length?a`<div class="klein hinweis-norm" title=${t.norm.hinweise.join(`
`)}>ℹ ${t.norm.hinweise[0]}${t.norm.hinweise.length>1?` (+${t.norm.hinweise.length-1})`:""}</div>`:u}
              ${t.vorschlag?a`
                <button class="vorschlag" @click=${i=>{i.stopPropagation(),m([{op:"vorschlag",id:e.id,k:t.k}])}}
                  title=${`Vorschlag nach Norm: ${t.vorschlag.benennung}${t.vorschlag.sicher?"":" (unsicher)"}`}>
                  → ${t.vorschlag.klasse} übernehmen</button>${g("vorschlag")}`:u}
            </td>
          </tr>`)}
      </tbody>
    </table>`}function ht(e,n){tt(e,n);const t=Number(e.id.split(":")[0]),i=!!l.z.dokumente[t]?.pdf,s=me?.schluessel===`${l.sig}/${t}/${(n[0]?.quelle.seite??e.seite)-1}`?me.daten:null,r=n.find(c=>c.k===l.k)??null,o=(c,v)=>{if(!c||!s)return u;const z=s.px_je_pt*F;return a`<div class=${`bbox ${v}`} style=${`left:${c[0]*z}px;top:${c[1]*z}px;width:${(c[2]-c[0])*z}px;height:${(c[3]-c[1])*z}px`}></div>`},d=n.map(c=>c.quelle.bbox).filter(c=>!!c&&c.length===4),h=d.length?[Math.min(...d.map(c=>c[0])),Math.min(...d.map(c=>c[1])),Math.max(...d.map(c=>c[2])),Math.max(...d.map(c=>c[3]))]:null;return a`
    <aside class="quelle-spalte">
      <div class="saeule-rahmen">
        ${Xn(n.map(c=>({k:c.k,von:c.von,bis:c.bis,farbe:c.farbe,warn:c.offen,geprueft:c.geprueft,titel:`${pe(c.von)}–${pe(c.bis)} m: ${c.bodenart}${c.beschreibung?` – ${c.beschreibung}`:""}`})),{hoehe:420,gewaehlt:l.k,waehlen:c=>{l.k=c,p()}})}
      </div>
      ${i?a`<div class="pdf-rahmen">
        <div class="pdf-kopf"><b>Quelle im PDF</b> ${g("quelle")}
          <span class="fueller"></span>
          ${i?a`<button class="symbol" title="kleiner" @click=${()=>{F=Math.max(.25,F/1.4),p()}}>−</button>
            <button class="symbol" title="größer" @click=${()=>{F=Math.min(1.5,F*1.4),p()}}>+</button>`:u}
        </div>
        ${s?a`
          ${gt(h,s.px_je_pt*F)}
          <div class="pdf-seite">
            <div class="pdf-flaeche" style=${`width:${s.breite_pt*s.px_je_pt*F}px;height:${s.hoehe_pt*s.px_je_pt*F}px`}>
              <img src=${s.url} alt=${`Seite ${s.seite+1}`} draggable="false">
              ${o(h,"saeule-bbox")}
              ${o(r?.quelle.bbox,"schicht-bbox")}
            </div>
          </div>`:a`<p class="leise klein">Seite wird geladen …</p>`}
      </div>`:u}
    </aside>`}let Je="";function gt(e,n){const t=`${l.bid}/${F}`;return!e||Je===t?u:(requestAnimationFrame(()=>{const i=document.querySelector(".pdf-seite");i&&(i.scrollLeft=Math.max(0,e[0]*n-i.clientWidth/3),i.scrollTop=Math.max(0,e[1]*n-40),Je=t)}),u)}function pt(){const e=l.z,n=l.details.get(l.bid),t=e.bohrungen.find(r=>r.id===l.bid),i=t?Number(t.id.split(":")[0]):0,s=!e.dokumente[i]?.pdf;return a`
    <div class=${`schritt-bohrungen ${s?"ohne-pdf":""}`}>
      ${st()}
      ${lt()}
      <section class="bohrung-detail">
        ${t?a`
          ${ut(t)}
          ${n?a`
            ${dt(t,n.schichten)}
            <div class="detail-fuss">
              <button class="primaer" title="Alle Schichten dieser Bohrung als geprüft markieren und zur nächsten offenen (G)"
                @click=${zn}>✓ Alle Schichten geprüft – weiter</button>
              <button class="leise-knopf" ?disabled=${!t.schichten_geprueft}
                @click=${()=>m([{op:"bohrung_pruefen",id:t.id,wert:!1}])}>Prüfung zurücknehmen</button>
              <span class="fueller"></span>
              <button class="gefahr" @click=${()=>m([{op:"entfernen",id:t.id}])}>🗑 Aus dem Modell entfernen</button>
            </div>`:a`<p class="leise">Schichten werden geladen …</p>`}`:a`<p class="leise">Links eine Bohrung wählen.</p>`}
      </section>
      ${t&&n?ht(t,n.schichten):a`<aside class="quelle-spalte"></aside>`}
    </div>`}const S=(e,n=2)=>e==null||!Number.isFinite(e)?"":e.toLocaleString("de-DE",{minimumFractionDigits:n,maximumFractionDigits:n}),M=e=>{const n=e.target.value.trim().replace(",",".");return n===""?null:Number(n)};let $=null,fe="",X="plan",ie,Ne=250,Ee=100,Pe=100;const H=new Set;function Qe(e){const n=e.unterlage;return n?`${n.sha}/${n.seite}/${n.art}/${JSON.stringify(n.kalibrierung)}`:""}function Sn(e){const n=e.unterlage;if(!n)return $=null;if($&&$.schluessel===Qe(e))return $;const t=n.kalibrierung,i=o=>o&&!("n"in o)?o:null,s=i(t?.massstab),r=i(t?.hoehe);return $={schluessel:Qe(e),massArt:t?.massstab&&"n"in t.massstab?"n":"strecke",p1:s?{u:s.u1,v:s.v1}:null,p2:s?{u:s.u2,v:s.v2}:null,meter:s?.meter??null,n:t?.massstab&&"n"in t.massstab?t.massstab.n:null,hoeheArt:t?.hoehe?"n"in t.hoehe?"n":"strecke":"gleich",h1:r?{u:r.u1,v:r.v1}:null,h2:r?{u:r.u2,v:r.v2}:null,hoeheMeter:r?.meter??null,hoeheN:t?.hoehe&&"n"in t.hoehe?t.hoehe.n:null,bezug:t?.bezug?{u:t.bezug.u,v:t.bezug.v}:null,x:t?.bezug?.x??null,y:t?.bezug?.y??null,drehung:t?.drehung??0,epsg:t?.epsg??e.viewer.epsg??null},$}function Re(e,n=!1){const t=$,i=e.unterlage;if(!t||!i)return null;let s=null;if(t.massArt==="n"&&t.n&&t.n>0&&(s={n:t.n}),t.massArt==="strecke"&&t.p1&&t.p2&&t.meter&&t.meter>0&&(s={u1:t.p1.u,v1:t.p1.v,u2:t.p2.u,v2:t.p2.v,meter:t.meter}),!s||!t.bezug||t.x===null||t.y===null)return null;let r=null;return i.art==="schnitt"&&t.hoeheArt==="n"&&t.hoeheN&&t.hoeheN>0&&(r={n:t.hoeheN}),i.art==="schnitt"&&t.hoeheArt==="strecke"&&t.h1&&t.h2&&t.hoeheMeter&&t.hoeheMeter>0&&(r={u1:t.h1.u,v1:t.h1.v,u2:t.h2.u,v2:t.h2.v,meter:t.hoeheMeter}),{massstab:s,hoehe:r,bezug:{...t.bezug,x:t.x,y:t.y},drehung:i.art==="plan"?t.drehung:0,epsg:i.art==="plan"?t.epsg:null,gesperrt:n}}function G(){const e=l.z;l.entwurf=Re(e);const n=l.viewer;n&&$&&(n.editor.hilfsmarken({strecke:$.massArt==="strecke"?[$.p1,$.p2]:[],hoehe:$.hoeheArt==="strecke"?[$.h1,$.h2]:[],bezug:$.bezug}),l.entwurf&&n.editor.vorschau(l.entwurf)),p()}async function mt(e){const n=l.viewer;if(!n||!$)return;fe=e,p();const t=await n.editor.bildpunktWaehlen();if(fe="",!t||!$||l.z?.unterlage?.kalibrierung?.gesperrt){p();return}$[e]=t,G()}async function Ye(e){l.viewer?.editor.waehlenAbbrechen();const n=Re(l.z,e);if(!n){D("Für die Kalibrierung fehlen Maßstab oder Bezugspunkt.","warn");return}await m([{op:"kalibrierung",wert:n}])&&(l.entwurf=null,D(e?"Plan kalibriert und gesperrt – jetzt die Bohrungen ziehen.":"Kalibrierung übernommen.","ok"),await l.viewer?.ansicht(l.z?.unterlage?.art==="schnitt"?"sued":"oben"))}async function bt(e){const n=l.z.unterlage;n?.kalibrierung&&await m([{op:"kalibrierung",wert:{...n.kalibrierung,gesperrt:e}}])}async function ft(e){const n=e.target,t=n.files?.[0];if(n.value="",!t)return;const i=await w(()=>f.unterlage(l.sig,t,X,0),"Unterlage wird gelesen …");i&&(P(i),l.entwurf=null,p(),await ve(),await l.viewer?.lageModus(!0),await l.viewer?.ansicht(i.unterlage?.art==="schnitt"?"sued":"oben"))}async function Xe(e,n){const t=await w(()=>f.unterlageSeite(l.sig,e,n),"Seite wird gelesen …");t&&(P(t),l.entwurf=null,p(),await ve(),await l.viewer?.ansicht(n==="schnitt"?"sued":"oben"))}async function $t(){if(!confirm("Unterlage mit ihrer Kalibrierung entfernen? Gesetzte Bohrungen behalten ihre Lage."))return;const e=await w(()=>f.unterlageEntfernen(l.sig));e&&(P(e),l.entwurf=null,p(),await ve())}const R=(e,n,t=!0)=>a`<details class="abschnitt" ?open=${t}><summary>${e}</summary><div class="abschnitt-inhalt">${n}</div></details>`;function Y(e,n,t,i){return a`<button class=${`punkt ${fe===n?"aktiv":""} ${t?"gesetzt":""}`} ?disabled=${i}
    @click=${()=>mt(n)}>${fe===n?"… im Plan klicken":t?`${e} ✓`:e}</button>`}function kt(e){const n=fn(e.epsg,e.x,e.y);return n?a`<p class=${`klein ${n.ok?"ok":"warn"}`}>${n.ok?"✓":"⚠"} ${n.text}</p>`:u}function wt(e){const n=e.unterlage,t=Sn(e),i=!!n.kalibrierung?.gesperrt,s=n.art==="plan",r=t.p1&&t.p2?Math.hypot(t.p2.u-t.p1.u,t.p2.v-t.p1.v):null,o=Re(e),d=o?An(o.massstab,n.mm_pro_px):null,h=e.viewer.bohrungen.filter(c=>c.x!==null&&(s?!/Plan|Viewer/.test(c.quelle):c.gok_bekannt));return a`
    <p class=${`status ${n.kalibrierung?i?"ok":"":"warn"}`}>
      ${n.kalibrierung?a`${i?"🔒 gesperrt · ":""}${je(n)}${s?` · ${Te(n.kalibrierung.epsg)}`:""}`:"nicht kalibriert"}
      ${l.entwurf&&JSON.stringify({...l.entwurf,gesperrt:!1})!==JSON.stringify({...n.kalibrierung??{},gesperrt:!1})?a`<br><span class="leise">Vorschau: ${je(n,l.entwurf)} (noch nicht übernommen)</span>`:u}
    </p>
    ${i?a`
      <p class="leise klein">Der Plan liegt fest. ${s?"Bohrungen unten mit „Punkte setzen“ in den Plan klicken oder im Viewer ziehen – nur in x/y":"Bohrungen im Viewer ziehen – entlang der Station; die Höhe nur ohne GOK aus dem PDF"}.</p>
      <button @click=${()=>bt(!1)}>🔓 Entsperren (neu kalibrieren)</button>`:a`
      <fieldset class="gruppe">
        <legend>1 · Maßstab ${g("massstab")}</legend>
        <div class="umschalter">
          <label><input type="radio" name="massart" .checked=${t.massArt==="strecke"} @change=${()=>{t.massArt="strecke",G()}}> Strecke messen</label>
          <label><input type="radio" name="massart" .checked=${t.massArt==="n"} @change=${()=>{t.massArt="n",G()}}> 1:n eingeben</label>
        </div>
        ${t.massArt==="strecke"?a`
          <div class="zeile">${Y("Punkt 1","p1",t.p1,!1)}${Y("Punkt 2","p2",t.p2,!1)}</div>
          <div class="zeile">
            <span class="leise klein">${r?`gemessen ${S(r,0)} px`:"zwei Punkte anklicken"}</span>
            <label class="inline">wahre Länge <input type="number" step="0.01" min="0" class="kurz" .value=${k(t.meter===null?"":String(t.meter))}
              @input=${c=>{t.meter=M(c),G()}}> m</label>
          </div>`:a`
          <label class="inline">Maßstab 1: <input type="number" step="1" min="1" class="kurz" .value=${k(t.n===null?"":String(t.n))}
            @input=${c=>{t.n=M(c),G()}}></label>`}
        ${d?a`<p class="leise klein">ergibt 1:${Math.round(d).toLocaleString("de-DE")}</p>`:u}
      </fieldset>
      ${s?u:a`
        <fieldset class="gruppe">
          <legend>Höhenmaßstab ${g("hoehe")}</legend>
          <div class="umschalter">
            <label><input type="radio" name="hoeheart" .checked=${t.hoeheArt==="gleich"} @change=${()=>{t.hoeheArt="gleich",G()}}> wie Länge</label>
            <label><input type="radio" name="hoeheart" .checked=${t.hoeheArt==="n"} @change=${()=>{t.hoeheArt="n",G()}}> 1:n</label>
            <label><input type="radio" name="hoeheart" .checked=${t.hoeheArt==="strecke"} @change=${()=>{t.hoeheArt="strecke",G()}}> messen</label>
          </div>
          ${t.hoeheArt==="n"?a`<label class="inline">Höhe 1: <input type="number" step="1" min="1" class="kurz"
              .value=${k(t.hoeheN===null?"":String(t.hoeheN))} @input=${c=>{t.hoeheN=M(c),G()}}></label>`:u}
          ${t.hoeheArt==="strecke"?a`
            <div class="zeile">${Y("Höhe oben","h1",t.h1,!1)}${Y("Höhe unten","h2",t.h2,!1)}</div>
            <label class="inline">Höhenunterschied <input type="number" step="0.01" min="0" class="kurz"
              .value=${k(t.hoeheMeter===null?"":String(t.hoeheMeter))} @input=${c=>{t.hoeheMeter=M(c),G()}}> m</label>`:u}
        </fieldset>`}
      <fieldset class="gruppe">
        <legend>2 · Bezugspunkt ${g("bezug")}</legend>
        <div class="zeile">${Y("Punkt im Plan wählen","bezug",t.bezug,!1)}</div>
        <div class="zeile">
          <label class="feld schmal"><span>${s?"Rechtswert":"Station [m]"}</span>
            <input type="number" step="0.01" .value=${k(t.x===null?"":String(t.x))} @input=${c=>{t.x=M(c),G()}}></label>
          <label class="feld schmal"><span>${s?"Hochwert":"Höhe [m NHN]"}</span>
            <input type="number" step="0.01" .value=${k(t.y===null?"":String(t.y))} @input=${c=>{t.y=M(c),G()}}></label>
        </div>
        ${s?a`
          <label class="feld breit"><span>Koordinatensystem (EPSG) ${g("epsg")}</span>
            ${Fe(t.epsg,c=>{t.epsg=c,G()})}</label>
          ${kt(t)}`:u}
        ${h.length?a`
          <label class="inline klein">oder von Bohrung
            <select @change=${c=>{const v=e.viewer.bohrungen.find(z=>z.id===c.target.value);v&&(t.x=v.x,t.y=s?v.y:v.gok,G())}}>
              <option value="">–</option>
              ${h.map(c=>a`<option value=${c.id}>${c.code}</option>`)}
            </select></label>`:u}
      </fieldset>
      ${s?a`
        <fieldset class="gruppe">
          <legend>3 · Drehung ${g("drehung")}</legend>
          <div class="zeile">
            <label class="inline"><input type="number" step="0.1" class="kurz" .value=${k(String(t.drehung))}
              @input=${c=>{t.drehung=M(c)??0,G()}}> ° gegen den Uhrzeigersinn</label>
          </div>
        </fieldset>`:u}
      <div class="zeile knopfzeile">
        <button ?disabled=${!o} @click=${()=>Ye(!1)}>Übernehmen</button>
        <button class="primaer" ?disabled=${!o} @click=${()=>Ye(!0)}>🔒 Übernehmen und sperren</button>
        ${g("sperren")}
      </div>
      ${n.kalibrierung?a`<button class="link klein" @click=${()=>m([{op:"kalibrierung",wert:null}])}>Kalibrierung zurücksetzen</button>`:u}`}`}function vt(e){const n=e.unterlage;return n?a`
    <p><b>${n.name}</b> <span class="leise">· ${n.art==="plan"?"Lageplan":"Längsschnitt"}</span></p>
    <div class="zeile">
      ${(n.seiten??1)>1?a`<label class="inline">Seite <select @change=${t=>Xe(Number(t.target.value),n.art)}>
          ${Array.from({length:n.seiten},(t,i)=>a`<option value=${i} .selected=${i===n.seite}>${i+1}</option>`)}
        </select></label>`:u}
      <label class="inline">Ansicht <select @change=${t=>Xe(n.seite,t.target.value)}>
        <option value="plan" .selected=${n.art==="plan"}>Lageplan</option>
        <option value="schnitt" .selected=${n.art==="schnitt"}>Längsschnitt</option>
      </select></label>
    </div>
    <label class="inline">Deckkraft ${g("deckkraft")}
      <input type="range" min="0.1" max="1" step="0.05" .value=${String(l.viewer?.editor.deckkraft??.85)}
        @input=${t=>{l.viewer&&(l.viewer.editor.deckkraft=Number(t.target.value),l.viewer.editor.bildSichtbarkeit())}}></label>
    <button class="link klein" @click=${$t}>Unterlage entfernen</button>`:a`
      <p class="leise klein">Lageplan (von oben) oder Längsschnitt (von der Seite) als PDF – er liegt im Viewer unter den Bohrungen.</p>
      <div class="umschalter">
        <label><input type="radio" name="neueart" .checked=${X==="plan"} @change=${()=>{X="plan"}}> Lageplan</label>
        <label><input type="radio" name="neueart" .checked=${X==="schnitt"} @change=${()=>{X="schnitt"}}> Längsschnitt</label>
      </div>
      <label class="datei-knopf"><input type="file" accept=".pdf,application/pdf" @change=${ft}>PDF wählen …</label>`}function zt(e){const n=e.unterlage,t=!n||!!n.kalibrierung?.gesperrt,i=e.viewer.bohrungen.filter(o=>o.x===null),s=e.lage_modus==="reihe",r=!s&&n?.art==="plan"&&!!n.kalibrierung?.gesperrt;return a`
    ${t?u:a`<p class="warnung">Erst kalibrieren und sperren (🔒) – dann Punkte setzen oder Bohrungen ziehen.</p>`}
    ${r?St(e):u}
    ${i.length?a`
      <p class="klein">Ohne Lage (${i.length}) – ${r?"anklicken = als Nächste setzen, oder":""} in den Viewer ziehen
        ${g("ohne_lage")}</p>
      <div class="parkplatz">
        ${i.map(o=>a`<span class=${`park ${t?"":"gesperrt"} ${l.punktModus&&l.naechste===o.id?"aktiv":""}`}
          title=${r?"Klick: als nächste Bohrung setzen · Ziehen: direkt in den Viewer":"In den Viewer ziehen"}
          @pointerdown=${d=>l.viewer?.editor.ziehenStart(d,o.id,!0)}
          @click=${()=>{r&&$e(!0,o.id)}}>${o.code}</span>`)}
      </div>`:a`<p class="leise klein">Alle Bohrungen im Modell haben eine Lage.</p>`}
    ${r?yt(e):u}
    ${s?Bt(e):u}`}function $e(e,n){l.punktModus=e,n!==void 0?l.naechste=n:e&&!l.naechste&&(l.naechste=Nn()),l.viewer?.editor.punktModusSetzen(e),p()}function St(e){const n=e.viewer.bohrungen.filter(i=>i.x===null),t=e.viewer.bohrungen.filter(i=>i.x!==null);return a`
    <div class="zeile">
      <button class=${l.punktModus?"primaer":""} @click=${()=>$e(!l.punktModus)}>
        ${l.punktModus?"● Punkte setzen – Klick in den Plan":"＋ Punkte im Plan setzen"}</button>
      ${l.punktModus?a`<button class="leise-knopf" @click=${()=>$e(!1)}>Fertig (Esc)</button>`:u}
      ${g("punkte")}
    </div>
    ${l.punktModus?a`
      <label class="feld breit"><span>Nächster Klick setzt</span>
        <select class="naechste" @change=${i=>{l.naechste=i.target.value,p()}}>
          <option value="" .selected=${!l.naechste}>– freien Punkt (später zuordnen) –</option>
          ${n.length?a`<optgroup label="Ohne Lage">
            ${n.map(i=>a`<option value=${i.id} .selected=${l.naechste===i.id}>${i.code}</option>`)}</optgroup>`:u}
          ${t.length?a`<optgroup label="Mit Lage (neu setzen)">
            ${t.map(i=>a`<option value=${i.id} .selected=${l.naechste===i.id}>${i.code}</option>`)}</optgroup>`:u}
        </select></label>
      <p class="leise klein">Danach ist automatisch die nächste Bohrung ohne Lage dran.</p>`:u}`}function yt(e){const n=e.viewer.bohrungen.filter(r=>r.x!==null&&/Plan|Viewer/.test(r.quelle)),t=e.viewer.bohrungen,i=t.filter(r=>r.x===null);if(!n.length&&!e.punkte.length)return u;const s=(r,o)=>a`<span class="leise klein">R ${S(r)}<br>H ${S(o)}</span>`;return a`
    <p class="klein">Gesetzte Punkte (${n.length+e.punkte.length})</p>
    <table class="tabelle kompakt punkte">
      <tbody>
        ${e.punkte.map(r=>a`
          <tr class=${`frei ${l.viewer?.editor.punktGewaehlt===r.id?"gewaehlt":""}`}>
            <td><button class="link" title="Im Viewer wählen" @click=${()=>{l.viewer?.editor.punktWaehlen(r.id),p()}}>◆ ${r.id}</button></td>
            <td>${s(r.x,r.y)}</td>
            <td><select aria-label=${`${r.id} zuordnen`} @change=${o=>{const d=o.target.value;d&&m([{op:"punkt_zuordnen",punkt:r.id,bohrung:d}])}}>
              <option value="" selected>– Bohrung zuordnen –</option>
              ${i.length?a`<optgroup label="Ohne Lage">${i.map(o=>a`<option value=${o.id}>${o.code}</option>`)}</optgroup>`:u}
              <optgroup label="Mit Lage (ersetzen)">${t.filter(o=>o.x!==null).map(o=>a`<option value=${o.id}>${o.code}</option>`)}</optgroup>
            </select></td>
            <td><button class="symbol" title="Punkt löschen" @click=${()=>m([{op:"punkt_loeschen",punkt:r.id}])}>✕</button></td>
          </tr>`)}
        ${n.map(r=>a`
          <tr class=${l.viewer?.editor.ausgewaehlt===r.id?"gewaehlt":""}>
            <td><button class="link" title="Im Viewer wählen" @click=${()=>{l.viewer?.nadelWaehlen(r.id),p()}}>● ${r.code}</button></td>
            <td>${s(r.x,r.y)}</td>
            <td><select aria-label=${`${r.code} umhängen`} @change=${o=>{const d=o.target.value;d==="-"?m([{op:"lage_loesen",id:r.id}]):d&&d!==r.id&&m([{op:"lage_umhaengen",id:r.id,nach:d}])}}>
              <option value=${r.id} selected>${r.code}</option>
              <option value="-">– Zuordnung lösen (freier Punkt) –</option>
              ${i.length?a`<optgroup label="Andere Bohrung (ohne Lage)">${i.map(o=>a`<option value=${o.id}>${o.code}</option>`)}</optgroup>`:u}
            </select></td>
            <td><button class="symbol" title="Lage entfernen (Bohrung wieder ohne Lage)" @click=${()=>m([{op:"lage_entfernen",id:r.id}])}>✕</button></td>
          </tr>`)}
      </tbody>
    </table>`}function Bt(e){const n=e.reihe.map(i=>i.id),t=(i,s)=>{const r=[...n],[o]=r.splice(i,1);r.splice(Math.max(0,Math.min(r.length,i+s)),0,o),m([{op:"reihe",reihenfolge:r}],{leise:!0})};return a`
    <div class="zeile">
      <label class="inline">Standardabstand ${g("standardabstand")}
        <input type="number" step="1" min="1" class="kurz" .value=${k(String(e.reihe_standard))}
          @change=${i=>m([{op:"reihe",standard:M(i)}])}> m</label>
    </div>
    <table class="tabelle kompakt reihe">
      <thead><tr><th></th><th>Bohrung</th><th>Abstand [m] ${g("reihe")}</th><th>Station [m]</th></tr></thead>
      <tbody>
        ${e.reihe.map((i,s)=>a`
          <tr>
            <td class="pfeile"><button class="symbol" ?disabled=${s===0} title="nach vorn" @click=${()=>t(s,-1)}>▲</button><button class="symbol"
              ?disabled=${s===n.length-1} title="nach hinten" @click=${()=>t(s,1)}>▼</button></td>
            <td>${i.code}</td>
            <td><input type="number" step="0.1" min="0" class="kurz" ?disabled=${s===0} .value=${k(i.abstand===null?"":String(i.abstand))}
              @change=${r=>m([{op:"reihe",abstand:{[i.id]:M(r)}}],{leise:!0})}></td>
            <td><input type="number" step="0.1" class="kurz" .value=${k(String(i.station))} title=${i.quelle_text}
              @change=${r=>m([{op:"reihe",station:{[i.id]:M(r)}}],{leise:!0})}></td>
          </tr>`)}
      </tbody>
    </table>`}async function Gt(e){const n=e.target,t=[...n.files??[]];if(n.value="",!t.length)return;const i=ie===void 0?l.z?.viewer.epsg??null:ie,s=await w(()=>f.dgm(l.sig,t,i),"DGM wird gelesen …");if(s){P(s),p();const r=s.gelaende?.pruefung?.warnungen.length??0;D(r?"DGM geladen – Hinweise zum Vergleich beachten.":"DGM geladen.",r?"warn":"ok")}}async function Dt(){const e=await w(()=>f.dgmAbruf(l.sig,Ee),"DGM wird beim Land abgerufen …");if(e){P(e),p();const n=e.gelaende?.pruefung?.warnungen.length??0;D(n?"DGM vom Land geladen – Hinweise zum Vergleich beachten.":"DGM vom Land geladen.",n?"warn":"ok")}}function en(e){return e.lage_modus!=="koordinaten"?u:a`
    <div class="zeile">
      <label class="inline">Rand <input type="number" min="0" max="1000" step="25" class="kurz" aria-label="Rand um die Bohrungen"
        .value=${k(String(Ee))} @change=${n=>{Ee=M(n)??100}}> m</label>
      <button @click=${Dt} title="Sendet den Ausschnitt um die Bohrungen an den Dienst des Landes">
        DGM vom Land abrufen</button>${g("dgm_land")}
    </div>
    <p class="leise klein">Brandenburg mit Berlin und NRW (DGM1, WCS). Sendet den Ausschnitt um die Bohrungen an den Dienst.</p>`}async function Mt(){if(!confirm("DGM aus dem Projekt entfernen? Übernommene GOK bleiben (Quelle DGM)."))return;const e=await w(()=>f.dgmEntfernen(l.sig));e&&(P(e),p())}const ye={ok:["✓","ok"],abweichung:["⚠ weicht ab","warn"],ohne_gok:["GOK fehlt",""],aus_dgm:["aus dem DGM","leise"],ausserhalb:["außerhalb","leise"],ohne_lage:["ohne Lage","leise"],anderes_system:["anderes EPSG","warn"]},nn=e=>e===null?"":Math.abs(e)<.005?S(0):`${e>0?"+":""}${S(e)}`;function _t(e){const n=e.gelaende,t=h=>a`<label class="datei-knopf"><input type="file" multiple aria-label="DGM-Dateien"
    accept=".xyz,.txt,.csv,.asc,.tif,.tiff,.zip,.gz" @change=${Gt}>${h}</label>`,i=ie===void 0?e.viewer.epsg??null:ie,s=a`<label class="feld breit"><span>System der Datei (XYZ, ASCII) ${g("dgm_epsg")}</span>
    ${Fe(i,h=>{ie=h,p()},"System der DGM-Datei")}</label>`;if(!n)return a`
      <p class="leise klein">DGM-Kachel(n) des Landes (Open Data, z. B. DGM1) als XYZ, ASCII-Raster oder GeoTIFF, auch als
        ZIP – Höhen in m NHN. Damit prüft die App die GOK, schlägt fehlende vor und legt das Gelände ins Modell.</p>
      ${en(e)}
      ${s}
      ${t("DGM-Dateien wählen …")}`;const r=n.info,o=n.pruefung,d=r.quelle;return a`
    <p><b>${r.name}</b><br><span class="leise klein">${Te(r.epsg)} · Raster ${S(r.dx,1)} m ·
      ${r.spalten.toLocaleString("de-DE")} × ${r.zeilen.toLocaleString("de-DE")} · ${S(r.zmin,1)} – ${S(r.zmax,1)} m NHN</span></p>
    ${d?a`<p class="leise klein">${d.anbieter} · <a href=${d.beleg} target="_blank" rel="noopener">${d.lizenz}</a> ·
      ${d.namensnennung} · abgerufen ${d.abgerufen}</p>`:u}
    ${n.fehler?a`<p class="warnung klein">${n.fehler}</p>`:u}
    ${o?a`
      <table class="tabelle kompakt gelaende">
        <thead><tr><th>Bohrung</th><th class="zahl">GOK</th><th class="zahl">DGM</th><th class="zahl">Δ [m]</th><th></th></tr></thead>
        <tbody>
          ${o.zeilen.map(h=>a`
            <tr class=${ye[h.status][1]}>
              <td><button class="link" title="Im Viewer wählen" @click=${()=>{l.viewer?.nadelWaehlen(h.id),p()}}>${h.code}</button></td>
              <td class="zahl">${S(h.gok)}</td>
              <td class="zahl">${S(h.dgm)}</td>
              <td class="zahl">${nn(h.differenz)}</td>
              <td class=${`klein ${ye[h.status][1]}`}>${h.status==="ohne_gok"?a`<button class="klein" title="GOK aus dem DGM übernehmen (Quelle DGM)"
                    @click=${()=>m([{op:"gok_aus_dgm",ids:[h.id]}])}>übernehmen</button>`:ye[h.status][0]}</td>
            </tr>`)}
        </tbody>
      </table>
      ${o.verglichen?a`<p class="leise klein">${o.verglichen} verglichen · Median ${nn(o.median)} m ·
        größte Abweichung ${S(o.max)} m (unauffällig bis ${S(o.toleranz,1)} m)</p>`:u}
      ${o.warnungen.map(h=>a`<p class="warnung klein">⚠ ${h}</p>`)}
      ${o.vorschlaege>1?a`<button @click=${()=>m([{op:"gok_aus_dgm"}])}>
        Alle ${o.vorschlaege} fehlenden GOK aus dem DGM übernehmen</button>`:u}`:u}
    ${en(e)}
    ${s}
    <div class="zeile">${t("Andere DGM-Dateien …")}
      <button class="link klein" @click=${Mt}>DGM entfernen</button></div>`}async function Lt(){const e=await w(()=>f.sgdAbfrage(l.sig,Ne),"Dienste der Länder werden abgefragt …");if(!e?.sgd)return;P(e),H.clear(),p();const n=e.sgd;D(`${n.treffer.length} Bohrungen der Länder im Umkreis von ${S(n.radius,0)} m`+(n.fehler.length?` – ${n.fehler.length} Meldung(en) der Dienste`:""),n.fehler.length?"warn":"ok")}async function xt(){const e=[...H].map(t=>({dienst:t.slice(0,t.indexOf("/")),id:t.slice(t.indexOf("/")+1)})),n=await w(()=>f.sgdUebernehmen(l.sig,e),"Schichtdaten werden beim Land geholt …");if(n){P(n.zustand),H.clear();for(const t of n.meldungen)D(t,"ok");await ve(),p()}}function Nt(e){const n=e.treffer.filter(r=>!r.uebernehmbar&&!r.uebernommen&&!r.gutachten);if(!n.length)return u;const t=r=>e.quellen.find(o=>o.dienst===r)?.land??r,i=r=>{const o=n.filter(d=>d.schichten===r);return o.length?`${o.length} (${[...new Set(o.map(d=>t(d.dienst)))].join(", ")})`:""},s=[i("grafik")&&`${i("grafik")} nur mit Kopfdaten: das Land gibt das Schichtenverzeichnis nur als Bild heraus (Profil ↗), nicht als Daten`,i("portal")&&`${i("portal")} nur als Hinweis: das Schichtenverzeichnis liegt beim Land, der Dienst nennt nur die Kopfdaten`,i("keine")&&`${i("keine")} ohne Schichtenverzeichnis`,i("ohne Petrographie")&&`${i("ohne Petrographie")} mit Schichten ohne Petrographie`].filter(Boolean);return a`<p class="leise klein sgd-warum">Nicht übernehmbar: ${s.join("; ")}. Ohne Schichten entsteht kein Modell –
    sie zu erfinden wäre falsch. Lage, GOK und Teufe sehen Sie hier; die Schichten im Profil des Landes. Übernehmbar sind
    Bohrungen mit Schichtdaten in BoreholeML (NRW, Baden-Württemberg, Hamburg).</p>`}function Et(e){return e.gutachten?a`<span class="ok" title="Dieselbe Bohrung im Gutachten">= ${e.gutachten}</span>`:e.uebernommen?a`<span class="ok">✓ im Projekt</span>`:e.schichten==="boreholeml"?a`${e.schichten_n} Schichten`:e.schichten==="grafik"&&e.profil?a`<a href=${e.profil} target="_blank" rel="noopener">Profil ↗</a>`:e.schichten==="portal"?a`<span class="leise" title="Nur ein Hinweis: das Schichtenverzeichnis liegt beim Land, nicht in diesem Dienst">beim Land</span>`:a`<span class="leise">${e.schichten==="ohne Petrographie"?"ohne Petrographie":"keine Schichten"}</span>`}async function Pt(){const e=await w(()=>f.gebaeudeAbruf(l.sig,Pe),"Gebäude werden beim Land abgerufen …");e&&(P(e),p(),D(`${e.gebaeude?.anzahl??0} Gebäude geladen – im Modell als Umgebung.`,"ok"))}async function At(){const e=await w(()=>f.gebaeudeEntfernen(l.sig));e&&(P(e),p())}function Kt(e){if(e.lage_modus!=="koordinaten")return a`<p class="leise klein">Nur mit Lage nach Koordinaten.</p>`;const n=e.gebaeude,t=a`
    <div class="zeile">
      <label class="inline">Rand <input type="number" min="0" max="1000" step="25" class="kurz" aria-label="Rand der Gebäude"
        .value=${k(String(Pe))} @change=${s=>{Pe=M(s)??100}}> m</label>
      <button @click=${Pt} title="Lädt die Kacheln (1 × 1 km) um die Bohrungen beim Land">
        ${n?"Gebäude neu abrufen":"Gebäude vom Land abrufen"}</button>${g("gebaeude")}
    </div>`;if(!n)return a`
      <p class="leise klein">3D-Gebäudemodelle LoD2 von Berlin, Brandenburg und NRW (CityGML, m NHN) als Umgebung im Modell und
        im IFC. Lädt die Kacheln von 1 × 1 km um die Bohrungen – das verrät die Lage des Projekts auf etwa 1 km.</p>
      ${t}`;const i=n.quelle;return a`
    <p><b>${n.anzahl.toLocaleString("de-DE")} Gebäude</b> · ${n.flaechen.toLocaleString("de-DE")} Flächen ·
      ${i.kacheln} Kachel${i.kacheln===1?"":"n"} <span class="leise klein">· abgerufen ${i.abgerufen}</span></p>
    ${i.dienste.map(s=>a`<p class="leise klein">${s.anbieter} · <a href=${s.beleg} target="_blank" rel="noopener">${s.lizenz}</a> ·
      ${s.namensnennung}</p>`)}
    ${i.ohne_kachel.length?a`<p class="leise klein">ohne Kachel beim Land: ${i.ohne_kachel.join(", ")}</p>`:u}
    ${i.fehler.map(s=>a`<p class="warnung klein">⚠ ${s}</p>`)}
    ${n.hinweis?a`<p class="warnung klein">⚠ ${n.hinweis}</p>`:u}
    <p class="leise klein">Im Viewer mit dem Knopf „Gebäude“ ein- und ausblendbar.</p>
    ${t}
    <button class="link klein" @click=${At}>Gebäude entfernen</button>`}function Tt(e){if(e.lage_modus==="reihe")return a`<p class="leise klein">Nur mit Lage nach Koordinaten.</p>`;const n=e.sgd,t=a`
    <p class="leise klein">Bohrungen aus den Datenbanken der Geologischen Dienste um die Mitte des Projekts.
      <b>Die Abfrage sendet die Lage des Projekts an den Dienst des Landes.</b></p>
    <div class="zeile">
      <label class="inline">Umkreis <input type="number" min="10" max="2000" step="50" class="kurz" aria-label="Umkreis der Abfrage"
        .value=${k(String(Ne))} @change=${d=>{Ne=M(d)??250}}> m</label>
      <button @click=${Lt}>${n?"Neu abfragen":"Abfragen"}</button>
    </div>`;if(!n)return t;const i=n.gegenprobe,s=i.anzahl>0&&(i.lage_max??0)<=1&&(i.gok_max??0)<=.5,r=n.treffer.slice(0,60),o=n.treffer.filter(d=>d.uebernehmbar).length;return a`
    ${t}
    <p class="klein">${n.treffer.length} Bohrungen im Umkreis von ${S(n.radius,0)} m · ${n.zeit}</p>
    ${i.anzahl?a`<p class=${`klein ${s?"ok":"warnung"}`}>${s?"✓":"⚠"} ${i.anzahl} Bohrungen des Gutachtens auch
      beim Land: Lage ≤ ${S(i.lage_max)} m${i.gok_max!==null?a`, GOK ≤ ${S(i.gok_max)} m`:u}${s?"":" – Lage und GOK prüfen"}</p>`:u}
    ${n.fehler.map(d=>a`<p class="warnung klein">${d.dienst}: ${d.fehler}</p>`)}
    ${Kn(n.portale)}
    ${r.length?a`
      <table class="tabelle kompakt sgd">
        <thead><tr><th></th><th>Bohrung</th><th class="zahl">Abstand</th><th class="zahl">GOK</th><th class="zahl">Teufe</th><th>Schichten</th></tr></thead>
        <tbody>
          ${r.map(d=>{const h=`${d.dienst}/${d.id}`;return a`<tr class=${d.gutachten?"doppelt":""}>
              <td>${d.uebernehmbar?a`<input type="checkbox" aria-label=${`${d.name} übernehmen`} .checked=${H.has(h)}
                @change=${c=>{c.target.checked?H.add(h):H.delete(h),p()}}>`:u}</td>
              <td title=${`${d.dienst} · ID ${d.id}${d.datum?` · ${d.datum}`:""}`}>${d.name}</td>
              <td class="zahl">${S(d.abstand,0)}</td>
              <td class="zahl">${S(d.gok)}</td>
              <td class="zahl">${S(d.teufe,1)}</td>
              <td class="klein">${Et(d)}</td>
            </tr>`})}
        </tbody>
      </table>
      ${n.treffer.length>r.length?a`<p class="leise klein">… und ${n.treffer.length-r.length} weitere (Umkreis verkleinern)</p>`:u}`:u}
    ${o?a`<button class="primaer" ?disabled=${!H.size} @click=${xt}>
      Ausgewählte übernehmen (${H.size})</button>
      <p class="leise klein">Nur Bohrungen mit Schichtdaten in BoreholeML (NRW, Baden-Württemberg, Hamburg); sie kommen mit Quelle und Lizenz ins Projekt.</p>`:u}
    ${Nt(n)}
    ${n.quellen.map(d=>a`<p class="leise klein">Quelle: ${d.namensnennung} · <a href=${d.beleg} target="_blank" rel="noopener">Dienst</a></p>`)}
    <button class="link klein" @click=${async()=>{const d=await w(()=>f.sgdVerwerfen(l.sig));d&&(P(d),p())}}>Abfrage verwerfen</button>`}function Ft(e){const n=l.viewer;n&&(!e.unterlage||e.unterlage.kalibrierung?.gesperrt||!$?n.editor.hilfsmarken({}):n.editor.hilfsmarken({strecke:$.massArt==="strecke"?[$.p1,$.p2]:[],hoehe:$.hoeheArt==="strecke"?[$.h1,$.h2]:[],bezug:$.bezug}))}let tn=!1;function Rt(e){const n=e.standort;return R(a`Standort ${g("standort")}`,a`
    <p class="klein"><b>${S(n.x,1)} / ${S(n.y,1)}</b> · EPSG:${n.epsg}</p>
    <p class="leise klein">Georeferenziert über den Punkt: kein Lageplan, keine Kalibrierung – die Bohrungen der Länder
      kommen mit ihren Koordinaten. Ein Gutachten dazu (Schritt Start) wird ein neues Projekt mit Lageplan.</p>
    ${gn(n.dienste)}`)}let an=!1;function Ot(e){const n=e.viewer.bohrungen.length,t=e.viewer.bohrungen.filter(i=>i.x===null).length;return e.standort?a`<p class="stand-satz ok">Standort ${Math.round(e.standort.x)} / ${Math.round(e.standort.y)} · EPSG:${e.standort.epsg}
      ${n?a` · ${n} Bohrungen der Länder`:a` · <span class="leise">Bohrungen der Länder unten abfragen</span>`}</p>`:n?t?a`<p class="stand-satz warn">${t} von ${n} Bohrungen ohne Lage – auf dem Plan setzen oder Koordinaten eingeben</p>`:a`<p class="stand-satz ok">✓ Alle ${n} Bohrungen haben eine Lage${e.lage_modus==="reihe"?" (Reihe)":""}
      – jetzt mit den Bohrungen der Länder vergleichen</p>`:u}function jt(){const e=l.z;Sn(e),Ft(e);const n=e.lage_modus!=="reihe"&&e.unterlage?.art==="plan"&&!!e.unterlage.kalibrierung?.gesperrt;l.punktModus&&!n&&(l.punktModus=!1),l.viewer?.editor.punktModusSetzen(l.punktModus),tn||(tn=!0,window.addEventListener("keydown",r=>{r.key==="Escape"&&l.schritt==="lage"&&l.punktModus&&$e(!1)}));const t=e.viewer.bohrungen.length>0&&e.viewer.bohrungen.every(r=>r.x!==null),i=e.lage_modus==="koordinaten"&&t&&!e.unterlage,s=an||!!(e.gelaende||e.gebaeude);return a`
    <div class="app-panel links">
      ${Ot(e)}
      ${e.standort?Rt(e):a`
        ${R(a`Lage der Bohrungen ${g("lage_art")}`,a`
          <div class="umschalter">
            <label><input type="radio" name="lagemodus" .checked=${e.lage_modus==="koordinaten"}
              @change=${()=>m([{op:"lage_modus",wert:"koordinaten"}])}> Koordinaten (Lageplan)</label>
            <label><input type="radio" name="lagemodus" .checked=${e.lage_modus==="reihe"}
              @change=${()=>m([{op:"lage_modus",wert:"reihe"}])}> Reihe (Längsschnitt)</label>
          </div>`)}
        ${R(a`Unterlage ${g("unterlage")}`,vt(e),!i)}
        ${e.unterlage?R(a`Kalibrieren`,wt(e)):u}
        ${R(a`Bohrungen setzen`,zt(e),!i)}`}
      ${R(a`Vergleich mit Bohrungen der Länder${e.sgd?.gegenprobe.anzahl?" ✓":""} ${g("sgd")}`,Tt(e))}
      <details class="erweitert" ?open=${s}
        @toggle=${r=>{an=r.target.open}}>
        <summary>Erweitert <span class="leise klein">Gelände · Gebäude · Darstellung</span></summary>
        ${R(a`Gelände (DGM)${e.gelaende?.pruefung?.warnungen.length?" ⚠":e.gelaende?" ✓":""} ${g("gelaende")}`,_t(e),!!e.gelaende)}
        ${R(a`Gebäude (LoD2)${e.gebaeude?" ✓":""} ${g("gebaeude")}`,Kt(e),!!e.gebaeude)}
        ${R(a`Darstellung`,a`
          <label class="inline">Ø Bohrsäulen ${g("durchmesser")}
            <input type="number" step="0.1" min="0" class="kurz" placeholder=${`auto ${S(e.durchmesser_auto,1)}`}
              .value=${k(e.durchmesser===null?"":String(e.durchmesser))}
              @change=${r=>m([{op:"durchmesser",wert:M(r)}])}> m</label>
          <p class="leise klein">Je Bohrung im Schritt Bohrungen (Ø Säule). Leer = automatisch nach Modellgröße.</p>`,!1)}
      </details>
      ${e.hinweise.length?a`<div class="hinweisliste">${e.hinweise.map(r=>a`<p class="klein">ℹ ${r}</p>`)}</div>`:u}
    </div>`}const B=(e,n=2)=>e==null?"–":e.toLocaleString("de-DE",{minimumFractionDigits:n,maximumFractionDigits:n}),yn={idw:"IDW",tps:"Dünnplatten-Spline",implizit:"implizit (GemPy)"};let de=null,Bn="",rn=!1,O={x:"",y:""},Oe=null;async function Ht(){const e=l.sig;if(!e)return;const n=await w(()=>f.analyse(e,100),"Kreuzprobe und Unsicherheit werden gerechnet …");n&&(de=n,Bn=l.modell?.schluessel??"",Oe=null,n.mitte&&!O.x&&(O={x:String(n.mitte[0]),y:String(n.mitte[1])}),p())}async function Gn(){const e=l.sig,n=Number(O.x.replace(",",".")),t=Number(O.y.replace(",","."));if(!e||!Number.isFinite(n)||!Number.isFinite(t))return;const i=await w(()=>f.analysePunkt(e,n,t),"Virtuelle Bohrung …");i&&(Oe=i,p())}function It(e){const n=e.kreuzprobe;return a`
    <table class="tabelle kompakt">
      <thead><tr><th>Methode</th><th title="mittlerer Fehler der Schichtgrenzen an der weggelassenen Bohrung">mittl. Fehler [m]</th>
        <th>max. [m]</th><th>Grenzen</th></tr></thead>
      <tbody>${Object.entries(n.methoden).map(([t,i])=>a`
        <tr class=${t===n.methode_modell?"gewaehlt":""}>
          <td>${yn[t]??t}${t===n.methode_modell?a` <span class="leise klein">(Modell)</span>`:u}${t===n.beste?a` <b title="sagt die Bohrungen am besten voraus">★</b>`:u}</td>
          <td class="zahl">${B(i.gesamt.mae)}</td><td class="zahl">${B(i.gesamt.max)}</td><td class="zahl">${i.gesamt.n}</td>
        </tr>`)}</tbody>
    </table>`}function Ut(e){const n=e.unsicherheit,t=e.kreuzprobe.methoden[e.kreuzprobe.methode_modell];return a`
    <table class="tabelle kompakt">
      <thead><tr><th>Einheit</th>
        <th title="mittlerer Fehler der Unterkante in der Kreuzprobe">Kreuzprobe [m]</th>
        <th title="Streuung der Unterkante im Mittel über die Fläche (± σ)">σ Unterkante [m]</th>
        <th title="95 % der Fläche liegen darunter">σ 95 % [m]</th>
        <th title="falsch als vorhanden / fehlend vorhergesagt">Ausdehnung</th>
        <th title="Volumen mit 5 %- und 95 %-Wert aus der Messung der Grenzen">Volumen [m³]</th>
        <th title="größte Abweichung der Unterkante zur anderen Interpolation">anders interpoliert [m]</th></tr></thead>
      <tbody>${n.einheiten.map((i,s)=>{const r=t?.einheiten[s],o=r?r.praesenz.falsch_vorhanden+r.praesenz.falsch_fehlend:0;return a`<tr>
          <td>${i.name}</td>
          <td class="zahl">${r?.n?B(r.mae):a`<span class="leise">–</span>`}</td>
          <td class="zahl">${i.unterkante_bezifferbar?B(i.sigma_mittel_m):a`<span class="leise" title="keine Bohrung erreicht die Unterkante">offen</span>`}</td>
          <td class="zahl">${i.unterkante_bezifferbar?B(i.sigma_p95_m):"–"}</td>
          <td class="zahl ${o?"warn":""}">${o?`${o} ×`:"✓"}</td>
          <td class="zahl klein">${Math.round(i.volumen_m3.modell).toLocaleString("de-DE")}${i.volumen_m3.p5!==null?a`<br><span class="leise">${Math.round(i.volumen_m3.p5).toLocaleString("de-DE")}–${Math.round(i.volumen_m3.p95).toLocaleString("de-DE")}</span>`:u}</td>
          <td class="zahl">${B(i.methoden_differenz_m.max)}</td>
        </tr>`})}</tbody>
    </table>`}function Wt(e){const n=e.vorschlaege??[];return n.length?a`
    <h4>Wo die nächste Bohrung am meisten bringt ${g("erkundung")}</h4>
    <table class="tabelle kompakt vorschlag">
      <thead><tr><th>#</th><th>Rechtswert</th><th>Hochwert</th><th>Grund</th><th title="nächste vorhandene Bohrung">Abstand [m]</th><th></th></tr></thead>
      <tbody>${n.map((t,i)=>a`<tr>
        <td>${i+1}</td><td class="zahl">${B(t.x,1)}</td><td class="zahl">${B(t.y,1)}</td><td class="klein">${t.grund}</td>
        <td class="zahl">${B(t.abstand_naechste_bohrung_m,0)}</td>
        <td><button class="link" @click=${()=>{O={x:String(t.x),y:String(t.y)},Gn()}}>virtuell bohren</button></td></tr>`)}</tbody>
    </table>
    <p class="leise klein">Ein Vorschlag aus der Unsicherheit des Modells – Zugang, Leitungen und Baufeld kennt es nicht.</p>`:u}function Vt(e){const n=Oe;return a`
    <h4>Virtuelle Bohrung ${g("virtuell")}</h4>
    <div class="zeile knopfzeile">
      <label class="inline">Rechtswert <input class="mittel" .value=${O.x} @input=${t=>{O.x=t.target.value}}></label>
      <label class="inline">Hochwert <input class="mittel" .value=${O.y} @input=${t=>{O.y=t.target.value}}></label>
      <button @click=${Gn}>Bohren</button>
    </div>
    <p class="leise klein">Im System der Bohrungen${e.epsg?` (EPSG ${e.epsg})`:""}; vorbelegt mit der Mitte des Modells.</p>
    ${n?.fehler?a`<p class="warn">${n.fehler}</p>`:u}
    ${n&&!n.fehler?a`
      <p class="klein">GOK ${B(n.gok_nhn)} m NHN · ${B(n.abstand_m,1)} m von ${n.naechste_bohrung} · <span class="leise">${n.herkunft}</span></p>
      <table class="tabelle kompakt virtuell">
        <thead><tr><th>Tiefe [m]</th><th>Einheit</th><th>Unterkante [m NHN]</th><th>± σ [m]</th><th>95 % [m NHN]</th></tr></thead>
        <tbody>${n.schichten.map(t=>a`<tr>
          <td class="zahl">${B(t.tiefe_oben_m)}–${B(t.tiefe_unten_m)}</td><td>${t.einheit}</td>
          <td class="zahl">${B(t.unten_nhn)}${t.unterkante_offen?a` <span class="leise klein">offen</span>`:u}</td>
          <td class="zahl">${B(t.sigma_unten_m)}</td>
          <td class="zahl klein">${t.unten_95_nhn?`${B(t.unten_95_nhn[0])} … ${B(t.unten_95_nhn[1])}`:"–"}</td></tr>`)}</tbody>
      </table>
      ${n.hinweise.map(t=>a`<p class="leise klein">${t}</p>`)}`:u}`}function Ct(){const e=l.modell;if(!e?.bericht)return u;const n=de&&Bn===e.schluessel?de:null,t=de&&!n,i=n;return a`
    <details class="erweitert karte analyse" ?open=${rn||!!i}
      @toggle=${s=>{rn=s.target.open}}>
      <summary>Ground Analysis ${g("analyse")} <span class="leise klein">Kreuzprobe · Unsicherheit · virtuelle Bohrung</span></summary>
      <div class="zeile knopfzeile">
        <button class=${i?"":"primaer"} @click=${Ht}>${i?"Neu rechnen":"Analyse rechnen"}</button>
        ${t?a`<span class="warn klein">Das Modell hat sich geändert – neu rechnen.</span>`:u}
      </div>
      ${i?.fehler?a`<p class="warn">${i.fehler}</p>`:u}
      ${i&&!i.fehler?a`
        <h4>Kreuzprobe <span class="leise klein">(${i.kreuzprobe.bohrungen} Bohrungen, je eine weggelassen)</span></h4>
        ${It(i)}
        ${[...i.kreuzprobe.hinweise,...i.unsicherheit.hinweise].map(s=>a`<p class="hinweis klein">⚑ ${s}</p>`)}
        <h4>Unsicherheit je Einheit <span class="leise klein">(${i.unsicherheit.laeufe} Läufe, ${yn[i.unsicherheit.methode]??i.unsicherheit.methode})</span></h4>
        ${Ut(i)}
        <details class="klein"><summary class="leise">Annahmen</summary>
          <ul>${i.unsicherheit.annahmen.map(s=>a`<li>${s}</li>`)}</ul></details>
        ${Wt(i)}
        ${Vt(i)}`:u}
    </details>`}let ee=0,U="",Dn="";const Be=e=>e.replace(/[<>&"]/g,n=>({"<":"&lt;",">":"&gt;","&":"&amp;",'"':"&quot;"})[n]);async function Zt(){const e=l.sig;if(!e||!l.viewer)return;const n=await w(()=>f.analyseFlaeche(e,ee),"Unsicherheit wird gerechnet …");if(n){if(n.fehler){l.viewer.meldung(n.fehler,6e3);return}l.viewer.unsicherheit({name:n.name,punkte:n.punkte,dreiecke:n.dreiecke,sigma:n.sigma,sigma_max:n.sigma_max}),U=n.name,Dn=l.modell?.schluessel??"",n.hinweis&&l.viewer.meldung(n.hinweis,6e3),p()}}function qt(){l.viewer?.unsicherheit(null),U="",p()}let ae=null,Mn="";async function Jt(){const e=l.sig;if(!e||!l.viewer)return;const n=await w(()=>f.analyseGrundwasser(e),"Grundwasserfläche …");if(n){if(n.fehler){l.viewer.meldung(n.fehler,6e3);return}ae=n,Mn=l.modell?.schluessel??"",l.viewer.grundwasser(n.flaeche??null),n.flaeche||l.viewer.meldung(n.hinweise?.[0]??"keine Grundwasserfläche",6e3),p()}}function Qt(){l.viewer?.grundwasser(null),ae=null,p()}function Yt(){ae&&Mn!==(l.modell?.schluessel??"")&&(l.viewer?.grundwasser(null),ae=null);const e=ae,n=(t,i=2)=>t.toLocaleString("de-DE",{minimumFractionDigits:i,maximumFractionDigits:i});return a`
    <div class="zeile">
      <button @click=${Jt}>Grundwasserfläche zeigen</button>${g("grundwasser")}
      ${e?a`<button class="link" @click=${Qt}>Grundwasser ausblenden</button>`:u}
    </div>
    ${e?a`<div class="klein grundwasser">
      <p>${e.gemessen} gemessene${e.trocken?`, ${e.trocken} trockene`:""} von ${e.staende?.length??0} Bohrungen
        ${e.flaeche?a` · ${n(e.flaeche.z_min)} bis ${n(e.flaeche.z_max)} m NHN`:u}
        ${e.kreuzprobe?a` · Kreuzprobe ⌀ ${n(e.kreuzprobe.mae_m)} m, max. ${n(e.kreuzprobe.max_m)} m`:u}</p>
      ${(e.hinweise??[]).length?a`<ul class="hinweise">${e.hinweise.map(t=>a`<li>${t}</li>`)}</ul>`:u}
    </div>`:u}`}async function Xt(){const e=l.sig,n=l.viewer;if(!e||!n)return;const t=await n.punktWaehlen();if(!t)return;const i=await w(()=>f.analysePunkt(e,t.e,t.n),"Virtuelle Bohrung …");if(!i)return;if(i.fehler){n.meldung(i.fehler,6e3);return}const s=(o,d=2)=>o==null?"–":o.toLocaleString("de-DE",{minimumFractionDigits:d,maximumFractionDigits:d}),r=i.schichten.map(o=>`<tr><td>${s(o.tiefe_oben_m)}–${s(o.tiefe_unten_m)} m</td><td>${Be(o.einheit)}</td>
    <td>${o.sigma_unten_m===null?o.unterkante_offen?"offen":"–":`± ${s(o.sigma_unten_m)} m`}</td></tr>`).join("");n.tafel("Virtuelle Bohrung",`<p>${s(i.x,1)} / ${s(i.y,1)} · GOK ${s(i.gok_nhn)} m NHN · ${s(i.abstand_m,1)} m von ${Be(i.naechste_bohrung??"")}</p>
    <table><tr><th>Tiefe</th><th>Einheit</th><th>Unterkante</th></tr>${r}</table>
    <p><i>${Be(i.herkunft??"")}</i></p>`)}function ei(){const e=l.modell?.bericht;return!e||l.modell?.fehler?u:(ee>=e.einheiten.length&&(ee=0),U&&Dn!==(l.modell?.schluessel??"")&&(l.viewer?.unsicherheit(null),U=""),a`
    <section class="abschnitt-flach analyse-viewer">
      <h3>Ground Analysis im Viewer ${g("analyse")}</h3>
      <div class="zeile">
        <select @change=${n=>{ee=Number(n.target.value)}}>
          ${e.einheiten.map((n,t)=>a`<option value=${t} .selected=${t===ee}>${n.name}</option>`)}
        </select>
        <button @click=${Zt}>Unsicherheit zeigen</button>
        ${U?a`<button class="link" @click=${qt}>Unsicherheit ausblenden</button>`:u}
      </div>
      ${U?a`<p class="leise klein">Gezeigt: Unterkante ${U}, gefärbt nach σ (grün sicher, rot unsicher).</p>`:u}
      <div class="zeile"><button @click=${Xt}>Virtuelle Bohrung: Punkt im Viewer wählen</button>${g("virtuell")}</div>
      ${Yt()}
    </section>`)}const T=(e,n=1)=>e==null?"–":e.toLocaleString("de-DE",{minimumFractionDigits:n,maximumFractionDigits:n});let C="",Ge=null,ln="",sn=!1;function ni(e){return!e||e.quelle!=="DGM"?"aus den GOK der Bohrungen":`aus dem DGM (an den Bohrungen auf die GOK, GOK − DGM bis ${T(Number(e.gok_minus_dgm_max_m),2)} m)`}function ti(){const e=l.z.einstellungen,n=(r,o)=>m([{op:"einstellungen",[r]:o}]),t=(r,o,d,h,c)=>{const v=e[r];return a`
      <div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${v===null} @change=${z=>n(r,z.target.checked?null:h)}> ${o} automatisch</label>${g(c)}
        ${v===null?u:a`<input type="number" step="any" class="kurz" .value=${k(String(v))}
          @change=${z=>n(r,Number(z.target.value))}> ${d}`}
      </div>`},i=l.modell?.bericht?.parameter??{},s=e.methode!=="idw"||e.puffer!==null||e.raster!==null||e.basis!==null||!e.gok_relativ||!e.gelaende_dgm;return a`
    <details class="erweitert karte" ?open=${sn||s}
      @toggle=${r=>{sn=r.target.open}}>
      <summary>Erweitert <span class="leise klein">Interpolation · Puffer · Raster · Basis · Gelände</span></summary>
      <div class="einstellung">
        <span>Interpolation ${g("methode")}</span>
        <label class="inline"><input type="radio" name="methode" .checked=${e.methode==="idw"} @change=${()=>n("methode","idw")}> IDW</label>
        <label class="inline"><input type="radio" name="methode" .checked=${e.methode==="tps"} @change=${()=>n("methode","tps")}> Dünnplatten-Spline</label>
        <label class="inline" title=${l.info?.implizit?"GemPy: je Fläche ein Skalarfeld, Orientierung aus den Kontakten (docs/27)":"GemPy ist auf diesem Server nicht installiert (requirements-analyse.txt)"}><input
          type="radio" name="methode" ?disabled=${!l.info?.implizit&&e.methode!=="implizit"} .checked=${e.methode==="implizit"}
          @change=${()=>n("methode","implizit")}> Implizit (GemPy)</label>
      </div>
      ${e.methode==="implizit"?ii():u}
      ${t("puffer","Puffer","m",Number(i.puffer_m??20),"puffer")}
      ${t("raster","Raster","m",Number(i.raster_m??5),"raster")}
      ${t("basis","Modellbasis","m NHN",Math.floor(Number(i.basis_nhn??0)),"basis")}
      <div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${e.gok_relativ} @change=${r=>n("gok_relativ",r.target.checked)}> fehlende GOK: Gelände = 0 m</label>${g("gok_relativ")}
      </div>
      ${l.z.gelaende?a`<div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${e.gelaende_dgm} @change=${r=>n("gelaende_dgm",r.target.checked)}> Gelände aus dem DGM</label>${g("gelaende_dgm")}
      </div>`:u}
      ${i.raster_m!==void 0?a`<p class="leise klein">gerechnet: Puffer ${T(Number(i.puffer_m),0)} m · Raster ${T(Number(i.raster_m))} m ·
        Basis ${T(Number(i.basis_nhn),2)} m NHN · Fläche ${T(Number(i.flaeche_m2)/1e4,2)} ha ·
        Gelände ${ni(i.gelaende)}</p>`:u}
    </details>`}function ii(){const e=l.modell?.bericht,n=e?.parameter?.orientierung??[];if(!e||!n.length)return a`<p class="leise klein">Orientierung je Einheit: nach dem Rechnen hier eingebbar.</p>`;const t={...l.z.einstellungen.orientierung??{}},i=(r,o,d)=>{const h=t[r]??{fallrichtung:NaN,fallwinkel:NaN},c=d.trim()===""?NaN:Number(d.replace(",",".")),v={...h,[o]:c};if(Number.isNaN(v.fallrichtung)&&Number.isNaN(v.fallwinkel))delete t[r];else if(Number.isNaN(v.fallrichtung)||Number.isNaN(v.fallwinkel)){t[r]=v;return}else t[r]=v;const z=Object.fromEntries(Object.entries(t).filter(([,N])=>!Number.isNaN(N.fallrichtung)&&!Number.isNaN(N.fallwinkel)));m([{op:"einstellungen",orientierung:Object.keys(z).length?z:null}])},s=(r,o,d,h)=>a`
    <input type="number" step="any" min="0" max=${o==="fallwinkel"?80:360} class="kurz" title=${h}
      placeholder="–" .value=${k(d===void 0||Number.isNaN(d)?"":String(d))}
      @change=${c=>i(r,o,c.target.value)}>`;return a`
    <div class="einstellung">
      <span>Orientierung je Einheit ${g("orientierung")}</span>
      <table class="klein orientierung">
        <thead><tr><th>Einheit</th><th>berechnet</th><th>Fallrichtung °</th><th>Fallwinkel °</th></tr></thead>
        <tbody>${n.map(r=>a`<tr>
          <td>${r.einheit}</td>
          <td class="leise">${r.quelle==="Eingabe"?"Eingabe":r.fallen_grad===null?r.quelle:`${T(r.fallen_grad,1)}°${r.fallrichtung_grad!=null?` nach ${T(r.fallrichtung_grad,0)}°`:""} (${r.quelle})`}</td>
          <td>${s(r.einheit,"fallrichtung",t[r.einheit]?.fallrichtung,"Fallrichtung: Azimut von Nord im Uhrzeigersinn")}</td>
          <td>${s(r.einheit,"fallwinkel",t[r.einheit]?.fallwinkel,"Fallwinkel gegen die Horizontale, 0–80°")}</td>
        </tr>`)}</tbody>
      </table>
    </div>`}function ai(){const e=l.modell?.bericht;if(!e)return u;const n=l.z.vorgabe??e.vorlage_einheiten,t=JSON.stringify(n);(!Ge||ln!==t)&&(Ge=n.map(r=>({name:r.name,bodenarten:r.bodenarten.join(", ")})),ln=t);const i=Ge,s=()=>m([{op:"vorgabe",wert:i.filter(r=>r.name.trim()).map(r=>({name:r.name.trim(),bodenarten:r.bodenarten.split(",").map(o=>o.trim()).filter(Boolean)}))}]);return a`
    <section class="karte">
      <h3>Einheiten festlegen ${g("einheiten")}</h3>
      <p class="leise klein">${l.z.vorgabe?"Vorgegeben (eigene Einheiten).":"Automatisch korreliert – hier umbenennen oder Bodenarten zusammenlegen."}</p>
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
        <button ?disabled=${!l.z.vorgabe} @click=${()=>m([{op:"vorgabe",wert:null}])}>Automatisch korrelieren</button>
        <button class="primaer" @click=${s}>Mit diesen Einheiten rechnen</button>
      </div>
    </section>`}function ri(){const e=l.modell,n=e?.bericht,t=n?.einheiten.find(i=>i.name===C);return a`
    <div class="schritt-einheiten">
      <div class="spalte">
        ${ai()}
        ${ti()}
      </div>
      <div class="spalte breit">
        ${l.rechnet?a`<div class="karte"><div class="kreisel klein"></div> Modell wird gerechnet …</div>`:u}
        ${e?.fehler?a`<div class="karte warnung">Noch kein Modell: ${e.fehler}
          <button class="link" @click=${()=>j("lage")}>→ Lage setzen</button></div>`:u}
        ${n?a`
          <section class="karte">
            <h3>Einheiten (${n.einheiten.length})</h3>
            <table class="tabelle einheiten">
              <thead><tr><th></th><th>Einheit</th><th>Bodenarten</th><th>Volumen [m³]</th><th>max. Mächtigkeit [m]</th>
                <th title="in Bohrungen vorhanden / fehlt / unter der Endteufe">✓ / – / ?</th><th>Hinweise</th></tr></thead>
              <tbody>
                ${n.einheiten.map(i=>a`
                  <tr class=${i.name===C?"gewaehlt":""} @click=${()=>{C=C===i.name?"":i.name,p()}}>
                    <td><span class="farbfeld" style=${`background:${i.farbe}`}></span></td>
                    <td><b>${i.name}</b></td>
                    <td>${i.bodenarten.join(", ")}</td>
                    <td class="zahl">${Math.round(i.volumen_m3).toLocaleString("de-DE")}</td>
                    <td class="zahl">${T(i.maechtigkeit_max_m,2)}</td>
                    <td class="zahl">${i.bohrungen.vorhanden.length} / ${i.bohrungen.fehlt.length} / ${i.bohrungen.unbekannt.length}</td>
                    <td class="klein">${i.hinweise.join("; ")}</td>
                  </tr>`)}
              </tbody>
            </table>
          </section>
          <section class="karte profil-karte">
            <h3>Einheiten je Bohrung <span class="leise klein">(m NHN, Klick wählt die Einheit)</span></h3>
            <div class="profil-scroll">${et(n,{hoehe:380,gewaehlt:C,waehlen:i=>{C=i,p()}})}</div>
          </section>
          ${t?a`
            <section class="karte">
              <h3><span class="farbfeld" style=${`background:${t.farbe}`}></span> ${t.name}: Beschreibungen aus dem PDF</h3>
              <table class="tabelle kompakt">
                <thead><tr><th>Bohrung</th><th>Tiefe [m]</th><th>Bodenart</th><th>Beschreibung</th></tr></thead>
                <tbody>${t.schichten.map(i=>a`
                  <tr><td>${i.bohrung}</td><td class="zahl">${T(i.von,2)}–${T(i.bis,2)}</td><td>${i.bodenart??"unklassifiziert"}</td>
                    <td>${i.beschreibung||a`<span class="leise">–</span>`}</td></tr>`)}</tbody>
              </table>
            </section>`:u}
          ${Ct()}`:u}
      </div>
    </div>`}let ke="";async function li(){const e=await w(()=>f.einchecken(l.sig,ke));e&&(P(e.zustand),ke="",D(`Eingecheckt: v${e.eintrag.nr} · ${e.eintrag.stand.bohrungen[0]}/${e.eintrag.stand.bohrungen[1]} Bohrungen geprüft`,"ok"),p())}const _n=new Set([25831,25832,25833,4647,5650]);let ne=(()=>{try{return localStorage.getItem("groundtwin.organisation")??""}catch{return""}})();function si(){const e=l.z,n=e.bohrungen.filter(s=>s.modell),t=n.filter(s=>s.schichten_n>0&&s.schichten_geprueft===s.schichten_n&&s.x!==null&&s.y!==null&&s.epsg!==null&&_n.has(s.epsg)&&s.gok!==null&&e.lage_modus==="koordinaten"),i=`${f.exportUrl(l.sig,"boreholeml")}?organisation=${encodeURIComponent(ne)}`;return a`
    <label class="feld breit"><span>Organisation (Absender) ${g("boreholeml")}</span>
      <input type="text" aria-label="Organisation für BoreholeML" placeholder="z. B. Ingenieurbüro …" .value=${ne}
        @input=${s=>{ne=s.target.value;try{localStorage.setItem("groundtwin.organisation",ne)}catch{}p()}}></label>
    ${t.length?a`<a class="knopf" href=${i} download>Bohrungen für den Geologischen Dienst (BoreholeML 3.2)</a>`:a`<span class="knopf aus" title="Erst alle Schichten prüfen; Lage in ETRS89/UTM und GOK nötig">Bohrungen für den Geologischen Dienst (BoreholeML 3.2)</span>`}
    <p class="leise klein">${t.length} von ${n.length} Bohrungen exportierbar (vollständig geprüft, ETRS89/UTM, GOK).</p>`}let re=!1;async function oi(){if(!re){re=!0,p();try{const e=await fetch(f.exportUrl(l.sig,"3dtiles"));if(!e.ok){const i=await e.text();let s=i;try{s=JSON.parse(i).detail??i}catch{}D(`3D Tiles: ${s}`,"fehler",1e4);return}const n=/filename\*=UTF-8''([^;]+)/.exec(e.headers.get("content-disposition")??"")?.[1],t=document.createElement("a");t.href=URL.createObjectURL(await e.blob()),t.download=n?decodeURIComponent(n):"baugrundmodell_3dtiles.zip",t.click(),setTimeout(()=>URL.revokeObjectURL(t.href),1e4),D("3D Tiles exportiert (tileset.json + GLB, Höhen ellipsoidisch mit GCG2016).","ok")}finally{re=!1,p()}}}function ui(){const e=l.z;return e.lage_modus==="koordinaten"&&e.viewer.epsg!==null&&_n.has(e.viewer.epsg)?a`<button class="knopf" ?disabled=${re} @click=${oi}>${re?"3D Tiles werden erstellt …":"Baugrundmodell für Cesium (3D Tiles, ZIP)"}</button>${g("tiles3d")}`:a`<span class="knopf aus" title="Nur mit Lage nach Koordinaten in ETRS89/UTM">Baugrundmodell für Cesium (3D Tiles, ZIP)</span>`}const ci={anzeige:"Anzeige",fachdaten:"Fachdaten",bewertungsdaten:"Bewertungsdaten"},di=e=>e.split("-").reverse().join(".");function hi(e){return!e.bis||e.tage===null?e.regel:`bis ${di(e.bis)} (${e.tage>0?`noch ${e.tage} Tage`:e.tage===0?"heute":"verstrichen"})`}function gi(){const e=l.z.geoldg,n=e.zusammenfassung,t=(r,o)=>m([{op:"geoldg",[r]:o}],{leise:!0}),i=`${f.exportUrl(l.sig,"geoldg")}?organisation=${encodeURIComponent(ne)}`,s=e.punkte.filter(r=>r.quelle==="protokoll").map(r=>r.titel.replace(/, falls durchgeführt$/,""));return a`
    <section class="abschnitt-flach geoldg">
      <h3>Geologischer Dienst (GeolDG) ${g("geoldg")}</h3>
      <div class="zeile">
        <label class="inline">Beginn <input type="date" aria-label="Beginn der Untersuchung" .value=${e.angaben.beginn}
          @change=${r=>t("beginn",r.target.value)}></label>
        <label class="inline">Abschluss <input type="date" aria-label="Abschluss der Untersuchung" .value=${e.angaben.abschluss}
          @change=${r=>t("abschluss",r.target.value)}></label>${g("geoldg_abschluss")}
      </div>
      <label class="inline"><input type="checkbox" aria-label="Auftraggeber ist eine Behörde" .checked=${e.angaben.behoerde}
        @change=${r=>t("behoerde",r.target.checked)}> Auftraggeber ist eine Behörde</label>
      <ul class="fristen">${e.fristen.map(r=>a`
        <li class=${r.tage!==null&&r.tage<0?"warn":""} data-frist=${r.id}><b>${ci[r.id]}</b>
          <a href=${r.url} target="_blank" rel="noopener">${r.beleg}</a>: ${hi(r)}</li>`)}</ul>
      ${e.vorerkundung?a`
        <p class="klein">Noch keine eigene Bohrung: die geplante Erkundung spätestens zwei Wochen vor Beginn anzeigen
          (<a href=${e.anzeige_inhalt.url} target="_blank" rel="noopener">§ 8</a>). ${e.anzeige_inhalt.aus_der_app}</p>`:n.eigene?a`
        <p class="klein geoldg-stand">${n.eigene} eigene Bohrungen: für <b>${n.bereit}</b> liefert GroundTwin Lage, GOK, Endteufe
          und das geprüfte Schichtenverzeichnis, <b>${n.boreholeml}</b> davon im BoreholeML.${n.fremd?` ${n.fremd} Bohrungen der Länder liegen dem Land schon vor.`:""}</p>
        ${n.offen.length?a`<details class="protokoll"><summary class="warnung">⚠ ${n.offen.length} Bohrung(en) offen</summary>
          <ul>${n.offen.map(r=>a`<li><b>${r.code}</b>: ${r.was}</li>`)}</ul></details>`:u}
        <p class="klein leise">Aus dem Bohrprotokoll ergänzen (Spalten in pruefliste.csv): ${s.join(" · ")}.</p>
        <a class="knopf" href=${i} download>Paket für den Geologischen Dienst (ZIP)</a>`:u}
      <p class="leise klein">${e.quelle.hinweis}</p>
    </section>`}let on=!1;function pi(){const e=l.z,n=l.modell,t=n?.bericht,i=e.pruefstand,s=e.eincheckungen[e.eincheckungen.length-1],r=[["ifc","Baugrundmodell (IFC 4.3)"],["bericht","Prüfbericht (JSON)"]],o=[["einheiten","Einheiten-Vorlage (JSON)"],["extraktion","Extraktion (JSON)"],["eingabe","Modell-Eingabe mit Korrekturen (JSON)"],["projekt","Projektstand (JSON)"]],d=on||!!(e.geoldg?.angaben.beginn||e.geoldg?.angaben.abschluss);return a`
    <div class="app-panel rechts">
      <section class="abschnitt-flach">
        <h3>Modell</h3>
        ${e.reifegrad.stufe!=="Gutachten"?a`<p class=${`reife ${e.reifegrad.stufe==="Vorerkundung"?"vorerkundung":"gemischt"}`}>
          <b>${e.reifegrad.stufe}</b> – ${e.reifegrad.stufe==="Vorerkundung"?"Bohrungen aus Datenbanken der Länder, kein Gutachten: eine erste Vorstellung für die Planung der Erkundung.":Object.entries(e.reifegrad.anzahl).map(([h,c])=>`${c} ${h}`).join(", ")+": Bohrungen ohne Gutachten sind nicht gegen ein PDF geprüft."}
          ${g("reifegrad")}</p>`:u}
        ${l.rechnet?a`<p><span class="kreisel klein"></span> wird gerechnet …</p>`:u}
        ${n?.fehler?a`<p class="warnung">Noch kein Modell: ${n.fehler}</p>
          <button class="link" @click=${()=>j("lage")}>→ Lage setzen</button>`:u}
        ${t?a`
          <ul class="kennzahlen">
            <li><b>${t.einheiten.length}</b> Einheiten</li>
            <li><b>${t.bohrungen.length}</b> Bohrungen im Modell</li>
            <li class=${t.epsg?"":"warn"}>${t.epsg?`EPSG:${t.epsg}`:"lokales System"}</li>
            <li class=${t.pruefungen.alle_koerper_geschlossen?"ok":"warn"}>${t.pruefungen.alle_koerper_geschlossen?"Körper geschlossen":"Körper offen"}</li>
            <li class=${t.pruefungen.max_abweichung_an_bohrungen_m<.01?"ok":"warn"}>Abweichung an Bohrungen ${t.pruefungen.max_abweichung_an_bohrungen_m.toFixed(3)} m</li>
          </ul>`:u}
        <div class="zeile">
          <label class="inline"><input type="checkbox" .checked=${e.auto} @change=${h=>m([{op:"auto",wert:h.target.checked}],{leise:!0})}>
            automatisch nachführen</label>${g("auto")}
          <span class="fueller"></span>
          <button ?disabled=${l.rechnet} @click=${()=>En()}>Neu rechnen</button>
        </div>
      </section>

      <section class="abschnitt-flach">
        <h3>Prüfstand ${g("pruefstand")}</h3>
        <div class="balken"><span>Bohrungen <b>${i.bohrungen[0]}/${i.bohrungen[1]}</b></span><progress max=${i.bohrungen[1]||1} value=${i.bohrungen[0]}></progress></div>
        <div class="balken"><span>Schichten <b>${i.schichten[0]}/${i.schichten[1]}</b></span><progress max=${i.schichten[1]||1} value=${i.schichten[0]}></progress></div>
        <p class="klein">${i.unklassifiziert_offen?a`<span class="warnung">⚠ ${i.unklassifiziert_offen} Schicht(en) nicht klassifiziert</span>
          <button class="link" @click=${()=>j("bohrungen")}>prüfen</button>`:a`<span class="ok">✓ keine offenen Warnungen</span>`}
          · ${i.korrigiert} korrigiert · ${i.manuelle_lage} Lagen manuell · ${i.entfernt} entfernt</p>
        <p class=${`klein ${s&&!e.seit_einchecken_geaendert?"ok":"warn"}`}>
          ${s?`Eingecheckt: ${e.eingecheckt}${e.seit_einchecken_geaendert?" · seitdem geändert":""}`:"noch nicht eingecheckt"}</p>
        <div class="zeile">
          <input class="breit" placeholder="Kommentar (z. B. BK1–BK5 mit Anlage 2 verglichen)" .value=${ke}
            @input=${h=>{ke=h.target.value}}>
        </div>
        <div class="zeile"><button class="primaer" @click=${li}>✓ Stand einchecken</button>${g("einchecken")}</div>
        ${e.eincheckungen.length?a`
          <details class="protokoll"><summary>Protokoll (${e.eincheckungen.length})</summary>
            <ul>${[...e.eincheckungen].reverse().map(h=>a`
              <li><b>v${h.nr}</b> ${h.zeit} · ${h.stand.bohrungen[0]}/${h.stand.bohrungen[1]} Bohrungen, ${h.stand.schichten[0]}/${h.stand.schichten[1]} Schichten
                ${h.kommentar?a`<div class="leise klein">${h.kommentar}</div>`:u}</li>`)}</ul>
          </details>`:u}
      </section>

      <section class="abschnitt-flach">
        <h3>Export ${g("export")}</h3>
        <div class="export-liste">
          ${r.map(([h,c])=>a`<a class=${`knopf ${h==="ifc"?"primaer":""}`} href=${f.exportUrl(l.sig,h)}
            download>${c}</a>`)}
        </div>
      </section>

      <details class="erweitert" ?open=${d}
        @toggle=${h=>{on=h.target.open}}>
        <summary>Erweitert <span class="leise klein">Exporte · Cesium · BoreholeML · GeolDG · Ground Analysis · Darstellung</span></summary>
        <section class="abschnitt-flach">
          <h3>Weitere Exporte</h3>
          <div class="export-liste">
            ${o.map(([h,c])=>a`<a class="knopf" href=${f.exportUrl(l.sig,h)} download>${c}</a>`)}
            ${ui()}
            ${si()}
          </div>
        </section>
        ${gi()}
        ${ei()}
        <section class="abschnitt-flach">
          <h3>Darstellung</h3>
          <label class="inline">Überhöhung ${g("ueberhoehung")}
            <select @change=${async h=>{const c=Number(h.target.value);await l.viewer?.ueberhoehen(c),await m([{op:"ueberhoehung",wert:c}],{leise:!0})}}>
              ${[1,2,5,10,20].map(h=>a`<option value=${h} .selected=${e.ueberhoehung===h}>${h}×</option>`)}
            </select></label>
        </section>
      </details>

      ${n&&(n.hinweise.length||n.nicht_im_modell.length)?a`
        <section class="abschnitt-flach">
          <h3>Hinweise</h3>
          ${n.nicht_im_modell.length?a`<p class="klein"><b>Nicht im Modell:</b> ${n.nicht_im_modell.map(h=>`${h.code} (${h.grund})`).join(", ")}</p>`:u}
          ${n.hinweise.map(h=>a`<p class="klein">ℹ ${h}</p>`)}
        </section>`:u}
    </div>`}const un={gutachten:"",bohrungen:"Weiter: Lage",lage:"Weiter: Einheiten",einheiten:"Weiter: Modell",modell:""};function mi(e){const n=l.z;if(!n)return"";const t=n.pruefstand;return e==="gutachten"?"ok":e==="bohrungen"?t.unklassifiziert_offen?"warn":t.bohrungen[0]===t.bohrungen[1]&&t.bohrungen[1]?"ok":"":e==="lage"?n.viewer.bohrungen.filter(s=>s.x===null).length?"warn":"ok":e==="einheiten"||e==="modell"?l.modell?.fehler?"warn":l.modell?.bericht?"ok":"":""}function bi(){const e=l.z;return a`
    <header class="kopf">
      <div class="marke" @click=${()=>j("gutachten")} title="Start">
        <span class="logo">⛰</span>
        <span><b>GroundTwin</b> · Baugrundmodell</span>
      </div>
      <nav class="schritte" aria-label="Schritte">
        ${ce.map(n=>{const t=n.id!=="gutachten"&&!e,i=mi(n.id);return a`
            <button class=${`schritt-knopf ${l.schritt===n.id?"aktiv":""} ${i}`} ?disabled=${t}
              aria-current=${l.schritt===n.id?"step":"false"} @click=${()=>j(n.id)} title=${n.kurz}>
              <span class="nr">${i==="ok"&&l.schritt!==n.id?"✓":i==="warn"?"!":n.nr}</span>
              <span class="titel">${n.titel}</span>
            </button>`})}
      </nav>
      <div class="projekt">
        ${e&&e.reifegrad.stufe!=="Gutachten"?a`<span class=${`abzeichen ${e.reifegrad.stufe==="Vorerkundung"?"vorerkundung":"gemischt"}`}
          title=${e.reifegrad.stufe==="Vorerkundung"?"Bohrungen aus Datenbanken der Länder, kein Gutachten":"Gutachten und Bohrungen der Länder"}>${e.reifegrad.stufe}</span>`:u}
        ${e?a`<span class="projektname" title=${e.dokumente.map(n=>n.datei).join(", ")}>${e.name}</span>
          <details class="menue">
            <summary title="Projekt">⋯</summary>
            <div class="menue-inhalt" @click=${fi}>
              <button @click=${()=>j("gutachten")}>Anderes Projekt öffnen</button>
              <button @click=${$i}>Alle Korrekturen verwerfen …</button>
              <a href="viewer.html" target="_blank" rel="noopener">Viewer allein öffnen</a>
              <a href="dienste.html" target="_blank" rel="noopener">Dienste der Länder (Werkzeug)</a>
              ${l.info?a`<a href=${l.info.quellcode} target="_blank" rel="noopener">Quellcode (${l.info.lizenz})</a>`:u}
            </div>
          </details>`:u}
      </div>
    </header>`}function fi(e){e.currentTarget.closest("details")?.removeAttribute("open")}document.addEventListener("click",e=>{for(const n of document.querySelectorAll("details.menue[open]"))n.contains(e.target)||n.removeAttribute("open")});async function $i(){if(!l.sig||!confirm("Alle Korrekturen, Lagen, Prüfhaken und Eincheckungen dieses Projekts verwerfen – auch übernommene Bohrungen der Länder, DGM und Gebäude? Der Name bleibt."))return;const e=await w(()=>f.zuruecksetzen(l.sig));e&&await J(l.sig,e.standort?"lage":"bohrungen")}function ki(){if(l.schritt==="gutachten")return u;const e=ce.findIndex(s=>s.id===l.schritt),n=ce[e-1],t=ce[e+1],i=l.z?.pruefstand;return a`
    <footer class="fuss">
      ${n?a`<button @click=${()=>j(n.id)}>← ${n.titel}</button>`:u}
      <span class="fuss-status">${i?`${i.bohrungen[0]}/${i.bohrungen[1]} Bohrungen · ${i.schichten[0]}/${i.schichten[1]} Schichten geprüft`:""}
        ${i?.unklassifiziert_offen?a` · <span class="warnung">⚠ ${i.unklassifiziert_offen} nicht klassifiziert</span>`:u}</span>
      <span class="fueller"></span>
      ${t&&un[l.schritt]?a`<button class="primaer" @click=${()=>j(t.id)}>${un[l.schritt]} →</button>`:u}
    </footer>`}function wi(){return l.schritt==="gutachten"||!l.z?Jn():l.schritt==="bohrungen"?pt():l.schritt==="lage"?jt():l.schritt==="einheiten"?ri():pi()}function vi(){return a`
    ${bi()}
    <main class=${`inhalt schritt-${l.schritt}`}>
      <section id="schritt" class="schritt">${wi()}</section>
    </main>
    ${ki()}
    <div class="meldungen" aria-live="polite">
      ${l.meldungen.map(e=>a`<div class=${`meldung ${e.art}`}>${e.text}</div>`)}
    </div>
    ${l.beschaeftigt?a`<div class="beschaeftigt"><div class="kreisel"></div><span>${l.beschaeftigt}</span></div>`:u}`}const cn=document.getElementById("app");let Z=null;function zi(){xn(vi(),cn);const e=cn.querySelector("main");Z||(Z=document.createElement("div"),Z.id="buehne",Z.className="buehne"),Z.parentElement!==e&&e.append(Z),document.body.dataset.schritt=l.schritt}Pn(zi);async function Ln(){const[e,n,t]=location.hash.replace(/^#\/?/,"").split("/").map(decodeURIComponent);if(e&&e!==l.sig){if(await J(e,n||void 0),t&&l.schritt==="bohrungen"){const{bohrungWaehlen:i}=await De(async()=>{const{bohrungWaehlen:s}=await import("./store-BxtDZSAk.js").then(r=>r.k);return{bohrungWaehlen:s}},__vite__mapDeps([1,2]),import.meta.url);await i(t)}}else e||await j("gutachten")}window.addEventListener("hashchange",()=>void Ln());l.info=await w(()=>f.info())??null;p();await dn();await Ln();window.app=l;
