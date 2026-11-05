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


def _befehl(cwd: Path, befehl: str, zeit: int, env: dict | None = None) -> tuple[int, str]:
    teile = shlex.split(befehl)
    if teile and teile[0] in ("python", "python3"):
        import sys
        teile[0] = sys.executable
    try:
        import os
        r = subprocess.run(teile, cwd=cwd, capture_output=True, text=True, timeout=zeit,
                           env={**os.environ, **env} if env else None)
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
    # die letzten Aenderungen der genannten Dateien (ohne Tests): ein neuer Fehler steckt meist dort
    def quelle(x: str) -> bool:
        return x in erlaubt and not x.startswith("tests/") and x != "AGENTS.md" and not kontext.gesperrt(x)
    quellen = [x for x in dateien if quelle(x)]
    if not quellen:                                          # keine Quelldatei genannt: die der letzten drei Commits
        namen = _git(repo, "log", "-n", "3", "--name-only", "--format=", check=False).split()
        quellen = list(dict.fromkeys(x for x in namen if quelle(x)))[:8]
    teile = [_git(repo, "log", "-p", "-n", "3", "--format=commit %h %s", "--", x, check=False) for x in quellen]
    juengst = "".join(x for x in teile if not kontext.geheim(x))[:40_000]     # eine Datei mit Geheimnis faellt weg
    paket, _ = kontext.packen(repo, dateien, BUDGET["testanalyst"] - kontext.tokens(kurz) - kontext.tokens(juengst))
    d = a.rufen("testanalyst", modell, f"BEFEHL: {befehl or '(Protokoll)'}\n\nPROTOKOLL (gekuerzt):\n{kurz}\n\n"
                f"LETZTE AENDERUNGEN der genannten Quelldateien (git log -p -3):\n{juengst or '(keine)'}\n\nDATEIEN:\n{paket}")
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


# ------------------------------------------------------------------ Tests schreiben (mit Mutationsprobe)
MUTANTEN = {"<=": "<", ">=": ">", "==": "!=", "!=": "==", "<": "<=", ">": ">=", "+": "-", "-": "+",
            "and": "or", "or": "and", "True": "False", "False": "True"}


def _mutanten(text: str, hoechstens: int = 8) -> list[tuple[int, str, str, int]]:
    """Einfache Mutationen an Operatoren im Code (Kommentare und Texte bleiben), gleichmaessig ueber die Datei."""
    import io
    import tokenize
    anfang = [0]
    for z in text.splitlines(keepends=True):
        anfang.append(anfang[-1] + len(z))
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, SyntaxError):
        return []
    k = [t for t in toks if t.type in (tokenize.OP, tokenize.NAME) and t.string in MUTANTEN]
    if len(k) > hoechstens:
        k = [k[int(i * len(k) / hoechstens)] for i in range(hoechstens)]
    return [(anfang[t.start[0] - 1] + t.start[1], t.string, MUTANTEN[t.string], t.start[0]) for t in k]


