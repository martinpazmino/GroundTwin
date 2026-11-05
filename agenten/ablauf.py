"""Ablaeufe mit festen Runden (docs/24 §5.5): review, diagnose, uebergabe an Antigravity, uebernehmen.

Agenten sprechen ueber das Nachrichtenprotokoll des Auftrags (.agenten/<id>/nachrichten.jsonl), nicht frei; Claude
liest nur bericht.json. Aenderungen eines Agenten werden nur in einem git-Worktree angewandt; geschuetzte Dateien und
abgeschwaechte Tests lehnt der Orchestrator ab, nicht der Agent."""
from __future__ import annotations

import json
import re
import shlex
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from . import kontext, modelle, protokoll
from .anbieter import AnbieterFehler, Antwort
from .einstellungen import Einstellungen

GESCHUETZT = ("services/extractor/prototyp_v4.py", "benchmark/", "constraints.txt", ".github/workflows/", "CLAUDE.md",
              "LICENSE", "agenten/", "AGENTS.md")
BUDGET = {"pruefer": 60_000, "testanalyst": 80_000}
SCHWERE = {"hoch": 3, "mittel": 2, "niedrig": 1}


def _git(repo: Path, *args: str, check: bool = True) -> str:
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()[:300]}")
    return r.stdout


def _rolle(name: str, repo: Path) -> str:
    text = (Path(__file__).parent / "rollen" / f"{name}.md").read_text(encoding="utf-8")
    text = text.split("---", 2)[2] if text.startswith("---") else text
    spez = (repo / "AGENTS.md").read_text(encoding="utf-8") if (repo / "AGENTS.md").exists() else ""
    return spez + "\n\n" + text.strip()


