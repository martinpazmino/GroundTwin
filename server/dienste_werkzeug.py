"""Werkzeug „Dienste der Länder“ (docs/21 §4.8, D98): das Register services/geodaten/geodaten/dienste.json ansehen,
bearbeiten und gegen den echten Dienst pruefen - Seite dienste.html.

Bearbeiten nur ohne Passwort (eigener Rechner) oder mit GEO_AGENT_DIENSTE_BEARBEITEN=1. Sonst nur lesen und die
gespeicherten Eintraege pruefen: der Server ruft dann nur Adressen auf, die schon im Register stehen (nie eine
Adresse aus der Anfrage). Wer speichert, schickt den Stand mit, den er gelesen hat (sonst Konflikt statt
stillem Ueberschreiben).
"""
from __future__ import annotations

import os
from pathlib import Path

from geodaten import bohrdaten, laender
from geodaten import dienste as register

REPO = Path(__file__).resolve().parents[1]


class Konflikt(ValueError):
    """Das Register hat sich seit dem Lesen geaendert."""


class Gesperrt(PermissionError):
    """Bearbeiten ist auf diesem Server ausgeschaltet."""


def bearbeiten_erlaubt(passwort: str) -> tuple[bool, str]:
    if os.environ.get("GEO_AGENT_DIENSTE_BEARBEITEN", "") == "1":
        return True, ""
    if passwort:
        return False, ("Im Netz (mit Passwort) nur lesen und prüfen. Bearbeiten auf dem eigenen Rechner oder mit "
                       "GEO_AGENT_DIENSTE_BEARBEITEN=1.")
    return True, ""


def _datei() -> str:
    pfad = Path(register.DATEI).resolve()
    try:
        return pfad.relative_to(REPO).as_posix()
    except ValueError:
        return str(pfad)


def ansicht(bearbeiten: bool, grund: str) -> dict:
    daten = register.laden()
    return {"datei": _datei(), "version": register.version(), "bearbeiten": bearbeiten, "grund": grund,
            "format": daten.get("format", ""), "stand": daten.get("stand", ""),
            "beschreibung": daten.get("beschreibung", ""),
            "laender": ["Deutschland", *laender.LAENDER], "themen": register.THEMEN,
            "arten": {art: {"thema": th, "angebunden": verbunden, "pflicht": list(register.PFLICHT_JE_ART.get(art, ()))}
                      for art, (th, verbunden) in register.ARTEN.items()},
            "dienste": daten.get("dienste") or []}


def speichern(dienste: list[dict], version: str, bearbeiten: bool) -> None:
    if not bearbeiten:
        raise Gesperrt("Bearbeiten ist auf diesem Server ausgeschaltet")
    if version != register.version():
        raise Konflikt("Das Register wurde inzwischen geändert – neu laden und die Änderung noch einmal machen")
    daten = register.laden()
    register.speichern({**{k: v for k, v in daten.items() if k != "dienste"}, "dienste": dienste})
    bohrdaten.neu_laden(erzwingen=True)                  # die App fragt ab jetzt mit dem neuen Stand


def pruefen(kennung: str, eintrag: dict | None, bearbeiten: bool) -> dict:
    """Einen Eintrag gegen den echten Dienst pruefen: gespeichert (Kennung) oder, nur beim Bearbeiten, ein Entwurf."""
    if eintrag is not None:
        if not bearbeiten:
            raise Gesperrt("Entwürfe prüfen nur beim Bearbeiten (im Netz nur gespeicherte Einträge)")
        probleme = register.fehler({"dienste": [register.ergaenzen(eintrag)]})
        if probleme:
            raise ValueError("; ".join(probleme[:6]))
        d = eintrag
    else:
        d = next((x for x in register.laden().get("dienste") or [] if x.get("id") == kennung), None)
        if d is None:
            raise KeyError(kennung)
    return {"id": d.get("id", ""), **register.pruefen_live(d)}