def tests_schreiben(repo: Path, e: Einstellungen, anbieter, modul: str, ziel: str, vorhandene: list[str],
                    zeit: int = 600, runden: int = 1) -> dict:
    """Der Testautor schreibt eine neue Testdatei; sie zaehlt nur, wenn sie gruen ist und die Haelfte der Mutanten des
    Moduls toetet. Ueberlebende Mutanten gehen einmal an den Testautor zurueck (begrenzte Runde)."""
    a = Auftrag(repo, "tests", e, anbieter)
    paket, _ = kontext.packen(repo, [modul, *vorhandene], BUDGET["testanalyst"])
    modell = modelle.waehlen("testautor", e, [modul])
    d = a.rufen("testautor", modell, f"MODUL: {modul}\nZIELDATEI: {ziel}\n\nDATEIEN:\n{paket}")
    datei = str(d.get("datei") or ziel)
    if not datei.startswith("tests/") or ".." in datei or kontext.gesperrt(datei) or (repo / datei).exists():
        return a.bericht({"status": "abgelehnt", "abgelehnt": [f"{datei}: nur eine neue Datei unter tests/"]})
    baum = a.ordner / "baum"
    _git(repo, "worktree", "add", "-q", "-b", f"agenten/{a.id}", str(baum), "HEAD")
    befehl = f"python -m pytest -q -p no:cacheprovider {datei}"
    ohne_pyc = {"PYTHONDONTWRITEBYTECODE": "1"}        # sonst laeuft bei gleicher Groesse und Sekunde alter Bytecode
    quelle = baum / modul
    original = quelle.read_text(encoding="utf-8")
    zeilen = original.splitlines()

    def probe(inhalt: str) -> tuple[int, list[str], list[bool]]:
        (baum / datei).write_text(inhalt, encoding="utf-8")
        code, log = _befehl(baum, befehl, zeit, ohne_pyc)
        (a.ordner / "tests.log").write_text(log, encoding="utf-8")
        namen, tot = [], []
        if code == 0:
            for pos, alt, neu, zeile in _mutanten(original):
                quelle.write_text(original[:pos] + neu + original[pos + len(alt):], encoding="utf-8")
                c, _ = _befehl(baum, befehl, zeit, ohne_pyc)
                namen.append(f"Zeile {zeile}: {alt} → {neu}")
                tot.append(c != 0)
            quelle.write_text(original, encoding="utf-8")
        return code, namen, tot

    inhalt = str(d.get("inhalt", ""))
    code, namen, tot = probe(inhalt)
    runde = 0
    while runde < runden and code == 0 and not all(tot):
        runde += 1
        offen = [f"{n}   | {zeilen[int(n.split()[1].rstrip(':')) - 1].strip()}" for n, t in zip(namen, tot) if not t]
        a.nachricht("orchestrator", "testautor", "nachbessern", "\n".join(offen))
        try:
            d2 = a.rufen("testautor", modell, f"MODUL: {modul}\nZIELDATEI: {datei}\n\nDEINE TESTS (grün):\n{inhalt}\n\n"
                         "DIESE MUTATIONEN DES MODULS UEBERLEBEN (deine Tests bleiben grün, obwohl der Code falsch ist):\n"
                         + "\n".join(offen) + "\n\nErgänze Tests, die sie erkennen; gib die vollständige Datei zurück. "
                         "Eine Mutation ohne Wirkung auf das Verhalten nenne in der begruendung.\n\nDATEIEN:\n" + paket)
        except AnbieterFehler as err:                        # Kontingent erschoepft: das erste Ergebnis zaehlt
            a.nachricht("orchestrator", "testautor", "hinweis", f"Nachbesserung ausgefallen: {err}")
            break
        neu = str(d2.get("inhalt", ""))
        c2, n2, t2 = probe(neu)
        if c2 == 0 and sum(t2) >= sum(tot):                  # nur uebernehmen, was nicht schlechter ist
            inhalt, code, namen, tot, d = neu, c2, n2, t2, d2
        else:
            probe(inhalt)
    (baum / datei).write_text(inhalt, encoding="utf-8")
    _git(baum, "add", "-N", datei)
    (a.ordner / "patch.diff").write_text(_git(baum, "diff"), encoding="utf-8")
    brauchbar = code == 0 and any(tot) and sum(tot) * 2 >= len(tot)
    n = len(re.findall(r"^def test_", inhalt, flags=re.M))
    if not brauchbar:
        verwerfen(repo, a.id, still=True)
    return a.bericht({"status": "wartet_auf_freigabe" if brauchbar else "verworfen", "datei": datei, "tests": n,
                      "gruen": code == 0, "mutanten": len(tot), "getoetet": sum(tot), "runden": runde,
                      "ueberlebt": [m for m, t in zip(namen, tot) if not t],
                      "begruendung": d.get("begruendung", ""),
                      "patch": str(a.ordner / "patch.diff") if brauchbar else "",
                      "stat": [f"{datei} neu, {n} Tests"]})


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
def uebergabe(repo: Path, ziel: str, dateien: list[str], tests: list[str], titel: str = "") -> tuple[Path, str]:
    """Auftrag fuer Antigravity in agenten/auftraege/ (eingecheckt, damit er auf den PC des Nutzers kommt). Der Nutzer
    startet ihn selbst - nie Claude Code (Abschnitt 6 der Antigravity-Bedingungen, docs/24 §4.2)."""
    kennung = f"agy-{datetime.now():%Y%m%d-%H%M%S}"
    ordner = repo / "agenten" / "auftraege"
    ordner.mkdir(parents=True, exist_ok=True)
    datei = ordner / f"{kennung}.md"
    rel = datei.relative_to(repo).as_posix()
    basis = _git(repo, "rev-parse", "--abbrev-ref", "HEAD", check=False).strip() or "main"
    datei.write_text(f"""# Auftrag {kennung}{(': ' + titel) if titel else ''} (GroundTwin)

Lies zuerst AGENTS.md im Repository und halte dich an alle Punkte. Grundlage ist der Zweig `{basis}`.

## Ziel

{ziel}

## Rahmen

- **Dateien, die du ändern darfst:** {', '.join(dateien) or '(nur, was das Ziel verlangt; nichts Geschütztes)'}
- **Danach grün:** {', '.join(tests) or 'python -m agenten pruefen'}
- Arbeite nur auf dem Zweig `agy/{kennung}`, committe dort mit klaren Nachrichten und pushe ihn.
- Ändere keinen Test, um ihn grün zu machen. Was unklar ist, schreib in die Commit-Nachricht statt zu raten.
""", encoding="utf-8")
    befehl = (f"git fetch origin {basis}\n"
              f"git worktree add --no-track ..\\gt-{kennung} -b agy/{kennung} origin/{basis}\n"
              f"cd ..\\gt-{kennung}\n"
              f"agy      (dann eintippen: Lies {rel} und fuehre den Auftrag aus.)\n"
              f"   oder ohne Dialog, in PowerShell:\n"
              f"   agy -p (Get-Content -Raw {rel.replace('/', chr(92))}) --output-format json > ..\\{kennung}.json\n"
              f"git push -u origin agy/{kennung}\n"
              f"python -m agenten agy-einlesen {kennung} ..\\{kennung}.json   (nur nach agy -p)")
    return datei, befehl


def agy_einlesen(repo: Path, kennung: str, datei: Path) -> dict:
    """Die JSON-Ausgabe von agy -p in die Messwerte (Tokens, wie agy sie meldet)."""
    d = json.loads(Path(datei).read_text(encoding="utf-8"))
    u = d.get("usage") or {}
    a = Antwort(text="", modell=d.get("model") or "antigravity", tokens_ein=u.get("input_tokens", 0),
                tokens_aus=u.get("output_tokens", 0), tokens_denken=u.get("thinking_tokens", 0),
                tokens_cache=u.get("cache_read_tokens", 0))
    return protokoll.schreiben(repo / ".agenten", kennung, "umsetzer", "antigravity", a, kosten=False)
