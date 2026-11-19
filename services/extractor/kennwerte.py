"""Bodenkennwerte aus dem Text des Gutachtens (Issue #18): eigene Stufe, prototyp_v4.py bleibt unberuehrt.

Zwei Formen, beide nach der Lage der Woerter auf der Seite, nie nach Buero oder PDF:

A  Tabelle mit Spalten: Kopfzellen mit Kennwert-Namen (Wichte, Reibungswinkel, Kohaesion, Steifemodul ...) stehen
   nebeneinander (auch hochkant gedreht); die Zeilen sind Boeden oder Schichten, die Bezeichnung steht links der
   ersten Kennwert-Spalte. Zeilengrenzen: waagrechte Tabellenlinien, sonst die Mitte zwischen zwei Wertzeilen.
B  Liste: je Kennwert eine Zeile "Name  Wert" (rechts daneben), mehrere Bloecke untereinander; die Bezeichnung ist
   die naechste Ueberschrift darueber ("Schicht 2 - Auffuellung", "Homogenbereich B").

Gelesen werden nur Spannen und Zahlen mit Einheit aus dem Kopf; ein Wert ausserhalb der ueblichen Spanne bekommt
einen Hinweis (markiert, nicht verworfen). Der Steifemodul wird in MN/m2 gefuehrt (kN/m2 / 1000). Was nicht als Zahl
lesbar ist (z. B. "18 sqrt(t)"), bleibt als Text ohne Zahl. Kennwerte sind Angaben des Gutachters (charakteristische
oder Erfahrungswerte): GroundTwin ordnet sie zu und zeigt sie, setzt sie aber nicht selbst fest.
"""
from __future__ import annotations

import re
import statistics
import sys
from pathlib import Path

import pymupdf

# Reihenfolge zaehlt: Auftrieb vor Wichte, undrainiert vor Kohaesion
PARAMETER = (
    ("wichte_auftrieb", re.compile(r"auftrieb|[γ𝛾y]\s*[’′´'`]", re.I)),
    ("wichte", re.compile(r"wichte|[γ𝛾]", re.I)),
    ("reibungswinkel", re.compile(r"(?<!wand)reibungs\s*-?\s*winkel|winkel\s+der\s+inneren\s+reibung|[φϕ𝜑]", re.I)),
    ("kohaesion_undrainiert", re.compile(r"undr[äa]n|scherfestigkeit|\bc\s*u\b|𝑐\s*u", re.I)),
    ("kohaesion", re.compile(r"koh[äa]\s*-?\s*sion|\bc\s*[’′´'`]|𝑐\s*′", re.I)),
    ("steifemodul", re.compile(r"steife\s*-?\s*(?:modul|ziffer)|\bE\s*[sS]\b|𝐸\s*s|\bEsk?\b", re.I)),
)
NAMEN = {"wichte": "Wichte", "wichte_auftrieb": "Wichte unter Auftrieb", "reibungswinkel": "Reibungswinkel",
         "kohaesion": "Kohäsion", "kohaesion_undrainiert": "undränierte Kohäsion", "steifemodul": "Steifemodul"}
EINHEIT = {"wichte": "kN/m³", "wichte_auftrieb": "kN/m³", "reibungswinkel": "°", "kohaesion": "kN/m²",
           "kohaesion_undrainiert": "kN/m²", "steifemodul": "MN/m²"}
PLAUSIBEL = {"wichte": (10, 26), "wichte_auftrieb": (3, 16), "reibungswinkel": (5, 47.5), "kohaesion": (0, 150),
             "kohaesion_undrainiert": (0, 600), "steifemodul": (0.2, 2000)}
KOPF_MAX = 48                  # Zeichen: laengere Zeilen sind Fliesstext, keine Kopfzelle
ZAHL = r"[-+]?\d{1,3}(?:\.\d{3})+(?:,\d+)?|[-+]?\d+(?:,\d+)?|[-+]?\d+\.\d+"
WERT_RE = re.compile(rf"^\s*(?:ca\.\s*)?({ZAHL})(?:\s*[-–]\s*({ZAHL}))?\s*(?:kN/m[²³23]|MN/m[²³23]|°|deg)?\s*$")
UEBERSCHRIFT_RE = re.compile(r"^\s*(?:Schicht|Bodenschicht|Homogenbereich|Bereich|HB)\s*[\w.]+\s*(?:[–\-:]\s*.+)?$", re.I)


