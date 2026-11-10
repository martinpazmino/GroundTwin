import"./viewer-DAT6rRHi.js";/* empty css            */import{D as N,b as l,A as u}from"./lit-element-BS0sz3Y2.js";const O={"wfs-kopf":"WFS – nur Kopfdaten","wfs-boreholeml":"WFS – BoreholeML mit Schichten","wms-kopf":"WMS – nur Hinweis (Kopfdaten)","wcs-dgm":"WCS – DGM","lod2-kacheln":"LoD2-Kacheln","portal-bohrungen":"Portal (Link)","portal-dgm":"Portal (Link)","portal-gebaeude":"Portal (Link)"},S=["id","land","laender","art","status","geprueft","aktiv","titel","anbieter","url","hinweis","lizenz","lizenz_url","namensnennung","beleg"],P=["id","land","art","titel","anbieter","url"],n={reg:null,entwurf:[],gespeichert:"",wahl:-1,technik:"",technikFehler:"",sicht:"alle",suche:"",pruefungen:new Map,alle:null,fehler:"",meldung:""};async function w(e,t){const a=await fetch(e,t);if(!a.ok){let s=`${a.status} ${a.statusText}`;try{const r=await a.json();s=typeof r.detail=="string"?r.detail:JSON.stringify(r.detail)}catch{}throw new Error(s)}return await a.json()}const z=(e,t)=>({method:e,headers:{"Content-Type":"application/json"},body:JSON.stringify(t)});async function T(){try{k(await w("/api/dienste"))}catch(e){n.fehler=`Register nicht lesbar: ${e.message}`}o()}function k(e,t=""){n.reg=e,n.entwurf=structuredClone(e.dienste),n.gespeichert=JSON.stringify(e.dienste),n.wahl=t?n.entwurf.findIndex(a=>a.id===t):-1,$()}const A=()=>!!n.reg&&JSON.stringify(n.entwurf)!==n.gespeichert;async function x(){if(!n.reg)return;const e=n.entwurf[n.wahl]?.id??"";try{k(await w("/api/dienste",z("PUT",{dienste:n.entwurf,version:n.reg.version})),e),n.fehler="",B("Gespeichert – die App fragt ab jetzt mit diesem Stand.")}catch(t){n.fehler=t.message}o()}function F(){!n.reg||!confirm("Alle nicht gespeicherten Änderungen verwerfen?")||(k(n.reg,n.entwurf[n.wahl]?.id??""),n.fehler="",o())}async function L(e){const t=n.entwurf[e];if(!t||!n.reg)return;const a=t.id||`#${e}`;n.pruefungen.set(a,"laeuft"),o();try{const s=n.reg.bearbeiten?{eintrag:t}:{id:t.id};n.pruefungen.set(a,await w("/api/dienste/pruefen",z("POST",s)))}catch(s){n.pruefungen.set(a,{id:t.id,ok:!1,meldung:s.message,dauer_ms:0,gefunden:[]})}o()}async function G(){const e=D().map(({i:r})=>r);n.alle={fertig:0,gesamt:e.length},o();const t=[...e],a=async()=>{for(let r=t.shift();r!==void 0;r=t.shift())await L(r),n.alle.fertig+=1,o()};await Promise.all([a(),a(),a(),a()]);const s=e.filter(r=>n.pruefungen.get(n.entwurf[r]?.id)?.ok===!1).length;n.alle=null,B(s?`${e.length} geprüft, ${s} nicht erreichbar oder unvollständig`:`${e.length} geprüft, alle erreichbar`),o()}function H(e){return n.reg?.arten[e.art]?.thema??""}function b(e){return!!n.reg?.arten[e.art]?.angebunden}function $(){const e=n.entwurf[n.wahl];if(n.technikFehler="",!e){n.technik="";return}const t=Object.fromEntries(Object.entries(e).filter(([a])=>!S.includes(a)));n.technik=Object.keys(t).length?JSON.stringify(t,null,1):"{}"}function v(e){n.wahl=n.wahl===e?-1:e,$(),o(),n.wahl>=0&&document.querySelector(".editor")?.scrollIntoView({block:"nearest",behavior:"smooth"})}function g(e,t){const a=n.entwurf[n.wahl];if(!a)return;const s=r=>!!n.reg?.laender.includes(String(r))&&r!=="Deutschland";e==="land"&&(!a.laender||a.laender.length===1&&a.laender[0]===a.land)&&(s(t)?a.laender=[String(t)]:delete a.laender,$()),t===""||t===void 0?delete a[e]:a[e]=t,e==="art"&&!a.id&&(a.id=E(a.land,String(t))),o()}function K(e){n.technik=e;const t=n.entwurf[n.wahl];try{const a=JSON.parse(e||"{}");if(typeof a!="object"||a===null||Array.isArray(a))throw new Error("ein Objekt { … } erwartet");for(const s of Object.keys(t))S.includes(s)||delete t[s];Object.assign(t,a),n.technikFehler=""}catch(a){n.technikFehler=a.message}o()}const R={"Schleswig-Holstein":"SH",Hamburg:"HH",Niedersachsen:"NI",Bremen:"HB","Nordrhein-Westfalen":"NW",Hessen:"HE","Rheinland-Pfalz":"RP","Baden-Württemberg":"BW",Bayern:"BY",Saarland:"SL",Berlin:"BE",Brandenburg:"BB","Mecklenburg-Vorpommern":"MV",Sachsen:"SN","Sachsen-Anhalt":"ST",Thüringen:"TH",Deutschland:"DE"};function E(e,t){const a=`${R[e]??"XX"}${t.endsWith("dgm")?"-DGM":t.includes("lod2")||t.endsWith("gebaeude")?"-LOD2":""}`,s=new Set(n.entwurf.map(r=>r.id));if(!s.has(a))return a;for(let r=2;;r++)if(!s.has(`${a}-${r}`))return`${a}-${r}`}function j(e="Bayern",t="bohrungen"){const a=`portal-${t}`,s={id:E(e,a),land:e,laender:e==="Deutschland"?void 0:[e],art:a,status:"ungeprueft",titel:"",anbieter:"",url:"https://",hinweis:"",lizenz:"",namensnennung:"",beleg:""};s.laender||delete s.laender,n.entwurf.push(s),n.wahl=n.entwurf.length-1,n.sicht="alle",n.suche="",$(),o(),window.setTimeout(()=>document.querySelector(".editor input[name=titel]")?.focus(),30)}function W(){const e=n.entwurf[n.wahl];!e||!confirm(`Eintrag ${e.id||"(ohne Kennung)"} entfernen? (Erst „Speichern“ schreibt die Datei.)`)||(n.entwurf.splice(n.wahl,1),n.wahl=-1,$(),o())}function J(){const e=n.entwurf[n.wahl];e&&(e.status="geprueft",e.geprueft=new Date().toISOString().slice(0,10),o())}function M(){if(!n.reg)return;const{format:e,stand:t,beschreibung:a}=n.reg,s=new Blob([JSON.stringify({format:e,stand:t,beschreibung:a,dienste:n.entwurf},null,1)+`
`],{type:"application/json"}),r=Object.assign(document.createElement("a"),{href:URL.createObjectURL(s),download:"dienste.json"});r.click(),window.setTimeout(()=>URL.revokeObjectURL(r.href),1e3)}let y=0;function B(e){n.meldung=e,window.clearTimeout(y),y=window.setTimeout(()=>{n.meldung="",o()},4500)}function m(e,t){return n.pruefungen.get(e.id||`#${t}`)}function U(e,t){const a=m(e,t);if(n.sicht==="angebunden"&&!b(e)||n.sicht==="links"&&b(e)||n.sicht==="ungeprueft"&&e.status==="geprueft"||n.sicht==="fehler"&&!(a&&a!=="laeuft"&&!a.ok))return!1;const s=n.suche.trim().toLowerCase();return!s||[e.id,e.titel,e.anbieter,e.url,e.land,e.hinweis].some(r=>String(r??"").toLowerCase().includes(s))}function D(){return n.entwurf.map((e,t)=>({d:e,i:t})).filter(({d:e,i:t})=>U(e,t))}function I(){const e=n.entwurf,t=e.filter((a,s)=>{const r=m(a,s);return r&&r!=="laeuft"&&!r.ok}).length;return{alle:e.length,angebunden:e.filter(b).length,links:e.filter(a=>!b(a)).length,ungeprueft:e.filter(a=>a.status!=="geprueft").length,fehler:t}}function C(e,t,a){const s=m(e,t),r=e.land!==a&&a!=="Deutschland",d=["chip",b(e)?"chip-angebunden":"chip-portal",e.status==="geprueft"?"chip-geprueft":"chip-offen",e.aktiv===!1?"chip-aus":"",n.wahl===t?"chip-gewaehlt":"",s&&s!=="laeuft"?s.ok?"chip-ok":"chip-kaputt":""].filter(Boolean).join(" "),i=`${e.titel||"(ohne Titel)"}
${b(e)?"angebunden: die App fragt selbst ab":"Link zum Portal"} · ${e.status==="geprueft"?`geprüft ${e.geprueft??""}`:"ungeprüft"}${e.aktiv===!1?" · abgeschaltet":""}${r?`
Dienst von ${e.land}`:""}${s&&s!=="laeuft"?`
Prüfung: ${s.meldung}`:""}`;return l`<button class=${d} title=${i} @click=${()=>v(t)} aria-pressed=${n.wahl===t}>
    <span class="punkt" aria-hidden="true"></span>${e.id||"neu"}${r?l`<span class="fremd">↗</span>`:u}
    ${s==="laeuft"?l`<span class="pruef laeuft" aria-label="wird geprüft">…</span>`:s?l`<span class=${`pruef ${s.ok?"ja":"nein"}`}>${s.ok?"✓":"✗"}</span>`:u}</button>`}function _(){const e=n.reg,t=Object.entries(e.themen),a=n.sicht!=="alle"||n.suche.trim()!=="",s=e.laender.map(r=>{const d=t.map(([i])=>D().filter(({d:c})=>H(c)===i&&(r==="Deutschland"?c.land==="Deutschland":c.land!=="Deutschland"&&(c.laender?.length?c.laender.includes(r):c.land===r))));return{land:r,zellen:d}}).filter(r=>!a||r.zellen.some(d=>d.length));return l`
    <table class="matrix">
      <thead><tr><th scope="col">Land</th>${t.map(([,r])=>l`<th scope="col">${r}</th>`)}</tr></thead>
      <tbody>
        ${s.map(({land:r,zellen:d})=>l`<tr>
          <th scope="row">${r}</th>
          ${d.map((i,c)=>l`<td>
            <div class="zelle">${i.map(({d:h,i:f})=>C(h,f,r))}
              ${e.bearbeiten?l`<button class="plus" title=${`Neuer Eintrag: ${r}, ${t[c][1]}`}
                aria-label=${`Neuer Eintrag ${r} ${t[c][1]}`} @click=${()=>j(r,t[c][0])}>+</button>`:u}
              ${!i.length&&!e.bearbeiten?l`<span class="leer">–</span>`:u}
            </div></td>`)}
        </tr>`)}
        ${s.length?u:l`<tr><td colspan=${t.length+1} class="leise">Kein Eintrag passt zum Filter.</td></tr>`}
      </tbody>
    </table>`}function p(e,t,a,s="text",r=""){const d=!n.reg.bearbeiten,i=P.includes(e)||(n.reg.arten[a.art]?.pflicht??[]).includes(e),c=String(a[e]??""),h=i&&!c.trim();return l`<label class=${`eingabe ${h?"fehlt":""}`}>
    <span>${t}${i?l`<i title="Pflichtangabe">*</i>`:u}</span>
    ${s==="lang"?l`<textarea name=${e} rows="3" ?disabled=${d} .value=${c}
          @input=${f=>g(e,f.target.value)}></textarea>`:l`<input name=${e} type=${s==="url"?"url":"text"} ?disabled=${d} .value=${c} spellcheck="false"
          @input=${f=>g(e,f.target.value)} />`}
    ${r?l`<small class="leise">${r}</small>`:u}
  </label>`}function Z(){const e=n.reg,t=n.entwurf[n.wahl];if(!t)return l`<aside class="editor leer-editor">
      <p class="gross">Eintrag wählen</p>
      <p class="leise">Ein Klick auf einen Eintrag der Tabelle zeigt ihn hier – ${e.bearbeiten?"zum Bearbeiten und Prüfen":"zum Ansehen und Prüfen"}.</p>
      <ul class="legende">
        <li><span class="chip chip-angebunden chip-geprueft"><span class="punkt"></span>BE</span> angebunden: die App fragt den Dienst selbst ab</li>
        <li><span class="chip chip-portal chip-offen"><span class="punkt"></span>BY</span> Link zum Portal (ansehen, herunterladen, anfragen)</li>
        <li><span class="chip chip-portal chip-geprueft"><span class="punkt"></span>…</span> grün umrandet: geprüft (mit Datum)</li>
        <li><span class="chip chip-portal chip-offen"><span class="punkt"></span>…<span class="fremd">↗</span></span> Dienst eines Nachbarlandes, gilt auch hier</li>
      </ul>
    </aside>`;const a=!e.bearbeiten,s=m(t,n.wahl),r=(e.arten[t.art]?.pflicht??[]).filter(i=>t[i]===void 0||t[i]===""||Array.isArray(t[i])&&!t[i].length),d=[!0,!1].map(i=>Object.entries(e.arten).filter(([,c])=>c.angebunden===i));return l`<aside class="editor" aria-label="Eintrag">
    <div class="editor-kopf">
      <div>
        <h2>${t.id||"Neuer Eintrag"}</h2>
        <p class="leise klein">${b(t)?"angebunden – die App fragt selbst ab":"Link zum Portal"} ·
          ${t.status==="geprueft"?l`<span class="ok">geprüft ${t.geprueft??""}</span>`:"ungeprüft"}
          ${t.aktiv===!1?l` · <span class="warn">abgeschaltet</span>`:u}</p>
      </div>
      <button class="symbol" title="Schließen (Esc)" aria-label="Schließen" @click=${()=>v(n.wahl)}>✕</button>
    </div>
    <div class="adresse">
      <a class="knopf" href=${t.url} target="_blank" rel="noopener noreferrer" ?hidden=${!/^https?:\/\/[^{]+$/.test(t.url)}>Öffnen ↗</a>
      <button class="primaer" @click=${()=>L(n.wahl)} ?disabled=${s==="laeuft"}>
        ${s==="laeuft"?"Prüft …":"Prüfen"}</button>
      ${!a&&s&&s!=="laeuft"&&s.ok&&t.status!=="geprueft"?l`<button @click=${J}>Als geprüft markieren</button>`:u}
    </div>
    ${s&&s!=="laeuft"?l`<div class=${`ergebnis ${s.ok?"ja":"nein"}`} role="status">
      <b>${s.ok?"✓":"✗"}</b> ${s.meldung}${s.dauer_ms?l` <span class="leise">(${(s.dauer_ms/1e3).toFixed(1)} s)</span>`:u}
      ${s.gefunden.length?l`<details><summary>${s.gefunden.length} gefunden</summary><p class="klein">${s.gefunden.join(", ")}</p></details>`:u}
    </div>`:u}
    <div class="formular">
      ${p("id","Kennung",t,"text","Großbuchstaben, Ziffern, „-“ (z. B. BY-DGM)")}
      <label class="eingabe"><span>Land<i>*</i></span>
        <input name="land" list="laenderliste" ?disabled=${a} .value=${t.land} spellcheck="false"
          @input=${i=>g("land",i.target.value)} />
        <datalist id="laenderliste">${e.laender.map(i=>l`<option value=${i}></option>`)}</datalist>
        <small class="leise">Name zum Anzeigen (z. B. „Brandenburg mit Berlin“); wo der Eintrag gilt:
          ${(t.laender??[]).length?(t.laender??[]).join(", "):t.land==="Deutschland"?"alle Länder":"aus dem Land"}
          (Technische Angaben, „laender“)</small></label>
      <label class="eingabe"><span>Art<i>*</i></span>
        <select ?disabled=${a} .value=${t.art} @change=${i=>g("art",i.target.value)}>
          ${d.map((i,c)=>l`<optgroup label=${c===0?"angebunden (die App fragt ab)":"nur Link"}>
            ${i.map(([h,f])=>l`<option value=${h} ?selected=${h===t.art}>${e.themen[f.thema]} – ${O[h]??h}</option>`)}
          </optgroup>`)}
        </select></label>
      ${p("titel","Titel",t)}
      ${p("anbieter","Anbieter",t)}
      ${p("url","Adresse",t,"url",t.art==="lod2-kacheln"?"mit {e} und {n} (Kilometer Ost/Nord der Kachel)":"")}
      ${p("hinweis","Hinweis",t,"lang")}
      ${p("lizenz","Lizenz",t)}
      ${p("lizenz_url","Lizenz-Adresse",t,"url")}
      ${p("namensnennung","Namensnennung",t,"text","{jahr} wird beim Abruf ersetzt")}
      ${p("beleg","Beleg (wo steht das?)",t,"url")}
      <div class="eingabe zwei">
        <label><span>Status</span>
          <select ?disabled=${a} .value=${t.status==="geprueft"?"geprueft":"ungeprueft"}
            @change=${i=>g("status",i.target.value)}>
            <option value="ungeprueft" ?selected=${t.status!=="geprueft"}>ungeprüft</option>
            <option value="geprueft" ?selected=${t.status==="geprueft"}>geprüft</option>
          </select></label>
        <label><span>Geprüft am</span>
          <input type="date" ?disabled=${a} .value=${String(t.geprueft??"")}
            @change=${i=>g("geprueft",i.target.value)} /></label>
      </div>
      <label class="inline schalter"><input type="checkbox" ?disabled=${a} .checked=${t.aktiv!==!1}
        @change=${i=>g("aktiv",i.target.checked?void 0:!1)} />
        In der App verwenden</label>
      <details class="technik" ?open=${r.length>0}>
        <summary>Technische Angaben${r.length?l` – <span class="warn">fehlt: ${r.join(", ")}</span>`:u}</summary>
        <p class="leise klein">JSON: Länder, Gebiet, Typen, Systeme, Felder, Coverage … (Länder und Gebiet ergänzt der Server aus dem Land).</p>
        <textarea class="json" rows="10" spellcheck="false" ?disabled=${a} .value=${n.technik}
          @input=${i=>K(i.target.value)}></textarea>
        ${n.technikFehler?l`<p class="warn klein">Kein gültiges JSON: ${n.technikFehler}</p>`:u}
      </details>
      ${a?u:l`<div class="zeile"><span class="fueller"></span>
        <button class="gefahr" @click=${W}>Eintrag entfernen …</button></div>`}
    </div>
  </aside>`}function V(){const e=n.reg;if(!e)return l`<div class="werkzeug-rahmen"><p class=${n.fehler?"warn":"leise"}>${n.fehler||"Register wird geladen …"}</p></div>`;const t=I(),a=[["alle","Alle",t.alle],["angebunden","Angebunden",t.angebunden],["links","Links",t.links],["ungeprueft","Ungeprüft",t.ungeprueft],["fehler","Nicht erreichbar",t.fehler]];return l`
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
        <p class="leise klein">Datei <code>${e.datei}</code> · Stand ${e.stand} · ${e.format}</p>
        ${e.bearbeiten?u:l`<p class="nur-lesen" role="note">Nur lesen – ${e.grund}</p>`}
      </section>
      <div class="werkzeugleiste">
        <div class="segmente" role="group" aria-label="Ansicht">
          ${a.map(([s,r,d])=>l`<button class=${n.sicht===s?"aktiv":""} aria-pressed=${n.sicht===s}
            ?disabled=${s==="fehler"&&!d} @click=${()=>{n.sicht=s,o()}}>${r} <span class="zahl">${d}</span></button>`)}
        </div>
        <input type="search" class="register-suche" placeholder="Suchen: Kennung, Titel, Adresse …" aria-label="Suchen" .value=${n.suche}
          @input=${s=>{n.suche=s.target.value,o()}} />
        <span class="fueller"></span>
        <button @click=${G} ?disabled=${!!n.alle} title="Jeden sichtbaren Eintrag einmal ansprechen">
          ${n.alle?`Prüft ${n.alle.fertig}/${n.alle.gesamt} …`:"Alle prüfen"}</button>
        <button @click=${M} title="Den Stand dieser Seite als dienste.json herunterladen">Als Datei</button>
        ${e.bearbeiten?l`<button class="primaer" @click=${()=>j()}>+ Neuer Eintrag</button>`:u}
      </div>
      ${n.fehler?l`<div class="speicherfehler" role="alert"><b>Nicht gespeichert:</b> ${n.fehler}</div>`:u}
      <div class="arbeitsflaeche">
        <div class="tabelle">${_()}</div>
        ${Z()}
      </div>
    </div>
    ${A()?l`<div class="speicherleiste" role="region" aria-label="Ungespeicherte Änderungen">
      <span>Änderungen nicht gespeichert</span>
      <button @click=${F}>Verwerfen</button>
      <button class="primaer" @click=${x}>Speichern</button>
    </div>`:u}
    ${n.meldung?l`<div class="werkzeug-meldung" role="status">${n.meldung}</div>`:u}`}const Y=document.getElementById("werkzeug");function o(){N(V(),Y)}document.addEventListener("keydown",e=>{e.key==="Escape"&&n.wahl>=0&&!e.target.closest?.("textarea")&&v(n.wahl)});window.addEventListener("beforeunload",e=>{A()&&e.preventDefault()});o();await T();window.werkzeug=n;
