"""Doku ohne Modell pruefen: relative Links und Anker, und die Zahlen in CLAUDE.md gegen ihre Quelle
(letzte Entscheidung in docs/11, letzte P-Lektion in docs/16). Die Zahl der End-to-End-Pruefungen nicht:
check_app.mjs hat Zweige (Netz, Passwort), statisch gezaehlt waere sie falsch."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

from .kontext import verfolgt


def _anker(text: str) -> set[str]:
    out, gesehen, code = set(), {}, False
    for z in text.splitlines():
        if z.startswith("```"):
            code = not code
        if code:
            continue
        m = re.match(r"^#{1,6}\s+(.*)$", z)
        if m:
            s = re.sub(r"[`*]", "", m.group(1)).strip().lower()
            s = re.sub(r"[^\w\- ]", "", s).replace(" ", "-")
            n = gesehen.get(s, 0)
            out.add(s if n == 0 else f"{s}-{n}")
            gesehen[s] = n + 1
    return out


def links(repo: Path, dateien: list[str]) -> list[str]:
    fehler, cache = [], {}
    for name in dateien:
        p = repo / name
        text = re.sub(r"```.*?```", "", p.read_text(encoding="utf-8"), flags=re.S)
        for m in re.finditer(r"\]\(([^)\s]+)\)", text):
            ziel = m.group(1)
            if ziel.startswith(("http://", "https://", "mailto:")):
                continue
            pfad, _, a = ziel.partition("#")
            datei = (p.parent / unquote(pfad)).resolve() if pfad else p.resolve()
            if not datei.exists():
                fehler.append(f"{name}: Link fehlt {ziel}")
                continue
            if a and datei.suffix == ".md":
                if datei not in cache:
                    cache[datei] = _anker(datei.read_text(encoding="utf-8"))
                if unquote(a) not in cache[datei]:
                    fehler.append(f"{name}: Anker fehlt {ziel}")
    return fehler


def zahlen(repo: Path) -> list[str]:
    fehler = []
    claude = (repo / "CLAUDE.md").read_text(encoding="utf-8") if (repo / "CLAUDE.md").exists() else ""
    def letzte(datei: str, muster: str) -> int:
        p = repo / datei
        return max((int(x) for x in re.findall(muster, p.read_text(encoding="utf-8"), flags=re.M)), default=0) if p.exists() else 0
    d = letzte("docs/11_decisions.md", r"^\| D(\d+) \|")
    m = re.search(r"decisions D1–D(\d+)", claude)
    if d and m and int(m.group(1)) != d:
        fehler.append(f"CLAUDE.md nennt D1–D{m.group(1)}, docs/11 endet bei D{d}")
    pl = letzte("docs/16_lessons_learned.md", r"^\| P(\d+) \|")
    m = re.search(r"process P1–P(\d+)", claude)
    if pl and m and int(m.group(1)) != pl:
        fehler.append(f"CLAUDE.md nennt P1–P{m.group(1)}, docs/16 endet bei P{pl}")
    return fehler


def pruefen(repo: Path) -> dict:
    md = sorted(d for d in verfolgt(repo) if d.endswith(".md") and not d.startswith(("apps/web/node_modules", "benchmark/groundtruth")))
    return {"dateien": len(md), "fehler": links(repo, md) + zahlen(repo)}
