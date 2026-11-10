"""Kommandozeile:

    python -m baugrundanalyse <extraktion.json> [...] [--einheiten e.json] [--methode idw|tps] [--laeufe n]
                              [--punkt x y] [--bericht analyse.json]

Rechnet das Schichtmodell (services/modeler) und dazu Kreuzprobe, Unsicherheit und, mit --punkt, eine virtuelle
Bohrung. services/modeler muss im Suchpfad liegen (PYTHONPATH).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from baugrundmodell.einheiten import einheiten_aus_vorgabe
from baugrundmodell.modell import bauen

from . import kreuzprobe, unsicherheit, virtuelle_bohrung
from .unsicherheit import zusammenfassung


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="baugrundanalyse", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jsons", type=Path, nargs="+")
    ap.add_argument("--einheiten", type=Path)
    ap.add_argument("--methode", choices=["idw", "tps"], default="idw")
    ap.add_argument("--laeufe", type=int, default=100)
    ap.add_argument("--punkt", type=float, nargs=2, metavar=("X", "Y"))
    ap.add_argument("--bericht", type=Path)
    a = ap.parse_args(argv)
    docs = [json.loads(p.read_text(encoding="utf-8")) for p in a.jsons]
    vorgabe = einheiten_aus_vorgabe(json.loads(a.einheiten.read_text(encoding="utf-8"))) if a.einheiten else None
    try:
        m = bauen(docs, vorgabe, a.methode)
        k = kreuzprobe(m)
    except ValueError as err:
        print(f"Keine Analyse: {err}")
        return 2
    u = unsicherheit(m, k, laeufe=a.laeufe)
    aus = {"kreuzprobe": {x: v for x, v in k.items() if not x.startswith("_")}, "unsicherheit": zusammenfassung(u)}
    print(f"Kreuzprobe ({len(m.bohrungen)} Bohrungen), mittlerer Fehler der Unterkanten:")
    for name, v in k["methoden"].items():
        g = v["gesamt"]
        print(f"  {name}{' (Modell)' if name == k['methode_modell'] else ''}: "
              + (f"{g['mae']:.2f} m (max {g['max']:.2f} m, {g['n']} Grenzen)" if g["n"] else "nichts zu vergleichen"))
    print(f"Unsicherheit ({u['laeufe']} Läufe, Methode {u['methode']}):")
    for e in u["einheiten"]:
        if e["unterkante_bezifferbar"]:
            print(f"  {e['name']:<22} sigma Unterkante im Mittel {e['sigma_mittel_m']:.2f} m, 95 % der Fläche unter "
                  f"{e['sigma_p95_m']:.2f} m; {e['methoden_differenz_m']['gegen']} weicht bis "
                  f"{e['methoden_differenz_m']['max']:.2f} m ab")
        else:
            print(f"  {e['name']:<22} Unterkante nicht bezifferbar")
    for h in k["hinweise"] + u["hinweise"]:
        print(f"  Hinweis: {h}")
    if a.punkt:
        try:
            v = virtuelle_bohrung(m, a.punkt[0], a.punkt[1], u)
        except ValueError as err:
            print(f"Virtuelle Bohrung: {err}")
            return 2
        aus["virtuelle_bohrung"] = v
        print(f"Virtuelle Bohrung bei {v['x']:.1f} / {v['y']:.1f}: GOK {v['gok_nhn']:.2f} m NHN, "
              f"{v['abstand_m']:.1f} m von {v['naechste_bohrung']}")
        for s in v["schichten"]:
            pm = "" if s["sigma_unten_m"] is None else f" ± {s['sigma_unten_m']:.2f} m"
            print(f"  {s['tiefe_oben_m']:>6.2f} – {s['tiefe_unten_m']:>6.2f} m  {s['einheit']}{pm}"
                  f"{' (Unterkante offen)' if s['unterkante_offen'] else ''}")
    if a.bericht:
        a.bericht.write_text(json.dumps(aus, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
