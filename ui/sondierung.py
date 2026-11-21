"""Sondierungen im Projekt (Issue #27 Teil 2, docs/05 §6): aus der Stufe services/extractor/sondierungen.py, je Dokument
in ``doc['sondierungen']``. Das Projekt haelt nur, was der Nutzer setzt (``Projekt.sondierung``): Lage, GOK, geprueft,
im Projekt oder entfernt. Nichts davon aendert die gelesenen Werte; die bleiben mit Seite und Beleg nachpruefbar.

GOK: die Ansatzhoehe aus dem PDF (``ansatzhoehe``), sonst eine Eingabe. Lage: eine Eingabe (Rechts-/Hochwert) oder ein
Punkt auf dem gesperrten Lageplan; nie geraten (eine Sondierung neben einer Bohrung gleicher Nummer steht nicht an
deren Stelle).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui.projekt import Projekt

LAGE_VOM_PLAN = ("Plan (kalibriert)",)
FELDER = ("geprueft", "modell", "x", "y", "gok")


def alle(docs: list[dict]) -> list[tuple[str, dict, dict]]:
    """(id, Dokument, Sondierung); id = 'Dokumentindex:S<Index>' (eigener Namensraum neben den Bohrungen)."""
    return [(f"{di}:S{k}", d, s) for di, d in enumerate(docs) for k, s in enumerate(d.get("sondierungen") or [])]


def finden(docs: list[dict], sid: str) -> tuple[dict, dict]:
    for i, d, s in alle(docs):
        if i == sid:
            return d, s
    raise ValueError(f"Sondierung {sid} gibt es nicht")


def _zahl(v) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        raise ValueError(f"keine Zahl: {v}") from None


def setzen(docs: list[dict], p: Projekt, sid: str, feld: str, wert) -> str:
    """Ein Feld setzen; None/'' bei x, y, gok nimmt die Eingabe zurueck. Rueckgabe: Meldung."""
    _, s = finden(docs, sid)
    if feld not in FELDER:
        raise ValueError(f"Feld {feld}: erlaubt {', '.join(FELDER)}")
    o = p.sondierung.setdefault(sid, {})
    if feld in ("geprueft", "modell"):
        o[feld] = bool(wert)
        meldung = {("geprueft", True): "als geprüft markiert", ("geprueft", False): "Prüfung zurückgenommen",
                   ("modell", True): "wieder im Projekt", ("modell", False): "entfernt"}[(feld, bool(wert))]
    else:
        z = _zahl(wert)
        if z is None:
            o.pop(feld, None)
            if feld in ("x", "y"):
                o.pop("quelle", None)
            meldung = f"{feld.upper() if feld == 'gok' else feld}: Eingabe zurückgenommen"
        else:
            if feld == "gok" and not -500 <= z <= 9000:
                raise ValueError("GOK: m NHN zwischen -500 und 9000")
            o[feld] = round(z, 3)
            if feld in ("x", "y"):
                o["quelle"] = "manuell"
            meldung = f"{feld.upper() if feld == 'gok' else feld} = {z:.2f}"
    if not o:
        p.sondierung.pop(sid, None)
    return f"{s['code']}: {meldung}"


def vom_plan(docs: list[dict], p: Projekt, sid: str, x: float, y: float, kal: dict) -> bool:
    """Lage aus dem gesperrten Lageplan; True = eine gesetzte Lage wurde ersetzt."""
    finden(docs, sid)
    o = p.sondierung.setdefault(sid, {})
    ersetzt = o.get("x") is not None
    o.update(x=round(float(x), 3), y=round(float(y), 3), quelle=LAGE_VOM_PLAN[0])
    if kal.get("epsg"):
        o["epsg"] = int(kal["epsg"])
    return ersetzt


def _gok(p: Projekt, sid: str, s: dict) -> tuple[float | None, str]:
    o = p.sondierung.get(sid, {})
    if o.get("gok") is not None:
        return float(o["gok"]), "Eingabe"
    if s.get("ansatzhoehe") is not None:
        return float(s["ansatzhoehe"]), "PDF"
    return None, ""


def _wert(v) -> tuple[float | None, bool]:
    """N10 oder Messwert; zensiert ('> 50') als {'wert', 'zensiert'}."""
    if isinstance(v, dict):
        return (None if v.get("wert") is None else float(v["wert"])), bool(v.get("zensiert"))
    return (None if v is None else float(v)), False


def zeilen(docs: list[dict], p: Projekt) -> list[dict]:
    """Eine Zeile je Sondierung fuer die Schritte Bohrungen und Lage."""
    out = []
    for sid, d, s in alle(docs):
        o = p.sondierung.get(sid, {})
        gok, gok_q = _gok(p, sid, s)
        werte = s.get("werte") or []
        n10 = [w for w, _ in (_wert(r[2]) for r in werte if len(r) >= 3 and s.get("art", "").upper().startswith(("DP", "SRS")))
               if w is not None]
        out.append({
            "id": sid, "code": s.get("code") or "?", "art": s.get("art") or "", "form": s.get("form") or "",
            "dokument": d["document"]["file"], "dokument_index": int(sid.split(":")[0]),
            "seite": s.get("seite"), "quelle": s.get("quelle") or "Text",
            "werte_n": len(werte), "endtiefe": s.get("endtiefe"),
            "endtiefe_aus": "Werte" if werte else ("Achse (≈)" if s.get("endtiefe") is not None else ""),
            "n10_max": max(n10) if n10 else None,
            "zensiert": sum(_wert(r[2])[1] for r in werte if len(r) >= 3),
            "gok": gok, "gok_quelle": gok_q,
            "x": o.get("x"), "y": o.get("y"), "epsg": o.get("epsg"), "lage_aus": o.get("quelle") or "",
            "geprueft": bool(o.get("geprueft")), "entfernt": o.get("modell") is False,
            "konfidenz": s.get("konfidenz"),
            "hinweise": list(s.get("hinweise") or []) + ([] if werte else ["ohne Werte (nur Code und Seite gelesen)"]),
        })
    return out


def detail(docs: list[dict], p: Projekt, sid: str) -> dict:
    """Zeile plus alle Werte und der Beleg (Seite, Rahmen, Methode) fuer die Kurve und den Blick ins PDF."""
    _, s = finden(docs, sid)
    zeile = next(z for z in zeilen(docs, p) if z["id"] == sid)
    return {"sondierung": zeile, "werte": s.get("werte") or [], "beleg": s.get("beleg") or {},
            "einheiten": s.get("einheiten") or ({"N10": "Schläge/10 cm"} if zeile["art"].upper().startswith("DP") else {})}


def pruefstand(docs: list[dict], p: Projekt) -> list[int]:
    """[geprueft, im Projekt]."""
    z = [r for r in zeilen(docs, p) if not r["entfernt"]]
    return [sum(r["geprueft"] for r in z), len(z)]


def viewer(docs: list[dict], p: Projekt) -> list[dict]:
    """Marken fuer den Lage-Editor: Sondierungen im Projekt mit Lage (Rechts-/Hochwert wie die Bohrungen)."""
    return [{"id": z["id"], "code": z["code"], "art": z["art"], "x": z["x"], "y": z["y"],
             "gok": z["gok"], "ende": z["endtiefe"], "geprueft": z["geprueft"]}
            for z in zeilen(docs, p) if not z["entfernt"]]


def fuer_ifc(docs: list[dict], p: Projekt) -> tuple[list[dict], list[dict]]:
    """Sondierungen fuer das IFC (baugrundmodell.modell.ifc_schreiben, Teil 3): im Projekt, mit Lage, GOK und Endtiefe.
    Rueckgabe (drin, draussen); draussen nennt den Grund (ohne Lage / ohne GOK / ohne Endtiefe / entfernt)."""
    drin, draussen = [], []
    for z in zeilen(docs, p):
        d, s = finden(docs, z["id"])
        grund = ("entfernt" if z["entfernt"] else "ohne Lage" if z["x"] is None or z["y"] is None
                 else "ohne GOK" if z["gok"] is None else "ohne Endtiefe" if not z["endtiefe"] else "")
        if grund:
            draussen.append({"id": z["id"], "code": z["code"], "grund": grund})
            continue
        dph = z["art"].upper().startswith(("DP", "SRS"))
        werte = s.get("werte") or []
        kurven, zensierte = [], []
        if dph:
            tiefen, n10 = [], []
            for r in werte:
                w, zen = _wert(r[2]) if len(r) >= 3 else (None, False)
                if w is None:
                    continue
                tiefen.append(float(r[1]))
                n10.append(w)
                if zen:
                    zensierte.append((float(r[0]), float(r[1]), w))
            kurven.append(("N10", tiefen, n10, "Schläge/10 cm", "Schlagzahl je 10 cm, Tiefe = Unterkante der Stufe"))
        else:
            for i, name in ((1, "q_c"), (2, "f_s"), (3, "R_f")):
                paare = [(float(r[0]), float(r[i])) for r in werte if len(r) > i and r[i] is not None]
                if paare:
                    kurven.append((name, [a for a, _ in paare], [b for _, b in paare],
                                   (s.get("einheiten") or {}).get(name, "wie im Diagramm (Einheit nicht gelesen)"),
                                   f"{name} über der Tiefe, aus dem Diagramm gelesen"))
        beleg = s.get("beleg") or {}
        drin.append({**z, "werte": werte, "kurven": kurven, "zensierte": zensierte,
                     "sha256": d["document"].get("sha256"), "methode": beleg.get("methode"),
                     "lage": z["lage_aus"] + (f" (EPSG:{z['epsg']})" if z["epsg"] else "")})
    return drin, draussen
