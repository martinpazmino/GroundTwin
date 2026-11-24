"""Hausregeln als Pruefung statt als Prosa (docs/31): was CLAUDE.md und docs/16 verlangen und sich mechanisch pruefen
laesst, steht hier. Jede Meldung sagt, wie man es richtig macht - nicht, wie man die Regel umgeht.

Eine Regel ohne Ausnahme bleibt ohne Ausnahme. ``BESTAND`` sind alte Stellen, die die Regel verletzen duerfen; die Liste
darf nur kuerzer werden (eine neue Stelle dort einzutragen braucht eine Entscheidung in docs/11).
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

# Bereiche des Codes und wer wen importieren darf (docs/31 §3.1, Architektur in docs/ARCHITECTURE_BAUGRUNDMODELL.md).
BEREICHE = {
    "extractor": "services/extractor",
    "baugrundmodell": "services/modeler/baugrundmodell",
    "geodaten": "services/geodaten/geodaten",
    "baugrundanalyse": "services/analyse/baugrundanalyse",
    "wissen": "services/wissen/wissen",
    "ui": "ui",
    "server": "server",
    "agenten": "agenten",
    "geo_agent": "geo_agent",
}
ERLAUBT = {
    "extractor": set(),                                   # Extraktion kennt kein Modell, keine App
    "baugrundmodell": set(),                              # Modellierer: reine Rechnung aus dem JSON
    "geodaten": {"baugrundmodell"},                       # BoreholeML deutet wie die App (normen)
    "baugrundanalyse": {"baugrundmodell"},                # Analyse liest das Modell, aendert die Bohrungen nie
    "wissen": set(),                                      # Wissenskatalog: Daten und Planer; Code nur als Verweis (A2)
    "ui": {"extractor", "baugrundmodell", "baugrundanalyse", "geodaten"},
    "server": {"ui", "baugrundmodell", "geodaten", "baugrundanalyse"},
    "agenten": set(),
    "geo_agent": set(),                                   # v1, eingefroren
}
BESTAND_IMPORT = {                                        # (Datei, Ziel): alt, darf nur verschwinden
    ("services/extractor/prototyp_v2.py", "geo_agent"),   # Prototyp v2 nutzt den Bodenparser von v1
    ("ui/excel_v1.py", "geo_agent"),                      # Excel v1 (Streamlit) bleibt bei v1
}
NETZ_ERLAUBT = {"services/geodaten/geodaten/netz.py",     # X33: jede Anfrage der App ueber netz.py (System + certifi)
                "agenten/anbieter.py"}                    # Agententeam: einzige Stelle zur Modell-API (docs/24)
WERKZEUGE = "services/geodaten/werkzeuge/"                # Werkzeuge von Hand (Codelisten, Grenzen), nicht in der App
NETZ_MODULE = {"urllib.request", "http.client", "requests", "httpx", "aiohttp", "socket"}


def _py(ordner: str):
    for f in sorted((REPO / ordner).rglob("*.py")):
        if "tests" not in f.relative_to(REPO).parts and "__pycache__" not in f.parts:
            yield f


def _rel(f: Path) -> str:
    return f.relative_to(REPO).as_posix()


def _importe(f: Path):
    for n in ast.walk(ast.parse(f.read_text(encoding="utf-8"), str(f))):
        if isinstance(n, ast.Import):
            for a in n.names:
                yield n.lineno, a.name
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            yield n.lineno, n.module


def _bereich_von_modul(modul: str, extractor_stems: set[str]) -> str | None:
    top = modul.split(".")[0]
    if top in extractor_stems:
        return "extractor"
    return top if top in BEREICHE else None


def test_bereiche_importieren_nur_erlaubte_bereiche():
    stems = {f.stem for f in (REPO / BEREICHE["extractor"]).glob("*.py")}
    fehler = []
    for bereich, ordner in BEREICHE.items():
        for f in _py(ordner):
            for zeile, modul in _importe(f):
                ziel = _bereich_von_modul(modul, stems)
                if ziel is None or ziel == bereich or ziel in ERLAUBT[bereich] or (_rel(f), ziel) in BESTAND_IMPORT:
                    continue
                fehler.append(f"{_rel(f)}:{zeile}: {bereich} importiert {ziel} ({modul}). Erlaubt fuer {bereich}: "
                              f"{sorted(ERLAUBT[bereich]) or 'nichts'}. Die Logik gehoert in den tieferen Bereich; "
                              f"eine neue Abhaengigkeit braucht eine Entscheidung (docs/11) und ERLAUBT hier.")
    assert not fehler, "\n".join(fehler)


def test_bestand_der_importe_ist_noch_noetig():
    stems = {f.stem for f in (REPO / BEREICHE["extractor"]).glob("*.py")}
    for datei, ziel in BESTAND_IMPORT:
        f = REPO / datei
        assert f.exists() and any(_bereich_von_modul(m, stems) == ziel for _, m in _importe(f)), \
            f"BESTAND_IMPORT ({datei}, {ziel}) wird nicht mehr gebraucht: aus der Liste streichen"


def test_netzzugriff_nur_ueber_netz_py():
    fehler = []
    for ordner in ("server", "ui", "services", "agenten"):
        for f in _py(ordner):
            if _rel(f) in NETZ_ERLAUBT or _rel(f).startswith(WERKZEUGE):
                continue
            for zeile, modul in _importe(f):
                if modul in NETZ_MODULE or modul.split(".")[0] in {"requests", "httpx", "aiohttp"}:
                    fehler.append(f"{_rel(f)}:{zeile}: {modul}. Anfragen gehen ueber geodaten.netz "
                                  f"(TLS mit System-Store und certifi, X33), nie direkt.")
    assert not fehler, "\n".join(fehler)


def _breit_und_still(h: ast.ExceptHandler) -> bool:
    breit = h.type is None or (isinstance(h.type, ast.Name) and h.type.id in ("Exception", "BaseException"))
    still = all(isinstance(s, (ast.Pass, ast.Continue)) or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
                for s in h.body)
    return breit and still


def test_kein_fehler_wird_still_verschluckt():
    """Ein zweifelhafter Wert wird markiert, nie versteckt (CLAUDE.md): kein 'except Exception: pass'."""
    fehler = [f"{_rel(f)}:{n.lineno}: breites except ohne Behandlung. Den erwarteten Fehler nennen und ihn melden "
              f"(issue, Hinweis, Protokoll) statt ihn zu verschlucken."
              for o in ("server", "ui", "services", "agenten") for f in _py(o)
              for n in ast.walk(ast.parse(f.read_text(encoding="utf-8"))) if isinstance(n, ast.ExceptHandler) and _breit_und_still(n)]
    assert not fehler, "\n".join(fehler)


def test_noqa_nennt_die_regel():
    fehler = [f"{_rel(f)}:{i}: '# noqa' ohne Code. Den Fehler beheben oder die Regel nennen ('# noqa: E402')."
              for o in ("server", "ui", "services", "agenten", "tests", "scripts", "benchmark") for f in REPO.glob(f"{o}/**/*.py")
              if "__pycache__" not in f.parts and f.name != Path(__file__).name
              for i, z in enumerate(f.read_text(encoding="utf-8").splitlines(), 1) if re.search(r"#\s*noqa\b(?!:)", z)]
    assert not fehler, "\n".join(fehler)


def _git_dateien() -> list[str]:
    try:
        r = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError) as e:
        pytest.skip(f"kein git: {e}")
    return r.stdout.splitlines()


def test_keine_pfade_die_sich_nur_in_gross_klein_schreibung_unterscheiden():
    """Windows und macOS unterscheiden nicht: zwei solche Dateien ueberschreiben sich beim Auschecken (gesehen:
    agenten/routinen/README.md und readme.md, 2026-11-21)."""
    je: dict[str, list[str]] = {}
    for d in _git_dateien():
        je.setdefault(d.lower(), []).append(d)
    fehler = [f"{' und '.join(v)}: unterscheiden sich nur in Gross-/Kleinschreibung. Eine umbenennen." for v in je.values() if len(v) > 1]
    assert not fehler, "\n".join(fehler)


EIGENE_PDF = {"data/beispiele/synthetisch_bohrprofil.pdf"}   # selbst erzeugt (synth_bohrprofil.py)


def test_keine_gutachten_dritter_im_repository():
    """Gutachten Dritter nie ins Repository: nur URL, sha256 und Fakten (CLAUDE.md, P-Regeln in docs/16)."""
    fehler = [f"{d}: PDF im Repository. Gutachten Dritter bleiben ausserhalb; in benchmark/groundtruth nur source + "
              f"sha256. Eigene synthetische PDFs in EIGENE_PDF eintragen." for d in _git_dateien()
              if d.lower().endswith(".pdf") and d not in EIGENE_PDF]
    bilder = [d for d in _git_dateien() if re.search(r"\.(png|jpe?g|tiff?|webp)$", d, re.I)
              and not d.startswith(("docs/img/", "apps/web/"))]
    fehler += [f"{d}: Bild ausserhalb von docs/img. Bilder aus Gutachten Dritter gehoeren nicht ins Repository; "
               f"eigene Bildschirmfotos nach docs/img." for d in bilder]
    assert not fehler, "\n".join(fehler)


def test_wahrheit_nennt_quelle_und_sha256():
    fehler = []
    for f in sorted((REPO / "benchmark/groundtruth").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if not d.get("source") or not re.fullmatch(r"[0-9a-f]{64}", d.get("sha256") or ""):
            fehler.append(f"{_rel(f)}: 'source' (URL) und 'sha256' (64 hex) fehlen; ohne sie ist die Zahl nicht nachpruefbar.")
    assert not fehler, "\n".join(fehler)


def test_keine_claude_modellkennung_im_repository():
    muster = re.compile(r"claude-(?:opus|sonnet|haiku|fable)-\d")
    fehler = []
    for d in _git_dateien():
        p = REPO / d
        if p.suffix in {".py", ".md", ".json", ".ts", ".mjs", ".yml", ".yaml", ".txt", ".toml", ".html", ".bat", ".tsv"} \
                and p.is_file() and not d.startswith("apps/web/dist/"):
            for i, z in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if muster.search(z):
                    fehler.append(f"{d}:{i}: Kennung eines Claude-Modells. Keine Modellkennungen in Dateien des Repositorys.")
    assert not fehler, "\n".join(fehler)


def test_keine_geheimnisse_im_repository():
    dateien = _git_dateien()
    fehler = [f"{d}: .env im Repository. Einstellungen gehoeren in .env (ignoriert), Vorlage agenten/env.beispiel."
              for d in dateien if Path(d).name == ".env"]
    muster = re.compile(r"AIza[0-9A-Za-z_\-]{35}|sk-ant-[0-9A-Za-z_\-]{20,}|ghp_[0-9A-Za-z]{36}|-----BEGIN [A-Z ]*PRIVATE KEY")
    for d in dateien:
        p = REPO / d
        if p.is_file() and p.stat().st_size < 2_000_000 and not d.startswith("apps/web/dist/"):
            try:
                text = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            fehler += [f"{d}: sieht nach einem Schluessel aus. Schluessel nie ins Repository (.env oder Geheimnis der Umgebung)."
                       for _ in muster.finditer(text)]
    assert not fehler, "\n".join(fehler)


def test_bodenkennwerte_setzen_nie_char():
    """GroundTwin leitet ab, der Ingenieur setzt charakteristische Werte (D108): kein '_char' aus dem Code."""
    fehler = []
    for f in _py("services/modeler/baugrundmodell"):
        for n in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and re.search(r"_char\b", n.value) \
                    and len(n.value) < 60 and " " not in n.value.strip():
                fehler.append(f"{_rel(f)}:{n.lineno}: '{n.value}'. Kennwerte nur als _min/_max/_mean/_n; "
                              f"_char setzt der Ingenieur.")
    assert not fehler, "\n".join(fehler)


def modul_huelle(pfad: Path) -> str:
    """sha256 des Quelltexts mit LF-Zeilenenden (gleich unter Windows und Linux)."""
    return hashlib.sha256(pfad.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def test_baseline_passt_zur_extraktion():
    """Jede Aenderung an prototyp_v4.py geht durch die Regression (CLAUDE.md): die Baseline traegt die Huelle des
    Moduls, mit dem sie gerechnet wurde (benchmark/regression.py --write schreibt beide)."""
    modul = REPO / "services/extractor/prototyp_v4.py"
    seite = REPO / "benchmark/baseline_v4.modul.json"
    assert seite.exists(), "benchmark/baseline_v4.modul.json fehlt: Regression mit --write laufen lassen"
    soll = json.loads(seite.read_text(encoding="utf-8"))["sha256"]
    assert modul_huelle(modul) == soll, (
        "prototyp_v4.py hat sich seit der Baseline geaendert. Regression laufen lassen (real, stress, synth; Befehl in "
        "CLAUDE.md); ohne Rueckgang mit --write die Baseline neu schreiben. Die Huelle wird dabei mitgeschrieben.")


def test_baseline_der_sondierungen_passt_zur_stufe():
    """Wie bei prototyp_v4: wer sondierungen.py aendert, misst neu (benchmark/sondierungen_eval.py --write)."""
    seite = REPO / "benchmark/baseline_sondierungen.json"
    assert seite.exists(), "benchmark/baseline_sondierungen.json fehlt: sondierungen_eval.py --write laufen lassen"
    soll = json.loads(seite.read_text(encoding="utf-8"))["_meta"]["sha256"]
    assert modul_huelle(REPO / "services/extractor/sondierungen.py") == soll, (
        "sondierungen.py hat sich seit der Baseline geaendert. Messen (echte PDFs, Stress, synthetisch; docs/05 §5) "
        "und ohne Rueckgang mit --write die Baseline neu schreiben.")
