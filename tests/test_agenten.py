"""Agententeam (agenten/, docs/24): Einstellungen, Modellwahl, Kontext (Sperrliste, Geheimnisse), Gemini-Adapter,
Diagnose mit Worktree und Freigabe, Ablehnungen, Nachbesserung, Review, Uebergabe an Antigravity, Messwerte.

Ohne Netz und ohne Schluessel: eine Attrappe antwortet; gearbeitet wird in einem Wegwerf-Repository.
"""
from __future__ import annotations

import io
import json
import subprocess
import sys
import urllib.error
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from agenten import ablauf, kontext, modelle, protokoll  # noqa: E402
from agenten.anbieter import AnbieterFehler, Attrappe, Gemini  # noqa: E402
from agenten.einstellungen import laden  # noqa: E402

FEHLERHAFT = "def summe(a, b):\n    return a - b\n"
TEST = "from rechnen import summe\n\n\ndef test_summe():\n    assert summe(2, 3) == 5\n"


def _git(repo, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=repo, check=True,
                          capture_output=True, text=True).stdout


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    for k in list(__import__("os").environ):
        if k.startswith(("AI_", "GEMINI_")):
            monkeypatch.delenv(k)
    r = tmp_path / "repo"
    r.mkdir()
    (r / "rechnen.py").write_text(FEHLERHAFT, encoding="utf-8")
    (r / "tests").mkdir()
    (r / "tests" / "test_rechnen.py").write_text(TEST, encoding="utf-8")
    (r / "tests" / "conftest.py").write_text("import sys, pathlib\nsys.path.insert(0, str(pathlib.Path(__file__).parents[1]))\n")
    (r / "CLAUDE.md").write_text("geschuetzt\n")
    (r / "geheim.py").write_text('TOKEN = "AIzaSyD0123456789abcdefghijklmnopqrstu"\n')
    (r / "plan.pdf").write_bytes(b"%PDF-1.4")
    (r / "AGENTS.md").write_text("Regeln\n")
    _git(r, "init", "-q")
    _git(r, "add", "-A")
    _git(r, "commit", "-q", "-m", "start")
    return r


def befehl():
    return f"{sys.executable} -m pytest -q -p no:cacheprovider tests"


# ------------------------------------------------------------------ Einstellungen und Modelle
def test_einstellungen_aus_env_datei_und_sichere_vorgaben(repo, monkeypatch):
    e = laden(repo)
    assert not e.hat_schluessel and e.modell == "gemini-3.8-flash" and not e.bezahlt_erlaubt and e.freigabe_claude
    (repo / ".env").write_text("GEMINI_API_KEY=abc  # Kommentar\nGEMINI_MODEL=gemini-2.5-flash\nAI_MAX_PARALLEL_AGENTS=5\n"
                               "AI_ALLOW_PAID_API=false\n")
    monkeypatch.setenv("AI_MAX_RETRIES", "4")                       # Umgebung vor .env
    e = laden(repo)
    assert (e.api_schluessel, e.modell, e.parallel, e.versuche) == ("abc", "gemini-2.5-flash", 5, 4)


def test_modellwahl_risiko_ersatz_und_bezahlt(repo, monkeypatch):
    e = laden(repo)
    assert modelle.waehlen("pruefer", e, ["ui/x.py"]) == "gemini-3.8-flash"
    assert modelle.waehlen("pruefer", e, ["services/extractor/prototyp_v4.py"]) == "gemini-3.8-flash"   # ohne Bezahlen
    e.modell = "gemini-2.5-flash"
    assert modelle.waehlen("pruefer", e) == "gemini-3.8-flash"                                  # alte Generation → Ersatz
    e.bezahlt_erlaubt = True
    assert modelle.waehlen("pruefer", e, ["services/modeler/baugrundmodell/ifc.py"]) == "gemini-4-argon"
    e.bezahlt_erlaubt, e.modell = False, "gemini-4-argon"
    with pytest.raises(PermissionError, match="kostenpflichtig"):
        modelle.waehlen("pruefer", e)
    assert modelle.kosten_usd("gemini-4-argon", 1_000_000, 100_000) == 3.0


# ------------------------------------------------------------------ Kontext
def test_kontext_sperrliste_geheimnisse_budget_und_protokoll(repo):
    text, info = kontext.packen(repo, ["rechnen.py", "geheim.py", "plan.pdf", "nicht/da.py", "tests/test_rechnen.py"], 10_000)
    assert info["genommen"] == ["rechnen.py", "tests/test_rechnen.py"]
    assert info["geheim"] == ["geheim.py"] and info["gesperrt"] == ["plan.pdf"] and info["ausserhalb"] == ["nicht/da.py"]
    assert "AIza" not in text and "=== rechnen.py ===" in text
    _, klein = kontext.packen(repo, ["rechnen.py", "tests/test_rechnen.py"], 12)
    assert klein["zu_gross"]                                                      # Budget gehalten
    log = "E   assert -1 == 5\ntests/test_rechnen.py:5: AssertionError\n  File \"./rechnen.py\", line 2\n"
    assert kontext.dateien_aus_log(log, kontext.verfolgt(repo)) == ["tests/test_rechnen.py", "rechnen.py"]
    assert kontext.gesperrt("benchmark/groundtruth/x.json") and kontext.gesperrt("docs/a.png")


