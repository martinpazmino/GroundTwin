"""Abruf bei den Diensten der Laender (services/geodaten/geodaten/netz.py): TLS gegen System + certifi, Meldungen.

Fall aus der Praxis (2026-11-03, Windows): "BE: nicht erreichbar ([SSL: CERTIFICATE_VERIFY_FAILED] ... unable to get
local issuer certificate)". gdi.berlin.de ist ueber "Telekom Security TLS RSA Root 2023" signiert; Windows haelt neue
Wurzeln erst, wenn der Browser sie einmal brauchte, Python liest nur den Speicher. Hier: ein HTTPS-Server mit eigener
Wurzel, die nur "certifi" kennt (dessen Datei ersetzt), nicht das System.
"""
from __future__ import annotations

import http.server
import shutil
import ssl
import subprocess
import sys
import threading
import urllib.request
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO / "services" / "geodaten")]
from geodaten import netz  # noqa: E402
from geodaten.bohrdaten import DienstFehler  # noqa: E402


@pytest.fixture(autouse=True)
def neuer_kontext():
    netz.ssl_kontext.cache_clear()
    yield
    netz.ssl_kontext.cache_clear()


def test_kontext_kennt_die_wurzel_von_berlin():
    certifi = pytest.importorskip("certifi")
    namen = {dict(teil[0] for teil in c["subject"]).get("commonName") for c in netz.ssl_kontext().get_ca_certs()}
    assert "Telekom Security TLS RSA Root 2023" in namen                 # gdi.berlin.de seit 2026
    assert Path(certifi.where()).exists()


def _zertifikate(ordner: Path) -> tuple[Path, Path, Path]:
    """Eigene Wurzel und ein Serverzertifikat fuer localhost (openssl; X509_STRICT von Python 3.13 erfuellt)."""
    if not shutil.which("openssl"):
        pytest.skip("openssl nicht vorhanden")
    ec = ["-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:prime256v1", "-nodes"]

    def lauf(*args):
        subprocess.run(["openssl", *args], cwd=ordner, check=True, capture_output=True)
    lauf("req", "-x509", *ec, "-keyout", "wurzel.key", "-out", "wurzel.pem", "-days", "2",
         "-subj", "/CN=GroundTwin Test-Wurzel", "-addext", "basicConstraints=critical,CA:TRUE",
         "-addext", "keyUsage=critical,keyCertSign,cRLSign")
    lauf("req", *ec, "-keyout", "server.key", "-out", "server.csr", "-subj", "/CN=localhost")
    (ordner / "ext.cnf").write_text("subjectAltName=DNS:localhost,IP:127.0.0.1\nbasicConstraints=CA:FALSE\n"
                                    "keyUsage=critical,digitalSignature\nextendedKeyUsage=serverAuth\n"
                                    "authorityKeyIdentifier=keyid\nsubjectKeyIdentifier=hash\n")
    lauf("x509", "-req", "-in", "server.csr", "-CA", "wurzel.pem", "-CAkey", "wurzel.key", "-CAcreateserial",
         "-out", "server.pem", "-days", "2", "-extfile", "ext.cnf")
    return ordner / "wurzel.pem", ordner / "server.pem", ordner / "server.key"


class _Antwort(http.server.BaseHTTPRequestHandler):
    def do_GET(self):                                    # noqa: N802 (Name von http.server)
        self.send_response(200)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass


@pytest.fixture()
def https(tmp_path):
    wurzel, zert, schluessel = _zertifikate(tmp_path)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Antwort)
    kontext = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    kontext.load_cert_chain(zert, schluessel)
    server.socket = kontext.wrap_socket(server.socket, server_side=True)
    faden = threading.Thread(target=server.serve_forever, daemon=True)
    faden.start()
    yield f"https://localhost:{server.server_address[1]}/", wurzel
    server.shutdown()
    server.server_close()


def test_wurzel_nur_in_certifi_reicht(https, monkeypatch):
    certifi = pytest.importorskip("certifi")
    url, wurzel = https
    monkeypatch.setattr(certifi, "where", lambda: str(wurzel))          # die Wurzel kennt nur "certifi"
    assert netz.holen(url, 5) == b"ok"


def test_zertifikatsfehler_klar_und_ohne_wiederholung(https, monkeypatch):
    url, _ = https
    aufrufe = []
    echt = urllib.request.urlopen

    def zaehlen(*args, **kw):
        aufrufe.append(1)
        return echt(*args, **kw)
    monkeypatch.setattr(urllib.request, "urlopen", zaehlen)
    monkeypatch.setattr(netz.time, "sleep", lambda s: pytest.fail("Zertifikatsfehler nicht wiederholen"))
    with pytest.raises(DienstFehler, match=r"Zertifikat von localhost nicht prüfbar \(.*\) – fehlt auf diesem Rechner"):
        netz.holen(url, 5)
    assert len(aufrufe) == 1


def _skript():
    import importlib.util
    spec = importlib.util.spec_from_file_location("dienste_pruefen", REPO / "scripts" / "dienste_pruefen.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def test_dienste_pruefen_ohne_netz(monkeypatch):
    """scripts/dienste_pruefen.py: Capabilities fuer WFS/WCS, fuer Kacheln nur der Server; 404 dort ist kein Fehler,
    ein Zertifikatsfehler immer."""
    s = _skript()
    wfs = {"id": "BE", "art": "wfs-kopf", "url": "https://gdi.berlin.de/services/wfs/bohrdaten"}
    kacheln = {"id": "BE-LOD2", "art": "lod2-kacheln", "url": "https://gdi.berlin.de/data/a_lod2/atom/LoD2_{e}_{n}.zip"}
    assert s.pruef_url(wfs) == "https://gdi.berlin.de/services/wfs/bohrdaten?SERVICE=WFS&REQUEST=GetCapabilities"
    assert s.pruef_url(kacheln) == "https://gdi.berlin.de/"
    monkeypatch.setattr(netz, "holen", lambda url, zeit: (_ for _ in ()).throw(DienstFehler("HTTP 404")))
    assert s.pruefen(kacheln)[0] and not s.pruefen(wfs)[0]
    monkeypatch.setattr(netz, "holen", lambda url, zeit: (_ for _ in ()).throw(DienstFehler("Zertifikat von x nicht prüfbar")))
    assert not s.pruefen(kacheln)[0]
    monkeypatch.setattr(netz, "holen", lambda url, zeit: b"<wfs:WFS_Capabilities/>")
    assert s.pruefen(wfs) == (True, "23 Byte in 0.0 s")
