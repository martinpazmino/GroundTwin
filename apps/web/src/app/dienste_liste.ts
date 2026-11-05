// Dienste der Länder an einem Ort (Karte, Standort, Abfrage): angebundene als Text, Portale als Link. „ungeprüft“ bleibt
// sichtbar (Adresse eingetragen, nicht gegen den Dienst getestet) - nie still als geprüft ausgeben.
import { html, nothing } from "lit";
import type { DienstAmOrt, Sgd } from "./api";

const ungeprueft = html`<span class="ungeprueft" title="Adresse eingetragen, nicht gegen den Dienst geprüft">ungeprüft</span>`;

export function dienstListe(dienste: DienstAmOrt[], beschriftung = "Dienste am Standort") {
  return html`<ul class="dienste klein" aria-label=${beschriftung}>${dienste.map((d) => html`<li class=${d.art}>
    ${d.url ? html`<a href=${d.url} target="_blank" rel="noopener noreferrer">${d.text}</a>` : d.text}
    ${d.status === "ungeprueft" ? ungeprueft : nothing}</li>`)}</ul>`;
}

/** Länder im Umkreis ohne Datendienst (Abfrage der Bohrungen): ihr Portal und die Bohrpunktkarte der BGR. */
export function portalListe(portale: Sgd["portale"]) {
  if (!portale?.length) return nothing;
  const laender = [...new Set(portale.map((p) => p.land).filter((l) => l !== "Deutschland"))];
  return html`<div class="portale" role="note">
    <p class="klein">Kein Datendienst für ${laender.length ? laender.join(", ") : "diesen Ort"} – die Bohrungen im Portal ansehen:</p>
    <ul class="dienste klein" aria-label="Portale der Länder">${portale.map((p) => html`<li>
      <a href=${p.url} target="_blank" rel="noopener noreferrer">${p.titel}</a> <span class="leise">(${p.land})</span>
      ${p.status === "ungeprueft" ? ungeprueft : nothing}
      ${p.hinweis ? html`<div class="leise">${p.hinweis}</div>` : nothing}</li>`)}</ul>
  </div>`;
}