def _zahl(s: str) -> float:
    s = s.strip().lstrip("+")
    if re.fullmatch(r"-?\d{1,3}(?:\.\d{3})+(?:,\d+)?", s):          # 1.000 / 10.000,5: Tausenderpunkt
        s = s.replace(".", "")
    return float(s.replace(",", "."))


def wert(text: str, param: str, kopf_einheit: str = "") -> dict:
    """'11 - 20' -> min 11, max 20; '17,0' -> 17; '-' -> leer; sonst nur Text. Steifemodul in MN/m2."""
    t = re.sub(r"(m)\s+([²³23])\b", r"\1\2", " ".join((text or "").split()))
    out = {"text": t}
    m = WERT_RE.match(t.replace("−", "-")) if t not in ("-", "–", "") else None
    if not m:
        return out
    a = _zahl(m.group(1))
    b = _zahl(m.group(2)) if m.group(2) else a
    faktor = 0.001 if param == "steifemodul" and re.search(r"kN", kopf_einheit + t) else 1.0
    out.update(min=round(min(a, b) * faktor, 4), max=round(max(a, b) * faktor, 4), einheit=EINHEIT[param])
    lo, hi = PLAUSIBEL[param]
    if not (lo <= out["min"] and out["max"] <= hi):
        out["hinweis"] = f"außerhalb der üblichen Spanne {lo}–{hi} {EINHEIT[param]}"
    return out


def _norm(text: str) -> str:
    return " ".join((text or "").replace("\u00ad", "").split())


def param_von(text: str) -> str | None:
    """Kennwert einer Kopfzelle; None fuer Fliesstext und Zellen mit eigener Zahl (ausser Einheiten wie m3)."""
    t = _norm(text)
    if not t or len(t) > KOPF_MAX:
        return None
    rein = re.sub(r"\[[^\]]*\]|\b(?:k?N|MN)/m[²³23]|\bm[²³23]\b", "", t)
    if re.search(r"\d", rein):
        return None
    for p, rx in PARAMETER:
        if rx.search(rein):
            return p
    return None


def _zeilen(seite) -> list[tuple[pymupdf.Rect, str]]:
    out = []
    for blk in seite.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            t = " ".join(s["text"] for s in ln["spans"]).strip()
            if t:
                out.append((pymupdf.Rect(ln["bbox"]), _norm(t)))
    return out


def _woerter(seite) -> list[tuple[pymupdf.Rect, str]]:
    return [(pymupdf.Rect(w[:4]), w[4]) for w in seite.get_text("words")]