class Auftrag:
    def __init__(self, repo: Path, art: str, e: Einstellungen, anbieter, kennung: str = ""):
        self.repo, self.art, self.e, self.anbieter = repo, art, e, anbieter
        self.id = kennung or f"{art}-{datetime.now():%Y%m%d-%H%M%S-%f}"[:-3]
        self.ordner = repo / ".agenten" / self.id
        self.ordner.mkdir(parents=True, exist_ok=True)
        self.aufrufe: list[dict] = []

    def nachricht(self, von: str, an: str, typ: str, text: str, belege=None, vertrauen=None):
        z = {"zeit": protokoll.jetzt(), "von": von, "an": an, "typ": typ, "text": text[:4000],
             "belege": belege or [], "vertrauen": vertrauen}
        with open(self.ordner / "nachrichten.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(z, ensure_ascii=False) + "\n")

    def rufen(self, rolle: str, modell: str, text: str) -> dict:
        while True:
            try:
                a: Antwort = self.anbieter.antworten(modell, _rolle(rolle, self.repo), text)
                daten = a.json()
                break
            except (AnbieterFehler, ValueError) as err:
                protokoll.schreiben(self.repo / ".agenten", self.id, rolle, self.anbieter.name, erfolg=False,
                                    fehler=f"{modell}: {err}")
                ersatz = modelle.ausweich(modell, self.e) if getattr(err, "code", 0) in (429, 503) else None
                if not ersatz:
                    raise AnbieterFehler(f"{rolle}: {err}") from None
                self.nachricht("orchestrator", rolle, "hinweis", f"{modell} überlastet, weiter mit {ersatz}")
                modell = ersatz
        z = protokoll.schreiben(self.repo / ".agenten", self.id, rolle, self.anbieter.name, a,
                                kosten=self.e.kosten_protokollieren)
        self.aufrufe.append(z)
        return daten

    def bericht(self, inhalt: dict) -> dict:
        b = {"auftrag": self.id, "art": self.art, **inhalt,
             "aufrufe": len(self.aufrufe),
             "tokens": {k: sum(a.get(k, 0) for a in self.aufrufe) for k in ("tokens_ein", "tokens_aus", "tokens_denken")},
             "kosten_usd_geschaetzt": round(sum(a.get("kosten_usd", 0.0) for a in self.aufrufe), 4),
             "modelle": sorted({a.get("modell", "") for a in self.aufrufe})}
        (self.ordner / "bericht.json").write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
        return b


# ------------------------------------------------------------------ review
def _diff(repo: Path, basis: str) -> str:
    d = _git(repo, "diff", basis)
    if not d.strip() and basis == "HEAD":
        d = _git(repo, "diff", "HEAD~1", check=False)
    return d


def review(repo: Path, e: Einstellungen, anbieter, basis: str = "HEAD", stark: bool = False) -> dict:
    a = Auftrag(repo, "review", e, anbieter)
    diff = _diff(repo, basis)
    if not diff.strip():
        return a.bericht({"status": "nichts_zu_pruefen", "urteil": "ok", "befunde": []})
    dateien = kontext.dateien_aus_diff(diff)
    # Gruppen nach Bereich, parallel geprueft, wenn der Diff gross ist
    gruppen: dict[str, list[str]] = {}
    for d in dateien:
        gruppen.setdefault(d.split("/")[0], []).append(d)
    if kontext.tokens(diff) < BUDGET["pruefer"] // 2:
        gruppen = {"alle": dateien}

    def pruefen_gruppe(liste: list[str]) -> dict:
        teil = _git(repo, "diff", basis, "--", *liste) if len(gruppen) > 1 else diff
        paket, info = kontext.packen(repo, liste, BUDGET["pruefer"] - kontext.tokens(teil), nummern=True)
        modell = modelle.waehlen("pruefer", e, liste, stark)
        d = a.rufen("pruefer", modell, f"DIFF:\n{teil}\n\nDATEIEN:\n{paket}\n\nNicht mitgeschickt: {json.dumps(info)}")
        a.nachricht("pruefer", "claude", "urteil", d.get("zusammenfassung", ""), [f"{b.get('datei')}:{b.get('zeile')}"
                    for b in d.get("befunde", [])])
        return d

    with ThreadPoolExecutor(max_workers=e.parallel) as pool:
        teile = list(pool.map(pruefen_gruppe, gruppen.values()))
    befunde = sorted((b for t in teile for b in t.get("befunde", [])), key=lambda b: -SCHWERE.get(b.get("schwere"), 0))
    urteil = max((t.get("urteil", "ok") for t in teile), key=lambda u: {"ok": 0, "nachbessern": 1, "ablehnen": 2}.get(u, 1))
    return a.bericht({"status": "fertig", "basis": basis, "dateien": dateien, "urteil": urteil, "befunde": befunde,
                      "zusammenfassung": [t.get("zusammenfassung", "") for t in teile]})


# ------------------------------------------------------------------ diagnose
def _ablehnen(aenderungen: list[dict]) -> list[str]:
    gruende = []
    for x in aenderungen:
        d = str(x.get("datei", ""))
        if d.startswith(GESCHUETZT) or d in GESCHUETZT:
            gruende.append(f"{d}: geschützt")
        if "/test" in "/" + d or d.startswith("tests/"):
            alt, neu = str(x.get("alt", "")), str(x.get("neu", ""))
            if len(re.findall(r"def test_", alt)) > len(re.findall(r"def test_", neu)):
                gruende.append(f"{d}: entfernt einen Test")
            if re.search(r"pytest\.skip|mark\.skip|xfail|skipif", neu) and not re.search(r"pytest\.skip|mark\.skip|xfail|skipif", alt):
                gruende.append(f"{d}: überspringt einen Test")
            if re.search(r"\bassert\b", alt) and not re.search(r"\bassert\b", neu):
                gruende.append(f"{d}: nimmt eine Prüfung heraus")
    return gruende


def _anwenden(baum: Path, aenderungen: list[dict]) -> list[str]:
    fehler = []
    for x in aenderungen:
        p = baum / x["datei"]
        if not p.exists():
            if x.get("alt"):
                fehler.append(f"{x['datei']}: Datei fehlt")
                continue
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(x.get("neu", ""), encoding="utf-8")
            continue
        text = p.read_text(encoding="utf-8")
        n = text.count(x.get("alt", ""))
        if not x.get("alt") or n != 1:
            fehler.append(f"{x['datei']}: Text kommt {n}-mal vor (verlangt: genau einmal)")
            continue
        p.write_text(text.replace(x["alt"], x.get("neu", ""), 1), encoding="utf-8")
    return fehler


def _befehl(cwd: Path, befehl: str, zeit: int) -> tuple[int, str]:
    teile = shlex.split(befehl)
    if teile and teile[0] in ("python", "python3"):
        import sys
        teile[0] = sys.executable
    try:
        r = subprocess.run(teile, cwd=cwd, capture_output=True, text=True, timeout=zeit)
        return r.returncode, r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return 124, f"Zeitlimit {zeit} s"
    except FileNotFoundError as err:
        return 127, str(err)


def diagnose(repo: Path, e: Einstellungen, anbieter, befehl: str = "", log: str = "", runden: int = 2,
             stark: bool = False, zeit: int = 900) -> dict:
    a = Auftrag(repo, "diagnose", e, anbieter)
    if befehl:
        code, log = _befehl(repo, befehl, zeit)
        (a.ordner / "vorher.log").write_text(log, encoding="utf-8")
        if code == 0:
            return a.bericht({"status": "kein_fehler", "befehl": befehl})
    if not log.strip():
        raise ValueError("diagnose braucht --befehl oder --log")
    kurz = kontext.log_kuerzen(log)
    erlaubt = kontext.verfolgt(repo)
    dateien = kontext.dateien_aus_log(kurz, erlaubt)[:8]
    modell = modelle.waehlen("testanalyst", e, dateien, stark)
    paket, _ = kontext.packen(repo, dateien, BUDGET["testanalyst"] - kontext.tokens(kurz))
    d = a.rufen("testanalyst", modell, f"BEFEHL: {befehl or '(Protokoll)'}\n\nPROTOKOLL (gekuerzt):\n{kurz}\n\nDATEIEN:\n{paket}")
    if d.get("mehr_dateien") and not d.get("aenderungen"):                    # einmal mehr Kontext, dann entscheiden
        mehr, info = kontext.packen(repo, [str(x) for x in d["mehr_dateien"][:5]], BUDGET["testanalyst"] // 2)
        a.nachricht("orchestrator", "testanalyst", "antwort", f"geliefert: {info['genommen']}, nicht: {info}")
        d = a.rufen("testanalyst", modell, f"PROTOKOLL (gekuerzt):\n{kurz}\n\nDATEIEN:\n{paket}\n\nNACHGELIEFERT:\n{mehr}")
    baum = a.ordner / "baum"
    zweig = f"agenten/{a.id}"
    _git(repo, "worktree", "add", "-q", "-b", zweig, str(baum), "HEAD")
    pruefer: dict = {}
    nachher_code, nachher_log = None, ""
    abgelehnt: list[str] = []
    for runde in range(1, runden + 1):
        a.nachricht("testanalyst", "pruefer", "patch", d.get("ursache", ""), d.get("belege"), d.get("vertrauen"))
        aenderungen = d.get("aenderungen") or []
        abgelehnt = _ablehnen(aenderungen)
        if abgelehnt:
            break
        fehler = _anwenden(baum, aenderungen)
        if fehler:
            abgelehnt = fehler
            break
        if befehl:
            nachher_code, nachher_log = _befehl(baum, befehl, zeit)
            (a.ordner / f"nachher_{runde}.log").write_text(nachher_log, encoding="utf-8")
        diff = _git(baum, "diff")
        (a.ordner / "patch.diff").write_text(diff, encoding="utf-8")
        ergebnis = ("Befehl danach: " + ("grün" if nachher_code == 0 else f"rot (Code {nachher_code})\n"
                                          + kontext.log_kuerzen(nachher_log, 60))) if befehl else "nicht ausgeführt"
        geaendert = kontext.dateien_aus_diff(diff)
        pruefer = a.rufen("pruefer", modelle.waehlen("pruefer", e, geaendert, stark),
                          f"URSACHE laut Testanalyst: {d.get('ursache')}\n\nDIFF:\n{diff}\n\nTEST: {ergebnis}")
        a.nachricht("pruefer", "testanalyst", "urteil", pruefer.get("zusammenfassung", ""),
                    [f"{b.get('datei')}:{b.get('zeile')}" for b in pruefer.get("befunde", [])])
        if pruefer.get("urteil") == "ok" and (not befehl or nachher_code == 0):
            break
        if runde < runden:                                                  # eine Nachbesserung mit den Befunden
            d = a.rufen("testanalyst", modell, f"Deine Aenderung ist angewandt (Diff unten). Der Pruefer sagt: "
                        f"{json.dumps(pruefer, ensure_ascii=False)}\nTEST: {ergebnis}\n\nDIFF:\n{diff}\n\n"
                        f"Gib nur die ZUSAETZLICHEN Aenderungen relativ zum geaenderten Stand.\n\nDATEIEN:\n{paket}")
    gruen = bool(befehl) and nachher_code == 0
    status = ("abgelehnt" if abgelehnt else "wartet_auf_freigabe" if (a.ordner / "patch.diff").exists()
              and (a.ordner / "patch.diff").read_text().strip() else "ohne_patch")
    stat = _git(baum, "diff", "--stat") if status == "wartet_auf_freigabe" else ""
    if status != "wartet_auf_freigabe":
        verwerfen(repo, a.id, still=True)
    return a.bericht({"status": status, "befehl": befehl, "ursache": d.get("ursache"), "vertrauen": d.get("vertrauen"),
                      "belege": d.get("belege", []), "offen": d.get("offen", []), "abgelehnt": abgelehnt,
                      "test_nachher": ("grün" if gruen else "rot") if befehl else "nicht ausgeführt",
                      "pruefer": {"urteil": pruefer.get("urteil"), "befunde": pruefer.get("befunde", [])},
                      "patch": str(a.ordner / "patch.diff") if status == "wartet_auf_freigabe" else "",
                      "stat": stat.strip().splitlines()[-1:] if stat else [], "zweig": zweig})


# ------------------------------------------------------------------ Freigabe durch Claude
def uebernehmen(repo: Path, kennung: str) -> dict:
    ordner = repo / ".agenten" / kennung
    b = json.loads((ordner / "bericht.json").read_text(encoding="utf-8"))
    if b.get("status") != "wartet_auf_freigabe":
        raise ValueError(f"{kennung}: nichts zu übernehmen (Status {b.get('status')})")
    patch = ordner / "patch.diff"
    dateien = kontext.dateien_aus_diff(patch.read_text(encoding="utf-8"))
    geschuetzt = [d for d in dateien if d.startswith(GESCHUETZT) or d in GESCHUETZT]
    if geschuetzt:
        raise PermissionError(f"geschützte Dateien im Patch: {geschuetzt}")
    _git(repo, "apply", "--check", str(patch))
    _git(repo, "apply", str(patch))
    verwerfen(repo, kennung, still=True)
    b["status"] = "uebernommen"
    b["uebernommen"] = protokoll.jetzt()
    (ordner / "bericht.json").write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
    return b


def verwerfen(repo: Path, kennung: str, still: bool = False) -> None:
    baum = repo / ".agenten" / kennung / "baum"
    if baum.exists():
        _git(repo, "worktree", "remove", "--force", str(baum), check=False)
        shutil.rmtree(baum, ignore_errors=True)
    _git(repo, "worktree", "prune", check=False)
    _git(repo, "branch", "-D", f"agenten/{kennung}", check=False)
    b = repo / ".agenten" / kennung / "bericht.json"
    if b.exists() and not still:
        d = json.loads(b.read_text(encoding="utf-8"))
        d["status"] = "verworfen"
        b.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


# ------------------------------------------------------------------ Uebergabe an Antigravity (der Nutzer startet sie)
def uebergabe(repo: Path, ziel: str, dateien: list[str], tests: list[str]) -> tuple[Path, str]:
    kennung = f"agy-{datetime.now():%Y%m%d-%H%M%S}"
    ordner = repo / ".agenten" / "auftraege"
    ordner.mkdir(parents=True, exist_ok=True)
    datei = ordner / f"{kennung}.md"
    datei.write_text(f"""# Auftrag {kennung} (GroundTwin)

Lies zuerst AGENTS.md im Repository und halte dich an alle Punkte.

**Ziel:** {ziel}

**Dateien, die du ändern darfst:** {', '.join(dateien) or '(nur, was das Ziel verlangt; nichts Geschütztes)'}

**Tests, die danach grün sein müssen:** {', '.join(tests) or 'python -m pytest tests -q'}

**Arbeitsweise:** arbeite nur auf dem Zweig `agy/{kennung}`, committe dort mit einer klaren Nachricht und pushe ihn.
Ändere keinen Test, um ihn grün zu machen. Wenn etwas unklar ist, schreib es in die Commit-Nachricht statt zu raten.
""", encoding="utf-8")
    befehl = (f"git worktree add ../gt-{kennung} -b agy/{kennung}\n"
              f"cd ../gt-{kennung}\n"
              f"agy -p \"$(cat {datei.relative_to(repo).as_posix()})\" --output-format json > ../{kennung}.json\n"
              f"git push -u origin agy/{kennung}")
    return datei, befehl


def agy_einlesen(repo: Path, kennung: str, datei: Path) -> dict:
    """Die JSON-Ausgabe von agy -p in die Messwerte (Tokens, wie agy sie meldet)."""
    d = json.loads(Path(datei).read_text(encoding="utf-8"))
    u = d.get("usage") or {}
    a = Antwort(text="", modell=d.get("model") or "antigravity", tokens_ein=u.get("input_tokens", 0),
                tokens_aus=u.get("output_tokens", 0), tokens_denken=u.get("thinking_tokens", 0),
                tokens_cache=u.get("cache_read_tokens", 0))
    return protokoll.schreiben(repo / ".agenten", kennung, "umsetzer", "antigravity", a, kosten=False)
