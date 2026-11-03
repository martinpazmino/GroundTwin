const __vite__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["./store-BfVmWQ09.js","./preload-helper-Ct5FWWRu.js"])))=>i.map(i=>d[i]);
import"./viewer-DAT6rRHi.js";import{_ as Xe}from"./preload-helper-Ct5FWWRu.js";import{b as a,A as u,w as T,l as $,m as Ye,k as De,D as en}from"./lage-aaRnPTcx.js";import{S as s,n as g,o as j,v,a as k,m as x,p as je,s as C,b as ce,c as ze,d as m,z as D,e as ue,f as nn,g as P,h as tn,i as an,j as ee}from"./store-BfVmWQ09.js";import"./three.core-Dd2BBCN2.js";const me={ocr:["OCR für Scans","Liest gescannte PDFs und Text, der nur als Linien gezeichnet ist (SHX). Langsamer; bei Vektor-PDFs nicht nötig."],beispiele:["Beispiele","Fertig ausgewertete Gutachten zum Ausprobieren. Echte Daten: Berlin (georeferenziert) und Talheim (ohne Koordinaten)."],pruefstand:["Prüfstand","Wie viele Bohrungen und Schichten Sie geprüft haben. Eine Korrektur zählt als geprüft. Der Stand wird beim Einchecken festgehalten."],alle_pruefen:["Alle geprüft","Markiert alle Schichten aller Bohrungen im Modell als geprüft – nur wenn Sie alles mit dem Gutachten verglichen haben. Zurücknehmen ist jederzeit möglich."],warnung:["Warnung","Eine Schicht, deren Bodenart nicht erkannt wurde (unklassifiziert). Bodenart wählen, den Vorschlag nach Norm übernehmen oder die Schicht als geprüft markieren."],bodenart:["Bodenart","Klasse für das Modell; Farbe nach DIN 4023 (Kies gelb, Sand orange, Schluff oliv, Ton violett …). Gleiche Bodenarten werden zu Einheiten verbunden."],norm:["Deutung nach Norm","Die Beschreibung aus dem PDF gelesen nach DIN 4023 / DIN EN ISO 14688-1: Hauptanteil, Nebenanteile (schwach ' / stark ¯), Kurzzeichen, Bodengruppe nach DIN 18196 (nur wenn genannt), Konsistenz. Steht auch im IFC (CPset_Bodenansprache)."],vorschlag:["Vorschlag nach Norm","Für eine unklassifizierte Schicht schlägt die Normen-Datenbank eine Bodenart aus der Beschreibung vor. Sie wird nur übernommen, wenn Sie klicken; danach gilt die Schicht als korrigiert."],geprueft:["Geprüft","Haken: Schicht mit dem Gutachten verglichen. Steht im IFC (Geprueft) und im Prüfstand."],tiefe:["Tiefe","Ober- und Unterkante in m unter Geländeoberkante (GOK). Geändertes wird als korrigiert markiert."],gok:["GOK","Ansatzhöhe der Bohrung in m NHN. Aus dem PDF oder hier eingetragen (manuell). Ohne GOK bei allen Bohrungen rechnet das Modell relativ (Gelände = 0 m)."],koordinaten:["Koordinaten","Rechts- und Hochwert der Bohrung; leer lassen, wenn die Lage im Schritt Lage auf dem Plan gesetzt wird."],entfernen:["Entfernen","Die Bohrung kommt nicht ins Modell (sie bleibt in der Liste unter „Entfernt“ und lässt sich wiederherstellen)."],quelle:["Quelle im PDF","Die Seite des Gutachtens, auf der die Bohrung erkannt wurde; der Rahmen zeigt die gewählte Schicht."],lage_art:["Art der Lage","Koordinaten: Bohrungen mit Rechts-/Hochwert (aus dem PDF, eingetragen oder auf dem Lageplan gesetzt). Reihe: ohne Koordinaten nebeneinander mit Abständen bzw. Stationen aus dem Längsschnitt."],unterlage:["Unterlage","Lageplan (Draufsicht) oder Längsschnitt (Seitenansicht) als PDF. Er liegt im Viewer unter den Bohrungen; nach dem Kalibrieren werden die Bohrungen daraufgezogen."],massstab:["Maßstab","Zwei Punkte auf dem Plan anklicken, deren Abstand Sie kennen (Maßstabsleiste, Bemaßung, zwei Bohrungen), und die wahre Länge in m eintragen. Oder den Maßstab 1:n direkt angeben."],bezug:["Bezugspunkt","Ein Punkt im Plan mit bekannter Koordinate (Koordinatenkreuz, Bohrung mit Koordinaten): anklicken und Rechts-/Hochwert eintragen – im Längsschnitt Station und Höhe NHN."],drehung:["Drehung","Winkel, um den der Plan gegen Norden gedreht ist (gegen den Uhrzeigersinn positiv). Nordpfeil nach oben = 0°; Nordpfeil 10° nach links geneigt = 10°."],hoehe:["Höhenmaßstab","Längsschnitte sind oft überhöht (z. B. Länge 1:500, Höhe 1:100). Ohne Angabe gilt der Längenmaßstab."],epsg:["Koordinatensystem (EPSG)","System der Rechts-/Hochwerte aus der Liste wählen: in Deutschland meist ETRS89 / UTM 32N (25832), im Osten 33N (25833), ältere Pläne Gauß-Krüger (Rechtswert 7-stellig, erste Ziffer = Zone); dazu Schweiz und Österreich. Passen die Werte nicht zum System (Ziffernzahl, Zonenkennung), erscheint ein Hinweis. Steht im IFC (IfcMapConversion)."],sperren:["Sperren","Schloss zu: der Plan liegt fest und ändert sich nicht mehr; jetzt die Bohrungen ziehen. Auf dem Lageplan nur in x/y, im Längsschnitt entlang der Station – in der Höhe nur, wenn das PDF keine GOK hat."],deckkraft:["Deckkraft","Wie stark der Plan die Szene überdeckt."],ohne_lage:["Ohne Lage","Bohrungen ohne Koordinaten: anklicken und dann in den gesperrten Plan klicken (Punkte setzen) – oder mit der Maus aus der Liste auf den Plan ziehen."],punkte:["Punkte setzen","Modus an, dann in den gesperrten Lageplan klicken: die gewählte Bohrung bekommt die Lage, danach ist die nächste ohne Lage dran (oder einen Chip anklicken). Mit „freien Punkt“ entsteht ein Punkt ◆, den Sie in der Liste einer Bohrung zuordnen. ✕ löscht einen Punkt bzw. die gesetzte Lage – im Viewer ebenso: Marke anklicken, Entf. Esc beendet den Modus."],reihe:["Reihe","Bohrungen in einer Linie. Abstand zum Vorgänger je Bohrung eintragen (BK1 → BK2 10 m, BK2 → BK3 15 m) oder eine Station; ohne Eintrag gilt der Standardabstand. Reihenfolge mit den Pfeilen."],standardabstand:["Standardabstand","Abstand zwischen Bohrungen, für die nichts eingetragen ist (nur zur Anschauung, im Modell als schematisch markiert)."],boreholeml:["BoreholeML","Austauschformat der Geologischen Dienste der Länder (Version 3.2). Exportiert werden nur vollständig geprüfte Bohrungen mit Lage in ETRS89/UTM und GOK in m NHN; Petrographie, Genese, Konsistenz, Lagerung, Kalk und Feuchte über die amtlichen Codelisten, die Beschreibung aus dem Gutachten im Klartext. Die Organisation steht als Absender in der Datei. Welche Bohrungen ausgelassen wurden und warum, steht oben in der Datei. Umgekehrt lassen sich BoreholeML-Dateien wie ein Gutachten hochladen (Bohrungen der Länder)."],sgd:["Bohrungen der Länder","Bohrungen aus den Datenbanken der Geologischen Dienste um die Mitte des Projekts: Berlin und Brandenburg mit Kopfdaten und dem Schichtenverzeichnis als Grafik, NRW und Baden-Württemberg in BoreholeML mit den freigegebenen Schichtdaten. Abgefragt wird nur auf Klick – die Anfrage sendet die Lage des Projekts an den Dienst. Bohrungen des Gutachtens, die auch beim Land liegen, zeigen die Abweichung von Lage und GOK (Gegenprobe). Übernommene Bohrungen tragen Quelle, Lizenz und Datum, erscheinen als Raute und gehen nicht in den BoreholeML-Export."],gelaende:["Gelände (DGM)","Digitales Geländemodell der Vermessungsverwaltung (Open Data, meist DGM1 mit 1 m Raster) für das Baufeld herunterladen und hier laden: XYZ, ASCII-Raster oder GeoTIFF, mehrere Kacheln auch als ZIP. Die App vergleicht die GOK aus dem PDF mit dem Gelände: liegen alle Bohrungen gleich viel höher oder tiefer, stimmen Lage, EPSG oder Höhenbezug nicht. Fehlende GOK schlägt sie vor – übernommen wird nur auf Klick, markiert als „DGM“ (auch im IFC)."],dgm_land:["DGM vom Land","Holt das DGM1 (1 m) für den Ausschnitt um die Bohrungen plus Rand direkt beim Dienst des Landes (WCS): bisher Brandenburg mit Berlin und NRW. Nur auf Klick – die Anfrage sendet den Ausschnitt an den Dienst. Quelle, Lizenz und Namensnennung bleiben am DGM und gehen ins IFC. Baden-Württemberg liefert über seinen Dienst nur ganze Meter, Bayern hat keinen freien Dienst: dort die DGM1-Kacheln als Datei laden."],gebaeude:["Gebäude (LoD2)","3D-Gebäudemodelle LoD2 der Länder als Umgebung des Baugrundmodells: Berlin, Brandenburg und NRW geben sie als CityGML-Kacheln von 1 × 1 km heraus, in ETRS89/UTM mit Höhen in m NHN – derselbe Rahmen wie das Modell. Nur auf Klick werden die Kacheln um die Bohrungen (plus Rand) geladen; Gebäude, deren Grundriss den Ausschnitt berührt, kommen ins IFC (IfcBuildingElementProxy mit Wänden und Dach, Quelle und Lizenz je Gebäude) und in den Viewer (Knopf „Gebäude“). Bestand, nicht erkundet."],standort:["Standort ohne Gutachten","Ein Projekt an einem Punkt (ETRS89/UTM): im Schritt Lage fragt es die Bohrungen der Länder um den Punkt ab, holt das DGM und die Gebäude. Übernommene Bohrungen mit Schichtdaten (NRW, Baden-Württemberg) ergeben ein Modell – eine Vorerkundung: Archivdaten unbekannter Güte, ohne Sondierungen, oft alt oder weit weg. Kommt später das Gutachten, entsteht ein neues Projekt, das die Bohrungen der Länder, DGM und Gebäude mitnimmt (gemischt)."],reifegrad:["Reifegrad","Woraus das Modell besteht: Gutachten (nur Bohrungen aus dem PDF), Vorerkundung (nur Bohrungen aus Datenbanken der Länder oder BoreholeML-Dateien) oder gemischt. Er steht in der App, im Viewer, im Prüfbericht und im IFC (CPset_Baugrundmodell.Reifegrad); jede Bohrung trägt ihre Herkunft mit Quelle und Lizenz (CPset_Herkunft)."],gelaende_dgm:["Gelände aus dem DGM","Mit DGM folgt die Oberkante des Modells dem Gelände statt der Interpolation zwischen den GOK. An jeder Bohrung bleibt sie genau auf der GOK; deren Abweichung vom DGM klingt bis zur Reichweite (halber Bohrabstand, höchstens 25 m) ab. Im IFC liegt das Gelände um das Modell als IfcGeographicElement (TERRAIN), im Viewer mit dem Knopf „Gelände“ ein- und ausblendbar. Deckt das DGM das Modellgebiet nicht ganz ab, bleibt die Oberkante aus den GOK (mit Hinweis)."],dgm_epsg:["System der DGM-Datei","XYZ- und ASCII-Dateien enthalten kein Koordinatensystem: das System der Kacheln wählen (meist dasselbe wie das Projekt, z. B. 25832). Ein GeoTIFF bringt es selbst mit."],durchmesser:["Durchmesser","Dicke der Bohrsäulen im Viewer und im IFC (Darstellung, nicht der Bohrdurchmesser im Feld). Automatisch wächst er mit der Modellgröße, damit Säulen auf langen Trassen sichtbar bleiben."],einheiten:["Einheiten","Modelleinheiten verbinden gleiche Bodenarten zwischen den Bohrungen (Sand 1, Kies, Sand 2). Umbenennen oder Bodenarten zusammenlegen (z. B. „Sand, Kies“ als eine Einheit); Reihenfolge von oben nach unten."],methode:["Interpolation","IDW: gewichtetes Mittel der Nachbarbohrungen, ruhig und sicher. Dünnplatten-Spline: glatte Flächen mit Trend, gut bei geneigten Schichten."],puffer:["Puffer","Wie weit das Modell über die Bohrungen hinausreicht. Automatisch: halber Bohrabstand (5–100 m)."],raster:["Raster","Maschenweite der Schichtflächen. Automatisch: Gebietsgröße/40, bei großen Modellen gröber (höchstens 30 000 Knoten)."],basis:["Modellbasis","Unterkante des Modells in m NHN. Automatisch: tiefste Endteufe."],gok_relativ:["Fehlende GOK","Hat keine Bohrung eine GOK, rechnet das Modell relativ (Gelände = 0 m) – markiert im IFC."],auto:["Automatisch nachführen","Jede Änderung (Tabelle, Lage, Einheiten) rechnet das Modell sofort neu."],einchecken:["Einchecken","Hält den Prüfstand fest (Zeit, Zähler, Fingerabdruck des Modells, Kommentar). Das exportierte IFC trägt ihn (CPset_Baugrundmodell.Pruefstand)."],export:["Export","IFC 4.3 mit Prüfstand, Bodenansprache je Schicht und Beschreibungen je Einheit; dazu Prüfbericht und die Daten als JSON."],ueberhoehung:["Überhöhung","Höhen im Viewer mal Faktor, damit dünne Schichten sichtbar werden. Die Koordinaten bleiben echt."]};let G=null,be=null;function ne(){G?.remove(),G=null,be=null}function sn(e,t){e.preventDefault(),e.stopPropagation();const n=e.currentTarget;if(be===n){ne();return}ne();const[i,l]=me[t];G=document.createElement("div"),G.className="hilfe-blase",G.setAttribute("role","tooltip"),G.innerHTML="<strong></strong><p></p>",G.querySelector("strong").textContent=i,G.querySelector("p").textContent=l,document.body.append(G);const r=n.getBoundingClientRect(),o=G.getBoundingClientRect(),h=Math.min(Math.max(8,r.left+r.width/2-o.width/2),window.innerWidth-o.width-8),p=r.bottom+8+o.height>window.innerHeight?r.top-o.height-8:r.bottom+8;Object.assign(G.style,{left:`${h}px`,top:`${p}px`}),be=n}document.addEventListener("click",e=>{G&&!G.contains(e.target)&&ne()});document.addEventListener("keydown",e=>{e.key==="Escape"&&ne()});const d=e=>a`<button type="button" class="hilfe" title=${me[e][0]} aria-label=${`Hilfe: ${me[e][0]}`}
    @click=${t=>sn(t,e)}>?</button>`;let L=[],fe=!0,Q=!1;const _={x:"",y:"",epsg:25832,name:""},ln=[[25832,"ETRS89 / UTM 32N"],[25833,"ETRS89 / UTM 33N"],[4647,"ETRS89 / UTM 32N (zE-N)"],[5650,"ETRS89 / UTM 33N (zE-N)"]];async function He(e){for(;;){const t=await v(()=>k.auftrag(e));if(!t)return;if(s.auftrag=t,g(),t.fertig){s.auftrag=null;for(const n of t.fehler)x(n,"fehler",1e4);t.projekt?(L=[],await j(t.projekt,"bohrungen")):g();return}await new Promise(n=>setTimeout(n,600))}}const Ue=()=>s.z?.standort?s.sig:"";async function rn(){if(!L.length)return;const e=await v(()=>k.gutachten(L,fe&&!!s.info?.ocr,Ue()));e&&await He(e.id)}async function on(){const e=Number(_.x.replace(",",".")),t=Number(_.y.replace(",","."));if(!Number.isFinite(e)||!Number.isFinite(t)||!_.x||!_.y){x("Rechtswert und Hochwert als Zahlen eingeben.","warn");return}const n=await v(()=>k.standort(e,t,_.epsg,_.name),"Standort wird angelegt …");n&&await j(n.projekt,"lage")}function cn(){const e=(t,n,i)=>a`
    <label class="feld"><span>${n}</span><input type="text" inputmode=${t==="name"?"text":"decimal"}
      aria-label=${n} placeholder=${i} .value=${_[t]} @input=${l=>{_[t]=l.target.value}}></label>`;return a`
    <section class="karte">
      <h3>Standort ohne Gutachten ${d("standort")}</h3>
      <p class="leise klein">Ein Punkt statt eines PDFs: Bohrungen der Länder, DGM und Gebäude um den Standort. Das Modell
        ist eine <b>Vorerkundung</b> – kein Ersatz für das Gutachten.</p>
      <div class="raster-2">
        ${e("x","Rechtswert","z. B. 368130")}
        ${e("y","Hochwert","z. B. 5724400")}
        <label class="feld"><span>System</span>
          <select aria-label="System des Standorts" @change=${t=>{_.epsg=Number(t.target.value)}}>
            ${ln.map(([t,n])=>a`<option value=${t} ?selected=${_.epsg===t}>${t} · ${n}</option>`)}
          </select></label>
        ${e("name","Name (frei)","z. B. Marl Nord")}
      </div>
      <button class="primaer" @click=${on}>Projekt am Standort anlegen →</button>
    </section>`}async function un(e){const t=await v(()=>k.beispiel(e),"Beispiel wird geöffnet …");t?.projekt?await j(t.projekt,"bohrungen"):t?.auftrag&&await He(t.auftrag)}function xe(e){L=[...e??[]].filter(t=>/\.(pdf|json|xml)$/i.test(t.name)),e?.length&&!L.length&&x("Bitte PDF-Dateien wählen (oder eine Extraktion als JSON, Bohrungen als BoreholeML).","warn"),g()}async function hn(e,t){confirm(`Projekt „${t}“ mit allen Korrekturen löschen? Das Gutachten selbst bleibt unberührt.`)&&(await v(()=>k.loeschen(e)),await je())}function dn(){const e=s.auftrag,t=!!s.info?.ocr;return a`
    <div class="seite-mitte">
      <section class="karte gross">
        <h2>Bodengutachten auswerten</h2>
        <p class="leise">Bohrprofile, Schichtenverzeichnisse oder ganze Gutachten als PDF – Vektor oder Scan. Die Bohrungen
          werden erkannt; im nächsten Schritt prüfen und korrigieren Sie sie.</p>
        ${Ue()?a`<p class="hinweis-standort">Zum Standort <b>${s.z.name}</b>: Bohrungen der Länder (mit Prüfstand),
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
          <label class=${`ablage ${Q?"ueber":""}`}
            @dragover=${n=>{n.preventDefault(),Q=!0,g()}}
            @dragleave=${()=>{Q=!1,g()}}
            @drop=${n=>{n.preventDefault(),Q=!1,xe(n.dataTransfer?.files)}}>
            <input type="file" accept=".pdf,application/pdf,.json,application/json,.xml,application/xml,text/xml" multiple @change=${n=>xe(n.target.files)}>
            <span class="ablage-icon">⇪</span>
            <strong>${L.length?L.map(n=>n.name).join(", "):"PDF hierher ziehen oder klicken"}</strong>
            <span class="leise">${L.length?`${L.length} Datei(en) bereit`:"mehrere Dateien möglich (z. B. Anlagen 2–4) · auch eine Extraktion als JSON oder Bohrungen als BoreholeML (XML)"}</span>
          </label>
          <div class="zeile">
            <label class="schalter" title=${t?"":"nicht installiert: pip install -r requirements-ocr.txt"}>
              <input type="checkbox" .checked=${fe&&t} ?disabled=${!t} @change=${n=>{fe=n.target.checked}}>
              OCR für Scans ${t?"":"(nicht installiert)"}
            </label>${d("ocr")}
            <span class="fueller"></span>
            <button class="primaer" ?disabled=${!L.length} @click=${rn}>Auswerten →</button>
          </div>`}
      </section>

      ${cn()}

      <div class="zwei-spalten">
        <section class="karte">
          <h3>Beispiele ${d("beispiele")}</h3>
          <ul class="auswahl-liste">
            ${(s.info?.beispiele??[]).map(n=>a`
              <li><button class="link" ?disabled=${!!e} @click=${()=>un(n.name)}>${n.titel}</button></li>`)}
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
                    <td><button class="link" @click=${()=>j(n.signatur)}>${n.name}</button>${n.standort?a` <span class="abzeichen vorerkundung" title="Standort ohne Gutachten">Standort</span>`:u}
                      <div class="leise klein">${n.dokumente.join(", ")}</div></td>
                    <td class="zahl" title=${n.fremd?`davon ${n.fremd} aus den Datenbanken der Länder`:""}>${n.bohrungen}</td>
                    <td class="zahl">${n.geprueft}${n.eincheckungen?a` · <span title="eingecheckt">✓${n.eincheckungen}</span>`:u}</td>
                    <td class="leise klein">${n.geaendert}</td>
                    <td><button class="symbol" title="Projekt löschen" aria-label="Projekt löschen" @click=${()=>hn(n.signatur,n.name)}>🗑</button></td>
                  </tr>`)}
              </tbody>
            </table>`:a`<p class="leise">Noch keine Projekte. Ein Projekt entsteht beim ersten Auswerten und wird automatisch gesichert.</p>`}
        </section>
      </div>
      ${s.info?a`<p class="leise klein impressum">GroundTwin ${s.info.version} · freie Software unter
        <a href=${`${s.info.quellcode}/blob/main/LICENSE`} target="_blank" rel="noopener">${s.info.lizenz}</a> ·
        <a href=${s.info.quellcode} target="_blank" rel="noopener">Quellcode</a> · die App extrahiert und schlägt vor;
        die Interpretation und Freigabe bleibt beim Geotechniker.</p>`:u}
    </div>`}const X="Deutschland · ETRS89 / UTM (amtlich)",F="Deutschland · Gauß-Krüger (alt)",te=[{code:25832,name:"ETRS89 / UTM Zone 32N",gruppe:X,e:[22e4,101e4],n:[503e4,614e4],hinweis:"Rechtswert 6-stellig, die meisten Länder"},{code:25833,name:"ETRS89 / UTM Zone 33N",gruppe:X,e:[15e4,7e5],n:[509e4,613e4],hinweis:"Rechtswert 6-stellig, Osten (Berlin, Brandenburg, Sachsen, MV)"},{code:4647,name:"ETRS89 / UTM 32N mit Zone (32…)",gruppe:X,e:[3223e4,33e6],n:[52e5,614e4],hinweis:"Rechtswert 8-stellig, beginnt mit 32"},{code:5650,name:"ETRS89 / UTM 33N mit Zone (33…)",gruppe:X,e:[3315e4,3354e4],n:[52e5,613e4],hinweis:"Rechtswert 8-stellig, beginnt mit 33"},{code:31466,name:"DHDN / Gauß-Krüger Zone 2",gruppe:F,e:[23e5,27e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 2"},{code:31467,name:"DHDN / Gauß-Krüger Zone 3",gruppe:F,e:[33e5,37e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 3"},{code:31468,name:"DHDN / Gauß-Krüger Zone 4",gruppe:F,e:[43e5,47e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 4"},{code:31469,name:"DHDN / Gauß-Krüger Zone 5",gruppe:F,e:[531e4,57e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 5"},{code:2398,name:"Krassowski (42/83) / Gauß-Krüger Zone 4",gruppe:F,e:[43e5,47e5],n:[52e5,613e4],hinweis:"neue Länder vor ETRS89, Rechtswert beginnt mit 4"},{code:2399,name:"Krassowski (42/83) / Gauß-Krüger Zone 5",gruppe:F,e:[53e5,57e5],n:[52e5,613e4],hinweis:"neue Länder vor ETRS89, Rechtswert beginnt mit 5"},{code:3068,name:"DHDN / Soldner Berlin",gruppe:"Deutschland · andere",e:[-4e4,9e4],n:[-4e4,8e4],hinweis:"Berlin, alte Katasterkoordinaten (5-stellig)"},{code:2056,name:"CH1903+ / LV95",gruppe:"Schweiz",e:[245e4,287e4],n:[103e4,134e4],hinweis:"E 2 xxx xxx, N 1 xxx xxx"},{code:21781,name:"CH1903 / LV03",gruppe:"Schweiz",e:[45e4,87e4],n:[3e4,34e4],hinweis:"Y 6-stellig, X 5–6-stellig (alt)"},{code:31254,name:"MGI / Austria GK West",gruppe:"Österreich",e:[-11e4,17e4],n:[11e4,34e4],hinweis:"Rechtswert um 0 (±), Hochwert ohne 5 000 000"},{code:31255,name:"MGI / Austria GK Central",gruppe:"Österreich",e:[-16e4,17e4],n:[9e4,46e4],hinweis:"Rechtswert um 0 (±), Hochwert ohne 5 000 000"},{code:31256,name:"MGI / Austria GK East",gruppe:"Österreich",e:[-16e4,1e5],n:[1e5,48e4],hinweis:"Rechtswert um 0 (±), Hochwert ohne 5 000 000"},{code:31257,name:"MGI / Austria GK M28 (BMN)",gruppe:"Österreich",e:[4e4,32e4],n:[11e4,34e4],hinweis:"Bundesmeldenetz West"},{code:31258,name:"MGI / Austria GK M31 (BMN)",gruppe:"Österreich",e:[29e4,62e4],n:[9e4,46e4],hinweis:"Bundesmeldenetz Mitte"},{code:31259,name:"MGI / Austria GK M34 (BMN)",gruppe:"Österreich",e:[59e4,85e4],n:[1e5,48e4],hinweis:"Bundesmeldenetz Ost"},{code:32632,name:"WGS 84 / UTM Zone 32N",gruppe:"GPS (WGS 84)",e:[22e4,101e4],n:[503e4,614e4],hinweis:"wie ETRS89 / UTM 32N (Abweichung < 1 m)"},{code:32633,name:"WGS 84 / UTM Zone 33N",gruppe:"GPS (WGS 84)",e:[15e4,7e5],n:[509e4,613e4],hinweis:"wie ETRS89 / UTM 33N (Abweichung < 1 m)"}],gn=new Map(te.map(e=>[e.code,e]));function Se(e){return e?gn.get(e)??null:null}function Be(e){if(!e)return"ohne System (lokal)";const t=Se(e);return t?`EPSG ${e} · ${t.name}`:`EPSG ${e} (nicht in der Liste)`}const Ve=(e,t,n)=>t>=e.e[0]&&t<=e.e[1]&&n>=e.n[0]&&n<=e.n[1];function pn(e,t){return e===null||t===null||!Number.isFinite(e)||!Number.isFinite(t)?[]:te.filter(n=>n.gruppe!=="GPS (WGS 84)"&&Ve(n,e,t))}function We(e,t,n){if(t===null||n===null||!Number.isFinite(t)||!Number.isFinite(n))return null;const i=pn(t,n),l=i.slice(0,3).map(o=>`${o.code} (${o.name})`).join(", ");if(!e)return i.length?{ok:!1,text:`Kein System gewählt – die Werte passen zu ${l}.`}:null;const r=Se(e);return r?Ve(r,t,n)?{ok:!0,text:`passt zu EPSG ${e} (${r.hinweis})`}:{ok:!1,text:i.length?`Rechts-/Hochwert passen nicht zu EPSG ${e} (${r.hinweis}), aber zu ${l}.`:"Rechts-/Hochwert passen zu keinem System der Liste – Ziffern prüfen (z. B. fehlende Zonenkennung)."}:{ok:!1,text:`EPSG ${e} ist nicht in der Liste – bitte prüfen.`}}function Me(e,t,n="Koordinatensystem"){const i=[...new Set(te.map(r=>r.gruppe))],l=e!==null&&!Se(e);return a`
    <select class="epsg" aria-label=${n} title=${Be(e)}
      @change=${r=>{const o=r.target.value;t(o===""?null:Number(o))}}>
      <option value="" .selected=${e===null}>– ohne (lokal) –</option>
      ${l?a`<option value=${String(e)} .selected=${!0}>EPSG ${e} – nicht in der Liste ⚠</option>`:u}
      ${i.map(r=>a`
        <optgroup label=${r}>
          ${te.filter(o=>o.gruppe===r).map(o=>a`
            <option value=${String(o.code)} .selected=${o.code===e}>${o.code} · ${o.name}</option>`)}
        </optgroup>`)}
    </select>`}const V=(e,t=2)=>e.toLocaleString("de-DE",{minimumFractionDigits:t,maximumFractionDigits:t});function Ce(e){for(const t of[.5,1,2,5,10,20,50,100])if(e/t<=12)return t;return 200}function mn(e,t){const n=Math.max(1,...e.map(c=>c.bis)),i=12,l=(t.hoehe-i-14)/n,r=34,o=46,h=Ce(n),p=[];for(let c=0;c<=n+1e-9;c+=h)p.push(c);return a`<svg class="saeule" viewBox="0 0 150 ${t.hoehe}" width="150" height=${t.hoehe} role="img" aria-label="Bohrsäule">
    <defs>
      <pattern id="schraffur-warn" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
        <rect width="6" height="6" fill="#e6e6e6"></rect><line x1="0" y1="0" x2="0" y2="6" stroke="#f0a33a" stroke-width="3"></line>
      </pattern>
    </defs>
    ${p.map(c=>T`
      <line x1=${r-5} x2=${r} y1=${i+c*l} y2=${i+c*l} class="achse"></line>
      <text x=${r-7} y=${i+c*l+3} class="achse-text" text-anchor="end">${V(c,h<1?1:0)}</text>`)}
    <line x1=${r} x2=${r} y1=${i} y2=${i+n*l} class="achse"></line>
    ${e.map(c=>T`
      <g class=${`schicht ${c.k===t.gewaehlt?"gewaehlt":""} ${c.warn?"warn":""}`} @click=${()=>t.waehlen?.(c.k)}>
        <title>${c.titel}</title>
        <rect x=${r+4} y=${i+c.von*l} width=${o} height=${Math.max(1,(c.bis-c.von)*l)}
          fill=${c.warn?"url(#schraffur-warn)":c.farbe}></rect>
        ${c.geprueft?T`<text x=${r+o+9} y=${i+(c.von+c.bis)/2*l+4} class="haken">✓</text>`:u}
        ${(c.bis-c.von)*l>11?T`<text x=${r+o+22} y=${i+c.bis*l-2} class="tiefe">${V(c.bis)}</text>`:u}
      </g>`)}
  </svg>`}function bn(e,t){const n=[...e.bohrungen].sort((b,q)=>b.x-q.x||b.y-q.y);if(!n.length)return u;const i=new Map(e.einheiten.map(b=>[b.name,b.farbe])),l=Math.max(...n.map(b=>b.gok)),r=Math.min(...n.map(b=>b.endteufe_nhn)),o=22,h=44,p=Math.max(38,Math.min(70,900/n.length)),c=h+n.length*p+10,B=(t.hoehe-o-10)/Math.max(1,l-r),M=b=>o+(l-b)*B,Z=Ce(l-r),Ge=[];for(let b=Math.ceil(r/Z)*Z;b<=l+1e-9;b+=Z)Ge.push(b);return a`<svg class="einheitenprofil" viewBox="0 0 ${c} ${t.hoehe}" width=${c} height=${t.hoehe} role="img"
      aria-label="Einheiten je Bohrung">
    ${Ge.map(b=>T`
      <line x1=${h-4} x2=${c} y1=${M(b)} y2=${M(b)} class="raster"></line>
      <text x=${h-6} y=${M(b)+3} class="achse-text" text-anchor="end">${V(b,Z<1?1:0)}</text>`)}
    ${n.map((b,q)=>{const J=h+q*p+p*.2,he=p*.6;return T`
        <text x=${J+he/2} y=${o-8} class="code" text-anchor="middle">${b.code}</text>
        ${b.einheiten.filter(y=>y.status==="vorhanden"&&y.ok_modell-y.uk_modell>.001).map(y=>T`
          <rect x=${J} y=${M(y.ok_modell)} width=${he} height=${Math.max(.8,(y.ok_modell-y.uk_modell)*B)}
            fill=${i.get(y.einheit)??"#ccc"} class=${`einheit ${t.gewaehlt===y.einheit?"gewaehlt":""}`}
            @click=${()=>t.waehlen?.(y.einheit)}>
            <title>${b.code}: ${y.einheit} ${V(y.ok_modell)} bis ${V(y.uk_modell)} m NHN</title>
          </rect>`)}
        <line x1=${J-3} x2=${J+he+3} y1=${M(b.endteufe_nhn)} y2=${M(b.endteufe_nhn)} class="endteufe"></line>`})}
  </svg>`}const ie=(e,t=2)=>e==null?"":e.toLocaleString("de-DE",{minimumFractionDigits:t,maximumFractionDigits:t}),$e=e=>{const t=e.target.value.trim().replace(",",".");return t===""?null:Number(t)},fn=[["boden","Böden"],["organisch","Organisch"],["geologisch","Geologische Benennung"],["fels","Fels"],["anthropogen","Anthropogen"],["unbekannt","Nicht klassifiziert"]];let ae=null,de="",N=.5,_e=!1;function se(e){const t=C(),n=t.findIndex(l=>l.id===s.bid),i=t[Math.min(t.length-1,Math.max(0,n+e))];i&&ce(i.id)}function Ze(){const e=C(),t=ze(e.findIndex(n=>n.id===s.bid));t&&ce(t)}async function qe(){const e=s.bid;if(!await m([{op:"bohrung_pruefen",id:e,wert:!0}],{leise:!0}))return;const t=ze(C().findIndex(n=>n.id===e));t&&t!==e&&await ce(t)}async function Le(e){const t=s.z.pruefstand,n=e?`Alle Schichten aller ${t.bohrungen[1]} Bohrungen als geprüft markieren?`:"Die Prüfung aller Bohrungen zurücknehmen?";confirm(n)&&await m([{op:"alle_pruefen",wert:e}])}window.addEventListener("keydown",e=>{if(s.schritt!=="bohrungen"||e.ctrlKey||e.metaKey||e.altKey||e.target?.closest?.("input, select, textarea, [contenteditable]"))return;const n=e.key.toLowerCase();if(e.key==="ArrowDown"||n==="j")se(1);else if(e.key==="ArrowUp"||n==="k")se(-1);else if(n==="n")Ze();else if(n==="g")qe();else return;e.preventDefault()});async function $n(e,t){const n=Number(e.id.split(":")[0]),i=(t[0]?.quelle.seite??e.seite)-1,l=`${s.sig}/${n}/${i}`;if(ae?.schluessel===l||de===l||!s.z?.dokumente[n]?.pdf)return;de=l;const r=await v(()=>k.seite(s.sig,n,i));de="",r&&(ae={schluessel:l,daten:r},g())}function kn(e){return e.entfernt?a`<span class="zeichen raus" title="nicht im Modell">–</span>`:e.offen>0?a`<span class="zeichen warn" title=${`${e.offen} Schicht(en) nicht klassifiziert`}>⚠</span>`:e.schichten_n&&e.schichten_geprueft===e.schichten_n?a`<span class="zeichen ok" title="alle Schichten geprüft">✓</span>`:a`<span class="zeichen" title="noch zu prüfen">○</span>`}function wn(){const e=s.z.bohrungen,t=C(),n=e.filter(i=>i.entfernt);return a`
    <aside class="bohrliste-app">
      <input class="suche" type="search" placeholder="Bohrung suchen …" .value=${s.filter}
        @input=${i=>{s.filter=i.target.value,g()}}>
      <ul class="bliste" role="listbox" aria-label="Bohrungen">
        ${t.map(i=>a`
          <li role="option" aria-selected=${String(i.id===s.bid)} class=${i.id===s.bid?"aktiv":""}
            @click=${()=>ce(i.id)}>
            ${kn(i)}
            <span class="name">${i.code}</span>
            <span class="wert">${i.schichten_geprueft}/${i.schichten_n}</span>
            <button class="symbol leise-knopf" title="Aus dem Modell entfernen" aria-label=${`${i.code} entfernen`}
              @click=${l=>{l.stopPropagation(),m([{op:"entfernen",id:i.id}])}}>🗑</button>
          </li>`)}
      </ul>
      ${n.length?a`
        <details class="entfernt" ?open=${_e} @toggle=${i=>{_e=i.target.open}}>
          <summary>Entfernt / nicht im Modell (${n.length}) ${d("entfernen")}</summary>
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
    </aside>`}function vn(){const e=s.z.pruefstand,[t,n]=e.bohrungen,[i,l]=e.schichten;return a`
    <div class="pruefleiste">
      <div class="balken"><span>Bohrungen geprüft <b>${t}/${n}</b></span><progress max=${n||1} value=${t}></progress></div>
      <div class="balken"><span>Schichten geprüft <b>${i}/${l}</b></span><progress max=${l||1} value=${i}></progress></div>
      <span class=${`plakette ${e.unklassifiziert_offen?"warn":"ok"}`}>
        ${e.unklassifiziert_offen?`⚠ ${e.unklassifiziert_offen} Schicht(en) nicht klassifiziert`:"✓ keine offenen Warnungen"}</span>
      ${d("warnung")}
      <span class="fueller"></span>
      ${d("pruefstand")}
      <button @click=${()=>Le(!0)} ?disabled=${t===n&&i===l}>✓ Alle Bohrungen geprüft</button>
      <button class="leise-knopf" @click=${()=>Le(!1)} ?disabled=${!i}>Zurücknehmen</button>
      ${d("alle_pruefen")}
    </div>`}function R(e,t,n){return a`<label class="feld"><span>${e}${n?d(n):u}</span>${t}</label>`}function zn(e){const t=We(e.epsg,e.x,e.y);return t&&!t.ok?a`<p class="hinweise warn">⚠ ${t.text}</p>`:u}function Sn(e){const t=C(),n=t.findIndex(l=>l.id===e.id),i=l=>r=>m([{op:"bohrung",id:e.id,feld:l,wert:$e(r)}]);return a`
    <div class="detail-kopf">
      <div class="titelzeile">
        <h2>${e.code}</h2>
        <span class="leise">${e.dokument} · Seite ${e.seite}${e.doppelt_in?` · doppelt (auch in ${e.doppelt_in})`:""}</span>
        <span class="fueller"></span>
        <button title="Vorherige Bohrung (↑)" ?disabled=${n<=0} @click=${()=>se(-1)}>↑ Vorherige</button>
        <button title="Nächste Bohrung (↓)" ?disabled=${n>=t.length-1} @click=${()=>se(1)}>↓ Nächste</button>
        <button title="Nächste Bohrung mit offenen Schichten (N)" ?disabled=${!ze(n)} @click=${Ze}>⚠ Nächste offene</button>
      </div>
      <div class="felder">
        ${R("GOK [m NHN]",a`<input type="number" step="0.01" .value=${$(e.gok===null?"":String(e.gok))}
            placeholder="unbekannt" @change=${i("gok")}>
            <small class=${e.gok_quelle==="manuell"||e.gok_quelle==="DGM"?"manuell":"leise"}>${e.gok_quelle||"fehlt"}</small>`,"gok")}
        ${R("Endteufe [m]",a`<output>${ie(e.endteufe)}</output>`)}
        ${R("Rechtswert",a`<input type="number" step="0.01" .value=${$(e.x===null?"":String(e.x))} @change=${i("x")}>`,"koordinaten")}
        ${R("Hochwert",a`<input type="number" step="0.01" .value=${$(e.y===null?"":String(e.y))} @change=${i("y")}>`)}
        ${R("Koordinatensystem (EPSG)",Me(e.epsg,l=>m([{op:"bohrung",id:e.id,feld:"epsg",wert:l}])),"epsg")}
        ${R("Ø Säule [m]",a`<input type="number" step="0.1" min="0" class="kurz" placeholder=${`auto ${ie(s.z.durchmesser??s.z.durchmesser_auto,1)}`}
            .value=${$(e.durchmesser===null?"":String(e.durchmesser))} @change=${i("durchmesser")}>`,"durchmesser")}
        ${R("Grundwasser",a`<output>${e.grundwasser||"–"}</output>`)}
      </div>
      ${zn(e)}
      ${e.hinweise.length?a`<p class="hinweise">ℹ ${e.hinweise.join(" · ")}</p>`:u}
    </div>`}function Bn(e,t){const n=s.z.klassen,i=n.some(l=>l.klasse===t.bodenart);return a`
    <span class="farbfeld" style=${`background:${t.farbe}`}></span>
    <select aria-label="Bodenart" @change=${l=>m([{op:"schicht",id:e.id,k:t.k,feld:"bodenart",wert:l.target.value}])}>
      ${i?u:a`<option .selected=${!0} value=${t.bodenart}>${t.bodenart}</option>`}
      ${fn.map(([l,r])=>a`
        <optgroup label=${r}>
          ${n.filter(o=>o.art===l).map(o=>a`
            <option value=${o.klasse} .selected=${o.klasse===t.bodenart}>${o.name}${o.din4023?` (${o.din4023})`:""}</option>`)}
        </optgroup>`)}
    </select>`}function Mn(e,t){return a`
    <table class="tabelle schichten">
      <thead><tr>
        <th title="geprüft">✓ ${d("geprueft")}</th><th>von [m] ${d("tiefe")}</th><th>bis [m]</th>
        <th>Bodenart ${d("bodenart")}</th><th>Beschreibung (PDF)</th><th>nach Norm ${d("norm")}</th>
      </tr></thead>
      <tbody>
        ${t.map(n=>a`
          <tr class=${[n.offen?"warn":"",n.korrigiert?"korrigiert":"",n.k===s.k?"gewaehlt":""].join(" ")}
            @click=${()=>{s.k=n.k,g()}}>
            <td><input type="checkbox" .checked=${$(n.geprueft)} aria-label="geprüft"
              @change=${i=>m([{op:"schicht",id:e.id,k:n.k,feld:"geprueft",wert:i.target.checked}],{leise:!0})}></td>
            <td><input type="number" step="0.01" min="0" class="tief" .value=${$(String(n.von))}
              @change=${i=>m([{op:"schicht",id:e.id,k:n.k,feld:"oben",wert:$e(i)}])}></td>
            <td><input type="number" step="0.01" min="0" class="tief" .value=${$(String(n.bis))}
              @change=${i=>m([{op:"schicht",id:e.id,k:n.k,feld:"unten",wert:$e(i)}])}></td>
            <td class="bodenart">${Bn(e,n)}
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
                  → ${n.vorschlag.klasse} übernehmen</button>${d("vorschlag")}`:u}
            </td>
          </tr>`)}
      </tbody>
    </table>`}function yn(e,t){$n(e,t);const n=Number(e.id.split(":")[0]),i=!!s.z.dokumente[n]?.pdf,l=ae?.schluessel===`${s.sig}/${n}/${(t[0]?.quelle.seite??e.seite)-1}`?ae.daten:null,r=t.find(c=>c.k===s.k)??null,o=(c,B)=>{if(!c||!l)return u;const M=l.px_je_pt*N;return a`<div class=${`bbox ${B}`} style=${`left:${c[0]*M}px;top:${c[1]*M}px;width:${(c[2]-c[0])*M}px;height:${(c[3]-c[1])*M}px`}></div>`},h=t.map(c=>c.quelle.bbox).filter(c=>!!c&&c.length===4),p=h.length?[Math.min(...h.map(c=>c[0])),Math.min(...h.map(c=>c[1])),Math.max(...h.map(c=>c[2])),Math.max(...h.map(c=>c[3]))]:null;return a`
    <aside class="quelle-spalte">
      <div class="saeule-rahmen">
        ${mn(t.map(c=>({k:c.k,von:c.von,bis:c.bis,farbe:c.farbe,warn:c.offen,geprueft:c.geprueft,titel:`${ie(c.von)}–${ie(c.bis)} m: ${c.bodenart}${c.beschreibung?` – ${c.beschreibung}`:""}`})),{hoehe:420,gewaehlt:s.k,waehlen:c=>{s.k=c,g()}})}
      </div>
      ${i?a`<div class="pdf-rahmen">
        <div class="pdf-kopf"><b>Quelle im PDF</b> ${d("quelle")}
          <span class="fueller"></span>
          ${i?a`<button class="symbol" title="kleiner" @click=${()=>{N=Math.max(.25,N/1.4),g()}}>−</button>
            <button class="symbol" title="größer" @click=${()=>{N=Math.min(1.5,N*1.4),g()}}>+</button>`:u}
        </div>
        ${l?a`
          ${Gn(p,l.px_je_pt*N)}
          <div class="pdf-seite">
            <div class="pdf-flaeche" style=${`width:${l.breite_pt*l.px_je_pt*N}px;height:${l.hoehe_pt*l.px_je_pt*N}px`}>
              <img src=${l.url} alt=${`Seite ${l.seite+1}`} draggable="false">
              ${o(p,"saeule-bbox")}
              ${o(r?.quelle.bbox,"schicht-bbox")}
            </div>
          </div>`:a`<p class="leise klein">Seite wird geladen …</p>`}
      </div>`:u}
    </aside>`}let Ne="";function Gn(e,t){const n=`${s.bid}/${N}`;return!e||Ne===n?u:(requestAnimationFrame(()=>{const i=document.querySelector(".pdf-seite");i&&(i.scrollLeft=Math.max(0,e[0]*t-i.clientWidth/3),i.scrollTop=Math.max(0,e[1]*t-40),Ne=n)}),u)}function Dn(){const e=s.z,t=s.details.get(s.bid),n=e.bohrungen.find(r=>r.id===s.bid),i=n?Number(n.id.split(":")[0]):0,l=!e.dokumente[i]?.pdf;return a`
    <div class=${`schritt-bohrungen ${l?"ohne-pdf":""}`}>
      ${vn()}
      ${wn()}
      <section class="bohrung-detail">
        ${n?a`
          ${Sn(n)}
          ${t?a`
            ${Mn(n,t.schichten)}
            <div class="detail-fuss">
              <button class="primaer" title="Alle Schichten dieser Bohrung als geprüft markieren und zur nächsten offenen (G)"
                @click=${qe}>✓ Alle Schichten geprüft – weiter</button>
              <button class="leise-knopf" ?disabled=${!n.schichten_geprueft}
                @click=${()=>m([{op:"bohrung_pruefen",id:n.id,wert:!1}])}>Prüfung zurücknehmen</button>
              <span class="fueller"></span>
              <button class="gefahr" @click=${()=>m([{op:"entfernen",id:n.id}])}>🗑 Aus dem Modell entfernen</button>
            </div>`:a`<p class="leise">Schichten werden geladen …</p>`}`:a`<p class="leise">Links eine Bohrung wählen.</p>`}
      </section>
      ${n&&t?yn(n,t.schichten):a`<aside class="quelle-spalte"></aside>`}
    </div>`}const w=(e,t=2)=>e==null||!Number.isFinite(e)?"":e.toLocaleString("de-DE",{minimumFractionDigits:t,maximumFractionDigits:t}),S=e=>{const t=e.target.value.trim().replace(",",".");return t===""?null:Number(t)};let f=null,le="",U="plan",W,ke=250,we=100,ve=100;const A=new Set;function Pe(e){const t=e.unterlage;return t?`${t.sha}/${t.seite}/${t.art}/${JSON.stringify(t.kalibrierung)}`:""}function Je(e){const t=e.unterlage;if(!t)return f=null;if(f&&f.schluessel===Pe(e))return f;const n=t.kalibrierung,i=o=>o&&!("n"in o)?o:null,l=i(n?.massstab),r=i(n?.hoehe);return f={schluessel:Pe(e),massArt:n?.massstab&&"n"in n.massstab?"n":"strecke",p1:l?{u:l.u1,v:l.v1}:null,p2:l?{u:l.u2,v:l.v2}:null,meter:l?.meter??null,n:n?.massstab&&"n"in n.massstab?n.massstab.n:null,hoeheArt:n?.hoehe?"n"in n.hoehe?"n":"strecke":"gleich",h1:r?{u:r.u1,v:r.v1}:null,h2:r?{u:r.u2,v:r.v2}:null,hoeheMeter:r?.meter??null,hoeheN:n?.hoehe&&"n"in n.hoehe?n.hoehe.n:null,bezug:n?.bezug?{u:n.bezug.u,v:n.bezug.v}:null,x:n?.bezug?.x??null,y:n?.bezug?.y??null,drehung:n?.drehung??0,epsg:n?.epsg??e.viewer.epsg??null},f}function ye(e,t=!1){const n=f,i=e.unterlage;if(!n||!i)return null;let l=null;if(n.massArt==="n"&&n.n&&n.n>0&&(l={n:n.n}),n.massArt==="strecke"&&n.p1&&n.p2&&n.meter&&n.meter>0&&(l={u1:n.p1.u,v1:n.p1.v,u2:n.p2.u,v2:n.p2.v,meter:n.meter}),!l||!n.bezug||n.x===null||n.y===null)return null;let r=null;return i.art==="schnitt"&&n.hoeheArt==="n"&&n.hoeheN&&n.hoeheN>0&&(r={n:n.hoeheN}),i.art==="schnitt"&&n.hoeheArt==="strecke"&&n.h1&&n.h2&&n.hoeheMeter&&n.hoeheMeter>0&&(r={u1:n.h1.u,v1:n.h1.v,u2:n.h2.u,v2:n.h2.v,meter:n.hoeheMeter}),{massstab:l,hoehe:r,bezug:{...n.bezug,x:n.x,y:n.y},drehung:i.art==="plan"?n.drehung:0,epsg:i.art==="plan"?n.epsg:null,gesperrt:t}}function z(){const e=s.z;s.entwurf=ye(e);const t=s.viewer;t&&f&&(t.editor.hilfsmarken({strecke:f.massArt==="strecke"?[f.p1,f.p2]:[],hoehe:f.hoeheArt==="strecke"?[f.h1,f.h2]:[],bezug:f.bezug}),s.entwurf&&t.editor.vorschau(s.entwurf)),g()}async function xn(e){const t=s.viewer;if(!t||!f)return;le=e,g();const n=await t.editor.bildpunktWaehlen();if(le="",!n||!f||s.z?.unterlage?.kalibrierung?.gesperrt){g();return}f[e]=n,z()}async function Ee(e){s.viewer?.editor.waehlenAbbrechen();const t=ye(s.z,e);if(!t){x("Für die Kalibrierung fehlen Maßstab oder Bezugspunkt.","warn");return}await m([{op:"kalibrierung",wert:t}])&&(s.entwurf=null,x(e?"Plan kalibriert und gesperrt – jetzt die Bohrungen ziehen.":"Kalibrierung übernommen.","ok"),await s.viewer?.ansicht(s.z?.unterlage?.art==="schnitt"?"sued":"oben"))}async function _n(e){const t=s.z.unterlage;t?.kalibrierung&&await m([{op:"kalibrierung",wert:{...t.kalibrierung,gesperrt:e}}])}async function Ln(e){const t=e.target,n=t.files?.[0];if(t.value="",!n)return;const i=await v(()=>k.unterlage(s.sig,n,U,0),"Unterlage wird gelesen …");i&&(D(i),s.entwurf=null,g(),await ue(),await s.viewer?.lageModus(!0),await s.viewer?.ansicht(i.unterlage?.art==="schnitt"?"sued":"oben"))}async function Ae(e,t){const n=await v(()=>k.unterlageSeite(s.sig,e,t),"Seite wird gelesen …");n&&(D(n),s.entwurf=null,g(),await ue(),await s.viewer?.ansicht(t==="schnitt"?"sued":"oben"))}async function Nn(){if(!confirm("Unterlage mit ihrer Kalibrierung entfernen? Gesetzte Bohrungen behalten ihre Lage."))return;const e=await v(()=>k.unterlageEntfernen(s.sig));e&&(D(e),s.entwurf=null,g(),await ue())}const E=(e,t,n=!0)=>a`<details class="abschnitt" ?open=${n}><summary>${e}</summary><div class="abschnitt-inhalt">${t}</div></details>`;function H(e,t,n,i){return a`<button class=${`punkt ${le===t?"aktiv":""} ${n?"gesetzt":""}`} ?disabled=${i}
    @click=${()=>xn(t)}>${le===t?"… im Plan klicken":n?`${e} ✓`:e}</button>`}function Pn(e){const t=We(e.epsg,e.x,e.y);return t?a`<p class=${`klein ${t.ok?"ok":"warn"}`}>${t.ok?"✓":"⚠"} ${t.text}</p>`:u}function En(e){const t=e.unterlage,n=Je(e),i=!!t.kalibrierung?.gesperrt,l=t.art==="plan",r=n.p1&&n.p2?Math.hypot(n.p2.u-n.p1.u,n.p2.v-n.p1.v):null,o=ye(e),h=o?Ye(o.massstab,t.mm_pro_px):null,p=e.viewer.bohrungen.filter(c=>c.x!==null&&(l?!/Plan|Viewer/.test(c.quelle):c.gok_bekannt));return a`
    <p class=${`status ${t.kalibrierung?i?"ok":"":"warn"}`}>
      ${t.kalibrierung?a`${i?"🔒 gesperrt · ":""}${De(t)}${l?` · ${Be(t.kalibrierung.epsg)}`:""}`:"nicht kalibriert"}
      ${s.entwurf&&JSON.stringify({...s.entwurf,gesperrt:!1})!==JSON.stringify({...t.kalibrierung??{},gesperrt:!1})?a`<br><span class="leise">Vorschau: ${De(t,s.entwurf)} (noch nicht übernommen)</span>`:u}
    </p>
    ${i?a`
      <p class="leise klein">Der Plan liegt fest. ${l?"Bohrungen unten mit „Punkte setzen“ in den Plan klicken oder im Viewer ziehen – nur in x/y":"Bohrungen im Viewer ziehen – entlang der Station; die Höhe nur ohne GOK aus dem PDF"}.</p>
      <button @click=${()=>_n(!1)}>🔓 Entsperren (neu kalibrieren)</button>`:a`
      <fieldset class="gruppe">
        <legend>1 · Maßstab ${d("massstab")}</legend>
        <div class="umschalter">
          <label><input type="radio" name="massart" .checked=${n.massArt==="strecke"} @change=${()=>{n.massArt="strecke",z()}}> Strecke messen</label>
          <label><input type="radio" name="massart" .checked=${n.massArt==="n"} @change=${()=>{n.massArt="n",z()}}> 1:n eingeben</label>
        </div>
        ${n.massArt==="strecke"?a`
          <div class="zeile">${H("Punkt 1","p1",n.p1,!1)}${H("Punkt 2","p2",n.p2,!1)}</div>
          <div class="zeile">
            <span class="leise klein">${r?`gemessen ${w(r,0)} px`:"zwei Punkte anklicken"}</span>
            <label class="inline">wahre Länge <input type="number" step="0.01" min="0" class="kurz" .value=${$(n.meter===null?"":String(n.meter))}
              @input=${c=>{n.meter=S(c),z()}}> m</label>
          </div>`:a`
          <label class="inline">Maßstab 1: <input type="number" step="1" min="1" class="kurz" .value=${$(n.n===null?"":String(n.n))}
            @input=${c=>{n.n=S(c),z()}}></label>`}
        ${h?a`<p class="leise klein">ergibt 1:${Math.round(h).toLocaleString("de-DE")}</p>`:u}
      </fieldset>
      ${l?u:a`
        <fieldset class="gruppe">
          <legend>Höhenmaßstab ${d("hoehe")}</legend>
          <div class="umschalter">
            <label><input type="radio" name="hoeheart" .checked=${n.hoeheArt==="gleich"} @change=${()=>{n.hoeheArt="gleich",z()}}> wie Länge</label>
            <label><input type="radio" name="hoeheart" .checked=${n.hoeheArt==="n"} @change=${()=>{n.hoeheArt="n",z()}}> 1:n</label>
            <label><input type="radio" name="hoeheart" .checked=${n.hoeheArt==="strecke"} @change=${()=>{n.hoeheArt="strecke",z()}}> messen</label>
          </div>
          ${n.hoeheArt==="n"?a`<label class="inline">Höhe 1: <input type="number" step="1" min="1" class="kurz"
              .value=${$(n.hoeheN===null?"":String(n.hoeheN))} @input=${c=>{n.hoeheN=S(c),z()}}></label>`:u}
          ${n.hoeheArt==="strecke"?a`
            <div class="zeile">${H("Höhe oben","h1",n.h1,!1)}${H("Höhe unten","h2",n.h2,!1)}</div>
            <label class="inline">Höhenunterschied <input type="number" step="0.01" min="0" class="kurz"
              .value=${$(n.hoeheMeter===null?"":String(n.hoeheMeter))} @input=${c=>{n.hoeheMeter=S(c),z()}}> m</label>`:u}
        </fieldset>`}
      <fieldset class="gruppe">
        <legend>2 · Bezugspunkt ${d("bezug")}</legend>
        <div class="zeile">${H("Punkt im Plan wählen","bezug",n.bezug,!1)}</div>
        <div class="zeile">
          <label class="feld schmal"><span>${l?"Rechtswert":"Station [m]"}</span>
            <input type="number" step="0.01" .value=${$(n.x===null?"":String(n.x))} @input=${c=>{n.x=S(c),z()}}></label>
          <label class="feld schmal"><span>${l?"Hochwert":"Höhe [m NHN]"}</span>
            <input type="number" step="0.01" .value=${$(n.y===null?"":String(n.y))} @input=${c=>{n.y=S(c),z()}}></label>
        </div>
        ${l?a`
          <label class="feld breit"><span>Koordinatensystem (EPSG) ${d("epsg")}</span>
            ${Me(n.epsg,c=>{n.epsg=c,z()})}</label>
          ${Pn(n)}`:u}
        ${p.length?a`
          <label class="inline klein">oder von Bohrung
            <select @change=${c=>{const B=e.viewer.bohrungen.find(M=>M.id===c.target.value);B&&(n.x=B.x,n.y=l?B.y:B.gok,z())}}>
              <option value="">–</option>
              ${p.map(c=>a`<option value=${c.id}>${c.code}</option>`)}
            </select></label>`:u}
      </fieldset>
      ${l?a`
        <fieldset class="gruppe">
          <legend>3 · Drehung ${d("drehung")}</legend>
          <div class="zeile">
            <label class="inline"><input type="number" step="0.1" class="kurz" .value=${$(String(n.drehung))}
              @input=${c=>{n.drehung=S(c)??0,z()}}> ° gegen den Uhrzeigersinn</label>
          </div>
        </fieldset>`:u}
      <div class="zeile knopfzeile">
        <button ?disabled=${!o} @click=${()=>Ee(!1)}>Übernehmen</button>
        <button class="primaer" ?disabled=${!o} @click=${()=>Ee(!0)}>🔒 Übernehmen und sperren</button>
        ${d("sperren")}
      </div>
      ${t.kalibrierung?a`<button class="link klein" @click=${()=>m([{op:"kalibrierung",wert:null}])}>Kalibrierung zurücksetzen</button>`:u}`}`}function An(e){const t=e.unterlage;return t?a`
    <p><b>${t.name}</b> <span class="leise">· ${t.art==="plan"?"Lageplan":"Längsschnitt"}</span></p>
    <div class="zeile">
      ${(t.seiten??1)>1?a`<label class="inline">Seite <select @change=${n=>Ae(Number(n.target.value),t.art)}>
          ${Array.from({length:t.seiten},(n,i)=>a`<option value=${i} .selected=${i===t.seite}>${i+1}</option>`)}
        </select></label>`:u}
      <label class="inline">Ansicht <select @change=${n=>Ae(t.seite,n.target.value)}>
        <option value="plan" .selected=${t.art==="plan"}>Lageplan</option>
        <option value="schnitt" .selected=${t.art==="schnitt"}>Längsschnitt</option>
      </select></label>
    </div>
    <label class="inline">Deckkraft ${d("deckkraft")}
      <input type="range" min="0.1" max="1" step="0.05" .value=${String(s.viewer?.editor.deckkraft??.85)}
        @input=${n=>{s.viewer&&(s.viewer.editor.deckkraft=Number(n.target.value),s.viewer.editor.bildSichtbarkeit())}}></label>
    <button class="link klein" @click=${Nn}>Unterlage entfernen</button>`:a`
      <p class="leise klein">Lageplan (von oben) oder Längsschnitt (von der Seite) als PDF – er liegt im Viewer unter den Bohrungen.</p>
      <div class="umschalter">
        <label><input type="radio" name="neueart" .checked=${U==="plan"} @change=${()=>{U="plan"}}> Lageplan</label>
        <label><input type="radio" name="neueart" .checked=${U==="schnitt"} @change=${()=>{U="schnitt"}}> Längsschnitt</label>
      </div>
      <label class="datei-knopf"><input type="file" accept=".pdf,application/pdf" @change=${Ln}>PDF wählen …</label>`}function Kn(e){const t=e.unterlage,n=!t||!!t.kalibrierung?.gesperrt,i=e.viewer.bohrungen.filter(o=>o.x===null),l=e.lage_modus==="reihe",r=!l&&t?.art==="plan"&&!!t.kalibrierung?.gesperrt;return a`
    ${n?u:a`<p class="warnung">Erst kalibrieren und sperren (🔒) – dann Punkte setzen oder Bohrungen ziehen.</p>`}
    ${r?Rn(e):u}
    ${i.length?a`
      <p class="klein">Ohne Lage (${i.length}) – ${r?"anklicken = als Nächste setzen, oder":""} in den Viewer ziehen
        ${d("ohne_lage")}</p>
      <div class="parkplatz">
        ${i.map(o=>a`<span class=${`park ${n?"":"gesperrt"} ${s.punktModus&&s.naechste===o.id?"aktiv":""}`}
          title=${r?"Klick: als nächste Bohrung setzen · Ziehen: direkt in den Viewer":"In den Viewer ziehen"}
          @pointerdown=${h=>s.viewer?.editor.ziehenStart(h,o.id,!0)}
          @click=${()=>{r&&re(!0,o.id)}}>${o.code}</span>`)}
      </div>`:a`<p class="leise klein">Alle Bohrungen im Modell haben eine Lage.</p>`}
    ${r?Tn(e):u}
    ${l?Fn(e):u}`}function re(e,t){s.punktModus=e,t!==void 0?s.naechste=t:e&&!s.naechste&&(s.naechste=nn()),s.viewer?.editor.punktModusSetzen(e),g()}function Rn(e){const t=e.viewer.bohrungen.filter(i=>i.x===null),n=e.viewer.bohrungen.filter(i=>i.x!==null);return a`
    <div class="zeile">
      <button class=${s.punktModus?"primaer":""} @click=${()=>re(!s.punktModus)}>
        ${s.punktModus?"● Punkte setzen – Klick in den Plan":"＋ Punkte im Plan setzen"}</button>
      ${s.punktModus?a`<button class="leise-knopf" @click=${()=>re(!1)}>Fertig (Esc)</button>`:u}
      ${d("punkte")}
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
      <p class="leise klein">Danach ist automatisch die nächste Bohrung ohne Lage dran.</p>`:u}`}function Tn(e){const t=e.viewer.bohrungen.filter(r=>r.x!==null&&/Plan|Viewer/.test(r.quelle)),n=e.viewer.bohrungen,i=n.filter(r=>r.x===null);if(!t.length&&!e.punkte.length)return u;const l=(r,o)=>a`<span class="leise klein">R ${w(r)}<br>H ${w(o)}</span>`;return a`
    <p class="klein">Gesetzte Punkte (${t.length+e.punkte.length})</p>
    <table class="tabelle kompakt punkte">
      <tbody>
        ${e.punkte.map(r=>a`
          <tr class=${`frei ${s.viewer?.editor.punktGewaehlt===r.id?"gewaehlt":""}`}>
            <td><button class="link" title="Im Viewer wählen" @click=${()=>{s.viewer?.editor.punktWaehlen(r.id),g()}}>◆ ${r.id}</button></td>
            <td>${l(r.x,r.y)}</td>
            <td><select aria-label=${`${r.id} zuordnen`} @change=${o=>{const h=o.target.value;h&&m([{op:"punkt_zuordnen",punkt:r.id,bohrung:h}])}}>
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
            <td><select aria-label=${`${r.code} umhängen`} @change=${o=>{const h=o.target.value;h==="-"?m([{op:"lage_loesen",id:r.id}]):h&&h!==r.id&&m([{op:"lage_umhaengen",id:r.id,nach:h}])}}>
              <option value=${r.id} selected>${r.code}</option>
              <option value="-">– Zuordnung lösen (freier Punkt) –</option>
              ${i.length?a`<optgroup label="Andere Bohrung (ohne Lage)">${i.map(o=>a`<option value=${o.id}>${o.code}</option>`)}</optgroup>`:u}
            </select></td>
            <td><button class="symbol" title="Lage entfernen (Bohrung wieder ohne Lage)" @click=${()=>m([{op:"lage_entfernen",id:r.id}])}>✕</button></td>
          </tr>`)}
      </tbody>
    </table>`}function Fn(e){const t=e.reihe.map(i=>i.id),n=(i,l)=>{const r=[...t],[o]=r.splice(i,1);r.splice(Math.max(0,Math.min(r.length,i+l)),0,o),m([{op:"reihe",reihenfolge:r}],{leise:!0})};return a`
    <div class="zeile">
      <label class="inline">Standardabstand ${d("standardabstand")}
        <input type="number" step="1" min="1" class="kurz" .value=${$(String(e.reihe_standard))}
          @change=${i=>m([{op:"reihe",standard:S(i)}])}> m</label>
    </div>
    <table class="tabelle kompakt reihe">
      <thead><tr><th></th><th>Bohrung</th><th>Abstand [m] ${d("reihe")}</th><th>Station [m]</th></tr></thead>
      <tbody>
        ${e.reihe.map((i,l)=>a`
          <tr>
            <td class="pfeile"><button class="symbol" ?disabled=${l===0} title="nach vorn" @click=${()=>n(l,-1)}>▲</button><button class="symbol"
              ?disabled=${l===t.length-1} title="nach hinten" @click=${()=>n(l,1)}>▼</button></td>
            <td>${i.code}</td>
            <td><input type="number" step="0.1" min="0" class="kurz" ?disabled=${l===0} .value=${$(i.abstand===null?"":String(i.abstand))}
              @change=${r=>m([{op:"reihe",abstand:{[i.id]:S(r)}}],{leise:!0})}></td>
            <td><input type="number" step="0.1" class="kurz" .value=${$(String(i.station))} title=${i.quelle_text}
              @change=${r=>m([{op:"reihe",station:{[i.id]:S(r)}}],{leise:!0})}></td>
          </tr>`)}
      </tbody>
    </table>`}async function On(e){const t=e.target,n=[...t.files??[]];if(t.value="",!n.length)return;const i=W===void 0?s.z?.viewer.epsg??null:W,l=await v(()=>k.dgm(s.sig,n,i),"DGM wird gelesen …");if(l){D(l),g();const r=l.gelaende?.pruefung?.warnungen.length??0;x(r?"DGM geladen – Hinweise zum Vergleich beachten.":"DGM geladen.",r?"warn":"ok")}}async function In(){const e=await v(()=>k.dgmAbruf(s.sig,we),"DGM wird beim Land abgerufen …");if(e){D(e),g();const t=e.gelaende?.pruefung?.warnungen.length??0;x(t?"DGM vom Land geladen – Hinweise zum Vergleich beachten.":"DGM vom Land geladen.",t?"warn":"ok")}}function Ke(e){return e.lage_modus!=="koordinaten"?u:a`
    <div class="zeile">
      <label class="inline">Rand <input type="number" min="0" max="1000" step="25" class="kurz" aria-label="Rand um die Bohrungen"
        .value=${$(String(we))} @change=${t=>{we=S(t)??100}}> m</label>
      <button @click=${In} title="Sendet den Ausschnitt um die Bohrungen an den Dienst des Landes">
        DGM vom Land abrufen</button>${d("dgm_land")}
    </div>
    <p class="leise klein">Brandenburg mit Berlin und NRW (DGM1, WCS). Sendet den Ausschnitt um die Bohrungen an den Dienst.</p>`}async function jn(){if(!confirm("DGM aus dem Projekt entfernen? Übernommene GOK bleiben (Quelle DGM)."))return;const e=await v(()=>k.dgmEntfernen(s.sig));e&&(D(e),g())}const ge={ok:["✓","ok"],abweichung:["⚠ weicht ab","warn"],ohne_gok:["GOK fehlt",""],aus_dgm:["aus dem DGM","leise"],ausserhalb:["außerhalb","leise"],ohne_lage:["ohne Lage","leise"],anderes_system:["anderes EPSG","warn"]},Re=e=>e===null?"":Math.abs(e)<.005?w(0):`${e>0?"+":""}${w(e)}`;function Hn(e){const t=e.gelaende,n=p=>a`<label class="datei-knopf"><input type="file" multiple aria-label="DGM-Dateien"
    accept=".xyz,.txt,.csv,.asc,.tif,.tiff,.zip,.gz" @change=${On}>${p}</label>`,i=W===void 0?e.viewer.epsg??null:W,l=a`<label class="feld breit"><span>System der Datei (XYZ, ASCII) ${d("dgm_epsg")}</span>
    ${Me(i,p=>{W=p,g()},"System der DGM-Datei")}</label>`;if(!t)return a`
      <p class="leise klein">DGM-Kachel(n) des Landes (Open Data, z. B. DGM1) als XYZ, ASCII-Raster oder GeoTIFF, auch als
        ZIP – Höhen in m NHN. Damit prüft die App die GOK, schlägt fehlende vor und legt das Gelände ins Modell.</p>
      ${Ke(e)}
      ${l}
      ${n("DGM-Dateien wählen …")}`;const r=t.info,o=t.pruefung,h=r.quelle;return a`
    <p><b>${r.name}</b><br><span class="leise klein">${Be(r.epsg)} · Raster ${w(r.dx,1)} m ·
      ${r.spalten.toLocaleString("de-DE")} × ${r.zeilen.toLocaleString("de-DE")} · ${w(r.zmin,1)} – ${w(r.zmax,1)} m NHN</span></p>
    ${h?a`<p class="leise klein">${h.anbieter} · <a href=${h.beleg} target="_blank" rel="noopener">${h.lizenz}</a> ·
      ${h.namensnennung} · abgerufen ${h.abgerufen}</p>`:u}
    ${t.fehler?a`<p class="warnung klein">${t.fehler}</p>`:u}
    ${o?a`
      <table class="tabelle kompakt gelaende">
        <thead><tr><th>Bohrung</th><th class="zahl">GOK</th><th class="zahl">DGM</th><th class="zahl">Δ [m]</th><th></th></tr></thead>
        <tbody>
          ${o.zeilen.map(p=>a`
            <tr class=${ge[p.status][1]}>
              <td><button class="link" title="Im Viewer wählen" @click=${()=>{s.viewer?.nadelWaehlen(p.id),g()}}>${p.code}</button></td>
              <td class="zahl">${w(p.gok)}</td>
              <td class="zahl">${w(p.dgm)}</td>
              <td class="zahl">${Re(p.differenz)}</td>
              <td class=${`klein ${ge[p.status][1]}`}>${p.status==="ohne_gok"?a`<button class="klein" title="GOK aus dem DGM übernehmen (Quelle DGM)"
                    @click=${()=>m([{op:"gok_aus_dgm",ids:[p.id]}])}>übernehmen</button>`:ge[p.status][0]}</td>
            </tr>`)}
        </tbody>
      </table>
      ${o.verglichen?a`<p class="leise klein">${o.verglichen} verglichen · Median ${Re(o.median)} m ·
        größte Abweichung ${w(o.max)} m (unauffällig bis ${w(o.toleranz,1)} m)</p>`:u}
      ${o.warnungen.map(p=>a`<p class="warnung klein">⚠ ${p}</p>`)}
      ${o.vorschlaege>1?a`<button @click=${()=>m([{op:"gok_aus_dgm"}])}>
        Alle ${o.vorschlaege} fehlenden GOK aus dem DGM übernehmen</button>`:u}`:u}
    ${Ke(e)}
    ${l}
    <div class="zeile">${n("Andere DGM-Dateien …")}
      <button class="link klein" @click=${jn}>DGM entfernen</button></div>`}async function Un(){const e=await v(()=>k.sgdAbfrage(s.sig,ke),"Dienste der Länder werden abgefragt …");if(!e?.sgd)return;D(e),A.clear(),g();const t=e.sgd;x(`${t.treffer.length} Bohrungen der Länder im Umkreis von ${w(t.radius,0)} m`+(t.fehler.length?` – ${t.fehler.length} Dienst(e) ohne Antwort`:""),t.fehler.length?"warn":"ok")}async function Vn(){const e=[...A].map(n=>({dienst:n.slice(0,n.indexOf("/")),id:n.slice(n.indexOf("/")+1)})),t=await v(()=>k.sgdUebernehmen(s.sig,e),"Schichtdaten werden beim Land geholt …");if(t){D(t.zustand),A.clear();for(const n of t.meldungen)x(n,"ok");await ue(),g()}}function Wn(e){return e.gutachten?a`<span class="ok" title="Dieselbe Bohrung im Gutachten">= ${e.gutachten}</span>`:e.uebernommen?a`<span class="ok">✓ im Projekt</span>`:e.schichten==="boreholeml"?a`${e.schichten_n} Schichten`:e.schichten==="grafik"&&e.profil?a`<a href=${e.profil} target="_blank" rel="noopener">Profil ↗</a>`:a`<span class="leise">${e.schichten==="ohne Petrographie"?"ohne Petrographie":"keine Schichten"}</span>`}async function Cn(){const e=await v(()=>k.gebaeudeAbruf(s.sig,ve),"Gebäude werden beim Land abgerufen …");e&&(D(e),g(),x(`${e.gebaeude?.anzahl??0} Gebäude geladen – im Modell als Umgebung.`,"ok"))}async function Zn(){const e=await v(()=>k.gebaeudeEntfernen(s.sig));e&&(D(e),g())}function qn(e){if(e.lage_modus!=="koordinaten")return a`<p class="leise klein">Nur mit Lage nach Koordinaten.</p>`;const t=e.gebaeude,n=a`
    <div class="zeile">
      <label class="inline">Rand <input type="number" min="0" max="1000" step="25" class="kurz" aria-label="Rand der Gebäude"
        .value=${$(String(ve))} @change=${l=>{ve=S(l)??100}}> m</label>
      <button @click=${Cn} title="Lädt die Kacheln (1 × 1 km) um die Bohrungen beim Land">
        ${t?"Gebäude neu abrufen":"Gebäude vom Land abrufen"}</button>${d("gebaeude")}
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
    <p class="leise klein">Im Viewer mit dem Knopf „Gebäude“ ein- und ausblendbar.</p>
    ${n}
    <button class="link klein" @click=${Zn}>Gebäude entfernen</button>`}function Jn(e){if(e.lage_modus==="reihe")return a`<p class="leise klein">Nur mit Lage nach Koordinaten.</p>`;const t=e.sgd,n=a`
    <p class="leise klein">Bohrungen aus den Datenbanken der Geologischen Dienste um die Mitte des Projekts.
      <b>Die Abfrage sendet die Lage des Projekts an den Dienst des Landes.</b></p>
    <div class="zeile">
      <label class="inline">Umkreis <input type="number" min="10" max="2000" step="50" class="kurz" aria-label="Umkreis der Abfrage"
        .value=${$(String(ke))} @change=${h=>{ke=S(h)??250}}> m</label>
      <button @click=${Un}>${t?"Neu abfragen":"Abfragen"}</button>
    </div>`;if(!t)return n;const i=t.gegenprobe,l=i.anzahl>0&&(i.lage_max??0)<=1&&(i.gok_max??0)<=.5,r=t.treffer.slice(0,60),o=t.treffer.filter(h=>h.uebernehmbar).length;return a`
    ${n}
    <p class="klein">${t.treffer.length} Bohrungen im Umkreis von ${w(t.radius,0)} m · ${t.zeit}</p>
    ${i.anzahl?a`<p class=${`klein ${l?"ok":"warnung"}`}>${l?"✓":"⚠"} ${i.anzahl} Bohrungen des Gutachtens auch
      beim Land: Lage ≤ ${w(i.lage_max)} m${i.gok_max!==null?a`, GOK ≤ ${w(i.gok_max)} m`:u}${l?"":" – Lage und GOK prüfen"}</p>`:u}
    ${t.fehler.map(h=>a`<p class="warnung klein">${h.dienst}: ${h.fehler}</p>`)}
    ${r.length?a`
      <table class="tabelle kompakt sgd">
        <thead><tr><th></th><th>Bohrung</th><th class="zahl">Abstand</th><th class="zahl">GOK</th><th class="zahl">Teufe</th><th>Schichten</th></tr></thead>
        <tbody>
          ${r.map(h=>{const p=`${h.dienst}/${h.id}`;return a`<tr class=${h.gutachten?"doppelt":""}>
              <td>${h.uebernehmbar?a`<input type="checkbox" aria-label=${`${h.name} übernehmen`} .checked=${A.has(p)}
                @change=${c=>{c.target.checked?A.add(p):A.delete(p),g()}}>`:u}</td>
              <td title=${`${h.dienst} · ID ${h.id}${h.datum?` · ${h.datum}`:""}`}>${h.name}</td>
              <td class="zahl">${w(h.abstand,0)}</td>
              <td class="zahl">${w(h.gok)}</td>
              <td class="zahl">${w(h.teufe,1)}</td>
              <td class="klein">${Wn(h)}</td>
            </tr>`})}
        </tbody>
      </table>
      ${t.treffer.length>r.length?a`<p class="leise klein">… und ${t.treffer.length-r.length} weitere (Umkreis verkleinern)</p>`:u}`:u}
    ${o?a`<button class="primaer" ?disabled=${!A.size} @click=${Vn}>
      Ausgewählte übernehmen (${A.size})</button>
      <p class="leise klein">Nur Bohrungen mit Schichtdaten in BoreholeML (NRW, Baden-Württemberg); sie kommen mit Quelle und Lizenz ins Projekt.</p>`:u}
    ${t.quellen.map(h=>a`<p class="leise klein">Quelle: ${h.namensnennung} · <a href=${h.beleg} target="_blank" rel="noopener">Dienst</a></p>`)}
    <button class="link klein" @click=${async()=>{const h=await v(()=>k.sgdVerwerfen(s.sig));h&&(D(h),g())}}>Abfrage verwerfen</button>`}function Qn(e){const t=s.viewer;t&&(!e.unterlage||e.unterlage.kalibrierung?.gesperrt||!f?t.editor.hilfsmarken({}):t.editor.hilfsmarken({strecke:f.massArt==="strecke"?[f.p1,f.p2]:[],hoehe:f.hoeheArt==="strecke"?[f.h1,f.h2]:[],bezug:f.bezug}))}let Te=!1;function Xn(){const e=s.z;Je(e),Qn(e);const t=e.lage_modus!=="reihe"&&e.unterlage?.art==="plan"&&!!e.unterlage.kalibrierung?.gesperrt;return s.punktModus&&!t&&(s.punktModus=!1),s.viewer?.editor.punktModusSetzen(s.punktModus),Te||(Te=!0,window.addEventListener("keydown",n=>{n.key==="Escape"&&s.schritt==="lage"&&s.punktModus&&re(!1)})),a`
    <div class="app-panel links">
      ${E(a`Lage der Bohrungen ${d("lage_art")}`,a`
        <div class="umschalter">
          <label><input type="radio" name="lagemodus" .checked=${e.lage_modus==="koordinaten"}
            @change=${()=>m([{op:"lage_modus",wert:"koordinaten"}])}> Koordinaten (Lageplan)</label>
          <label><input type="radio" name="lagemodus" .checked=${e.lage_modus==="reihe"}
            @change=${()=>m([{op:"lage_modus",wert:"reihe"}])}> Reihe (Längsschnitt)</label>
        </div>`)}
      ${E(a`Unterlage ${d("unterlage")}`,An(e))}
      ${e.unterlage?E(a`Kalibrieren`,En(e)):u}
      ${E(a`Bohrungen setzen`,Kn(e))}
      ${E(a`Gelände (DGM)${e.gelaende?.pruefung?.warnungen.length?" ⚠":e.gelaende?" ✓":""} ${d("gelaende")}`,Hn(e),!!e.gelaende)}
      ${E(a`Bohrungen der Länder${e.sgd?.gegenprobe.anzahl?" ✓":""} ${d("sgd")}`,Jn(e),!!e.sgd)}
      ${E(a`Gebäude (LoD2)${e.gebaeude?" ✓":""} ${d("gebaeude")}`,qn(e),!!e.gebaeude)}
      ${E(a`Darstellung`,a`
        <label class="inline">Ø Bohrsäulen ${d("durchmesser")}
          <input type="number" step="0.1" min="0" class="kurz" placeholder=${`auto ${w(e.durchmesser_auto,1)}`}
            .value=${$(e.durchmesser===null?"":String(e.durchmesser))}
            @change=${n=>m([{op:"durchmesser",wert:S(n)}])}> m</label>
        <p class="leise klein">Je Bohrung im Schritt Bohrungen (Ø Säule). Leer = automatisch nach Modellgröße.</p>`,!1)}
      ${e.hinweise.length?a`<div class="hinweisliste">${e.hinweise.map(n=>a`<p class="klein">ℹ ${n}</p>`)}</div>`:u}
    </div>`}const K=(e,t=1)=>e==null?"–":e.toLocaleString("de-DE",{minimumFractionDigits:t,maximumFractionDigits:t});let O="",pe=null,Fe="";function Yn(e){return!e||e.quelle!=="DGM"?"aus den GOK der Bohrungen":`aus dem DGM (an den Bohrungen auf die GOK, GOK − DGM bis ${K(Number(e.gok_minus_dgm_max_m),2)} m)`}function et(){const e=s.z.einstellungen,t=(l,r)=>m([{op:"einstellungen",[l]:r}]),n=(l,r,o,h,p)=>{const c=e[l];return a`
      <div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${c===null} @change=${B=>t(l,B.target.checked?null:h)}> ${r} automatisch</label>${d(p)}
        ${c===null?u:a`<input type="number" step="any" class="kurz" .value=${$(String(c))}
          @change=${B=>t(l,Number(B.target.value))}> ${o}`}
      </div>`},i=s.modell?.bericht?.parameter??{};return a`
    <section class="karte">
      <h3>Modell</h3>
      <div class="einstellung">
        <span>Interpolation ${d("methode")}</span>
        <label class="inline"><input type="radio" name="methode" .checked=${e.methode==="idw"} @change=${()=>t("methode","idw")}> IDW</label>
        <label class="inline"><input type="radio" name="methode" .checked=${e.methode==="tps"} @change=${()=>t("methode","tps")}> Dünnplatten-Spline</label>
      </div>
      ${n("puffer","Puffer","m",Number(i.puffer_m??20),"puffer")}
      ${n("raster","Raster","m",Number(i.raster_m??5),"raster")}
      ${n("basis","Modellbasis","m NHN",Math.floor(Number(i.basis_nhn??0)),"basis")}
      <div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${e.gok_relativ} @change=${l=>t("gok_relativ",l.target.checked)}> fehlende GOK: Gelände = 0 m</label>${d("gok_relativ")}
      </div>
      ${s.z.gelaende?a`<div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${e.gelaende_dgm} @change=${l=>t("gelaende_dgm",l.target.checked)}> Gelände aus dem DGM</label>${d("gelaende_dgm")}
      </div>`:u}
      ${i.raster_m!==void 0?a`<p class="leise klein">gerechnet: Puffer ${K(Number(i.puffer_m),0)} m · Raster ${K(Number(i.raster_m))} m ·
        Basis ${K(Number(i.basis_nhn),2)} m NHN · Fläche ${K(Number(i.flaeche_m2)/1e4,2)} ha ·
        Gelände ${Yn(i.gelaende)}</p>`:u}
    </section>`}function nt(){const e=s.modell?.bericht;if(!e)return u;const t=s.z.vorgabe??e.vorlage_einheiten,n=JSON.stringify(t);(!pe||Fe!==n)&&(pe=t.map(r=>({name:r.name,bodenarten:r.bodenarten.join(", ")})),Fe=n);const i=pe,l=()=>m([{op:"vorgabe",wert:i.filter(r=>r.name.trim()).map(r=>({name:r.name.trim(),bodenarten:r.bodenarten.split(",").map(o=>o.trim()).filter(Boolean)}))}]);return a`
    <section class="karte">
      <h3>Einheiten festlegen ${d("einheiten")}</h3>
      <p class="leise klein">${s.z.vorgabe?"Vorgegeben (eigene Einheiten).":"Automatisch korreliert – hier umbenennen oder Bodenarten zusammenlegen."}</p>
      <table class="tabelle kompakt vorgabe">
        <colgroup><col class="pfeil"><col><col><col class="weg"></colgroup>
        <thead><tr><th></th><th>Einheit</th><th>Bodenarten (mit Komma)</th><th></th></tr></thead>
        <tbody>
          ${i.map((r,o)=>a`
            <tr>
              <td class="pfeile"><button class="symbol" ?disabled=${o===0} @click=${()=>{i.splice(o-1,0,...i.splice(o,1)),g()}}>▲</button><button
                class="symbol" ?disabled=${o===i.length-1} @click=${()=>{i.splice(o+1,0,...i.splice(o,1)),g()}}>▼</button></td>
              <td><input .value=${$(r.name)} @input=${h=>{r.name=h.target.value}}></td>
              <td><input .value=${$(r.bodenarten)} @input=${h=>{r.bodenarten=h.target.value}}></td>
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
    </section>`}function tt(){const e=s.modell,t=e?.bericht,n=t?.einheiten.find(i=>i.name===O);return a`
    <div class="schritt-einheiten">
      <div class="spalte">
        ${et()}
        ${nt()}
      </div>
      <div class="spalte breit">
        ${s.rechnet?a`<div class="karte"><div class="kreisel klein"></div> Modell wird gerechnet …</div>`:u}
        ${e?.fehler?a`<div class="karte warnung">Noch kein Modell: ${e.fehler}
          <button class="link" @click=${()=>P("lage")}>→ Lage setzen</button></div>`:u}
        ${t?a`
          <section class="karte">
            <h3>Einheiten (${t.einheiten.length})</h3>
            <table class="tabelle einheiten">
              <thead><tr><th></th><th>Einheit</th><th>Bodenarten</th><th>Volumen [m³]</th><th>max. Mächtigkeit [m]</th>
                <th title="in Bohrungen vorhanden / fehlt / unter der Endteufe">✓ / – / ?</th><th>Hinweise</th></tr></thead>
              <tbody>
                ${t.einheiten.map(i=>a`
                  <tr class=${i.name===O?"gewaehlt":""} @click=${()=>{O=O===i.name?"":i.name,g()}}>
                    <td><span class="farbfeld" style=${`background:${i.farbe}`}></span></td>
                    <td><b>${i.name}</b></td>
                    <td>${i.bodenarten.join(", ")}</td>
                    <td class="zahl">${Math.round(i.volumen_m3).toLocaleString("de-DE")}</td>
                    <td class="zahl">${K(i.maechtigkeit_max_m,2)}</td>
                    <td class="zahl">${i.bohrungen.vorhanden.length} / ${i.bohrungen.fehlt.length} / ${i.bohrungen.unbekannt.length}</td>
                    <td class="klein">${i.hinweise.join("; ")}</td>
                  </tr>`)}
              </tbody>
            </table>
          </section>
          <section class="karte profil-karte">
            <h3>Einheiten je Bohrung <span class="leise klein">(m NHN, Klick wählt die Einheit)</span></h3>
            <div class="profil-scroll">${bn(t,{hoehe:380,gewaehlt:O,waehlen:i=>{O=i,g()}})}</div>
          </section>
          ${n?a`
            <section class="karte">
              <h3><span class="farbfeld" style=${`background:${n.farbe}`}></span> ${n.name}: Beschreibungen aus dem PDF</h3>
              <table class="tabelle kompakt">
                <thead><tr><th>Bohrung</th><th>Tiefe [m]</th><th>Bodenart</th><th>Beschreibung</th></tr></thead>
                <tbody>${n.schichten.map(i=>a`
                  <tr><td>${i.bohrung}</td><td class="zahl">${K(i.von,2)}–${K(i.bis,2)}</td><td>${i.bodenart??"unklassifiziert"}</td>
                    <td>${i.beschreibung||a`<span class="leise">–</span>`}</td></tr>`)}</tbody>
              </table>
            </section>`:u}`:u}
      </div>
    </div>`}let oe="";async function it(){const e=await v(()=>k.einchecken(s.sig,oe));e&&(D(e.zustand),oe="",x(`Eingecheckt: v${e.eintrag.nr} · ${e.eintrag.stand.bohrungen[0]}/${e.eintrag.stand.bohrungen[1]} Bohrungen geprüft`,"ok"),g())}const at=new Set([25831,25832,25833,4647,5650]);let Y=(()=>{try{return localStorage.getItem("groundtwin.organisation")??""}catch{return""}})();function st(){const e=s.z,t=e.bohrungen.filter(l=>l.modell),n=t.filter(l=>l.schichten_n>0&&l.schichten_geprueft===l.schichten_n&&l.x!==null&&l.y!==null&&l.epsg!==null&&at.has(l.epsg)&&l.gok!==null&&e.lage_modus==="koordinaten"),i=`${k.exportUrl(s.sig,"boreholeml")}?organisation=${encodeURIComponent(Y)}`;return a`
    <label class="feld breit"><span>Organisation (Absender) ${d("boreholeml")}</span>
      <input type="text" aria-label="Organisation für BoreholeML" placeholder="z. B. Ingenieurbüro …" .value=${Y}
        @input=${l=>{Y=l.target.value;try{localStorage.setItem("groundtwin.organisation",Y)}catch{}g()}}></label>
    ${n.length?a`<a class="knopf" href=${i} download>Bohrungen für den Geologischen Dienst (BoreholeML 3.2)</a>`:a`<span class="knopf aus" title="Erst alle Schichten prüfen; Lage in ETRS89/UTM und GOK nötig">Bohrungen für den Geologischen Dienst (BoreholeML 3.2)</span>`}
    <p class="leise klein">${n.length} von ${t.length} Bohrungen exportierbar (vollständig geprüft, ETRS89/UTM, GOK).</p>`}function lt(){const e=s.z,t=s.modell,n=t?.bericht,i=e.pruefstand,l=e.eincheckungen[e.eincheckungen.length-1],r=[["ifc","Baugrundmodell (IFC 4.3)"],["bericht","Prüfbericht (JSON)"],["einheiten","Einheiten-Vorlage (JSON)"],["extraktion","Extraktion (JSON)"],["eingabe","Modell-Eingabe mit Korrekturen (JSON)"],["projekt","Projektstand (JSON)"]];return a`
    <div class="app-panel rechts">
      <section class="abschnitt-flach">
        <h3>Modell</h3>
        ${e.reifegrad.stufe!=="Gutachten"?a`<p class=${`reife ${e.reifegrad.stufe==="Vorerkundung"?"vorerkundung":"gemischt"}`}>
          <b>${e.reifegrad.stufe}</b> – ${e.reifegrad.stufe==="Vorerkundung"?"Bohrungen aus Datenbanken der Länder, kein Gutachten: eine erste Vorstellung für die Planung der Erkundung.":Object.entries(e.reifegrad.anzahl).map(([o,h])=>`${h} ${o}`).join(", ")+": Bohrungen ohne Gutachten sind nicht gegen ein PDF geprüft."}
          ${d("reifegrad")}</p>`:u}
        ${s.rechnet?a`<p><span class="kreisel klein"></span> wird gerechnet …</p>`:u}
        ${t?.fehler?a`<p class="warnung">Noch kein Modell: ${t.fehler}</p>
          <button class="link" @click=${()=>P("lage")}>→ Lage setzen</button>`:u}
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
            automatisch nachführen</label>${d("auto")}
          <span class="fueller"></span>
          <button ?disabled=${s.rechnet} @click=${()=>tn()}>Neu rechnen</button>
        </div>
        <label class="inline">Überhöhung ${d("ueberhoehung")}
          <select @change=${async o=>{const h=Number(o.target.value);await s.viewer?.ueberhoehen(h),await m([{op:"ueberhoehung",wert:h}],{leise:!0})}}>
            ${[1,2,5,10,20].map(o=>a`<option value=${o} .selected=${e.ueberhoehung===o}>${o}×</option>`)}
          </select></label>
      </section>

      <section class="abschnitt-flach">
        <h3>Prüfstand ${d("pruefstand")}</h3>
        <div class="balken"><span>Bohrungen <b>${i.bohrungen[0]}/${i.bohrungen[1]}</b></span><progress max=${i.bohrungen[1]||1} value=${i.bohrungen[0]}></progress></div>
        <div class="balken"><span>Schichten <b>${i.schichten[0]}/${i.schichten[1]}</b></span><progress max=${i.schichten[1]||1} value=${i.schichten[0]}></progress></div>
        <p class="klein">${i.unklassifiziert_offen?a`<span class="warnung">⚠ ${i.unklassifiziert_offen} Schicht(en) nicht klassifiziert</span>
          <button class="link" @click=${()=>P("bohrungen")}>prüfen</button>`:a`<span class="ok">✓ keine offenen Warnungen</span>`}
          · ${i.korrigiert} korrigiert · ${i.manuelle_lage} Lagen manuell · ${i.entfernt} entfernt</p>
        <p class=${`klein ${l&&!e.seit_einchecken_geaendert?"ok":"warn"}`}>
          ${l?`Eingecheckt: ${e.eingecheckt}${e.seit_einchecken_geaendert?" · seitdem geändert":""}`:"noch nicht eingecheckt"}</p>
        <div class="zeile">
          <input class="breit" placeholder="Kommentar (z. B. BK1–BK5 mit Anlage 2 verglichen)" .value=${oe}
            @input=${o=>{oe=o.target.value}}>
        </div>
        <div class="zeile"><button class="primaer" @click=${it}>✓ Stand einchecken</button>${d("einchecken")}</div>
        ${e.eincheckungen.length?a`
          <details class="protokoll"><summary>Protokoll (${e.eincheckungen.length})</summary>
            <ul>${[...e.eincheckungen].reverse().map(o=>a`
              <li><b>v${o.nr}</b> ${o.zeit} · ${o.stand.bohrungen[0]}/${o.stand.bohrungen[1]} Bohrungen, ${o.stand.schichten[0]}/${o.stand.schichten[1]} Schichten
                ${o.kommentar?a`<div class="leise klein">${o.kommentar}</div>`:u}</li>`)}</ul>
          </details>`:u}
      </section>

      <section class="abschnitt-flach">
        <h3>Export ${d("export")}</h3>
        <div class="export-liste">
          ${r.map(([o,h])=>a`<a class=${`knopf ${o==="ifc"?"primaer":""}`} href=${k.exportUrl(s.sig,o)}
            download>${h}</a>`)}
          ${st()}
        </div>
      </section>

      ${t&&(t.hinweise.length||t.nicht_im_modell.length)?a`
        <section class="abschnitt-flach">
          <h3>Hinweise</h3>
          ${t.nicht_im_modell.length?a`<p class="klein"><b>Nicht im Modell:</b> ${t.nicht_im_modell.map(o=>`${o.code} (${o.grund})`).join(", ")}</p>`:u}
          ${t.hinweise.map(o=>a`<p class="klein">ℹ ${o}</p>`)}
        </section>`:u}
    </div>`}const Oe={gutachten:"",bohrungen:"Weiter: Lage",lage:"Weiter: Einheiten",einheiten:"Weiter: Modell",modell:""};function rt(e){const t=s.z;if(!t)return"";const n=t.pruefstand;return e==="gutachten"?"ok":e==="bohrungen"?n.unklassifiziert_offen?"warn":n.bohrungen[0]===n.bohrungen[1]&&n.bohrungen[1]?"ok":"":e==="lage"?t.viewer.bohrungen.filter(l=>l.x===null).length?"warn":"ok":e==="einheiten"||e==="modell"?s.modell?.fehler?"warn":s.modell?.bericht?"ok":"":""}function ot(){const e=s.z;return a`
    <header class="kopf">
      <div class="marke" @click=${()=>P("gutachten")} title="Start">
        <span class="logo">⛰</span>
        <span><b>GroundTwin</b> · Baugrundmodell</span>
      </div>
      <nav class="schritte" aria-label="Schritte">
        ${ee.map(t=>{const n=t.id!=="gutachten"&&!e,i=rt(t.id);return a`
            <button class=${`schritt-knopf ${s.schritt===t.id?"aktiv":""} ${i}`} ?disabled=${n}
              aria-current=${s.schritt===t.id?"step":"false"} @click=${()=>P(t.id)} title=${t.kurz}>
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
            <div class="menue-inhalt" @click=${ct}>
              <button @click=${()=>P("gutachten")}>Anderes Projekt öffnen</button>
              <button @click=${ut}>Alle Korrekturen verwerfen …</button>
              <a href="viewer.html" target="_blank" rel="noopener">Viewer allein öffnen</a>
              ${s.info?a`<a href=${s.info.quellcode} target="_blank" rel="noopener">Quellcode (${s.info.lizenz})</a>`:u}
            </div>
          </details>`:u}
      </div>
    </header>`}function ct(e){e.currentTarget.closest("details")?.removeAttribute("open")}document.addEventListener("click",e=>{for(const t of document.querySelectorAll("details.menue[open]"))t.contains(e.target)||t.removeAttribute("open")});async function ut(){if(!s.sig||!confirm("Alle Korrekturen, Lagen, Prüfhaken und Eincheckungen dieses Projekts verwerfen?"))return;await v(()=>k.zuruecksetzen(s.sig))&&await j(s.sig,"bohrungen")}function ht(){if(s.schritt==="gutachten")return u;const e=ee.findIndex(l=>l.id===s.schritt),t=ee[e-1],n=ee[e+1],i=s.z?.pruefstand;return a`
    <footer class="fuss">
      ${t?a`<button @click=${()=>P(t.id)}>← ${t.titel}</button>`:u}
      <span class="fuss-status">${i?`${i.bohrungen[0]}/${i.bohrungen[1]} Bohrungen · ${i.schichten[0]}/${i.schichten[1]} Schichten geprüft`:""}
        ${i?.unklassifiziert_offen?a` · <span class="warnung">⚠ ${i.unklassifiziert_offen} nicht klassifiziert</span>`:u}</span>
      <span class="fueller"></span>
      ${n&&Oe[s.schritt]?a`<button class="primaer" @click=${()=>P(n.id)}>${Oe[s.schritt]} →</button>`:u}
    </footer>`}function dt(){return s.schritt==="gutachten"||!s.z?dn():s.schritt==="bohrungen"?Dn():s.schritt==="lage"?Xn():s.schritt==="einheiten"?tt():lt()}function gt(){return a`
    ${ot()}
    <main class=${`inhalt schritt-${s.schritt}`}>
      <section id="schritt" class="schritt">${dt()}</section>
    </main>
    ${ht()}
    <div class="meldungen" aria-live="polite">
      ${s.meldungen.map(e=>a`<div class=${`meldung ${e.art}`}>${e.text}</div>`)}
    </div>
    ${s.beschaeftigt?a`<div class="beschaeftigt"><div class="kreisel"></div><span>${s.beschaeftigt}</span></div>`:u}`}const Ie=document.getElementById("app");let I=null;function pt(){en(gt(),Ie);const e=Ie.querySelector("main");I||(I=document.createElement("div"),I.id="buehne",I.className="buehne"),I.parentElement!==e&&e.append(I),document.body.dataset.schritt=s.schritt}an(pt);async function Qe(){const[e,t,n]=location.hash.replace(/^#\/?/,"").split("/").map(decodeURIComponent);if(e&&e!==s.sig){if(await j(e,t||void 0),n&&s.schritt==="bohrungen"){const{bohrungWaehlen:i}=await Xe(async()=>{const{bohrungWaehlen:l}=await import("./store-BfVmWQ09.js").then(r=>r.k);return{bohrungWaehlen:l}},__vite__mapDeps([0,1]),import.meta.url);await i(n)}}else e||await P("gutachten")}window.addEventListener("hashchange",()=>void Qe());s.info=await v(()=>k.info())??null;g();await je();await Qe();window.app=s;
