"""Abruf bei den Diensten der Laender: ein Weg fuer Bohrungen, DGM und Gebaeude (Kennung, Wiederholung, TLS).

TLS prueft gegen die Wurzelzertifikate des Systems **und** das Mozilla-Bundle (certifi). Windows laedt neue
Wurzelzertifikate erst, wenn ein Programm ueber die Windows-Kryptografie danach fragt (der Browser); Python liest
nur, was schon im Speicher liegt. Berlin (gdi.berlin.de) ist seit 2026 ueber "Telekom Security TLS RSA Root 2023"
signiert: auf einem Rechner, der die Seite nie im Browser hatte, scheiterte jede Abfrage mit
CERTIFICATE_VERIFY_FAILED, unter Linux nie (docs/16 X33). Die Wurzeln des Systems bleiben dabei: ein Firmen-Proxy,
der TLS mit eigener Wurzel prueft, funktioniert weiter.
"""
from __future__ import annotations

import functools
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Callable

AGENT = "GroundTwin (+https://github.com/martinpazmino/GroundTwin)"
VERSUCHE = 3                                    # Verbindungsabbrueche (Brandenburg: 2 von 3 an manchen Tagen)


class DienstFehler(Exception):
    """Ein Dienst eines Landes antwortet nicht oder nicht verwertbar (die Meldung geht an die Oberflaeche)."""


@functools.lru_cache(maxsize=1)
def ssl_kontext() -> ssl.SSLContext:
    """Wurzeln des Systems (Windows-Speicher, /etc/ssl, SSL_CERT_FILE) plus certifi, falls installiert."""
    kontext = ssl.create_default_context()
    try:
        import certifi
        kontext.load_verify_locations(cafile=certifi.where())
    except (ImportError, OSError):                  # ohne certifi: nur das System
        pass
    return kontext


def zertifikat_meldung(url: str, grund: Exception) -> str:
    host = urllib.parse.urlsplit(url).hostname or url
    text = getattr(grund, "verify_message", "") or str(grund)
    return (f"Zertifikat von {host} nicht prüfbar ({text}) – fehlt auf diesem Rechner ein Wurzelzertifikat, "
            "oder prüft ein Proxy bzw. Virenscanner die Verbindung mit?")


def holen(url: str, zeit: float, bei_http: Callable[[urllib.error.HTTPError], None] | None = None) -> bytes:
    """GET mit Kennung; Verbindungsabbruch bis zu VERSUCHE-mal, nie bei Zeitueberschreitung, HTTP- oder
    Zertifikatsfehler (die aendern sich nicht). bei_http darf einen eigenen Fehler werfen (WCS-Text, 404)."""
    anfrage = urllib.request.Request(url, headers={"User-Agent": AGENT})
    for versuch in range(1, VERSUCHE + 1):
        try:
            with urllib.request.urlopen(anfrage, timeout=zeit, context=ssl_kontext()) as antwort:
                return antwort.read()
        except TimeoutError:
            raise DienstFehler(f"keine Antwort in {zeit:g} s") from None
        except urllib.error.HTTPError as err:
            if bei_http is not None:
                bei_http(err)
            raise DienstFehler(f"HTTP {err.code}") from None
        except (urllib.error.URLError, OSError) as err:
            grund = err.reason if isinstance(err, urllib.error.URLError) else err
            if isinstance(grund, TimeoutError):            # Zeitueberschreitung beim Verbinden: nicht neu
                raise DienstFehler(f"keine Antwort in {zeit:g} s") from None
            if isinstance(grund, ssl.SSLCertVerificationError):
                raise DienstFehler(zertifikat_meldung(url, grund)) from None
            if versuch < VERSUCHE:                         # Verbindung abgebrochen (z. B. reset by peer): kurz warten, neu
                time.sleep(versuch)
                continue
            raise DienstFehler(f"nicht erreichbar ({grund})") from None
    raise AssertionError("unerreichbar")


def erreichbar(url: str, zeit: float) -> tuple[int, bytes]:
    """Nur ansehen, nicht laden (Werkzeug „Dienste der Länder“): GET mit Range auf die ersten 2 KB, gelesen werden
    hoechstens diese - auch eine Kachel von 25 MB kostet so nichts. Rueckgabe (HTTP-Status, Anfang der Antwort)."""
    anfrage = urllib.request.Request(url, headers={"User-Agent": AGENT, "Range": "bytes=0-2047"})
    try:
        with urllib.request.urlopen(anfrage, timeout=zeit, context=ssl_kontext()) as antwort:
            return antwort.status, antwort.read(2048)
    except TimeoutError:
        raise DienstFehler(f"keine Antwort in {zeit:g} s") from None
    except urllib.error.HTTPError as err:
        raise DienstFehler(f"HTTP {err.code}") from None
    except (urllib.error.URLError, OSError) as err:
        grund = err.reason if isinstance(err, urllib.error.URLError) else err
        if isinstance(grund, ssl.SSLCertVerificationError):
            raise DienstFehler(zertifikat_meldung(url, grund)) from None
        raise DienstFehler(f"nicht erreichbar ({grund})") from None
