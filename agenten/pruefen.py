"""Alle Pruefungen auf einen Blick, ohne Modell: Suiten parallel, Protokolle in Dateien, ein knappes Urteil
(docs/24 §3). Claude liest das Urteil statt der Protokolle."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import doku

PYTHON_PFADE = ["server", "ui", "services/geodaten", "services/modeler/baugrundmodell", "services/analyse", "agenten", "tests", "scripts"]


def suiten(repo: Path, web: bool = False, schnell: bool = False) -> list[tuple[str, list[str], Path]]:
    py = sys.executable
    s = []
    if shutil.which("ruff") or _hat_modul("ruff"):
        s.append(("ruff", [py, "-m", "ruff", "check", "--select", "F,E9", "--line-length", "120", "-q",
                           "--per-file-ignores", "tests/*:F811",           # Fixtures aus anderen Testdateien
                           *[p for p in PYTHON_PFADE if (repo / p).exists()]], repo))
    if schnell:
        return s
    s.append(("pytest", [py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"], repo))
    if (repo / "services/modeler/tests").exists():
        s.append(("modellierer", [py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"], repo / "services/modeler"))
    if (repo / "services/analyse/tests").exists():
        s.append(("analyse", [py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"], repo / "services/analyse"))
    if web and shutil.which("npm"):
        s.append(("web", ["npm", "run", "build"], repo / "apps/web"))
    return s


def _hat_modul(name: str) -> bool:
    try:
        __import__(name)
        return True
    except ImportError:
        return False


def _auswerten(name: str, code: int, log: str) -> dict:
    e = {"name": name, "ok": code == 0, "code": code}
    m = re.findall(r"^=*\s*(\d+ (?:passed|failed|error).*?) in [\d.]+s", log, flags=re.M)
    if m:
        e["summe"] = m[-1]
    fehl = [l.strip() for l in log.splitlines() if l.startswith(("FAILED", "ERROR")) or re.match(r"^\S+\.py:\d+:\d+: [A-Z]\d+", l)]
    if fehl:
        e["fehler"] = fehl[:8]
    if code != 0 and not fehl:
        e["ende"] = [l for l in log.strip().splitlines()[-6:]]
    return e


def _laufen(name: str, befehl: list[str], cwd: Path, ordner: Path, zeit: int) -> dict:
    beginn = time.monotonic()
    try:
        r = subprocess.run(befehl, cwd=cwd, capture_output=True, text=True, timeout=zeit)
        code, log = r.returncode, r.stdout + r.stderr
    except subprocess.TimeoutExpired as err:
        code, log = 124, f"Zeitlimit {zeit} s\n{(err.stdout or '')}"
    (ordner / f"{name}.log").write_text(log, encoding="utf-8")
    e = _auswerten(name, code, log)
    e["dauer_s"] = round(time.monotonic() - beginn, 1)
    return e


def pruefen(repo: Path, web: bool = False, schnell: bool = False, zeit: int = 1800) -> dict:
    ordner = repo / ".agenten" / "pruefen"
    ordner.mkdir(parents=True, exist_ok=True)
    liste = suiten(repo, web, schnell)
    with ThreadPoolExecutor(max_workers=max(1, len(liste))) as pool:
        ergebnisse = list(pool.map(lambda s: _laufen(*s, ordner, zeit), liste))
    d = doku.pruefen(repo)
    ergebnisse.append({"name": "doku", "ok": not d["fehler"], "summe": f"{d['dateien']} Dateien, {len(d['fehler'])} Fehler",
                       **({"fehler": d["fehler"][:8]} if d["fehler"] else {})})
    urteil = {"ok": all(e["ok"] for e in ergebnisse), "suiten": ergebnisse, "protokolle": str(ordner)}
    (ordner / "urteil.json").write_text(json.dumps(urteil, ensure_ascii=False, indent=1), encoding="utf-8")
    return urteil


def kurz(urteil: dict) -> str:
    z = [f"{'OK' if urteil['ok'] else 'FEHLER'} · Protokolle: {urteil['protokolle']}"]
    for e in urteil["suiten"]:
        z.append(f"  {'✓' if e['ok'] else '✗'} {e['name']:<12} {e.get('summe', '')} {('(' + str(e['dauer_s']) + ' s)') if 'dauer_s' in e else ''}".rstrip())
        for f in (e.get("fehler") or e.get("ende") or [])[:5]:
            z.append(f"      {f[:150]}")
    return "\n".join(z)
