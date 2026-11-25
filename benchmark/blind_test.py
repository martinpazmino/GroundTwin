"""Blindtest-Protokoll: erst Vorhersagen einfrieren, dann Wahrheit anlegen, dann bewerten.

    python blind_test.py freeze <ordner_mit_neuen_pdfs> <ausgabe>       # vor dem Anschauen der PDFs
    # ... groundtruth/<name>.json anlegen ...
    python blind_test.py score <ausgabe> [<ordner_swissgeol>]           # bewertet die eingefrorenen Dateien

Sondierungen (ab Runde 5): <ausgabe>/<name>.sondierungen.json wird gegen groundtruth_sondierungen/<name>.json
bewertet, einmal streng (Code + Seite) und einmal nach Seite (Code nicht verglichen). Werte einer Wahrheit mit
werte_nicht_transkribiert zaehlen nicht (weder richtig noch falsch).

Die eingefrorenen JSON-Dateien enthalten den Code-Stand (git rev) und koennen per sha256 belegt werden.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from eval_real import run_sg, run_v1, run_v4, score  # noqa: E402


def freeze(src: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=HERE, capture_output=True, text=True).stdout.strip()
    for pdf in sorted(src.glob("*.pdf")):
        v4, bhs = run_v4(pdf)
        detail = [{"code": b.code, "page": b.page, "scale": b.scale, "mode": b.mode, "gok": b.gok,
                   "bottoms": [ly.bottom for ly in b.layers], "soils": [ly.soil for ly in b.layers],
                   "unconfirmed": sum(not ly.label_confirmed for ly in b.layers),
                   "gw": b.gw_depths, "gw_status": b.gw_status, "dups": b.duplicates}
                  for b in bhs]
        sha = hashlib.sha256(pdf.read_bytes()).hexdigest()
        (out / f"{pdf.stem}.json").write_text(json.dumps(
            {"code_rev": rev, "pdf_sha256": sha, "v1": run_v1(pdf), "v4": v4, "v4_detail": detail},
            indent=1, default=float))
        print(pdf.stem, "v4 Bohrungen:", len(v4))


def score_sondierungen(gt: dict, preds: list[dict]) -> dict:
    """Bewertet eingefrorene Sondierungen; streng (Code) und nach Seite, Werte nur wo transkribiert."""
    from sondierungen_eval import _abgeleitete_endtiefe, _bewerte_fall

    ohne_werte = {s for g in gt.get("sondierungen") or [] if g.get("werte_nicht_transkribiert")
                  for s in [g.get("seite"), *(g.get("auch_auf_seiten") or [])]}     # Seiten ohne transkribierte Werte
    seiten = {}
    for g in gt.get("sondierungen") or []:
        seiten.setdefault(g.get("seite"), []).append(g)

    def ohne(p: dict, code: str) -> dict:
        if p.get("seite") in ohne_werte or p.get("seite") is None:
            return {**p, "endtiefe": _abgeleitete_endtiefe(p, str(p.get("art") or "").upper()), "werte": []}
        return p

    streng = [ohne(p, p.get("code")) for p in preds]
    # nach Seite: eine Vorhersage auf der Hauptseite einer Wahrheit derselben Art traegt deren Code
    nach_seite = []
    for p in preds:
        kand = [g for g in seiten.get(p.get("seite"), []) if str(g.get("art")).upper() == str(p.get("art")).upper()]
        code = kand[0]["code"] if len(kand) == 1 else p.get("code")
        nach_seite.append(ohne({**p, "code": code}, code))
    a, _ = _bewerte_fall(gt, streng, 0, 0.0)
    b, _ = _bewerte_fall(gt, nach_seite, 0, 0.0)
    gok = sum(1 for g in gt.get("sondierungen") or [] for p in nach_seite
              if p.get("seite") == g.get("seite") and p["code"] == g["code"] and g.get("ansatzhoehe") is not None
              and p.get("ansatzhoehe") is not None and abs(p["ansatzhoehe"] - g["ansatzhoehe"]) < 0.01)
    felder = ("gefunden", "falsche_sondierungen", "endtiefe_5cm", "dph_schritt_1", "cpt_punkte", "falsche_werte")
    return {"streng": {k: a[k] for k in felder}, "nach_seite": {**{k: b[k] for k in felder}, "ansatzhoehe": gok}}


def score_frozen(out: Path, sg_dir: Path | None) -> None:
    for sd_file in sorted(out.glob("*.sondierungen.json")):
        gt_file = HERE / "groundtruth_sondierungen" / sd_file.name.replace(".sondierungen", "")
        if gt_file.exists():
            gt, pred = json.loads(gt_file.read_text()), json.loads(sd_file.read_text())
            print(f"== {sd_file.stem} (Stufe sha256 {str(pred.get('modul_sha256'))[:12]})")
            for art, r in score_sondierungen(gt, pred["sondierungen"]).items():
                print(f"   {art:10}", r)
    for pred_file in sorted(out.glob("*.json")):
        gt_file = HERE / "groundtruth" / pred_file.name
        if not gt_file.exists():
            continue
        gt, pred = json.loads(gt_file.read_text()), json.loads(pred_file.read_text())
        print(f"== {pred_file.stem} (Code-Stand {pred.get('code_rev')})")
        print("   v1 ", score(gt, pred["v1"]))
        for version in ("v4", "v3"):                     # v3: eingefrorene Dateien bis Runde 4
            if version in pred:
                print(f"   {version} ", score(gt, pred[version]))
        if "sg" in pred:                                   # mit eingefroren (ab Runde 3)
            print("   sg ", score(gt, pred["sg"]))
        elif sg_dir and (sg := sg_dir / f"real_out_{pred_file.stem}" / "predictions.json").exists():
            print("   sg ", score(gt, run_sg(sg, pred_file.stem)))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "freeze":
        freeze(Path(sys.argv[2]), Path(sys.argv[3]))
    else:
        score_frozen(Path(sys.argv[2]), Path(sys.argv[3]) if len(sys.argv) > 3 else None)
