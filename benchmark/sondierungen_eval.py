"""Auswertung und Regressionstest der Sondierungsextraktion (DPH/DPL/DPM/DPSH und CPT/CPTu).

    python sondierungen_eval.py [--module services/extractor/sondierungen.py]
                                [--real <pdfs>] [--gt benchmark/groundtruth_sondierungen]
                                [--stress <stressordner>] [--synth <synthordner>]
                                [--baseline [datei.json]] [--write]
                                [--disable regel1,regel2] [--no-ocr] [--tol-cpt 0.05] [--quiet]

Ohne --real, --stress und --synth werden automatisch die synthetischen Stressfaelle
(stress_sondierungen.py) und alle synthetischen Bohrprofile (synth_bohrprofil.py) in
einem temporaeren Ordner erzeugt und geprueft.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import statistics
import sys
import tempfile
import time
from pathlib import Path

import pymupdf

HERE = Path(__file__).resolve().parent
REPO_WURZEL = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
EXTRACTOR_DIR = REPO_WURZEL / "services" / "extractor"
if str(EXTRACTOR_DIR) not in sys.path:
    sys.path.insert(0, str(EXTRACTOR_DIR))

DPH_ARTEN = {"DPH", "DPL", "DPM", "DPSH"}
CPT_ARTEN = {"CPT", "CPTU"}
GUTE_BRUECHE = ("gefunden", "code_richtig", "endtiefe_5cm", "dph_schritt_1", "cpt_punkte")
SCHLECHTE_ZAHLEN = ("falsche_sondierungen", "falsche_werte")
CPT_FEHLER_FELDER = ("cpt_qc_mittel_pct", "cpt_qc_max_pct")


def norm(code: str | None) -> str:
    """Normiert eine Sondierungs-Kennung fuer den Vergleich (ohne Leerzeichen, Grossbuchstaben)."""
    return re.sub(r"\s+", "", str(code or "")).upper()


def lade_modul(pfad: Path):
    """Laedt ein Extraktionsmodul dynamisch per Dateipfad."""
    spec = importlib.util.spec_from_file_location(pfad.stem, pfad)
    if spec is None or spec.loader is None:
        raise ImportError(f"Modul konnte nicht geladen werden: {pfad}")
    modul = importlib.util.module_from_spec(spec)
    sys.modules[pfad.stem] = modul
    spec.loader.exec_module(modul)
    return modul


def _art_aus_code(code: str) -> str:
    """Leitet die Sondierungsart aus dem Praefix einer Kennung ab."""
    text = str(code or "").upper()
    treffer = re.match(r"^\s*(DPSH|CPTU|DPH|DPL|DPM|CPT|SRS|DS)\b", text)
    if not treffer:
        treffer = re.match(r"^\s*(DPSH|CPTU|DPH|DPL|DPM|CPT|SRS|DS)", text)
    if not treffer:
        return "DPH"
    art = treffer.group(1)
    if art == "DS":
        return "CPT"
    if art == "CPTU":
        return "CPTu"
    return art


def _normalisiere_ausgabe(rohausgabe) -> list[dict]:
    """Bringt Ausgaben von lesen(), prototyp_v4.extract() oder to_canonical() in ein einheitliches Schema."""
    if isinstance(rohausgabe, dict) and "soundings" in rohausgabe:
        rohausgabe = rohausgabe["soundings"]
    if isinstance(rohausgabe, dict):
        liste: list[dict] = []
        for code, schritte in rohausgabe.items():
            werte = [
                [float(a), float(b), v if isinstance(v, dict) else float(v)]
                for a, b, v in (schritte or [])
            ]
            endtiefe = max(float(b) for _, b, _ in schritte) if schritte else None
            liste.append(
                {
                    "code": str(code),
                    "art": _art_aus_code(str(code)),
                    "seite": None,
                    "form": "diagramm",
                    "werte": werte,
                    "endtiefe": endtiefe,
                    "ansatzhoehe": None,
                    "konfidenz": 1.0,
                }
            )
        return liste
    if isinstance(rohausgabe, list):
        normalisiert: list[dict] = []
        for eintrag in rohausgabe:
            if isinstance(eintrag, dict):
                kopie = dict(eintrag)
                if not kopie.get("art"):
                    kopie["art"] = _art_aus_code(str(kopie.get("code") or ""))
                normalisiert.append(kopie)
        return normalisiert
    raise TypeError(f"Unerwarteter Rueckgabetyp der Extraktion: {type(rohausgabe).__name__}")


def extrahiere_sondierungen(modul, pdf: Path, ocr: bool = True) -> tuple[list[dict], int, float]:
    """Fuehrt die Extraktion fuer ein PDF aus und liefert (Sondierungen, Seitenanzahl, Laufzeit_ms)."""
    if hasattr(modul, "lesen"):
        with pymupdf.open(pdf) as dok:
            seiten = len(dok)
            t0 = time.perf_counter()
            rohausgabe = modul.lesen(pdf, doc=dok, ocr=ocr)
            t1 = time.perf_counter()
    elif hasattr(modul, "extract"):
        with pymupdf.open(pdf) as dok:
            seiten = len(dok)
        regeln = getattr(modul, "RULES", None)
        vorher_ocr = None
        if not ocr and isinstance(regeln, dict) and "ocr" in regeln:
            vorher_ocr = regeln["ocr"]
            regeln["ocr"] = False
        try:
            t0 = time.perf_counter()
            _, dph = modul.extract(pdf)
            t1 = time.perf_counter()
        finally:
            if vorher_ocr is not None:
                regeln["ocr"] = vorher_ocr
        rohausgabe = dph or {}
    else:
        raise AttributeError("Modul besitzt weder 'lesen' noch 'extract'.")
    laufzeit_ms = round((t1 - t0) * 1000.0, 2)
    return _normalisiere_ausgabe(rohausgabe), seiten, laufzeit_ms


def synth_truth(pdf: Path) -> dict:
    """Wandelt die Bohrprofil-Wahrheit von synth_bohrprofil.py ins Sondierungs-Schema um."""
    roh = json.loads(pdf.with_suffix(".json").read_text(encoding="utf-8"))
    sondierungen: list[dict] = []
    for bh in roh:
        dph = bh.get("dph") or []
        if not dph:
            continue
        teile = str(bh.get("code") or "").split()
        nummer = teile[1] if len(teile) > 1 else str(bh.get("code") or "")
        code = f"DPH {nummer}".strip()
        vorher = 0.0
        werte: list[list] = []
        for tiefe_u, schlagzahl in dph:
            d_u = float(tiefe_u)
            n_val = (
                int(schlagzahl)
                if isinstance(schlagzahl, int) or float(schlagzahl).is_integer()
                else float(schlagzahl)
            )
            werte.append([round(vorher, 4), d_u, n_val])
            vorher = d_u
        sondierungen.append(
            {
                "code": code,
                "art": "DPH",
                "seite": 1,
                "auch_auf_seiten": [],
                "form": "diagramm",
                "ansatzhoehe": bh.get("gok"),
                "endtiefe": float(dph[-1][0]),
                "werte": werte,
                "stichprobe": [],
                "unsicher": [],
            }
        )
    return {"file": pdf.name, "sondierungen": sondierungen}


def _datei_sha256(pfad: Path) -> str:
    return hashlib.sha256(pfad.read_bytes()).hexdigest()


def faelle_sammeln(
    real_ordner: Path | None,
    gt_ordner: Path,
    stress_ordner: Path | None,
    synth_ordner: Path | None,
) -> list[tuple[str, Path, dict]]:
    """Sammelt alle auszuwertenden (Fallname, PDF-Pfad, Wahrheits-Dict)-Tupel."""
    faelle: list[tuple[str, Path, dict]] = []
    if real_ordner is not None:
        stems = sorted(
            {p.stem for p in (HERE / "groundtruth").glob("*.json")}
            | {p.stem for p in gt_ordner.glob("*.json")}
        )
        for stem in stems:
            pdf = real_ordner / f"{stem}.pdf"
            if not pdf.exists():
                continue
            gt_pfad = gt_ordner / f"{stem}.json"
            if gt_pfad.exists():
                gt = json.loads(gt_pfad.read_text(encoding="utf-8"))
                erw_sha = gt.get("sha256")
                if erw_sha:
                    ist_sha = _datei_sha256(pdf)
                    if ist_sha != erw_sha:
                        print(
                            f"Warnung: SHA256-Abweichung bei {pdf.name} "
                            f"(erwartet {erw_sha[:12]}, vorhanden {ist_sha[:12]}).",
                            file=sys.stderr,
                        )
            else:
                gt = {"file": pdf.name, "sondierungen": []}
            faelle.append((f"real/{stem}", pdf, gt))

    if stress_ordner is not None:
        for js in sorted(stress_ordner.glob("s*.json")):
            pdf = js.with_suffix(".pdf")
            if pdf.exists():
                faelle.append((f"stress/{js.stem}", pdf, json.loads(js.read_text(encoding="utf-8"))))

    if synth_ordner is not None:
        for pdf in sorted(synth_ordner.glob("synth_*.pdf")):
            if pdf.with_suffix(".json").exists():
                faelle.append((f"synth/{pdf.stem}", pdf, synth_truth(pdf)))

    return faelle


def _entpacke_wert(wert) -> tuple[float | None, bool]:
    """Liefert (numerischer_wert, zensiert_flag) fuer Zahl oder Zensur-Dict."""
    if wert is None:
        return None, False
    if isinstance(wert, dict):
        roh = wert.get("wert")
        return (float(roh) if roh is not None else None), bool(wert.get("zensiert", False))
    return float(wert), False


def _abgeleitete_endtiefe(sond: dict, art_gross: str) -> float | None:
    """Liest endtiefe oder leitet sie bei Bedarf aus der letzten Wertezeile ab."""
    endtiefe = sond.get("endtiefe")
    if endtiefe is not None:
        return float(endtiefe)
    werte = sond.get("werte") or []
    if not werte:
        return None
    letzte = werte[-1]
    if art_gross in DPH_ARTEN and len(letzte) >= 3:
        return float(letzte[1])
    if len(letzte) >= 1:
        return float(letzte[0])
    return None


def _cpt_qc_vorhersage(pred_punkte: list[tuple[float, float]], tiefe_gt: float) -> float | None:
    """Bestimmt q_c an tiefe_gt via Naechstwert (<= 5 cm) oder linearer Interpolation (<= 25 cm)."""
    if not pred_punkte:
        return None
    naechster = min(pred_punkte, key=lambda pt: abs(pt[0] - tiefe_gt))
    if abs(naechster[0] - tiefe_gt) <= 0.05 + 1e-9:
        return naechster[1]
    links = [pt for pt in pred_punkte if pt[0] < tiefe_gt]
    rechts = [pt for pt in pred_punkte if pt[0] > tiefe_gt]
    if not links or not rechts:
        return None
    p_l = max(links, key=lambda pt: pt[0])
    p_r = min(rechts, key=lambda pt: pt[0])
    spanne = p_r[0] - p_l[0]
    if spanne <= 0 or spanne > 0.25 + 1e-9:
        return None
    anteil = (tiefe_gt - p_l[0]) / spanne
    return p_l[1] + (p_r[1] - p_l[1]) * anteil


def _bewerte_fall(gt: dict, preds: list[dict], seiten: int, laufzeit_ms: float) -> tuple[dict, dict]:
    """Berechnet alle Metriken fuer ein PDF sowie die Rohzaehler fuer die Aggregation."""
    gt_sond = gt.get("sondierungen") or []
    pred_sond = preds or []

    # 1:1-Zuordnung (normierter Code + erlaubte Seite, Hauptseite bevorzugt).
    kandidaten: list[tuple[tuple[bool, bool, float, int, int], int, int]] = []
    for g_idx, g in enumerate(gt_sond):
        g_norm = norm(g.get("code"))
        erlaubte_seiten = {g.get("seite")} | set(g.get("auch_auf_seiten") or [])
        for p_idx, p in enumerate(pred_sond):
            if norm(p.get("code")) != g_norm:
                continue
            p_seite = p.get("seite")
            if p_seite is not None and p_seite not in erlaubte_seiten:
                continue
            rang = (
                p_seite == g.get("seite"),
                bool(p.get("werte")),
                float(p.get("konfidenz") or 0.0),
                -g_idx,
                -p_idx,
            )
            kandidaten.append((rang, g_idx, p_idx))

    kandidaten.sort(key=lambda eintrag: eintrag[0], reverse=True)
    genutzt_g: set[int] = set()
    genutzt_p: set[int] = set()
    paare: list[tuple[dict, dict]] = []
    zuordnung: dict[int, dict] = {}
    for _, g_idx, p_idx in kandidaten:
        if g_idx in genutzt_g or p_idx in genutzt_p:
            continue
        genutzt_g.add(g_idx)
        genutzt_p.add(p_idx)
        zuordnung[g_idx] = pred_sond[p_idx]
        paare.append((gt_sond[g_idx], pred_sond[p_idx]))

    gefunden_treffer = len(paare)
    erwartet = len(gt_sond)
    falsche_sond = len(pred_sond) - gefunden_treffer
    code_treffer = sum(1 for g, p in paare if norm(p.get("code")) == norm(g.get("code")))

    end_treffer = 0
    end_gesamt = 0
    dph_treffer = 0
    dph_gesamt = 0
    cpt_treffer = 0
    cpt_gesamt = 0
    cpt_fehler: list[float] = []
    falsche_werte = 0

    for g_idx, g in enumerate(gt_sond):
        p = zuordnung.get(g_idx)
        art_gross = str(g.get("art") or "").upper()

        if g.get("endtiefe") is not None:
            end_gesamt += 1
            if p is not None:
                p_end = _abgeleitete_endtiefe(p, art_gross)
                if p_end is not None and abs(p_end - float(g["endtiefe"])) <= 0.05 + 1e-9:
                    end_treffer += 1

        if art_gross in DPH_ARTEN:
            gt_schritte = g.get("werte") or []
            dph_gesamt += len(gt_schritte)
            if p is not None:
                p_schritte = p.get("werte") or []
                schritt_kand: list[tuple[tuple[float, float, int, int], int, int]] = []
                for gi, gz in enumerate(gt_schritte):
                    gt_o, gt_u = float(gz[0]), float(gz[1])
                    min_ov = 0.5 * (gt_u - gt_o) - 1e-6
                    for pi, pz in enumerate(p_schritte):
                        if len(pz) < 3:
                            continue
                        p_o, p_u = float(pz[0]), float(pz[1])
                        ov = min(gt_u, p_u) - max(gt_o, p_o)
                        if ov >= min_ov:
                            schritt_kand.append(((-ov, abs(p_o - gt_o), gi, pi), gi, pi))
                schritt_kand.sort(key=lambda eintrag: eintrag[0])
                verbraucht_g: set[int] = set()
                verbraucht_p: set[int] = set()
                for _, gi, pi in schritt_kand:
                    if gi in verbraucht_g or pi in verbraucht_p:
                        continue
                    verbraucht_g.add(gi)
                    verbraucht_p.add(pi)
                    g_num, g_zens = _entpacke_wert(gt_schritte[gi][2])
                    p_num, p_zens = _entpacke_wert(p_schritte[pi][2])
                    if (
                        g_num is not None
                        and p_num is not None
                        and p_zens == g_zens
                        and abs(p_num - g_num) <= 1.0 + 1e-6
                    ):
                        dph_treffer += 1
                falsche_werte += len(p_schritte) - len(verbraucht_p)

        elif art_gross in CPT_ARTEN:
            gt_zeilen = [z for z in (g.get("werte") or []) if len(z) >= 2 and z[1] is not None]
            cpt_gesamt += len(gt_zeilen)
            gt_qc_werte = [
                val
                for val, _ in (_entpacke_wert(z[1]) for z in gt_zeilen)
                if val is not None
            ]
            if g.get("qc_axis_range") is not None:
                qc_spanne = float(g["qc_axis_range"])
            elif gt_qc_werte:
                qc_spanne = max(gt_qc_werte) - min(0.0, min(gt_qc_werte))
            else:
                qc_spanne = 0.0

            if p is not None:
                p_zeilen = p.get("werte") or []
                pred_qc_punkte: list[tuple[float, float]] = []
                for pz in p_zeilen:
                    if len(pz) >= 2 and pz[1] is not None:
                        p_qc, _ = _entpacke_wert(pz[1])
                        if p_qc is not None:
                            pred_qc_punkte.append((float(pz[0]), p_qc))
                pred_qc_punkte.sort(key=lambda pt: pt[0])

                for gz in gt_zeilen:
                    t_gt = float(gz[0])
                    qc_gt, _ = _entpacke_wert(gz[1])
                    if qc_gt is None or qc_spanne <= 0.0:
                        continue
                    qc_p = _cpt_qc_vorhersage(pred_qc_punkte, t_gt)
                    if qc_p is not None:
                        cpt_treffer += 1
                        cpt_fehler.append(abs(qc_p - qc_gt) / qc_spanne * 100.0)

                gt_tiefen = sorted(float(z[0]) for z in gt_zeilen)
                if len(gt_tiefen) >= 2:
                    dts = [gt_tiefen[i + 1] - gt_tiefen[i] for i in range(len(gt_tiefen) - 1)
                           if gt_tiefen[i + 1] > gt_tiefen[i]]
                    median_dt = statistics.median(dts) if dts else 0.0
                else:
                    median_dt = 0.0
                tiefe_tol = max(0.15, 0.75 * median_dt) + 1e-9
                for pz in p_zeilen:
                    if not gt_tiefen or min(abs(float(pz[0]) - tg) for tg in gt_tiefen) > tiefe_tol:
                        falsche_werte += 1

    for p_idx, p in enumerate(pred_sond):
        if p_idx not in genutzt_p:
            falsche_werte += len(p.get("werte") or [])

    laufzeit_je_seite_ms = round(laufzeit_ms / max(seiten, 1), 2)
    ergebnis = {
        "seiten": seiten,
        "laufzeit_ms": laufzeit_ms,
        "laufzeit_je_seite_ms": laufzeit_je_seite_ms,
        "gefunden": f"{gefunden_treffer}/{erwartet}",
        "falsche_sondierungen": falsche_sond,
        "code_richtig": f"{code_treffer}/{erwartet}",
        "endtiefe_5cm": f"{end_treffer}/{end_gesamt}",
        "dph_schritt_1": f"{dph_treffer}/{dph_gesamt}",
        "cpt_punkte": f"{cpt_treffer}/{cpt_gesamt}",
        "cpt_qc_mittel_pct": round(sum(cpt_fehler) / len(cpt_fehler), 4) if cpt_fehler else None,
        "cpt_qc_max_pct": round(max(cpt_fehler), 4) if cpt_fehler else None,
        "falsche_werte": falsche_werte,
    }
    rohzaehler = {
        "seiten": seiten,
        "laufzeit_ms": laufzeit_ms,
        "gefunden": [gefunden_treffer, erwartet],
        "falsche_sondierungen": falsche_sond,
        "code_richtig": [code_treffer, erwartet],
        "endtiefe_5cm": [end_treffer, end_gesamt],
        "dph_schritt_1": [dph_treffer, dph_gesamt],
        "cpt_punkte": [cpt_treffer, cpt_gesamt],
        "cpt_fehler": cpt_fehler,
        "falsche_werte": falsche_werte,
    }
    return ergebnis, rohzaehler


def _aggregiere(liste_roh: list[dict]) -> dict:
    """Fasst Rohzaehler mehrerer Faelle zu einem Datensatz- oder Gesamtergebnis zusammen."""
    seiten = sum(r["seiten"] for r in liste_roh)
    laufzeit_ms = round(sum(r["laufzeit_ms"] for r in liste_roh), 2)
    gef_a = sum(r["gefunden"][0] for r in liste_roh)
    gef_b = sum(r["gefunden"][1] for r in liste_roh)
    code_a = sum(r["code_richtig"][0] for r in liste_roh)
    code_b = sum(r["code_richtig"][1] for r in liste_roh)
    end_a = sum(r["endtiefe_5cm"][0] for r in liste_roh)
    end_b = sum(r["endtiefe_5cm"][1] for r in liste_roh)
    dph_a = sum(r["dph_schritt_1"][0] for r in liste_roh)
    dph_b = sum(r["dph_schritt_1"][1] for r in liste_roh)
    cpt_a = sum(r["cpt_punkte"][0] for r in liste_roh)
    cpt_b = sum(r["cpt_punkte"][1] for r in liste_roh)
    cpt_alle = [err for r in liste_roh for err in r["cpt_fehler"]]
    return {
        "seiten": seiten,
        "laufzeit_ms": laufzeit_ms,
        "laufzeit_je_seite_ms": round(laufzeit_ms / max(seiten, 1), 2),
        "gefunden": f"{gef_a}/{gef_b}",
        "falsche_sondierungen": sum(r["falsche_sondierungen"] for r in liste_roh),
        "code_richtig": f"{code_a}/{code_b}",
        "endtiefe_5cm": f"{end_a}/{end_b}",
        "dph_schritt_1": f"{dph_a}/{dph_b}",
        "cpt_punkte": f"{cpt_a}/{cpt_b}",
        "cpt_qc_mittel_pct": round(sum(cpt_alle) / len(cpt_alle), 4) if cpt_alle else None,
        "cpt_qc_max_pct": round(max(cpt_alle), 4) if cpt_alle else None,
        "falsche_werte": sum(r["falsche_werte"] for r in liste_roh),
    }


def _bruch(wert: str) -> tuple[int, int]:
    a, _, b = str(wert).partition("/")
    return (int(a), int(b)) if b else (0, 0)


def _format_pct(wert: float | None) -> str:
    return "-" if wert is None else f"{wert:.2f}%"


def _zeile_drucken(name: str, res: dict) -> None:
    if "Fehler" in res:
        print(f"{name:34s} FEHLER: {res['Fehler']}", flush=True)
        return
    print(
        f"{name:34s} {res['seiten']:3d}S {res['laufzeit_je_seite_ms']:7.1f}ms/S "
        f"gef={res['gefunden']:>6s} falschS={res['falsche_sondierungen']:2d} "
        f"code={res['code_richtig']:>6s} end={res['endtiefe_5cm']:>6s} "
        f"dph={res['dph_schritt_1']:>9s} cpt={res['cpt_punkte']:>7s} "
        f"qc_m={_format_pct(res['cpt_qc_mittel_pct']):>7s} "
        f"qc_x={_format_pct(res['cpt_qc_max_pct']):>7s} "
        f"falschW={res['falsche_werte']:3d}",
        flush=True,
    )


def _werte_ausfuehren(
    modul,
    faelle: list[tuple[str, Path, dict]],
    ocr: bool,
    quiet: bool,
) -> tuple[dict[str, dict], dict[str, dict], dict]:
    ergebnisse: dict[str, dict] = {}
    roh_nach_datensatz: dict[str, list[dict]] = {}
    alle_roh: list[dict] = []

    for name, pdf, gt in faelle:
        seiten = 0
        laufzeit_ms = 0.0
        try:
            preds, seiten, laufzeit_ms = extrahiere_sondierungen(modul, pdf, ocr=ocr)
            res, roh = _bewerte_fall(gt, preds, seiten, laufzeit_ms)
        except Exception as exc:
            res = {
                "seiten": seiten,
                "laufzeit_ms": laufzeit_ms,
                "laufzeit_je_seite_ms": round(laufzeit_ms / max(seiten, 1), 2),
                "Fehler": repr(exc)[:160],
            }
            roh = {
                "seiten": seiten,
                "laufzeit_ms": laufzeit_ms,
                "gefunden": [0, len(gt.get("sondierungen") or [])],
                "falsche_sondierungen": 0,
                "code_richtig": [0, len(gt.get("sondierungen") or [])],
                "endtiefe_5cm": [0, sum(1 for s in (gt.get("sondierungen") or []) if s.get("endtiefe") is not None)],
                "dph_schritt_1": [0, 0],
                "cpt_punkte": [0, 0],
                "cpt_fehler": [],
                "falsche_werte": 0,
            }
        ergebnisse[name] = res
        datensatz = name.split("/", 1)[0]
        roh_nach_datensatz.setdefault(datensatz, []).append(roh)
        alle_roh.append(roh)
        if not quiet:
            _zeile_drucken(name, res)

    nach_datensatz = {ds: _aggregiere(liste) for ds, liste in roh_nach_datensatz.items()}
    summe = _aggregiere(alle_roh)
    if not quiet:
        for ds, ds_res in nach_datensatz.items():
            _zeile_drucken(f"DATENSATZ/{ds}", ds_res)
    _zeile_drucken("SUMME", summe)
    return ergebnisse, nach_datensatz, summe


def _pruefe_baseline(
    ergebnisse: dict[str, dict],
    baseline_pfad: Path,
    tol_cpt: float,
) -> int:
    if not ergebnisse:
        print("Fehler: Keine Faelle fuer den Baseline-Vergleich ausgewertet.", file=sys.stderr)
        return 2
    if not baseline_pfad.exists():
        print(f"Fehler: Baseline-Datei fehlt: {baseline_pfad}", file=sys.stderr)
        return 2

    basis_dok = json.loads(baseline_pfad.read_text(encoding="utf-8"))
    basis_faelle = basis_dok.get("faelle", basis_dok)
    status = 0

    for name, res in ergebnisse.items():
        if "Fehler" in res:
            print(f"REGRESSION {name}: {res['Fehler']}")
            status = 1
            continue
        alt = basis_faelle.get(name)
        if not alt:
            continue
        for feld in GUTE_BRUECHE:
            if feld in alt and _bruch(res.get(feld, "0/0"))[0] < _bruch(alt[feld])[0]:
                print(f"REGRESSION {name}: {feld} {alt[feld]} -> {res.get(feld)}")
                status = 1
        for feld in SCHLECHTE_ZAHLEN:
            if res.get(feld, 0) > alt.get(feld, 0):
                print(f"REGRESSION {name}: {feld} {alt.get(feld)} -> {res.get(feld)}")
                status = 1
        for feld in CPT_FEHLER_FELDER:
            alt_wert = alt.get(feld)
            if alt_wert is not None:
                neu_wert = res.get(feld)
                if neu_wert is None or neu_wert > alt_wert + tol_cpt:
                    print(f"REGRESSION {name}: {feld} {alt_wert} -> {neu_wert}")
                    status = 1

    print("OK: keine Regression" if status == 0 else "FEHLGESCHLAGEN")
    return status


def _baue_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bewertet die Sondierungsextraktion gegen echte, Stress- und synthetische Wahrheiten."
    )
    parser.add_argument(
        "--module",
        default=str(REPO_WURZEL / "services" / "extractor" / "sondierungen.py"),
        help="Pfad zum Extraktionsmodul (Standard: services/extractor/sondierungen.py)",
    )
    parser.add_argument("--real", help="Ordner mit echten PDFs")
    parser.add_argument(
        "--gt",
        default=str(HERE / "groundtruth_sondierungen"),
        help="Ordner mit Sondierungs-Grundwahrheiten (Standard: benchmark/groundtruth_sondierungen)",
    )
    parser.add_argument("--stress", help="Ordner mit Stressfaellen (stress_sondierungen.py)")
    parser.add_argument("--synth", help="Ordner mit synthetischen PDFs (synth_bohrprofil.py)")
    parser.add_argument(
        "--baseline",
        nargs="?",
        const=str(HERE / "baseline_sondierungen.json"),
        default=None,
        help="Pfad zur Baseline-JSON-Datei fuer den Regressionstest",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Schreibt das Auswertungsergebnis als Baseline-JSON",
    )
    parser.add_argument(
        "--disable",
        default="",
        help="Kommagetrennte Regelnamen in REGELN oder RULES fuer die Ablation abschalten",
    )
    parser.add_argument(
        "--no-ocr",
        action="store_true",
        help="OCR waehrend der Auswertung deaktivieren",
    )
    parser.add_argument(
        "--tol-cpt",
        type=float,
        default=0.05,
        help="Toleranz in Prozentpunkten fuer den CPT-q_c-Regressionsvergleich (Standard: 0.05)",
    )
    parser.add_argument("--quiet", action="store_true", help="Nur Zusammenfassung ausgeben")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _baue_parser()
    args = parser.parse_args(argv)

    modul_pfad = Path(args.module).resolve()
    modul = lade_modul(modul_pfad)

    if args.disable:
        regeln = getattr(modul, "REGELN", None)
        if regeln is None:
            regeln = getattr(modul, "RULES", None)
        if not isinstance(regeln, dict):
            print("Fehler: Modul besitzt weder REGELN noch RULES.", file=sys.stderr)
            return 2
        for regel in filter(None, (x.strip() for x in args.disable.split(","))):
            if regel not in regeln:
                print(f"Fehler: Unbekannte Regel '{regel}'.", file=sys.stderr)
                return 2
            regeln[regel] = False

    ziel_baseline: Path | None = None
    if args.baseline:
        ziel_baseline = Path(args.baseline)
    elif args.write:
        ziel_baseline = HERE / "baseline_sondierungen.json"

    gt_ordner = Path(args.gt)
    real_ordner = Path(args.real) if args.real else None
    stress_ordner = Path(args.stress) if args.stress else None
    synth_ordner = Path(args.synth) if args.synth else None

    if real_ordner is None and stress_ordner is None and synth_ordner is None:
        import stress_sondierungen
        import synth_bohrprofil

        with tempfile.TemporaryDirectory() as tmp:
            tmp_pfad = Path(tmp)
            auto_stress = tmp_pfad / "stress"
            auto_synth = tmp_pfad / "synth"
            stress_sondierungen.build(auto_stress)
            for layout_schluessel in synth_bohrprofil.LAYOUTS:
                synth_bohrprofil.make(layout_schluessel, auto_synth)
            faelle = faelle_sammeln(None, gt_ordner, auto_stress, auto_synth)
            ergebnisse, nach_datensatz, summe = _werte_ausfuehren(
                modul, faelle, ocr=not args.no_ocr, quiet=args.quiet
            )
    else:
        faelle = faelle_sammeln(real_ordner, gt_ordner, stress_ordner, synth_ordner)
        if not faelle:
            print("Fehler: Keine auszuwertenden PDF-Faelle gefunden.", file=sys.stderr)
            return 2
        ergebnisse, nach_datensatz, summe = _werte_ausfuehren(
            modul, faelle, ocr=not args.no_ocr, quiet=args.quiet
        )

    if args.write and ziel_baseline is not None:
        huelle = hashlib.sha256(modul_pfad.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        dok = {
            "_meta": {
                "modul": modul_pfad.name,
                "sha256": huelle,
                "ocr": not args.no_ocr,
                "schema_version": 1,
            },
            "faelle": ergebnisse,
            "nach_datensatz": nach_datensatz,
            "summe": summe,
        }
        ziel_baseline.parent.mkdir(parents=True, exist_ok=True)
        ziel_baseline.write_text(json.dumps(dok, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Baseline geschrieben: {ziel_baseline}")
        return 0

    if ziel_baseline is not None:
        return _pruefe_baseline(ergebnisse, ziel_baseline, tol_cpt=args.tol_cpt)

    return 0


if __name__ == "__main__":
    sys.exit(main())
