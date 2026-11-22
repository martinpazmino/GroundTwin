"""Schichtwechsel aus Sondierungen (DPH/CPT) als optionale Stuetzpunkte fuer das Schichtmodell (Issue #28).

Eine Sondierung (DPH N10, CPT q_c) liefert keine Bodenart, sondern nur Hinweise auf einen moeglichen Schichtwechsel
ueber die Tiefe. Dieses Modul:
1. erkennt deutliche Spruenge in N10 bzw. q_c (Fenster-Median + robuste Skala + Richtungskonsistenz),
2. ordnet einen erkannten Wechsel nur dann einer Modelleinheit zu, wenn deren Basis nach dem Modell *ohne* Sondierungen
   eindeutig in der Naehe liegt (unklar -> ablehnen, Hinweis),
3. misst den Effekt per leckfreier Leave-one-out-Kreuzprobe (Zuordnung je ausgelassener Bohrung nur aus den uebrigen
   Bohrungen) auf synthetischen Faellen mit bekannter Wahrheit (eben, geneigt, Rinne, Linse, ohne Sprung, CPT) und auf
   realen Projekt-JSONs.

Grundsatz (Issue #28): Lieber kein Effekt mit 0 falschen Grenzen als ein Gewinn, der eine Grenze erfindet.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from baugrundmodell import synthetisch as syn
from baugrundmodell.flaechen import orientierungen_holen, orientierungen_setzen, schichtmodell
from baugrundmodell.modell import bauen

from .kreuzprobe import METHODEN, _masse, kreuzprobe

# ------------------------------------------------------------------ Schwellen fuer Schichtwechsel-Erkennung
FENSTER_M = 0.5               # m: halbe Fensterbreite ober-/unterhalb einer moeglichen Grenze (DPH: 5 Stufen)
FENSTER_MIN_PUNKTE = 4        # Mindestanzahl Messpunkte je Seite des Fensters
MIN_TIEFE_M = 0.5             # m u. GOK: oberhalb davon nicht suchen (Randeffekt)
MIN_ABSTAND_M = 0.8           # m: Mindestabstand zweier getrennter Schichtwechsel (NMS)
SNR_MIN = 3.0                 # Mindest-Signal-Rausch-Verhaeltnis |m_R - m_L| / sigma
RATIO_MIN = 1.45              # Mindestverhaeltnis max(m_L, m_R) / min(m_L, m_R)
KONSISTENZ_MIN = 0.75         # Anteil der Messwerte je Seite auf der richtigen Seite der Mitte (gegen Rampen)
DELTA_MIN_DPH = 4.0           # Schlaege/10 cm (N10)
DELTA_MIN_CPT = 2.0           # MN/m2 (q_c)
SIGMA_BODEN_DPH = 1.5         # Rauschboden N10 (Schlaege/10 cm)
SIGMA_BODEN_CPT = 0.8         # Rauschboden q_c (MN/m2)

# ------------------------------------------------------------------ Schwellen fuer Zuordnung zur Einheit
MAX_ABWEICHUNG_M = 2.5        # m: hoechster Abstand zwischen Sondierungs-Wechsel und Basis im Basismodell
MIN_TRENNUNG_M = 0.8          # m: Mindestabstand zwischen naechster und zweitnaechster Einheit
MAX_VERHAELTNIS = 0.45        # d1 / d2 <= 0,45 (eindeutige Zuordnung, sonst ablehnen)
MIN_ABSTAND_BOHRUNG_M = 0.5   # m: naeher an einer Bohrung gilt die Bohrung allein
PRAESENZ_MIN = 0.05           # m: Einheit gilt im Basismodell am Ort der Sondierung als vorhanden


def _zahl(v) -> tuple[float | None, bool]:
    """Messwert (Zahl oder {'wert', 'zensiert'}) -> (float | None, zensiert)."""
    if isinstance(v, dict):
        w = v.get("wert")
        return (None if w is None else float(w)), bool(v.get("zensiert"))
    return (None if v is None else float(v)), False


def _kurve_lesen(s: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray, str, str | None]:
    """Tiefe (m), Messwert, zensiert-Flag und Groesse ('N10' | 'q_c') aus einer Sondierung lesen."""
    art = str(s.get("art") or "").upper()
    werte = s.get("werte") or []
    if not werte:
        return np.empty(0), np.empty(0), np.empty(0, dtype=bool), "", "ohne Messwerte"
    tiefen, mess, zens = [], [], []
    if art.startswith(("DP", "SRS")):
        groesse = "N10"
        for r in werte:
            if not isinstance(r, (list, tuple)) or len(r) < 3:
                continue
            o, u = float(r[0]), float(r[1])
            w, z = _zahl(r[2])
            if w is None or not (math.isfinite(o) and math.isfinite(u) and math.isfinite(w)):
                continue
            tiefen.append(0.5 * (o + u))
            mess.append(w)
            zens.append(z)
    elif art.startswith("CPT"):
        groesse = "q_c"
        for r in werte:
            if not isinstance(r, (list, tuple)) or len(r) < 2:
                continue
            t = float(r[0])
            w, z = _zahl(r[1])
            if w is None or not (math.isfinite(t) and math.isfinite(w)):
                continue
            tiefen.append(t)
            mess.append(w)
            zens.append(z)
    else:
        return np.empty(0), np.empty(0), np.empty(0, dtype=bool), "", f"unbekannte Sondierungsart '{art}'"
    if len(tiefen) < 2 * FENSTER_MIN_PUNKTE:
        return np.empty(0), np.empty(0), np.empty(0, dtype=bool), groesse, f"zu wenige Messpunkte ({len(tiefen)})"
    ordn = np.argsort(tiefen)
    return (np.asarray(tiefen, dtype=float)[ordn], np.asarray(mess, dtype=float)[ordn],
            np.asarray(zens, dtype=bool)[ordn], groesse, None)


def schichtwechsel_erkennen(sondierung: dict, fenster_m: float = FENSTER_M,
                            snr_min: float = SNR_MIN) -> dict:
    """Deutliche Schichtwechsel (Spruenge in N10 bzw. q_c) in einer Sondierung erkennen.

    Rueckgabe: {"code", "art", "groesse", "wechsel": [...], "hinweis": str | None}.
    Nie wird eine Bodenart geraten; jeder Wechsel traegt Tiefe, Sprung, SNR und Konfidenz (0,50..0,95).
    """
    code = str(sondierung.get("code") or "?")
    art = str(sondierung.get("art") or "")
    tiefen, werte, zens, groesse, grund = _kurve_lesen(sondierung)
    if grund:
        return {"code": code, "art": art, "groesse": groesse, "wechsel": [], "hinweis": grund}
    delta_min = DELTA_MIN_DPH if groesse == "N10" else DELTA_MIN_CPT
    sigma_boden = SIGMA_BODEN_DPH if groesse == "N10" else SIGMA_BODEN_CPT
    t_max = float(tiefen[-1])
    gok = sondierung.get("gok", sondierung.get("ansatzhoehe"))
    gok_f = None if gok is None else float(gok)

    kandidaten = []
    # Moegliche Grenzpositionen liegen genau zwischen zwei aufeinanderfolgenden Messpunkten
    for i in range(1, len(tiefen)):
        d = 0.5 * (tiefen[i - 1] + tiefen[i])
        if d < MIN_TIEFE_M or d > t_max - MIN_TIEFE_M:
            continue
        links_mask = (tiefen >= d - fenster_m) & (tiefen < d)
        rechts_mask = (tiefen > d) & (tiefen <= d + fenster_m)
        if links_mask.sum() < FENSTER_MIN_PUNKTE or rechts_mask.sum() < FENSTER_MIN_PUNKTE:
            continue
        if zens[links_mask].all() and zens[rechts_mask].all():
            continue                                       # kein Sprung innerhalb eines zensierten Plateaus
        l_w, r_w = werte[links_mask], werte[rechts_mask]
        m_l, m_r = float(np.median(l_w)), float(np.median(r_w))
        delta = abs(m_r - m_l)
        if delta < delta_min:
            continue
        verh = max(m_l, m_r) / max(min(m_l, m_r), 0.5)
        if verh < RATIO_MIN:
            continue
        mad_l = 1.4826 * float(np.median(np.abs(l_w - m_l)))
        mad_r = 1.4826 * float(np.median(np.abs(r_w - m_r)))
        sigma = max(math.sqrt(0.5 * (mad_l * mad_l + mad_r * mad_r)), sigma_boden)
        snr = delta / sigma
        if snr < snr_min:
            continue
        mitte = 0.5 * (m_l + m_r)
        if m_r > m_l:
            kons = 0.5 * (float((l_w < mitte).mean()) + float((r_w > mitte).mean()))
        else:
            kons = 0.5 * (float((l_w > mitte).mean()) + float((r_w < mitte).mean()))
        if kons < KONSISTENZ_MIN:
            continue
        konf = min(0.95, max(0.50, 0.50 + 0.08 * (snr - snr_min) + 0.25 * (kons - KONSISTENZ_MIN)))
        kandidaten.append({
            "tiefe_m": round(float(d), 2),
            "z_nhn": None if gok_f is None else round(gok_f - float(d), 3),
            "oben_median": round(m_l, 2),
            "unten_median": round(m_r, 2),
            "sprung": round(float(m_r - m_l), 2),
            "verhaeltnis": round(float(verh), 2),
            "snr": round(float(snr), 2),
            "konsistenz": round(float(kons), 2),
            "konfidenz": round(float(konf), 2),
            "groesse": groesse,
        })

    # Nicht-Maximum-Unterdrueckung: innerhalb MIN_ABSTAND_M den schaerfsten Sprung behalten
    # (konsistenz * snr bestraft verschobene Fenster, bei denen der Median noch stimmt, aber Randpunkte falsch liegen)
    wechsel = []
    for k in sorted(kandidaten, key=lambda x: (-(x["konsistenz"] * x["snr"]), -x["konsistenz"], -abs(x["sprung"]))):
        if all(abs(k["tiefe_m"] - w["tiefe_m"]) >= MIN_ABSTAND_M for w in wechsel):
            wechsel.append(k)
    wechsel.sort(key=lambda x: x["tiefe_m"])
    return {"code": code, "art": art, "groesse": groesse, "wechsel": wechsel, "hinweis": None}


def _basismodell_an_punkten(m, xy_lokal: np.ndarray, methode: str,
                            ausser: frozenset[int] = frozenset()) -> np.ndarray:
    """Basismodell (ohne Sondierungen, ohne Bohrungen `ausser`) an `xy_lokal` auswerten."""
    nb = len(m.bohrungen)
    rest = [i for i in range(nb) if i not in ausser]
    xy_r = m.punkte[:nb][rest]
    punkte = np.vstack([xy_r, xy_lokal]) if len(xy_lokal) else xy_r
    oben = None
    if m.dgm is not None and len(xy_lokal) == 0:
        oben = m.flaechen[0][rest]
    vorher = orientierungen_holen()
    orientierungen_setzen({int(j): tuple(v) for j, v in (m.parameter.get("orientierung_vorgabe") or {}).items()})
    try:
        sm = schichtmodell([m.bohrungen[i] for i in rest], [m.kontakte[i] for i in rest],
                           punkte, xy_r, m.basis, methode, oben=oben)
    finally:
        orientierungen_setzen(vorher)
    return sm["flaechen"][:, len(rest):]


def stuetzpunkte_zuordnen(m, sondierungen: list[dict], methode: str | None = None,
                          ausser: frozenset[int] = frozenset(),
                          max_abweichung_m: float = MAX_ABWEICHUNG_M,
                          min_trennung_m: float = MIN_TRENNUNG_M) -> dict:
    """Erkannte Schichtwechsel den wahrscheinlichsten Einheiten des Basismodells zuordnen.

    Unklare, mehrdeutige oder zu weit entfernte Wechsel werden verworfen und mit Grund in `abgelehnt` genannt.
    Rueckgabe: {"stuetzpunkte": [...], "abgelehnt": [...], "hinweise": [...]}.
    """
    meth = methode or m.parameter.get("methode", "idw")
    nb, n_einh = len(m.bohrungen), len(m.einheiten)
    rest = [i for i in range(nb) if i not in ausser]
    xy_b = m.punkte[:nb][rest]
    # Einheiten mit mindestens einer exakten Unterkante in den verbleibenden Bohrungen (offene Basis nie zuordnen)
    exakte_einheiten = {
        j for j in range(n_einh)
        if any(m.kontakte[bi][j].art == "exakt" and m.kontakte[bi][j].status == "vorhanden" for bi in rest)
    }

    stuetzpunkte: list[dict] = []
    abgelehnt: list[dict] = []
    hinweise: list[str] = []

    nutzbar: list[tuple[dict, float, float, float, dict]] = []
    for s in sondierungen or []:
        code = str(s.get("code") or "?")
        x, y = s.get("x"), s.get("y")
        gok = s.get("gok", s.get("ansatzhoehe"))
        if x is None or y is None:
            abgelehnt.append({"code": code, "tiefe_m": None, "grund": "ohne Lage"})
            continue
        if gok is None:
            abgelehnt.append({"code": code, "tiefe_m": None, "grund": "ohne GOK"})
            continue
        xf, yf, gokf = float(x), float(y), float(gok)
        xl, yl = xf - m.ursprung[0], yf - m.ursprung[1]
        if len(xy_b):
            d_bohr = float(np.hypot(xy_b[:, 0] - xl, xy_b[:, 1] - yl).min())
            if d_bohr <= MIN_ABSTAND_BOHRUNG_M:
                abgelehnt.append({"code": code, "tiefe_m": None, "grund": f"zu nah an Bohrung ({d_bohr:.2f} m)"})
                continue
        erk = schichtwechsel_erkennen(s)
        if erk["hinweis"]:
            abgelehnt.append({"code": code, "tiefe_m": None, "grund": erk["hinweis"]})
            continue
        if not erk["wechsel"]:
            abgelehnt.append({"code": code, "tiefe_m": None, "grund": "kein deutlicher Sprung erkannt"})
            continue
        nutzbar.append((s, xf, yf, gokf, erk))

    if not nutzbar:
        if sondierungen:
            hinweise.append("Sondierungen: kein verwertbarer Stützpunkt (ohne Lage/GOK/Werte oder ohne deutlichen Sprung)")
        return {"stuetzpunkte": stuetzpunkte, "abgelehnt": abgelehnt, "hinweise": hinweise}

    xy_s = np.array([(xf - m.ursprung[0], yf - m.ursprung[1]) for _, xf, yf, _, _ in nutzbar], dtype=float)
    fl = _basismodell_an_punkten(m, xy_s, meth, ausser=ausser)

    for si, (s, xf, yf, gokf, erk) in enumerate(nutzbar):
        code = erk["code"]
        f_col = fl[:, si]                                  # Zeile 0 = Gelaende, Zeile j+1 = UK Einheit j
        # Vorhandene Einheiten mit exakter Unterkante an diesem Ort
        basis_kand: list[tuple[int, float]] = []
        for j in sorted(exakte_einheiten):
            if float(f_col[j] - f_col[j + 1]) >= PRAESENZ_MIN:
                basis_kand.append((j, float(f_col[j + 1])))
        if not basis_kand:
            abgelehnt.append({"code": code, "tiefe_m": None, "grund": "keine Einheit mit Basis am Ort"})
            continue

        # Wechsel einzeln pruefen
        vorlaeufig: list[dict] = []
        for w in erk["wechsel"]:
            z_cp = gokf - float(w["tiefe_m"])
            if z_cp <= m.basis + 0.05:
                abgelehnt.append({"code": code, "tiefe_m": w["tiefe_m"], "grund": "unterhalb der Modellbasis"})
                continue
            abstaende = sorted((abs(z_cp - z_mod), j, z_mod) for j, z_mod in basis_kand)
            d1, j1, z_mod1 = abstaende[0]
            if d1 > max_abweichung_m:
                abgelehnt.append({"code": code, "tiefe_m": w["tiefe_m"],
                                  "grund": f"zu weit von nächster Basis ({m.einheiten[j1].name}, {d1:.2f} m)"})
                continue
            if len(abstaende) >= 2:
                d2, j2, _ = abstaende[1]
                if (d2 - d1) < min_trennung_m or (d2 > 1e-6 and d1 / d2 > MAX_VERHAELTNIS):
                    abgelehnt.append({"code": code, "tiefe_m": w["tiefe_m"],
                                      "grund": f"mehrdeutig zwischen {m.einheiten[j1].name} ({d1:.2f} m) und "
                                               f"{m.einheiten[j2].name} ({d2:.2f} m)"})
                    continue
            vorlaeufig.append({
                "einheit": m.einheiten[j1].name, "einheit_index": j1, "code": code,
                "x": round(xf, 3), "y": round(yf, 3), "z": round(z_cp, 3),
                "tiefe_m": w["tiefe_m"], "quelle": "Sondierung",
                "konfidenz": w["konfidenz"], "sprung": w["sprung"], "snr": w["snr"], "groesse": w["groesse"],
                "abweichung_modell_m": round(z_cp - z_mod1, 3),
            })

        # Doppelbelegung derselben Einheit in einer Sondierung -> mehrdeutig, beide verwerfen
        je_einh: dict[int, list[dict]] = {}
        for p in vorlaeufig:
            je_einh.setdefault(p["einheit_index"], []).append(p)
        bereinigt: list[dict] = []
        for j, gruppe in sorted(je_einh.items()):
            if len(gruppe) > 1:
                for p in gruppe:
                    abgelehnt.append({"code": code, "tiefe_m": p["tiefe_m"],
                                      "grund": f"mehrere Wechsel für {p['einheit']} (unklar)"})
            else:
                bereinigt.append(gruppe[0])

        # Stratigraphische Reihenfolge pruefen (tiefere Einheit muss <= hoehere Einheit liegen)
        bereinigt.sort(key=lambda p: p["einheit_index"])
        ok_folge = True
        for a, b in zip(bereinigt, bereinigt[1:]):
            if a["z"] <= b["z"] + 0.05:
                ok_folge = False
                break
        if not ok_folge:
            for p in bereinigt:
                abgelehnt.append({"code": code, "tiefe_m": p["tiefe_m"],
                                  "grund": "Widerspruch in der Schichtfolge"})
            continue
        stuetzpunkte.extend(bereinigt)

    if abgelehnt:
        hinweise.append(f"Sondierungen: {len(stuetzpunkte)} Stützpunkte übernommen, {len(abgelehnt)} abgelehnt")
    return {"stuetzpunkte": stuetzpunkte, "abgelehnt": abgelehnt, "hinweise": hinweise}


# ------------------------------------------------------------------ Leckfreie Leave-one-out-Kreuzprobe
def _ist_falsche_grenze(p: dict, wahrheit: syn.Fall, toleranz_m: float = 0.5) -> bool:
    """Prueft gegen die synthetische Wahrheit, ob ein Stuetzpunkt der falschen Einheit zugeordnet wurde."""
    xl, yl = float(p["x"]) - syn.URSPRUNG[0], float(p["y"]) - syn.URSPRUNG[1]
    j = int(p["einheit_index"])
    if j < 0 or j >= len(wahrheit.einheiten):
        return True
    gok = wahrheit.gok(xl, yl)
    oben = gok
    for idx, (_, uk_fn) in enumerate(wahrheit.einheiten):
        unten = min(uk_fn(xl, yl), oben)
        if idx == j:
            if oben - unten < PRAESENZ_MIN:
                return True                                # Einheit ist am Ort der Sondierung gar nicht vorhanden
            return abs(float(p["z"]) - unten) > toleranz_m
        oben = unten
    return True


def kreuzprobe_sondierungen(m, sondierungen: list[dict], methoden: tuple[str, ...] = METHODEN,
                            wahrheit: syn.Fall | None = None) -> dict:
    """Vergleicht Leave-one-out-Kreuzprobe OHNE vs. MIT Sondierungs-Stuetzpunkten (ohne Datenleck).

    Je ausgelassener Bohrung `bi` werden die Sondierungen streng nur anhand des Basismodells der uebrigen
    N-1 Bohrungen zugeordnet. Bei bekannter synthetischer Wahrheit wird zusaetzlich gezaehlt, wie viele
    uebernommene Stuetzpunkte an der falschen Einheit landen (`falsche_grenzen`).
    """
    basis_kp = kreuzprobe(m, methoden=methoden)
    nb = len(m.bohrungen)
    xy = m.punkte[:nb]

    out: dict = {"bohrungen": nb, "sondierungen": len(sondierungen or []), "methoden": {}}
    for methode in methoden:
        fehler_mit: list[tuple[int, int, float]] = []
        n_stuetz_gesamt = 0
        n_abgelehnt_gesamt = 0
        falsche_gesamt = 0
        gruende: dict[str, int] = {}

        for bi in range(nb):
            zuo = stuetzpunkte_zuordnen(m, sondierungen, methode=methode, ausser=frozenset({bi}))
            st = zuo["stuetzpunkte"]
            n_stuetz_gesamt += len(st)
            n_abgelehnt_gesamt += len(zuo["abgelehnt"])
            for a in zuo["abgelehnt"]:
                g = a["grund"].split("(")[0].strip()
                gruende[g] = gruende.get(g, 0) + 1
            if wahrheit is not None:
                for p in st:
                    if _ist_falsche_grenze(p, wahrheit):
                        falsche_gesamt += 1

            zusatz_je: dict[int, list[tuple[float, float, float]]] = {}
            for p in st:
                zusatz_je.setdefault(p["einheit_index"], []).append(
                    (p["x"] - m.ursprung[0], p["y"] - m.ursprung[1], p["z"]))

            rest = [i for i in range(nb) if i != bi]
            punkte = np.vstack([xy[rest], xy[bi:bi + 1]])
            oben = np.r_[m.flaechen[0][rest], m.flaechen[0][bi]] if m.dgm is not None else None
            vorher = orientierungen_holen()
            orientierungen_setzen({int(j): tuple(v) for j, v in (m.parameter.get("orientierung_vorgabe") or {}).items()})
            try:
                sm = schichtmodell([m.bohrungen[i] for i in rest], [m.kontakte[i] for i in rest],
                                   punkte, xy[rest], m.basis, methode, oben=oben,
                                   zusatz_stuetzpunkte=zusatz_je or None)
            finally:
                orientierungen_setzen(vorher)
            f = sm["flaechen"][:, -1]
            for j, k in enumerate(m.kontakte[bi]):
                if k.art == "exakt" and k.status == "vorhanden":
                    fehler_mit.append((bi, j, float(f[j + 1] - k.z)))

        m_ohne = basis_kp["methoden"][methode]["gesamt"]
        m_mit = _masse([e for _, _, e in fehler_mit])
        einh_out = []
        for j, e_ohne in enumerate(basis_kp["methoden"][methode]["einheiten"]):
            e_mit = _masse([e for _, jj, e in fehler_mit if jj == j])
            delta = None if (e_ohne["mae"] is None or e_mit["mae"] is None) else round(e_mit["mae"] - e_ohne["mae"], 3)
            einh_out.append({"name": e_ohne["name"], "ohne": {k: e_ohne[k] for k in ("n", "mae", "rmse", "max")},
                             "mit": {k: e_mit[k] for k in ("n", "mae", "rmse", "max")}, "delta_mae_m": delta})
        delta_ges = None if (m_ohne["mae"] is None or m_mit["mae"] is None) else round(m_mit["mae"] - m_ohne["mae"], 3)

        # Gesamtzahl auf dem vollen Modell (alle Bohrungen) fuer Berichtsstatistik
        voll = stuetzpunkte_zuordnen(m, sondierungen, methode=methode)
        falsche_voll = (sum(1 for p in voll["stuetzpunkte"] if _ist_falsche_grenze(p, wahrheit))
                        if wahrheit is not None else None)

        out["methoden"][methode] = {
            "ohne": m_ohne,
            "mit": m_mit,
            "delta_mae_m": delta_ges,
            "einheiten": einh_out,
            "stuetzpunkte_voll": len(voll["stuetzpunkte"]),
            "abgelehnt_voll": len(voll["abgelehnt"]),
            "falsche_grenzen_voll": falsche_voll,
            "stuetzpunkte_loo_gesamt": n_stuetz_gesamt,
            "abgelehnt_loo_gesamt": n_abgelehnt_gesamt,
            "falsche_grenzen_loo": falsche_gesamt if wahrheit is not None else None,
            "ablehnungsgruende_loo": gruende,
        }
    return out


# ------------------------------------------------------------------ Synthetische Wahrheit mit Sondierungen (Schritt 2)
@dataclass
class SondierungsFall:
    name: str
    flaechenform: str
    fall: syn.Fall
    doc: dict
    sondierungen: list[dict]


def _n10_kurve(fall: syn.Fall, x: float, y: float, endteufe: float,
               n10_je_einheit: list[tuple[float, float]], rng: np.random.Generator,
               schritt: float = 0.1, stein_p: float = 0.02) -> list[list[float]]:
    """DPH-N10-Kurve aus den wahren Schichten an (x, y): je Einheit (Mittelwert, Rausch-Sigma) + seltene Steinspitzen."""
    gok = fall.gok(x, y)
    # Wahre Ober-/Unterkanten je Einheit am Punkt (x, y)
    intervalle: list[tuple[float, float, int]] = []
    oben = gok
    for idx, (_, uk_fn) in enumerate(fall.einheiten):
        unten = min(uk_fn(x, y), oben)
        if oben - unten > 0.005:
            intervalle.append((gok - oben, gok - unten, idx))
        oben = unten
    n_stufen = int(round(endteufe / schritt))
    werte = []
    for k in range(n_stufen):
        o = round(k * schritt, 2)
        u = round((k + 1) * schritt, 2)
        mitte = 0.5 * (o + u)
        idx_e = len(fall.einheiten) - 1
        for t0, t1, idx in intervalle:
            if t0 - 1e-9 <= mitte < t1:
                idx_e = idx
                break
        mu, sd = n10_je_einheit[idx_e]
        w = max(1.0, float(rng.normal(mu, sd)))
        if rng.random() < stein_p:
            w += float(rng.uniform(10.0, 20.0))           # einzelner Stein (Ausreisser, 1 Stufe)
        werte.append([o, u, round(w, 1)])
    return werte


def _cpt_kurve(fall: syn.Fall, x: float, y: float, endteufe: float,
               qc_je_einheit: list[tuple[float, float]], rng: np.random.Generator,
               schritt: float = 0.05) -> list[list[float]]:
    """CPT-Kurve [tiefe, q_c, f_s, R_f] aus den wahren Schichten an (x, y)."""
    gok = fall.gok(x, y)
    intervalle: list[tuple[float, float, int]] = []
    oben = gok
    for idx, (_, uk_fn) in enumerate(fall.einheiten):
        unten = min(uk_fn(x, y), oben)
        if oben - unten > 0.005:
            intervalle.append((gok - oben, gok - unten, idx))
        oben = unten
    n_pkt = int(round(endteufe / schritt))
    werte = []
    for k in range(1, n_pkt + 1):
        t = round(k * schritt, 2)
        idx_e = len(fall.einheiten) - 1
        for t0, t1, idx in intervalle:
            if t0 - 1e-9 <= t < t1:
                idx_e = idx
                break
        mu, sd = qc_je_einheit[idx_e]
        qc = max(0.3, float(rng.normal(mu, sd)))
        fs = round(max(0.01, 0.015 * qc), 3)
        rf = round(100.0 * fs / qc, 2)
        werte.append([t, round(qc, 2), fs, rf])
    return werte


def _sondierung_dict(code: str, art: str, x_lokal: float, y_lokal: float, gok: float,
                     werte: list, endteufe: float) -> dict:
    return {
        "code": code, "art": art, "form": "synthetisch", "seite": 0,
        "x": syn.URSPRUNG[0] + x_lokal, "y": syn.URSPRUNG[1] + y_lokal,
        "crs_epsg": syn.EPSG, "ansatzhoehe": round(gok, 2), "gok": round(gok, 2),
        "endtiefe": round(endteufe, 2), "werte": werte, "konfidenz": 0.95,
        "quelle": "synthetisch", "hinweise": [],
    }


def _sondierungs_punkte_zwischen(bohr_xy: list[tuple[float, float]], abstand: float = 25.0) -> list[tuple[float, float]]:
    """Sondierungen mittig auf den Kanten und im Inneren eines 3x3-Rasters."""
    xs = sorted({p[0] for p in bohr_xy})
    ys = sorted({p[1] for p in bohr_xy})
    punkte = []
    for i in range(len(xs) - 1):
        mx = 0.5 * (xs[i] + xs[i + 1])
        for y in ys:
            punkte.append((mx, y))
    for j in range(len(ys) - 1):
        my = 0.5 * (ys[j] + ys[j + 1])
        for x in xs:
            punkte.append((x, my))
    return punkte


def synthetischer_fall(name: str, seed: int = 42, abstand_m: float | None = None) -> SondierungsFall:
    """Baut einen der synthetischen Benchmark-Faelle fuer Issue #28.

    Faelle: 'eben', 'geneigt', 'rinne', 'linse', 'ohne_sprung', 'cpt_rinne'.
    abstand_m: wenn gesetzt, stehen die Sondierungen im angegebenen Abstand neben den Bohrungen (Abstandsstudie).
    """
    rng = np.random.default_rng(seed)

    if name == "eben":
        def gok(x, y):
            return 40.0
        fall = syn.Fall("eben", gok, [
            ("Auffuellung", lambda x, y: 38.5),
            ("Sand", lambda x, y: 33.5),
            ("Geschiebemergel", lambda x, y: 27.5),
            ("Ton", lambda x, y: -100.0),
        ], syn._raster(16.0))
        profile = [(6.0, 1.2), (18.0, 1.8), (34.0, 2.2), (12.0, 1.5)]
        art, form = "DPH", "eben"

    elif name == "geneigt":
        fall = syn.geneigt()
        profile = [(6.0, 1.2), (18.0, 1.8), (34.0, 2.2), (12.0, 1.5)]
        art, form = "DPH", "geneigt"

    elif name == "rinne":
        def gok(x, y):
            return 40.0 + 0.01 * x
        # Rinne laeuft entlang x = 50 m (24 m breit, bis 2,6 m tief in den dichten Geschiebemergel eingeschnitten)
        def rinne_uk(x, y):
            return 34.0 - 2.6 * math.exp(-((x - 50.0) / 14.0) ** 2)
        bohr = [(f"B{3 * i + j + 1}", 40.0 * j + 10.0, 40.0 * i + 10.0, 16.0) for i in range(3) for j in range(3)]
        fall = syn.Fall("rinne", gok, [
            ("Auffuellung", lambda x, y: gok(x, y) - 1.2),
            ("Sand", rinne_uk),
            ("Geschiebemergel", lambda x, y: 27.0 + 0.01 * y),
            ("Ton", lambda x, y: -100.0),
        ], bohr)
        profile = [(6.0, 1.2), (14.0, 1.6), (34.0, 2.2), (12.0, 1.5)]
        art, form = "DPH", "Rinne"

    elif name == "linse":
        fall = syn.linse()
        profile = [(6.0, 1.2), (14.0, 1.5), (38.0, 2.5), (14.0, 1.5), (34.0, 2.2)]
        art, form = "DPH", "Linse"

    elif name == "ohne_sprung":
        fall = syn.geneigt()
        fall.name = "ohne_sprung"
        # Gleiche Lagerungsdichte / N10 ueber verschiedene Bodenarten -> kein erkennbarer Sprung
        profile = [(17.0, 2.0), (18.0, 2.0), (19.0, 2.0), (18.5, 2.0)]
        art, form = "DPH", "ohne Sprung (gleiche Dichte)"

    elif name == "cpt_rinne":
        base = synthetischer_fall("rinne", seed=seed, abstand_m=abstand_m)
        fall = base.fall
        fall.name = "cpt_rinne"
        profile = [(2.5, 0.4), (9.0, 1.0), (24.0, 1.8), (6.0, 0.8)]
        art, form = "CPT", "Rinne (CPT q_c)"

    else:
        raise ValueError(f"unbekannter Sondierungs-Fall: {name}")

    doc = syn.dokument(fall)
    bohr_xy = [(x, y) for _, x, y, _ in fall.bohrungen]
    if abstand_m is not None:
        # Je Bohrung eine Sondierung im definierten Abstand Richtung Gebietsmitte (leicht gedreht gegen Kollision)
        cx = float(np.mean([p[0] for p in bohr_xy]))
        cy = float(np.mean([p[1] for p in bohr_xy]))
        s_punkte = []
        for idx, (bx, by) in enumerate(bohr_xy):
            dx, dy = cx - bx, cy - by
            laenge = math.hypot(dx, dy)
            if laenge < 1e-6:
                ux, uy = math.cos(0.6), math.sin(0.6)
            else:
                ux, uy = dx / laenge, dy / laenge
            s_punkte.append((bx + ux * abstand_m, by + uy * abstand_m))
    else:
        s_punkte = _sondierungs_punkte_zwischen(bohr_xy)
        if name == "linse":
            # Zusaetzlich 2 Sondierungen direkt im Randbereich der Kieslinse (Stresstest gegen falsche Zuordnung)
            s_punkte = s_punkte + [(40.0, 50.0), (60.0, 50.0)]

    sondierungen = []
    for k, (sx, sy) in enumerate(s_punkte, 1):
        endtiefe = 15.0
        gok_s = fall.gok(sx, sy)
        if art == "CPT":
            werte = _cpt_kurve(fall, sx, sy, endtiefe, profile, rng)
            code = f"CPT {k}"
        else:
            werte = _n10_kurve(fall, sx, sy, endtiefe, profile, rng)
            code = f"DPH {k}"
        sondierungen.append(_sondierung_dict(code, art, sx, sy, gok_s, werte, endtiefe))

    doc["sondierungen"] = sondierungen
    return SondierungsFall(name=name, flaechenform=form, fall=fall, doc=doc, sondierungen=sondierungen)


FAELLE = ("eben", "geneigt", "rinne", "linse", "ohne_sprung", "cpt_rinne")


def benchmark_ausfuehren(seed: int = 42) -> list[dict]:
    """Misst alle synthetischen Faelle (Leave-one-out ohne vs. mit Sondierungen)."""
    ergebnisse = []
    for name in FAELLE:
        sf = synthetischer_fall(name, seed=seed)
        m = bauen([sf.doc])
        kp = kreuzprobe_sondierungen(m, sf.sondierungen, wahrheit=sf.fall)
        ergebnisse.append({"name": name, "flaechenform": sf.flaechenform, **kp})
    return ergebnisse


def abstand_studie(fall_name: str = "rinne", abstaende: tuple[float, ...] = (5.0, 10.0, 20.0, 35.0),
                   seed: int = 42) -> list[dict]:
    """Variiert den Abstand Sondierung-Bohrung und misst den Leave-one-out-Fehler."""
    out = []
    for d in abstaende:
        sf = synthetischer_fall(fall_name, seed=seed, abstand_m=d)
        m = bauen([sf.doc])
        kp = kreuzprobe_sondierungen(m, sf.sondierungen, wahrheit=sf.fall)
        out.append({"fall": fall_name, "abstand_m": d, **kp})
    return out
