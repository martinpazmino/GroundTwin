"""Kontext packen statt erkunden: nur Dateien, die git verfolgt (das Repository ist oeffentlich, AGPL), ohne die
Sperrliste (Grundwahrheit, PDFs, Bilder, Build, .env), jede Datei auf Geheimnisse geprueft, bis zu einem Budget.
Fremde Gutachten und Projektordner liegen nie im Repository und koennen so nicht hinausgehen (docs/24 §4.4)."""
from __future__ import annotations

import fnmatch
import re
import subprocess
from pathlib import Path

SPERRE = ["benchmark/groundtruth/*", "*.pdf", "*.png", "*.jpg", "*.jpeg", "*.gif", "*.ifc", "*.glb", "*.zip",
          "*.tif", "*.tiff", "apps/web/dist/*", ".env", ".env.*", "*.key", "*.pem", "constraints.txt",
          "services/geodaten/geodaten/laender.geojson", "package-lock.json"]
GEHEIM = [re.compile(r"AIza[0-9A-Za-z_\-]{30,}"), re.compile(r"gh[pousr]_[0-9A-Za-z]{30,}"),
          re.compile(r"sk-[A-Za-z0-9_\-]{20,}"), re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
          re.compile(r"(?i)(passwort|password|secret|token)\s*[=:]\s*['\"][^'\"\s]{8,}['\"]")]
MAX_DATEI = 200_000                      # Zeichen; groessere Dateien nur ausschnittweise ueber die Zeilen


def tokens(text: str) -> int:
    """Schaetzung fuer das Budget (Zeichen/4) - gemessen wird beim Anbieter."""
    return len(text) // 4


def verfolgt(repo: Path) -> set[str]:
    aus = subprocess.run(["git", "ls-files"], cwd=repo, capture_output=True, text=True, check=True).stdout
    return {z for z in aus.splitlines() if z}


def gesperrt(pfad: str) -> bool:
    return any(fnmatch.fnmatch(pfad, m) or fnmatch.fnmatch(Path(pfad).name, m) for m in SPERRE)


def geheim(text: str) -> bool:
    return any(m.search(text) for m in GEHEIM)


def dateien_aus_diff(diff: str) -> list[str]:
    return list(dict.fromkeys(m.group(1) for m in re.finditer(r"^\+\+\+ b/(\S+)", diff, flags=re.M)))


def dateien_aus_log(log: str, erlaubt: set[str]) -> list[str]:
    """Pfade im Protokoll (Traceback, pytest), soweit git sie kennt - in der Reihenfolge des Auftretens."""
    gefunden = []
    for m in re.finditer(r"([\w./\-]+\.(?:py|ts|mjs|js|json|md))(?::(\d+))?", log):
        p = m.group(1).lstrip("./")
        for kandidat in (p, *[e for e in erlaubt if e.endswith("/" + p)]):
            if kandidat in erlaubt and kandidat not in gefunden:
                gefunden.append(kandidat)
                break
    return gefunden


def log_kuerzen(log: str, zeilen: int = 160) -> str:
    """Fehlerrelevantes behalten: Zeilen mit Error/FAILED/assert/Traceback und ihre Umgebung, dazu das Ende."""
    z = log.splitlines()
    wichtig = set()
    for i, l in enumerate(z):
        if re.search(r"Error|FAILED|FEHL|assert|Traceback|Exception|^E\s", l):
            wichtig.update(range(max(0, i - 3), min(len(z), i + 4)))
    behalten = [z[i] for i in sorted(wichtig)][-zeilen:]
    ende = z[-40:]
    return "\n".join(behalten + ["…"] + ende) if behalten else "\n".join(z[-zeilen:])


def packen(repo: Path, dateien: list[str], budget_tokens: int, nummern: bool = False) -> tuple[str, dict]:
    """Dateien bis zum Budget; Rueckgabe (Text, Bericht {genommen, gesperrt, geheim, zu_gross, ausserhalb})."""
    erlaubt = verfolgt(repo)
    bericht = {"genommen": [], "gesperrt": [], "geheim": [], "zu_gross": [], "ausserhalb": []}
    teile, rest = [], budget_tokens
    for d in dateien:
        if d not in erlaubt:
            bericht["ausserhalb"].append(d)
            continue
        if gesperrt(d):
            bericht["gesperrt"].append(d)
            continue
        try:
            inhalt = (repo / d).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            bericht["gesperrt"].append(d)
            continue
        if geheim(inhalt):
            bericht["geheim"].append(d)
            continue
        if len(inhalt) > MAX_DATEI or tokens(inhalt) > rest:
            bericht["zu_gross"].append(d)
            continue
        if nummern:
            inhalt = "\n".join(f"{i + 1:5d}  {l}" for i, l in enumerate(inhalt.splitlines()))
        teile.append(f"=== {d} ===\n{inhalt}")
        rest -= tokens(inhalt)
        bericht["genommen"].append(d)
    return "\n\n".join(teile), bericht
