"""Funktionskarte (docs/feature_map.json, docs/31 §3.3) gegen den Code: jede Route der API und jede Operation von
ui/projekt.aendern steht in der Karte, jeder Beweis (Test, Pruefung von Ende zu Ende) existiert.

So bleibt die Karte die gemeinsame Sprache fuer Agenten und Menschen ('wo ist X, was beweist, dass X geht'), und eine
Funktion verschwindet nicht still: wer eine Route oder Operation entfernt, muss sie auch aus der Karte nehmen
(CLAUDE.md: nie loeschen, einklappen).
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
KARTE = json.loads((REPO / "docs/feature_map.json").read_text(encoding="utf-8"))
SCHRITTE = {"Start", "Bohrungen", "Lage", "Einheiten", "Modell", "Werkzeug", "System"}


def routen_im_code() -> set[str]:
    text = (REPO / "server/api.py").read_text(encoding="utf-8")
    return {f"{m.upper()} {p}" for m, p in re.findall(r'@app\.(get|post|put|delete|patch)\("([^"]+)"', text)}


def ops_im_code() -> set[str]:
    baum = ast.parse((REPO / "ui/projekt.py").read_text(encoding="utf-8"))
    f = next(n for n in baum.body if isinstance(n, ast.FunctionDef) and n.name == "aendern")
    ops = set()
    for n in ast.walk(f):
        if isinstance(n, ast.Compare) and isinstance(n.left, ast.Name) and n.left.id == "art":
            for c in n.comparators:
                werte = c.elts if isinstance(c, (ast.Tuple, ast.List, ast.Set)) else [c]
                ops |= {w.value for w in werte if isinstance(w, ast.Constant) and isinstance(w.value, str)}
    return ops


def e2e_pruefungen() -> list[str]:
    text = (REPO / "scripts/check_app.mjs").read_text(encoding="utf-8")
    return re.findall(r'pruefe\(\s*"([^"]+)"', text)


def test_jede_route_steht_in_der_karte():
    karte = {r for f in KARTE["funktionen"] for r in f["routen"]}
    code = routen_im_code()
    fehlt, alt = code - karte, karte - code
    assert not fehlt, (f"Routen ohne Eintrag in docs/feature_map.json: {sorted(fehlt)}. Neue Funktion eintragen: "
                       f"Schritt, eingeklappt oder nicht, und was beweist, dass sie geht.")
    assert not alt, f"Karte nennt Routen, die es nicht gibt: {sorted(alt)}. Nie still loeschen: einklappen (D99)."


def test_jede_operation_steht_in_der_karte():
    karte = {o for f in KARTE["funktionen"] for o in f["ops"]}
    code = ops_im_code()
    assert len(code) > 20, "Operationen in ui/projekt.aendern nicht gefunden: Erkennung pruefen"
    assert not code - karte, f"Operationen ohne Eintrag in docs/feature_map.json: {sorted(code - karte)}"
    assert not karte - code, f"Karte nennt Operationen, die es nicht gibt: {sorted(karte - code)}"


def test_jede_funktion_hat_einen_beweis_der_existiert():
    e2e = e2e_pruefungen()
    assert len(e2e) > 40, "Pruefungen in scripts/check_app.mjs nicht gefunden: Erkennung pruefen"
    ids, fehler = set(), []
    for f in KARTE["funktionen"]:
        assert f["id"] not in ids, f"doppelte id {f['id']}"
        ids.add(f["id"])
        assert f["schritt"] in SCHRITTE, f"{f['id']}: Schritt {f['schritt']} nicht in {sorted(SCHRITTE)}"
        assert (REPO / f["doku"]).exists(), f"{f['id']}: Doku {f['doku']} fehlt"
        b = f["beweis"]
        if not b["tests"] and not b["e2e"]:
            fehler.append(f"{f['id']}: ohne Beweis. Einen Test oder eine Pruefung in scripts/check_app.mjs nennen.")
        for t in b["tests"]:
            datei, _, name = t.partition("::")
            p = REPO / datei
            if not p.exists() or (name and not re.search(rf"^def {re.escape(name)}\(", p.read_text(encoding="utf-8"), re.M)):
                fehler.append(f"{f['id']}: Test {t} gibt es nicht")
        for anfang in b["e2e"]:
            if not any(p.startswith(anfang) for p in e2e):
                fehler.append(f"{f['id']}: keine Pruefung in scripts/check_app.mjs beginnt mit '{anfang}'")
    assert not fehler, "\n".join(fehler)
