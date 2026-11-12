const __vite__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["./leaflet-CIGW-MKW.css","./store-CVGYfZHk.js","./preload-helper-Ct5FWWRu.js"])))=>i.map(i=>d[i]);
import"./viewer-Czjhv0Od.js";import{_ as Ae}from"./preload-helper-Ct5FWWRu.js";/* empty css            */import{b as a,A as u,w as Z,D as Hn}from"./lit-element-BS0sz3Y2.js";import{a as $,S as l,n as p,v as w,m as L,o as X,p as zn,s as he,b as Se,c as Ie,d as b,z as P,e as Ge,f as In,g as H,h as Un,i as Vn,j as pe}from"./store-CVGYfZHk.js";import{l as z,m as Wn,k as qe}from"./lage-dDtwcw43.js";import"./three.core-Dd2BBCN2.js";const Bn=a`<span class="ungeprueft" title="Adresse eingetragen, nicht gegen den Dienst geprüft">ungeprüft</span>`;function yn(e,n="Dienste am Standort"){return a`<ul class="dienste klein" aria-label=${n}>${e.map(t=>a`<li class=${t.art}>
    ${t.url?a`<a href=${t.url} target="_blank" rel="noopener noreferrer">${t.text}</a>`:t.text}
    ${t.status==="ungeprueft"?Bn:u}</li>`)}</ul>`}function Cn(e){if(!e?.length)return u;const n=[...new Set(e.map(t=>t.land).filter(t=>t!=="Deutschland"))];return a`<div class="portale" role="note">
    <p class="klein">Kein Datendienst mit Schichtdaten für ${n.length?n.join(", "):"diesen Ort"} – die Bohrungen im Portal ansehen:</p>
    <ul class="dienste klein" aria-label="Portale der Länder">${e.map(t=>a`<li>
      <a href=${t.url} target="_blank" rel="noopener noreferrer">${t.titel}</a> <span class="leise">(${t.land})</span>
      ${t.status==="ungeprueft"?Bn:u}
      ${t.hinweis?a`<div class="leise">${t.hinweis}</div>`:u}</li>`)}</ul>
  </div>`}const Pe={ocr:["OCR für Scans","Liest gescannte PDFs und Text, der nur als Linien gezeichnet ist (SHX). Langsamer; bei Vektor-PDFs nicht nötig."],beispiele:["Beispiele","Fertig ausgewertete Gutachten zum Ausprobieren. Echte Daten: Berlin (georeferenziert) und Talheim (ohne Koordinaten). Dazu Standorte ohne Gutachten, die zeigen, was die Länder liefern: Dortmund (NRW, Bohrungen mit Schichtdaten), Karlsruhe (Baden-Württemberg, Schichten oft ohne Petrographie) und Berlin (nur Kopfdaten: Gelände und Gebäude, kein Schichtenmodell). Die Bohrungen fragt der Schritt Lage auf Klick beim Land ab (Netz nötig)."],karte:["Karte","Eine Karte zum Orientieren: ein Klick setzt den Standort; Rechts- und Hochwert in ETRS89/UTM rechnet die App aus (Zone 32 westlich von 12° Ost, sonst 33) und sagt, was die Dienste der Länder dort liefern. Hintergrund basemap.de (amtlich, © GeoBasis-DE / BKG, CC BY 4.0) oder OpenStreetMap. Die Kacheln laden erst beim Öffnen – der Kartenausschnitt geht an diesen Server. Auf wenige Meter genau (Karte in WGS84): für eine Vorerkundung genug."],pruefstand:["Prüfstand","Wie viele Bohrungen und Schichten Sie geprüft haben. Eine Korrektur zählt als geprüft. Der Stand wird beim Einchecken festgehalten."],alle_pruefen:["Alle geprüft","Markiert alle Schichten aller Bohrungen im Modell als geprüft – nur wenn Sie alles mit dem Gutachten verglichen haben. Zurücknehmen ist jederzeit möglich."],warnung:["Warnung","Eine Schicht, deren Bodenart nicht erkannt wurde (unklassifiziert). Bodenart wählen, den Vorschlag nach Norm übernehmen oder die Schicht als geprüft markieren."],bodenart:["Bodenart","Klasse für das Modell; Farbe nach DIN 4023 (Kies gelb, Sand orange, Schluff oliv, Ton violett …). Gleiche Bodenarten werden zu Einheiten verbunden."],norm:["Deutung nach Norm","Die Beschreibung aus dem PDF gelesen nach DIN 4023 / DIN EN ISO 14688-1: Hauptanteil, Nebenanteile (schwach ' / stark ¯), Kurzzeichen, Bodengruppe nach DIN 18196 (nur wenn genannt), Konsistenz. Steht auch im IFC (CPset_Bodenansprache)."],vorschlag:["Vorschlag nach Norm","Für eine unklassifizierte Schicht schlägt die Normen-Datenbank eine Bodenart aus der Beschreibung vor. Sie wird nur übernommen, wenn Sie klicken; danach gilt die Schicht als korrigiert."],geprueft:["Geprüft","Haken: Schicht mit dem Gutachten verglichen. Steht im IFC (Geprueft) und im Prüfstand."],tiefe:["Tiefe","Ober- und Unterkante in m unter Geländeoberkante (GOK). Geändertes wird als korrigiert markiert."],gok:["GOK","Ansatzhöhe der Bohrung in m NHN. Aus dem PDF oder hier eingetragen (manuell). Ohne GOK bei allen Bohrungen rechnet das Modell relativ (Gelände = 0 m)."],koordinaten:["Koordinaten","Rechts- und Hochwert der Bohrung; leer lassen, wenn die Lage im Schritt Lage auf dem Plan gesetzt wird."],entfernen:["Entfernen","Die Bohrung kommt nicht ins Modell (sie bleibt in der Liste unter „Entfernt“ und lässt sich wiederherstellen)."],quelle:["Quelle im PDF","Die Seite des Gutachtens, auf der die Bohrung erkannt wurde; der Rahmen zeigt die gewählte Schicht."],lage_art:["Art der Lage","Koordinaten: Bohrungen mit Rechts-/Hochwert (aus dem PDF, eingetragen oder auf dem Lageplan gesetzt). Reihe: ohne Koordinaten nebeneinander mit Abständen bzw. Stationen aus dem Längsschnitt."],unterlage:["Unterlage","Lageplan (Draufsicht) oder Längsschnitt (Seitenansicht) als PDF. Er liegt im Viewer unter den Bohrungen; nach dem Kalibrieren werden die Bohrungen daraufgezogen."],massstab:["Maßstab","Zwei Punkte auf dem Plan anklicken, deren Abstand Sie kennen (Maßstabsleiste, Bemaßung, zwei Bohrungen), und die wahre Länge in m eintragen. Oder den Maßstab 1:n direkt angeben."],bezug:["Bezugspunkt","Ein Punkt im Plan mit bekannter Koordinate (Koordinatenkreuz, Bohrung mit Koordinaten): anklicken und Rechts-/Hochwert eintragen – im Längsschnitt Station und Höhe NHN."],drehung:["Drehung","Winkel, um den der Plan gegen Norden gedreht ist (gegen den Uhrzeigersinn positiv). Nordpfeil nach oben = 0°; Nordpfeil 10° nach links geneigt = 10°."],hoehe:["Höhenmaßstab","Längsschnitte sind oft überhöht (z. B. Länge 1:500, Höhe 1:100). Ohne Angabe gilt der Längenmaßstab."],epsg:["Koordinatensystem (EPSG)","System der Rechts-/Hochwerte aus der Liste wählen: in Deutschland meist ETRS89 / UTM 32N (25832), im Osten 33N (25833), ältere Pläne Gauß-Krüger (Rechtswert 7-stellig, erste Ziffer = Zone); dazu Schweiz und Österreich. Passen die Werte nicht zum System (Ziffernzahl, Zonenkennung), erscheint ein Hinweis. Steht im IFC (IfcMapConversion)."],sperren:["Sperren","Schloss zu: der Plan liegt fest und ändert sich nicht mehr; jetzt die Bohrungen ziehen. Auf dem Lageplan nur in x/y, im Längsschnitt entlang der Station – in der Höhe nur, wenn das PDF keine GOK hat."],deckkraft:["Deckkraft","Wie stark der Plan die Szene überdeckt."],ohne_lage:["Ohne Lage","Bohrungen ohne Koordinaten: anklicken und dann in den gesperrten Plan klicken (Punkte setzen) – oder mit der Maus aus der Liste auf den Plan ziehen."],punkte:["Punkte setzen","Modus an, dann in den gesperrten Lageplan klicken: die gewählte Bohrung bekommt die Lage, danach ist die nächste ohne Lage dran (oder einen Chip anklicken). Mit „freien Punkt“ entsteht ein Punkt ◆, den Sie in der Liste einer Bohrung zuordnen. ✕ löscht einen Punkt bzw. die gesetzte Lage – im Viewer ebenso: Marke anklicken, Entf. Esc beendet den Modus."],reihe:["Reihe","Bohrungen in einer Linie. Abstand zum Vorgänger je Bohrung eintragen (BK1 → BK2 10 m, BK2 → BK3 15 m) oder eine Station; ohne Eintrag gilt der Standardabstand. Reihenfolge mit den Pfeilen."],standardabstand:["Standardabstand","Abstand zwischen Bohrungen, für die nichts eingetragen ist (nur zur Anschauung, im Modell als schematisch markiert)."],boreholeml:["BoreholeML","Austauschformat der Geologischen Dienste der Länder (Version 3.2). Exportiert werden nur vollständig geprüfte Bohrungen mit Lage in ETRS89/UTM und GOK in m NHN; Petrographie, Genese, Konsistenz, Lagerung, Kalk und Feuchte über die amtlichen Codelisten, die Beschreibung aus dem Gutachten im Klartext. Die Organisation steht als Absender in der Datei. Welche Bohrungen ausgelassen wurden und warum, steht oben in der Datei. Umgekehrt lassen sich BoreholeML-Dateien wie ein Gutachten hochladen (Bohrungen der Länder)."],sgd:["Bohrungen der Länder","Bohrungen aus den Datenbanken der Geologischen Dienste um die Mitte des Projekts: Berlin und Brandenburg mit Kopfdaten und dem Schichtenverzeichnis als Grafik, NRW, Baden-Württemberg und Hamburg in BoreholeML mit den freigegebenen Schichtdaten. Abgefragt wird nur auf Klick – die Anfrage sendet die Lage des Projekts an den Dienst. Bohrungen des Gutachtens, die auch beim Land liegen, zeigen die Abweichung von Lage und GOK (Gegenprobe). Übernommene Bohrungen tragen Quelle, Lizenz und Datum, erscheinen als Raute und gehen nicht in den BoreholeML-Export. Für Länder ohne eigenen Dienst zeigen die BGR und Bremen über WMS, wo gebohrt wurde: nur als Hinweis mit Lage, GOK und Teufe, nie im Modell. Länder ohne Datendienst nennt die Abfrage außerdem mit dem Link zu ihrem Portal und der Bohrpunktkarte der BGR („ungeprüft“: Adresse eingetragen, nicht gegen den Dienst getestet). Welches Land: aus den Ländergrenzen (VG2500 des BKG); an einer Grenze beide. Die Adressen pflegt das Werkzeug „Dienste der Länder“ (Menü ⋯)."],gelaende:["Gelände (DGM)","Digitales Geländemodell der Vermessungsverwaltung (Open Data, meist DGM1 mit 1 m Raster) für das Baufeld herunterladen und hier laden: XYZ, ASCII-Raster oder GeoTIFF, mehrere Kacheln auch als ZIP. Die App vergleicht die GOK aus dem PDF mit dem Gelände: liegen alle Bohrungen gleich viel höher oder tiefer, stimmen Lage, EPSG oder Höhenbezug nicht. Fehlende GOK schlägt sie vor – übernommen wird nur auf Klick, markiert als „DGM“ (auch im IFC)."],dgm_land:["DGM vom Land","Holt das DGM1 (1 m) für den Ausschnitt um die Bohrungen plus Rand direkt beim Dienst des Landes (WCS): bisher Brandenburg mit Berlin und NRW. Nur auf Klick – die Anfrage sendet den Ausschnitt an den Dienst. Quelle, Lizenz und Namensnennung bleiben am DGM und gehen ins IFC. Baden-Württemberg liefert über seinen Dienst nur ganze Meter, Bayern hat keinen freien Dienst: dort die DGM1-Kacheln als Datei laden."],gebaeude:["Gebäude (LoD2)","3D-Gebäudemodelle LoD2 der Länder als Umgebung des Baugrundmodells: Berlin, Brandenburg und NRW geben sie als CityGML-Kacheln von 1 × 1 km heraus, in ETRS89/UTM mit Höhen in m NHN – derselbe Rahmen wie das Modell. Nur auf Klick werden die Kacheln um die Bohrungen (plus Rand) geladen; Gebäude, deren Grundriss den Ausschnitt berührt, kommen ins IFC (IfcBuildingElementProxy mit Wänden und Dach, Quelle und Lizenz je Gebäude) und in den Viewer (Knopf „Gebäude“). Bestand, nicht erkundet."],standort:["Standort ohne Gutachten","Ein Projekt an einem Punkt (ETRS89/UTM, aus der Karte oder eingetragen): im Schritt Lage fragt es die Bohrungen der Länder um den Punkt ab, holt das DGM und die Gebäude – ein Lageplan ist nicht nötig, der Punkt ist schon georeferenziert. Übernommene Bohrungen mit Schichtdaten (NRW, Baden-Württemberg) ergeben ein Modell – eine Vorerkundung: Archivdaten unbekannter Güte, ohne Sondierungen, oft alt oder weit weg. Kommt später das Gutachten, entsteht ein neues Projekt, das die Bohrungen der Länder, DGM und Gebäude mitnimmt (gemischt)."],reifegrad:["Reifegrad","Woraus das Modell besteht: Gutachten (nur Bohrungen aus dem PDF), Vorerkundung (nur Bohrungen aus Datenbanken der Länder oder BoreholeML-Dateien) oder gemischt. Er steht in der App, im Viewer, im Prüfbericht und im IFC (CPset_Baugrundmodell.Reifegrad); jede Bohrung trägt ihre Herkunft mit Quelle und Lizenz (CPset_Herkunft)."],homogenbereiche:["Homogenbereiche (VOB/C)","Ein Homogenbereich fasst Boden zusammen, der sich für ein Gewerk gleich verhält; die ATV der VOB/C (z. B. DIN 18300 Erdarbeiten) verlangen je Bereich bestimmte Kennwerte. Dieselbe Einheit kann für verschiedene Gewerke in verschiedenen Bereichen liegen: Gewerk wählen, je Einheit einen Bereich eintragen (gleicher Name = gleicher Bereich, leer = keiner). Die Liste zeigt die Kennwerte, die die ATV verlangt (Matrix nach Abbildung 8, Quelle in docs/28; gegen die geltende ATV prüfen). Im IFC trägt jede Einheit und jede Bodenschicht ein Pset CPset_Homogenbereich_<ATV>; liegt eine Schicht an einer Bohrung in zwei Einheiten, nennt es beide Bereiche. „IFC-Modell: Homogenbereiche“ schreibt das Modell aus den Bereichen (dieselben Körper, je Bereich ein Stratum); Einheiten ohne Bereich bleiben einzeln und markiert. Ohne Zuordnung zeigt der Abschnitt einen Vorschlag für die gewählte ATV: Einheiten, die sich für dieses Gewerk gleich verhalten, in einem Bereich, mit Begründung je Bereich. Wie fein er trennt, folgt aus den Kennwerten der ATV: wenige (z. B. DIN 18300 GK 1, DIN 18320) – nur nichtbindig, bindig, organisch, anthropogen, befestigt (Beton, Asphalt, Pflaster), Fels; sonst dazu die Bodengruppe DIN 18196, wenn mindestens die Hälfte der Schichten sie nennt (sonst die Hauptbodenart); verlangt die ATV Mineralogie oder Abrasivität (z. B. DIN 18312, 18319, 18324) – dazu Steine/Blöcke getrennt. Nicht klassifizierte Einheiten bleiben einzeln. Übernommen wird der Vorschlag erst mit einem Klick und ist danach je Einheit änderbar; zuordnen entscheidet der Planer."],hb_kennwerte:["Kennwerte aus den Beschreibungen","Je Homogenbereich (ohne Zuordnung: je Einheit) steht hier, was die Schichtbeschreibungen der Bohrprofile zu den verlangten Kennwerten sagen: ortsübliche Bezeichnung (Benennung), Konsistenz, Lagerungsdichte, Kalkgehalt, Bodengruppe DIN 18196, Plastizität (aus der Bodengruppe), genannte Steine, Blöcke und organische Anteile – jeweils mit dem Anteil der Schichten, die es nennen (z. B. „steif (5/8)“). Das ist Ansprache, kein Laborwert: Korngrößenverteilung, Massenanteile, Dichte, undrainierte Scherfestigkeit, Wassergehalt, Plastizitäts- und Konsistenzzahl, Durchlässigkeit, Abrasivität stehen nur im Text oder in den Anlagen des Gutachtens und bleiben „offen“. Im IFC stehen die Angaben als Kennwert_… und die offenen als Kennwerte_offen im Pset des Bereichs."],grundwasser:["Grundwasserfläche","Eine Fläche durch die gemessenen Wasserstände der Bohrungen (GOK − Tiefe), mit derselben Interpolation wie das Modell; sie geht nicht ins IFC und ändert das Modell nicht. Trockene Bohrungen („kein Grundwasser“) sind Daten: liegt die Fläche dort über der Endteufe, steht der Widerspruch dabei. Gemeldet werden auch eine Fläche über dem Gelände (gespanntes Wasser oder Stände verschiedener Tage) und mehrere Stände in einer Bohrung (der höchste gilt). Ab vier Ständen zeigt eine Kreuzprobe, wie gut sich der Wasserstand zwischen den Bohrungen vorhersagen lässt. Bohrzeit-Wasserstände sind Momentaufnahmen: kein Bemessungswasserstand."],orientierung:["Orientierung je Einheit","Nur für die implizite Methode (GemPy). Ohne Eingabe folgt die Orientierung einer Unterkante aus ihren Kontakten: Ebene durch die Bohrungen, entlang einer Trasse in Linienrichtung, steiler als 30° oder mit weniger als drei Kontakten horizontal. Ist das Einfallen bekannt (Gutachten, geologische Karte, Aufschluss), hier Fallrichtung (Azimut von Nord im Uhrzeigersinn, 0–360°) und Fallwinkel (0–80°) eingeben; dann gilt die Eingabe, auch in der Kreuzprobe, und Bericht und IFC nennen sie als Quelle „Eingabe“. An den Bohrungen bleibt jede Grenze exakt; passt die Eingabe nicht zu den Kontakten (mehr als 5 cm daneben), gilt für diese Fläche der Spline mit Hinweis. Leere Felder = aus den Kontakten."],gelaende_dgm:["Gelände aus dem DGM","Mit DGM folgt die Oberkante des Modells dem Gelände statt der Interpolation zwischen den GOK. An jeder Bohrung bleibt sie genau auf der GOK; deren Abweichung vom DGM klingt bis zur Reichweite (halber Bohrabstand, höchstens 25 m) ab. Im IFC liegt das Gelände um das Modell als IfcGeographicElement (TERRAIN), im Viewer mit dem Knopf „Gelände“ ein- und ausblendbar. Deckt das DGM das Modellgebiet nicht ganz ab, bleibt die Oberkante aus den GOK (mit Hinweis)."],dgm_epsg:["System der DGM-Datei","XYZ- und ASCII-Dateien enthalten kein Koordinatensystem: das System der Kacheln wählen (meist dasselbe wie das Projekt, z. B. 25832). Ein GeoTIFF bringt es selbst mit."],durchmesser:["Durchmesser","Dicke der Bohrsäulen im Viewer und im IFC (Darstellung, nicht der Bohrdurchmesser im Feld). Automatisch wächst er mit der Modellgröße, damit Säulen auf langen Trassen sichtbar bleiben."],einheiten:["Einheiten","Modelleinheiten verbinden gleiche Bodenarten zwischen den Bohrungen (Sand 1, Kies, Sand 2). Umbenennen oder Bodenarten zusammenlegen (z. B. „Sand, Kies“ als eine Einheit); Reihenfolge von oben nach unten."],analyse:["Ground Analysis","Wie weit trägt das Modell zwischen den Bohrungen? Die Kreuzprobe rechnet das Modell ohne je eine Bohrung und vergleicht seine Vorhersage mit ihr (mittlerer Fehler der Schichtgrenzen, für IDW und Spline). Die Unsicherheit verbindet die Messung der Grenzen (± 0,10 m, Monte Carlo) mit diesem Fehler über den Abstand zur nächsten Bohrung. Liest nur das Modell, ändert nichts. Mindestens 3 Bohrungen."],erkundung:["Erkundungsvorschlag","Punkte, an denen eine weitere Bohrung das Modell am meisten verbessert: wo die Unterkanten am stärksten streuen und wo unklar ist, wie weit eine Einheit reicht (Linse, Rinne). Am Beispiel einer Rinne zwischen den Bohrungen senkten zwei Bohrungen an den vorgeschlagenen Stellen den Fehler stärker als zwei zufällige; eine andere Interpolation half dort nicht (docs/27). Ein Vorschlag, keine Planung."],virtuell:["Virtuelle Bohrung","Was das Modell an einem Punkt erwartet: Einheiten mit Tiefen und der Streuung jeder Unterkante (± σ, 95 % etwa ± 2 σ). Eine Vorhersage aus den Nachbarbohrungen, keine Messung."],methode:["Interpolation","IDW: gewichtetes Mittel der Nachbarbohrungen, ruhig und sicher. Dünnplatten-Spline: glatte Flächen mit Trend, gut bei geneigten Schichten. Implizit (GemPy, wenn installiert): je Fläche ein Skalarfeld in 3D mit einer Orientierung aus den Kontakten (Ebene, sonst horizontal; steht im Bericht); langsamer, exakt an den Bohrungen; eine gefaltete Fläche rechnet der Spline (mit Hinweis). Welche Methode die Bohrungen am besten vorhersagt, zeigt die Ground Analysis."],puffer:["Puffer","Wie weit das Modell über die Bohrungen hinausreicht. Automatisch: halber Bohrabstand (5–100 m)."],raster:["Raster","Maschenweite der Schichtflächen. Automatisch: Gebietsgröße/40, bei großen Modellen gröber (höchstens 30 000 Knoten)."],basis:["Modellbasis","Unterkante des Modells in m NHN. Automatisch: tiefste Endteufe."],gok_relativ:["Fehlende GOK","Hat keine Bohrung eine GOK, rechnet das Modell relativ (Gelände = 0 m) – markiert im IFC."],auto:["Automatisch nachführen","Jede Änderung (Tabelle, Lage, Einheiten) rechnet das Modell sofort neu."],einchecken:["Einchecken","Hält den Prüfstand fest (Zeit, Zähler, Fingerabdruck des Modells, Kommentar). Das exportierte IFC trägt ihn (CPset_Baugrundmodell.Pruefstand)."],tiles3d:["3D Tiles für Cesium","Das Baugrundmodell als 3D Tiles 1.1 (tileset.json und glTF) für CesiumJS, Cesium for Unreal oder QGIS 3D: Baugrundmodell, Gelände und Gebäude je eine Kachel. Jeder Punkt wird exakt aus ETRS89/UTM umgerechnet, die Höhen ellipsoidisch mit dem Quasigeoid GCG2016 des BKG (CC BY 4.0; beim ersten Export einmal 1 MB geladen). ETRS89 ist nicht in WGS84/ITRF überführt (rund 0,9 m). Quellen und Lizenzen stehen in LIESMICH.txt."],geoldg:["Geologiedatengesetz (GeolDG)","Wer bohrt oder bohren lässt, muss die Untersuchung beim Geologischen Dienst des Landes anzeigen und die Daten übermitteln: Anzeige spätestens zwei Wochen vor Beginn (§ 8), Fachdaten wie das Schichtenverzeichnis spätestens drei Monate nach Abschluss (§ 9), Bewertungsdaten wie Gutachten und räumliche Modelle mit Dokumentation auf Verlangen (§ 10). Die Liste zeigt je Bohrung, was GroundTwin liefert (Lage, GOK, Endteufe, geprüfte Schichten) und was aus dem Bohrprotokoll kommt (Bohrverfahren, Ausbau, Proben, Messungen, Labor). Das Paket enthält BoreholeML, IFC, Prüfbericht, Modelldokumentation und eine Prüfliste zum Ergänzen. Hilfe, keine Rechtsberatung: Form und Weg legt die zuständige Behörde fest."],geoldg_abschluss:["Abschluss der Untersuchung","Die Untersuchung gilt mit Ablauf der Dauer als abgeschlossen, die in der Anzeige angegeben wurde – außer eine Fortdauer wurde rechtzeitig angezeigt (§ 15 Abs. 1). Ab dann laufen drei Monate für die Fachdaten; ist eine Behörde verpflichtet, etwa als Auftraggeber, sechs Monate für die Bewertungsdaten (§ 10 Abs. 2 Satz 2). Die Daten bleiben im Projekt."],export:["Export","IFC 4.3 mit Prüfstand, Bodenansprache je Schicht und Beschreibungen je Einheit; dazu Prüfbericht und die Daten als JSON."],ueberhoehung:["Überhöhung","Höhen im Viewer mal Faktor, damit dünne Schichten sichtbar werden. Die Koordinaten bleiben echt."]};let N=null,Ke=null;function fe(){N?.remove(),N=null,Ke=null}function Zn(e,n){e.preventDefault(),e.stopPropagation();const t=e.currentTarget;if(Ke===t){fe();return}fe();const[i,s]=Pe[n];N=document.createElement("div"),N.className="hilfe-blase",N.setAttribute("role","tooltip"),N.innerHTML="<strong></strong><p></p>",N.querySelector("strong").textContent=i,N.querySelector("p").textContent=s,document.body.append(N);const r=t.getBoundingClientRect(),o=N.getBoundingClientRect(),h=Math.min(Math.max(8,r.left+r.width/2-o.width/2),window.innerWidth-o.width-8),d=r.bottom+8+o.height>window.innerHeight?r.top-o.height-8:r.bottom+8;Object.assign(N.style,{left:`${h}px`,top:`${d}px`}),Ke=t}document.addEventListener("click",e=>{N&&!N.contains(e.target)&&fe()});document.addEventListener("keydown",e=>{e.key==="Escape"&&fe()});const m=e=>a`<button type="button" class="hilfe" title=${Pe[e][0]} aria-label=${`Hilfe: ${Pe[e][0]}`}
    @click=${n=>Zn(n,e)}>?</button>`,qn="https://sgx.geodatenzentrum.de/wmts_basemapde/tile/1.0.0/de_basemapde_web_raster_farbe/default/GLOBAL_WEBMERCATOR/{z}/{y}/{x}.png",Jn="https://tile.openstreetmap.org/{z}/{x}/{y}.png",Je=[51.16,10.45];let ee=null;const de=e=>e.replace(/[&<>"]/g,n=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[n]),Qe=e=>e.toLocaleString("de-DE",{minimumFractionDigits:1,maximumFractionDigits:1});async function Qn(){const[{default:e}]=await Promise.all([Ae(()=>import("./leaflet-src-7ah4FPQk.js").then(n=>n.l),[],import.meta.url),Ae(()=>Promise.resolve({}),__vite__mapDeps([0]),import.meta.url)]);return new Promise(n=>{const t=document.createElement("dialog");t.className="karte-dialog",t.setAttribute("aria-label","Standort auf der Karte wählen"),t.innerHTML=`
      <header><strong>Standort auf der Karte wählen</strong>
        <button type="button" class="symbol schliessen" aria-label="Karte schließen">✕</button></header>
      <div class="karte-flaeche"></div>
      <footer>
        <div class="karte-info klein" aria-live="polite">In die Karte klicken: der Punkt wird der Standort (zum Orientieren,
          auf wenige Meter genau). Mausrad zoomt, Ziehen verschiebt.</div>
        <div class="zeile"><span class="fueller"></span>
          <button type="button" class="abbrechen">Abbrechen</button>
          <button type="button" class="primaer uebernehmen" disabled>Punkt übernehmen</button></div>
      </footer>`,document.body.append(t),t.showModal();const i=t.querySelector(".karte-info"),s=t.querySelector(".uebernehmen"),r=e.map(t.querySelector(".karte-flaeche"),{zoomControl:!0,attributionControl:!0}).setView(ee?[ee.breite,ee.laenge]:Je,ee?.zoom??6),o=new Date().getFullYear(),h=e.tileLayer(qn,{maxZoom:18,attribution:`© <a href="https://basemap.de" target="_blank" rel="noopener">GeoBasis-DE / BKG (${o})</a> <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>`}).addTo(r),d=e.tileLayer(Jn,{maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap-Mitwirkende</a>'});e.control.layers({"basemap.de (BKG)":h,OpenStreetMap:d},{},{position:"topright"}).addTo(r),e.control.scale({imperial:!1}).addTo(r);const c=e.circleMarker(Je,{radius:8,color:"#10210a",weight:2,fillColor:"#a2c513",fillOpacity:.95});let v=null,g=0;r.on("click",async S=>{const f=++g;c.setLatLng(S.latlng).addTo(r),v=null,s.disabled=!0,i.textContent="wird umgerechnet …";try{const A=await $.standortPunkt(Number(S.latlng.lng.toFixed(7)),Number(S.latlng.lat.toFixed(7)));if(f!==g)return;v=A,s.disabled=!1,i.innerHTML=`<b>Rechtswert ${Qe(A.x)} · Hochwert ${Qe(A.y)} · EPSG:${A.epsg}</b>
          <ul class="dienste">${A.dienste.map(K=>`<li class="${K.art}">${/^https?:\/\//.test(K.url??"")?`<a href="${de(K.url)}" target="_blank" rel="noopener noreferrer">${de(K.text)}</a>`:de(K.text)}${K.status==="ungeprueft"?' <span class="ungeprueft">ungeprüft</span>':""}</li>`).join("")}</ul>
          <span class="leise">Das Land aus den Ländergrenzen (VG2500 des BKG, auf rund 150 m); Portale als Link.</span>`}catch(A){if(f!==g)return;i.innerHTML=`<span class="warnung">${de(A.message)}</span>`}});const k=S=>{const f=r.getCenter();ee=S?{laenge:S.laenge,breite:S.breite,zoom:Math.max(r.getZoom(),14)}:{laenge:f.lng,breite:f.lat,zoom:r.getZoom()},r.remove(),t.close(),t.remove(),n(S)};t.querySelector(".schliessen").addEventListener("click",()=>k(null)),t.querySelector(".abbrechen").addEventListener("click",()=>k(null)),s.addEventListener("click",()=>k(v)),t.addEventListener("cancel",S=>{S.preventDefault(),k(null)}),requestAnimationFrame(()=>r.invalidateSize())})}let T=[],Te=!0,ge=!1;const G={x:"",y:"",epsg:25832,name:""};let Y=null;const Yn=[[25832,"ETRS89 / UTM 32N"],[25833,"ETRS89 / UTM 33N"],[4647,"ETRS89 / UTM 32N (zE-N)"],[5650,"ETRS89 / UTM 33N (zE-N)"]];async function Sn(e){for(;;){const n=await w(()=>$.auftrag(e));if(!n)return;if(l.auftrag=n,p(),n.fertig){l.auftrag=null;for(const t of n.fehler)L(t,"fehler",1e4);n.projekt?(T=[],await X(n.projekt,"bohrungen")):p();return}await new Promise(t=>setTimeout(t,600))}}const Gn=()=>l.z?.standort?l.sig:"";async function Xn(){if(!T.length)return;const e=await w(()=>$.gutachten(T,Te&&!!l.info?.ocr,Gn()));e&&await Sn(e.id)}async function et(){const e=Number(G.x.replace(",",".")),n=Number(G.y.replace(",","."));if(!Number.isFinite(e)||!Number.isFinite(n)||!G.x||!G.y){L("Rechtswert und Hochwert als Zahlen eingeben.","warn");return}const t=await w(()=>$.standort(e,n,G.epsg,G.name),"Standort wird angelegt …");t&&(await X(t.projekt,t.vorhanden?void 0:"lage"),t.vorhanden&&L(`Den Standort gibt es schon: „${l.z?.name}“ geöffnet.`))}async function nt(){let e=null;try{e=await Qn()}catch(n){L(`Karte: ${n.message}`,"fehler",8e3)}e&&(G.x=String(e.x),G.y=String(e.y),G.epsg=e.epsg,Y=e.dienste,p())}function tt(){const e=(t,i,s)=>a`
    <label class="feld"><span>${i}</span><input type="text" inputmode=${t==="name"?"text":"decimal"}
      aria-label=${i} placeholder=${s} .value=${G[t]} @input=${r=>{G[t]=r.target.value,t!=="name"&&Y&&(Y=null),p()}}></label>`,n=!!(G.x.trim()&&G.y.trim());return a`
    <section class="weg" aria-labelledby="weg-standort">
      <div class="weg-symbol" aria-hidden="true">◎</div>
      <h2 id="weg-standort">Standort</h2>
      <p class="weg-text">Noch kein Gutachten? Ein Punkt auf der Karte genügt: Bohrungen der Länder rund um den Punkt –
        eine <b>Vorerkundung</b>, kein Ersatz für das Gutachten. ${m("standort")}</p>
      <button class=${n?"":"primaer gross-knopf"} @click=${nt}>🗺 Auf der Karte wählen</button>
      ${n?a`<div class="punkt-wahl">
        <p class="klein"><b>${G.x} / ${G.y}</b> · EPSG:${G.epsg}</p>
        ${Y?yn(Y):u}
        ${e("name","Name (frei)","z. B. Marl Nord")}
        <button class="primaer gross-knopf" @click=${et}>Projekt am Standort anlegen →</button>
      </div>`:u}
      <details class="still">
        <summary>Koordinaten eingeben</summary>
        <div class="raster-2">
          ${e("x","Rechtswert","z. B. 368130")}
          ${e("y","Hochwert","z. B. 5724400")}
          <label class="feld"><span>System</span>
            <select aria-label="System des Standorts" @change=${t=>{G.epsg=Number(t.target.value),Y=null,p()}}>
              ${Yn.map(([t,i])=>a`<option value=${t} ?selected=${G.epsg===t}>${t} · ${i}</option>`)}
            </select></label>
        </div>
        <p class="leise klein">ETRS89/UTM, nur Deutschland. ${m("karte")}</p>
      </details>
    </section>`}async function Ye(e){const n=await w(()=>$.beispiel(e),"Beispiel wird geöffnet …");n?.projekt?await X(n.projekt,n.schritt??"bohrungen"):n?.auftrag&&await Sn(n.auftrag)}function Xe(e){T=[...e??[]].filter(n=>/\.(pdf|json|xml)$/i.test(n.name)),e?.length&&!T.length&&L("Bitte PDF-Dateien wählen (oder eine Extraktion als JSON, Bohrungen als BoreholeML).","warn"),p()}async function it(e,n){confirm(`Projekt „${n}“ mit allen Korrekturen löschen? Das Gutachten selbst bleibt unberührt.`)&&(await w(()=>$.loeschen(e)),await zn())}function at(){const e=l.auftrag,n=!!l.info?.ocr;return a`
    <section class="weg" aria-labelledby="weg-gutachten">
      <div class="weg-symbol" aria-hidden="true">⇪</div>
      <h2 id="weg-gutachten">Gutachten</h2>
      <p class="weg-text">Das Bodengutachten als PDF – Vektor oder Scan. Die Bohrungen werden erkannt; Sie prüfen sie,
        sehen sie in 3D und vergleichen sie mit den Bohrungen der Länder.</p>
      ${Gn()?a`<p class="hinweis-standort">Zum Standort <b>${l.z.name}</b>: Bohrungen der Länder (mit Prüfstand),
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
        <label class=${`ablage ${ge?"ueber":""} ${T.length?"bereit":""}`}
          @dragover=${t=>{t.preventDefault(),ge=!0,p()}}
          @dragleave=${()=>{ge=!1,p()}}
          @drop=${t=>{t.preventDefault(),ge=!1,Xe(t.dataTransfer?.files)}}>
          <input type="file" accept=".pdf,application/pdf,.json,application/json,.xml,application/xml,text/xml" multiple @change=${t=>Xe(t.target.files)}>
          <strong>${T.length?T.map(t=>t.name).join(", "):"PDF hierher ziehen oder klicken"}</strong>
          <span class="leise klein">${T.length?`${T.length} Datei(en) bereit`:"mehrere Dateien möglich (z. B. Anlagen 2–4)"}</span>
        </label>
        <button class="primaer gross-knopf" ?disabled=${!T.length} @click=${Xn}>Auswerten →</button>
        <details class="still">
          <summary>Optionen</summary>
          <div class="zeile">
            <label class="schalter" title=${n?"":"nicht installiert: pip install -r requirements-ocr.txt"}>
              <input type="checkbox" .checked=${Te&&n} ?disabled=${!n} @change=${t=>{Te=t.target.checked}}>
              OCR für Scans ${n?"":"(nicht installiert)"}
            </label>${m("ocr")}
          </div>
          <p class="leise klein">Auch eine Extraktion als JSON oder Bohrungen als BoreholeML (XML) lassen sich laden.</p>
        </details>`}
    </section>`}const en=5;function nn(e){return e.map(n=>a`
    <tr>
      <td><button class="link" @click=${()=>X(n.signatur)}>${n.name}</button>${n.standort?a` <span class="abzeichen vorerkundung" title="Standort ohne Gutachten">Standort</span>`:u}
        <div class="leise klein">${n.dokumente.join(", ")}</div></td>
      <td class="zahl" title=${n.fremd?`davon ${n.fremd} aus den Datenbanken der Länder`:""}>${n.bohrungen}</td>
      <td class="zahl">${n.geprueft}${n.eincheckungen?a` · <span title="eingecheckt">✓${n.eincheckungen}</span>`:u}</td>
      <td class="leise klein">${n.geaendert}</td>
      <td><button class="symbol" title="Projekt löschen" aria-label="Projekt löschen" @click=${()=>it(n.signatur,n.name)}>🗑</button></td>
    </tr>`)}function rt(){if(!l.projekte.length)return u;const e=a`<thead><tr><th>Projekt</th><th>Bohrungen</th><th>geprüft</th><th>geändert</th><th></th></tr></thead>`,n=l.projekte.slice(en);return a`
    <section class="zuletzt">
      <h3>Zuletzt bearbeitet</h3>
      <table class="tabelle kompakt">${e}<tbody>${nn(l.projekte.slice(0,en))}</tbody></table>
      ${n.length?a`<details class="still"><summary>Alle ${l.projekte.length} Projekte</summary>
        <table class="tabelle kompakt">${e}<tbody>${nn(n)}</tbody></table></details>`:u}
    </section>`}function lt(){const e=l.auftrag,n=l.info?.beispiele??[];return a`
    <details class="still beispiele">
      <summary>Beispiele ausprobieren</summary>
      <div class="zwei-spalten">
        <div>
          <h4 class="klein">Gutachten ${m("beispiele")}</h4>
          <ul class="auswahl-liste">
            ${n.filter(t=>!t.standort).map(t=>a`
              <li><button class="link" ?disabled=${!!e} @click=${()=>Ye(t.name)}>${t.titel}</button></li>`)}
          </ul>
        </div>
        <div>
          <h4 class="klein">Standort <span class="leise">(Bohrungen der Länder: Abfrage im Schritt Lage, mit Netz)</span></h4>
          <ul class="auswahl-liste">
            ${n.filter(t=>t.standort).map(t=>a`
              <li><button class="link" ?disabled=${!!e} @click=${()=>Ye(t.name)}>${t.titel}</button></li>`)}
          </ul>
        </div>
      </div>
    </details>`}function st(){return a`
    <div class="seite-mitte start">
      <header class="start-titel">
        <h1>Baugrund verstehen.</h1>
        <p>Bohrungen aus dem Gutachten oder vom Standort – geprüft, in 3D, im Vergleich mit den Bohrungen der Länder.</p>
      </header>
      <div class="wege">
        ${at()}
        ${tt()}
      </div>
      ${rt()}
      ${lt()}
      ${l.info?a`<p class="leise klein impressum">GroundTwin ${l.info.version} ·
        <a href="dienste.html" target="_blank" rel="noopener">Dienste der Länder</a> ·
        <a href="viewer.html" target="_blank" rel="noopener">Viewer allein</a> · freie Software unter
        <a href=${`${l.info.quellcode}/blob/main/LICENSE`} target="_blank" rel="noopener">${l.info.lizenz}</a> ·
        <a href=${l.info.quellcode} target="_blank" rel="noopener">Quellcode</a><br>Die App extrahiert und schlägt vor;
        die Interpretation und Freigabe bleibt beim Geotechniker.</p>`:u}
    </div>`}const me="Deutschland · ETRS89 / UTM (amtlich)",q="Deutschland · Gauß-Krüger (alt)",$e=[{code:25832,name:"ETRS89 / UTM Zone 32N",gruppe:me,e:[22e4,101e4],n:[503e4,614e4],hinweis:"Rechtswert 6-stellig, die meisten Länder"},{code:25833,name:"ETRS89 / UTM Zone 33N",gruppe:me,e:[15e4,7e5],n:[509e4,613e4],hinweis:"Rechtswert 6-stellig, Osten (Berlin, Brandenburg, Sachsen, MV)"},{code:4647,name:"ETRS89 / UTM 32N mit Zone (32…)",gruppe:me,e:[3223e4,33e6],n:[52e5,614e4],hinweis:"Rechtswert 8-stellig, beginnt mit 32"},{code:5650,name:"ETRS89 / UTM 33N mit Zone (33…)",gruppe:me,e:[3315e4,3354e4],n:[52e5,613e4],hinweis:"Rechtswert 8-stellig, beginnt mit 33"},{code:31466,name:"DHDN / Gauß-Krüger Zone 2",gruppe:q,e:[23e5,27e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 2"},{code:31467,name:"DHDN / Gauß-Krüger Zone 3",gruppe:q,e:[33e5,37e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 3"},{code:31468,name:"DHDN / Gauß-Krüger Zone 4",gruppe:q,e:[43e5,47e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 4"},{code:31469,name:"DHDN / Gauß-Krüger Zone 5",gruppe:q,e:[531e4,57e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 5"},{code:2398,name:"Krassowski (42/83) / Gauß-Krüger Zone 4",gruppe:q,e:[43e5,47e5],n:[52e5,613e4],hinweis:"neue Länder vor ETRS89, Rechtswert beginnt mit 4"},{code:2399,name:"Krassowski (42/83) / Gauß-Krüger Zone 5",gruppe:q,e:[53e5,57e5],n:[52e5,613e4],hinweis:"neue Länder vor ETRS89, Rechtswert beginnt mit 5"},{code:3068,name:"DHDN / Soldner Berlin",gruppe:"Deutschland · andere",e:[-4e4,9e4],n:[-4e4,8e4],hinweis:"Berlin, alte Katasterkoordinaten (5-stellig)"},{code:2056,name:"CH1903+ / LV95",gruppe:"Schweiz",e:[245e4,287e4],n:[103e4,134e4],hinweis:"E 2 xxx xxx, N 1 xxx xxx"},{code:21781,name:"CH1903 / LV03",gruppe:"Schweiz",e:[45e4,87e4],n:[3e4,34e4],hinweis:"Y 6-stellig, X 5–6-stellig (alt)"},{code:31254,name:"MGI / Austria GK West",gruppe:"Österreich",e:[-11e4,17e4],n:[11e4,34e4],hinweis:"Rechtswert um 0 (±), Hochwert ohne 5 000 000"},{code:31255,name:"MGI / Austria GK Central",gruppe:"Österreich",e:[-16e4,17e4],n:[9e4,46e4],hinweis:"Rechtswert um 0 (±), Hochwert ohne 5 000 000"},{code:31256,name:"MGI / Austria GK East",gruppe:"Österreich",e:[-16e4,1e5],n:[1e5,48e4],hinweis:"Rechtswert um 0 (±), Hochwert ohne 5 000 000"},{code:31257,name:"MGI / Austria GK M28 (BMN)",gruppe:"Österreich",e:[4e4,32e4],n:[11e4,34e4],hinweis:"Bundesmeldenetz West"},{code:31258,name:"MGI / Austria GK M31 (BMN)",gruppe:"Österreich",e:[29e4,62e4],n:[9e4,46e4],hinweis:"Bundesmeldenetz Mitte"},{code:31259,name:"MGI / Austria GK M34 (BMN)",gruppe:"Österreich",e:[59e4,85e4],n:[1e5,48e4],hinweis:"Bundesmeldenetz Ost"},{code:32632,name:"WGS 84 / UTM Zone 32N",gruppe:"GPS (WGS 84)",e:[22e4,101e4],n:[503e4,614e4],hinweis:"wie ETRS89 / UTM 32N (Abweichung < 1 m)"},{code:32633,name:"WGS 84 / UTM Zone 33N",gruppe:"GPS (WGS 84)",e:[15e4,7e5],n:[509e4,613e4],hinweis:"wie ETRS89 / UTM 33N (Abweichung < 1 m)"}],ot=new Map($e.map(e=>[e.code,e]));function Ue(e){return e?ot.get(e)??null:null}function Ve(e){if(!e)return"ohne System (lokal)";const n=Ue(e);return n?`EPSG ${e} · ${n.name}`:`EPSG ${e} (nicht in der Liste)`}const Dn=(e,n,t)=>n>=e.e[0]&&n<=e.e[1]&&t>=e.n[0]&&t<=e.n[1];function ut(e,n){return e===null||n===null||!Number.isFinite(e)||!Number.isFinite(n)?[]:$e.filter(t=>t.gruppe!=="GPS (WGS 84)"&&Dn(t,e,n))}function Mn(e,n,t){if(n===null||t===null||!Number.isFinite(n)||!Number.isFinite(t))return null;const i=ut(n,t),s=i.slice(0,3).map(o=>`${o.code} (${o.name})`).join(", ");if(!e)return i.length?{ok:!1,text:`Kein System gewählt – die Werte passen zu ${s}.`}:null;const r=Ue(e);return r?Dn(r,n,t)?{ok:!0,text:`passt zu EPSG ${e} (${r.hinweis})`}:{ok:!1,text:i.length?`Rechts-/Hochwert passen nicht zu EPSG ${e} (${r.hinweis}), aber zu ${s}.`:"Rechts-/Hochwert passen zu keinem System der Liste – Ziffern prüfen (z. B. fehlende Zonenkennung)."}:{ok:!1,text:`EPSG ${e} ist nicht in der Liste – bitte prüfen.`}}function We(e,n,t="Koordinatensystem"){const i=[...new Set($e.map(r=>r.gruppe))],s=e!==null&&!Ue(e);return a`
    <select class="epsg" aria-label=${t} title=${Ve(e)}
      @change=${r=>{const o=r.target.value;n(o===""?null:Number(o))}}>
      <option value="" .selected=${e===null}>– ohne (lokal) –</option>
      ${s?a`<option value=${String(e)} .selected=${!0}>EPSG ${e} – nicht in der Liste ⚠</option>`:u}
      ${i.map(r=>a`
        <optgroup label=${r}>
          ${$e.filter(o=>o.gruppe===r).map(o=>a`
            <option value=${String(o.code)} .selected=${o.code===e}>${o.code} · ${o.name}</option>`)}
        </optgroup>`)}
    </select>`}const se=(e,n=2)=>e.toLocaleString("de-DE",{minimumFractionDigits:n,maximumFractionDigits:n});function _n(e){for(const n of[.5,1,2,5,10,20,50,100])if(e/n<=12)return n;return 200}function ct(e,n){const t=Math.max(1,...e.map(c=>c.bis)),i=12,s=(n.hoehe-i-14)/t,r=34,o=46,h=_n(t),d=[];for(let c=0;c<=t+1e-9;c+=h)d.push(c);return a`<svg class="saeule" viewBox="0 0 150 ${n.hoehe}" width="150" height=${n.hoehe} role="img" aria-label="Bohrsäule">
    <defs>
      <pattern id="schraffur-warn" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
        <rect width="6" height="6" fill="#e6e6e6"></rect><line x1="0" y1="0" x2="0" y2="6" stroke="#f0a33a" stroke-width="3"></line>
      </pattern>
    </defs>
    ${d.map(c=>Z`
      <line x1=${r-5} x2=${r} y1=${i+c*s} y2=${i+c*s} class="achse"></line>
      <text x=${r-7} y=${i+c*s+3} class="achse-text" text-anchor="end">${se(c,h<1?1:0)}</text>`)}
    <line x1=${r} x2=${r} y1=${i} y2=${i+t*s} class="achse"></line>
    ${e.map(c=>Z`
      <g class=${`schicht ${c.k===n.gewaehlt?"gewaehlt":""} ${c.warn?"warn":""}`} @click=${()=>n.waehlen?.(c.k)}>
        <title>${c.titel}</title>
        <rect x=${r+4} y=${i+c.von*s} width=${o} height=${Math.max(1,(c.bis-c.von)*s)}
          fill=${c.warn?"url(#schraffur-warn)":c.farbe}></rect>
        ${c.geprueft?Z`<text x=${r+o+9} y=${i+(c.von+c.bis)/2*s+4} class="haken">✓</text>`:u}
        ${(c.bis-c.von)*s>11?Z`<text x=${r+o+22} y=${i+c.bis*s-2} class="tiefe">${se(c.bis)}</text>`:u}
      </g>`)}
  </svg>`}function ht(e,n){const t=[...e.bohrungen].sort((f,A)=>f.x-A.x||f.y-A.y);if(!t.length)return u;const i=new Map(e.einheiten.map(f=>[f.name,f.farbe])),s=Math.max(...t.map(f=>f.gok)),r=Math.min(...t.map(f=>f.endteufe_nhn)),o=22,h=44,d=Math.max(38,Math.min(70,900/t.length)),c=h+t.length*d+10,v=(n.hoehe-o-10)/Math.max(1,s-r),g=f=>o+(s-f)*v,k=_n(s-r),S=[];for(let f=Math.ceil(r/k)*k;f<=s+1e-9;f+=k)S.push(f);return a`<svg class="einheitenprofil" viewBox="0 0 ${c} ${n.hoehe}" width=${c} height=${n.hoehe} role="img"
      aria-label="Einheiten je Bohrung">
    ${S.map(f=>Z`
      <line x1=${h-4} x2=${c} y1=${g(f)} y2=${g(f)} class="raster"></line>
      <text x=${h-6} y=${g(f)+3} class="achse-text" text-anchor="end">${se(f,k<1?1:0)}</text>`)}
    ${t.map((f,A)=>{const K=h+A*d+d*.2,De=d*.6;return Z`
        <text x=${K+De/2} y=${o-8} class="code" text-anchor="middle">${f.code}</text>
        ${f.einheiten.filter(E=>E.status==="vorhanden"&&E.ok_modell-E.uk_modell>.001).map(E=>Z`
          <rect x=${K} y=${g(E.ok_modell)} width=${De} height=${Math.max(.8,(E.ok_modell-E.uk_modell)*v)}
            fill=${i.get(E.einheit)??"#ccc"} class=${`einheit ${n.gewaehlt===E.einheit?"gewaehlt":""}`}
            @click=${()=>n.waehlen?.(E.einheit)}>
            <title>${f.code}: ${E.einheit} ${se(E.ok_modell)} bis ${se(E.uk_modell)} m NHN</title>
          </rect>`)}
        <line x1=${K-3} x2=${K+De+3} y1=${g(f.endteufe_nhn)} y2=${g(f.endteufe_nhn)} class="endteufe"></line>`})}
  </svg>`}const ke=(e,n=2)=>e==null?"":e.toLocaleString("de-DE",{minimumFractionDigits:n,maximumFractionDigits:n}),je=e=>{const n=e.target.value.trim().replace(",",".");return n===""?null:Number(n)},dt=[["boden","Böden"],["organisch","Organisch"],["geologisch","Geologische Benennung"],["fels","Fels"],["anthropogen","Anthropogen"],["unbekannt","Nicht klassifiziert"]];let we=null,Me="",F=.5,tn=!1;function Ln(){return l.z?.plausibilitaet??[]}function xn(e){return Ln().find(n=>n.id===e)?.befunde??[]}function ve(e){const n=he(),t=n.findIndex(s=>s.id===l.bid),i=n[Math.min(n.length-1,Math.max(0,t+e))];i&&Se(i.id)}function En(){const e=he(),n=Ie(e.findIndex(t=>t.id===l.bid));n&&Se(n)}async function Nn(){const e=l.bid;if(!await b([{op:"bohrung_pruefen",id:e,wert:!0}],{leise:!0}))return;const n=Ie(he().findIndex(t=>t.id===e));n&&n!==e&&await Se(n)}async function an(e){const n=l.z.pruefstand,t=e?`Alle Schichten aller ${n.bohrungen[1]} Bohrungen als geprüft markieren?`:"Die Prüfung aller Bohrungen zurücknehmen?";confirm(t)&&await b([{op:"alle_pruefen",wert:e}])}window.addEventListener("keydown",e=>{if(l.schritt!=="bohrungen"||e.ctrlKey||e.metaKey||e.altKey||e.target?.closest?.("input, select, textarea, [contenteditable]"))return;const t=e.key.toLowerCase();if(e.key==="ArrowDown"||t==="j")ve(1);else if(e.key==="ArrowUp"||t==="k")ve(-1);else if(t==="n")En();else if(t==="g")Nn();else return;e.preventDefault()});async function gt(e,n){const t=Number(e.id.split(":")[0]),i=(n[0]?.quelle.seite??e.seite)-1,s=`${l.sig}/${t}/${i}`;if(we?.schluessel===s||Me===s||!l.z?.dokumente[t]?.pdf)return;Me=s;const r=await w(()=>$.seite(l.sig,t,i));Me="",r&&(we={schluessel:s,daten:r},p())}function mt(e){return e.entfernt?a`<span class="zeichen raus" title="nicht im Modell">–</span>`:e.offen>0?a`<span class="zeichen warn" title=${`${e.offen} Schicht(en) nicht klassifiziert`}>⚠</span>`:e.schichten_n&&e.schichten_geprueft===e.schichten_n?a`<span class="zeichen ok" title="alle Schichten geprüft">✓</span>`:a`<span class="zeichen" title="noch zu prüfen">○</span>`}function pt(e){const n=xn(e.id);if(!n.length)return u;const t=n.some(s=>s.stufe==="warnung"),i=n.map(s=>`${s.stufe==="warnung"?"Warnung":"Hinweis"}: ${s.text}`).join(`
`);return a`<span class=${`klein ${t?"warn":"leise"}`} title=${i}>${t?"⚠":"ℹ"}\u00a0${n.length}</span>`}function bt(e){const n=xn(e.id);if(!n.length)return u;const t=n.filter(r=>r.stufe==="warnung").length,i=n.filter(r=>r.stufe==="hinweis").length,s=[t?`${t} Warnung(en)`:"",i?`${i} Hinweis(e)`:""].filter(Boolean).join(", ");return a`
    <details class="still" ?open=${t>0}>
      <summary class=${t?"warn":""}>${t?"⚠":"ℹ"} Plausibilität (${n.length}): ${s}</summary>
      <ul class="dienste klein">
        ${n.map(r=>a`
          <li class=${r.stufe==="warnung"?"warn":"leise"}>
            ${r.stufe==="warnung"?"⚠ Warnung":"ℹ Hinweis"}: ${r.text}
          </li>`)}
      </ul>
    </details>`}function ft(){const e=l.z.bohrungen,n=he(),t=e.filter(i=>i.entfernt);return a`
    <aside class="bohrliste-app">
      <input class="suche" type="search" placeholder="Bohrung suchen …" .value=${l.filter}
        @input=${i=>{l.filter=i.target.value,p()}}>
      <ul class="bliste" role="listbox" aria-label="Bohrungen">
        ${n.map(i=>a`
          <li role="option" aria-selected=${String(i.id===l.bid)} class=${i.id===l.bid?"aktiv":""}
            @click=${()=>Se(i.id)}>
            ${mt(i)}
            <span class="name">${i.code} ${pt(i)}</span>
            <span class="wert">${i.schichten_geprueft}/${i.schichten_n}</span>
            <button class="symbol leise-knopf" title="Aus dem Modell entfernen" aria-label=${`${i.code} entfernen`}
              @click=${s=>{s.stopPropagation(),b([{op:"entfernen",id:i.id}])}}>🗑</button>
          </li>`)}
      </ul>
      ${t.length?a`
        <details class="entfernt" ?open=${tn} @toggle=${i=>{tn=i.target.open}}>
          <summary>Entfernt / nicht im Modell (${t.length}) ${m("entfernen")}</summary>
          <ul class="bliste">
            ${t.map(i=>a`
              <li class="raus">
                <span class="name">${i.code}</span>
                <span class="wert klein">${i.doppelt_in?"doppelt":i.schichten_n?"":"ohne Schichten"}</span>
                <button class="link klein" ?disabled=${!i.schichten_n} @click=${()=>b([{op:"wiederherstellen",id:i.id}])}>wiederherstellen</button>
              </li>`)}
          </ul>
        </details>`:u}
      <p class="leise klein tasten">↑/↓ blättern · N nächste offene · G alle Schichten geprüft und weiter</p>
    </aside>`}function $t(){const e=l.z.pruefstand,[n,t]=e.bohrungen,[i,s]=e.schichten,r=Ln().flatMap(d=>d.befunde),o=r.filter(d=>d.stufe==="warnung").length,h=r.filter(d=>d.stufe==="hinweis").length;return a`
    <div class="pruefleiste">
      <div class="balken"><span>Bohrungen geprüft <b>${n}/${t}</b></span><progress max=${t||1} value=${n}></progress></div>
      <div class="balken"><span>Schichten geprüft <b>${i}/${s}</b></span><progress max=${s||1} value=${i}></progress></div>
      <span class=${`plakette ${e.unklassifiziert_offen?"warn":"ok"}`}>
        ${e.unklassifiziert_offen?`⚠ ${e.unklassifiziert_offen} Schicht(en) nicht klassifiziert`:"✓ keine offenen Warnungen"}</span>
      ${m("warnung")}
      <span class=${`klein ${o?"warn":"leise"}`}>Plausibilität: ${o} Warnungen, ${h} Hinweise</span>
      <span class="fueller"></span>
      ${m("pruefstand")}
      <button @click=${()=>an(!0)} ?disabled=${n===t&&i===s}>✓ Alle Bohrungen geprüft</button>
      <button class="leise-knopf" @click=${()=>an(!1)} ?disabled=${!i}>Zurücknehmen</button>
      ${m("alle_pruefen")}
    </div>`}function W(e,n,t){return a`<label class="feld"><span>${e}${t?m(t):u}</span>${n}</label>`}function kt(e){const n=Mn(e.epsg,e.x,e.y);return n&&!n.ok?a`<p class="hinweise warn">⚠ ${n.text}</p>`:u}function wt(e){const n=he(),t=n.findIndex(s=>s.id===e.id),i=s=>r=>b([{op:"bohrung",id:e.id,feld:s,wert:je(r)}]);return a`
    <div class="detail-kopf">
      <div class="titelzeile">
        <h2>${e.code}</h2>
        <span class="leise">${e.dokument} · Seite ${e.seite}${e.doppelt_in?` · doppelt (auch in ${e.doppelt_in})`:""}</span>
        <span class="fueller"></span>
        <button title="Vorherige Bohrung (↑)" ?disabled=${t<=0} @click=${()=>ve(-1)}>↑ Vorherige</button>
        <button title="Nächste Bohrung (↓)" ?disabled=${t>=n.length-1} @click=${()=>ve(1)}>↓ Nächste</button>
        <button title="Nächste Bohrung mit offenen Schichten (N)" ?disabled=${!Ie(t)} @click=${En}>⚠ Nächste offene</button>
      </div>
      <div class="felder">
        ${W("GOK [m NHN]",a`<input type="number" step="0.01" .value=${z(e.gok===null?"":String(e.gok))}
            placeholder="unbekannt" @change=${i("gok")}>
            <small class=${e.gok_quelle==="manuell"||e.gok_quelle==="DGM"?"manuell":"leise"}>${e.gok_quelle||"fehlt"}</small>`,"gok")}
        ${W("Endteufe [m]",a`<output>${ke(e.endteufe)}</output>`)}
        ${W("Rechtswert",a`<input type="number" step="0.01" .value=${z(e.x===null?"":String(e.x))} @change=${i("x")}>`,"koordinaten")}
        ${W("Hochwert",a`<input type="number" step="0.01" .value=${z(e.y===null?"":String(e.y))} @change=${i("y")}>`)}
        ${W("Koordinatensystem (EPSG)",We(e.epsg,s=>b([{op:"bohrung",id:e.id,feld:"epsg",wert:s}])),"epsg")}
        ${W("Ø Säule [m]",a`<input type="number" step="0.1" min="0" class="kurz" placeholder=${`auto ${ke(l.z.durchmesser??l.z.durchmesser_auto,1)}`}
            .value=${z(e.durchmesser===null?"":String(e.durchmesser))} @change=${i("durchmesser")}>`,"durchmesser")}
        ${W("Grundwasser",a`<output>${e.grundwasser||"–"}</output>`)}
      </div>
      ${kt(e)}
      ${bt(e)}
      ${e.hinweise.length?a`<p class="hinweise">ℹ ${e.hinweise.join(" · ")}</p>`:u}
    </div>`}function vt(e,n){const t=l.z.klassen,i=t.some(s=>s.klasse===n.bodenart);return a`
    <span class="farbfeld" style=${`background:${n.farbe}`}></span>
    <select aria-label="Bodenart" @change=${s=>b([{op:"schicht",id:e.id,k:n.k,feld:"bodenart",wert:s.target.value}])}>
      ${i?u:a`<option .selected=${!0} value=${n.bodenart}>${n.bodenart}</option>`}
      ${dt.map(([s,r])=>a`
        <optgroup label=${r}>
          ${t.filter(o=>o.art===s).map(o=>a`
            <option value=${o.klasse} .selected=${o.klasse===n.bodenart}>${o.name}${o.din4023?` (${o.din4023})`:""}</option>`)}
        </optgroup>`)}
    </select>`}function zt(e,n){return a`
    <table class="tabelle schichten">
      <thead><tr>
        <th title="geprüft">✓ ${m("geprueft")}</th><th>von [m] ${m("tiefe")}</th><th>bis [m]</th>
        <th>Bodenart ${m("bodenart")}</th><th>Beschreibung (PDF)</th><th>nach Norm ${m("norm")}</th>
      </tr></thead>
      <tbody>
        ${n.map(t=>a`
          <tr class=${[t.offen?"warn":"",t.korrigiert?"korrigiert":"",t.k===l.k?"gewaehlt":""].join(" ")}
            @click=${()=>{l.k=t.k,p()}}>
            <td><input type="checkbox" .checked=${z(t.geprueft)} aria-label="geprüft"
              @change=${i=>b([{op:"schicht",id:e.id,k:t.k,feld:"geprueft",wert:i.target.checked}],{leise:!0})}></td>
            <td><input type="number" step="0.01" min="0" class="tief" .value=${z(String(t.von))}
              @change=${i=>b([{op:"schicht",id:e.id,k:t.k,feld:"oben",wert:je(i)}])}></td>
            <td><input type="number" step="0.01" min="0" class="tief" .value=${z(String(t.bis))}
              @change=${i=>b([{op:"schicht",id:e.id,k:t.k,feld:"unten",wert:je(i)}])}></td>
            <td class="bodenart">${vt(e,t)}
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
                <button class="vorschlag" @click=${i=>{i.stopPropagation(),b([{op:"vorschlag",id:e.id,k:t.k}])}}
                  title=${`Vorschlag nach Norm: ${t.vorschlag.benennung}${t.vorschlag.sicher?"":" (unsicher)"}`}>
                  → ${t.vorschlag.klasse} übernehmen</button>${m("vorschlag")}`:u}
            </td>
          </tr>`)}
      </tbody>
    </table>`}function Bt(e,n){gt(e,n);const t=Number(e.id.split(":")[0]),i=!!l.z.dokumente[t]?.pdf,s=we?.schluessel===`${l.sig}/${t}/${(n[0]?.quelle.seite??e.seite)-1}`?we.daten:null,r=n.find(c=>c.k===l.k)??null,o=(c,v)=>{if(!c||!s)return u;const g=s.px_je_pt*F;return a`<div class=${`bbox ${v}`} style=${`left:${c[0]*g}px;top:${c[1]*g}px;width:${(c[2]-c[0])*g}px;height:${(c[3]-c[1])*g}px`}></div>`},h=n.map(c=>c.quelle.bbox).filter(c=>!!c&&c.length===4),d=h.length?[Math.min(...h.map(c=>c[0])),Math.min(...h.map(c=>c[1])),Math.max(...h.map(c=>c[2])),Math.max(...h.map(c=>c[3]))]:null;return a`
    <aside class="quelle-spalte">
      <div class="saeule-rahmen">
        ${ct(n.map(c=>({k:c.k,von:c.von,bis:c.bis,farbe:c.farbe,warn:c.offen,geprueft:c.geprueft,titel:`${ke(c.von)}–${ke(c.bis)} m: ${c.bodenart}${c.beschreibung?` – ${c.beschreibung}`:""}`})),{hoehe:420,gewaehlt:l.k,waehlen:c=>{l.k=c,p()}})}
      </div>
      ${i?a`<div class="pdf-rahmen">
        <div class="pdf-kopf"><b>Quelle im PDF</b> ${m("quelle")}
          <span class="fueller"></span>
          ${i?a`<button class="symbol" title="kleiner" @click=${()=>{F=Math.max(.25,F/1.4),p()}}>−</button>
            <button class="symbol" title="größer" @click=${()=>{F=Math.min(1.5,F*1.4),p()}}>+</button>`:u}
        </div>
        ${s?a`
          ${yt(d,s.px_je_pt*F)}
          <div class="pdf-seite">
            <div class="pdf-flaeche" style=${`width:${s.breite_pt*s.px_je_pt*F}px;height:${s.hoehe_pt*s.px_je_pt*F}px`}>
              <img src=${s.url} alt=${`Seite ${s.seite+1}`} draggable="false">
              ${o(d,"saeule-bbox")}
              ${o(r?.quelle.bbox,"schicht-bbox")}
            </div>
          </div>`:a`<p class="leise klein">Seite wird geladen …</p>`}
      </div>`:u}
    </aside>`}let rn="";function yt(e,n){const t=`${l.bid}/${F}`;return!e||rn===t?u:(requestAnimationFrame(()=>{const i=document.querySelector(".pdf-seite");i&&(i.scrollLeft=Math.max(0,e[0]*n-i.clientWidth/3),i.scrollTop=Math.max(0,e[1]*n-40),rn=t)}),u)}function St(){const e=l.z,n=l.details.get(l.bid),t=e.bohrungen.find(r=>r.id===l.bid),i=t?Number(t.id.split(":")[0]):0,s=!e.dokumente[i]?.pdf;return a`
    <div class=${`schritt-bohrungen ${s?"ohne-pdf":""}`}>
      ${$t()}
      ${ft()}
      <section class="bohrung-detail">
        ${t?a`
          ${wt(t)}
          ${n?a`
            ${zt(t,n.schichten)}
            <div class="detail-fuss">
              <button class="primaer" title="Alle Schichten dieser Bohrung als geprüft markieren und zur nächsten offenen (G)"
                @click=${Nn}>✓ Alle Schichten geprüft – weiter</button>
              <button class="leise-knopf" ?disabled=${!t.schichten_geprueft}
                @click=${()=>b([{op:"bohrung_pruefen",id:t.id,wert:!1}])}>Prüfung zurücknehmen</button>
              <span class="fueller"></span>
              <button class="gefahr" @click=${()=>b([{op:"entfernen",id:t.id}])}>🗑 Aus dem Modell entfernen</button>
            </div>`:a`<p class="leise">Schichten werden geladen …</p>`}`:a`<p class="leise">Links eine Bohrung wählen.</p>`}
      </section>
      ${t&&n?Bt(t,n.schichten):a`<aside class="quelle-spalte"></aside>`}
    </div>`}const y=(e,n=2)=>e==null||!Number.isFinite(e)?"":e.toLocaleString("de-DE",{minimumFractionDigits:n,maximumFractionDigits:n}),x=e=>{const n=e.target.value.trim().replace(",",".");return n===""?null:Number(n)};let B=null,ze="",ie="plan",oe,Fe=250,Oe=100,Re=100;const V=new Set;function ln(e){const n=e.unterlage;return n?`${n.sha}/${n.seite}/${n.art}/${JSON.stringify(n.kalibrierung)}`:""}function An(e){const n=e.unterlage;if(!n)return B=null;if(B&&B.schluessel===ln(e))return B;const t=n.kalibrierung,i=o=>o&&!("n"in o)?o:null,s=i(t?.massstab),r=i(t?.hoehe);return B={schluessel:ln(e),massArt:t?.massstab&&"n"in t.massstab?"n":"strecke",p1:s?{u:s.u1,v:s.v1}:null,p2:s?{u:s.u2,v:s.v2}:null,meter:s?.meter??null,n:t?.massstab&&"n"in t.massstab?t.massstab.n:null,hoeheArt:t?.hoehe?"n"in t.hoehe?"n":"strecke":"gleich",h1:r?{u:r.u1,v:r.v1}:null,h2:r?{u:r.u2,v:r.v2}:null,hoeheMeter:r?.meter??null,hoeheN:t?.hoehe&&"n"in t.hoehe?t.hoehe.n:null,bezug:t?.bezug?{u:t.bezug.u,v:t.bezug.v}:null,x:t?.bezug?.x??null,y:t?.bezug?.y??null,drehung:t?.drehung??0,epsg:t?.epsg??e.viewer.epsg??null},B}function Ce(e,n=!1){const t=B,i=e.unterlage;if(!t||!i)return null;let s=null;if(t.massArt==="n"&&t.n&&t.n>0&&(s={n:t.n}),t.massArt==="strecke"&&t.p1&&t.p2&&t.meter&&t.meter>0&&(s={u1:t.p1.u,v1:t.p1.v,u2:t.p2.u,v2:t.p2.v,meter:t.meter}),!s||!t.bezug||t.x===null||t.y===null)return null;let r=null;return i.art==="schnitt"&&t.hoeheArt==="n"&&t.hoeheN&&t.hoeheN>0&&(r={n:t.hoeheN}),i.art==="schnitt"&&t.hoeheArt==="strecke"&&t.h1&&t.h2&&t.hoeheMeter&&t.hoeheMeter>0&&(r={u1:t.h1.u,v1:t.h1.v,u2:t.h2.u,v2:t.h2.v,meter:t.hoeheMeter}),{massstab:s,hoehe:r,bezug:{...t.bezug,x:t.x,y:t.y},drehung:i.art==="plan"?t.drehung:0,epsg:i.art==="plan"?t.epsg:null,gesperrt:n}}function _(){const e=l.z;l.entwurf=Ce(e);const n=l.viewer;n&&B&&(n.editor.hilfsmarken({strecke:B.massArt==="strecke"?[B.p1,B.p2]:[],hoehe:B.hoeheArt==="strecke"?[B.h1,B.h2]:[],bezug:B.bezug}),l.entwurf&&n.editor.vorschau(l.entwurf)),p()}async function Gt(e){const n=l.viewer;if(!n||!B)return;ze=e,p();const t=await n.editor.bildpunktWaehlen();if(ze="",!t||!B||l.z?.unterlage?.kalibrierung?.gesperrt){p();return}B[e]=t,_()}async function sn(e){l.viewer?.editor.waehlenAbbrechen();const n=Ce(l.z,e);if(!n){L("Für die Kalibrierung fehlen Maßstab oder Bezugspunkt.","warn");return}await b([{op:"kalibrierung",wert:n}])&&(l.entwurf=null,L(e?"Plan kalibriert und gesperrt – jetzt die Bohrungen ziehen.":"Kalibrierung übernommen.","ok"),await l.viewer?.ansicht(l.z?.unterlage?.art==="schnitt"?"sued":"oben"))}async function Dt(e){const n=l.z.unterlage;n?.kalibrierung&&await b([{op:"kalibrierung",wert:{...n.kalibrierung,gesperrt:e}}])}async function Mt(e){const n=e.target,t=n.files?.[0];if(n.value="",!t)return;const i=await w(()=>$.unterlage(l.sig,t,ie,0),"Unterlage wird gelesen …");i&&(P(i),l.entwurf=null,p(),await Ge(),await l.viewer?.lageModus(!0),await l.viewer?.ansicht(i.unterlage?.art==="schnitt"?"sued":"oben"))}async function on(e,n){const t=await w(()=>$.unterlageSeite(l.sig,e,n),"Seite wird gelesen …");t&&(P(t),l.entwurf=null,p(),await Ge(),await l.viewer?.ansicht(n==="schnitt"?"sued":"oben"))}async function _t(){if(!confirm("Unterlage mit ihrer Kalibrierung entfernen? Gesetzte Bohrungen behalten ihre Lage."))return;const e=await w(()=>$.unterlageEntfernen(l.sig));e&&(P(e),l.entwurf=null,p(),await Ge())}const O=(e,n,t=!0)=>a`<details class="abschnitt" ?open=${t}><summary>${e}</summary><div class="abschnitt-inhalt">${n}</div></details>`;function ne(e,n,t,i){return a`<button class=${`punkt ${ze===n?"aktiv":""} ${t?"gesetzt":""}`} ?disabled=${i}
    @click=${()=>Gt(n)}>${ze===n?"… im Plan klicken":t?`${e} ✓`:e}</button>`}function Lt(e){const n=Mn(e.epsg,e.x,e.y);return n?a`<p class=${`klein ${n.ok?"ok":"warn"}`}>${n.ok?"✓":"⚠"} ${n.text}</p>`:u}function xt(e){const n=e.unterlage,t=An(e),i=!!n.kalibrierung?.gesperrt,s=n.art==="plan",r=t.p1&&t.p2?Math.hypot(t.p2.u-t.p1.u,t.p2.v-t.p1.v):null,o=Ce(e),h=o?Wn(o.massstab,n.mm_pro_px):null,d=e.viewer.bohrungen.filter(c=>c.x!==null&&(s?!/Plan|Viewer/.test(c.quelle):c.gok_bekannt));return a`
    <p class=${`status ${n.kalibrierung?i?"ok":"":"warn"}`}>
      ${n.kalibrierung?a`${i?"🔒 gesperrt · ":""}${qe(n)}${s?` · ${Ve(n.kalibrierung.epsg)}`:""}`:"nicht kalibriert"}
      ${l.entwurf&&JSON.stringify({...l.entwurf,gesperrt:!1})!==JSON.stringify({...n.kalibrierung??{},gesperrt:!1})?a`<br><span class="leise">Vorschau: ${qe(n,l.entwurf)} (noch nicht übernommen)</span>`:u}
    </p>
    ${i?a`
      <p class="leise klein">Der Plan liegt fest. ${s?"Bohrungen unten mit „Punkte setzen“ in den Plan klicken oder im Viewer ziehen – nur in x/y":"Bohrungen im Viewer ziehen – entlang der Station; die Höhe nur ohne GOK aus dem PDF"}.</p>
      <button @click=${()=>Dt(!1)}>🔓 Entsperren (neu kalibrieren)</button>`:a`
      <fieldset class="gruppe">
        <legend>1 · Maßstab ${m("massstab")}</legend>
        <div class="umschalter">
          <label><input type="radio" name="massart" .checked=${t.massArt==="strecke"} @change=${()=>{t.massArt="strecke",_()}}> Strecke messen</label>
          <label><input type="radio" name="massart" .checked=${t.massArt==="n"} @change=${()=>{t.massArt="n",_()}}> 1:n eingeben</label>
        </div>
        ${t.massArt==="strecke"?a`
          <div class="zeile">${ne("Punkt 1","p1",t.p1,!1)}${ne("Punkt 2","p2",t.p2,!1)}</div>
          <div class="zeile">
            <span class="leise klein">${r?`gemessen ${y(r,0)} px`:"zwei Punkte anklicken"}</span>
            <label class="inline">wahre Länge <input type="number" step="0.01" min="0" class="kurz" .value=${z(t.meter===null?"":String(t.meter))}
              @input=${c=>{t.meter=x(c),_()}}> m</label>
          </div>`:a`
          <label class="inline">Maßstab 1: <input type="number" step="1" min="1" class="kurz" .value=${z(t.n===null?"":String(t.n))}
            @input=${c=>{t.n=x(c),_()}}></label>`}
        ${h?a`<p class="leise klein">ergibt 1:${Math.round(h).toLocaleString("de-DE")}</p>`:u}
      </fieldset>
      ${s?u:a`
        <fieldset class="gruppe">
          <legend>Höhenmaßstab ${m("hoehe")}</legend>
          <div class="umschalter">
            <label><input type="radio" name="hoeheart" .checked=${t.hoeheArt==="gleich"} @change=${()=>{t.hoeheArt="gleich",_()}}> wie Länge</label>
            <label><input type="radio" name="hoeheart" .checked=${t.hoeheArt==="n"} @change=${()=>{t.hoeheArt="n",_()}}> 1:n</label>
            <label><input type="radio" name="hoeheart" .checked=${t.hoeheArt==="strecke"} @change=${()=>{t.hoeheArt="strecke",_()}}> messen</label>
          </div>
          ${t.hoeheArt==="n"?a`<label class="inline">Höhe 1: <input type="number" step="1" min="1" class="kurz"
              .value=${z(t.hoeheN===null?"":String(t.hoeheN))} @input=${c=>{t.hoeheN=x(c),_()}}></label>`:u}
          ${t.hoeheArt==="strecke"?a`
            <div class="zeile">${ne("Höhe oben","h1",t.h1,!1)}${ne("Höhe unten","h2",t.h2,!1)}</div>
            <label class="inline">Höhenunterschied <input type="number" step="0.01" min="0" class="kurz"
              .value=${z(t.hoeheMeter===null?"":String(t.hoeheMeter))} @input=${c=>{t.hoeheMeter=x(c),_()}}> m</label>`:u}
        </fieldset>`}
      <fieldset class="gruppe">
        <legend>2 · Bezugspunkt ${m("bezug")}</legend>
        <div class="zeile">${ne("Punkt im Plan wählen","bezug",t.bezug,!1)}</div>
        <div class="zeile">
          <label class="feld schmal"><span>${s?"Rechtswert":"Station [m]"}</span>
            <input type="number" step="0.01" .value=${z(t.x===null?"":String(t.x))} @input=${c=>{t.x=x(c),_()}}></label>
          <label class="feld schmal"><span>${s?"Hochwert":"Höhe [m NHN]"}</span>
            <input type="number" step="0.01" .value=${z(t.y===null?"":String(t.y))} @input=${c=>{t.y=x(c),_()}}></label>
        </div>
        ${s?a`
          <label class="feld breit"><span>Koordinatensystem (EPSG) ${m("epsg")}</span>
            ${We(t.epsg,c=>{t.epsg=c,_()})}</label>
          ${Lt(t)}`:u}
        ${d.length?a`
          <label class="inline klein">oder von Bohrung
            <select @change=${c=>{const v=e.viewer.bohrungen.find(g=>g.id===c.target.value);v&&(t.x=v.x,t.y=s?v.y:v.gok,_())}}>
              <option value="">–</option>
              ${d.map(c=>a`<option value=${c.id}>${c.code}</option>`)}
            </select></label>`:u}
      </fieldset>
      ${s?a`
        <fieldset class="gruppe">
          <legend>3 · Drehung ${m("drehung")}</legend>
          <div class="zeile">
            <label class="inline"><input type="number" step="0.1" class="kurz" .value=${z(String(t.drehung))}
              @input=${c=>{t.drehung=x(c)??0,_()}}> ° gegen den Uhrzeigersinn</label>
          </div>
        </fieldset>`:u}
      <div class="zeile knopfzeile">
        <button ?disabled=${!o} @click=${()=>sn(!1)}>Übernehmen</button>
        <button class="primaer" ?disabled=${!o} @click=${()=>sn(!0)}>🔒 Übernehmen und sperren</button>
        ${m("sperren")}
      </div>
      ${n.kalibrierung?a`<button class="link klein" @click=${()=>b([{op:"kalibrierung",wert:null}])}>Kalibrierung zurücksetzen</button>`:u}`}`}function Et(e){const n=e.unterlage;return n?a`
    <p><b>${n.name}</b> <span class="leise">· ${n.art==="plan"?"Lageplan":"Längsschnitt"}</span></p>
    <div class="zeile">
      ${(n.seiten??1)>1?a`<label class="inline">Seite <select @change=${t=>on(Number(t.target.value),n.art)}>
          ${Array.from({length:n.seiten},(t,i)=>a`<option value=${i} .selected=${i===n.seite}>${i+1}</option>`)}
        </select></label>`:u}
      <label class="inline">Ansicht <select @change=${t=>on(n.seite,t.target.value)}>
        <option value="plan" .selected=${n.art==="plan"}>Lageplan</option>
        <option value="schnitt" .selected=${n.art==="schnitt"}>Längsschnitt</option>
      </select></label>
    </div>
    <label class="inline">Deckkraft ${m("deckkraft")}
      <input type="range" min="0.1" max="1" step="0.05" .value=${String(l.viewer?.editor.deckkraft??.85)}
        @input=${t=>{l.viewer&&(l.viewer.editor.deckkraft=Number(t.target.value),l.viewer.editor.bildSichtbarkeit())}}></label>
    <button class="link klein" @click=${_t}>Unterlage entfernen</button>`:a`
      <p class="leise klein">Lageplan (von oben) oder Längsschnitt (von der Seite) als PDF – er liegt im Viewer unter den Bohrungen.</p>
      <div class="umschalter">
        <label><input type="radio" name="neueart" .checked=${ie==="plan"} @change=${()=>{ie="plan"}}> Lageplan</label>
        <label><input type="radio" name="neueart" .checked=${ie==="schnitt"} @change=${()=>{ie="schnitt"}}> Längsschnitt</label>
      </div>
      <label class="datei-knopf"><input type="file" accept=".pdf,application/pdf" @change=${Mt}>PDF wählen …</label>`}function Nt(e){const n=e.unterlage,t=!n||!!n.kalibrierung?.gesperrt,i=e.viewer.bohrungen.filter(o=>o.x===null),s=e.lage_modus==="reihe",r=!s&&n?.art==="plan"&&!!n.kalibrierung?.gesperrt;return a`
    ${t?u:a`<p class="warnung">Erst kalibrieren und sperren (🔒) – dann Punkte setzen oder Bohrungen ziehen.</p>`}
    ${r?At(e):u}
    ${i.length?a`
      <p class="klein">Ohne Lage (${i.length}) – ${r?"anklicken = als Nächste setzen, oder":""} in den Viewer ziehen
        ${m("ohne_lage")}</p>
      <div class="parkplatz">
        ${i.map(o=>a`<span class=${`park ${t?"":"gesperrt"} ${l.punktModus&&l.naechste===o.id?"aktiv":""}`}
          title=${r?"Klick: als nächste Bohrung setzen · Ziehen: direkt in den Viewer":"In den Viewer ziehen"}
          @pointerdown=${h=>l.viewer?.editor.ziehenStart(h,o.id,!0)}
          @click=${()=>{r&&Be(!0,o.id)}}>${o.code}</span>`)}
      </div>`:a`<p class="leise klein">Alle Bohrungen im Modell haben eine Lage.</p>`}
    ${r?Pt(e):u}
    ${s?Kt(e):u}`}function Be(e,n){l.punktModus=e,n!==void 0?l.naechste=n:e&&!l.naechste&&(l.naechste=In()),l.viewer?.editor.punktModusSetzen(e),p()}function At(e){const n=e.viewer.bohrungen.filter(i=>i.x===null),t=e.viewer.bohrungen.filter(i=>i.x!==null);return a`
    <div class="zeile">
      <button class=${l.punktModus?"primaer":""} @click=${()=>Be(!l.punktModus)}>
        ${l.punktModus?"● Punkte setzen – Klick in den Plan":"＋ Punkte im Plan setzen"}</button>
      ${l.punktModus?a`<button class="leise-knopf" @click=${()=>Be(!1)}>Fertig (Esc)</button>`:u}
      ${m("punkte")}
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
      <p class="leise klein">Danach ist automatisch die nächste Bohrung ohne Lage dran.</p>`:u}`}function Pt(e){const n=e.viewer.bohrungen.filter(r=>r.x!==null&&/Plan|Viewer/.test(r.quelle)),t=e.viewer.bohrungen,i=t.filter(r=>r.x===null);if(!n.length&&!e.punkte.length)return u;const s=(r,o)=>a`<span class="leise klein">R ${y(r)}<br>H ${y(o)}</span>`;return a`
    <p class="klein">Gesetzte Punkte (${n.length+e.punkte.length})</p>
    <table class="tabelle kompakt punkte">
      <tbody>
        ${e.punkte.map(r=>a`
          <tr class=${`frei ${l.viewer?.editor.punktGewaehlt===r.id?"gewaehlt":""}`}>
            <td><button class="link" title="Im Viewer wählen" @click=${()=>{l.viewer?.editor.punktWaehlen(r.id),p()}}>◆ ${r.id}</button></td>
            <td>${s(r.x,r.y)}</td>
            <td><select aria-label=${`${r.id} zuordnen`} @change=${o=>{const h=o.target.value;h&&b([{op:"punkt_zuordnen",punkt:r.id,bohrung:h}])}}>
              <option value="" selected>– Bohrung zuordnen –</option>
              ${i.length?a`<optgroup label="Ohne Lage">${i.map(o=>a`<option value=${o.id}>${o.code}</option>`)}</optgroup>`:u}
              <optgroup label="Mit Lage (ersetzen)">${t.filter(o=>o.x!==null).map(o=>a`<option value=${o.id}>${o.code}</option>`)}</optgroup>
            </select></td>
            <td><button class="symbol" title="Punkt löschen" @click=${()=>b([{op:"punkt_loeschen",punkt:r.id}])}>✕</button></td>
          </tr>`)}
        ${n.map(r=>a`
          <tr class=${l.viewer?.editor.ausgewaehlt===r.id?"gewaehlt":""}>
            <td><button class="link" title="Im Viewer wählen" @click=${()=>{l.viewer?.nadelWaehlen(r.id),p()}}>● ${r.code}</button></td>
            <td>${s(r.x,r.y)}</td>
            <td><select aria-label=${`${r.code} umhängen`} @change=${o=>{const h=o.target.value;h==="-"?b([{op:"lage_loesen",id:r.id}]):h&&h!==r.id&&b([{op:"lage_umhaengen",id:r.id,nach:h}])}}>
              <option value=${r.id} selected>${r.code}</option>
              <option value="-">– Zuordnung lösen (freier Punkt) –</option>
              ${i.length?a`<optgroup label="Andere Bohrung (ohne Lage)">${i.map(o=>a`<option value=${o.id}>${o.code}</option>`)}</optgroup>`:u}
            </select></td>
            <td><button class="symbol" title="Lage entfernen (Bohrung wieder ohne Lage)" @click=${()=>b([{op:"lage_entfernen",id:r.id}])}>✕</button></td>
          </tr>`)}
      </tbody>
    </table>`}function Kt(e){const n=e.reihe.map(i=>i.id),t=(i,s)=>{const r=[...n],[o]=r.splice(i,1);r.splice(Math.max(0,Math.min(r.length,i+s)),0,o),b([{op:"reihe",reihenfolge:r}],{leise:!0})};return a`
    <div class="zeile">
      <label class="inline">Standardabstand ${m("standardabstand")}
        <input type="number" step="1" min="1" class="kurz" .value=${z(String(e.reihe_standard))}
          @change=${i=>b([{op:"reihe",standard:x(i)}])}> m</label>
    </div>
    <table class="tabelle kompakt reihe">
      <thead><tr><th></th><th>Bohrung</th><th>Abstand [m] ${m("reihe")}</th><th>Station [m]</th></tr></thead>
      <tbody>
        ${e.reihe.map((i,s)=>a`
          <tr>
            <td class="pfeile"><button class="symbol" ?disabled=${s===0} title="nach vorn" @click=${()=>t(s,-1)}>▲</button><button class="symbol"
              ?disabled=${s===n.length-1} title="nach hinten" @click=${()=>t(s,1)}>▼</button></td>
            <td>${i.code}</td>
            <td><input type="number" step="0.1" min="0" class="kurz" ?disabled=${s===0} .value=${z(i.abstand===null?"":String(i.abstand))}
              @change=${r=>b([{op:"reihe",abstand:{[i.id]:x(r)}}],{leise:!0})}></td>
            <td><input type="number" step="0.1" class="kurz" .value=${z(String(i.station))} title=${i.quelle_text}
              @change=${r=>b([{op:"reihe",station:{[i.id]:x(r)}}],{leise:!0})}></td>
          </tr>`)}
      </tbody>
    </table>`}async function Tt(e){const n=e.target,t=[...n.files??[]];if(n.value="",!t.length)return;const i=oe===void 0?l.z?.viewer.epsg??null:oe,s=await w(()=>$.dgm(l.sig,t,i),"DGM wird gelesen …");if(s){P(s),p();const r=s.gelaende?.pruefung?.warnungen.length??0;L(r?"DGM geladen – Hinweise zum Vergleich beachten.":"DGM geladen.",r?"warn":"ok")}}async function jt(){const e=await w(()=>$.dgmAbruf(l.sig,Oe),"DGM wird beim Land abgerufen …");if(e){P(e),p();const n=e.gelaende?.pruefung?.warnungen.length??0;L(n?"DGM vom Land geladen – Hinweise zum Vergleich beachten.":"DGM vom Land geladen.",n?"warn":"ok")}}function un(e){return e.lage_modus!=="koordinaten"?u:a`
    <div class="zeile">
      <label class="inline">Rand <input type="number" min="0" max="1000" step="25" class="kurz" aria-label="Rand um die Bohrungen"
        .value=${z(String(Oe))} @change=${n=>{Oe=x(n)??100}}> m</label>
      <button @click=${jt} title="Sendet den Ausschnitt um die Bohrungen an den Dienst des Landes">
        DGM vom Land abrufen</button>${m("dgm_land")}
    </div>
    <p class="leise klein">Brandenburg mit Berlin und NRW (DGM1, WCS). Sendet den Ausschnitt um die Bohrungen an den Dienst.</p>`}async function Ft(){if(!confirm("DGM aus dem Projekt entfernen? Übernommene GOK bleiben (Quelle DGM)."))return;const e=await w(()=>$.dgmEntfernen(l.sig));e&&(P(e),p())}const _e={ok:["✓","ok"],abweichung:["⚠ weicht ab","warn"],ohne_gok:["GOK fehlt",""],aus_dgm:["aus dem DGM","leise"],ausserhalb:["außerhalb","leise"],ohne_lage:["ohne Lage","leise"],anderes_system:["anderes EPSG","warn"]},cn=e=>e===null?"":Math.abs(e)<.005?y(0):`${e>0?"+":""}${y(e)}`;function Ot(e){const n=e.gelaende,t=d=>a`<label class="datei-knopf"><input type="file" multiple aria-label="DGM-Dateien"
    accept=".xyz,.txt,.csv,.asc,.tif,.tiff,.zip,.gz" @change=${Tt}>${d}</label>`,i=oe===void 0?e.viewer.epsg??null:oe,s=a`<label class="feld breit"><span>System der Datei (XYZ, ASCII) ${m("dgm_epsg")}</span>
    ${We(i,d=>{oe=d,p()},"System der DGM-Datei")}</label>`;if(!n)return a`
      <p class="leise klein">DGM-Kachel(n) des Landes (Open Data, z. B. DGM1) als XYZ, ASCII-Raster oder GeoTIFF, auch als
        ZIP – Höhen in m NHN. Damit prüft die App die GOK, schlägt fehlende vor und legt das Gelände ins Modell.</p>
      ${un(e)}
      ${s}
      ${t("DGM-Dateien wählen …")}`;const r=n.info,o=n.pruefung,h=r.quelle;return a`
    <p><b>${r.name}</b><br><span class="leise klein">${Ve(r.epsg)} · Raster ${y(r.dx,1)} m ·
      ${r.spalten.toLocaleString("de-DE")} × ${r.zeilen.toLocaleString("de-DE")} · ${y(r.zmin,1)} – ${y(r.zmax,1)} m NHN</span></p>
    ${h?a`<p class="leise klein">${h.anbieter} · <a href=${h.beleg} target="_blank" rel="noopener">${h.lizenz}</a> ·
      ${h.namensnennung} · abgerufen ${h.abgerufen}</p>`:u}
    ${n.fehler?a`<p class="warnung klein">${n.fehler}</p>`:u}
    ${o?a`
      <table class="tabelle kompakt gelaende">
        <thead><tr><th>Bohrung</th><th class="zahl">GOK</th><th class="zahl">DGM</th><th class="zahl">Δ [m]</th><th></th></tr></thead>
        <tbody>
          ${o.zeilen.map(d=>a`
            <tr class=${_e[d.status][1]}>
              <td><button class="link" title="Im Viewer wählen" @click=${()=>{l.viewer?.nadelWaehlen(d.id),p()}}>${d.code}</button></td>
              <td class="zahl">${y(d.gok)}</td>
              <td class="zahl">${y(d.dgm)}</td>
              <td class="zahl">${cn(d.differenz)}</td>
              <td class=${`klein ${_e[d.status][1]}`}>${d.status==="ohne_gok"?a`<button class="klein" title="GOK aus dem DGM übernehmen (Quelle DGM)"
                    @click=${()=>b([{op:"gok_aus_dgm",ids:[d.id]}])}>übernehmen</button>`:_e[d.status][0]}</td>
            </tr>`)}
        </tbody>
      </table>
      ${o.verglichen?a`<p class="leise klein">${o.verglichen} verglichen · Median ${cn(o.median)} m ·
        größte Abweichung ${y(o.max)} m (unauffällig bis ${y(o.toleranz,1)} m)</p>`:u}
      ${o.warnungen.map(d=>a`<p class="warnung klein">⚠ ${d}</p>`)}
      ${o.vorschlaege>1?a`<button @click=${()=>b([{op:"gok_aus_dgm"}])}>
        Alle ${o.vorschlaege} fehlenden GOK aus dem DGM übernehmen</button>`:u}`:u}
    ${un(e)}
    ${s}
    <div class="zeile">${t("Andere DGM-Dateien …")}
      <button class="link klein" @click=${Ft}>DGM entfernen</button></div>`}async function Rt(){const e=await w(()=>$.sgdAbfrage(l.sig,Fe),"Dienste der Länder werden abgefragt …");if(!e?.sgd)return;P(e),V.clear(),p();const n=e.sgd;L(`${n.treffer.length} Bohrungen der Länder im Umkreis von ${y(n.radius,0)} m`+(n.fehler.length?` – ${n.fehler.length} Meldung(en) der Dienste`:""),n.fehler.length?"warn":"ok")}async function Ht(){const e=[...V].map(t=>({dienst:t.slice(0,t.indexOf("/")),id:t.slice(t.indexOf("/")+1)})),n=await w(()=>$.sgdUebernehmen(l.sig,e),"Schichtdaten werden beim Land geholt …");if(n){P(n.zustand),V.clear();for(const t of n.meldungen)L(t,"ok");await Ge(),p()}}function It(e){const n=e.treffer.filter(r=>!r.uebernehmbar&&!r.uebernommen&&!r.gutachten);if(!n.length)return u;const t=r=>e.quellen.find(o=>o.dienst===r)?.land??r,i=r=>{const o=n.filter(h=>h.schichten===r);return o.length?`${o.length} (${[...new Set(o.map(h=>t(h.dienst)))].join(", ")})`:""},s=[i("grafik")&&`${i("grafik")} nur mit Kopfdaten: das Land gibt das Schichtenverzeichnis nur als Bild heraus (Profil ↗), nicht als Daten`,i("portal")&&`${i("portal")} nur als Hinweis: das Schichtenverzeichnis liegt beim Land, der Dienst nennt nur die Kopfdaten`,i("keine")&&`${i("keine")} ohne Schichtenverzeichnis`,i("ohne Petrographie")&&`${i("ohne Petrographie")} mit Schichten ohne Petrographie`].filter(Boolean);return a`<p class="leise klein sgd-warum">Nicht übernehmbar: ${s.join("; ")}. Ohne Schichten entsteht kein Modell –
    sie zu erfinden wäre falsch. Lage, GOK und Teufe sehen Sie hier; die Schichten im Profil des Landes. Übernehmbar sind
    Bohrungen mit Schichtdaten in BoreholeML (NRW, Baden-Württemberg, Hamburg).</p>`}function Ut(e){return e.gutachten?a`<span class="ok" title="Dieselbe Bohrung im Gutachten">= ${e.gutachten}</span>`:e.uebernommen?a`<span class="ok">✓ im Projekt</span>`:e.schichten==="boreholeml"?a`${e.schichten_n} Schichten`:e.schichten==="grafik"&&e.profil?a`<a href=${e.profil} target="_blank" rel="noopener">Profil ↗</a>`:e.schichten==="portal"?a`<span class="leise" title="Nur ein Hinweis: das Schichtenverzeichnis liegt beim Land, nicht in diesem Dienst">beim Land</span>`:a`<span class="leise">${e.schichten==="ohne Petrographie"?"ohne Petrographie":"keine Schichten"}</span>`}async function Vt(){const e=await w(()=>$.gebaeudeAbruf(l.sig,Re),"Gebäude werden beim Land abgerufen …");e&&(P(e),p(),L(`${e.gebaeude?.anzahl??0} Gebäude geladen – im Modell als Umgebung.`,"ok"))}async function Wt(){const e=await w(()=>$.gebaeudeEntfernen(l.sig));e&&(P(e),p())}function Ct(e){if(e.lage_modus!=="koordinaten")return a`<p class="leise klein">Nur mit Lage nach Koordinaten.</p>`;const n=e.gebaeude,t=a`
    <div class="zeile">
      <label class="inline">Rand <input type="number" min="0" max="1000" step="25" class="kurz" aria-label="Rand der Gebäude"
        .value=${z(String(Re))} @change=${s=>{Re=x(s)??100}}> m</label>
      <button @click=${Vt} title="Lädt die Kacheln (1 × 1 km) um die Bohrungen beim Land">
        ${n?"Gebäude neu abrufen":"Gebäude vom Land abrufen"}</button>${m("gebaeude")}
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
    <button class="link klein" @click=${Wt}>Gebäude entfernen</button>`}function Zt(e){if(e.lage_modus==="reihe")return a`<p class="leise klein">Nur mit Lage nach Koordinaten.</p>`;const n=e.sgd,t=a`
    <p class="leise klein">Bohrungen aus den Datenbanken der Geologischen Dienste um die Mitte des Projekts.
      <b>Die Abfrage sendet die Lage des Projekts an den Dienst des Landes.</b></p>
    <div class="zeile">
      <label class="inline">Umkreis <input type="number" min="10" max="2000" step="50" class="kurz" aria-label="Umkreis der Abfrage"
        .value=${z(String(Fe))} @change=${h=>{Fe=x(h)??250}}> m</label>
      <button @click=${Rt}>${n?"Neu abfragen":"Abfragen"}</button>
    </div>`;if(!n)return t;const i=n.gegenprobe,s=i.anzahl>0&&(i.lage_max??0)<=1&&(i.gok_max??0)<=.5,r=n.treffer.slice(0,60),o=n.treffer.filter(h=>h.uebernehmbar).length;return a`
    ${t}
    <p class="klein">${n.treffer.length} Bohrungen im Umkreis von ${y(n.radius,0)} m · ${n.zeit}</p>
    ${i.anzahl?a`<p class=${`klein ${s?"ok":"warnung"}`}>${s?"✓":"⚠"} ${i.anzahl} Bohrungen des Gutachtens auch
      beim Land: Lage ≤ ${y(i.lage_max)} m${i.gok_max!==null?a`, GOK ≤ ${y(i.gok_max)} m`:u}${s?"":" – Lage und GOK prüfen"}</p>`:u}
    ${n.fehler.map(h=>a`<p class="warnung klein">${h.dienst}: ${h.fehler}</p>`)}
    ${Cn(n.portale)}
    ${r.length?a`
      <table class="tabelle kompakt sgd">
        <thead><tr><th></th><th>Bohrung</th><th class="zahl">Abstand</th><th class="zahl">GOK</th><th class="zahl">Teufe</th><th>Schichten</th></tr></thead>
        <tbody>
          ${r.map(h=>{const d=`${h.dienst}/${h.id}`;return a`<tr class=${h.gutachten?"doppelt":""}>
              <td>${h.uebernehmbar?a`<input type="checkbox" aria-label=${`${h.name} übernehmen`} .checked=${V.has(d)}
                @change=${c=>{c.target.checked?V.add(d):V.delete(d),p()}}>`:u}</td>
              <td title=${`${h.dienst} · ID ${h.id}${h.datum?` · ${h.datum}`:""}`}>${h.name}</td>
              <td class="zahl">${y(h.abstand,0)}</td>
              <td class="zahl">${y(h.gok)}</td>
              <td class="zahl">${y(h.teufe,1)}</td>
              <td class="klein">${Ut(h)}</td>
            </tr>`})}
        </tbody>
      </table>
      ${n.treffer.length>r.length?a`<p class="leise klein">… und ${n.treffer.length-r.length} weitere (Umkreis verkleinern)</p>`:u}`:u}
    ${o?a`<button class="primaer" ?disabled=${!V.size} @click=${Ht}>
      Ausgewählte übernehmen (${V.size})</button>
      <p class="leise klein">Nur Bohrungen mit Schichtdaten in BoreholeML (NRW, Baden-Württemberg, Hamburg); sie kommen mit Quelle und Lizenz ins Projekt.</p>`:u}
    ${It(n)}
    ${n.quellen.map(h=>a`<p class="leise klein">Quelle: ${h.namensnennung} · <a href=${h.beleg} target="_blank" rel="noopener">Dienst</a></p>`)}
    <button class="link klein" @click=${async()=>{const h=await w(()=>$.sgdVerwerfen(l.sig));h&&(P(h),p())}}>Abfrage verwerfen</button>`}function qt(e){const n=l.viewer;n&&(!e.unterlage||e.unterlage.kalibrierung?.gesperrt||!B?n.editor.hilfsmarken({}):n.editor.hilfsmarken({strecke:B.massArt==="strecke"?[B.p1,B.p2]:[],hoehe:B.hoeheArt==="strecke"?[B.h1,B.h2]:[],bezug:B.bezug}))}let hn=!1;function Jt(e){const n=e.standort;return O(a`Standort ${m("standort")}`,a`
    <p class="klein"><b>${y(n.x,1)} / ${y(n.y,1)}</b> · EPSG:${n.epsg}</p>
    <p class="leise klein">Georeferenziert über den Punkt: kein Lageplan, keine Kalibrierung – die Bohrungen der Länder
      kommen mit ihren Koordinaten. Ein Gutachten dazu (Schritt Start) wird ein neues Projekt mit Lageplan.</p>
    ${yn(n.dienste)}`)}let dn=!1;function Qt(e){const n=e.viewer.bohrungen.length,t=e.viewer.bohrungen.filter(i=>i.x===null).length;return e.standort?a`<p class="stand-satz ok">Standort ${Math.round(e.standort.x)} / ${Math.round(e.standort.y)} · EPSG:${e.standort.epsg}
      ${n?a` · ${n} Bohrungen der Länder`:a` · <span class="leise">Bohrungen der Länder unten abfragen</span>`}</p>`:n?t?a`<p class="stand-satz warn">${t} von ${n} Bohrungen ohne Lage – auf dem Plan setzen oder Koordinaten eingeben</p>`:a`<p class="stand-satz ok">✓ Alle ${n} Bohrungen haben eine Lage${e.lage_modus==="reihe"?" (Reihe)":""}
      – jetzt mit den Bohrungen der Länder vergleichen</p>`:u}function Yt(){const e=l.z;An(e),qt(e);const n=e.lage_modus!=="reihe"&&e.unterlage?.art==="plan"&&!!e.unterlage.kalibrierung?.gesperrt;l.punktModus&&!n&&(l.punktModus=!1),l.viewer?.editor.punktModusSetzen(l.punktModus),hn||(hn=!0,window.addEventListener("keydown",r=>{r.key==="Escape"&&l.schritt==="lage"&&l.punktModus&&Be(!1)}));const t=e.viewer.bohrungen.length>0&&e.viewer.bohrungen.every(r=>r.x!==null),i=e.lage_modus==="koordinaten"&&t&&!e.unterlage,s=dn||!!(e.gelaende||e.gebaeude);return a`
    <div class="app-panel links">
      ${Qt(e)}
      ${e.standort?Jt(e):a`
        ${O(a`Lage der Bohrungen ${m("lage_art")}`,a`
          <div class="umschalter">
            <label><input type="radio" name="lagemodus" .checked=${e.lage_modus==="koordinaten"}
              @change=${()=>b([{op:"lage_modus",wert:"koordinaten"}])}> Koordinaten (Lageplan)</label>
            <label><input type="radio" name="lagemodus" .checked=${e.lage_modus==="reihe"}
              @change=${()=>b([{op:"lage_modus",wert:"reihe"}])}> Reihe (Längsschnitt)</label>
          </div>`)}
        ${O(a`Unterlage ${m("unterlage")}`,Et(e),!i)}
        ${e.unterlage?O(a`Kalibrieren`,xt(e)):u}
        ${O(a`Bohrungen setzen`,Nt(e),!i)}`}
      ${O(a`Vergleich mit Bohrungen der Länder${e.sgd?.gegenprobe.anzahl?" ✓":""} ${m("sgd")}`,Zt(e))}
      <details class="erweitert" ?open=${s}
        @toggle=${r=>{dn=r.target.open}}>
        <summary>Erweitert <span class="leise klein">Gelände · Gebäude · Darstellung</span></summary>
        ${O(a`Gelände (DGM)${e.gelaende?.pruefung?.warnungen.length?" ⚠":e.gelaende?" ✓":""} ${m("gelaende")}`,Ot(e),!!e.gelaende)}
        ${O(a`Gebäude (LoD2)${e.gebaeude?" ✓":""} ${m("gebaeude")}`,Ct(e),!!e.gebaeude)}
        ${O(a`Darstellung`,a`
          <label class="inline">Ø Bohrsäulen ${m("durchmesser")}
            <input type="number" step="0.1" min="0" class="kurz" placeholder=${`auto ${y(e.durchmesser_auto,1)}`}
              .value=${z(e.durchmesser===null?"":String(e.durchmesser))}
              @change=${r=>b([{op:"durchmesser",wert:x(r)}])}> m</label>
          <p class="leise klein">Je Bohrung im Schritt Bohrungen (Ø Säule). Leer = automatisch nach Modellgröße.</p>`,!1)}
      </details>
      ${e.hinweise.length?a`<div class="hinweisliste">${e.hinweise.map(r=>a`<p class="klein">ℹ ${r}</p>`)}</div>`:u}
    </div>`}const M=(e,n=2)=>e==null?"–":e.toLocaleString("de-DE",{minimumFractionDigits:n,maximumFractionDigits:n}),Pn={idw:"IDW",tps:"Dünnplatten-Spline",implizit:"implizit (GemPy)"};let be=null,Kn="",gn=!1,R={x:"",y:""},Ze=null;async function Xt(){const e=l.sig;if(!e)return;const n=await w(()=>$.analyse(e,100),"Kreuzprobe und Unsicherheit werden gerechnet …");n&&(be=n,Kn=l.modell?.schluessel??"",Ze=null,n.mitte&&!R.x&&(R={x:String(n.mitte[0]),y:String(n.mitte[1])}),p())}async function Tn(){const e=l.sig,n=Number(R.x.replace(",",".")),t=Number(R.y.replace(",","."));if(!e||!Number.isFinite(n)||!Number.isFinite(t))return;const i=await w(()=>$.analysePunkt(e,n,t),"Virtuelle Bohrung …");i&&(Ze=i,p())}function ei(e){const n=e.kreuzprobe;return a`
    <table class="tabelle kompakt">
      <thead><tr><th>Methode</th><th title="mittlerer Fehler der Schichtgrenzen an der weggelassenen Bohrung">mittl. Fehler [m]</th>
        <th>max. [m]</th><th>Grenzen</th></tr></thead>
      <tbody>${Object.entries(n.methoden).map(([t,i])=>a`
        <tr class=${t===n.methode_modell?"gewaehlt":""}>
          <td>${Pn[t]??t}${t===n.methode_modell?a` <span class="leise klein">(Modell)</span>`:u}${t===n.beste?a` <b title="sagt die Bohrungen am besten voraus">★</b>`:u}</td>
          <td class="zahl">${M(i.gesamt.mae)}</td><td class="zahl">${M(i.gesamt.max)}</td><td class="zahl">${i.gesamt.n}</td>
        </tr>`)}</tbody>
    </table>`}function ni(e){const n=e.unsicherheit,t=e.kreuzprobe.methoden[e.kreuzprobe.methode_modell];return a`
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
          <td class="zahl">${r?.n?M(r.mae):a`<span class="leise">–</span>`}</td>
          <td class="zahl">${i.unterkante_bezifferbar?M(i.sigma_mittel_m):a`<span class="leise" title="keine Bohrung erreicht die Unterkante">offen</span>`}</td>
          <td class="zahl">${i.unterkante_bezifferbar?M(i.sigma_p95_m):"–"}</td>
          <td class="zahl ${o?"warn":""}">${o?`${o} ×`:"✓"}</td>
          <td class="zahl klein">${Math.round(i.volumen_m3.modell).toLocaleString("de-DE")}${i.volumen_m3.p5!==null?a`<br><span class="leise">${Math.round(i.volumen_m3.p5).toLocaleString("de-DE")}–${Math.round(i.volumen_m3.p95).toLocaleString("de-DE")}</span>`:u}</td>
          <td class="zahl">${M(i.methoden_differenz_m.max)}</td>
        </tr>`})}</tbody>
    </table>`}function ti(e){const n=e.vorschlaege??[];return n.length?a`
    <h4>Wo die nächste Bohrung am meisten bringt ${m("erkundung")}</h4>
    <table class="tabelle kompakt vorschlag">
      <thead><tr><th>#</th><th>Rechtswert</th><th>Hochwert</th><th>Grund</th><th title="nächste vorhandene Bohrung">Abstand [m]</th><th></th></tr></thead>
      <tbody>${n.map((t,i)=>a`<tr>
        <td>${i+1}</td><td class="zahl">${M(t.x,1)}</td><td class="zahl">${M(t.y,1)}</td><td class="klein">${t.grund}</td>
        <td class="zahl">${M(t.abstand_naechste_bohrung_m,0)}</td>
        <td><button class="link" @click=${()=>{R={x:String(t.x),y:String(t.y)},Tn()}}>virtuell bohren</button></td></tr>`)}</tbody>
    </table>
    <p class="leise klein">Ein Vorschlag aus der Unsicherheit des Modells – Zugang, Leitungen und Baufeld kennt es nicht.</p>`:u}function ii(e){const n=Ze;return a`
    <h4>Virtuelle Bohrung ${m("virtuell")}</h4>
    <div class="zeile knopfzeile">
      <label class="inline">Rechtswert <input class="mittel" .value=${R.x} @input=${t=>{R.x=t.target.value}}></label>
      <label class="inline">Hochwert <input class="mittel" .value=${R.y} @input=${t=>{R.y=t.target.value}}></label>
      <button @click=${Tn}>Bohren</button>
    </div>
    <p class="leise klein">Im System der Bohrungen${e.epsg?` (EPSG ${e.epsg})`:""}; vorbelegt mit der Mitte des Modells.</p>
    ${n?.fehler?a`<p class="warn">${n.fehler}</p>`:u}
    ${n&&!n.fehler?a`
      <p class="klein">GOK ${M(n.gok_nhn)} m NHN · ${M(n.abstand_m,1)} m von ${n.naechste_bohrung} · <span class="leise">${n.herkunft}</span></p>
      <table class="tabelle kompakt virtuell">
        <thead><tr><th>Tiefe [m]</th><th>Einheit</th><th>Unterkante [m NHN]</th><th>± σ [m]</th><th>95 % [m NHN]</th></tr></thead>
        <tbody>${n.schichten.map(t=>a`<tr>
          <td class="zahl">${M(t.tiefe_oben_m)}–${M(t.tiefe_unten_m)}</td><td>${t.einheit}</td>
          <td class="zahl">${M(t.unten_nhn)}${t.unterkante_offen?a` <span class="leise klein">offen</span>`:u}</td>
          <td class="zahl">${M(t.sigma_unten_m)}</td>
          <td class="zahl klein">${t.unten_95_nhn?`${M(t.unten_95_nhn[0])} … ${M(t.unten_95_nhn[1])}`:"–"}</td></tr>`)}</tbody>
      </table>
      ${n.hinweise.map(t=>a`<p class="leise klein">${t}</p>`)}`:u}`}function ai(){const e=l.modell;if(!e?.bericht)return u;const n=be&&Kn===e.schluessel?be:null,t=be&&!n,i=n;return a`
    <details class="erweitert karte analyse" ?open=${gn||!!i}
      @toggle=${s=>{gn=s.target.open}}>
      <summary>Ground Analysis ${m("analyse")} <span class="leise klein">Kreuzprobe · Unsicherheit · virtuelle Bohrung</span></summary>
      <div class="zeile knopfzeile">
        <button class=${i?"":"primaer"} @click=${Xt}>${i?"Neu rechnen":"Analyse rechnen"}</button>
        ${t?a`<span class="warn klein">Das Modell hat sich geändert – neu rechnen.</span>`:u}
      </div>
      ${i?.fehler?a`<p class="warn">${i.fehler}</p>`:u}
      ${i&&!i.fehler?a`
        <h4>Kreuzprobe <span class="leise klein">(${i.kreuzprobe.bohrungen} Bohrungen, je eine weggelassen)</span></h4>
        ${ei(i)}
        ${[...i.kreuzprobe.hinweise,...i.unsicherheit.hinweise].map(s=>a`<p class="hinweis klein">⚑ ${s}</p>`)}
        <h4>Unsicherheit je Einheit <span class="leise klein">(${i.unsicherheit.laeufe} Läufe, ${Pn[i.unsicherheit.methode]??i.unsicherheit.methode})</span></h4>
        ${ni(i)}
        <details class="klein"><summary class="leise">Annahmen</summary>
          <ul>${i.unsicherheit.annahmen.map(s=>a`<li>${s}</li>`)}</ul></details>
        ${ti(i)}
        ${ii(i)}`:u}
    </details>`}let ae=0,C="",jn="";const Le=e=>e.replace(/[<>&"]/g,n=>({"<":"&lt;",">":"&gt;","&":"&amp;",'"':"&quot;"})[n]);async function ri(){const e=l.sig;if(!e||!l.viewer)return;const n=await w(()=>$.analyseFlaeche(e,ae),"Unsicherheit wird gerechnet …");if(n){if(n.fehler){l.viewer.meldung(n.fehler,6e3);return}l.viewer.unsicherheit({name:n.name,punkte:n.punkte,dreiecke:n.dreiecke,sigma:n.sigma,sigma_max:n.sigma_max}),C=n.name,jn=l.modell?.schluessel??"",n.hinweis&&l.viewer.meldung(n.hinweis,6e3),p()}}function li(){l.viewer?.unsicherheit(null),C="",p()}let ue=null,Fn="";async function si(){const e=l.sig;if(!e||!l.viewer)return;const n=await w(()=>$.analyseGrundwasser(e),"Grundwasserfläche …");if(n){if(n.fehler){l.viewer.meldung(n.fehler,6e3);return}ue=n,Fn=l.modell?.schluessel??"",l.viewer.grundwasser(n.flaeche??null),n.flaeche||l.viewer.meldung(n.hinweise?.[0]??"keine Grundwasserfläche",6e3),p()}}function oi(){l.viewer?.grundwasser(null),ue=null,p()}function ui(){ue&&Fn!==(l.modell?.schluessel??"")&&(l.viewer?.grundwasser(null),ue=null);const e=ue,n=(t,i=2)=>t.toLocaleString("de-DE",{minimumFractionDigits:i,maximumFractionDigits:i});return a`
    <div class="zeile">
      <button @click=${si}>Grundwasserfläche zeigen</button>${m("grundwasser")}
      ${e?a`<button class="link" @click=${oi}>Grundwasser ausblenden</button>`:u}
    </div>
    ${e?a`<div class="klein grundwasser">
      <p>${e.gemessen} gemessene${e.trocken?`, ${e.trocken} trockene`:""} von ${e.staende?.length??0} Bohrungen
        ${e.flaeche?a` · ${n(e.flaeche.z_min)} bis ${n(e.flaeche.z_max)} m NHN`:u}
        ${e.kreuzprobe?a` · Kreuzprobe ⌀ ${n(e.kreuzprobe.mae_m)} m, max. ${n(e.kreuzprobe.max_m)} m`:u}</p>
      ${(e.hinweise??[]).length?a`<ul class="hinweise">${e.hinweise.map(t=>a`<li>${t}</li>`)}</ul>`:u}
    </div>`:u}`}async function ci(){const e=l.sig,n=l.viewer;if(!e||!n)return;const t=await n.punktWaehlen();if(!t)return;const i=await w(()=>$.analysePunkt(e,t.e,t.n),"Virtuelle Bohrung …");if(!i)return;if(i.fehler){n.meldung(i.fehler,6e3);return}const s=(o,h=2)=>o==null?"–":o.toLocaleString("de-DE",{minimumFractionDigits:h,maximumFractionDigits:h}),r=i.schichten.map(o=>`<tr><td>${s(o.tiefe_oben_m)}–${s(o.tiefe_unten_m)} m</td><td>${Le(o.einheit)}</td>
    <td>${o.sigma_unten_m===null?o.unterkante_offen?"offen":"–":`± ${s(o.sigma_unten_m)} m`}</td></tr>`).join("");n.tafel("Virtuelle Bohrung",`<p>${s(i.x,1)} / ${s(i.y,1)} · GOK ${s(i.gok_nhn)} m NHN · ${s(i.abstand_m,1)} m von ${Le(i.naechste_bohrung??"")}</p>
    <table><tr><th>Tiefe</th><th>Einheit</th><th>Unterkante</th></tr>${r}</table>
    <p><i>${Le(i.herkunft??"")}</i></p>`)}function hi(){const e=l.modell?.bericht;return!e||l.modell?.fehler?u:(ae>=e.einheiten.length&&(ae=0),C&&jn!==(l.modell?.schluessel??"")&&(l.viewer?.unsicherheit(null),C=""),a`
    <section class="abschnitt-flach analyse-viewer">
      <h3>Ground Analysis im Viewer ${m("analyse")}</h3>
      <div class="zeile">
        <select @change=${n=>{ae=Number(n.target.value)}}>
          ${e.einheiten.map((n,t)=>a`<option value=${t} .selected=${t===ae}>${n.name}</option>`)}
        </select>
        <button @click=${ri}>Unsicherheit zeigen</button>
        ${C?a`<button class="link" @click=${li}>Unsicherheit ausblenden</button>`:u}
      </div>
      ${C?a`<p class="leise klein">Gezeigt: Unterkante ${C}, gefärbt nach σ (grün sicher, rot unsicher).</p>`:u}
      <div class="zeile"><button @click=${ci}>Virtuelle Bohrung: Punkt im Viewer wählen</button>${m("virtuell")}</div>
      ${ui()}
    </section>`)}let U=null,xe=!1,D="DIN 18300",Ee=null;async function mn(){U||xe||(xe=!0,U=await w(()=>$.homogenbereicheDaten())??null,xe=!1,p())}let I=null,He="";async function pn(){const e=l.sig;if(!e)return;const n=`${D}|${l.modell?.schluessel??""}`;He!==n&&(He=n,I=await w(()=>$.hbVorschlag(e,D))??null,p())}let re=null,bn="";async function di(){const e=l.sig;if(!e)return;const n=`${D}|${l.modell?.schluessel??""}|${JSON.stringify(l.z?.homogenbereiche?.[D]??{})}`;bn!==n&&(bn=n,re=await w(()=>$.hbKennwerte(e,D))??null,p())}function te(e){return b([{op:"homogenbereiche",atv:D,zuordnung:e}])}function gi(){const e=l.modell?.bericht;if(!e)return u;const n=l.z?.homogenbereiche??{},t=n[D]??{},i=e.einheiten.map(g=>g.name),s=Ee??Object.keys(n).length>0;s&&mn();const r=U?U.kennwerte.filter(g=>U.matrix[D]?.[g.nr]):[],o=[];for(const g of i){const k=t[g];if(!k)continue;let S=o.find(f=>f.name===k);S||o.push(S={name:k,einheiten:[]}),S.einheiten.push(g)}s&&!Object.keys(t).length&&pn();const h=I&&!I.fehler&&I.atv===D?I:null;s&&di();const d=re&&!re.fehler&&re.atv===D?re:null,c=Object.keys(t).filter(g=>!i.includes(g)),v=i.filter(g=>!t[g]);return a`
    <details class="erweitert karte homogenbereiche" .open=${z(s)}
      @toggle=${g=>{Ee=g.target.open,Ee&&mn()}}>
      <summary>Homogenbereiche (VOB/C) <span class="leise klein">${Object.keys(n).length?Object.keys(n).join(", "):"Einheiten je Gewerk zuordnen"}</span></summary>
      <div class="einstellung">
        <span>Gewerk (ATV) ${m("homogenbereiche")}</span>
        <select @change=${g=>{D=g.target.value,I=null,p()}}>
          ${(U?.atv??[{code:"DIN 18300",gewerk:"Erdarbeiten"}]).map(g=>a`
            <option value=${g.code} .selected=${g.code===D}>${g.code} ${g.gewerk}${n[g.code]?" ✓":""}</option>`)}
        </select>
      </div>
      ${h&&!Object.keys(t).length?a`
        <div class="hb-vorschlag">
          <p class="klein"><b>Vorschlag für ${D}</b> <span class="leise">(${h.stufe}: ${h.regel})</span></p>
          <table class="tabelle kompakt">
            <tbody>${h.bereiche.map(g=>a`<tr><td><b>${g.name}</b></td><td>${g.einheiten.join(", ")}</td>
              <td class="leise klein">${g.grund}</td></tr>`)}</tbody>
          </table>
          <button @click=${()=>te(h.zuordnung)}>Vorschlag übernehmen</button>
          <span class="leise klein">danach je Einheit änderbar</span>
        </div>`:u}
      <table class="tabelle kompakt hb-zuordnung">
        <thead><tr><th>Einheit</th><th>Homogenbereich</th></tr></thead>
        <tbody>${e.einheiten.map(g=>a`<tr>
          <td><span class="farbfeld" style=${`background:${g.farbe}`}></span> ${g.name}</td>
          <td><input class="kurz" list="hb-namen" placeholder="–" .value=${z(t[g.name]??"")}
            @change=${k=>{const S=k.target.value.trim(),f={...t};S?f[g.name]=S:delete f[g.name],te(Object.keys(f).length?f:null)}}></td></tr>`)}</tbody>
      </table>
      <datalist id="hb-namen">${o.map(g=>a`<option value=${g.name}></option>`)}</datalist>
      <div class="zeile knopfzeile">
        <button class="link" @click=${()=>te(Object.fromEntries(i.map((g,k)=>[g,`B${k+1}`])))}
          title="Je Einheit ein eigener Bereich (B1, B2, … von oben); zusammenfassen durch gleiche Namen">Vorschlag: je Einheit ein Bereich</button>
        <button class="link" @click=${async()=>{He="",await pn(),I?.zuordnung&&await te(I.zuordnung)}}
          title="Einheiten, die sich für dieses Gewerk gleich verhalten, in einem Bereich (Begründung oben, wenn noch nichts zugeordnet ist)">Vorschlag für ${D}</button>
        ${Object.keys(t).length?a`<button class="link" @click=${()=>te(null)}>Zuordnung ${D} löschen</button>`:u}
      </div>
      ${c.length?a`<p class="warn klein">Zugeordnet, aber nicht mehr im Modell: ${c.join(", ")}</p>`:u}
      ${o.length?a`
        <p class="klein">${o.map(g=>a`<b>${g.name}</b>: ${g.einheiten.join(", ")}<br>`)}
          ${v.length?a`<span class="warn">ohne Bereich: ${v.join(", ")}</span>`:u}</p>`:u}
      ${r.length?a`
        <h4>Kennwerte für ${D} (${r.length})</h4>
        <ul class="klein hb-kennwerte">${r.map(g=>{const k=U.matrix[D][g.nr];return a`<li>${g.nr} ${g.name}${k!=="erforderlich"?a` <span class="leise">(${k})</span>`:u}</li>`})}</ul>
        <p class="leise klein">Quelle der Matrix: ${U.quelle}</p>`:u}
      ${d?a`
        <h4>Aus den Beschreibungen ${m("hb_kennwerte")}</h4>
        ${d.bereiche.map(g=>a`
          <details class="hb-werte">
            <summary><b>${g.name}</b>${g.ohne_bereich?a` <span class="leise">(ohne Bereich)</span>`:u}
              <span class="leise klein">${g.einheiten.join(", ")} · ${g.belegt} von ${g.verlangt} Kennwerten angesprochen ·
                ${g.schichten} Schichten</span></summary>
            <table class="tabelle kompakt">
              <tbody>${g.kennwerte.map(k=>a`<tr>
                <td>${k.nr} ${k.name}</td>
                <td class=${k.wert?"":"leise"}>${k.wert??"offen – nicht im Extrakt"}</td></tr>`)}</tbody>
            </table>
          </details>`)}
        <p class="leise klein">Ansprache aus den Schichtbeschreibungen mit dem Anteil der Schichten; keine Laborwerte.
          Offene Kennwerte stehen im Text oder in den Anlagen des Gutachtens. Das IFC trägt beides je Bereich.</p>`:u}
      <div class="einstellung">
        <span>IFC-Modell</span>
        <label class="inline"><input type="radio" name="hb-modell" .checked=${!l.z?.hb_modell}
          @change=${()=>b([{op:"hb_modell",wert:null}])}> Einheiten</label>
        ${Object.keys(n).map(g=>a`<label class="inline"><input type="radio" name="hb-modell"
          .checked=${l.z?.hb_modell===g} @change=${()=>b([{op:"hb_modell",wert:g}])}>
          Homogenbereiche ${g}</label>`)}
      </div>
      <p class="leise klein">Mit Einheiten trägt jede Einheit und jede Bodenschicht der Bohrsäulen ein Pset je ATV
        (CPset_Homogenbereich_…). Mit Homogenbereichen besteht das Modell aus den Bereichen (gleiche Körper, je Bereich
        zusammengefasst).</p>
    </details>`}const j=(e,n=1)=>e==null?"–":e.toLocaleString("de-DE",{minimumFractionDigits:n,maximumFractionDigits:n});let J="",Ne=null,fn="",$n=!1;function mi(e){return!e||e.quelle!=="DGM"?"aus den GOK der Bohrungen":`aus dem DGM (an den Bohrungen auf die GOK, GOK − DGM bis ${j(Number(e.gok_minus_dgm_max_m),2)} m)`}function pi(){const e=l.z.einstellungen,n=(r,o)=>b([{op:"einstellungen",[r]:o}]),t=(r,o,h,d,c)=>{const v=e[r];return a`
      <div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${v===null} @change=${g=>n(r,g.target.checked?null:d)}> ${o} automatisch</label>${m(c)}
        ${v===null?u:a`<input type="number" step="any" class="kurz" .value=${z(String(v))}
          @change=${g=>n(r,Number(g.target.value))}> ${h}`}
      </div>`},i=l.modell?.bericht?.parameter??{},s=e.methode!=="idw"||e.puffer!==null||e.raster!==null||e.basis!==null||!e.gok_relativ||!e.gelaende_dgm;return a`
    <details class="erweitert karte" ?open=${$n||s}
      @toggle=${r=>{$n=r.target.open}}>
      <summary>Erweitert <span class="leise klein">Interpolation · Puffer · Raster · Basis · Gelände</span></summary>
      <div class="einstellung">
        <span>Interpolation ${m("methode")}</span>
        <label class="inline"><input type="radio" name="methode" .checked=${e.methode==="idw"} @change=${()=>n("methode","idw")}> IDW</label>
        <label class="inline"><input type="radio" name="methode" .checked=${e.methode==="tps"} @change=${()=>n("methode","tps")}> Dünnplatten-Spline</label>
        <label class="inline" title=${l.info?.implizit?"GemPy: je Fläche ein Skalarfeld, Orientierung aus den Kontakten (docs/27)":"GemPy ist auf diesem Server nicht installiert (requirements-analyse.txt)"}><input
          type="radio" name="methode" ?disabled=${!l.info?.implizit&&e.methode!=="implizit"} .checked=${e.methode==="implizit"}
          @change=${()=>n("methode","implizit")}> Implizit (GemPy)</label>
      </div>
      ${e.methode==="implizit"?bi():u}
      ${t("puffer","Puffer","m",Number(i.puffer_m??20),"puffer")}
      ${t("raster","Raster","m",Number(i.raster_m??5),"raster")}
      ${t("basis","Modellbasis","m NHN",Math.floor(Number(i.basis_nhn??0)),"basis")}
      <div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${e.gok_relativ} @change=${r=>n("gok_relativ",r.target.checked)}> fehlende GOK: Gelände = 0 m</label>${m("gok_relativ")}
      </div>
      ${l.z.gelaende?a`<div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${e.gelaende_dgm} @change=${r=>n("gelaende_dgm",r.target.checked)}> Gelände aus dem DGM</label>${m("gelaende_dgm")}
      </div>`:u}
      ${i.raster_m!==void 0?a`<p class="leise klein">gerechnet: Puffer ${j(Number(i.puffer_m),0)} m · Raster ${j(Number(i.raster_m))} m ·
        Basis ${j(Number(i.basis_nhn),2)} m NHN · Fläche ${j(Number(i.flaeche_m2)/1e4,2)} ha ·
        Gelände ${mi(i.gelaende)}</p>`:u}
    </details>`}function bi(){const e=l.modell?.bericht,n=e?.parameter?.orientierung??[];if(!e||!n.length)return a`<p class="leise klein">Orientierung je Einheit: nach dem Rechnen hier eingebbar.</p>`;const t={...l.z.einstellungen.orientierung??{}},i=(r,o,h)=>{const d=t[r]??{fallrichtung:NaN,fallwinkel:NaN},c=h.trim()===""?NaN:Number(h.replace(",",".")),v={...d,[o]:c};if(Number.isNaN(v.fallrichtung)&&Number.isNaN(v.fallwinkel))delete t[r];else if(Number.isNaN(v.fallrichtung)||Number.isNaN(v.fallwinkel)){t[r]=v;return}else t[r]=v;const g=Object.fromEntries(Object.entries(t).filter(([,k])=>!Number.isNaN(k.fallrichtung)&&!Number.isNaN(k.fallwinkel)));b([{op:"einstellungen",orientierung:Object.keys(g).length?g:null}])},s=(r,o,h,d)=>a`
    <input type="number" step="any" min="0" max=${o==="fallwinkel"?80:360} class="kurz" title=${d}
      placeholder="–" .value=${z(h===void 0||Number.isNaN(h)?"":String(h))}
      @change=${c=>i(r,o,c.target.value)}>`;return a`
    <div class="einstellung">
      <span>Orientierung je Einheit ${m("orientierung")}</span>
      <table class="klein orientierung">
        <thead><tr><th>Einheit</th><th>berechnet</th><th>Fallrichtung °</th><th>Fallwinkel °</th></tr></thead>
        <tbody>${n.map(r=>a`<tr>
          <td>${r.einheit}</td>
          <td class="leise">${r.quelle==="Eingabe"?"Eingabe":r.fallen_grad===null?r.quelle:`${j(r.fallen_grad,1)}°${r.fallrichtung_grad!=null?` nach ${j(r.fallrichtung_grad,0)}°`:""} (${r.quelle})`}</td>
          <td>${s(r.einheit,"fallrichtung",t[r.einheit]?.fallrichtung,"Fallrichtung: Azimut von Nord im Uhrzeigersinn")}</td>
          <td>${s(r.einheit,"fallwinkel",t[r.einheit]?.fallwinkel,"Fallwinkel gegen die Horizontale, 0–80°")}</td>
        </tr>`)}</tbody>
      </table>
    </div>`}function fi(){const e=l.modell?.bericht;if(!e)return u;const n=l.z.vorgabe??e.vorlage_einheiten,t=JSON.stringify(n);(!Ne||fn!==t)&&(Ne=n.map(r=>({name:r.name,bodenarten:r.bodenarten.join(", ")})),fn=t);const i=Ne,s=()=>b([{op:"vorgabe",wert:i.filter(r=>r.name.trim()).map(r=>({name:r.name.trim(),bodenarten:r.bodenarten.split(",").map(o=>o.trim()).filter(Boolean)}))}]);return a`
    <section class="karte">
      <h3>Einheiten festlegen ${m("einheiten")}</h3>
      <p class="leise klein">${l.z.vorgabe?"Vorgegeben (eigene Einheiten).":"Automatisch korreliert – hier umbenennen oder Bodenarten zusammenlegen."}</p>
      <table class="tabelle kompakt vorgabe">
        <colgroup><col class="pfeil"><col><col><col class="weg"></colgroup>
        <thead><tr><th></th><th>Einheit</th><th>Bodenarten (mit Komma)</th><th></th></tr></thead>
        <tbody>
          ${i.map((r,o)=>a`
            <tr>
              <td class="pfeile"><button class="symbol" ?disabled=${o===0} @click=${()=>{i.splice(o-1,0,...i.splice(o,1)),p()}}>▲</button><button
                class="symbol" ?disabled=${o===i.length-1} @click=${()=>{i.splice(o+1,0,...i.splice(o,1)),p()}}>▼</button></td>
              <td><input .value=${z(r.name)} @input=${h=>{r.name=h.target.value}}></td>
              <td><input .value=${z(r.bodenarten)} @input=${h=>{r.bodenarten=h.target.value}}></td>
              <td><button class="symbol" title="Zeile löschen" @click=${()=>{i.splice(o,1),p()}}>✕</button></td>
            </tr>`)}
        </tbody>
      </table>
      <div class="zeile knopfzeile">
        <button class="link" @click=${()=>{i.push({name:"",bodenarten:""}),p()}}>+ Zeile</button>
        <span class="fueller"></span>
        <button ?disabled=${!l.z.vorgabe} @click=${()=>b([{op:"vorgabe",wert:null}])}>Automatisch korrelieren</button>
        <button class="primaer" @click=${s}>Mit diesen Einheiten rechnen</button>
      </div>
    </section>`}function $i(){const e=l.modell,n=e?.bericht,t=n?.einheiten.find(i=>i.name===J);return a`
    <div class="schritt-einheiten">
      <div class="spalte">
        ${fi()}
        ${gi()}
        ${pi()}
      </div>
      <div class="spalte breit">
        ${l.rechnet?a`<div class="karte"><div class="kreisel klein"></div> Modell wird gerechnet …</div>`:u}
        ${e?.fehler?a`<div class="karte warnung">Noch kein Modell: ${e.fehler}
          <button class="link" @click=${()=>H("lage")}>→ Lage setzen</button></div>`:u}
        ${n?a`
          <section class="karte">
            <h3>Einheiten (${n.einheiten.length})</h3>
            <table class="tabelle einheiten">
              <thead><tr><th></th><th>Einheit</th><th>Bodenarten</th><th>Volumen [m³]</th><th>max. Mächtigkeit [m]</th>
                <th title="in Bohrungen vorhanden / fehlt / unter der Endteufe">✓ / – / ?</th><th>Hinweise</th></tr></thead>
              <tbody>
                ${n.einheiten.map(i=>a`
                  <tr class=${i.name===J?"gewaehlt":""} @click=${()=>{J=J===i.name?"":i.name,p()}}>
                    <td><span class="farbfeld" style=${`background:${i.farbe}`}></span></td>
                    <td><b>${i.name}</b></td>
                    <td>${i.bodenarten.join(", ")}</td>
                    <td class="zahl">${Math.round(i.volumen_m3).toLocaleString("de-DE")}</td>
                    <td class="zahl">${j(i.maechtigkeit_max_m,2)}</td>
                    <td class="zahl">${i.bohrungen.vorhanden.length} / ${i.bohrungen.fehlt.length} / ${i.bohrungen.unbekannt.length}</td>
                    <td class="klein">${i.hinweise.join("; ")}</td>
                  </tr>`)}
              </tbody>
            </table>
          </section>
          <section class="karte profil-karte">
            <h3>Einheiten je Bohrung <span class="leise klein">(m NHN, Klick wählt die Einheit)</span></h3>
            <div class="profil-scroll">${ht(n,{hoehe:380,gewaehlt:J,waehlen:i=>{J=i,p()}})}</div>
          </section>
          ${t?a`
            <section class="karte">
              <h3><span class="farbfeld" style=${`background:${t.farbe}`}></span> ${t.name}: Beschreibungen aus dem PDF</h3>
              <table class="tabelle kompakt">
                <thead><tr><th>Bohrung</th><th>Tiefe [m]</th><th>Bodenart</th><th>Beschreibung</th></tr></thead>
                <tbody>${t.schichten.map(i=>a`
                  <tr><td>${i.bohrung}</td><td class="zahl">${j(i.von,2)}–${j(i.bis,2)}</td><td>${i.bodenart??"unklassifiziert"}</td>
                    <td>${i.beschreibung||a`<span class="leise">–</span>`}</td></tr>`)}</tbody>
              </table>
            </section>`:u}
          ${ai()}`:u}
      </div>
    </div>`}let ye="";async function ki(){const e=await w(()=>$.einchecken(l.sig,ye));e&&(P(e.zustand),ye="",L(`Eingecheckt: v${e.eintrag.nr} · ${e.eintrag.stand.bohrungen[0]}/${e.eintrag.stand.bohrungen[1]} Bohrungen geprüft`,"ok"),p())}const On=new Set([25831,25832,25833,4647,5650]);let le=(()=>{try{return localStorage.getItem("groundtwin.organisation")??""}catch{return""}})();function wi(){const e=l.z,n=e.bohrungen.filter(s=>s.modell),t=n.filter(s=>s.schichten_n>0&&s.schichten_geprueft===s.schichten_n&&s.x!==null&&s.y!==null&&s.epsg!==null&&On.has(s.epsg)&&s.gok!==null&&e.lage_modus==="koordinaten"),i=`${$.exportUrl(l.sig,"boreholeml")}?organisation=${encodeURIComponent(le)}`;return a`
    <label class="feld breit"><span>Organisation (Absender) ${m("boreholeml")}</span>
      <input type="text" aria-label="Organisation für BoreholeML" placeholder="z. B. Ingenieurbüro …" .value=${le}
        @input=${s=>{le=s.target.value;try{localStorage.setItem("groundtwin.organisation",le)}catch{}p()}}></label>
    ${t.length?a`<a class="knopf" href=${i} download>Bohrungen für den Geologischen Dienst (BoreholeML 3.2)</a>`:a`<span class="knopf aus" title="Erst alle Schichten prüfen; Lage in ETRS89/UTM und GOK nötig">Bohrungen für den Geologischen Dienst (BoreholeML 3.2)</span>`}
    <p class="leise klein">${t.length} von ${n.length} Bohrungen exportierbar (vollständig geprüft, ETRS89/UTM, GOK).</p>`}let ce=!1;async function vi(){if(!ce){ce=!0,p();try{const e=await fetch($.exportUrl(l.sig,"3dtiles"));if(!e.ok){const i=await e.text();let s=i;try{s=JSON.parse(i).detail??i}catch{}L(`3D Tiles: ${s}`,"fehler",1e4);return}const n=/filename\*=UTF-8''([^;]+)/.exec(e.headers.get("content-disposition")??"")?.[1],t=document.createElement("a");t.href=URL.createObjectURL(await e.blob()),t.download=n?decodeURIComponent(n):"baugrundmodell_3dtiles.zip",t.click(),setTimeout(()=>URL.revokeObjectURL(t.href),1e4),L("3D Tiles exportiert (tileset.json + GLB, Höhen ellipsoidisch mit GCG2016).","ok")}finally{ce=!1,p()}}}function zi(){const e=l.z;return e.lage_modus==="koordinaten"&&e.viewer.epsg!==null&&On.has(e.viewer.epsg)?a`<button class="knopf" ?disabled=${ce} @click=${vi}>${ce?"3D Tiles werden erstellt …":"Baugrundmodell für Cesium (3D Tiles, ZIP)"}</button>${m("tiles3d")}`:a`<span class="knopf aus" title="Nur mit Lage nach Koordinaten in ETRS89/UTM">Baugrundmodell für Cesium (3D Tiles, ZIP)</span>`}const Bi={anzeige:"Anzeige",fachdaten:"Fachdaten",bewertungsdaten:"Bewertungsdaten"},yi=e=>e.split("-").reverse().join(".");function Si(e){return!e.bis||e.tage===null?e.regel:`bis ${yi(e.bis)} (${e.tage>0?`noch ${e.tage} Tage`:e.tage===0?"heute":"verstrichen"})`}function Gi(){const e=l.z.geoldg,n=e.zusammenfassung,t=(r,o)=>b([{op:"geoldg",[r]:o}],{leise:!0}),i=`${$.exportUrl(l.sig,"geoldg")}?organisation=${encodeURIComponent(le)}`,s=e.punkte.filter(r=>r.quelle==="protokoll").map(r=>r.titel.replace(/, falls durchgeführt$/,""));return a`
    <section class="abschnitt-flach geoldg">
      <h3>Geologischer Dienst (GeolDG) ${m("geoldg")}</h3>
      <div class="zeile">
        <label class="inline">Beginn <input type="date" aria-label="Beginn der Untersuchung" .value=${e.angaben.beginn}
          @change=${r=>t("beginn",r.target.value)}></label>
        <label class="inline">Abschluss <input type="date" aria-label="Abschluss der Untersuchung" .value=${e.angaben.abschluss}
          @change=${r=>t("abschluss",r.target.value)}></label>${m("geoldg_abschluss")}
      </div>
      <label class="inline"><input type="checkbox" aria-label="Auftraggeber ist eine Behörde" .checked=${e.angaben.behoerde}
        @change=${r=>t("behoerde",r.target.checked)}> Auftraggeber ist eine Behörde</label>
      <ul class="fristen">${e.fristen.map(r=>a`
        <li class=${r.tage!==null&&r.tage<0?"warn":""} data-frist=${r.id}><b>${Bi[r.id]}</b>
          <a href=${r.url} target="_blank" rel="noopener">${r.beleg}</a>: ${Si(r)}</li>`)}</ul>
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
    </section>`}let kn=!1;function Di(){const e=l.z,n=l.modell,t=n?.bericht,i=e.pruefstand,s=e.eincheckungen[e.eincheckungen.length-1],r=[["ifc","Baugrundmodell (IFC 4.3)"],["bericht","Prüfbericht (JSON)"]],o=[["einheiten","Einheiten-Vorlage (JSON)"],["extraktion","Extraktion (JSON)"],["eingabe","Modell-Eingabe mit Korrekturen (JSON)"],["projekt","Projektstand (JSON)"]],h=kn||!!(e.geoldg?.angaben.beginn||e.geoldg?.angaben.abschluss);return a`
    <div class="app-panel rechts">
      <section class="abschnitt-flach">
        <h3>Modell</h3>
        ${e.reifegrad.stufe!=="Gutachten"?a`<p class=${`reife ${e.reifegrad.stufe==="Vorerkundung"?"vorerkundung":"gemischt"}`}>
          <b>${e.reifegrad.stufe}</b> – ${e.reifegrad.stufe==="Vorerkundung"?"Bohrungen aus Datenbanken der Länder, kein Gutachten: eine erste Vorstellung für die Planung der Erkundung.":Object.entries(e.reifegrad.anzahl).map(([d,c])=>`${c} ${d}`).join(", ")+": Bohrungen ohne Gutachten sind nicht gegen ein PDF geprüft."}
          ${m("reifegrad")}</p>`:u}
        ${l.rechnet?a`<p><span class="kreisel klein"></span> wird gerechnet …</p>`:u}
        ${n?.fehler?a`<p class="warnung">Noch kein Modell: ${n.fehler}</p>
          <button class="link" @click=${()=>H("lage")}>→ Lage setzen</button>`:u}
        ${t?a`
          <ul class="kennzahlen">
            <li><b>${t.einheiten.length}</b> Einheiten</li>
            <li><b>${t.bohrungen.length}</b> Bohrungen im Modell</li>
            <li class=${t.epsg?"":"warn"}>${t.epsg?`EPSG:${t.epsg}`:"lokales System"}</li>
            <li class=${t.pruefungen.alle_koerper_geschlossen?"ok":"warn"}>${t.pruefungen.alle_koerper_geschlossen?"Körper geschlossen":"Körper offen"}</li>
            <li class=${t.pruefungen.max_abweichung_an_bohrungen_m<.01?"ok":"warn"}>Abweichung an Bohrungen ${t.pruefungen.max_abweichung_an_bohrungen_m.toFixed(3)} m</li>
          </ul>`:u}
        <div class="zeile">
          <label class="inline"><input type="checkbox" .checked=${e.auto} @change=${d=>b([{op:"auto",wert:d.target.checked}],{leise:!0})}>
            automatisch nachführen</label>${m("auto")}
          <span class="fueller"></span>
          <button ?disabled=${l.rechnet} @click=${()=>Un()}>Neu rechnen</button>
        </div>
      </section>

      <section class="abschnitt-flach">
        <h3>Prüfstand ${m("pruefstand")}</h3>
        <div class="balken"><span>Bohrungen <b>${i.bohrungen[0]}/${i.bohrungen[1]}</b></span><progress max=${i.bohrungen[1]||1} value=${i.bohrungen[0]}></progress></div>
        <div class="balken"><span>Schichten <b>${i.schichten[0]}/${i.schichten[1]}</b></span><progress max=${i.schichten[1]||1} value=${i.schichten[0]}></progress></div>
        <p class="klein">${i.unklassifiziert_offen?a`<span class="warnung">⚠ ${i.unklassifiziert_offen} Schicht(en) nicht klassifiziert</span>
          <button class="link" @click=${()=>H("bohrungen")}>prüfen</button>`:a`<span class="ok">✓ keine offenen Warnungen</span>`}
          · ${i.korrigiert} korrigiert · ${i.manuelle_lage} Lagen manuell · ${i.entfernt} entfernt</p>
        <p class=${`klein ${s&&!e.seit_einchecken_geaendert?"ok":"warn"}`}>
          ${s?`Eingecheckt: ${e.eingecheckt}${e.seit_einchecken_geaendert?" · seitdem geändert":""}`:"noch nicht eingecheckt"}</p>
        <div class="zeile">
          <input class="breit" placeholder="Kommentar (z. B. BK1–BK5 mit Anlage 2 verglichen)" .value=${ye}
            @input=${d=>{ye=d.target.value}}>
        </div>
        <div class="zeile"><button class="primaer" @click=${ki}>✓ Stand einchecken</button>${m("einchecken")}</div>
        ${e.eincheckungen.length?a`
          <details class="protokoll"><summary>Protokoll (${e.eincheckungen.length})</summary>
            <ul>${[...e.eincheckungen].reverse().map(d=>a`
              <li><b>v${d.nr}</b> ${d.zeit} · ${d.stand.bohrungen[0]}/${d.stand.bohrungen[1]} Bohrungen, ${d.stand.schichten[0]}/${d.stand.schichten[1]} Schichten
                ${d.kommentar?a`<div class="leise klein">${d.kommentar}</div>`:u}</li>`)}</ul>
          </details>`:u}
      </section>

      <section class="abschnitt-flach">
        <h3>Export ${m("export")}</h3>
        <div class="export-liste">
          ${r.map(([d,c])=>a`<a class=${`knopf ${d==="ifc"?"primaer":""}`} href=${$.exportUrl(l.sig,d)}
            download>${c}</a>`)}
        </div>
      </section>

      <details class="erweitert" ?open=${h}
        @toggle=${d=>{kn=d.target.open}}>
        <summary>Erweitert <span class="leise klein">Exporte · Cesium · BoreholeML · GeolDG · Ground Analysis · Darstellung</span></summary>
        <section class="abschnitt-flach">
          <h3>Weitere Exporte</h3>
          <div class="export-liste">
            ${o.map(([d,c])=>a`<a class="knopf" href=${$.exportUrl(l.sig,d)} download>${c}</a>`)}
            ${zi()}
            ${wi()}
          </div>
        </section>
        ${Gi()}
        ${hi()}
        <section class="abschnitt-flach">
          <h3>Darstellung</h3>
          <label class="inline">Überhöhung ${m("ueberhoehung")}
            <select @change=${async d=>{const c=Number(d.target.value);await l.viewer?.ueberhoehen(c),await b([{op:"ueberhoehung",wert:c}],{leise:!0})}}>
              ${[1,2,5,10,20].map(d=>a`<option value=${d} .selected=${e.ueberhoehung===d}>${d}×</option>`)}
            </select></label>
        </section>
      </details>

      ${n&&(n.hinweise.length||n.nicht_im_modell.length)?a`
        <section class="abschnitt-flach">
          <h3>Hinweise</h3>
          ${n.nicht_im_modell.length?a`<p class="klein"><b>Nicht im Modell:</b> ${n.nicht_im_modell.map(d=>`${d.code} (${d.grund})`).join(", ")}</p>`:u}
          ${n.hinweise.map(d=>a`<p class="klein">ℹ ${d}</p>`)}
        </section>`:u}
    </div>`}const wn={gutachten:"",bohrungen:"Weiter: Lage",lage:"Weiter: Einheiten",einheiten:"Weiter: Modell",modell:""};function Mi(e){const n=l.z;if(!n)return"";const t=n.pruefstand;return e==="gutachten"?"ok":e==="bohrungen"?t.unklassifiziert_offen?"warn":t.bohrungen[0]===t.bohrungen[1]&&t.bohrungen[1]?"ok":"":e==="lage"?n.viewer.bohrungen.filter(s=>s.x===null).length?"warn":"ok":e==="einheiten"||e==="modell"?l.modell?.fehler?"warn":l.modell?.bericht?"ok":"":""}function _i(){const e=l.z;return a`
    <header class="kopf">
      <div class="marke" @click=${()=>H("gutachten")} title="Start">
        <span class="logo">⛰</span>
        <span><b>GroundTwin</b> · Baugrundmodell</span>
      </div>
      <nav class="schritte" aria-label="Schritte">
        ${pe.map(n=>{const t=n.id!=="gutachten"&&!e,i=Mi(n.id);return a`
            <button class=${`schritt-knopf ${l.schritt===n.id?"aktiv":""} ${i}`} ?disabled=${t}
              aria-current=${l.schritt===n.id?"step":"false"} @click=${()=>H(n.id)} title=${n.kurz}>
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
            <div class="menue-inhalt" @click=${Li}>
              <button @click=${()=>H("gutachten")}>Anderes Projekt öffnen</button>
              <button @click=${xi}>Alle Korrekturen verwerfen …</button>
              <a href="viewer.html" target="_blank" rel="noopener">Viewer allein öffnen</a>
              <a href="dienste.html" target="_blank" rel="noopener">Dienste der Länder (Werkzeug)</a>
              ${l.info?a`<a href=${l.info.quellcode} target="_blank" rel="noopener">Quellcode (${l.info.lizenz})</a>`:u}
            </div>
          </details>`:u}
      </div>
    </header>`}function Li(e){e.currentTarget.closest("details")?.removeAttribute("open")}document.addEventListener("click",e=>{for(const n of document.querySelectorAll("details.menue[open]"))n.contains(e.target)||n.removeAttribute("open")});async function xi(){if(!l.sig||!confirm("Alle Korrekturen, Lagen, Prüfhaken und Eincheckungen dieses Projekts verwerfen – auch übernommene Bohrungen der Länder, DGM und Gebäude? Der Name bleibt."))return;const e=await w(()=>$.zuruecksetzen(l.sig));e&&await X(l.sig,e.standort?"lage":"bohrungen")}function Ei(){if(l.schritt==="gutachten")return u;const e=pe.findIndex(s=>s.id===l.schritt),n=pe[e-1],t=pe[e+1],i=l.z?.pruefstand;return a`
    <footer class="fuss">
      ${n?a`<button @click=${()=>H(n.id)}>← ${n.titel}</button>`:u}
      <span class="fuss-status">${i?`${i.bohrungen[0]}/${i.bohrungen[1]} Bohrungen · ${i.schichten[0]}/${i.schichten[1]} Schichten geprüft`:""}
        ${i?.unklassifiziert_offen?a` · <span class="warnung">⚠ ${i.unklassifiziert_offen} nicht klassifiziert</span>`:u}</span>
      <span class="fueller"></span>
      ${t&&wn[l.schritt]?a`<button class="primaer" @click=${()=>H(t.id)}>${wn[l.schritt]} →</button>`:u}
    </footer>`}function Ni(){return l.schritt==="gutachten"||!l.z?st():l.schritt==="bohrungen"?St():l.schritt==="lage"?Yt():l.schritt==="einheiten"?$i():Di()}function Ai(){return a`
    ${_i()}
    <main class=${`inhalt schritt-${l.schritt}`}>
      <section id="schritt" class="schritt">${Ni()}</section>
    </main>
    ${Ei()}
    <div class="meldungen" aria-live="polite">
      ${l.meldungen.map(e=>a`<div class=${`meldung ${e.art}`}>${e.text}</div>`)}
    </div>
    ${l.beschaeftigt?a`<div class="beschaeftigt"><div class="kreisel"></div><span>${l.beschaeftigt}</span></div>`:u}`}const vn=document.getElementById("app");let Q=null;function Pi(){Hn(Ai(),vn);const e=vn.querySelector("main");Q||(Q=document.createElement("div"),Q.id="buehne",Q.className="buehne"),Q.parentElement!==e&&e.append(Q),document.body.dataset.schritt=l.schritt}Vn(Pi);async function Rn(){const[e,n,t]=location.hash.replace(/^#\/?/,"").split("/").map(decodeURIComponent);if(e&&e!==l.sig){if(await X(e,n||void 0),t&&l.schritt==="bohrungen"){const{bohrungWaehlen:i}=await Ae(async()=>{const{bohrungWaehlen:s}=await import("./store-CVGYfZHk.js").then(r=>r.k);return{bohrungWaehlen:s}},__vite__mapDeps([1,2]),import.meta.url);await i(t)}}else e||await H("gutachten")}window.addEventListener("hashchange",()=>void Rn());l.info=await w(()=>$.info())??null;p();await zn();await Rn();window.app=l;
