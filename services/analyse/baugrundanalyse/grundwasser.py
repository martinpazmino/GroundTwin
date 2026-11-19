"""Grundwasserflaeche aus den Wasserstaenden der Bohrungen (docs/27 G5).

Eine Flaeche durch die gemessenen Wasserstaende (m NHN = GOK - Tiefe), mit derselben Interpolation wie das
Schichtmodell (implizit: Spline, eine Wasserflaeche hat keine Orientierung aus Schichtkontakten). Sie liest das Modell
und die Extraktion und aendert nichts; ins IFC geht sie nicht.

Was markiert wird, nie verborgen:
- trockene Bohrungen ("kein Grundwasser", W2) sind Daten: liegt die Flaeche dort ueber der Endteufe, widersprechen
  sie ihr (Widerspruch je Bohrung);
- die Flaeche ueber dem Gelaende (gespanntes Wasser, Staende verschiedener Tage);
- mehrere Staende in einer Bohrung: die Art mit Vorrang gilt (Ruhewasser vor nach Bohrende vor unbestimmt vor
  Anschnitt, ``baugrundmodell.wasser``), darin der hoechste; die Spanne steht dabei. Schichtenwasser geht nie in die
  Flaeche und wird je Bohrung genannt (Issue #26);
- verschiedene Arten oder Tage zwischen den Bohrungen: der Hinweis nennt, was gemischt ist;
- relative GOK: die Wasserstaende sind dann auch relativ.

Bohrzeit-Wasserstaende sind Momentaufnahmen verschiedener Tage und Jahreszeiten: kein Bemessungswasserstand.
"""
from __future__ import annotations

import numpy as np
from baugrundmodell import wasser
from baugrundmodell.flaechen import interpolieren

UEBER_GELAENDE = 0.05          # m: so weit darf die Flaeche ueber dem Gelaende liegen, ehe es gemeldet wird
SPANNE = 0.10                  # m: ab hier sind mehrere Staende einer Bohrung eine Meldung wert
MIN_KREUZPROBE = 4             # gemessene Staende, ab denen die Kreuzprobe etwas sagt
HINWEIS_ZEIT = ("Wasserstände zur Bohrzeit (verschiedene Tage und Jahreszeiten) – Lage des Wassers zur Anschauung, "
                "kein Bemessungswasserstand")


def _trocken(status: str) -> bool:
    s = (status or "").lower()
    return s.startswith("kein") or "trocken" in s or "nicht angetroffen" in s


def staende(m, docs: list[dict]) -> list[dict]:
    """Je Bohrung des Modells: gemessen (z, Tiefe, Spanne), trocken (bis Endteufe) oder ohne Angabe."""
    je = {(d["document"]["file"], b["code"]): b for d in docs for b in d["boreholes"]}
    out = []
    for bi, b in enumerate(m.bohrungen):
        q = je.get((b.dokument, b.code)) or {}
        alle = [g for g in q.get("groundwater") or [] if g.get("depth") is not None]
        wart, gew = wasser.wahl(alle)
        tiefen = sorted(float(g["depth"]) for g in gew)
        e = {"bohrung": bi, "code": b.code, "relativ": b.hoehe == "relativ",
             "schichtenwasser": sorted(round(float(g["depth"]), 2) for g in alle
                                       if wasser.art(g.get("kind")) == "Schichtenwasser")}
        if tiefen:
            oben = min(gew, key=lambda g: float(g["depth"]))
            e.update(art="gemessen", wasserart=wart, datum=oben.get("observed_on"), tiefe_m=round(tiefen[0], 2),
                     z=round(b.gok - tiefen[0], 2), spanne_m=round(tiefen[-1] - tiefen[0], 2), staende=len(tiefen),
                     andere_arten=sorted({wasser.art(g.get("kind")) for g in alle} - {wart, "Schichtenwasser"}))
        elif _trocken(q.get("groundwater_status")):
            e.update(art="trocken", bis_z=round(b.ende, 2))
        else:
            e.update(art="ohne Angabe")
        out.append(e)
    return out


def _methode(m) -> str:
    x = m.parameter.get("methode", "idw")
    return x if x in ("idw", "tps") else "tps"


