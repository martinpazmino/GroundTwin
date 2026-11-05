"""Stand in wenigen Zeilen fuer den Beginn einer Sitzung: Zweig, letzte Commits, offene Aenderungen, letztes Urteil,
offene Auftraege. Kurze Sitzungen mit kleinem Kontext sind der billigste Hebel (docs/24 §2)."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True).stdout.strip()


def stand(repo: Path) -> str:
    z = [f"Zweig {_git(repo, 'branch', '--show-current')} · {_git(repo, 'log', '-1', '--format=%h %s')[:100]}"]
    offen = [l for l in _git(repo, "status", "--porcelain").splitlines() if l]
    z.append(f"Offene Aenderungen: {len(offen)}" + (f" ({', '.join(l[3:] for l in offen[:5])}{' …' if len(offen) > 5 else ''})" if offen else ""))
    z.append("Letzte Commits: " + " | ".join(_git(repo, "log", "-4", "--format=%h %s").splitlines()[1:4])[:240])
    u = repo / ".agenten" / "pruefen" / "urteil.json"
    if u.exists():
        d = json.loads(u.read_text(encoding="utf-8"))
        z.append("Letzte Pruefung: " + ("OK" if d["ok"] else "FEHLER") + " · " +
                 ", ".join(f"{e['name']} {'✓' if e['ok'] else '✗'}" for e in d["suiten"]))
    auftraege = sorted((repo / ".agenten").glob("*/bericht.json")) if (repo / ".agenten").exists() else []
    offen_a = [json.loads(b.read_text(encoding="utf-8")) for b in auftraege]
    offen_a = [b for b in offen_a if b.get("status") == "wartet_auf_freigabe"]
    if offen_a:
        z.append("Wartet auf Freigabe: " + ", ".join(b["auftrag"] for b in offen_a[-5:]))
    return "\n".join(z)