def _mitte(r: pymupdf.Rect) -> tuple[float, float]:
    return (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2


def _bloecke(seite) -> list[tuple[pymupdf.Rect, str]]:
    return [(pymupdf.Rect(b[:4]), _norm(b[4])) for b in seite.get_text("blocks") if b[4].strip()]


def _stapel(zeilen) -> list[tuple[pymupdf.Rect, str]]:
    """Kopfzellen ueber mehrere Zeilen ('Reibungs-' / 'winkel', 'Winkel der' / 'inneren' / 'Reibung'): je Zeile mit
    bis zu drei Zeilen direkt darunter (Abstand < 6 pt, Mitten < 25 pt auseinander) zusammengesetzt."""
    out = []
    for i, (r, t) in enumerate(zeilen):
        if len(t) > 25:
            continue
        rr, tt = pymupdf.Rect(r), t
        for _ in range(3):
            unter = [(r2, t2) for r2, t2 in zeilen if 0 <= r2.y0 - rr.y1 < 6 and len(t2) <= 25
                     and abs(_mitte(r2)[0] - _mitte(rr)[0]) < 25]
            if not unter:
                break
            r2, t2 = min(unter, key=lambda e: e[0].y0)
            rr |= r2
            tt = (tt[:-1] if tt.endswith("-") else tt + " ") + t2
            out.append((pymupdf.Rect(rr), tt))
    return out


def _spalten(kandidaten) -> list[dict] | None:
    """Form A: Kopfzellen mit Kennwerten, die nebeneinander stehen (>= 3 verschiedene, Mitten innerhalb 70 pt Hoehe).
    Kandidaten sind Zeilen und Bloecke: ein Kopf ueber mehrere Zeilen ('Reibungs- / winkel') ist ein Block."""
    kopf = [(r, t, p) for r, t in kandidaten if (p := param_von(t))]
    best = None
    for r0, _, _ in kopf:
        y0 = _mitte(r0)[1]
        band = [k for k in kopf if abs(_mitte(k[0])[1] - y0) <= 35]
        je = {}
        for r, t, p in sorted(band, key=lambda k: (k[0].x0, -k[0].height)):
            x = _mitte(r)[0]
            if all(abs(x - s["x"]) > 12 for s in je.values()) and p not in je:
                je[p] = {"param": p, "x": x, "rect": pymupdf.Rect(r), "kopf": t}
        if len(je) >= 3 and (best is None or len(je) > len(best)):
            best = je
    if not best:
        return None
    sp = sorted(best.values(), key=lambda s: s["x"])
    xs = [s["x"] for s in sp]
    for i, s in enumerate(sp):
        links = (xs[i] - xs[i - 1]) / 2 if i else (xs[1] - xs[0]) / 2
        rechts = (xs[i + 1] - xs[i]) / 2 if i + 1 < len(xs) else (xs[i] - xs[i - 1]) / 2
        s["x0"], s["x1"] = xs[i] - links, xs[i] + rechts
    sp[0]["x0"] = max(sp[0]["x0"], sp[0]["rect"].x0 - 8)          # links davon steht die Bezeichnung (auch 'Material')
    sp[-1]["x1"] = min(sp[-1]["x1"], sp[-1]["rect"].x1 + 30)
    return sp


WORT_RE = re.compile(r"[A-Za-zÄÖÜäöüß]{2,}")      # ein Wort, keine Zahl ('ca.' und Einheiten ausgenommen)
LEER_RE = re.compile(r"(?:ca\.?|m|-|–|\[?(?:k?N|MN)/m[²³23]\]?|kN/m[²³23]\s*MN/m[²³23])")
def _ist_wort(t: str) -> bool:
    return bool(WORT_RE.search(t)) and not re.fullmatch(r"\[?(?:in\s+)?(?:k?N|MN)/m[²³23]?\]?|ca\.?|deg", t)


EINHEIT_RE = re.compile(r"^\[?(?:in\s+)?(?:k?N/m[²³23]|MN/m[²³23]|°|deg|O)\]?$")


def _naechste(y: float, reihen: list[float], weit: float) -> int | None:
    i = min(range(len(reihen)), key=lambda k: abs(reihen[k] - y))
    return i if abs(reihen[i] - y) <= weit else None


def _form_a(seite, woerter, bloecke, sp, seite_nr) -> list[dict]:
    unten_kopf = max(s["rect"].y1 for s in sp)
    # Einheiten: Woerter im Kopfbereich, je Spalte das der Spaltenmitte naechste (eine Zeile 'kN/m2 MN/m2' gilt fuer zwei)
    kopf_woerter = [(r, t) for r, t in woerter if min(s["rect"].y0 for s in sp) - 2 <= r.y0 <= unten_kopf + 30]
    for s in sp:
        e = [(abs(_mitte(r)[0] - s["x"]), t, r) for r, t in kopf_woerter
             if EINHEIT_RE.match(t) and s["x0"] <= _mitte(r)[0] < s["x1"]]
        s["einheit"] = min(e)[1] if e else ""
    kopf_ende = max([unten_kopf] + [r.y1 for r, t in kopf_woerter if EINHEIT_RE.match(t)
                                    and any(s["x0"] <= _mitte(r)[0] < s["x1"] for s in sp)])
    links = sp[0]["x0"]
    zellen = []                                        # Wertwoerter je Spalte unter dem Kopf
    for r, t in woerter:
        if r.y0 < kopf_ende - 1:
            continue
        x, y = _mitte(r)
        s = next((s for s in sp if s["x0"] <= x < s["x1"]), None)
        if s and not _ist_wort(t):                     # Woerter (Material, Bodenart) sind keine Werte
            zellen.append((y, s["param"], r, t))
    anker = sorted(y for y, _, _, t in zellen if re.match(r"^[-+]?\d", t))
    gruppen: list[list[float]] = []
    for y in anker:                                    # Wertzeilen: Anker aehnlicher Hoehe
        if gruppen and y - gruppen[-1][-1] <= 4:
            gruppen[-1].append(y)
        else:
            gruppen.append([y])
    reihen = []
    for g in gruppen:
        y = statistics.median(g)
        gefuellt = {p for yy, p, _, t in zellen if abs(yy - y) <= 4 and re.match(r"^[-+–]?\d|^[-–]$", t)}
        if len(gefuellt) >= max(2, (len(sp) + 1) // 2):
            reihen.append(y)
        elif reihen and y - reihen[-1] > 40:
            break                                      # Ende der Tabelle
    if not reihen:
        return []
    if len(reihen) > 1:                                # grosser Sprung = Ende der Tabelle
        abst = [b - a for a, b in zip(reihen, reihen[1:])]
        typ = statistics.median(abst)
        for i, d in enumerate(abst):
            if d > 3.5 * typ:
                reihen = reihen[:i + 1]
                break
    typ = statistics.median([b - a for a, b in zip(reihen, reihen[1:])]) if len(reihen) > 1 else 24.0
    weit = max(8.0, 0.6 * typ)                         # Zelle gehoert zur naechsten Wertzeile, wenn nah genug
    werte_je: list[dict[str, list]] = [dict() for _ in reihen]
    for y, p, r, t in zellen:
        if (i := _naechste(y, reihen, weit)) is not None:
            werte_je[i].setdefault(p, []).append((r, t))
    # Bezeichnung: Bloecke links der Tabelle; ein Block, der in die Wertspalten reicht, zaehlt wortweise
    teile = []
    for r, t in bloecke:
        if r.x1 <= links + 2:
            teile.append((r, t))
        elif r.x0 < links - 4:
            teile += [(rr, tt) for rr, tt in woerter if r.contains(_mitte(rr))
                      and (_mitte(rr)[0] < links or _ist_wort(tt))]
    teile += [(r, t) for r, t in woerter if r.x0 >= links - 2 and r.y0 >= kopf_ende - 1 and _ist_wort(t)
              and any(s["x0"] <= _mitte(r)[0] < s["x1"] for s in sp)]          # Woerter in den Wertspalten
    teile = list(dict.fromkeys((tuple(r), t) for r, t in teile if not LEER_RE.fullmatch(t)))
    teile = [(pymupdf.Rect(r), t) for r, t in teile]
    bez_je: list[list] = [[] for _ in reihen]
    for r, t in teile:
        if r.y1 < kopf_ende - 1:
            continue
        if r.y0 > reihen[-1] + 0.5 * typ:             # unter der letzten Zeile: Fussnoten, Fliesstext
            continue
        drin = [i for i, y in enumerate(reihen) if r.y0 - 1 <= y <= r.y1 + 1]
        if len(drin) > 2:                              # ueber viele Zeilen: Anmerkung ('Genaue Tiefen gemaess ...')
            continue
        if len(drin) > 1:                              # eine Bezeichnung fuer zwei Zeilen (z. B. steif / halbfest)
            for i in drin:
                bez_je[i].append((r, t))
            continue
        i = drin[0] if drin else _naechste(_mitte(r)[1], reihen, 0.75 * typ)
        if i is not None:
            bez_je[i].append((r, t))
    out = []
    for i in range(len(reihen)):
        werte = {}
        for s in sp:
            ws = sorted(werte_je[i].get(s["param"], []), key=lambda e: (round(e[0].y0 / 3), e[0].x0))
            if ws:
                werte[s["param"]] = wert(" ".join(t for _, t in ws), s["param"], s.get("einheit", ""))
        bez = " ".join(t for _, t in sorted(bez_je[i], key=lambda e: (round(e[0].y0 / 3), e[0].x0)))
        out.append(_eintrag(bez, werte, seite_nr, "Tabelle"))
    return out


def _form_b(zeilen, seite_nr) -> list[dict]:
    """Form B: Kennwert-Zeile mit Wert rechts daneben; Bloecke nach der naechsten Ueberschrift darueber."""
    paare = []
    for r, t in zeilen:
        p = param_von(t)
        if not p:
            continue
        y = _mitte(r)[1]
        rechts = sorted(((rr, tt) for rr, tt in zeilen if rr.x0 >= r.x1 - 1 and abs(_mitte(rr)[1] - y) <= 4
                         and rr.x0 - r.x1 < 260), key=lambda e: e[0].x0)
        if not rechts:
            continue
        rr, tt = rechts[0]
        if param_von(tt) or not re.search(r"\d", tt):
            continue
        paare.append((r, p, tt))
    if len(paare) < 2:
        return []
    koepfe = sorted(((r, t) for r, t in zeilen if UEBERSCHRIFT_RE.match(t) and not param_von(t)),
                    key=lambda e: e[0].y0)
    bloecke: dict[str, dict] = {}
    for r, p, tt in sorted(paare, key=lambda e: e[0].y0):
        k = [kk for kk in koepfe if kk[0].y1 <= r.y0 + 1]
        bez = k[-1][1] if k else ""
        b = bloecke.setdefault(bez, {})
        if p not in b:
            b[p] = wert(tt, p)
    return [_eintrag(bez, w, seite_nr, "Liste") for bez, w in bloecke.items() if len(w) >= 2]


def _eintrag(bez: str, werte: dict, seite_nr: int, form: str) -> dict:
    hinweise = [f"{NAMEN[p]}: {w['hinweis']}" for p, w in werte.items() if w.get("hinweis")]
    if not bez:
        hinweise.append("ohne Bezeichnung (Zuordnung von Hand)")
    gruppen = sorted(set(re.findall(r"(?<![A-Za-z])\[?([GSTUO][WIEUTLMAH]\*?|HN|HZ|OK|A)\]?(?![a-z])", bez)))
    name = re.findall(r"\(([^)]*[a-zäöü][^)]*)\)", bez)
    return {"bezeichnung": bez, "name": name[-1].strip() if name else "", "bodengruppen": gruppen, "werte": werte,
            "seite": seite_nr, "form": form, "hinweise": hinweise}


HOEHE_RE = re.compile(r"(GOK|[+\-−]\s?\d{1,4}(?:,\d+)?)\s*bis\s*([+\-−]\s?\d{1,4}(?:,\d+)?)")


def hoehenbereich(bez: str) -> dict:
    """'GOK bis +32,0' / '+32,0 bis +30,0' -> hoehe_oben (None = GOK), hoehe_unten in m NHN; nur mit Vorzeichen
    (Ordinaten), damit Tiefen '0,2-1,8' nicht als Hoehen gelten. Sonst leer."""
    m = HOEHE_RE.search(bez or "")
    if not m:
        return {}
    z = lambda s: float(s.replace("−", "-").replace(" ", "").replace(",", "."))   # noqa: E731
    oben = None if m.group(1) == "GOK" else z(m.group(1))
    unten = z(m.group(2))
    if oben is not None and oben <= unten:
        return {}
    return {"hoehe_oben": oben, "hoehe_unten": unten, "hoehe_bezug": "m NHN"}


def lesen(pdf, doc=None) -> list[dict]:
    """Alle Kennwert-Eintraege des Dokuments (Seite 0-basiert). Nur die Textebene: gescannte Seiten tragen nichts bei."""
    doc = doc or pymupdf.open(pdf)
    out = []
    for nr, seite in enumerate(doc):
        if len(re.findall(r"Wichte|Reibung|Kohä|Steifemodul|Steifeziffer|[γφϕ𝛾𝜑]", seite.get_text())) < 3:
            continue
        zeilen, bloecke = _zeilen(seite), _bloecke(seite)
        # Bloecke als Kopfzelle nur, wenn schmal: ein breiter Block fasst Zeilen verschiedener Spalten zusammen
        sp = _spalten(zeilen + [(r, t) for r, t in bloecke if r.width <= 110] + _stapel(zeilen))
        eintraege = _form_a(seite, _woerter(seite), bloecke, sp, nr) if sp else []
        if not eintraege:
            eintraege = _form_b(zeilen, nr)
        nhn = bool(re.search(r"NHN|\bm\s*(?:ü\.?\s*)?NN\b", seite.get_text()))
        for e in eintraege:
            if nhn:                                  # Bezeichnung als Hoehenbereich ('+32,0 bis +30,0' m NHN)
                e.update(hoehenbereich(e["bezeichnung"]))
        out += [e for e in eintraege if len(e["werte"]) >= 2]
    return out


if __name__ == "__main__":                                # python kennwerte.py <pdf>
    import json
    print(json.dumps(lesen(Path(sys.argv[1])), indent=1, ensure_ascii=False))
