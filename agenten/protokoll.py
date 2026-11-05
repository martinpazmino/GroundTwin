"""Messwerte: eine JSON-Zeile je Modellaufruf in .agenten/metriken.jsonl (Tokens gemessen vom Anbieter, Kosten
geschaetzt aus modelle.json) und die Claude-Seite aus dem Transkript von Claude Code (die usage jeder Antwort)."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .modelle import eintrag, kosten_usd


def jetzt() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def schreiben(ordner: Path, auftrag: str, rolle: str, anbieter: str, antwort=None, erfolg: bool = True,
              fehler: str = "", kosten: bool = True) -> dict:
    ordner.mkdir(parents=True, exist_ok=True)
    z = {"zeit": jetzt(), "auftrag": auftrag, "rolle": rolle, "anbieter": anbieter, "erfolg": erfolg}
    if antwort is not None:
        z.update(modell=antwort.modell, tokens_ein=antwort.tokens_ein, tokens_aus=antwort.tokens_aus,
                 tokens_denken=antwort.tokens_denken, tokens_cache=antwort.tokens_cache, dauer_ms=antwort.dauer_ms,
                 versuche=antwort.versuche, tokens_art="gemessen" if anbieter != "attrappe" else "geschaetzt")
        if kosten:
            frei = eintrag(antwort.modell).get("frei", False)
            z.update(kosten_usd=kosten_usd(antwort.modell, antwort.tokens_ein, antwort.tokens_aus + antwort.tokens_denken),
                     kosten_art="geschätzt (Listenpreis; im freien Kontingent 0)" if frei else "geschätzt")
    if fehler:
        z["fehler"] = fehler[:300]
    with open(ordner / "metriken.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(z, ensure_ascii=False) + "\n")
    return z


def summe(ordner: Path, seit: str = "") -> dict:
    s = {"aufrufe": 0, "fehler": 0, "tokens_ein": 0, "tokens_aus": 0, "tokens_denken": 0, "kosten_usd": 0.0, "je_rolle": {}}
    datei = ordner / "metriken.jsonl"
    if not datei.exists():
        return s
    for zeile in datei.read_text(encoding="utf-8").splitlines():
        z = json.loads(zeile)
        if seit and z["zeit"] < seit:
            continue
        s["aufrufe"] += 1
        s["fehler"] += not z.get("erfolg", True)
        for k in ("tokens_ein", "tokens_aus", "tokens_denken"):
            s[k] += z.get(k, 0)
        s["kosten_usd"] = round(s["kosten_usd"] + z.get("kosten_usd", 0.0), 6)
        r = s["je_rolle"].setdefault(z["rolle"], 0)
        s["je_rolle"][z["rolle"]] = r + 1
    return s


def claude_transkript() -> Path | None:
    if os.environ.get("CLAUDE_TRANSKRIPT"):
        return Path(os.environ["CLAUDE_TRANSKRIPT"])
    dateien = sorted((Path.home() / ".claude" / "projects").glob("*/*.jsonl"), key=lambda p: p.stat().st_mtime)
    return dateien[-1] if dateien else None


def claude_verbrauch(seit: str = "", transkript: Path | None = None) -> dict:
    """Tokens der Claude-Antworten seit einem Zeitpunkt (ISO, UTC) - gemessen aus dem Transkript."""
    pfad = transkript or claude_transkript()
    s = {"antworten": 0, "eingabe": 0, "cache_lesen": 0, "cache_schreiben": 0, "ausgabe": 0, "transkript": str(pfad or "")}
    if not pfad or not Path(pfad).exists():
        return s
    with open(pfad, encoding="utf-8") as f:
        for zeile in f:
            try:
                e = json.loads(zeile)
            except ValueError:
                continue
            m = e.get("message")
            if not isinstance(m, dict) or m.get("role") != "assistant" or not m.get("usage"):
                continue
            if seit and (e.get("timestamp") or "") < seit:
                continue
            u = m["usage"]
            s["antworten"] += 1
            s["eingabe"] += u.get("input_tokens", 0)
            s["cache_lesen"] += u.get("cache_read_input_tokens", 0)
            s["cache_schreiben"] += u.get("cache_creation_input_tokens", 0)
            s["ausgabe"] += u.get("output_tokens", 0)
    return s