def grundwasser(m, docs: list[dict]) -> dict:
    """Flaeche an den Knoten des Modells, Pruefungen und Hinweise; ohne gemessenen Stand: nur die Staende."""
    st = staende(m, docs)
    gem = [s for s in st if s["art"] == "gemessen"]
    hinweise: list[str] = []
    out = {"staende": st, "gemessen": len(gem), "trocken": sum(s["art"] == "trocken" for s in st),
           "methode": _methode(m), "hinweise": hinweise, "z": None, "widersprueche": [], "kreuzprobe": None,
           # Bemessungswasserstand, HGW, MHGW aus dem Text des Gutachtens: zur Anschauung daneben, nie in der Flaeche
           "aus_dem_text": [{**w, "dokument": d["document"]["file"]} for d in docs for w in d.get("wasserstaende") or []]}
    if not gem:
        hinweise.append("keine Bohrung mit gemessenem Wasserstand – keine Grundwasserfläche")
        return out
    xy = m.punkte[[s["bohrung"] for s in gem]]
    z = np.array([s["z"] for s in gem], float)
    if len(gem) == 1:
        flaeche = np.full(len(m.punkte), z[0])
        hinweise.append(f"nur ein Wasserstand ({gem[0]['code']}): Fläche waagerecht angenommen")
    else:
        flaeche = interpolieren(m.punkte, xy, z, out["methode"])
    out["z"] = flaeche
    # trockene Bohrungen: Wasser tiefer als die Endteufe; liegt die Flaeche hoeher, widersprechen sie
    for s in st:
        if s["art"] == "trocken":
            hier = float(flaeche[s["bohrung"]])
            if hier > s["bis_z"]:
                out["widersprueche"].append({"code": s["code"], "trocken_bis_z": s["bis_z"], "flaeche_z": round(hier, 2),
                                             "differenz_m": round(hier - s["bis_z"], 2)})
    if out["widersprueche"]:
        hinweise.append(f"{len(out['widersprueche'])} trockene Bohrung(en) widersprechen der Fläche: "
                        + ", ".join(f"{w['code']} (+{w['differenz_m']:.2f} m)".replace(".", ",") for w in out["widersprueche"]))
    ueber = flaeche - m.flaechen[0] > UEBER_GELAENDE
    if ueber.any():
        hinweise.append(f"an {int(ueber.sum())} von {len(flaeche)} Knoten über dem Gelände (gespanntes Wasser oder Stände "
                        "verschiedener Tage)")
    out["ueber_gelaende_knoten"] = int(ueber.sum())
    breit = [s for s in gem if s["spanne_m"] > SPANNE]
    if breit:
        hinweise.append("mehrere Stände in " + ", ".join(f"{s['code']} (Spanne {s['spanne_m']:.2f} m)".replace(".", ",")
                                                         for s in breit) + ": der höchste der Art mit Vorrang gilt")
    sw = [s for s in st if s["schichtenwasser"]]
    if sw:
        hinweise.append("Schichtenwasser nicht in der Fläche: " + ", ".join(
            f"{s['code']} ({', '.join(f'{d:.2f}' for d in s['schichtenwasser'])} m)".replace(".", ",") for s in sw))
    arten = sorted({s["wasserart"] for s in gem})
    if len(arten) > 1:
        hinweise.append("Arten gemischt: " + "; ".join(
            f"{wasser.TEXT[a]}: " + ", ".join(s["code"] for s in gem if s["wasserart"] == a) for a in arten))
    elif arten == ["unbestimmt"]:
        hinweise.append("Art der Wasserstände im Gutachten nicht angegeben (Anschnitt oder Ruhewasser offen)")
    tage = sorted({s["datum"] for s in gem if s.get("datum")})
    if len(tage) > 1:
        hinweise.append(f"Stände von {len(tage)} Tagen ({tage[0]} bis {tage[-1]})")
    if any(s["relativ"] for s in gem):
        hinweise.append("relative GOK: Wasserstände dort ebenso relativ")
    if len(gem) >= MIN_KREUZPROBE:
        fehler = []
        for i in range(len(gem)):
            rest = [k for k in range(len(gem)) if k != i]
            v = float(interpolieren(xy[i:i + 1], xy[rest], z[rest], out["methode"])[0])
            fehler.append({"code": gem[i]["code"], "fehler_m": round(v - z[i], 2)})
        a = np.abs([f["fehler_m"] for f in fehler])
        out["kreuzprobe"] = {"mae_m": round(float(a.mean()), 2), "max_m": round(float(a.max()), 2), "je_bohrung": fehler}
    hinweise.append(HINWEIS_ZEIT)
    return out
