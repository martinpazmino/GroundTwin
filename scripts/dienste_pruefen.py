"""Alle Dienste der Laender aus dienste.json kurz ansprechen: erreichbar, Zertifikat (TLS), HTTP - auf diesem Rechner.

    python scripts/dienste_pruefen.py                 (Windows: .venv\\Scripts\\python scripts\\dienste_pruefen.py)
    python scripts/dienste_pruefen.py --nur BE NW      (nur diese Dienste)

WFS und WCS: GetCapabilities. Kacheldienste (LoD2): nur ihr Server - dort zaehlt, dass er mit gueltigem Zertifikat
antwortet (auch 403/404). Gesendet wird keine Lage eines Projekts. Rueckgabe 1, wenn ein Dienst nicht geht; die
Zeile sagt warum (docs/16 X33: fehlendes Wurzelzertifikat unter Windows).
"""
from __future__ import annotations

import argparse
import platform
import ssl
import sys
import time
import urllib.parse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "services" / "geodaten"))

from geodaten import netz  # noqa: E402
from geodaten.bohrdaten import DIENSTE, DienstFehler  # noqa: E402

ZEIT = 30
DIENST_ART = {"wfs-kopf": "WFS", "wfs-boreholeml": "WFS", "wcs-dgm": "WCS"}


def pruef_url(d: dict) -> str:
    if d["art"] in DIENST_ART:
        return d["url"] + "?" + urllib.parse.urlencode({"SERVICE": DIENST_ART[d["art"]], "REQUEST": "GetCapabilities"})
    teile = urllib.parse.urlsplit(d["url"])            # Kacheln: nur der Server (ihr Verzeichnis hat bis 7 MB)
    return f"{teile.scheme}://{teile.netloc}/"


def pruefen(d: dict) -> tuple[bool, str]:
    url = pruef_url(d)
    beginn = time.monotonic()
    try:
        daten = netz.holen(url, ZEIT)
    except DienstFehler as err:
        if d["art"] not in DIENST_ART and str(err).startswith("HTTP "):
            return True, f"Server antwortet ({err}), Zertifikat gültig"
        return False, str(err)
    dauer = time.monotonic() - beginn
    if d["art"] in DIENST_ART and b"Capabilities" not in daten[:5000]:
        return False, f"keine Capabilities ({len(daten)} Byte)"
    groesse = f"{len(daten) // 1024} KB" if len(daten) >= 1024 else f"{len(daten)} Byte"
    return True, f"{groesse} in {dauer:.1f} s"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):          # Windows-Konsole oder Umleitung in cp1252/cp850: nie abbrechen
        sys.stdout.reconfigure(errors="replace")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--nur", nargs="*", help="Kennungen der Dienste (z. B. BE NW BB-DGM1)")
    a = ap.parse_args()
    try:
        import certifi
        zusatz = f"certifi {certifi.__version__}"
    except ImportError:
        zusatz = "ohne certifi (nur Wurzeln des Systems)"
    print(f"Python {platform.python_version()} · {platform.system()} {platform.release()} · {ssl.OPENSSL_VERSION} · "
          f"{zusatz}")
    fehler = 0
    for d in DIENSTE:
        if a.nur and d["id"] not in a.nur:
            continue
        ok, text = pruefen(d)
        fehler += not ok
        host = urllib.parse.urlsplit(d["url"]).hostname
        print(f"{'ok  ' if ok else 'FEHL'}  {d['id']:<8} {d['art']:<15} {host:<28} {text}")
    print(f"{fehler} Dienst(e) mit Fehler" if fehler else "alle Dienste erreichbar")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