# ------------------------------------------------------------------ Gemini-Adapter (ohne Netz)
class _Antwort(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_gemini_anfrage_tokens_und_wiederholung(monkeypatch):
    monkeypatch.setattr("agenten.anbieter.time.sleep", lambda s: None)
    gesehen = []

    def oeffnen(anfrage, zeit):
        gesehen.append(anfrage)
        if len(gesehen) == 1:
            raise urllib.error.HTTPError(anfrage.full_url, 429, "zu viele", {}, io.BytesIO(b"{}"))
        roh = {"candidates": [{"content": {"parts": [{"text": "gedacht", "thought": True}, {"text": '{"ok": true}'}]}}],
               "usageMetadata": {"promptTokenCount": 120, "candidatesTokenCount": 7, "thoughtsTokenCount": 30},
               "modelVersion": "gemini-3.8-flash"}
        return _Antwort(json.dumps(roh).encode())
    g = Gemini("schluessel", versuche=2, oeffnen=oeffnen)
    a = g.antworten("gemini-3.8-flash", "System", "Frage")
    assert a.json() == {"ok": True} and (a.tokens_ein, a.tokens_aus, a.tokens_denken, a.versuche) == (120, 7, 30, 2)
    r = gesehen[-1]
    assert r.get_header("X-goog-api-key") == "schluessel" and "gemini-3.8-flash:generateContent" in r.full_url
    koerper = json.loads(r.data)
    assert koerper["generationConfig"]["responseMimeType"] == "application/json" and koerper["systemInstruction"]
    with pytest.raises(AnbieterFehler, match="GEMINI_API_KEY"):
        Gemini("")


# ------------------------------------------------------------------ Diagnose, Freigabe, Ablehnung
def _analyse(aenderungen, ursache="summe zieht ab statt zu addieren"):
    return {"ursache": ursache, "belege": ["rechnen.py:2"], "vertrauen": 0.9, "aenderungen": aenderungen,
            "mehr_dateien": [], "offen": []}


OK = {"urteil": "ok", "befunde": [], "zusammenfassung": "passt"}


def test_diagnose_patch_im_worktree_dann_freigabe(repo):
    e = laden(repo)
    anb = Attrappe([_analyse([{"datei": "rechnen.py", "alt": "return a - b", "neu": "return a + b"}]), OK])
    b = ablauf.diagnose(repo, e, anb, befehl())
    assert b["status"] == "wartet_auf_freigabe" and b["test_nachher"] == "grün" and b["pruefer"]["urteil"] == "ok"
    assert (repo / "rechnen.py").read_text() == FEHLERHAFT                         # Arbeitsstand unberuehrt
    assert "+    return a + b" in Path(b["patch"]).read_text()
    nachrichten = [json.loads(z) for z in (repo / ".agenten" / b["auftrag"] / "nachrichten.jsonl").read_text().splitlines()]
    assert [(n["von"], n["an"]) for n in nachrichten] == [("testanalyst", "pruefer"), ("pruefer", "testanalyst")]
    assert "AGENTS.md" not in anb.anfragen[0]["text"] and "Regeln" in anb.anfragen[0]["system"]   # Auftrag als System
    metriken = protokoll.summe(repo / ".agenten")
    assert metriken["aufrufe"] == 2 and metriken["je_rolle"] == {"testanalyst": 1, "pruefer": 1}
    ablauf.uebernehmen(repo, b["auftrag"])
    assert (repo / "rechnen.py").read_text() == "def summe(a, b):\n    return a + b\n"
    assert "agenten/" not in _git(repo, "branch")                                  # Zweig und Worktree weg
    with pytest.raises(ValueError, match="nichts zu übernehmen"):
        ablauf.uebernehmen(repo, b["auftrag"])


@pytest.mark.parametrize("aenderung, grund", [
    ({"datei": "CLAUDE.md", "alt": "geschuetzt", "neu": "frei"}, "geschützt"),
    ({"datei": "tests/test_rechnen.py", "alt": "    assert summe(2, 3) == 5\n", "neu": "    pass\n"}, "Prüfung"),
    ({"datei": "tests/test_rechnen.py", "alt": "def test_summe():", "neu": "@pytest.mark.skip\ndef test_summe():"}, "überspringt"),
    ({"datei": "rechnen.py", "alt": "gibt es nicht", "neu": "x"}, "genau einmal"),
])
def test_diagnose_lehnt_ab_was_die_regeln_bricht(repo, aenderung, grund):
    anb = Attrappe([_analyse([aenderung])])
    b = ablauf.diagnose(repo, laden(repo), anb, befehl())
    assert b["status"] == "abgelehnt" and any(grund in g for g in b["abgelehnt"]) and not b["patch"]
    assert "agenten/" not in _git(repo, "branch") and len(anb.anfragen) == 1     # kein Pruefer, aufgeraeumt


def test_diagnose_eine_nachbesserung_nach_dem_pruefer(repo):
    halb = _analyse([{"datei": "rechnen.py", "alt": "return a - b", "neu": "return a + b + 0"}])
    nachbessern = {"urteil": "nachbessern", "befunde": [{"schwere": "mittel", "datei": "rechnen.py", "zeile": 2,
                                                         "befund": "+ 0 ist überflüssig", "beleg": "", "vertrauen": 0.8}],
                   "zusammenfassung": "fast"}
    rest = _analyse([{"datei": "rechnen.py", "alt": "return a + b + 0", "neu": "return a + b"}])
    anb = Attrappe([halb, nachbessern, rest, OK])
    b = ablauf.diagnose(repo, laden(repo), anb, befehl())
    assert b["status"] == "wartet_auf_freigabe" and b["pruefer"]["urteil"] == "ok" and b["aufrufe"] == 4
    assert "+    return a + b\n" in Path(b["patch"]).read_text()
    assert "+ 0 ist überflüssig" in anb.anfragen[2]["text"]                       # Befunde gehen an den Analysten
    ablauf.verwerfen(repo, b["auftrag"])
    assert json.loads((repo / ".agenten" / b["auftrag"] / "bericht.json").read_text())["status"] == "verworfen"


def test_diagnose_ohne_fehler_ruft_kein_modell(repo):
    (repo / "rechnen.py").write_text("def summe(a, b):\n    return a + b\n")
    _git(repo, "commit", "-qam", "gut")
    anb = Attrappe([])
    assert ablauf.diagnose(repo, laden(repo), anb, befehl())["status"] == "kein_fehler" and not anb.anfragen


# ------------------------------------------------------------------ Review, Uebergabe, Messwerte
def test_review_des_arbeitsstands_mit_befunden(repo):
    (repo / "rechnen.py").write_text("def summe(a, b):\n    return a + b  # schnell\n")
    befund = {"urteil": "nachbessern", "zusammenfassung": "Kommentar",
              "befunde": [{"schwere": "niedrig", "datei": "rechnen.py", "zeile": 2, "befund": "Stil", "beleg": "", "vertrauen": 0.5},
                          {"schwere": "hoch", "datei": "rechnen.py", "zeile": 2, "befund": "kein Test", "beleg": "", "vertrauen": 0.7}]}
    anb = Attrappe([befund])
    b = ablauf.review(repo, laden(repo), anb)
    assert b["urteil"] == "nachbessern" and [x["schwere"] for x in b["befunde"]] == ["hoch", "niedrig"]
    assert "    1  def summe" in anb.anfragen[0]["text"]                           # Zeilennummern fuer Belege
    assert b["dateien"] == ["rechnen.py"]


def test_uebergabe_an_antigravity_und_token_einlesen(repo, tmp_path):
    datei, befehl_ = ablauf.uebergabe(repo, "Summe reparieren", ["rechnen.py"], ["pytest tests"])
    text = datei.read_text()
    assert "AGENTS.md" in text and "rechnen.py" in text and "agy/" in text
    assert "agy -p" in befehl_ and "git worktree add" in befehl_ and "--output-format json" in befehl_
    j = tmp_path / "agy.json"
    j.write_text(json.dumps({"response": "fertig", "num_turns": 3,
                             "usage": {"input_tokens": 10415, "output_tokens": 657, "thinking_tokens": 616}}))
    z = ablauf.agy_einlesen(repo, datei.stem, j)
    assert (z["tokens_ein"], z["tokens_aus"], z["anbieter"], z["tokens_art"]) == (10415, 657, "antigravity", "gemessen")


def test_claude_verbrauch_aus_dem_transkript(tmp_path):
    t = tmp_path / "s.jsonl"
    zeilen = [{"timestamp": "2026-11-05T10:00:00Z", "message": {"role": "assistant", "usage": {"input_tokens": 1,
               "cache_read_input_tokens": 100, "cache_creation_input_tokens": 10, "output_tokens": 5}}},
              {"timestamp": "2026-11-05T12:00:00Z", "message": {"role": "assistant", "usage": {"input_tokens": 2,
               "cache_read_input_tokens": 200, "output_tokens": 7}}},
              {"timestamp": "2026-11-05T12:01:00Z", "message": {"role": "user", "content": "x"}}]
    t.write_text("\n".join(json.dumps(z) for z in zeilen) + "\nkaputt\n")
    s = protokoll.claude_verbrauch("2026-11-05T11:00", t)
    assert (s["antworten"], s["cache_lesen"], s["ausgabe"]) == (1, 200, 7)


def test_befehlszeile_ohne_netz(repo, tmp_path, monkeypatch, capsys):
    from agenten.__main__ import main
    a = tmp_path / "antworten.json"
    a.write_text(json.dumps([{"ok": True}]))
    monkeypatch.setenv("AGENTEN_ATTRAPPE", str(a))
    monkeypatch.chdir(repo)
    assert main(["verbindung"]) == 0 and "ok · Modell gemini-3.5-flash-lite" in capsys.readouterr().out
    assert main(["stand"]) == 0 and "Zweig" in capsys.readouterr().out
