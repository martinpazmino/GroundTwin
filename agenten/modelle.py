"""Modellregister (modelle.json) und Auswahl je Rolle: Standardmodell aus der .env, das starke nur bei hohem Risiko und
wenn bezahlte Modelle erlaubt sind; ein auslaufendes Modell faellt auf seinen Ersatz."""
from __future__ import annotations

import json
from pathlib import Path

from .einstellungen import Einstellungen

REGISTER = json.loads(Path(__file__).with_name("modelle.json").read_text(encoding="utf-8"))


def eintrag(modell: str) -> dict:
    return REGISTER["modelle"].get(modell, {"anbieter": "gemini", "frei": False, "ein": 0.0, "aus": 0.0})


def kosten_usd(modell: str, ein: int, aus: int) -> float:
    e = eintrag(modell)
    return round((ein * e.get("ein", 0) + aus * e.get("aus", 0)) / 1e6, 6)


def ist_risiko(dateien: list[str]) -> bool:
    return any(d.startswith(tuple(REGISTER["risiko_pfade"])) for d in dateien)


def waehlen(rolle: str, e: Einstellungen, dateien: list[str] | None = None, stark: bool = False) -> str:
    regel = REGISTER["rollen"].get(rolle, {"modell": "standard"})
    modell = e.modell if regel["modell"] == "standard" else regel["modell"]
    if (stark or ist_risiko(dateien or [])) and regel.get("risiko_modell") == "stark" and e.bezahlt_erlaubt:
        modell = e.modell_stark
    while eintrag(modell).get("ersatz"):
        modell = eintrag(modell)["ersatz"]
    if not eintrag(modell).get("frei") and not e.bezahlt_erlaubt:
        raise PermissionError(f"{modell} ist kostenpflichtig, AI_ALLOW_PAID_API ist aus")
    return modell
