"""python -m agenten <befehl> - siehe docs/24. Jede Ausgabe ist knapp: Claude liest sie statt der Protokolle."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from . import ablauf, doku, protokoll, pruefen, stand
from .anbieter import AnbieterFehler, Attrappe, Gemini
from .einstellungen import laden


def _repo() -> Path:
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if r.returncode:
        sys.exit("nicht in einem git-Repository")
    return Path(r.stdout.strip())


def _anbieter(e):
    if os.environ.get("AGENTEN_ATTRAPPE"):                 # Pruefungen und Vorfuehrung ohne Netz
        return Attrappe(json.loads(Path(os.environ["AGENTEN_ATTRAPPE"]).read_text(encoding="utf-8")))
    if not e.aktiv:
        sys.exit("AI_ORCHESTRATION_ENABLED ist aus")
    return Gemini(e.api_schluessel, e.zeit_s, e.versuche)


def _bericht_kurz(b: dict) -> str:
    z = [f"{b['auftrag']}: {b.get('status')} · {b.get('aufrufe', 0)} Aufrufe · Tokens {b['tokens']['tokens_ein']}/"
         f"{b['tokens']['tokens_aus']} · ~{b.get('kosten_usd_geschaetzt', 0)} $ (Listenpreis) · {', '.join(b.get('modelle', []))}"]
    if b["art"] == "review":
        z.append(f"Urteil: {b.get('urteil')}")
        for f in b.get("befunde", [])[:8]:
            z.append(f"  [{f.get('schwere')}] {f.get('datei')}:{f.get('zeile')} {f.get('befund', '')[:140]}")
    if b["art"] == "diagnose":
        z.append(f"Ursache ({b.get('vertrauen')}): {str(b.get('ursache'))[:300]}")
        z.append(f"Test danach: {b.get('test_nachher')} · Prüfer: {(b.get('pruefer') or {}).get('urteil')}")
        for f in (b.get("pruefer") or {}).get("befunde", [])[:5]:
            z.append(f"  [{f.get('schwere')}] {f.get('datei')}:{f.get('zeile')} {f.get('befund', '')[:140]}")
        for g in b.get("abgelehnt", []):
            z.append(f"  abgelehnt: {g}")
        if b.get("patch"):
            z.append(f"Patch: {b['patch']} {' '.join(b.get('stat', []))}")
            z.append(f"Freigabe: python -m agenten uebernehmen {b['auftrag']}  ·  verwerfen: python -m agenten verwerfen {b['auftrag']}")
    z.append(f"Bericht: .agenten/{b['auftrag']}/bericht.json")
    return "\n".join(z)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m agenten", description="Agententeam von GroundTwin (docs/24)")
    sub = ap.add_subparsers(dest="kommando", required=True)
    p = sub.add_parser("pruefen", help="alle Pruefungen, ein Urteil")
    p.add_argument("--web", action="store_true")
    p.add_argument("--schnell", action="store_true", help="nur ruff und Doku")
    sub.add_parser("doku", help="Links, Anker, Zahlen der Doku")
    sub.add_parser("stand", help="Stand in wenigen Zeilen")
    sub.add_parser("verbindung", help="ein kleiner Aufruf an Gemini (Schluessel, Modell, Tokens)")
    r = sub.add_parser("review", help="Diff pruefen lassen")
    r.add_argument("--basis", default="HEAD")
    r.add_argument("--stark", action="store_true", help="starkes Modell (nur mit AI_ALLOW_PAID_API)")
    d = sub.add_parser("diagnose", help="Fehler analysieren, Patch im Worktree")
    d.add_argument("--befehl", default="")
    d.add_argument("--log", default="")
    d.add_argument("--runden", type=int, default=2)
    d.add_argument("--stark", action="store_true")
    te = sub.add_parser("tests", help="Tests fuer ein Modul schreiben lassen (mit Mutationsprobe)")
    te.add_argument("--modul", required=True)
    te.add_argument("--ziel", required=True, help="neue Testdatei unter tests/")
    te.add_argument("--vorhandene", nargs="*", default=[], help="Tests als Vorbild (Importweg, Stil)")
    for n in ("uebernehmen", "verwerfen"):
        x = sub.add_parser(n)
        x.add_argument("id")
    u = sub.add_parser("uebergabe", help="Auftrag fuer Antigravity (du startest ihn)")
    u.add_argument("--ziel", default="")
    u.add_argument("--dateien", nargs="*", default=[])
    u.add_argument("--tests", nargs="*", default=[])
    u.add_argument("--titel", default="")
    u.add_argument("--ziel-datei", default="", help="Ziel aus einer Datei (laengere Beschreibung)")
    g = sub.add_parser("agy-einlesen", help="Tokens aus der JSON-Ausgabe von agy -p")
    g.add_argument("id")
    g.add_argument("datei")
    k = sub.add_parser("kosten", help="Tokens der Agenten und von Claude")
    k.add_argument("--seit", default="", help="ISO-Zeit (UTC), z. B. 2026-11-05T14:00")
    a = ap.parse_args(argv)
    repo = _repo()
    e = laden(repo)
    try:
        if a.kommando == "pruefen":
            u_ = pruefen.pruefen(repo, a.web, a.schnell)
            print(pruefen.kurz(u_))
            return 0 if u_["ok"] else 1
        if a.kommando == "doku":
            d_ = doku.pruefen(repo)
            print(f"{d_['dateien']} Dateien, {len(d_['fehler'])} Fehler")
            print("\n".join(d_["fehler"][:20]))
            return 0 if not d_["fehler"] else 1
        if a.kommando == "stand":
            print(stand.stand(repo))
            return 0
        if a.kommando == "verbindung":
            anb = _anbieter(e)
            from . import modelle
            m = modelle.waehlen("zusammenfasser", e)
            antwort = anb.antworten(m, "Antworte nur mit JSON.", 'Gib {"ok": true} zurück.')
            protokoll.schreiben(repo / ".agenten", "verbindung", "test", anb.name, antwort)
            print(f"ok · Modell {antwort.modell} · Tokens {antwort.tokens_ein}/{antwort.tokens_aus} · {antwort.dauer_ms} ms")
            return 0
        if a.kommando == "review":
            print(_bericht_kurz(ablauf.review(repo, e, _anbieter(e), a.basis, a.stark)))
            return 0
        if a.kommando == "diagnose":
            log = Path(a.log).read_text(encoding="utf-8") if a.log else ""
            print(_bericht_kurz(ablauf.diagnose(repo, e, _anbieter(e), a.befehl, log, a.runden, a.stark)))
            return 0
        if a.kommando == "tests":
            b = ablauf.tests_schreiben(repo, e, _anbieter(e), a.modul, a.ziel, a.vorhandene)
            print(f"{b['auftrag']}: {b['status']} · {b.get('tests')} Tests, grün: {b.get('gruen')} · Mutanten getötet "
                  f"{b.get('getoetet')}/{b.get('mutanten')} · Tokens {b['tokens']['tokens_ein']}/{b['tokens']['tokens_aus']}"
                  f" · ~{b['kosten_usd_geschaetzt']} $ · {', '.join(b['modelle'])}")
            for m in b.get("ueberlebt", [])[:8]:
                print(f"  überlebt: {m}")
            for m in b.get("abgelehnt", []):
                print(f"  abgelehnt: {m}")
            if b.get("patch"):
                print(f"Patch: {b['patch']}\nFreigabe nach dem Lesen: python -m agenten uebernehmen {b['auftrag']}")
            return 0 if b["status"] == "wartet_auf_freigabe" else 1
        if a.kommando == "uebernehmen":
            b = ablauf.uebernehmen(repo, a.id)
            print(f"{a.id}: übernommen in den Arbeitsstand (noch nicht committet)")
            return 0 if b else 1
        if a.kommando == "verwerfen":
            ablauf.verwerfen(repo, a.id)
            print(f"{a.id}: verworfen")
            return 0
        if a.kommando == "uebergabe":
            ziel = Path(a.ziel_datei).read_text(encoding="utf-8") if a.ziel_datei else a.ziel
            datei, befehl = ablauf.uebergabe(repo, ziel, a.dateien, a.tests, a.titel)
            print(f"Auftrag: {datei.relative_to(repo)}\nAuf deinem PC, im Repository:\n{befehl}")
            return 0
        if a.kommando == "agy-einlesen":
            z = ablauf.agy_einlesen(repo, a.id, Path(a.datei))
            print(f"{a.id}: {z.get('tokens_ein')}/{z.get('tokens_aus')} Tokens von Antigravity eingelesen")
            return 0
        if a.kommando == "kosten":
            s = protokoll.summe(repo / ".agenten", a.seit)
            c = protokoll.claude_verbrauch(a.seit)
            print(f"Agenten: {s['aufrufe']} Aufrufe ({s['fehler']} Fehler), Tokens {s['tokens_ein']}/{s['tokens_aus']}"
                  f" (+{s['tokens_denken']} Denken), ~{s['kosten_usd']} $ Listenpreis, je Rolle {s['je_rolle']}")
            print(f"Claude: {c['antworten']} Antworten, Ausgabe {c['ausgabe']:,}, Cache gelesen {c['cache_lesen']:,}, "
                  f"geschrieben {c['cache_schreiben']:,}, Eingabe {c['eingabe']:,} (gemessen aus dem Transkript)")
            return 0
    except (AnbieterFehler, PermissionError, ValueError, RuntimeError) as err:
        print(f"Fehler: {err}", file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
