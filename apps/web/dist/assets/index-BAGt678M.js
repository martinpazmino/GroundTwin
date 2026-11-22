const __vite__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["./leaflet-CIGW-MKW.css","./store-Db7Mh03B.js","./preload-helper-Ct5FWWRu.js"])))=>i.map(i=>d[i]);
import"./viewer-C5b86ahh.js";import{_ as Ce}from"./preload-helper-Ct5FWWRu.js";/* empty css            */import{b as a,A as u,w as T,D as ut}from"./lit-element-BS0sz3Y2.js";import{a as k,S as s,n as m,v as w,m as A,o as se,p as Rn,b,s as ke,c as Te,d as tn,z as O,e as Oe,f as ct,g as C,h as dt,i as ht,j as Be}from"./store-Db7Mh03B.js";import{l as B,m as gt,k as cn}from"./lage-B6_kyRwu.js";import"./three.core-Dd2BBCN2.js";const In=a`<span class="ungeprueft" title="Adresse eingetragen, nicht gegen den Dienst geprüft">ungeprüft</span>`;function Vn(e,n="Dienste am Standort"){return a`<ul class="dienste klein" aria-label=${n}>${e.map(t=>a`<li class=${t.art}>
    ${t.url?a`<a href=${t.url} target="_blank" rel="noopener noreferrer">${t.text}</a>`:t.text}
    ${t.status==="ungeprueft"?In:u}</li>`)}</ul>`}function pt(e){if(!e?.length)return u;const n=[...new Set(e.map(t=>t.land).filter(t=>t!=="Deutschland"))];return a`<div class="portale" role="note">
    <p class="klein">Kein Datendienst mit Schichtdaten für ${n.length?n.join(", "):"diesen Ort"} – die Bohrungen im Portal ansehen:</p>
    <ul class="dienste klein" aria-label="Portale der Länder">${e.map(t=>a`<li>
      <a href=${t.url} target="_blank" rel="noopener noreferrer">${t.titel}</a> <span class="leise">(${t.land})</span>
      ${t.status==="ungeprueft"?In:u}
      ${t.hinweis?a`<div class="leise">${t.hinweis}</div>`:u}</li>`)}</ul>
  </div>`}const Ze={ocr:["OCR für Scans","Liest gescannte PDFs und Text, der nur als Linien gezeichnet ist (SHX). Langsamer; bei Vektor-PDFs nicht nötig."],beispiele:["Beispiele","Fertig ausgewertete Gutachten zum Ausprobieren. Echte Daten: Berlin (georeferenziert) und Talheim (ohne Koordinaten). Dazu Standorte ohne Gutachten, die zeigen, was die Länder liefern: Dortmund (NRW, Bohrungen mit Schichtdaten), Karlsruhe (Baden-Württemberg, Schichten oft ohne Petrographie) und Berlin (nur Kopfdaten: Gelände und Gebäude, kein Schichtenmodell). Die Bohrungen fragt der Schritt Lage auf Klick beim Land ab (Netz nötig)."],karte:["Karte","Eine Karte zum Orientieren: ein Klick setzt den Standort; Rechts- und Hochwert in ETRS89/UTM rechnet die App aus (Zone 32 westlich von 12° Ost, sonst 33) und sagt, was die Dienste der Länder dort liefern. Hintergrund basemap.de (amtlich, © GeoBasis-DE / BKG, CC BY 4.0) oder OpenStreetMap. Die Kacheln laden erst beim Öffnen – der Kartenausschnitt geht an diesen Server. Auf wenige Meter genau (Karte in WGS84): für eine Vorerkundung genug."],pruefstand:["Prüfstand","Wie viele Bohrungen und Schichten Sie geprüft haben. Eine Korrektur zählt als geprüft. Der Stand wird beim Einchecken festgehalten."],alle_pruefen:["Alle geprüft","Markiert alle Schichten aller Bohrungen im Modell als geprüft – nur wenn Sie alles mit dem Gutachten verglichen haben. Zurücknehmen ist jederzeit möglich."],warnung:["Warnung","Eine Schicht, deren Bodenart nicht erkannt wurde (unklassifiziert). Bodenart wählen, den Vorschlag nach Norm übernehmen oder die Schicht als geprüft markieren."],bodenart:["Bodenart","Klasse für das Modell; Farbe nach DIN 4023 (Kies gelb, Sand orange, Schluff oliv, Ton violett …). Gleiche Bodenarten werden zu Einheiten verbunden."],norm:["Deutung nach Norm","Die Beschreibung aus dem PDF gelesen nach DIN 4023 / DIN EN ISO 14688-1: Hauptanteil, Nebenanteile (schwach ' / stark ¯), Kurzzeichen, Bodengruppe nach DIN 18196 (nur wenn genannt), Konsistenz. Steht auch im IFC (CPset_Bodenansprache)."],vorschlag:["Vorschlag nach Norm","Für eine unklassifizierte Schicht schlägt die Normen-Datenbank eine Bodenart aus der Beschreibung vor. Sie wird nur übernommen, wenn Sie klicken; danach gilt die Schicht als korrigiert."],geprueft:["Geprüft","Haken: Schicht mit dem Gutachten verglichen. Steht im IFC (Geprueft) und im Prüfstand."],tiefe:["Tiefe","Ober- und Unterkante in m unter Geländeoberkante (GOK). Geändertes wird als korrigiert markiert."],gok:["GOK","Ansatzhöhe der Bohrung in m NHN. Aus dem PDF oder hier eingetragen (manuell). Ohne GOK bei allen Bohrungen rechnet das Modell relativ (Gelände = 0 m)."],koordinaten:["Koordinaten","Rechts- und Hochwert der Bohrung; leer lassen, wenn die Lage im Schritt Lage auf dem Plan gesetzt wird."],entfernen:["Entfernen","Die Bohrung kommt nicht ins Modell (sie bleibt in der Liste unter „Entfernt“ und lässt sich wiederherstellen)."],quelle:["Quelle im PDF","Die Seite des Gutachtens, auf der die Bohrung erkannt wurde; der Rahmen zeigt die gewählte Schicht."],lage_art:["Art der Lage","Koordinaten: Bohrungen mit Rechts-/Hochwert (aus dem PDF, eingetragen oder auf dem Lageplan gesetzt). Reihe: ohne Koordinaten nebeneinander mit Abständen bzw. Stationen aus dem Längsschnitt."],unterlage:["Unterlage","Lageplan (Draufsicht) oder Längsschnitt (Seitenansicht) als PDF. Er liegt im Viewer unter den Bohrungen; nach dem Kalibrieren werden die Bohrungen daraufgezogen."],massstab:["Maßstab","Zwei Punkte auf dem Plan anklicken, deren Abstand Sie kennen (Maßstabsleiste, Bemaßung, zwei Bohrungen), und die wahre Länge in m eintragen. Oder den Maßstab 1:n direkt angeben."],bezug:["Bezugspunkt","Ein Punkt im Plan mit bekannter Koordinate (Koordinatenkreuz, Bohrung mit Koordinaten): anklicken und Rechts-/Hochwert eintragen – im Längsschnitt Station und Höhe NHN."],drehung:["Drehung","Winkel, um den der Plan gegen Norden gedreht ist (gegen den Uhrzeigersinn positiv). Nordpfeil nach oben = 0°; Nordpfeil 10° nach links geneigt = 10°."],hoehe:["Höhenmaßstab","Längsschnitte sind oft überhöht (z. B. Länge 1:500, Höhe 1:100). Ohne Angabe gilt der Längenmaßstab."],epsg:["Koordinatensystem (EPSG)","System der Rechts-/Hochwerte aus der Liste wählen: in Deutschland meist ETRS89 / UTM 32N (25832), im Osten 33N (25833), ältere Pläne Gauß-Krüger (Rechtswert 7-stellig, erste Ziffer = Zone); dazu Schweiz und Österreich. Passen die Werte nicht zum System (Ziffernzahl, Zonenkennung), erscheint ein Hinweis. Steht im IFC (IfcMapConversion)."],sperren:["Sperren","Schloss zu: der Plan liegt fest und ändert sich nicht mehr; jetzt die Bohrungen ziehen. Auf dem Lageplan nur in x/y, im Längsschnitt entlang der Station – in der Höhe nur, wenn das PDF keine GOK hat."],deckkraft:["Deckkraft","Wie stark der Plan die Szene überdeckt."],ohne_lage:["Ohne Lage","Bohrungen ohne Koordinaten: anklicken und dann in den gesperrten Plan klicken (Punkte setzen) – oder mit der Maus aus der Liste auf den Plan ziehen."],punkte:["Punkte setzen","Modus an, dann in den gesperrten Lageplan klicken: die gewählte Bohrung bekommt die Lage, danach ist die nächste ohne Lage dran (oder einen Chip anklicken). Mit „freien Punkt“ entsteht ein Punkt ◆, den Sie in der Liste einer Bohrung zuordnen. ✕ löscht einen Punkt bzw. die gesetzte Lage – im Viewer ebenso: Marke anklicken, Entf. Esc beendet den Modus."],reihe:["Reihe","Bohrungen in einer Linie. Abstand zum Vorgänger je Bohrung eintragen (BK1 → BK2 10 m, BK2 → BK3 15 m) oder eine Station; ohne Eintrag gilt der Standardabstand. Reihenfolge mit den Pfeilen."],standardabstand:["Standardabstand","Abstand zwischen Bohrungen, für die nichts eingetragen ist (nur zur Anschauung, im Modell als schematisch markiert)."],boreholeml:["BoreholeML","Austauschformat der Geologischen Dienste der Länder (Version 3.2). Exportiert werden nur vollständig geprüfte Bohrungen mit Lage in ETRS89/UTM und GOK in m NHN; Petrographie, Genese, Konsistenz, Lagerung, Kalk und Feuchte über die amtlichen Codelisten, die Beschreibung aus dem Gutachten im Klartext. Die Organisation steht als Absender in der Datei. Welche Bohrungen ausgelassen wurden und warum, steht oben in der Datei. Umgekehrt lassen sich BoreholeML-Dateien wie ein Gutachten hochladen (Bohrungen der Länder)."],sgd:["Bohrungen der Länder","Bohrungen aus den Datenbanken der Geologischen Dienste um die Mitte des Projekts: Berlin und Brandenburg mit Kopfdaten und dem Schichtenverzeichnis als Grafik, NRW, Baden-Württemberg und Hamburg in BoreholeML mit den freigegebenen Schichtdaten. Abgefragt wird nur auf Klick – die Anfrage sendet die Lage des Projekts an den Dienst. Bohrungen des Gutachtens, die auch beim Land liegen, zeigen die Abweichung von Lage und GOK (Gegenprobe). Übernommene Bohrungen tragen Quelle, Lizenz und Datum, erscheinen als Raute und gehen nicht in den BoreholeML-Export. Für Länder ohne eigenen Dienst zeigen die BGR und Bremen über WMS, wo gebohrt wurde: nur als Hinweis mit Lage, GOK und Teufe, nie im Modell. Länder ohne Datendienst nennt die Abfrage außerdem mit dem Link zu ihrem Portal und der Bohrpunktkarte der BGR („ungeprüft“: Adresse eingetragen, nicht gegen den Dienst getestet). Welches Land: aus den Ländergrenzen (VG2500 des BKG); an einer Grenze beide. Die Adressen pflegt das Werkzeug „Dienste der Länder“ (Menü ⋯)."],gelaende:["Gelände (DGM)","Digitales Geländemodell der Vermessungsverwaltung (Open Data, meist DGM1 mit 1 m Raster) für das Baufeld herunterladen und hier laden: XYZ, ASCII-Raster oder GeoTIFF, mehrere Kacheln auch als ZIP. Die App vergleicht die GOK aus dem PDF mit dem Gelände: liegen alle Bohrungen gleich viel höher oder tiefer, stimmen Lage, EPSG oder Höhenbezug nicht. Fehlende GOK schlägt sie vor – übernommen wird nur auf Klick, markiert als „DGM“ (auch im IFC)."],dgm_land:["DGM vom Land","Holt das DGM1 (1 m) für den Ausschnitt um die Bohrungen plus Rand direkt beim Dienst des Landes (WCS): bisher Brandenburg mit Berlin und NRW. Nur auf Klick – die Anfrage sendet den Ausschnitt an den Dienst. Quelle, Lizenz und Namensnennung bleiben am DGM und gehen ins IFC. Baden-Württemberg liefert über seinen Dienst nur ganze Meter, Bayern hat keinen freien Dienst: dort die DGM1-Kacheln als Datei laden."],gebaeude:["Gebäude (LoD2)","3D-Gebäudemodelle LoD2 der Länder als Umgebung des Baugrundmodells: Berlin, Brandenburg und NRW geben sie als CityGML-Kacheln von 1 × 1 km heraus, in ETRS89/UTM mit Höhen in m NHN – derselbe Rahmen wie das Modell. Nur auf Klick werden die Kacheln um die Bohrungen (plus Rand) geladen; Gebäude, deren Grundriss den Ausschnitt berührt, kommen ins IFC (IfcBuildingElementProxy mit Wänden und Dach, Quelle und Lizenz je Gebäude) und in den Viewer (Knopf „Gebäude“). Bestand, nicht erkundet."],standort:["Standort ohne Gutachten","Ein Projekt an einem Punkt (ETRS89/UTM, aus der Karte oder eingetragen): im Schritt Lage fragt es die Bohrungen der Länder um den Punkt ab, holt das DGM und die Gebäude – ein Lageplan ist nicht nötig, der Punkt ist schon georeferenziert. Übernommene Bohrungen mit Schichtdaten (NRW, Baden-Württemberg) ergeben ein Modell – eine Vorerkundung: Archivdaten unbekannter Güte, ohne Sondierungen, oft alt oder weit weg. Kommt später das Gutachten, entsteht ein neues Projekt, das die Bohrungen der Länder, DGM und Gebäude mitnimmt (gemischt)."],reifegrad:["Reifegrad","Woraus das Modell besteht: Gutachten (nur Bohrungen aus dem PDF), Vorerkundung (nur Bohrungen aus Datenbanken der Länder oder BoreholeML-Dateien) oder gemischt. Er steht in der App, im Viewer, im Prüfbericht und im IFC (CPset_Baugrundmodell.Reifegrad); jede Bohrung trägt ihre Herkunft mit Quelle und Lizenz (CPset_Herkunft)."],bodenkennwerte:["Bodenkennwerte aus dem Gutachten","Die Kennwert-Tabellen des Berichts (Wichte, Wichte unter Auftrieb, Reibungswinkel, Kohäsion, undränierte Kohäsion, Steifemodul) werden beim Extrahieren gelesen: als Tabelle mit Spalten oder als Liste je Schicht/Homogenbereich, nur aus der Textebene (nicht aus Scans). Je Zeile stehen Bezeichnung, Bodengruppen, Seite und die Werte; ein Wert außerhalb der üblichen Spanne trägt ⚑, was keine Zahl ist (z. B. Es = 18√t), bleibt Text. Der Vorschlag ordnet einer Einheit die Zeile zu, deren Bezeichnung den Namen oder die Bodenart der Einheit nennt (sonst die Bodengruppe); passen mehrere gleich gut, gibt es keinen Vorschlag. Übernommen wird erst mit einem Klick, danach je Einheit änderbar. Im IFC trägt die Einheit CPset_Bodenkennwerte_Gutachten mit <Kennwert>_min/_max (Namensregel DAUB Teil 3), Seite und Bezeichnung. Es sind Angaben des Gutachters: GroundTwin setzt keine charakteristischen Werte fest."],homogenbereiche:["Homogenbereiche (VOB/C)","Ein Homogenbereich fasst Boden zusammen, der sich für ein Gewerk gleich verhält; die ATV der VOB/C (z. B. DIN 18300 Erdarbeiten) verlangen je Bereich bestimmte Kennwerte. Dieselbe Einheit kann für verschiedene Gewerke in verschiedenen Bereichen liegen: Gewerk wählen, je Einheit einen Bereich eintragen (gleicher Name = gleicher Bereich, leer = keiner). Die Liste zeigt die Kennwerte, die die ATV verlangt (Matrix nach Abbildung 8, Quelle in docs/28; gegen die geltende ATV prüfen). Im IFC trägt jede Einheit und jede Bodenschicht ein Pset CPset_Homogenbereich_<ATV>; liegt eine Schicht an einer Bohrung in zwei Einheiten, nennt es beide Bereiche. „IFC-Modell: Homogenbereiche“ schreibt das Modell aus den Bereichen (dieselben Körper, je Bereich ein Stratum); Einheiten ohne Bereich bleiben einzeln und markiert. Ohne Zuordnung zeigt der Abschnitt einen Vorschlag für die gewählte ATV: Einheiten, die sich für dieses Gewerk gleich verhalten, in einem Bereich, mit Begründung je Bereich. Wie fein er trennt, folgt aus den Kennwerten der ATV: wenige (z. B. DIN 18300 GK 1, DIN 18320) – nur nichtbindig, bindig, organisch, anthropogen, befestigt (Beton, Asphalt, Pflaster), Fels; sonst dazu die Bodengruppe DIN 18196, wenn mindestens die Hälfte der Schichten sie nennt (sonst die Hauptbodenart); verlangt die ATV Mineralogie oder Abrasivität (z. B. DIN 18312, 18319, 18324) – dazu Steine/Blöcke getrennt. Nicht klassifizierte Einheiten bleiben einzeln. Übernommen wird der Vorschlag erst mit einem Klick und ist danach je Einheit änderbar; zuordnen entscheidet der Planer."],hb_kennwerte:["Kennwerte aus den Beschreibungen","Je Homogenbereich (ohne Zuordnung: je Einheit) steht hier, was die Schichtbeschreibungen der Bohrprofile zu den verlangten Kennwerten sagen: ortsübliche Bezeichnung (Benennung), Konsistenz, Lagerungsdichte, Kalkgehalt, Bodengruppe DIN 18196, Plastizität (aus der Bodengruppe), genannte Steine, Blöcke und organische Anteile – jeweils mit dem Anteil der Schichten, die es nennen (z. B. „steif (5/8)“). Das ist Ansprache, kein Laborwert: Korngrößenverteilung, Massenanteile, Dichte, undrainierte Scherfestigkeit, Wassergehalt, Plastizitäts- und Konsistenzzahl, Durchlässigkeit, Abrasivität stehen nur im Text oder in den Anlagen des Gutachtens und bleiben „offen“. Im IFC stehen die Angaben als Kennwert_… und die offenen als Kennwerte_offen im Pset des Bereichs."],grundwasser:["Grundwasserfläche","Eine Fläche durch die gemessenen Wasserstände der Bohrungen (GOK − Tiefe), mit derselben Interpolation wie das Modell; sie geht nicht ins IFC und ändert das Modell nicht. Trockene Bohrungen („kein Grundwasser“) sind Daten: liegt die Fläche dort über der Endteufe, steht der Widerspruch dabei. Gemeldet werden auch eine Fläche über dem Gelände (gespanntes Wasser oder Stände verschiedener Tage) und mehrere Stände in einer Bohrung (der höchste gilt). Ab vier Ständen zeigt eine Kreuzprobe, wie gut sich der Wasserstand zwischen den Bohrungen vorhersagen lässt. Bohrzeit-Wasserstände sind Momentaufnahmen: kein Bemessungswasserstand."],orientierung:["Orientierung je Einheit","Nur für die implizite Methode (GemPy). Ohne Eingabe folgt die Orientierung einer Unterkante aus ihren Kontakten: Ebene durch die Bohrungen, entlang einer Trasse in Linienrichtung, steiler als 30° oder mit weniger als drei Kontakten horizontal. Ist das Einfallen bekannt (Gutachten, geologische Karte, Aufschluss), hier Fallrichtung (Azimut von Nord im Uhrzeigersinn, 0–360°) und Fallwinkel (0–80°) eingeben; dann gilt die Eingabe, auch in der Kreuzprobe, und Bericht und IFC nennen sie als Quelle „Eingabe“. An den Bohrungen bleibt jede Grenze exakt; passt die Eingabe nicht zu den Kontakten (mehr als 5 cm daneben), gilt für diese Fläche der Spline mit Hinweis. Leere Felder = aus den Kontakten."],gelaende_dgm:["Gelände aus dem DGM","Mit DGM folgt die Oberkante des Modells dem Gelände statt der Interpolation zwischen den GOK. An jeder Bohrung bleibt sie genau auf der GOK; deren Abweichung vom DGM klingt bis zur Reichweite (halber Bohrabstand, höchstens 25 m) ab. Im IFC liegt das Gelände um das Modell als IfcGeographicElement (TERRAIN), im Viewer mit dem Knopf „Gelände“ ein- und ausblendbar. Deckt das DGM das Modellgebiet nicht ganz ab, bleibt die Oberkante aus den GOK (mit Hinweis)."],dgm_epsg:["System der DGM-Datei","XYZ- und ASCII-Dateien enthalten kein Koordinatensystem: das System der Kacheln wählen (meist dasselbe wie das Projekt, z. B. 25832). Ein GeoTIFF bringt es selbst mit."],durchmesser:["Durchmesser","Dicke der Bohrsäulen im Viewer und im IFC (Darstellung, nicht der Bohrdurchmesser im Feld). Automatisch wächst er mit der Modellgröße, damit Säulen auf langen Trassen sichtbar bleiben."],einheiten:["Einheiten","Modelleinheiten verbinden gleiche Bodenarten zwischen den Bohrungen (Sand 1, Kies, Sand 2). Umbenennen oder Bodenarten zusammenlegen (z. B. „Sand, Kies“ als eine Einheit); Reihenfolge von oben nach unten."],analyse:["Ground Analysis","Wie weit trägt das Modell zwischen den Bohrungen? Die Kreuzprobe rechnet das Modell ohne je eine Bohrung und vergleicht seine Vorhersage mit ihr (mittlerer Fehler der Schichtgrenzen, für IDW und Spline). Die Unsicherheit verbindet die Messung der Grenzen (± 0,10 m, Monte Carlo) mit diesem Fehler über den Abstand zur nächsten Bohrung. Liest nur das Modell, ändert nichts. Mindestens 3 Bohrungen."],erkundung:["Erkundungsvorschlag","Punkte, an denen eine weitere Bohrung das Modell am meisten verbessert: wo die Unterkanten am stärksten streuen und wo unklar ist, wie weit eine Einheit reicht (Linse, Rinne). Am Beispiel einer Rinne zwischen den Bohrungen senkten zwei Bohrungen an den vorgeschlagenen Stellen den Fehler stärker als zwei zufällige; eine andere Interpolation half dort nicht (docs/27). Ein Vorschlag, keine Planung."],virtuell:["Virtuelle Bohrung","Was das Modell an einem Punkt erwartet: Einheiten mit Tiefen und der Streuung jeder Unterkante (± σ, 95 % etwa ± 2 σ). Eine Vorhersage aus den Nachbarbohrungen, keine Messung."],methode:["Interpolation","IDW: gewichtetes Mittel der Nachbarbohrungen, ruhig und sicher. Dünnplatten-Spline: glatte Flächen mit Trend, gut bei geneigten Schichten. Implizit (GemPy, wenn installiert): je Fläche ein Skalarfeld in 3D mit einer Orientierung aus den Kontakten (Ebene, sonst horizontal; steht im Bericht); langsamer, exakt an den Bohrungen; eine gefaltete Fläche rechnet der Spline (mit Hinweis). Welche Methode die Bohrungen am besten vorhersagt, zeigt die Ground Analysis."],puffer:["Puffer","Wie weit das Modell über die Bohrungen hinausreicht. Automatisch: halber Bohrabstand (5–100 m)."],raster:["Raster","Maschenweite der Schichtflächen. Automatisch: Gebietsgröße/40, bei großen Modellen gröber (höchstens 30 000 Knoten)."],basis:["Modellbasis","Unterkante des Modells in m NHN. Automatisch: tiefste Endteufe."],gok_relativ:["Fehlende GOK","Hat keine Bohrung eine GOK, rechnet das Modell relativ (Gelände = 0 m) – markiert im IFC."],auto:["Automatisch nachführen","Jede Änderung (Tabelle, Lage, Einheiten) rechnet das Modell sofort neu."],einchecken:["Einchecken","Hält den Prüfstand fest (Zeit, Zähler, Fingerabdruck des Modells, Kommentar). Das exportierte IFC trägt ihn (CPset_Baugrundmodell.Pruefstand)."],tiles3d:["3D Tiles für Cesium","Das Baugrundmodell als 3D Tiles 1.1 (tileset.json und glTF) für CesiumJS, Cesium for Unreal oder QGIS 3D: Baugrundmodell, Gelände und Gebäude je eine Kachel. Jeder Punkt wird exakt aus ETRS89/UTM umgerechnet, die Höhen ellipsoidisch mit dem Quasigeoid GCG2016 des BKG (CC BY 4.0; beim ersten Export einmal 1 MB geladen). ETRS89 ist nicht in WGS84/ITRF überführt (rund 0,9 m). Quellen und Lizenzen stehen in LIESMICH.txt."],geoldg:["Geologiedatengesetz (GeolDG)","Wer bohrt oder bohren lässt, muss die Untersuchung beim Geologischen Dienst des Landes anzeigen und die Daten übermitteln: Anzeige spätestens zwei Wochen vor Beginn (§ 8), Fachdaten wie das Schichtenverzeichnis spätestens drei Monate nach Abschluss (§ 9), Bewertungsdaten wie Gutachten und räumliche Modelle mit Dokumentation auf Verlangen (§ 10). Die Liste zeigt je Bohrung, was GroundTwin liefert (Lage, GOK, Endteufe, geprüfte Schichten) und was aus dem Bohrprotokoll kommt (Bohrverfahren, Ausbau, Proben, Messungen, Labor). Das Paket enthält BoreholeML, IFC, Prüfbericht, Modelldokumentation und eine Prüfliste zum Ergänzen. Hilfe, keine Rechtsberatung: Form und Weg legt die zuständige Behörde fest."],geoldg_abschluss:["Abschluss der Untersuchung","Die Untersuchung gilt mit Ablauf der Dauer als abgeschlossen, die in der Anzeige angegeben wurde – außer eine Fortdauer wurde rechtzeitig angezeigt (§ 15 Abs. 1). Ab dann laufen drei Monate für die Fachdaten; ist eine Behörde verpflichtet, etwa als Auftraggeber, sechs Monate für die Bewertungsdaten (§ 10 Abs. 2 Satz 2). Die Daten bleiben im Projekt."],export:["Export","IFC 4.3 mit Prüfstand, Bodenansprache je Schicht und Beschreibungen je Einheit; dazu Prüfbericht und die Daten als JSON."],sondierungen:["Sondierungen","Ramm- (DPH, N10 je 10 cm) und Drucksondierungen (CPT, q_c/f_s) aus dem Gutachten. Die Werte bleiben, wie sie im PDF stehen; gescannte Diagramme ohne sichere Achse liefern nur Code und Seite. GOK aus dem PDF oder eingeben, Lage eingeben oder auf dem gesperrten Lageplan setzen."],ueberhoehung:["Überhöhung","Höhen im Viewer mal Faktor, damit dünne Schichten sichtbar werden. Die Koordinaten bleiben echt."]};let j=null,qe=null;function xe(){j?.remove(),j=null,qe=null}function mt(e,n){e.preventDefault(),e.stopPropagation();const t=e.currentTarget;if(qe===t){xe();return}xe();const[i,l]=Ze[n];j=document.createElement("div"),j.className="hilfe-blase",j.setAttribute("role","tooltip"),j.innerHTML="<strong></strong><p></p>",j.querySelector("strong").textContent=i,j.querySelector("p").textContent=l,document.body.append(j);const r=t.getBoundingClientRect(),o=j.getBoundingClientRect(),d=Math.min(Math.max(8,r.left+r.width/2-o.width/2),window.innerWidth-o.width-8),h=r.bottom+8+o.height>window.innerHeight?r.top-o.height-8:r.bottom+8;Object.assign(j.style,{left:`${d}px`,top:`${h}px`}),qe=t}document.addEventListener("click",e=>{j&&!j.contains(e.target)&&xe()});document.addEventListener("keydown",e=>{e.key==="Escape"&&xe()});const p=e=>a`<button type="button" class="hilfe" title=${Ze[e][0]} aria-label=${`Hilfe: ${Ze[e][0]}`}
    @click=${n=>mt(n,e)}>?</button>`,bt="https://sgx.geodatenzentrum.de/wmts_basemapde/tile/1.0.0/de_basemapde_web_raster_farbe/default/GLOBAL_WEBMERCATOR/{z}/{y}/{x}.png",$t="https://tile.openstreetmap.org/{z}/{x}/{y}.png",dn=[51.16,10.45];let le=null;const we=e=>e.replace(/[&<>"]/g,n=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[n]),hn=e=>e.toLocaleString("de-DE",{minimumFractionDigits:1,maximumFractionDigits:1});async function ft(){const[{default:e}]=await Promise.all([Ce(()=>import("./leaflet-src-7ah4FPQk.js").then(n=>n.l),[],import.meta.url),Ce(()=>Promise.resolve({}),__vite__mapDeps([0]),import.meta.url)]);return new Promise(n=>{const t=document.createElement("dialog");t.className="karte-dialog",t.setAttribute("aria-label","Standort auf der Karte wählen"),t.innerHTML=`
      <header><strong>Standort auf der Karte wählen</strong>
        <button type="button" class="symbol schliessen" aria-label="Karte schließen">✕</button></header>
      <div class="karte-flaeche"></div>
      <footer>
        <div class="karte-info klein" aria-live="polite">In die Karte klicken: der Punkt wird der Standort (zum Orientieren,
          auf wenige Meter genau). Mausrad zoomt, Ziehen verschiebt.</div>
        <div class="zeile"><span class="fueller"></span>
          <button type="button" class="abbrechen">Abbrechen</button>
          <button type="button" class="primaer uebernehmen" disabled>Punkt übernehmen</button></div>
      </footer>`,document.body.append(t),t.showModal();const i=t.querySelector(".karte-info"),l=t.querySelector(".uebernehmen"),r=e.map(t.querySelector(".karte-flaeche"),{zoomControl:!0,attributionControl:!0}).setView(le?[le.breite,le.laenge]:dn,le?.zoom??6),o=new Date().getFullYear(),d=e.tileLayer(bt,{maxZoom:18,attribution:`© <a href="https://basemap.de" target="_blank" rel="noopener">GeoBasis-DE / BKG (${o})</a> <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>`}).addTo(r),h=e.tileLayer($t,{maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap-Mitwirkende</a>'});e.control.layers({"basemap.de (BKG)":d,OpenStreetMap:h},{},{position:"topright"}).addTo(r),e.control.scale({imperial:!1}).addTo(r);const c=e.circleMarker(dn,{radius:8,color:"#10210a",weight:2,fillColor:"#a2c513",fillOpacity:.95});let v=null,g=0;r.on("click",async S=>{const $=++g;c.setLatLng(S.latlng).addTo(r),v=null,l.disabled=!0,i.textContent="wird umgerechnet …";try{const f=await k.standortPunkt(Number(S.latlng.lng.toFixed(7)),Number(S.latlng.lat.toFixed(7)));if($!==g)return;v=f,l.disabled=!1,i.innerHTML=`<b>Rechtswert ${hn(f.x)} · Hochwert ${hn(f.y)} · EPSG:${f.epsg}</b>
          <ul class="dienste">${f.dienste.map(x=>`<li class="${x.art}">${/^https?:\/\//.test(x.url??"")?`<a href="${we(x.url)}" target="_blank" rel="noopener noreferrer">${we(x.text)}</a>`:we(x.text)}${x.status==="ungeprueft"?' <span class="ungeprueft">ungeprüft</span>':""}</li>`).join("")}</ul>
          <span class="leise">Das Land aus den Ländergrenzen (VG2500 des BKG, auf rund 150 m); Portale als Link.</span>`}catch(f){if($!==g)return;i.innerHTML=`<span class="warnung">${we(f.message)}</span>`}});const z=S=>{const $=r.getCenter();le=S?{laenge:S.laenge,breite:S.breite,zoom:Math.max(r.getZoom(),14)}:{laenge:$.lng,breite:$.lat,zoom:r.getZoom()},r.remove(),t.close(),t.remove(),n(S)};t.querySelector(".schliessen").addEventListener("click",()=>z(null)),t.querySelector(".abbrechen").addEventListener("click",()=>z(null)),l.addEventListener("click",()=>z(v)),t.addEventListener("cancel",S=>{S.preventDefault(),z(null)}),requestAnimationFrame(()=>r.invalidateSize())})}let H=[],Je=!0,ve=!1;const M={x:"",y:"",epsg:25832,name:""};let re=null;const kt=[[25832,"ETRS89 / UTM 32N"],[25833,"ETRS89 / UTM 33N"],[4647,"ETRS89 / UTM 32N (zE-N)"],[5650,"ETRS89 / UTM 33N (zE-N)"]];async function Wn(e){for(;;){const n=await w(()=>k.auftrag(e));if(!n)return;if(s.auftrag=n,m(),n.fertig){s.auftrag=null;for(const t of n.fehler)A(t,"fehler",1e4);n.projekt?(H=[],await se(n.projekt,"bohrungen")):m();return}await new Promise(t=>setTimeout(t,600))}}const Un=()=>s.z?.standort?s.sig:"";async function wt(){if(!H.length)return;const e=await w(()=>k.gutachten(H,Je&&!!s.info?.ocr,Un()));e&&await Wn(e.id)}async function vt(){const e=Number(M.x.replace(",",".")),n=Number(M.y.replace(",","."));if(!Number.isFinite(e)||!Number.isFinite(n)||!M.x||!M.y){A("Rechtswert und Hochwert als Zahlen eingeben.","warn");return}const t=await w(()=>k.standort(e,n,M.epsg,M.name),"Standort wird angelegt …");t&&(await se(t.projekt,t.vorhanden?void 0:"lage"),t.vorhanden&&A(`Den Standort gibt es schon: „${s.z?.name}“ geöffnet.`))}async function zt(){let e=null;try{e=await ft()}catch(n){A(`Karte: ${n.message}`,"fehler",8e3)}e&&(M.x=String(e.x),M.y=String(e.y),M.epsg=e.epsg,re=e.dienste,m())}function Bt(){const e=(t,i,l)=>a`
    <label class="feld"><span>${i}</span><input type="text" inputmode=${t==="name"?"text":"decimal"}
      aria-label=${i} placeholder=${l} .value=${M[t]} @input=${r=>{M[t]=r.target.value,t!=="name"&&re&&(re=null),m()}}></label>`,n=!!(M.x.trim()&&M.y.trim());return a`
    <section class="weg" aria-labelledby="weg-standort">
      <div class="weg-symbol" aria-hidden="true">◎</div>
      <h2 id="weg-standort">Standort</h2>
      <p class="weg-text">Noch kein Gutachten? Ein Punkt auf der Karte genügt: Bohrungen der Länder rund um den Punkt –
        eine <b>Vorerkundung</b>, kein Ersatz für das Gutachten. ${p("standort")}</p>
      <button class=${n?"":"primaer gross-knopf"} @click=${zt}>🗺 Auf der Karte wählen</button>
      ${n?a`<div class="punkt-wahl">
        <p class="klein"><b>${M.x} / ${M.y}</b> · EPSG:${M.epsg}</p>
        ${re?Vn(re):u}
        ${e("name","Name (frei)","z. B. Marl Nord")}
        <button class="primaer gross-knopf" @click=${vt}>Projekt am Standort anlegen →</button>
      </div>`:u}
      <details class="still">
        <summary>Koordinaten eingeben</summary>
        <div class="raster-2">
          ${e("x","Rechtswert","z. B. 368130")}
          ${e("y","Hochwert","z. B. 5724400")}
          <label class="feld"><span>System</span>
            <select aria-label="System des Standorts" @change=${t=>{M.epsg=Number(t.target.value),re=null,m()}}>
              ${kt.map(([t,i])=>a`<option value=${t} ?selected=${M.epsg===t}>${t} · ${i}</option>`)}
            </select></label>
        </div>
        <p class="leise klein">ETRS89/UTM, nur Deutschland. ${p("karte")}</p>
      </details>
    </section>`}async function gn(e){const n=await w(()=>k.beispiel(e),"Beispiel wird geöffnet …");n?.projekt?await se(n.projekt,n.schritt??"bohrungen"):n?.auftrag&&await Wn(n.auftrag)}function pn(e){H=[...e??[]].filter(n=>/\.(pdf|json|xml)$/i.test(n.name)),e?.length&&!H.length&&A("Bitte PDF-Dateien wählen (oder eine Extraktion als JSON, Bohrungen als BoreholeML).","warn"),m()}async function yt(e,n){confirm(`Projekt „${n}“ mit allen Korrekturen löschen? Das Gutachten selbst bleibt unberührt.`)&&(await w(()=>k.loeschen(e)),await Rn())}function St(){const e=s.auftrag,n=!!s.info?.ocr;return a`
    <section class="weg" aria-labelledby="weg-gutachten">
      <div class="weg-symbol" aria-hidden="true">⇪</div>
      <h2 id="weg-gutachten">Gutachten</h2>
      <p class="weg-text">Das Bodengutachten als PDF – Vektor oder Scan. Die Bohrungen werden erkannt; Sie prüfen sie,
        sehen sie in 3D und vergleichen sie mit den Bohrungen der Länder.</p>
      ${Un()?a`<p class="hinweis-standort">Zum Standort <b>${s.z.name}</b>: Bohrungen der Länder (mit Prüfstand),
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
        <label class=${`ablage ${ve?"ueber":""} ${H.length?"bereit":""}`}
          @dragover=${t=>{t.preventDefault(),ve=!0,m()}}
          @dragleave=${()=>{ve=!1,m()}}
          @drop=${t=>{t.preventDefault(),ve=!1,pn(t.dataTransfer?.files)}}>
          <input type="file" accept=".pdf,application/pdf,.json,application/json,.xml,application/xml,text/xml" multiple @change=${t=>pn(t.target.files)}>
          <strong>${H.length?H.map(t=>t.name).join(", "):"PDF hierher ziehen oder klicken"}</strong>
          <span class="leise klein">${H.length?`${H.length} Datei(en) bereit`:"mehrere Dateien möglich (z. B. Anlagen 2–4)"}</span>
        </label>
        <button class="primaer gross-knopf" ?disabled=${!H.length} @click=${wt}>Auswerten →</button>
        <details class="still">
          <summary>Optionen</summary>
          <div class="zeile">
            <label class="schalter" title=${n?"":"nicht installiert: pip install -r requirements-ocr.txt"}>
              <input type="checkbox" .checked=${Je&&n} ?disabled=${!n} @change=${t=>{Je=t.target.checked}}>
              OCR für Scans ${n?"":"(nicht installiert)"}
            </label>${p("ocr")}
          </div>
          <p class="leise klein">Auch eine Extraktion als JSON oder Bohrungen als BoreholeML (XML) lassen sich laden.</p>
        </details>`}
    </section>`}const mn=5;function bn(e){return e.map(n=>a`
    <tr>
      <td><button class="link" @click=${()=>se(n.signatur)}>${n.name}</button>${n.standort?a` <span class="abzeichen vorerkundung" title="Standort ohne Gutachten">Standort</span>`:u}
        <div class="leise klein">${n.dokumente.join(", ")}</div></td>
      <td class="zahl" title=${n.fremd?`davon ${n.fremd} aus den Datenbanken der Länder`:""}>${n.bohrungen}</td>
      <td class="zahl">${n.geprueft}${n.eincheckungen?a` · <span title="eingecheckt">✓${n.eincheckungen}</span>`:u}</td>
      <td class="leise klein">${n.geaendert}</td>
      <td><button class="symbol" title="Projekt löschen" aria-label="Projekt löschen" @click=${()=>yt(n.signatur,n.name)}>🗑</button></td>
    </tr>`)}function xt(){if(!s.projekte.length)return u;const e=a`<thead><tr><th>Projekt</th><th>Bohrungen</th><th>geprüft</th><th>geändert</th><th></th></tr></thead>`,n=s.projekte.slice(mn);return a`
    <section class="zuletzt">
      <h3>Zuletzt bearbeitet</h3>
      <table class="tabelle kompakt">${e}<tbody>${bn(s.projekte.slice(0,mn))}</tbody></table>
      ${n.length?a`<details class="still"><summary>Alle ${s.projekte.length} Projekte</summary>
        <table class="tabelle kompakt">${e}<tbody>${bn(n)}</tbody></table></details>`:u}
    </section>`}function _t(){const e=s.auftrag,n=s.info?.beispiele??[];return a`
    <details class="still beispiele">
      <summary>Beispiele ausprobieren</summary>
      <div class="zwei-spalten">
        <div>
          <h4 class="klein">Gutachten ${p("beispiele")}</h4>
          <ul class="auswahl-liste">
            ${n.filter(t=>!t.standort).map(t=>a`
              <li><button class="link" ?disabled=${!!e} @click=${()=>gn(t.name)}>${t.titel}</button></li>`)}
          </ul>
        </div>
        <div>
          <h4 class="klein">Standort <span class="leise">(Bohrungen der Länder: Abfrage im Schritt Lage, mit Netz)</span></h4>
          <ul class="auswahl-liste">
            ${n.filter(t=>t.standort).map(t=>a`
              <li><button class="link" ?disabled=${!!e} @click=${()=>gn(t.name)}>${t.titel}</button></li>`)}
          </ul>
        </div>
      </div>
    </details>`}function Gt(){return a`
    <div class="seite-mitte start">
      <header class="start-titel">
        <h1>Baugrund verstehen.</h1>
        <p>Bohrungen aus dem Gutachten oder vom Standort – geprüft, in 3D, im Vergleich mit den Bohrungen der Länder.</p>
      </header>
      <div class="wege">
        ${St()}
        ${Bt()}
      </div>
      ${xt()}
      ${_t()}
      ${s.info?a`<p class="leise klein impressum">GroundTwin ${s.info.version} ·
        <a href="dienste.html" target="_blank" rel="noopener">Dienste der Länder</a> ·
        <a href="viewer.html" target="_blank" rel="noopener">Viewer allein</a> · freie Software unter
        <a href=${`${s.info.quellcode}/blob/main/LICENSE`} target="_blank" rel="noopener">${s.info.lizenz}</a> ·
        <a href=${s.info.quellcode} target="_blank" rel="noopener">Quellcode</a><br>Die App extrahiert und schlägt vor;
        die Interpretation und Freigabe bleibt beim Geotechniker.</p>`:u}
    </div>`}const ze="Deutschland · ETRS89 / UTM (amtlich)",ee="Deutschland · Gauß-Krüger (alt)",_e=[{code:25832,name:"ETRS89 / UTM Zone 32N",gruppe:ze,e:[22e4,101e4],n:[503e4,614e4],hinweis:"Rechtswert 6-stellig, die meisten Länder"},{code:25833,name:"ETRS89 / UTM Zone 33N",gruppe:ze,e:[15e4,7e5],n:[509e4,613e4],hinweis:"Rechtswert 6-stellig, Osten (Berlin, Brandenburg, Sachsen, MV)"},{code:4647,name:"ETRS89 / UTM 32N mit Zone (32…)",gruppe:ze,e:[3223e4,33e6],n:[52e5,614e4],hinweis:"Rechtswert 8-stellig, beginnt mit 32"},{code:5650,name:"ETRS89 / UTM 33N mit Zone (33…)",gruppe:ze,e:[3315e4,3354e4],n:[52e5,613e4],hinweis:"Rechtswert 8-stellig, beginnt mit 33"},{code:31466,name:"DHDN / Gauß-Krüger Zone 2",gruppe:ee,e:[23e5,27e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 2"},{code:31467,name:"DHDN / Gauß-Krüger Zone 3",gruppe:ee,e:[33e5,37e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 3"},{code:31468,name:"DHDN / Gauß-Krüger Zone 4",gruppe:ee,e:[43e5,47e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 4"},{code:31469,name:"DHDN / Gauß-Krüger Zone 5",gruppe:ee,e:[531e4,57e5],n:[52e5,613e4],hinweis:"Rechtswert 7-stellig, beginnt mit 5"},{code:2398,name:"Krassowski (42/83) / Gauß-Krüger Zone 4",gruppe:ee,e:[43e5,47e5],n:[52e5,613e4],hinweis:"neue Länder vor ETRS89, Rechtswert beginnt mit 4"},{code:2399,name:"Krassowski (42/83) / Gauß-Krüger Zone 5",gruppe:ee,e:[53e5,57e5],n:[52e5,613e4],hinweis:"neue Länder vor ETRS89, Rechtswert beginnt mit 5"},{code:3068,name:"DHDN / Soldner Berlin",gruppe:"Deutschland · andere",e:[-4e4,9e4],n:[-4e4,8e4],hinweis:"Berlin, alte Katasterkoordinaten (5-stellig)"},{code:2056,name:"CH1903+ / LV95",gruppe:"Schweiz",e:[245e4,287e4],n:[103e4,134e4],hinweis:"E 2 xxx xxx, N 1 xxx xxx"},{code:21781,name:"CH1903 / LV03",gruppe:"Schweiz",e:[45e4,87e4],n:[3e4,34e4],hinweis:"Y 6-stellig, X 5–6-stellig (alt)"},{code:31254,name:"MGI / Austria GK West",gruppe:"Österreich",e:[-11e4,17e4],n:[11e4,34e4],hinweis:"Rechtswert um 0 (±), Hochwert ohne 5 000 000"},{code:31255,name:"MGI / Austria GK Central",gruppe:"Österreich",e:[-16e4,17e4],n:[9e4,46e4],hinweis:"Rechtswert um 0 (±), Hochwert ohne 5 000 000"},{code:31256,name:"MGI / Austria GK East",gruppe:"Österreich",e:[-16e4,1e5],n:[1e5,48e4],hinweis:"Rechtswert um 0 (±), Hochwert ohne 5 000 000"},{code:31257,name:"MGI / Austria GK M28 (BMN)",gruppe:"Österreich",e:[4e4,32e4],n:[11e4,34e4],hinweis:"Bundesmeldenetz West"},{code:31258,name:"MGI / Austria GK M31 (BMN)",gruppe:"Österreich",e:[29e4,62e4],n:[9e4,46e4],hinweis:"Bundesmeldenetz Mitte"},{code:31259,name:"MGI / Austria GK M34 (BMN)",gruppe:"Österreich",e:[59e4,85e4],n:[1e5,48e4],hinweis:"Bundesmeldenetz Ost"},{code:32632,name:"WGS 84 / UTM Zone 32N",gruppe:"GPS (WGS 84)",e:[22e4,101e4],n:[503e4,614e4],hinweis:"wie ETRS89 / UTM 32N (Abweichung < 1 m)"},{code:32633,name:"WGS 84 / UTM Zone 33N",gruppe:"GPS (WGS 84)",e:[15e4,7e5],n:[509e4,613e4],hinweis:"wie ETRS89 / UTM 33N (Abweichung < 1 m)"}],Dt=new Map(_e.map(e=>[e.code,e]));function an(e){return e?Dt.get(e)??null:null}function rn(e){if(!e)return"ohne System (lokal)";const n=an(e);return n?`EPSG ${e} · ${n.name}`:`EPSG ${e} (nicht in der Liste)`}const Cn=(e,n,t)=>n>=e.e[0]&&n<=e.e[1]&&t>=e.n[0]&&t<=e.n[1];function Mt(e,n){return e===null||n===null||!Number.isFinite(e)||!Number.isFinite(n)?[]:_e.filter(t=>t.gruppe!=="GPS (WGS 84)"&&Cn(t,e,n))}function Zn(e,n,t){if(n===null||t===null||!Number.isFinite(n)||!Number.isFinite(t))return null;const i=Mt(n,t),l=i.slice(0,3).map(o=>`${o.code} (${o.name})`).join(", ");if(!e)return i.length?{ok:!1,text:`Kein System gewählt – die Werte passen zu ${l}.`}:null;const r=an(e);return r?Cn(r,n,t)?{ok:!0,text:`passt zu EPSG ${e} (${r.hinweis})`}:{ok:!1,text:i.length?`Rechts-/Hochwert passen nicht zu EPSG ${e} (${r.hinweis}), aber zu ${l}.`:"Rechts-/Hochwert passen zu keinem System der Liste – Ziffern prüfen (z. B. fehlende Zonenkennung)."}:{ok:!1,text:`EPSG ${e} ist nicht in der Liste – bitte prüfen.`}}function sn(e,n,t="Koordinatensystem"){const i=[...new Set(_e.map(r=>r.gruppe))],l=e!==null&&!an(e);return a`
    <select class="epsg" aria-label=${t} title=${rn(e)}
      @change=${r=>{const o=r.target.value;n(o===""?null:Number(o))}}>
      <option value="" .selected=${e===null}>– ohne (lokal) –</option>
      ${l?a`<option value=${String(e)} .selected=${!0}>EPSG ${e} – nicht in der Liste ⚠</option>`:u}
      ${i.map(r=>a`
        <optgroup label=${r}>
          ${_e.filter(o=>o.gruppe===r).map(o=>a`
            <option value=${String(o.code)} .selected=${o.code===e}>${o.code} · ${o.name}</option>`)}
        </optgroup>`)}
    </select>`}const pe=(e,n=2)=>e.toLocaleString("de-DE",{minimumFractionDigits:n,maximumFractionDigits:n});function qn(e){for(const n of[.5,1,2,5,10,20,50,100])if(e/n<=12)return n;return 200}function Lt(e,n){const t=Math.max(1,...e.map(c=>c.bis)),i=12,l=(n.hoehe-i-14)/t,r=34,o=46,d=qn(t),h=[];for(let c=0;c<=t+1e-9;c+=d)h.push(c);return a`<svg class="saeule" viewBox="0 0 150 ${n.hoehe}" width="150" height=${n.hoehe} role="img" aria-label="Bohrsäule">
    <defs>
      <pattern id="schraffur-warn" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
        <rect width="6" height="6" fill="#e6e6e6"></rect><line x1="0" y1="0" x2="0" y2="6" stroke="#f0a33a" stroke-width="3"></line>
      </pattern>
    </defs>
    ${h.map(c=>T`
      <line x1=${r-5} x2=${r} y1=${i+c*l} y2=${i+c*l} class="achse"></line>
      <text x=${r-7} y=${i+c*l+3} class="achse-text" text-anchor="end">${pe(c,d<1?1:0)}</text>`)}
    <line x1=${r} x2=${r} y1=${i} y2=${i+t*l} class="achse"></line>
    ${e.map(c=>T`
      <g class=${`schicht ${c.k===n.gewaehlt?"gewaehlt":""} ${c.warn?"warn":""}`} @click=${()=>n.waehlen?.(c.k)}>
        <title>${c.titel}</title>
        <rect x=${r+4} y=${i+c.von*l} width=${o} height=${Math.max(1,(c.bis-c.von)*l)}
          fill=${c.warn?"url(#schraffur-warn)":c.farbe}></rect>
        ${c.geprueft?T`<text x=${r+o+9} y=${i+(c.von+c.bis)/2*l+4} class="haken">✓</text>`:u}
        ${(c.bis-c.von)*l>11?T`<text x=${r+o+22} y=${i+c.bis*l-2} class="tiefe">${pe(c.bis)}</text>`:u}
      </g>`)}
  </svg>`}function Nt(e,n){const t=[...e.bohrungen].sort(($,f)=>$.x-f.x||$.y-f.y);if(!t.length)return u;const i=new Map(e.einheiten.map($=>[$.name,$.farbe])),l=Math.max(...t.map($=>$.gok)),r=Math.min(...t.map($=>$.endteufe_nhn)),o=22,d=44,h=Math.max(38,Math.min(70,900/t.length)),c=d+t.length*h+10,v=(n.hoehe-o-10)/Math.max(1,l-r),g=$=>o+(l-$)*v,z=qn(l-r),S=[];for(let $=Math.ceil(r/z)*z;$<=l+1e-9;$+=z)S.push($);return a`<svg class="einheitenprofil" viewBox="0 0 ${c} ${n.hoehe}" width=${c} height=${n.hoehe} role="img"
      aria-label="Einheiten je Bohrung">
    ${S.map($=>T`
      <line x1=${d-4} x2=${c} y1=${g($)} y2=${g($)} class="raster"></line>
      <text x=${d-6} y=${g($)+3} class="achse-text" text-anchor="end">${pe($,z<1?1:0)}</text>`)}
    ${t.map(($,f)=>{const x=d+f*h+h*.2,E=h*.6;return T`
        <text x=${x+E/2} y=${o-8} class="code" text-anchor="middle">${$.code}</text>
        ${$.einheiten.filter(L=>L.status==="vorhanden"&&L.ok_modell-L.uk_modell>.001).map(L=>T`
          <rect x=${x} y=${g(L.ok_modell)} width=${E} height=${Math.max(.8,(L.ok_modell-L.uk_modell)*v)}
            fill=${i.get(L.einheit)??"#ccc"} class=${`einheit ${n.gewaehlt===L.einheit?"gewaehlt":""}`}
            @click=${()=>n.waehlen?.(L.einheit)}>
            <title>${$.code}: ${L.einheit} ${pe(L.ok_modell)} bis ${pe(L.uk_modell)} m NHN</title>
          </rect>`)}
        <line x1=${x-3} x2=${x+E+3} y1=${g($.endteufe_nhn)} y2=${g($.endteufe_nhn)} class="endteufe"></line>`})}
  </svg>`}let Ge="";const De=new Map;let Me=null,Fe="",R=.5;const Le=(e,n=2)=>e==null?"":e.toLocaleString("de-DE",{minimumFractionDigits:n,maximumFractionDigits:n}),Et=()=>(s.z?.sondierungen??[]).find(e=>e.id===Ge)??null;async function Pt(e){Ge=e,s.bid="",m(),await ln(e,!0)}async function ln(e,n=!1){if(!s.sig||!n&&De.has(e))return;const t=await w(()=>k.sondierung(s.sig,e));t&&(De.set(e,t),m())}function oe(e,n,t){return De.delete(e.id),b([{op:"sondierung",sondierung:e.id,feld:n,wert:t}]).then(()=>ln(e.id,!0))}function At(e){return e.entfernt?a`<span class="zeichen raus" title="nicht im Projekt">–</span>`:e.werte_n?e.geprueft?a`<span class="zeichen ok" title="geprüft">✓</span>`:a`<span class="zeichen" title="noch zu prüfen">○</span>`:a`<span class="zeichen warn" title="ohne Werte (nur Code und Seite gelesen)">⚠</span>`}function Kt(){const e=s.z?.sondierungen??[];if(!e.length)return u;const[n,t]=s.z.pruefstand.sondierungen??[0,0];return a`
    <h4 class="sondierungen-kopf">Sondierungen <span class="leise klein">${n}/${t} geprüft</span> ${p("sondierungen")}</h4>
    <ul class="bliste" role="listbox" aria-label="Sondierungen">
      ${e.map(i=>a`
        <li role="option" aria-selected=${String(i.id===Ge)} class=${`${i.id===Ge?"aktiv":""} ${i.entfernt?"raus":""}`}
          @click=${()=>Pt(i.id)}>
          ${At(i)}
          <span class="name">${i.code}</span>
          <span class="wert klein">${i.art}${i.werte_n?` · ${i.werte_n}`:""}</span>
        </li>`)}
    </ul>`}function jt(e){const n=e[2];return n&&typeof n=="object"?[Number(e[0]),Number(e[1]),n.wert,n.zensiert]:[Number(e[0]),Number(e[1]),n==null?null:Number(n),!1]}function Tt(e,n){const o=e.art.toUpperCase().startsWith("DP")||e.art.toUpperCase()==="SRS",d=Math.max(e.endtiefe??0,...n.werte.map(f=>Number(o?f[1]:f[0])||0),1),h=f=>22+f/d*392;if(o){const f=n.werte.map(jt),x=Math.ceil(Math.max(10,...f.map(G=>G[2]??0))/10)*10,E=G=>34+G/x*258,L=f.map(([G,F,Q])=>Q===null?"":`M${E(Q)},${h(G)} V${h(F)}`).join(" "),ot=f.slice(1).map(([G,,F],Q)=>F===null||f[Q][2]===null?"":`M${E(f[Q][2])},${h(G)} H${E(F)}`).join(" ");return T`<svg class="sondierung-kurve" viewBox=${"0 0 300 420"} role="img" aria-label=${`${e.code}: N10 über der Tiefe`}>
      ${Array.from({length:x/(x>60?20:10)+1},(G,F)=>F*(x>60?20:10)).map(G=>T`
        <line x1=${E(G)} x2=${E(G)} y1=${22} y2=${414} class="gitter"/>
        <text x=${E(G)} y=${16} text-anchor="middle">${G}</text>`)}
      ${Array.from({length:Math.floor(d)+1},(G,F)=>T`<text x=${30} y=${h(F)+3} text-anchor="end">${F}</text>`)}
      <path d=${`${L} ${ot}`} class="treppe"/>
      ${f.filter(G=>G[3]).map(([G,F,Q])=>T`<text x=${E(Q??0)+3} y=${(h(G)+h(F))/2+3} class="zensiert">&gt;</text>`)}
      <text x=${34} y=${418} class="achse">N10 [Schläge/10 cm] · Tiefe [m]</text>
    </svg>`}const c=n.werte.map(f=>[Number(f[0]),f[1]===null?null:Number(f[1]),f[2]===null||f[2]===void 0?null:Number(f[2])]),v=Math.max(1,...c.map(f=>f[1]??0)),g=Math.max(1,...c.map(f=>f[2]??0)),z=f=>34+f/v*258,S=f=>34+f/g*258,$=(f,x)=>c.filter(E=>E[x]!==null).map((E,L)=>`${L?"L":"M"}${f(E[x])},${h(E[0])}`).join(" ");return T`<svg class="sondierung-kurve" viewBox=${"0 0 300 420"} role="img" aria-label=${`${e.code}: q_c über der Tiefe`}>
    ${Array.from({length:Math.floor(d)+1},(f,x)=>T`<text x=${30} y=${h(x)+3} text-anchor="end">${x}</text>`)}
    <path d=${$(z,1)} class="qc"/><path d=${$(S,2)} class="fs"/>
    <text x=${34} y=${16} class="achse">q_c bis ${Le(v,1)}</text>
    <text x=${292} y=${16} text-anchor="end" class="achse fs">f_s bis ${Le(g,1)}</text>
  </svg>`}function ne(e,n,t=u){return a`<label class="feld"><span>${e}</span>${n}${t}</label>`}async function Ot(e){if(e.seite===null||!s.z?.dokumente[e.dokument_index]?.pdf)return;const n=`${s.sig}/${e.dokument_index}/${e.seite}`;if(Me?.schluessel===n||Fe===n)return;Fe=n;const t=await w(()=>k.seite(s.sig,e.dokument_index,e.seite-1));Fe="",t&&(Me={schluessel:n,daten:t},m())}function Ft(e,n){Ot(e);const t=Me?.schluessel===`${s.sig}/${e.dokument_index}/${e.seite}`?Me.daten:null,i=n?.beleg?.bbox;return a`
    <aside class="quelle-spalte">
      <div class="saeule-rahmen">${n?Tt(e,n):a`<p class="leise klein">Werte werden geladen …</p>`}</div>
      ${!s.z?.dokumente[e.dokument_index]?.pdf||e.seite===null?u:a`<div class="pdf-rahmen">
        <div class="pdf-kopf"><b>Quelle im PDF</b> <span class="leise klein">S. ${e.seite}</span>
          <span class="fueller"></span>
          <button class="symbol" title="kleiner" @click=${()=>{R=Math.max(.25,R/1.4),m()}}>−</button>
          <button class="symbol" title="größer" @click=${()=>{R=Math.min(1.5,R*1.4),m()}}>+</button>
        </div>
        ${t?a`
          <div class="pdf-seite">
            <div class="pdf-flaeche" style=${`width:${t.breite_pt*t.px_je_pt*R}px;height:${t.hoehe_pt*t.px_je_pt*R}px`}>
              <img src=${t.url} alt=${`Seite ${e.seite}`} draggable="false">
              ${i&&i.length===4?a`<div class="bbox saeule-bbox" style=${`left:${i[0]*t.px_je_pt*R}px;top:${i[1]*t.px_je_pt*R}px;width:${(i[2]-i[0])*t.px_je_pt*R}px;height:${(i[3]-i[1])*t.px_je_pt*R}px`}></div>`:u}
            </div>
          </div>`:a`<p class="leise klein">Seite wird geladen …</p>`}
      </div>`}
    </aside>`}function Ht(){const e=Et();if(!e)return null;const n=De.get(e.id);n||ln(e.id);const t=(i,l,r)=>a`<input type="number" step=${r}
    .value=${B(l===null?"":String(l))} @change=${o=>oe(e,i,o.target.value.trim()||null)}>`;return a`
    <section class="bohrung-detail sondierung-detail">
      <div class="kopfzeile">
        <h3>${e.code} <span class="leise klein">${e.art} · ${e.form}${e.seite?` · S. ${e.seite}`:""} · ${e.dokument}</span></h3>
      </div>
      <div class="felder">
        ${ne("GOK [m NHN]",t("gok",e.gok,"0.01"),a`<span class="leise klein">${e.gok_quelle}</span>`)}
        ${ne("Endtiefe [m]",a`<output>${Le(e.endtiefe)}</output>`,a`<span class="leise klein">${e.endtiefe_aus}</span>`)}
        ${ne("Rechtswert",t("x",e.x,"0.01"))}
        ${ne("Hochwert",t("y",e.y,"0.01"),e.lage_aus?a`<span class="leise klein">${e.lage_aus}</span>`:u)}
        ${ne("Werte",a`<output>${e.werte_n}${e.n10_max!==null?` · N10 max ${e.n10_max}`:""}${e.zensiert?` · ${e.zensiert} über der Achse`:""}</output>`)}
        ${ne("Quelle",a`<output>${e.quelle}${e.konfidenz!==null?` · Konfidenz ${Le(e.konfidenz)}`:""}</output>`)}
      </div>
      ${e.hinweise.length?a`<p class="hinweise">ℹ ${e.hinweise.join(" · ")}</p>`:u}
      <p class="klein leise">Lage: Rechts-/Hochwert eingeben oder im Schritt Lage einen Punkt auf dem gesperrten Plan setzen.
        Die Werte bleiben, wie sie im PDF stehen.</p>
      <div class="detail-fuss">
        <button class="primaer" ?disabled=${e.geprueft||e.entfernt} @click=${()=>oe(e,"geprueft",!0)}>✓ Geprüft</button>
        <button class="leise-knopf" ?disabled=${!e.geprueft} @click=${()=>oe(e,"geprueft",!1)}>Prüfung zurücknehmen</button>
        <span class="fueller"></span>
        ${e.entfernt?a`<button @click=${()=>oe(e,"modell",!0)}>wiederherstellen</button>`:a`<button class="gefahr" @click=${()=>oe(e,"modell",!1)}>🗑 Aus dem Projekt entfernen</button>`}
      </div>
    </section>
    ${Ft(e,n)}`}const Ne=(e,n=2)=>e==null?"":e.toLocaleString("de-DE",{minimumFractionDigits:n,maximumFractionDigits:n}),Qe=e=>{const n=e.target.value.trim().replace(",",".");return n===""?null:Number(n)},Rt=[["boden","Böden"],["organisch","Organisch"],["geologisch","Geologische Benennung"],["fels","Fels"],["anthropogen","Anthropogen"],["unbekannt","Nicht klassifiziert"]];let Ee=null,He="",V=.5,$n=!1;function Jn(){return s.z?.plausibilitaet??[]}function Qn(e){return Jn().find(n=>n.id===e)?.befunde??[]}function Pe(e){const n=ke(),t=n.findIndex(l=>l.id===s.bid),i=n[Math.min(n.length-1,Math.max(0,t+e))];i&&Te(i.id)}function Yn(){const e=ke(),n=tn(e.findIndex(t=>t.id===s.bid));n&&Te(n)}async function Xn(){const e=s.bid;if(!await b([{op:"bohrung_pruefen",id:e,wert:!0}],{leise:!0}))return;const n=tn(ke().findIndex(t=>t.id===e));n&&n!==e&&await Te(n)}async function fn(e){const n=s.z.pruefstand,t=e?`Alle Schichten aller ${n.bohrungen[1]} Bohrungen als geprüft markieren?`:"Die Prüfung aller Bohrungen zurücknehmen?";confirm(t)&&await b([{op:"alle_pruefen",wert:e}])}window.addEventListener("keydown",e=>{if(s.schritt!=="bohrungen"||e.ctrlKey||e.metaKey||e.altKey||e.target?.closest?.("input, select, textarea, [contenteditable]"))return;const t=e.key.toLowerCase();if(e.key==="ArrowDown"||t==="j")Pe(1);else if(e.key==="ArrowUp"||t==="k")Pe(-1);else if(t==="n")Yn();else if(t==="g")Xn();else return;e.preventDefault()});async function It(e,n){const t=Number(e.id.split(":")[0]),i=(n[0]?.quelle.seite??e.seite)-1,l=`${s.sig}/${t}/${i}`;if(Ee?.schluessel===l||He===l||!s.z?.dokumente[t]?.pdf)return;He=l;const r=await w(()=>k.seite(s.sig,t,i));He="",r&&(Ee={schluessel:l,daten:r},m())}function Vt(e){return e.entfernt?a`<span class="zeichen raus" title="nicht im Modell">–</span>`:e.offen>0?a`<span class="zeichen warn" title=${`${e.offen} Schicht(en) nicht klassifiziert`}>⚠</span>`:e.schichten_n&&e.schichten_geprueft===e.schichten_n?a`<span class="zeichen ok" title="alle Schichten geprüft">✓</span>`:a`<span class="zeichen" title="noch zu prüfen">○</span>`}function Wt(e){const n=Qn(e.id);if(!n.length)return u;const t=n.some(l=>l.stufe==="warnung"),i=n.map(l=>`${l.stufe==="warnung"?"Warnung":"Hinweis"}: ${l.text}`).join(`
`);return a`<span class=${`klein ${t?"warn":"leise"}`} title=${i}>${t?"⚠":"ℹ"}\u00a0${n.length}</span>`}function Ut(e){const n=Qn(e.id);if(!n.length)return u;const t=n.filter(r=>r.stufe==="warnung").length,i=n.filter(r=>r.stufe==="hinweis").length,l=[t?`${t} Warnung(en)`:"",i?`${i} Hinweis(e)`:""].filter(Boolean).join(", ");return a`
    <details class="still" ?open=${t>0}>
      <summary class=${t?"warn":""}>${t?"⚠":"ℹ"} Plausibilität (${n.length}): ${l}</summary>
      <ul class="dienste klein">
        ${n.map(r=>a`
          <li class=${r.stufe==="warnung"?"warn":"leise"}>
            ${r.stufe==="warnung"?"⚠ Warnung":"ℹ Hinweis"}: ${r.text}
          </li>`)}
      </ul>
    </details>`}function kn(){const e=s.z.bohrungen,n=ke(),t=e.filter(i=>i.entfernt);return a`
    <aside class="bohrliste-app">
      <input class="suche" type="search" placeholder="Bohrung suchen …" .value=${s.filter}
        @input=${i=>{s.filter=i.target.value,m()}}>
      <ul class="bliste" role="listbox" aria-label="Bohrungen">
        ${n.map(i=>a`
          <li role="option" aria-selected=${String(i.id===s.bid)} class=${i.id===s.bid?"aktiv":""}
            @click=${()=>Te(i.id)}>
            ${Vt(i)}
            <span class="name">${i.code} ${Wt(i)}</span>
            <span class="wert">${i.schichten_geprueft}/${i.schichten_n}</span>
            <button class="symbol leise-knopf" title="Aus dem Modell entfernen" aria-label=${`${i.code} entfernen`}
              @click=${l=>{l.stopPropagation(),b([{op:"entfernen",id:i.id}])}}>🗑</button>
          </li>`)}
      </ul>
      ${t.length?a`
        <details class="entfernt" ?open=${$n} @toggle=${i=>{$n=i.target.open}}>
          <summary>Entfernt / nicht im Modell (${t.length}) ${p("entfernen")}</summary>
          <ul class="bliste">
            ${t.map(i=>a`
              <li class="raus">
                <span class="name">${i.code}</span>
                <span class="wert klein">${i.doppelt_in?"doppelt":i.schichten_n?"":"ohne Schichten"}</span>
                <button class="link klein" ?disabled=${!i.schichten_n} @click=${()=>b([{op:"wiederherstellen",id:i.id}])}>wiederherstellen</button>
              </li>`)}
          </ul>
        </details>`:u}
      ${Kt()}
      <p class="leise klein tasten">↑/↓ blättern · N nächste offene · G alle Schichten geprüft und weiter</p>
    </aside>`}function wn(){const e=s.z.pruefstand,[n,t]=e.bohrungen,[i,l]=e.schichten,r=Jn().flatMap(h=>h.befunde),o=r.filter(h=>h.stufe==="warnung").length,d=r.filter(h=>h.stufe==="hinweis").length;return a`
    <div class="pruefleiste">
      <div class="balken"><span>Bohrungen geprüft <b>${n}/${t}</b></span><progress max=${t||1} value=${n}></progress></div>
      <div class="balken"><span>Schichten geprüft <b>${i}/${l}</b></span><progress max=${l||1} value=${i}></progress></div>
      <span class=${`plakette ${e.unklassifiziert_offen?"warn":"ok"}`}>
        ${e.unklassifiziert_offen?`⚠ ${e.unklassifiziert_offen} Schicht(en) nicht klassifiziert`:"✓ keine offenen Warnungen"}</span>
      ${p("warnung")}
      <span class=${`klein ${o?"warn":"leise"}`}>Plausibilität: ${o} Warnungen, ${d} Hinweise</span>
      <span class="fueller"></span>
      ${p("pruefstand")}
      <button @click=${()=>fn(!0)} ?disabled=${n===t&&i===l}>✓ Alle Bohrungen geprüft</button>
      <button class="leise-knopf" @click=${()=>fn(!1)} ?disabled=${!i}>Zurücknehmen</button>
      ${p("alle_pruefen")}
    </div>`}function Y(e,n,t){return a`<label class="feld"><span>${e}${t?p(t):u}</span>${n}</label>`}function Ct(e){const n=Zn(e.epsg,e.x,e.y);return n&&!n.ok?a`<p class="hinweise warn">⚠ ${n.text}</p>`:u}function Zt(e){const n=ke(),t=n.findIndex(l=>l.id===e.id),i=l=>r=>b([{op:"bohrung",id:e.id,feld:l,wert:Qe(r)}]);return a`
    <div class="detail-kopf">
      <div class="titelzeile">
        <h2>${e.code}</h2>
        <span class="leise">${e.dokument} · Seite ${e.seite}${e.doppelt_in?` · doppelt (auch in ${e.doppelt_in})`:""}</span>
        <span class="fueller"></span>
        <button title="Vorherige Bohrung (↑)" ?disabled=${t<=0} @click=${()=>Pe(-1)}>↑ Vorherige</button>
        <button title="Nächste Bohrung (↓)" ?disabled=${t>=n.length-1} @click=${()=>Pe(1)}>↓ Nächste</button>
        <button title="Nächste Bohrung mit offenen Schichten (N)" ?disabled=${!tn(t)} @click=${Yn}>⚠ Nächste offene</button>
      </div>
      <div class="felder">
        ${Y("GOK [m NHN]",a`<input type="number" step="0.01" .value=${B(e.gok===null?"":String(e.gok))}
            placeholder="unbekannt" @change=${i("gok")}>
            <small class=${e.gok_quelle==="manuell"||e.gok_quelle==="DGM"?"manuell":"leise"}>${e.gok_quelle||"fehlt"}</small>`,"gok")}
        ${Y("Endteufe [m]",a`<output>${Ne(e.endteufe)}</output>`)}
        ${Y("Rechtswert",a`<input type="number" step="0.01" .value=${B(e.x===null?"":String(e.x))} @change=${i("x")}>`,"koordinaten")}
        ${Y("Hochwert",a`<input type="number" step="0.01" .value=${B(e.y===null?"":String(e.y))} @change=${i("y")}>`)}
        ${Y("Koordinatensystem (EPSG)",sn(e.epsg,l=>b([{op:"bohrung",id:e.id,feld:"epsg",wert:l}])),"epsg")}
        ${Y("Ø Säule [m]",a`<input type="number" step="0.1" min="0" class="kurz" placeholder=${`auto ${Ne(s.z.durchmesser??s.z.durchmesser_auto,1)}`}
            .value=${B(e.durchmesser===null?"":String(e.durchmesser))} @change=${i("durchmesser")}>`,"durchmesser")}
        ${Y("Grundwasser",a`<output>${e.grundwasser||"–"}</output>`)}
      </div>
      ${Ct(e)}
      ${Ut(e)}
      ${e.hinweise.length?a`<p class="hinweise">ℹ ${e.hinweise.join(" · ")}</p>`:u}
    </div>`}function qt(e,n){const t=s.z.klassen,i=t.some(l=>l.klasse===n.bodenart);return a`
    <span class="farbfeld" style=${`background:${n.farbe}`}></span>
    <select aria-label="Bodenart" @change=${l=>b([{op:"schicht",id:e.id,k:n.k,feld:"bodenart",wert:l.target.value}])}>
      ${i?u:a`<option .selected=${!0} value=${n.bodenart}>${n.bodenart}</option>`}
      ${Rt.map(([l,r])=>a`
        <optgroup label=${r}>
          ${t.filter(o=>o.art===l).map(o=>a`
            <option value=${o.klasse} .selected=${o.klasse===n.bodenart}>${o.name}${o.din4023?` (${o.din4023})`:""}</option>`)}
        </optgroup>`)}
    </select>`}function Jt(e,n){return a`
    <table class="tabelle schichten">
      <thead><tr>
        <th title="geprüft">✓ ${p("geprueft")}</th><th>von [m] ${p("tiefe")}</th><th>bis [m]</th>
        <th>Bodenart ${p("bodenart")}</th><th>Beschreibung (PDF)</th><th>nach Norm ${p("norm")}</th>
      </tr></thead>
      <tbody>
        ${n.map(t=>a`
          <tr class=${[t.offen?"warn":"",t.korrigiert?"korrigiert":"",t.k===s.k?"gewaehlt":""].join(" ")}
            @click=${()=>{s.k=t.k,m()}}>
            <td><input type="checkbox" .checked=${B(t.geprueft)} aria-label="geprüft"
              @change=${i=>b([{op:"schicht",id:e.id,k:t.k,feld:"geprueft",wert:i.target.checked}],{leise:!0})}></td>
            <td><input type="number" step="0.01" min="0" class="tief" .value=${B(String(t.von))}
              @change=${i=>b([{op:"schicht",id:e.id,k:t.k,feld:"oben",wert:Qe(i)}])}></td>
            <td><input type="number" step="0.01" min="0" class="tief" .value=${B(String(t.bis))}
              @change=${i=>b([{op:"schicht",id:e.id,k:t.k,feld:"unten",wert:Qe(i)}])}></td>
            <td class="bodenart">${qt(e,t)}
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
                  → ${t.vorschlag.klasse} übernehmen</button>${p("vorschlag")}`:u}
            </td>
          </tr>`)}
      </tbody>
    </table>`}function Qt(e,n){It(e,n);const t=Number(e.id.split(":")[0]),i=!!s.z.dokumente[t]?.pdf,l=Ee?.schluessel===`${s.sig}/${t}/${(n[0]?.quelle.seite??e.seite)-1}`?Ee.daten:null,r=n.find(c=>c.k===s.k)??null,o=(c,v)=>{if(!c||!l)return u;const g=l.px_je_pt*V;return a`<div class=${`bbox ${v}`} style=${`left:${c[0]*g}px;top:${c[1]*g}px;width:${(c[2]-c[0])*g}px;height:${(c[3]-c[1])*g}px`}></div>`},d=n.map(c=>c.quelle.bbox).filter(c=>!!c&&c.length===4),h=d.length?[Math.min(...d.map(c=>c[0])),Math.min(...d.map(c=>c[1])),Math.max(...d.map(c=>c[2])),Math.max(...d.map(c=>c[3]))]:null;return a`
    <aside class="quelle-spalte">
      <div class="saeule-rahmen">
        ${Lt(n.map(c=>({k:c.k,von:c.von,bis:c.bis,farbe:c.farbe,warn:c.offen,geprueft:c.geprueft,titel:`${Ne(c.von)}–${Ne(c.bis)} m: ${c.bodenart}${c.beschreibung?` – ${c.beschreibung}`:""}`})),{hoehe:420,gewaehlt:s.k,waehlen:c=>{s.k=c,m()}})}
      </div>
      ${i?a`<div class="pdf-rahmen">
        <div class="pdf-kopf"><b>Quelle im PDF</b> ${p("quelle")}
          <span class="fueller"></span>
          ${i?a`<button class="symbol" title="kleiner" @click=${()=>{V=Math.max(.25,V/1.4),m()}}>−</button>
            <button class="symbol" title="größer" @click=${()=>{V=Math.min(1.5,V*1.4),m()}}>+</button>`:u}
        </div>
        ${l?a`
          ${Yt(h,l.px_je_pt*V)}
          <div class="pdf-seite">
            <div class="pdf-flaeche" style=${`width:${l.breite_pt*l.px_je_pt*V}px;height:${l.hoehe_pt*l.px_je_pt*V}px`}>
              <img src=${l.url} alt=${`Seite ${l.seite+1}`} draggable="false">
              ${o(h,"saeule-bbox")}
              ${o(r?.quelle.bbox,"schicht-bbox")}
            </div>
          </div>`:a`<p class="leise klein">Seite wird geladen …</p>`}
      </div>`:u}
    </aside>`}let vn="";function Yt(e,n){const t=`${s.bid}/${V}`;return!e||vn===t?u:(requestAnimationFrame(()=>{const i=document.querySelector(".pdf-seite");i&&(i.scrollLeft=Math.max(0,e[0]*n-i.clientWidth/3),i.scrollTop=Math.max(0,e[1]*n-40),vn=t)}),u)}function Xt(){const e=s.z,n=s.details.get(s.bid),t=e.bohrungen.find(o=>o.id===s.bid),i=t?Number(t.id.split(":")[0]):0,l=!e.dokumente[i]?.pdf,r=s.bid?null:Ht();return r?a`<div class="schritt-bohrungen">${wn()}${kn()}${r}</div>`:a`
    <div class=${`schritt-bohrungen ${l?"ohne-pdf":""}`}>
      ${wn()}
      ${kn()}
      <section class="bohrung-detail">
        ${t?a`
          ${Zt(t)}
          ${n?a`
            ${Jt(t,n.schichten)}
            <div class="detail-fuss">
              <button class="primaer" title="Alle Schichten dieser Bohrung als geprüft markieren und zur nächsten offenen (G)"
                @click=${Xn}>✓ Alle Schichten geprüft – weiter</button>
              <button class="leise-knopf" ?disabled=${!t.schichten_geprueft}
                @click=${()=>b([{op:"bohrung_pruefen",id:t.id,wert:!1}])}>Prüfung zurücknehmen</button>
              <span class="fueller"></span>
              <button class="gefahr" @click=${()=>b([{op:"entfernen",id:t.id}])}>🗑 Aus dem Modell entfernen</button>
            </div>`:a`<p class="leise">Schichten werden geladen …</p>`}`:a`<p class="leise">Links eine Bohrung wählen.</p>`}
      </section>
      ${t&&n?Qt(t,n.schichten):a`<aside class="quelle-spalte"></aside>`}
    </div>`}const _=(e,n=2)=>e==null||!Number.isFinite(e)?"":e.toLocaleString("de-DE",{minimumFractionDigits:n,maximumFractionDigits:n}),K=e=>{const n=e.target.value.trim().replace(",",".");return n===""?null:Number(n)};let y=null,Ae="",ce="plan",me,Ye=250,Xe=100,en=100;const J=new Set;function zn(e){const n=e.unterlage;return n?`${n.sha}/${n.seite}/${n.art}/${JSON.stringify(n.kalibrierung)}`:""}function et(e){const n=e.unterlage;if(!n)return y=null;if(y&&y.schluessel===zn(e))return y;const t=n.kalibrierung,i=o=>o&&!("n"in o)?o:null,l=i(t?.massstab),r=i(t?.hoehe);return y={schluessel:zn(e),massArt:t?.massstab&&"n"in t.massstab?"n":"strecke",p1:l?{u:l.u1,v:l.v1}:null,p2:l?{u:l.u2,v:l.v2}:null,meter:l?.meter??null,n:t?.massstab&&"n"in t.massstab?t.massstab.n:null,hoeheArt:t?.hoehe?"n"in t.hoehe?"n":"strecke":"gleich",h1:r?{u:r.u1,v:r.v1}:null,h2:r?{u:r.u2,v:r.v2}:null,hoeheMeter:r?.meter??null,hoeheN:t?.hoehe&&"n"in t.hoehe?t.hoehe.n:null,bezug:t?.bezug?{u:t.bezug.u,v:t.bezug.v}:null,x:t?.bezug?.x??null,y:t?.bezug?.y??null,drehung:t?.drehung??0,epsg:t?.epsg??e.viewer.epsg??null},y}function on(e,n=!1){const t=y,i=e.unterlage;if(!t||!i)return null;let l=null;if(t.massArt==="n"&&t.n&&t.n>0&&(l={n:t.n}),t.massArt==="strecke"&&t.p1&&t.p2&&t.meter&&t.meter>0&&(l={u1:t.p1.u,v1:t.p1.v,u2:t.p2.u,v2:t.p2.v,meter:t.meter}),!l||!t.bezug||t.x===null||t.y===null)return null;let r=null;return i.art==="schnitt"&&t.hoeheArt==="n"&&t.hoeheN&&t.hoeheN>0&&(r={n:t.hoeheN}),i.art==="schnitt"&&t.hoeheArt==="strecke"&&t.h1&&t.h2&&t.hoeheMeter&&t.hoeheMeter>0&&(r={u1:t.h1.u,v1:t.h1.v,u2:t.h2.u,v2:t.h2.v,meter:t.hoeheMeter}),{massstab:l,hoehe:r,bezug:{...t.bezug,x:t.x,y:t.y},drehung:i.art==="plan"?t.drehung:0,epsg:i.art==="plan"?t.epsg:null,gesperrt:n}}function P(){const e=s.z;s.entwurf=on(e);const n=s.viewer;n&&y&&(n.editor.hilfsmarken({strecke:y.massArt==="strecke"?[y.p1,y.p2]:[],hoehe:y.hoeheArt==="strecke"?[y.h1,y.h2]:[],bezug:y.bezug}),s.entwurf&&n.editor.vorschau(s.entwurf)),m()}async function ei(e){const n=s.viewer;if(!n||!y)return;Ae=e,m();const t=await n.editor.bildpunktWaehlen();if(Ae="",!t||!y||s.z?.unterlage?.kalibrierung?.gesperrt){m();return}y[e]=t,P()}async function Bn(e){s.viewer?.editor.waehlenAbbrechen();const n=on(s.z,e);if(!n){A("Für die Kalibrierung fehlen Maßstab oder Bezugspunkt.","warn");return}await b([{op:"kalibrierung",wert:n}])&&(s.entwurf=null,A(e?"Plan kalibriert und gesperrt – jetzt die Bohrungen ziehen.":"Kalibrierung übernommen.","ok"),await s.viewer?.ansicht(s.z?.unterlage?.art==="schnitt"?"sued":"oben"))}async function ni(e){const n=s.z.unterlage;n?.kalibrierung&&await b([{op:"kalibrierung",wert:{...n.kalibrierung,gesperrt:e}}])}async function ti(e){const n=e.target,t=n.files?.[0];if(n.value="",!t)return;const i=await w(()=>k.unterlage(s.sig,t,ce,0),"Unterlage wird gelesen …");i&&(O(i),s.entwurf=null,m(),await Oe(),await s.viewer?.lageModus(!0),await s.viewer?.ansicht(i.unterlage?.art==="schnitt"?"sued":"oben"))}async function yn(e,n){const t=await w(()=>k.unterlageSeite(s.sig,e,n),"Seite wird gelesen …");t&&(O(t),s.entwurf=null,m(),await Oe(),await s.viewer?.ansicht(n==="schnitt"?"sued":"oben"))}async function ii(){if(!confirm("Unterlage mit ihrer Kalibrierung entfernen? Gesetzte Bohrungen behalten ihre Lage."))return;const e=await w(()=>k.unterlageEntfernen(s.sig));e&&(O(e),s.entwurf=null,m(),await Oe())}const W=(e,n,t=!0)=>a`<details class="abschnitt" ?open=${t}><summary>${e}</summary><div class="abschnitt-inhalt">${n}</div></details>`;function ue(e,n,t,i){return a`<button class=${`punkt ${Ae===n?"aktiv":""} ${t?"gesetzt":""}`} ?disabled=${i}
    @click=${()=>ei(n)}>${Ae===n?"… im Plan klicken":t?`${e} ✓`:e}</button>`}function ai(e){const n=Zn(e.epsg,e.x,e.y);return n?a`<p class=${`klein ${n.ok?"ok":"warn"}`}>${n.ok?"✓":"⚠"} ${n.text}</p>`:u}function ri(e){const n=e.unterlage,t=et(e),i=!!n.kalibrierung?.gesperrt,l=n.art==="plan",r=t.p1&&t.p2?Math.hypot(t.p2.u-t.p1.u,t.p2.v-t.p1.v):null,o=on(e),d=o?gt(o.massstab,n.mm_pro_px):null,h=e.viewer.bohrungen.filter(c=>c.x!==null&&(l?!/Plan|Viewer/.test(c.quelle):c.gok_bekannt));return a`
    <p class=${`status ${n.kalibrierung?i?"ok":"":"warn"}`}>
      ${n.kalibrierung?a`${i?"🔒 gesperrt · ":""}${cn(n)}${l?` · ${rn(n.kalibrierung.epsg)}`:""}`:"nicht kalibriert"}
      ${s.entwurf&&JSON.stringify({...s.entwurf,gesperrt:!1})!==JSON.stringify({...n.kalibrierung??{},gesperrt:!1})?a`<br><span class="leise">Vorschau: ${cn(n,s.entwurf)} (noch nicht übernommen)</span>`:u}
    </p>
    ${i?a`
      <p class="leise klein">Der Plan liegt fest. ${l?"Bohrungen unten mit „Punkte setzen“ in den Plan klicken oder im Viewer ziehen – nur in x/y":"Bohrungen im Viewer ziehen – entlang der Station; die Höhe nur ohne GOK aus dem PDF"}.</p>
      <button @click=${()=>ni(!1)}>🔓 Entsperren (neu kalibrieren)</button>`:a`
      <fieldset class="gruppe">
        <legend>1 · Maßstab ${p("massstab")}</legend>
        <div class="umschalter">
          <label><input type="radio" name="massart" .checked=${t.massArt==="strecke"} @change=${()=>{t.massArt="strecke",P()}}> Strecke messen</label>
          <label><input type="radio" name="massart" .checked=${t.massArt==="n"} @change=${()=>{t.massArt="n",P()}}> 1:n eingeben</label>
        </div>
        ${t.massArt==="strecke"?a`
          <div class="zeile">${ue("Punkt 1","p1",t.p1,!1)}${ue("Punkt 2","p2",t.p2,!1)}</div>
          <div class="zeile">
            <span class="leise klein">${r?`gemessen ${_(r,0)} px`:"zwei Punkte anklicken"}</span>
            <label class="inline">wahre Länge <input type="number" step="0.01" min="0" class="kurz" .value=${B(t.meter===null?"":String(t.meter))}
              @input=${c=>{t.meter=K(c),P()}}> m</label>
          </div>`:a`
          <label class="inline">Maßstab 1: <input type="number" step="1" min="1" class="kurz" .value=${B(t.n===null?"":String(t.n))}
            @input=${c=>{t.n=K(c),P()}}></label>`}
        ${d?a`<p class="leise klein">ergibt 1:${Math.round(d).toLocaleString("de-DE")}</p>`:u}
      </fieldset>
      ${l?u:a`
        <fieldset class="gruppe">
          <legend>Höhenmaßstab ${p("hoehe")}</legend>
          <div class="umschalter">
            <label><input type="radio" name="hoeheart" .checked=${t.hoeheArt==="gleich"} @change=${()=>{t.hoeheArt="gleich",P()}}> wie Länge</label>
            <label><input type="radio" name="hoeheart" .checked=${t.hoeheArt==="n"} @change=${()=>{t.hoeheArt="n",P()}}> 1:n</label>
            <label><input type="radio" name="hoeheart" .checked=${t.hoeheArt==="strecke"} @change=${()=>{t.hoeheArt="strecke",P()}}> messen</label>
          </div>
          ${t.hoeheArt==="n"?a`<label class="inline">Höhe 1: <input type="number" step="1" min="1" class="kurz"
              .value=${B(t.hoeheN===null?"":String(t.hoeheN))} @input=${c=>{t.hoeheN=K(c),P()}}></label>`:u}
          ${t.hoeheArt==="strecke"?a`
            <div class="zeile">${ue("Höhe oben","h1",t.h1,!1)}${ue("Höhe unten","h2",t.h2,!1)}</div>
            <label class="inline">Höhenunterschied <input type="number" step="0.01" min="0" class="kurz"
              .value=${B(t.hoeheMeter===null?"":String(t.hoeheMeter))} @input=${c=>{t.hoeheMeter=K(c),P()}}> m</label>`:u}
        </fieldset>`}
      <fieldset class="gruppe">
        <legend>2 · Bezugspunkt ${p("bezug")}</legend>
        <div class="zeile">${ue("Punkt im Plan wählen","bezug",t.bezug,!1)}</div>
        <div class="zeile">
          <label class="feld schmal"><span>${l?"Rechtswert":"Station [m]"}</span>
            <input type="number" step="0.01" .value=${B(t.x===null?"":String(t.x))} @input=${c=>{t.x=K(c),P()}}></label>
          <label class="feld schmal"><span>${l?"Hochwert":"Höhe [m NHN]"}</span>
            <input type="number" step="0.01" .value=${B(t.y===null?"":String(t.y))} @input=${c=>{t.y=K(c),P()}}></label>
        </div>
        ${l?a`
          <label class="feld breit"><span>Koordinatensystem (EPSG) ${p("epsg")}</span>
            ${sn(t.epsg,c=>{t.epsg=c,P()})}</label>
          ${ai(t)}`:u}
        ${h.length?a`
          <label class="inline klein">oder von Bohrung
            <select @change=${c=>{const v=e.viewer.bohrungen.find(g=>g.id===c.target.value);v&&(t.x=v.x,t.y=l?v.y:v.gok,P())}}>
              <option value="">–</option>
              ${h.map(c=>a`<option value=${c.id}>${c.code}</option>`)}
            </select></label>`:u}
      </fieldset>
      ${l?a`
        <fieldset class="gruppe">
          <legend>3 · Drehung ${p("drehung")}</legend>
          <div class="zeile">
            <label class="inline"><input type="number" step="0.1" class="kurz" .value=${B(String(t.drehung))}
              @input=${c=>{t.drehung=K(c)??0,P()}}> ° gegen den Uhrzeigersinn</label>
          </div>
        </fieldset>`:u}
      <div class="zeile knopfzeile">
        <button ?disabled=${!o} @click=${()=>Bn(!1)}>Übernehmen</button>
        <button class="primaer" ?disabled=${!o} @click=${()=>Bn(!0)}>🔒 Übernehmen und sperren</button>
        ${p("sperren")}
      </div>
      ${n.kalibrierung?a`<button class="link klein" @click=${()=>b([{op:"kalibrierung",wert:null}])}>Kalibrierung zurücksetzen</button>`:u}`}`}function si(e){const n=e.unterlage;return n?a`
    <p><b>${n.name}</b> <span class="leise">· ${n.art==="plan"?"Lageplan":"Längsschnitt"}</span></p>
    <div class="zeile">
      ${(n.seiten??1)>1?a`<label class="inline">Seite <select @change=${t=>yn(Number(t.target.value),n.art)}>
          ${Array.from({length:n.seiten},(t,i)=>a`<option value=${i} .selected=${i===n.seite}>${i+1}</option>`)}
        </select></label>`:u}
      <label class="inline">Ansicht <select @change=${t=>yn(n.seite,t.target.value)}>
        <option value="plan" .selected=${n.art==="plan"}>Lageplan</option>
        <option value="schnitt" .selected=${n.art==="schnitt"}>Längsschnitt</option>
      </select></label>
    </div>
    <label class="inline">Deckkraft ${p("deckkraft")}
      <input type="range" min="0.1" max="1" step="0.05" .value=${String(s.viewer?.editor.deckkraft??.85)}
        @input=${t=>{s.viewer&&(s.viewer.editor.deckkraft=Number(t.target.value),s.viewer.editor.bildSichtbarkeit())}}></label>
    <button class="link klein" @click=${ii}>Unterlage entfernen</button>`:a`
      <p class="leise klein">Lageplan (von oben) oder Längsschnitt (von der Seite) als PDF – er liegt im Viewer unter den Bohrungen.</p>
      <div class="umschalter">
        <label><input type="radio" name="neueart" .checked=${ce==="plan"} @change=${()=>{ce="plan"}}> Lageplan</label>
        <label><input type="radio" name="neueart" .checked=${ce==="schnitt"} @change=${()=>{ce="schnitt"}}> Längsschnitt</label>
      </div>
      <label class="datei-knopf"><input type="file" accept=".pdf,application/pdf" @change=${ti}>PDF wählen …</label>`}function li(e){const n=e.unterlage,t=!n||!!n.kalibrierung?.gesperrt,i=e.viewer.bohrungen.filter(o=>o.x===null),l=e.lage_modus==="reihe",r=!l&&n?.art==="plan"&&!!n.kalibrierung?.gesperrt;return a`
    ${t?u:a`<p class="warnung">Erst kalibrieren und sperren (🔒) – dann Punkte setzen oder Bohrungen ziehen.</p>`}
    ${r?ci(e):u}
    ${i.length?a`
      <p class="klein">Ohne Lage (${i.length}) – ${r?"anklicken = als Nächste setzen, oder":""} in den Viewer ziehen
        ${p("ohne_lage")}</p>
      <div class="parkplatz">
        ${i.map(o=>a`<span class=${`park ${t?"":"gesperrt"} ${s.punktModus&&s.naechste===o.id?"aktiv":""}`}
          title=${r?"Klick: als nächste Bohrung setzen · Ziehen: direkt in den Viewer":"In den Viewer ziehen"}
          @pointerdown=${d=>s.viewer?.editor.ziehenStart(d,o.id,!0)}
          @click=${()=>{r&&Ke(!0,o.id)}}>${o.code}</span>`)}
      </div>`:a`<p class="leise klein">Alle Bohrungen im Modell haben eine Lage.</p>`}
    ${r?di(e):u}
    ${l?u:ui(e)}
    ${l?hi(e):u}`}function oi(e){const n=e.viewer.sondierungen??[];return n.length?a`<optgroup label="Sondierungen">${n.map(t=>a`<option value=${`S|${t.id}`}>${t.code}${t.x===null?"":" (ersetzen)"}</option>`)}</optgroup>`:u}function ui(e){const n=e.viewer.sondierungen??[];if(!n.length)return u;const t=n.filter(i=>i.x!==null);return a`<p class="klein">Sondierungen: ${t.length}/${n.length} mit Lage ${p("sondierungen")}
    ${n.length>t.length?a`<span class="leise">– ohne: ${n.filter(i=>i.x===null).map(i=>i.code).join(", ")}
      (Punkt auf dem gesperrten Plan setzen und hier zuordnen, oder Rechts-/Hochwert im Schritt Bohrungen)</span>`:u}</p>`}function Ke(e,n){s.punktModus=e,n!==void 0?s.naechste=n:e&&!s.naechste&&(s.naechste=ct()),s.viewer?.editor.punktModusSetzen(e),m()}function ci(e){const n=e.viewer.bohrungen.filter(i=>i.x===null),t=e.viewer.bohrungen.filter(i=>i.x!==null);return a`
    <div class="zeile">
      <button class=${s.punktModus?"primaer":""} @click=${()=>Ke(!s.punktModus)}>
        ${s.punktModus?"● Punkte setzen – Klick in den Plan":"＋ Punkte im Plan setzen"}</button>
      ${s.punktModus?a`<button class="leise-knopf" @click=${()=>Ke(!1)}>Fertig (Esc)</button>`:u}
      ${p("punkte")}
    </div>
    ${s.punktModus?a`
      <label class="feld breit"><span>Nächster Klick setzt</span>
        <select class="naechste" @change=${i=>{s.naechste=i.target.value,m()}}>
          <option value="" .selected=${!s.naechste}>– freien Punkt (später zuordnen) –</option>
          ${n.length?a`<optgroup label="Ohne Lage">
            ${n.map(i=>a`<option value=${i.id} .selected=${s.naechste===i.id}>${i.code}</option>`)}</optgroup>`:u}
          ${t.length?a`<optgroup label="Mit Lage (neu setzen)">
            ${t.map(i=>a`<option value=${i.id} .selected=${s.naechste===i.id}>${i.code}</option>`)}</optgroup>`:u}
        </select></label>
      <p class="leise klein">Danach ist automatisch die nächste Bohrung ohne Lage dran.</p>`:u}`}function di(e){const n=e.viewer.bohrungen.filter(r=>r.x!==null&&/Plan|Viewer/.test(r.quelle)),t=e.viewer.bohrungen,i=t.filter(r=>r.x===null);if(!n.length&&!e.punkte.length)return u;const l=(r,o)=>a`<span class="leise klein">R ${_(r)}<br>H ${_(o)}</span>`;return a`
    <p class="klein">Gesetzte Punkte (${n.length+e.punkte.length})</p>
    <table class="tabelle kompakt punkte">
      <tbody>
        ${e.punkte.map(r=>a`
          <tr class=${`frei ${s.viewer?.editor.punktGewaehlt===r.id?"gewaehlt":""}`}>
            <td><button class="link" title="Im Viewer wählen" @click=${()=>{s.viewer?.editor.punktWaehlen(r.id),m()}}>◆ ${r.id}</button></td>
            <td>${l(r.x,r.y)}</td>
            <td><select aria-label=${`${r.id} zuordnen`} @change=${o=>{const d=o.target.value;d.startsWith("S|")?b([{op:"punkt_zuordnen",punkt:r.id,sondierung:d.slice(2)}]):d&&b([{op:"punkt_zuordnen",punkt:r.id,bohrung:d}])}}>
              <option value="" selected>– Bohrung zuordnen –</option>
              ${oi(e)}
              ${i.length?a`<optgroup label="Ohne Lage">${i.map(o=>a`<option value=${o.id}>${o.code}</option>`)}</optgroup>`:u}
              <optgroup label="Mit Lage (ersetzen)">${t.filter(o=>o.x!==null).map(o=>a`<option value=${o.id}>${o.code}</option>`)}</optgroup>
            </select></td>
            <td><button class="symbol" title="Punkt löschen" @click=${()=>b([{op:"punkt_loeschen",punkt:r.id}])}>✕</button></td>
          </tr>`)}
        ${n.map(r=>a`
          <tr class=${s.viewer?.editor.ausgewaehlt===r.id?"gewaehlt":""}>
            <td><button class="link" title="Im Viewer wählen" @click=${()=>{s.viewer?.nadelWaehlen(r.id),m()}}>● ${r.code}</button></td>
            <td>${l(r.x,r.y)}</td>
            <td><select aria-label=${`${r.code} umhängen`} @change=${o=>{const d=o.target.value;d==="-"?b([{op:"lage_loesen",id:r.id}]):d&&d!==r.id&&b([{op:"lage_umhaengen",id:r.id,nach:d}])}}>
              <option value=${r.id} selected>${r.code}</option>
              <option value="-">– Zuordnung lösen (freier Punkt) –</option>
              ${i.length?a`<optgroup label="Andere Bohrung (ohne Lage)">${i.map(o=>a`<option value=${o.id}>${o.code}</option>`)}</optgroup>`:u}
            </select></td>
            <td><button class="symbol" title="Lage entfernen (Bohrung wieder ohne Lage)" @click=${()=>b([{op:"lage_entfernen",id:r.id}])}>✕</button></td>
          </tr>`)}
      </tbody>
    </table>`}function hi(e){const n=e.reihe.map(i=>i.id),t=(i,l)=>{const r=[...n],[o]=r.splice(i,1);r.splice(Math.max(0,Math.min(r.length,i+l)),0,o),b([{op:"reihe",reihenfolge:r}],{leise:!0})};return a`
    <div class="zeile">
      <label class="inline">Standardabstand ${p("standardabstand")}
        <input type="number" step="1" min="1" class="kurz" .value=${B(String(e.reihe_standard))}
          @change=${i=>b([{op:"reihe",standard:K(i)}])}> m</label>
    </div>
    <table class="tabelle kompakt reihe">
      <thead><tr><th></th><th>Bohrung</th><th>Abstand [m] ${p("reihe")}</th><th>Station [m]</th></tr></thead>
      <tbody>
        ${e.reihe.map((i,l)=>a`
          <tr>
            <td class="pfeile"><button class="symbol" ?disabled=${l===0} title="nach vorn" @click=${()=>t(l,-1)}>▲</button><button class="symbol"
              ?disabled=${l===n.length-1} title="nach hinten" @click=${()=>t(l,1)}>▼</button></td>
            <td>${i.code}</td>
            <td><input type="number" step="0.1" min="0" class="kurz" ?disabled=${l===0} .value=${B(i.abstand===null?"":String(i.abstand))}
              @change=${r=>b([{op:"reihe",abstand:{[i.id]:K(r)}}],{leise:!0})}></td>
            <td><input type="number" step="0.1" class="kurz" .value=${B(String(i.station))} title=${i.quelle_text}
              @change=${r=>b([{op:"reihe",station:{[i.id]:K(r)}}],{leise:!0})}></td>
          </tr>`)}
      </tbody>
    </table>`}async function gi(e){const n=e.target,t=[...n.files??[]];if(n.value="",!t.length)return;const i=me===void 0?s.z?.viewer.epsg??null:me,l=await w(()=>k.dgm(s.sig,t,i),"DGM wird gelesen …");if(l){O(l),m();const r=l.gelaende?.pruefung?.warnungen.length??0;A(r?"DGM geladen – Hinweise zum Vergleich beachten.":"DGM geladen.",r?"warn":"ok")}}async function pi(){const e=await w(()=>k.dgmAbruf(s.sig,Xe),"DGM wird beim Land abgerufen …");if(e){O(e),m();const n=e.gelaende?.pruefung?.warnungen.length??0;A(n?"DGM vom Land geladen – Hinweise zum Vergleich beachten.":"DGM vom Land geladen.",n?"warn":"ok")}}function Sn(e){return e.lage_modus!=="koordinaten"?u:a`
    <div class="zeile">
      <label class="inline">Rand <input type="number" min="0" max="1000" step="25" class="kurz" aria-label="Rand um die Bohrungen"
        .value=${B(String(Xe))} @change=${n=>{Xe=K(n)??100}}> m</label>
      <button @click=${pi} title="Sendet den Ausschnitt um die Bohrungen an den Dienst des Landes">
        DGM vom Land abrufen</button>${p("dgm_land")}
    </div>
    <p class="leise klein">Brandenburg mit Berlin und NRW (DGM1, WCS). Sendet den Ausschnitt um die Bohrungen an den Dienst.</p>`}async function mi(){if(!confirm("DGM aus dem Projekt entfernen? Übernommene GOK bleiben (Quelle DGM)."))return;const e=await w(()=>k.dgmEntfernen(s.sig));e&&(O(e),m())}const Re={ok:["✓","ok"],abweichung:["⚠ weicht ab","warn"],ohne_gok:["GOK fehlt",""],aus_dgm:["aus dem DGM","leise"],ausserhalb:["außerhalb","leise"],ohne_lage:["ohne Lage","leise"],anderes_system:["anderes EPSG","warn"]},xn=e=>e===null?"":Math.abs(e)<.005?_(0):`${e>0?"+":""}${_(e)}`;function bi(e){const n=e.gelaende,t=h=>a`<label class="datei-knopf"><input type="file" multiple aria-label="DGM-Dateien"
    accept=".xyz,.txt,.csv,.asc,.tif,.tiff,.zip,.gz" @change=${gi}>${h}</label>`,i=me===void 0?e.viewer.epsg??null:me,l=a`<label class="feld breit"><span>System der Datei (XYZ, ASCII) ${p("dgm_epsg")}</span>
    ${sn(i,h=>{me=h,m()},"System der DGM-Datei")}</label>`;if(!n)return a`
      <p class="leise klein">DGM-Kachel(n) des Landes (Open Data, z. B. DGM1) als XYZ, ASCII-Raster oder GeoTIFF, auch als
        ZIP – Höhen in m NHN. Damit prüft die App die GOK, schlägt fehlende vor und legt das Gelände ins Modell.</p>
      ${Sn(e)}
      ${l}
      ${t("DGM-Dateien wählen …")}`;const r=n.info,o=n.pruefung,d=r.quelle;return a`
    <p><b>${r.name}</b><br><span class="leise klein">${rn(r.epsg)} · Raster ${_(r.dx,1)} m ·
      ${r.spalten.toLocaleString("de-DE")} × ${r.zeilen.toLocaleString("de-DE")} · ${_(r.zmin,1)} – ${_(r.zmax,1)} m NHN</span></p>
    ${d?a`<p class="leise klein">${d.anbieter} · <a href=${d.beleg} target="_blank" rel="noopener">${d.lizenz}</a> ·
      ${d.namensnennung} · abgerufen ${d.abgerufen}</p>`:u}
    ${n.fehler?a`<p class="warnung klein">${n.fehler}</p>`:u}
    ${o?a`
      <table class="tabelle kompakt gelaende">
        <thead><tr><th>Bohrung</th><th class="zahl">GOK</th><th class="zahl">DGM</th><th class="zahl">Δ [m]</th><th></th></tr></thead>
        <tbody>
          ${o.zeilen.map(h=>a`
            <tr class=${Re[h.status][1]}>
              <td><button class="link" title="Im Viewer wählen" @click=${()=>{s.viewer?.nadelWaehlen(h.id),m()}}>${h.code}</button></td>
              <td class="zahl">${_(h.gok)}</td>
              <td class="zahl">${_(h.dgm)}</td>
              <td class="zahl">${xn(h.differenz)}</td>
              <td class=${`klein ${Re[h.status][1]}`}>${h.status==="ohne_gok"?a`<button class="klein" title="GOK aus dem DGM übernehmen (Quelle DGM)"
                    @click=${()=>b([{op:"gok_aus_dgm",ids:[h.id]}])}>übernehmen</button>`:Re[h.status][0]}</td>
            </tr>`)}
        </tbody>
      </table>
      ${o.verglichen?a`<p class="leise klein">${o.verglichen} verglichen · Median ${xn(o.median)} m ·
        größte Abweichung ${_(o.max)} m (unauffällig bis ${_(o.toleranz,1)} m)</p>`:u}
      ${o.warnungen.map(h=>a`<p class="warnung klein">⚠ ${h}</p>`)}
      ${o.vorschlaege>1?a`<button @click=${()=>b([{op:"gok_aus_dgm"}])}>
        Alle ${o.vorschlaege} fehlenden GOK aus dem DGM übernehmen</button>`:u}`:u}
    ${Sn(e)}
    ${l}
    <div class="zeile">${t("Andere DGM-Dateien …")}
      <button class="link klein" @click=${mi}>DGM entfernen</button></div>`}async function $i(){const e=await w(()=>k.sgdAbfrage(s.sig,Ye),"Dienste der Länder werden abgefragt …");if(!e?.sgd)return;O(e),J.clear(),m();const n=e.sgd;A(`${n.treffer.length} Bohrungen der Länder im Umkreis von ${_(n.radius,0)} m`+(n.fehler.length?` – ${n.fehler.length} Meldung(en) der Dienste`:""),n.fehler.length?"warn":"ok")}async function fi(){const e=[...J].map(t=>({dienst:t.slice(0,t.indexOf("/")),id:t.slice(t.indexOf("/")+1)})),n=await w(()=>k.sgdUebernehmen(s.sig,e),"Schichtdaten werden beim Land geholt …");if(n){O(n.zustand),J.clear();for(const t of n.meldungen)A(t,"ok");await Oe(),m()}}function ki(e){const n=e.treffer.filter(r=>!r.uebernehmbar&&!r.uebernommen&&!r.gutachten);if(!n.length)return u;const t=r=>e.quellen.find(o=>o.dienst===r)?.land??r,i=r=>{const o=n.filter(d=>d.schichten===r);return o.length?`${o.length} (${[...new Set(o.map(d=>t(d.dienst)))].join(", ")})`:""},l=[i("grafik")&&`${i("grafik")} nur mit Kopfdaten: das Land gibt das Schichtenverzeichnis nur als Bild heraus (Profil ↗), nicht als Daten`,i("portal")&&`${i("portal")} nur als Hinweis: das Schichtenverzeichnis liegt beim Land, der Dienst nennt nur die Kopfdaten`,i("keine")&&`${i("keine")} ohne Schichtenverzeichnis`,i("ohne Petrographie")&&`${i("ohne Petrographie")} mit Schichten ohne Petrographie`].filter(Boolean);return a`<p class="leise klein sgd-warum">Nicht übernehmbar: ${l.join("; ")}. Ohne Schichten entsteht kein Modell –
    sie zu erfinden wäre falsch. Lage, GOK und Teufe sehen Sie hier; die Schichten im Profil des Landes. Übernehmbar sind
    Bohrungen mit Schichtdaten in BoreholeML (NRW, Baden-Württemberg, Hamburg).</p>`}function wi(e){return e.gutachten?a`<span class="ok" title="Dieselbe Bohrung im Gutachten">= ${e.gutachten}</span>`:e.uebernommen?a`<span class="ok">✓ im Projekt</span>`:e.schichten==="boreholeml"?a`${e.schichten_n} Schichten`:e.schichten==="grafik"&&e.profil?a`<a href=${e.profil} target="_blank" rel="noopener">Profil ↗</a>`:e.schichten==="portal"?a`<span class="leise" title="Nur ein Hinweis: das Schichtenverzeichnis liegt beim Land, nicht in diesem Dienst">beim Land</span>`:a`<span class="leise">${e.schichten==="ohne Petrographie"?"ohne Petrographie":"keine Schichten"}</span>`}async function vi(){const e=await w(()=>k.gebaeudeAbruf(s.sig,en),"Gebäude werden beim Land abgerufen …");e&&(O(e),m(),A(`${e.gebaeude?.anzahl??0} Gebäude geladen – im Modell als Umgebung.`,"ok"))}async function zi(){const e=await w(()=>k.gebaeudeEntfernen(s.sig));e&&(O(e),m())}function Bi(e){if(e.lage_modus!=="koordinaten")return a`<p class="leise klein">Nur mit Lage nach Koordinaten.</p>`;const n=e.gebaeude,t=a`
    <div class="zeile">
      <label class="inline">Rand <input type="number" min="0" max="1000" step="25" class="kurz" aria-label="Rand der Gebäude"
        .value=${B(String(en))} @change=${l=>{en=K(l)??100}}> m</label>
      <button @click=${vi} title="Lädt die Kacheln (1 × 1 km) um die Bohrungen beim Land">
        ${n?"Gebäude neu abrufen":"Gebäude vom Land abrufen"}</button>${p("gebaeude")}
    </div>`;if(!n)return a`
      <p class="leise klein">3D-Gebäudemodelle LoD2 von Berlin, Brandenburg und NRW (CityGML, m NHN) als Umgebung im Modell und
        im IFC. Lädt die Kacheln von 1 × 1 km um die Bohrungen – das verrät die Lage des Projekts auf etwa 1 km.</p>
      ${t}`;const i=n.quelle;return a`
    <p><b>${n.anzahl.toLocaleString("de-DE")} Gebäude</b> · ${n.flaechen.toLocaleString("de-DE")} Flächen ·
      ${i.kacheln} Kachel${i.kacheln===1?"":"n"} <span class="leise klein">· abgerufen ${i.abgerufen}</span></p>
    ${i.dienste.map(l=>a`<p class="leise klein">${l.anbieter} · <a href=${l.beleg} target="_blank" rel="noopener">${l.lizenz}</a> ·
      ${l.namensnennung}</p>`)}
    ${i.ohne_kachel.length?a`<p class="leise klein">ohne Kachel beim Land: ${i.ohne_kachel.join(", ")}</p>`:u}
    ${i.fehler.map(l=>a`<p class="warnung klein">⚠ ${l}</p>`)}
    ${n.hinweis?a`<p class="warnung klein">⚠ ${n.hinweis}</p>`:u}
    <p class="leise klein">Im Viewer mit dem Knopf „Gebäude“ ein- und ausblendbar.</p>
    ${t}
    <button class="link klein" @click=${zi}>Gebäude entfernen</button>`}function yi(e){if(e.lage_modus==="reihe")return a`<p class="leise klein">Nur mit Lage nach Koordinaten.</p>`;const n=e.sgd,t=a`
    <p class="leise klein">Bohrungen aus den Datenbanken der Geologischen Dienste um die Mitte des Projekts.
      <b>Die Abfrage sendet die Lage des Projekts an den Dienst des Landes.</b></p>
    <div class="zeile">
      <label class="inline">Umkreis <input type="number" min="10" max="2000" step="50" class="kurz" aria-label="Umkreis der Abfrage"
        .value=${B(String(Ye))} @change=${d=>{Ye=K(d)??250}}> m</label>
      <button @click=${$i}>${n?"Neu abfragen":"Abfragen"}</button>
    </div>`;if(!n)return t;const i=n.gegenprobe,l=i.anzahl>0&&(i.lage_max??0)<=1&&(i.gok_max??0)<=.5,r=n.treffer.slice(0,60),o=n.treffer.filter(d=>d.uebernehmbar).length;return a`
    ${t}
    <p class="klein">${n.treffer.length} Bohrungen im Umkreis von ${_(n.radius,0)} m · ${n.zeit}</p>
    ${i.anzahl?a`<p class=${`klein ${l?"ok":"warnung"}`}>${l?"✓":"⚠"} ${i.anzahl} Bohrungen des Gutachtens auch
      beim Land: Lage ≤ ${_(i.lage_max)} m${i.gok_max!==null?a`, GOK ≤ ${_(i.gok_max)} m`:u}${l?"":" – Lage und GOK prüfen"}</p>`:u}
    ${n.fehler.map(d=>a`<p class="warnung klein">${d.dienst}: ${d.fehler}</p>`)}
    ${pt(n.portale)}
    ${r.length?a`
      <table class="tabelle kompakt sgd">
        <thead><tr><th></th><th>Bohrung</th><th class="zahl">Abstand</th><th class="zahl">GOK</th><th class="zahl">Teufe</th><th>Schichten</th></tr></thead>
        <tbody>
          ${r.map(d=>{const h=`${d.dienst}/${d.id}`;return a`<tr class=${d.gutachten?"doppelt":""}>
              <td>${d.uebernehmbar?a`<input type="checkbox" aria-label=${`${d.name} übernehmen`} .checked=${J.has(h)}
                @change=${c=>{c.target.checked?J.add(h):J.delete(h),m()}}>`:u}</td>
              <td title=${`${d.dienst} · ID ${d.id}${d.datum?` · ${d.datum}`:""}`}>${d.name}</td>
              <td class="zahl">${_(d.abstand,0)}</td>
              <td class="zahl">${_(d.gok)}</td>
              <td class="zahl">${_(d.teufe,1)}</td>
              <td class="klein">${wi(d)}</td>
            </tr>`})}
        </tbody>
      </table>
      ${n.treffer.length>r.length?a`<p class="leise klein">… und ${n.treffer.length-r.length} weitere (Umkreis verkleinern)</p>`:u}`:u}
    ${o?a`<button class="primaer" ?disabled=${!J.size} @click=${fi}>
      Ausgewählte übernehmen (${J.size})</button>
      <p class="leise klein">Nur Bohrungen mit Schichtdaten in BoreholeML (NRW, Baden-Württemberg, Hamburg); sie kommen mit Quelle und Lizenz ins Projekt.</p>`:u}
    ${ki(n)}
    ${n.quellen.map(d=>a`<p class="leise klein">Quelle: ${d.namensnennung} · <a href=${d.beleg} target="_blank" rel="noopener">Dienst</a></p>`)}
    <button class="link klein" @click=${async()=>{const d=await w(()=>k.sgdVerwerfen(s.sig));d&&(O(d),m())}}>Abfrage verwerfen</button>`}function Si(e){const n=s.viewer;n&&(!e.unterlage||e.unterlage.kalibrierung?.gesperrt||!y?n.editor.hilfsmarken({}):n.editor.hilfsmarken({strecke:y.massArt==="strecke"?[y.p1,y.p2]:[],hoehe:y.hoeheArt==="strecke"?[y.h1,y.h2]:[],bezug:y.bezug}))}let _n=!1;function xi(e){const n=e.standort;return W(a`Standort ${p("standort")}`,a`
    <p class="klein"><b>${_(n.x,1)} / ${_(n.y,1)}</b> · EPSG:${n.epsg}</p>
    <p class="leise klein">Georeferenziert über den Punkt: kein Lageplan, keine Kalibrierung – die Bohrungen der Länder
      kommen mit ihren Koordinaten. Ein Gutachten dazu (Schritt Start) wird ein neues Projekt mit Lageplan.</p>
    ${Vn(n.dienste)}`)}let Gn=!1;function _i(e){const n=e.viewer.bohrungen.length,t=e.viewer.bohrungen.filter(i=>i.x===null).length;return e.standort?a`<p class="stand-satz ok">Standort ${Math.round(e.standort.x)} / ${Math.round(e.standort.y)} · EPSG:${e.standort.epsg}
      ${n?a` · ${n} Bohrungen der Länder`:a` · <span class="leise">Bohrungen der Länder unten abfragen</span>`}</p>`:n?t?a`<p class="stand-satz warn">${t} von ${n} Bohrungen ohne Lage – auf dem Plan setzen oder Koordinaten eingeben</p>`:a`<p class="stand-satz ok">✓ Alle ${n} Bohrungen haben eine Lage${e.lage_modus==="reihe"?" (Reihe)":""}
      – jetzt mit den Bohrungen der Länder vergleichen</p>`:u}function Gi(){const e=s.z;et(e),Si(e);const n=e.lage_modus!=="reihe"&&e.unterlage?.art==="plan"&&!!e.unterlage.kalibrierung?.gesperrt;s.punktModus&&!n&&(s.punktModus=!1),s.viewer?.editor.punktModusSetzen(s.punktModus),_n||(_n=!0,window.addEventListener("keydown",r=>{r.key==="Escape"&&s.schritt==="lage"&&s.punktModus&&Ke(!1)}));const t=e.viewer.bohrungen.length>0&&e.viewer.bohrungen.every(r=>r.x!==null),i=e.lage_modus==="koordinaten"&&t&&!e.unterlage,l=Gn||!!(e.gelaende||e.gebaeude);return a`
    <div class="app-panel links">
      ${_i(e)}
      ${e.standort?xi(e):a`
        ${W(a`Lage der Bohrungen ${p("lage_art")}`,a`
          <div class="umschalter">
            <label><input type="radio" name="lagemodus" .checked=${e.lage_modus==="koordinaten"}
              @change=${()=>b([{op:"lage_modus",wert:"koordinaten"}])}> Koordinaten (Lageplan)</label>
            <label><input type="radio" name="lagemodus" .checked=${e.lage_modus==="reihe"}
              @change=${()=>b([{op:"lage_modus",wert:"reihe"}])}> Reihe (Längsschnitt)</label>
          </div>`)}
        ${W(a`Unterlage ${p("unterlage")}`,si(e),!i)}
        ${e.unterlage?W(a`Kalibrieren`,ri(e)):u}
        ${W(a`Bohrungen setzen`,li(e),!i)}`}
      ${W(a`Vergleich mit Bohrungen der Länder${e.sgd?.gegenprobe.anzahl?" ✓":""} ${p("sgd")}`,yi(e))}
      <details class="erweitert" ?open=${l}
        @toggle=${r=>{Gn=r.target.open}}>
        <summary>Erweitert <span class="leise klein">Gelände · Gebäude · Darstellung</span></summary>
        ${W(a`Gelände (DGM)${e.gelaende?.pruefung?.warnungen.length?" ⚠":e.gelaende?" ✓":""} ${p("gelaende")}`,bi(e),!!e.gelaende)}
        ${W(a`Gebäude (LoD2)${e.gebaeude?" ✓":""} ${p("gebaeude")}`,Bi(e),!!e.gebaeude)}
        ${W(a`Darstellung`,a`
          <label class="inline">Ø Bohrsäulen ${p("durchmesser")}
            <input type="number" step="0.1" min="0" class="kurz" placeholder=${`auto ${_(e.durchmesser_auto,1)}`}
              .value=${B(e.durchmesser===null?"":String(e.durchmesser))}
              @change=${r=>b([{op:"durchmesser",wert:K(r)}])}> m</label>
          <p class="leise klein">Je Bohrung im Schritt Bohrungen (Ø Säule). Leer = automatisch nach Modellgröße.</p>`,!1)}
      </details>
      ${e.hinweise.length?a`<div class="hinweisliste">${e.hinweise.map(r=>a`<p class="klein">ℹ ${r}</p>`)}</div>`:u}
    </div>`}const N=(e,n=2)=>e==null?"–":e.toLocaleString("de-DE",{minimumFractionDigits:n,maximumFractionDigits:n}),nt={idw:"IDW",tps:"Dünnplatten-Spline",implizit:"implizit (GemPy)"};let ye=null,tt="",Dn=!1,U={x:"",y:""},un=null;async function Di(){const e=s.sig;if(!e)return;const n=await w(()=>k.analyse(e,100),"Kreuzprobe und Unsicherheit werden gerechnet …");n&&(ye=n,tt=s.modell?.schluessel??"",un=null,n.mitte&&!U.x&&(U={x:String(n.mitte[0]),y:String(n.mitte[1])}),m())}async function it(){const e=s.sig,n=Number(U.x.replace(",",".")),t=Number(U.y.replace(",","."));if(!e||!Number.isFinite(n)||!Number.isFinite(t))return;const i=await w(()=>k.analysePunkt(e,n,t),"Virtuelle Bohrung …");i&&(un=i,m())}function Mi(e){const n=e.kreuzprobe;return a`
    <table class="tabelle kompakt">
      <thead><tr><th>Methode</th><th title="mittlerer Fehler der Schichtgrenzen an der weggelassenen Bohrung">mittl. Fehler [m]</th>
        <th>max. [m]</th><th>Grenzen</th></tr></thead>
      <tbody>${Object.entries(n.methoden).map(([t,i])=>a`
        <tr class=${t===n.methode_modell?"gewaehlt":""}>
          <td>${nt[t]??t}${t===n.methode_modell?a` <span class="leise klein">(Modell)</span>`:u}${t===n.beste?a` <b title="sagt die Bohrungen am besten voraus">★</b>`:u}</td>
          <td class="zahl">${N(i.gesamt.mae)}</td><td class="zahl">${N(i.gesamt.max)}</td><td class="zahl">${i.gesamt.n}</td>
        </tr>`)}</tbody>
    </table>`}function Li(e){const n=e.unsicherheit,t=e.kreuzprobe.methoden[e.kreuzprobe.methode_modell];return a`
    <table class="tabelle kompakt">
      <thead><tr><th>Einheit</th>
        <th title="mittlerer Fehler der Unterkante in der Kreuzprobe">Kreuzprobe [m]</th>
        <th title="Streuung der Unterkante im Mittel über die Fläche (± σ)">σ Unterkante [m]</th>
        <th title="95 % der Fläche liegen darunter">σ 95 % [m]</th>
        <th title="falsch als vorhanden / fehlend vorhergesagt">Ausdehnung</th>
        <th title="Volumen mit 5 %- und 95 %-Wert aus der Messung der Grenzen">Volumen [m³]</th>
        <th title="größte Abweichung der Unterkante zur anderen Interpolation">anders interpoliert [m]</th></tr></thead>
      <tbody>${n.einheiten.map((i,l)=>{const r=t?.einheiten[l],o=r?r.praesenz.falsch_vorhanden+r.praesenz.falsch_fehlend:0;return a`<tr>
          <td>${i.name}</td>
          <td class="zahl">${r?.n?N(r.mae):a`<span class="leise">–</span>`}</td>
          <td class="zahl">${i.unterkante_bezifferbar?N(i.sigma_mittel_m):a`<span class="leise" title="keine Bohrung erreicht die Unterkante">offen</span>`}</td>
          <td class="zahl">${i.unterkante_bezifferbar?N(i.sigma_p95_m):"–"}</td>
          <td class="zahl ${o?"warn":""}">${o?`${o} ×`:"✓"}</td>
          <td class="zahl klein">${Math.round(i.volumen_m3.modell).toLocaleString("de-DE")}${i.volumen_m3.p5!==null?a`<br><span class="leise">${Math.round(i.volumen_m3.p5).toLocaleString("de-DE")}–${Math.round(i.volumen_m3.p95).toLocaleString("de-DE")}</span>`:u}</td>
          <td class="zahl">${N(i.methoden_differenz_m.max)}</td>
        </tr>`})}</tbody>
    </table>`}function Ni(e){const n=e.vorschlaege??[];return n.length?a`
    <h4>Wo die nächste Bohrung am meisten bringt ${p("erkundung")}</h4>
    <table class="tabelle kompakt vorschlag">
      <thead><tr><th>#</th><th>Rechtswert</th><th>Hochwert</th><th>Grund</th><th title="nächste vorhandene Bohrung">Abstand [m]</th><th></th></tr></thead>
      <tbody>${n.map((t,i)=>a`<tr>
        <td>${i+1}</td><td class="zahl">${N(t.x,1)}</td><td class="zahl">${N(t.y,1)}</td><td class="klein">${t.grund}</td>
        <td class="zahl">${N(t.abstand_naechste_bohrung_m,0)}</td>
        <td><button class="link" @click=${()=>{U={x:String(t.x),y:String(t.y)},it()}}>virtuell bohren</button></td></tr>`)}</tbody>
    </table>
    <p class="leise klein">Ein Vorschlag aus der Unsicherheit des Modells – Zugang, Leitungen und Baufeld kennt es nicht.</p>`:u}function Ei(e){const n=un;return a`
    <h4>Virtuelle Bohrung ${p("virtuell")}</h4>
    <div class="zeile knopfzeile">
      <label class="inline">Rechtswert <input class="mittel" .value=${U.x} @input=${t=>{U.x=t.target.value}}></label>
      <label class="inline">Hochwert <input class="mittel" .value=${U.y} @input=${t=>{U.y=t.target.value}}></label>
      <button @click=${it}>Bohren</button>
    </div>
    <p class="leise klein">Im System der Bohrungen${e.epsg?` (EPSG ${e.epsg})`:""}; vorbelegt mit der Mitte des Modells.</p>
    ${n?.fehler?a`<p class="warn">${n.fehler}</p>`:u}
    ${n&&!n.fehler?a`
      <p class="klein">GOK ${N(n.gok_nhn)} m NHN · ${N(n.abstand_m,1)} m von ${n.naechste_bohrung} · <span class="leise">${n.herkunft}</span></p>
      <table class="tabelle kompakt virtuell">
        <thead><tr><th>Tiefe [m]</th><th>Einheit</th><th>Unterkante [m NHN]</th><th>± σ [m]</th><th>95 % [m NHN]</th></tr></thead>
        <tbody>${n.schichten.map(t=>a`<tr>
          <td class="zahl">${N(t.tiefe_oben_m)}–${N(t.tiefe_unten_m)}</td><td>${t.einheit}</td>
          <td class="zahl">${N(t.unten_nhn)}${t.unterkante_offen?a` <span class="leise klein">offen</span>`:u}</td>
          <td class="zahl">${N(t.sigma_unten_m)}</td>
          <td class="zahl klein">${t.unten_95_nhn?`${N(t.unten_95_nhn[0])} … ${N(t.unten_95_nhn[1])}`:"–"}</td></tr>`)}</tbody>
      </table>
      ${n.hinweise.map(t=>a`<p class="leise klein">${t}</p>`)}`:u}`}function Pi(){const e=s.modell;if(!e?.bericht)return u;const n=ye&&tt===e.schluessel?ye:null,t=ye&&!n,i=n;return a`
    <details class="erweitert karte analyse" ?open=${Dn||!!i}
      @toggle=${l=>{Dn=l.target.open}}>
      <summary>Ground Analysis ${p("analyse")} <span class="leise klein">Kreuzprobe · Unsicherheit · virtuelle Bohrung</span></summary>
      <div class="zeile knopfzeile">
        <button class=${i?"":"primaer"} @click=${Di}>${i?"Neu rechnen":"Analyse rechnen"}</button>
        ${t?a`<span class="warn klein">Das Modell hat sich geändert – neu rechnen.</span>`:u}
      </div>
      ${i?.fehler?a`<p class="warn">${i.fehler}</p>`:u}
      ${i&&!i.fehler?a`
        <h4>Kreuzprobe <span class="leise klein">(${i.kreuzprobe.bohrungen} Bohrungen, je eine weggelassen)</span></h4>
        ${Mi(i)}
        ${[...i.kreuzprobe.hinweise,...i.unsicherheit.hinweise].map(l=>a`<p class="hinweis klein">⚑ ${l}</p>`)}
        <h4>Unsicherheit je Einheit <span class="leise klein">(${i.unsicherheit.laeufe} Läufe, ${nt[i.unsicherheit.methode]??i.unsicherheit.methode})</span></h4>
        ${Li(i)}
        <details class="klein"><summary class="leise">Annahmen</summary>
          <ul>${i.unsicherheit.annahmen.map(l=>a`<li>${l}</li>`)}</ul></details>
        ${Ni(i)}
        ${Ei(i)}`:u}
    </details>`}let de=0,X="",at="";const Ie=e=>e.replace(/[<>&"]/g,n=>({"<":"&lt;",">":"&gt;","&":"&amp;",'"':"&quot;"})[n]);async function Ai(){const e=s.sig;if(!e||!s.viewer)return;const n=await w(()=>k.analyseFlaeche(e,de),"Unsicherheit wird gerechnet …");if(n){if(n.fehler){s.viewer.meldung(n.fehler,6e3);return}s.viewer.unsicherheit({name:n.name,punkte:n.punkte,dreiecke:n.dreiecke,sigma:n.sigma,sigma_max:n.sigma_max}),X=n.name,at=s.modell?.schluessel??"",n.hinweis&&s.viewer.meldung(n.hinweis,6e3),m()}}function Ki(){s.viewer?.unsicherheit(null),X="",m()}let be=null,rt="";async function ji(){const e=s.sig;if(!e||!s.viewer)return;const n=await w(()=>k.analyseGrundwasser(e),"Grundwasserfläche …");if(n){if(n.fehler){s.viewer.meldung(n.fehler,6e3);return}be=n,rt=s.modell?.schluessel??"",s.viewer.grundwasser(n.flaeche??null),n.flaeche||s.viewer.meldung(n.hinweise?.[0]??"keine Grundwasserfläche",6e3),m()}}function Ti(){s.viewer?.grundwasser(null),be=null,m()}function Oi(){be&&rt!==(s.modell?.schluessel??"")&&(s.viewer?.grundwasser(null),be=null);const e=be,n=(t,i=2)=>t.toLocaleString("de-DE",{minimumFractionDigits:i,maximumFractionDigits:i});return a`
    <div class="zeile">
      <button @click=${ji}>Grundwasserfläche zeigen</button>${p("grundwasser")}
      ${e?a`<button class="link" @click=${Ti}>Grundwasser ausblenden</button>`:u}
    </div>
    ${e?a`<div class="klein grundwasser">
      <p>${e.gemessen} gemessene${e.trocken?`, ${e.trocken} trockene`:""} von ${e.staende?.length??0} Bohrungen
        ${e.flaeche?a` · ${n(e.flaeche.z_min)} bis ${n(e.flaeche.z_max)} m NHN`:u}
        ${e.kreuzprobe?a` · Kreuzprobe ⌀ ${n(e.kreuzprobe.mae_m)} m, max. ${n(e.kreuzprobe.max_m)} m`:u}</p>
      ${(e.aus_dem_text??[]).length?a`<p>Im Text des Gutachtens (nicht in der Fläche):
        ${e.aus_dem_text.map((t,i)=>a`${i?" · ":""}<span title=${t.evidence}>${t.kind} ${n(t.nhn)} m NHN
          (S. ${t.page+1})</span>`)}</p>`:u}
      ${(e.hinweise??[]).length?a`<ul class="hinweise">${e.hinweise.map(t=>a`<li>${t}</li>`)}</ul>`:u}
    </div>`:u}`}async function Fi(){const e=s.sig,n=s.viewer;if(!e||!n)return;const t=await n.punktWaehlen();if(!t)return;const i=await w(()=>k.analysePunkt(e,t.e,t.n),"Virtuelle Bohrung …");if(!i)return;if(i.fehler){n.meldung(i.fehler,6e3);return}const l=(o,d=2)=>o==null?"–":o.toLocaleString("de-DE",{minimumFractionDigits:d,maximumFractionDigits:d}),r=i.schichten.map(o=>`<tr><td>${l(o.tiefe_oben_m)}–${l(o.tiefe_unten_m)} m</td><td>${Ie(o.einheit)}</td>
    <td>${o.sigma_unten_m===null?o.unterkante_offen?"offen":"–":`± ${l(o.sigma_unten_m)} m`}</td></tr>`).join("");n.tafel("Virtuelle Bohrung",`<p>${l(i.x,1)} / ${l(i.y,1)} · GOK ${l(i.gok_nhn)} m NHN · ${l(i.abstand_m,1)} m von ${Ie(i.naechste_bohrung??"")}</p>
    <table><tr><th>Tiefe</th><th>Einheit</th><th>Unterkante</th></tr>${r}</table>
    <p><i>${Ie(i.herkunft??"")}</i></p>`)}function Hi(){const e=s.modell?.bericht;return!e||s.modell?.fehler?u:(de>=e.einheiten.length&&(de=0),X&&at!==(s.modell?.schluessel??"")&&(s.viewer?.unsicherheit(null),X=""),a`
    <section class="abschnitt-flach analyse-viewer">
      <h3>Ground Analysis im Viewer ${p("analyse")}</h3>
      <div class="zeile">
        <select @change=${n=>{de=Number(n.target.value)}}>
          ${e.einheiten.map((n,t)=>a`<option value=${t} .selected=${t===de}>${n.name}</option>`)}
        </select>
        <button @click=${Ai}>Unsicherheit zeigen</button>
        ${X?a`<button class="link" @click=${Ki}>Unsicherheit ausblenden</button>`:u}
      </div>
      ${X?a`<p class="leise klein">Gezeigt: Unterkante ${X}, gefärbt nach σ (grün sicher, rot unsicher).</p>`:u}
      <div class="zeile"><button @click=${Fi}>Virtuelle Bohrung: Punkt im Viewer wählen</button>${p("virtuell")}</div>
      ${Oi()}
    </section>`)}const Ri={wichte:"γ [kN/m³]",wichte_auftrieb:"γ′ [kN/m³]",reibungswinkel:"φ′ [°]",kohaesion:"c′ [kN/m²]",kohaesion_undrainiert:"cu [kN/m²]",steifemodul:"Es [MN/m²]"},Ii={wassergehalt:"w",wassergehalt_korrigiert:"w (korr.)",fliessgrenze:"wL",ausrollgrenze:"wP",plastizitaetszahl:"IP",konsistenzzahl:"IC",gluehverlust:"Vgl",kalkgehalt:"VCa",trockendichte:"ρd",proctordichte:"ρPr",optimaler_wassergehalt:"wPr",cbr:"CBR",kf:"kf",ton:"T",schluff:"U",sand:"S",kies:"G"};let Se=null,Mn="",Ln=null;async function Vi(){const e=s.sig;if(!e)return;const n=`${e}|${s.modell?.schluessel??""}|${JSON.stringify(s.z?.bodenkennwerte??{})}`;Mn!==n&&(Mn=n,Se=await w(()=>k.bodenkennwerte(e))??null,m())}function Nn(e){return b([{op:"bodenkennwerte",zuordnung:e}])}const $e=e=>e.toLocaleString("de-DE",{maximumFractionDigits:2});function En(e){return Object.entries(e).map(([n,t])=>a`<span class="kw" title=${t.text}>${Ri[n]??n}
    ${t.min!==void 0?t.min===t.max?$e(t.min):`${$e(t.min)}–${$e(t.max)}`:t.text}${t.hinweis?" ⚑":""}</span>`)}function Wi(){if(!s.modell?.bericht)return u;Vi();const e=Se&&!Se.fehler?Se:null;if(!e||!e.zeilen.length&&!e.labor?.proben)return u;const n=s.z?.bodenkennwerte??{},t=Ln??Object.keys(n).length>0,i=Object.fromEntries(Object.entries(e.vorschlag).filter(([,r])=>r.ref).map(([r,o])=>[r,o.ref])),l=r=>e.zeilen.find(o=>o.ref===r);return a`
    <details class="erweitert karte bodenkennwerte" .open=${B(t)}
      @toggle=${r=>{Ln=r.target.open,m()}}>
      <summary>Bodenkennwerte aus dem Gutachten <span class="leise klein">${e.zeilen.length} Zeilen${e.labor?.proben?`, ${e.labor.proben} Laborproben`:""}${Object.keys(n).length?`, ${Object.keys(n).length} zugeordnet`:""}</span></summary>
      <p class="klein leise">Werte des Gutachters (Tabelle im Bericht), nicht von GroundTwin festgelegt.
        ${p("bodenkennwerte")}</p>
      ${!Object.keys(n).length&&Object.keys(i).length?a`
        <div class="hb-vorschlag"><p class="klein"><b>Vorschlag</b></p>
          <table class="tabelle kompakt"><tbody>${e.einheiten.map(r=>a`<tr><td><b>${r}</b></td>
            <td>${e.vorschlag[r]?.ref?l(e.vorschlag[r].ref)?.bezeichnung||"(ohne Bezeichnung)":"–"}</td>
            <td class="leise klein">${e.vorschlag[r]?.grund??""}</td></tr>`)}</tbody></table>
          <button @click=${()=>Nn(i)}>Vorschlag übernehmen</button>
        </div>`:u}
      ${e.zeilen.length?a`<table class="tabelle kompakt">
        <thead><tr><th>Einheit</th><th>Zeile im Gutachten</th></tr></thead>
        <tbody>${e.einheiten.map(r=>a`<tr><td>${r}</td><td>
          <select @change=${o=>{const d=o.target.value,h={...n};d?h[r]=d:delete h[r],Nn(Object.keys(h).length?h:null)}}>
            <option value="" .selected=${!n[r]}>– keine –</option>
            ${e.zeilen.map(o=>a`<option value=${o.ref} .selected=${n[r]===o.ref}>
              S. ${o.seite+1}: ${(o.bezeichnung||"(ohne Bezeichnung)").slice(0,60)}</option>`)}
          </select>
          ${n[r]&&l(n[r])?a`<div class="klein">${En(l(n[r]).werte)}</div>`:u}
        </td></tr>`)}</tbody>
      </table>`:u}
      ${e.labor?.proben?a`<h4 class="klein">Laborwerte (${e.labor.proben} Proben aus den Anlagen, gemessen)</h4>
        <table class="tabelle kompakt"><tbody>${Object.entries(e.labor.je_einheit).map(([r,o])=>a`<tr>
          <td>${r}</td><td>${Object.entries(o).map(([d,h])=>a`<span class="kw">${Ii[d]??d} ${h.text}</span>`)}</td>
        </tr>`)}</tbody></table>
        ${e.labor.ohne_schicht.length?a`<p class="klein warn">An keiner Schicht des Modells:
          ${e.labor.ohne_schicht.map(r=>`${r.bohrungen.join("+")} ${$e(r.von)}–${$e(r.bis)} m`).join("; ")}</p>`:u}`:u}
      ${e.zeilen.length?a`<details class="klein"><summary>Alle Zeilen aus dem Gutachten</summary>
        <table class="tabelle kompakt"><tbody>${e.zeilen.map(r=>a`<tr>
          <td class="leise">S. ${r.seite+1}</td><td>${r.bezeichnung||"(ohne Bezeichnung)"}</td>
          <td>${En(r.werte)}${r.hinweise.length?a`<div class="leise">⚑ ${r.hinweise.join("; ")}</div>`:u}</td>
        </tr>`)}</tbody></table>
      </details>`:u}
    </details>`}let q=null,Ve=!1,D="DIN 18300",We=null;async function Pn(){q||Ve||(Ve=!0,q=await w(()=>k.homogenbereicheDaten())??null,Ve=!1,m())}let Z=null,nn="";async function An(){const e=s.sig;if(!e)return;const n=`${D}|${s.modell?.schluessel??""}`;nn!==n&&(nn=n,Z=await w(()=>k.hbVorschlag(e,D))??null,m())}let he=null,Kn="";async function Ui(){const e=s.sig;if(!e)return;const n=`${D}|${s.modell?.schluessel??""}|${JSON.stringify(s.z?.homogenbereiche?.[D]??{})}`;Kn!==n&&(Kn=n,he=await w(()=>k.hbKennwerte(e,D))??null,m())}function te(e){return b([{op:"homogenbereiche",atv:D,zuordnung:e}])}function Ci(){const e=s.modell?.bericht;if(!e)return u;const n=s.z?.homogenbereiche??{},t=n[D]??{},i=e.einheiten.map(g=>g.name),l=We??Object.keys(n).length>0;l&&Pn();const r=q?q.kennwerte.filter(g=>q.matrix[D]?.[g.nr]):[],o=[];for(const g of i){const z=t[g];if(!z)continue;let S=o.find($=>$.name===z);S||o.push(S={name:z,einheiten:[]}),S.einheiten.push(g)}l&&!Object.keys(t).length&&An();const d=Z&&!Z.fehler&&Z.atv===D?Z:null;l&&Ui();const h=he&&!he.fehler&&he.atv===D?he:null,c=Object.keys(t).filter(g=>!i.includes(g)),v=i.filter(g=>!t[g]);return a`
    <details class="erweitert karte homogenbereiche" .open=${B(l)}
      @toggle=${g=>{We=g.target.open,We&&Pn()}}>
      <summary>Homogenbereiche (VOB/C) <span class="leise klein">${Object.keys(n).length?Object.keys(n).join(", "):"Einheiten je Gewerk zuordnen"}</span></summary>
      <div class="einstellung">
        <span>Gewerk (ATV) ${p("homogenbereiche")}</span>
        <select @change=${g=>{D=g.target.value,Z=null,m()}}>
          ${(q?.atv??[{code:"DIN 18300",gewerk:"Erdarbeiten"}]).map(g=>a`
            <option value=${g.code} .selected=${g.code===D}>${g.code} ${g.gewerk}${n[g.code]?" ✓":""}</option>`)}
        </select>
      </div>
      ${d?.gutachten&&!Object.keys(t).length?a`
        <div class="hb-vorschlag">
          <p class="klein"><b>Bereiche des Gutachtens für ${D}</b></p>
          <table class="tabelle kompakt">
            <tbody>${d.gutachten.bereiche.map(g=>a`<tr><td><b>${g.name}</b> ${g.titel}
              <div class="leise klein">${g.bodengruppen.join(", ")}${g.seite!==void 0?` · S. ${g.seite+1}`:""}</div></td>
              <td>${g.einheiten.length?g.einheiten.join(", "):a`<span class="warn">keine Einheit des Modells</span>`}</td>
              <td class="leise klein">${g.einheiten.length?g.grund:""}</td></tr>`)}</tbody>
          </table>
          ${d.gutachten.einheiten_ohne_bereich.length?a`<p class="klein warn">Ohne Bereich des Gutachtens:
            ${d.gutachten.einheiten_ohne_bereich.map(g=>`${g.einheit} (${g.grund})`).join("; ")}</p>`:u}
          <button @click=${()=>te(d.gutachten.zuordnung)}>Bereiche des Gutachtens übernehmen</button>
          <span class="leise klein">danach je Einheit änderbar</span>
        </div>`:u}
      ${d&&!Object.keys(t).length?a`
        <div class="hb-vorschlag">
          <p class="klein"><b>${d.gutachten?"Eigener Vorschlag":"Vorschlag"} für ${D}</b> <span class="leise">(${d.stufe}: ${d.regel})</span></p>
          <table class="tabelle kompakt">
            <tbody>${d.bereiche.map(g=>a`<tr><td><b>${g.name}</b></td><td>${g.einheiten.join(", ")}</td>
              <td class="leise klein">${g.grund}</td></tr>`)}</tbody>
          </table>
          <button @click=${()=>te(d.zuordnung)}>Vorschlag übernehmen</button>
          <span class="leise klein">danach je Einheit änderbar</span>
        </div>`:u}
      <table class="tabelle kompakt hb-zuordnung">
        <thead><tr><th>Einheit</th><th>Homogenbereich</th></tr></thead>
        <tbody>${e.einheiten.map(g=>a`<tr>
          <td><span class="farbfeld" style=${`background:${g.farbe}`}></span> ${g.name}</td>
          <td><input class="kurz" list="hb-namen" placeholder="–" .value=${B(t[g.name]??"")}
            @change=${z=>{const S=z.target.value.trim(),$={...t};S?$[g.name]=S:delete $[g.name],te(Object.keys($).length?$:null)}}></td></tr>`)}</tbody>
      </table>
      <datalist id="hb-namen">${o.map(g=>a`<option value=${g.name}></option>`)}</datalist>
      <div class="zeile knopfzeile">
        <button class="link" @click=${()=>te(Object.fromEntries(i.map((g,z)=>[g,`B${z+1}`])))}
          title="Je Einheit ein eigener Bereich (B1, B2, … von oben); zusammenfassen durch gleiche Namen">Vorschlag: je Einheit ein Bereich</button>
        <button class="link" @click=${async()=>{nn="",await An(),Z?.zuordnung&&await te(Z.zuordnung)}}
          title="Einheiten, die sich für dieses Gewerk gleich verhalten, in einem Bereich (Begründung oben, wenn noch nichts zugeordnet ist)">Vorschlag für ${D}</button>
        ${Object.keys(t).length?a`<button class="link" @click=${()=>te(null)}>Zuordnung ${D} löschen</button>`:u}
      </div>
      ${c.length?a`<p class="warn klein">Zugeordnet, aber nicht mehr im Modell: ${c.join(", ")}</p>`:u}
      ${o.length?a`
        <p class="klein">${o.map(g=>a`<b>${g.name}</b>: ${g.einheiten.join(", ")}<br>`)}
          ${v.length?a`<span class="warn">ohne Bereich: ${v.join(", ")}</span>`:u}</p>`:u}
      ${r.length?a`
        <h4>Kennwerte für ${D} (${r.length})</h4>
        <ul class="klein hb-kennwerte">${r.map(g=>{const z=q.matrix[D][g.nr];return a`<li>${g.nr} ${g.name}${z!=="erforderlich"?a` <span class="leise">(${z})</span>`:u}</li>`})}</ul>
        <p class="leise klein">Quelle der Matrix: ${q.quelle}</p>`:u}
      ${h?a`
        <h4>Aus den Beschreibungen ${p("hb_kennwerte")}</h4>
        ${h.bereiche.map(g=>a`
          <details class="hb-werte">
            <summary><b>${g.name}</b>${g.ohne_bereich?a` <span class="leise">(ohne Bereich)</span>`:u}
              <span class="leise klein">${g.einheiten.join(", ")} · ${g.belegt} von ${g.verlangt} Kennwerten angesprochen ·
                ${g.schichten} Schichten</span></summary>
            <table class="tabelle kompakt">
              <tbody>${g.kennwerte.map(z=>a`<tr>
                <td>${z.nr} ${z.name}</td>
                <td class=${z.wert?"":"leise"}>${z.wert??"offen – nicht im Extrakt"}</td></tr>`)}</tbody>
            </table>
          </details>`)}
        <p class="leise klein">Ansprache aus den Schichtbeschreibungen mit dem Anteil der Schichten; keine Laborwerte.
          Offene Kennwerte stehen im Text oder in den Anlagen des Gutachtens. Das IFC trägt beides je Bereich.</p>`:u}
      <div class="einstellung">
        <span>IFC-Modell</span>
        <label class="inline"><input type="radio" name="hb-modell" .checked=${!s.z?.hb_modell}
          @change=${()=>b([{op:"hb_modell",wert:null}])}> Einheiten</label>
        ${Object.keys(n).map(g=>a`<label class="inline"><input type="radio" name="hb-modell"
          .checked=${s.z?.hb_modell===g} @change=${()=>b([{op:"hb_modell",wert:g}])}>
          Homogenbereiche ${g}</label>`)}
      </div>
      <p class="leise klein">Mit Einheiten trägt jede Einheit und jede Bodenschicht der Bohrsäulen ein Pset je ATV
        (CPset_Homogenbereich_…). Mit Homogenbereichen besteht das Modell aus den Bereichen (gleiche Körper, je Bereich
        zusammengefasst).</p>
    </details>`}const I=(e,n=1)=>e==null?"–":e.toLocaleString("de-DE",{minimumFractionDigits:n,maximumFractionDigits:n});let ie="",Ue=null,jn="",Tn=!1;function Zi(e){return!e||e.quelle!=="DGM"?"aus den GOK der Bohrungen":`aus dem DGM (an den Bohrungen auf die GOK, GOK − DGM bis ${I(Number(e.gok_minus_dgm_max_m),2)} m)`}function qi(){const e=s.z.einstellungen,n=(r,o)=>b([{op:"einstellungen",[r]:o}]),t=(r,o,d,h,c)=>{const v=e[r];return a`
      <div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${v===null} @change=${g=>n(r,g.target.checked?null:h)}> ${o} automatisch</label>${p(c)}
        ${v===null?u:a`<input type="number" step="any" class="kurz" .value=${B(String(v))}
          @change=${g=>n(r,Number(g.target.value))}> ${d}`}
      </div>`},i=s.modell?.bericht?.parameter??{},l=e.methode!=="idw"||e.puffer!==null||e.raster!==null||e.basis!==null||!e.gok_relativ||!e.gelaende_dgm;return a`
    <details class="erweitert karte" ?open=${Tn||l}
      @toggle=${r=>{Tn=r.target.open}}>
      <summary>Erweitert <span class="leise klein">Interpolation · Puffer · Raster · Basis · Gelände</span></summary>
      <div class="einstellung">
        <span>Interpolation ${p("methode")}</span>
        <label class="inline"><input type="radio" name="methode" .checked=${e.methode==="idw"} @change=${()=>n("methode","idw")}> IDW</label>
        <label class="inline"><input type="radio" name="methode" .checked=${e.methode==="tps"} @change=${()=>n("methode","tps")}> Dünnplatten-Spline</label>
        <label class="inline" title=${s.info?.implizit?"GemPy: je Fläche ein Skalarfeld, Orientierung aus den Kontakten (docs/27)":"GemPy ist auf diesem Server nicht installiert (requirements-analyse.txt)"}><input
          type="radio" name="methode" ?disabled=${!s.info?.implizit&&e.methode!=="implizit"} .checked=${e.methode==="implizit"}
          @change=${()=>n("methode","implizit")}> Implizit (GemPy)</label>
      </div>
      ${e.methode==="implizit"?Ji():u}
      ${t("puffer","Puffer","m",Number(i.puffer_m??20),"puffer")}
      ${t("raster","Raster","m",Number(i.raster_m??5),"raster")}
      ${t("basis","Modellbasis","m NHN",Math.floor(Number(i.basis_nhn??0)),"basis")}
      <div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${e.gok_relativ} @change=${r=>n("gok_relativ",r.target.checked)}> fehlende GOK: Gelände = 0 m</label>${p("gok_relativ")}
      </div>
      ${s.z.gelaende?a`<div class="einstellung">
        <label class="inline"><input type="checkbox" .checked=${e.gelaende_dgm} @change=${r=>n("gelaende_dgm",r.target.checked)}> Gelände aus dem DGM</label>${p("gelaende_dgm")}
      </div>`:u}
      ${i.raster_m!==void 0?a`<p class="leise klein">gerechnet: Puffer ${I(Number(i.puffer_m),0)} m · Raster ${I(Number(i.raster_m))} m ·
        Basis ${I(Number(i.basis_nhn),2)} m NHN · Fläche ${I(Number(i.flaeche_m2)/1e4,2)} ha ·
        Gelände ${Zi(i.gelaende)}</p>`:u}
    </details>`}function Ji(){const e=s.modell?.bericht,n=e?.parameter?.orientierung??[];if(!e||!n.length)return a`<p class="leise klein">Orientierung je Einheit: nach dem Rechnen hier eingebbar.</p>`;const t={...s.z.einstellungen.orientierung??{}},i=(r,o,d)=>{const h=t[r]??{fallrichtung:NaN,fallwinkel:NaN},c=d.trim()===""?NaN:Number(d.replace(",",".")),v={...h,[o]:c};if(Number.isNaN(v.fallrichtung)&&Number.isNaN(v.fallwinkel))delete t[r];else if(Number.isNaN(v.fallrichtung)||Number.isNaN(v.fallwinkel)){t[r]=v;return}else t[r]=v;const g=Object.fromEntries(Object.entries(t).filter(([,z])=>!Number.isNaN(z.fallrichtung)&&!Number.isNaN(z.fallwinkel)));b([{op:"einstellungen",orientierung:Object.keys(g).length?g:null}])},l=(r,o,d,h)=>a`
    <input type="number" step="any" min="0" max=${o==="fallwinkel"?80:360} class="kurz" title=${h}
      placeholder="–" .value=${B(d===void 0||Number.isNaN(d)?"":String(d))}
      @change=${c=>i(r,o,c.target.value)}>`;return a`
    <div class="einstellung">
      <span>Orientierung je Einheit ${p("orientierung")}</span>
      <table class="klein orientierung">
        <thead><tr><th>Einheit</th><th>berechnet</th><th>Fallrichtung °</th><th>Fallwinkel °</th></tr></thead>
        <tbody>${n.map(r=>a`<tr>
          <td>${r.einheit}</td>
          <td class="leise">${r.quelle==="Eingabe"?"Eingabe":r.fallen_grad===null?r.quelle:`${I(r.fallen_grad,1)}°${r.fallrichtung_grad!=null?` nach ${I(r.fallrichtung_grad,0)}°`:""} (${r.quelle})`}</td>
          <td>${l(r.einheit,"fallrichtung",t[r.einheit]?.fallrichtung,"Fallrichtung: Azimut von Nord im Uhrzeigersinn")}</td>
          <td>${l(r.einheit,"fallwinkel",t[r.einheit]?.fallwinkel,"Fallwinkel gegen die Horizontale, 0–80°")}</td>
        </tr>`)}</tbody>
      </table>
    </div>`}function Qi(){const e=s.modell?.bericht;if(!e)return u;const n=s.z.vorgabe??e.vorlage_einheiten,t=JSON.stringify(n);(!Ue||jn!==t)&&(Ue=n.map(r=>({name:r.name,bodenarten:r.bodenarten.join(", ")})),jn=t);const i=Ue,l=()=>b([{op:"vorgabe",wert:i.filter(r=>r.name.trim()).map(r=>({name:r.name.trim(),bodenarten:r.bodenarten.split(",").map(o=>o.trim()).filter(Boolean)}))}]);return a`
    <section class="karte">
      <h3>Einheiten festlegen ${p("einheiten")}</h3>
      <p class="leise klein">${s.z.vorgabe?"Vorgegeben (eigene Einheiten).":"Automatisch korreliert – hier umbenennen oder Bodenarten zusammenlegen."}</p>
      <table class="tabelle kompakt vorgabe">
        <colgroup><col class="pfeil"><col><col><col class="weg"></colgroup>
        <thead><tr><th></th><th>Einheit</th><th>Bodenarten (mit Komma)</th><th></th></tr></thead>
        <tbody>
          ${i.map((r,o)=>a`
            <tr>
              <td class="pfeile"><button class="symbol" ?disabled=${o===0} @click=${()=>{i.splice(o-1,0,...i.splice(o,1)),m()}}>▲</button><button
                class="symbol" ?disabled=${o===i.length-1} @click=${()=>{i.splice(o+1,0,...i.splice(o,1)),m()}}>▼</button></td>
              <td><input .value=${B(r.name)} @input=${d=>{r.name=d.target.value}}></td>
              <td><input .value=${B(r.bodenarten)} @input=${d=>{r.bodenarten=d.target.value}}></td>
              <td><button class="symbol" title="Zeile löschen" @click=${()=>{i.splice(o,1),m()}}>✕</button></td>
            </tr>`)}
        </tbody>
      </table>
      <div class="zeile knopfzeile">
        <button class="link" @click=${()=>{i.push({name:"",bodenarten:""}),m()}}>+ Zeile</button>
        <span class="fueller"></span>
        <button ?disabled=${!s.z.vorgabe} @click=${()=>b([{op:"vorgabe",wert:null}])}>Automatisch korrelieren</button>
        <button class="primaer" @click=${l}>Mit diesen Einheiten rechnen</button>
      </div>
    </section>`}function Yi(){const e=s.modell,n=e?.bericht,t=n?.einheiten.find(i=>i.name===ie);return a`
    <div class="schritt-einheiten">
      <div class="spalte">
        ${Qi()}
        ${Ci()}
        ${Wi()}
        ${qi()}
      </div>
      <div class="spalte breit">
        ${s.rechnet?a`<div class="karte"><div class="kreisel klein"></div> Modell wird gerechnet …</div>`:u}
        ${e?.fehler?a`<div class="karte warnung">Noch kein Modell: ${e.fehler}
          <button class="link" @click=${()=>C("lage")}>→ Lage setzen</button></div>`:u}
        ${n?a`
          <section class="karte">
            <h3>Einheiten (${n.einheiten.length})</h3>
            <table class="tabelle einheiten">
              <thead><tr><th></th><th>Einheit</th><th>Bodenarten</th><th>Volumen [m³]</th><th>max. Mächtigkeit [m]</th>
                <th title="in Bohrungen vorhanden / fehlt / unter der Endteufe">✓ / – / ?</th><th>Hinweise</th></tr></thead>
              <tbody>
                ${n.einheiten.map(i=>a`
                  <tr class=${i.name===ie?"gewaehlt":""} @click=${()=>{ie=ie===i.name?"":i.name,m()}}>
                    <td><span class="farbfeld" style=${`background:${i.farbe}`}></span></td>
                    <td><b>${i.name}</b></td>
                    <td>${i.bodenarten.join(", ")}</td>
                    <td class="zahl">${Math.round(i.volumen_m3).toLocaleString("de-DE")}</td>
                    <td class="zahl">${I(i.maechtigkeit_max_m,2)}</td>
                    <td class="zahl">${i.bohrungen.vorhanden.length} / ${i.bohrungen.fehlt.length} / ${i.bohrungen.unbekannt.length}</td>
                    <td class="klein">${i.hinweise.join("; ")}</td>
                  </tr>`)}
              </tbody>
            </table>
          </section>
          <section class="karte profil-karte">
            <h3>Einheiten je Bohrung <span class="leise klein">(m NHN, Klick wählt die Einheit)</span></h3>
            <div class="profil-scroll">${Nt(n,{hoehe:380,gewaehlt:ie,waehlen:i=>{ie=i,m()}})}</div>
          </section>
          ${t?a`
            <section class="karte">
              <h3><span class="farbfeld" style=${`background:${t.farbe}`}></span> ${t.name}: Beschreibungen aus dem PDF</h3>
              <table class="tabelle kompakt">
                <thead><tr><th>Bohrung</th><th>Tiefe [m]</th><th>Bodenart</th><th>Beschreibung</th></tr></thead>
                <tbody>${t.schichten.map(i=>a`
                  <tr><td>${i.bohrung}</td><td class="zahl">${I(i.von,2)}–${I(i.bis,2)}</td><td>${i.bodenart??"unklassifiziert"}</td>
                    <td>${i.beschreibung||a`<span class="leise">–</span>`}</td></tr>`)}</tbody>
              </table>
            </section>`:u}
          ${Pi()}`:u}
      </div>
    </div>`}let je="";async function Xi(){const e=await w(()=>k.einchecken(s.sig,je));e&&(O(e.zustand),je="",A(`Eingecheckt: v${e.eintrag.nr} · ${e.eintrag.stand.bohrungen[0]}/${e.eintrag.stand.bohrungen[1]} Bohrungen geprüft`,"ok"),m())}const st=new Set([25831,25832,25833,4647,5650]);let ge=(()=>{try{return localStorage.getItem("groundtwin.organisation")??""}catch{return""}})();function ea(){const e=s.z,n=e.bohrungen.filter(l=>l.modell),t=n.filter(l=>l.schichten_n>0&&l.schichten_geprueft===l.schichten_n&&l.x!==null&&l.y!==null&&l.epsg!==null&&st.has(l.epsg)&&l.gok!==null&&e.lage_modus==="koordinaten"),i=`${k.exportUrl(s.sig,"boreholeml")}?organisation=${encodeURIComponent(ge)}`;return a`
    <label class="feld breit"><span>Organisation (Absender) ${p("boreholeml")}</span>
      <input type="text" aria-label="Organisation für BoreholeML" placeholder="z. B. Ingenieurbüro …" .value=${ge}
        @input=${l=>{ge=l.target.value;try{localStorage.setItem("groundtwin.organisation",ge)}catch{}m()}}></label>
    ${t.length?a`<a class="knopf" href=${i} download>Bohrungen für den Geologischen Dienst (BoreholeML 3.2)</a>`:a`<span class="knopf aus" title="Erst alle Schichten prüfen; Lage in ETRS89/UTM und GOK nötig">Bohrungen für den Geologischen Dienst (BoreholeML 3.2)</span>`}
    <p class="leise klein">${t.length} von ${n.length} Bohrungen exportierbar (vollständig geprüft, ETRS89/UTM, GOK).</p>`}let fe=!1;async function na(){if(!fe){fe=!0,m();try{const e=await fetch(k.exportUrl(s.sig,"3dtiles"));if(!e.ok){const i=await e.text();let l=i;try{l=JSON.parse(i).detail??i}catch{}A(`3D Tiles: ${l}`,"fehler",1e4);return}const n=/filename\*=UTF-8''([^;]+)/.exec(e.headers.get("content-disposition")??"")?.[1],t=document.createElement("a");t.href=URL.createObjectURL(await e.blob()),t.download=n?decodeURIComponent(n):"baugrundmodell_3dtiles.zip",t.click(),setTimeout(()=>URL.revokeObjectURL(t.href),1e4),A("3D Tiles exportiert (tileset.json + GLB, Höhen ellipsoidisch mit GCG2016).","ok")}finally{fe=!1,m()}}}function ta(){const e=s.z;return e.lage_modus==="koordinaten"&&e.viewer.epsg!==null&&st.has(e.viewer.epsg)?a`<button class="knopf" ?disabled=${fe} @click=${na}>${fe?"3D Tiles werden erstellt …":"Baugrundmodell für Cesium (3D Tiles, ZIP)"}</button>${p("tiles3d")}`:a`<span class="knopf aus" title="Nur mit Lage nach Koordinaten in ETRS89/UTM">Baugrundmodell für Cesium (3D Tiles, ZIP)</span>`}const ia={anzeige:"Anzeige",fachdaten:"Fachdaten",bewertungsdaten:"Bewertungsdaten"},aa=e=>e.split("-").reverse().join(".");function ra(e){return!e.bis||e.tage===null?e.regel:`bis ${aa(e.bis)} (${e.tage>0?`noch ${e.tage} Tage`:e.tage===0?"heute":"verstrichen"})`}function sa(){const e=s.z.geoldg,n=e.zusammenfassung,t=(r,o)=>b([{op:"geoldg",[r]:o}],{leise:!0}),i=`${k.exportUrl(s.sig,"geoldg")}?organisation=${encodeURIComponent(ge)}`,l=e.punkte.filter(r=>r.quelle==="protokoll").map(r=>r.titel.replace(/, falls durchgeführt$/,""));return a`
    <section class="abschnitt-flach geoldg">
      <h3>Geologischer Dienst (GeolDG) ${p("geoldg")}</h3>
      <div class="zeile">
        <label class="inline">Beginn <input type="date" aria-label="Beginn der Untersuchung" .value=${e.angaben.beginn}
          @change=${r=>t("beginn",r.target.value)}></label>
        <label class="inline">Abschluss <input type="date" aria-label="Abschluss der Untersuchung" .value=${e.angaben.abschluss}
          @change=${r=>t("abschluss",r.target.value)}></label>${p("geoldg_abschluss")}
      </div>
      <label class="inline"><input type="checkbox" aria-label="Auftraggeber ist eine Behörde" .checked=${e.angaben.behoerde}
        @change=${r=>t("behoerde",r.target.checked)}> Auftraggeber ist eine Behörde</label>
      <ul class="fristen">${e.fristen.map(r=>a`
        <li class=${r.tage!==null&&r.tage<0?"warn":""} data-frist=${r.id}><b>${ia[r.id]}</b>
          <a href=${r.url} target="_blank" rel="noopener">${r.beleg}</a>: ${ra(r)}</li>`)}</ul>
      ${e.vorerkundung?a`
        <p class="klein">Noch keine eigene Bohrung: die geplante Erkundung spätestens zwei Wochen vor Beginn anzeigen
          (<a href=${e.anzeige_inhalt.url} target="_blank" rel="noopener">§ 8</a>). ${e.anzeige_inhalt.aus_der_app}</p>`:n.eigene?a`
        <p class="klein geoldg-stand">${n.eigene} eigene Bohrungen: für <b>${n.bereit}</b> liefert GroundTwin Lage, GOK, Endteufe
          und das geprüfte Schichtenverzeichnis, <b>${n.boreholeml}</b> davon im BoreholeML.${n.fremd?` ${n.fremd} Bohrungen der Länder liegen dem Land schon vor.`:""}</p>
        ${n.offen.length?a`<details class="protokoll"><summary class="warnung">⚠ ${n.offen.length} Bohrung(en) offen</summary>
          <ul>${n.offen.map(r=>a`<li><b>${r.code}</b>: ${r.was}</li>`)}</ul></details>`:u}
        <p class="klein leise">Aus dem Bohrprotokoll ergänzen (Spalten in pruefliste.csv): ${l.join(" · ")}.</p>
        <a class="knopf" href=${i} download>Paket für den Geologischen Dienst (ZIP)</a>`:u}
      <p class="leise klein">${e.quelle.hinweis}</p>
    </section>`}let On=!1;function la(){const e=s.z,n=s.modell,t=n?.bericht,i=e.pruefstand,l=e.eincheckungen[e.eincheckungen.length-1],r=[["ifc","Baugrundmodell (IFC 4.3)"],["bericht","Prüfbericht (JSON)"]],o=[["einheiten","Einheiten-Vorlage (JSON)"],["extraktion","Extraktion (JSON)"],["eingabe","Modell-Eingabe mit Korrekturen (JSON)"],["projekt","Projektstand (JSON)"],["agsi","Informationspaket AGSi (ZIP)"]],d=On||!!(e.geoldg?.angaben.beginn||e.geoldg?.angaben.abschluss);return a`
    <div class="app-panel rechts">
      <section class="abschnitt-flach">
        <h3>Modell</h3>
        ${e.reifegrad.stufe!=="Gutachten"?a`<p class=${`reife ${e.reifegrad.stufe==="Vorerkundung"?"vorerkundung":"gemischt"}`}>
          <b>${e.reifegrad.stufe}</b> – ${e.reifegrad.stufe==="Vorerkundung"?"Bohrungen aus Datenbanken der Länder, kein Gutachten: eine erste Vorstellung für die Planung der Erkundung.":Object.entries(e.reifegrad.anzahl).map(([h,c])=>`${c} ${h}`).join(", ")+": Bohrungen ohne Gutachten sind nicht gegen ein PDF geprüft."}
          ${p("reifegrad")}</p>`:u}
        ${s.rechnet?a`<p><span class="kreisel klein"></span> wird gerechnet …</p>`:u}
        ${n?.fehler?a`<p class="warnung">Noch kein Modell: ${n.fehler}</p>
          <button class="link" @click=${()=>C("lage")}>→ Lage setzen</button>`:u}
        ${t?a`
          <ul class="kennzahlen">
            <li><b>${t.einheiten.length}</b> Einheiten</li>
            <li><b>${t.bohrungen.length}</b> Bohrungen im Modell</li>
            <li class=${t.epsg?"":"warn"}>${t.epsg?`EPSG:${t.epsg}`:"lokales System"}</li>
            <li class=${t.pruefungen.alle_koerper_geschlossen?"ok":"warn"}>${t.pruefungen.alle_koerper_geschlossen?"Körper geschlossen":"Körper offen"}</li>
            <li class=${t.pruefungen.max_abweichung_an_bohrungen_m<.01?"ok":"warn"}>Abweichung an Bohrungen ${t.pruefungen.max_abweichung_an_bohrungen_m.toFixed(3)} m</li>
          </ul>`:u}
        <div class="zeile">
          <label class="inline"><input type="checkbox" .checked=${e.auto} @change=${h=>b([{op:"auto",wert:h.target.checked}],{leise:!0})}>
            automatisch nachführen</label>${p("auto")}
          <span class="fueller"></span>
          <button ?disabled=${s.rechnet} @click=${()=>dt()}>Neu rechnen</button>
        </div>
      </section>

      <section class="abschnitt-flach">
        <h3>Prüfstand ${p("pruefstand")}</h3>
        <div class="balken"><span>Bohrungen <b>${i.bohrungen[0]}/${i.bohrungen[1]}</b></span><progress max=${i.bohrungen[1]||1} value=${i.bohrungen[0]}></progress></div>
        <div class="balken"><span>Schichten <b>${i.schichten[0]}/${i.schichten[1]}</b></span><progress max=${i.schichten[1]||1} value=${i.schichten[0]}></progress></div>
        <p class="klein">${i.unklassifiziert_offen?a`<span class="warnung">⚠ ${i.unklassifiziert_offen} Schicht(en) nicht klassifiziert</span>
          <button class="link" @click=${()=>C("bohrungen")}>prüfen</button>`:a`<span class="ok">✓ keine offenen Warnungen</span>`}
          · ${i.korrigiert} korrigiert · ${i.manuelle_lage} Lagen manuell · ${i.entfernt} entfernt</p>
        <p class=${`klein ${l&&!e.seit_einchecken_geaendert?"ok":"warn"}`}>
          ${l?`Eingecheckt: ${e.eingecheckt}${e.seit_einchecken_geaendert?" · seitdem geändert":""}`:"noch nicht eingecheckt"}</p>
        <div class="zeile">
          <input class="breit" placeholder="Kommentar (z. B. BK1–BK5 mit Anlage 2 verglichen)" .value=${je}
            @input=${h=>{je=h.target.value}}>
        </div>
        <div class="zeile"><button class="primaer" @click=${Xi}>✓ Stand einchecken</button>${p("einchecken")}</div>
        ${e.eincheckungen.length?a`
          <details class="protokoll"><summary>Protokoll (${e.eincheckungen.length})</summary>
            <ul>${[...e.eincheckungen].reverse().map(h=>a`
              <li><b>v${h.nr}</b> ${h.zeit} · ${h.stand.bohrungen[0]}/${h.stand.bohrungen[1]} Bohrungen, ${h.stand.schichten[0]}/${h.stand.schichten[1]} Schichten
                ${h.kommentar?a`<div class="leise klein">${h.kommentar}</div>`:u}</li>`)}</ul>
          </details>`:u}
      </section>

      <section class="abschnitt-flach">
        <h3>Export ${p("export")}</h3>
        <div class="export-liste">
          ${r.map(([h,c])=>a`<a class=${`knopf ${h==="ifc"?"primaer":""}`} href=${k.exportUrl(s.sig,h)}
            download>${c}</a>`)}
        </div>
      </section>

      <details class="erweitert" ?open=${d}
        @toggle=${h=>{On=h.target.open}}>
        <summary>Erweitert <span class="leise klein">Exporte · Cesium · BoreholeML · GeolDG · Ground Analysis · Darstellung</span></summary>
        <section class="abschnitt-flach">
          <h3>Weitere Exporte</h3>
          <div class="export-liste">
            ${o.map(([h,c])=>a`<a class="knopf" href=${k.exportUrl(s.sig,h)} download>${c}</a>`)}
            ${ta()}
            ${ea()}
          </div>
        </section>
        ${sa()}
        ${Hi()}
        <section class="abschnitt-flach">
          <h3>Darstellung</h3>
          <label class="inline">Überhöhung ${p("ueberhoehung")}
            <select @change=${async h=>{const c=Number(h.target.value);await s.viewer?.ueberhoehen(c),await b([{op:"ueberhoehung",wert:c}],{leise:!0})}}>
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
    </div>`}const Fn={gutachten:"",bohrungen:"Weiter: Lage",lage:"Weiter: Einheiten",einheiten:"Weiter: Modell",modell:""};function oa(e){const n=s.z;if(!n)return"";const t=n.pruefstand;return e==="gutachten"?"ok":e==="bohrungen"?t.unklassifiziert_offen?"warn":t.bohrungen[0]===t.bohrungen[1]&&t.bohrungen[1]?"ok":"":e==="lage"?n.viewer.bohrungen.filter(l=>l.x===null).length?"warn":"ok":e==="einheiten"||e==="modell"?s.modell?.fehler?"warn":s.modell?.bericht?"ok":"":""}function ua(){const e=s.z;return a`
    <header class="kopf">
      <div class="marke" @click=${()=>C("gutachten")} title="Start">
        <span class="logo">⛰</span>
        <span><b>GroundTwin</b> · Baugrundmodell</span>
      </div>
      <nav class="schritte" aria-label="Schritte">
        ${Be.map(n=>{const t=n.id!=="gutachten"&&!e,i=oa(n.id);return a`
            <button class=${`schritt-knopf ${s.schritt===n.id?"aktiv":""} ${i}`} ?disabled=${t}
              aria-current=${s.schritt===n.id?"step":"false"} @click=${()=>C(n.id)} title=${n.kurz}>
              <span class="nr">${i==="ok"&&s.schritt!==n.id?"✓":i==="warn"?"!":n.nr}</span>
              <span class="titel">${n.titel}</span>
            </button>`})}
      </nav>
      <div class="projekt">
        ${e&&e.reifegrad.stufe!=="Gutachten"?a`<span class=${`abzeichen ${e.reifegrad.stufe==="Vorerkundung"?"vorerkundung":"gemischt"}`}
          title=${e.reifegrad.stufe==="Vorerkundung"?"Bohrungen aus Datenbanken der Länder, kein Gutachten":"Gutachten und Bohrungen der Länder"}>${e.reifegrad.stufe}</span>`:u}
        ${e?a`<span class="projektname" title=${e.dokumente.map(n=>n.datei).join(", ")}>${e.name}</span>
          <details class="menue">
            <summary title="Projekt">⋯</summary>
            <div class="menue-inhalt" @click=${ca}>
              <button @click=${()=>C("gutachten")}>Anderes Projekt öffnen</button>
              <button @click=${da}>Alle Korrekturen verwerfen …</button>
              <a href="viewer.html" target="_blank" rel="noopener">Viewer allein öffnen</a>
              <a href="dienste.html" target="_blank" rel="noopener">Dienste der Länder (Werkzeug)</a>
              ${s.info?a`<a href=${s.info.quellcode} target="_blank" rel="noopener">Quellcode (${s.info.lizenz})</a>`:u}
            </div>
          </details>`:u}
      </div>
    </header>`}function ca(e){e.currentTarget.closest("details")?.removeAttribute("open")}document.addEventListener("click",e=>{for(const n of document.querySelectorAll("details.menue[open]"))n.contains(e.target)||n.removeAttribute("open")});async function da(){if(!s.sig||!confirm("Alle Korrekturen, Lagen, Prüfhaken und Eincheckungen dieses Projekts verwerfen – auch übernommene Bohrungen der Länder, DGM und Gebäude? Der Name bleibt."))return;const e=await w(()=>k.zuruecksetzen(s.sig));e&&await se(s.sig,e.standort?"lage":"bohrungen")}function ha(){if(s.schritt==="gutachten")return u;const e=Be.findIndex(l=>l.id===s.schritt),n=Be[e-1],t=Be[e+1],i=s.z?.pruefstand;return a`
    <footer class="fuss">
      ${n?a`<button @click=${()=>C(n.id)}>← ${n.titel}</button>`:u}
      <span class="fuss-status">${i?`${i.bohrungen[0]}/${i.bohrungen[1]} Bohrungen · ${i.schichten[0]}/${i.schichten[1]} Schichten geprüft`:""}
        ${i?.unklassifiziert_offen?a` · <span class="warnung">⚠ ${i.unklassifiziert_offen} nicht klassifiziert</span>`:u}</span>
      <span class="fueller"></span>
      ${t&&Fn[s.schritt]?a`<button class="primaer" @click=${()=>C(t.id)}>${Fn[s.schritt]} →</button>`:u}
    </footer>`}function ga(){return s.schritt==="gutachten"||!s.z?Gt():s.schritt==="bohrungen"?Xt():s.schritt==="lage"?Gi():s.schritt==="einheiten"?Yi():la()}function pa(){return a`
    ${ua()}
    <main class=${`inhalt schritt-${s.schritt}`}>
      <section id="schritt" class="schritt">${ga()}</section>
    </main>
    ${ha()}
    <div class="meldungen" aria-live="polite">
      ${s.meldungen.map(e=>a`<div class=${`meldung ${e.art}`}>${e.text}</div>`)}
    </div>
    ${s.beschaeftigt?a`<div class="beschaeftigt"><div class="kreisel"></div><span>${s.beschaeftigt}</span></div>`:u}`}const Hn=document.getElementById("app");let ae=null;function ma(){ut(pa(),Hn);const e=Hn.querySelector("main");ae||(ae=document.createElement("div"),ae.id="buehne",ae.className="buehne"),ae.parentElement!==e&&e.append(ae),document.body.dataset.schritt=s.schritt}ht(ma);async function lt(){const[e,n,t]=location.hash.replace(/^#\/?/,"").split("/").map(decodeURIComponent);if(e&&e!==s.sig){if(await se(e,n||void 0),t&&s.schritt==="bohrungen"){const{bohrungWaehlen:i}=await Ce(async()=>{const{bohrungWaehlen:l}=await import("./store-Db7Mh03B.js").then(r=>r.k);return{bohrungWaehlen:l}},__vite__mapDeps([1,2]),import.meta.url);await i(t)}}else e||await C("gutachten")}window.addEventListener("hashchange",()=>void lt());s.info=await w(()=>k.info())??null;m();await Rn();await lt();window.app=s;
