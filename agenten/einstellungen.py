"""Einstellungen aus der Umgebung und einer .env im Repository (nie eingecheckt). Die Namen sind die der .env des
Nutzers (AI_*, GEMINI_*); fehlt etwas, gelten sichere Vorgaben (keine bezahlten Modelle, Freigabe durch Claude)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_datei(pfad: Path) -> dict[str, str]:
    werte: dict[str, str] = {}
    if not pfad.is_file():
        return werte
    for zeile in pfad.read_text(encoding="utf-8").splitlines():
        zeile = zeile.strip()
        if not zeile or zeile.startswith("#") or "=" not in zeile:
            continue
        k, _, v = zeile.partition("=")
        v = v.split(" #")[0].strip().strip('"').strip("'")
        werte[k.strip()] = v
    return werte


def _wahr(v: str | None, vorgabe: bool) -> bool:
    return vorgabe if v in (None, "") else v.strip().lower() in ("1", "true", "ja", "yes", "on")


def _zahl(v: str | None, vorgabe: int) -> int:
    try:
        return int(v) if v not in (None, "") else vorgabe
    except ValueError:
        return vorgabe


@dataclass
class Einstellungen:
    api_schluessel: str
    modell: str
    modell_stark: str
    aktiv: bool
    parallel: int
    zeit_s: int
    versuche: int
    freigabe_claude: bool
    bezahlt_erlaubt: bool
    tokens_protokollieren: bool
    kosten_protokollieren: bool
    budget_usd_monat: float

    @property
    def hat_schluessel(self) -> bool:
        return bool(self.api_schluessel)


def laden(repo: Path) -> Einstellungen:
    w = {**_env_datei(repo / ".env"), **{k: v for k, v in os.environ.items() if k.startswith(("AI_", "GEMINI_"))}}
    try:
        budget = float(w.get("AI_BUDGET_USD_MONAT") or 9)
    except ValueError:
        budget = 9.0
    return Einstellungen(
        api_schluessel=w.get("GEMINI_API_KEY", ""),
        modell=w.get("GEMINI_MODEL") or "gemini-3.8-flash",
        modell_stark=w.get("GEMINI_ADVANCED_MODEL") or "gemini-4-argon",
        aktiv=_wahr(w.get("AI_ORCHESTRATION_ENABLED"), True),
        parallel=max(1, _zahl(w.get("AI_MAX_PARALLEL_AGENTS"), 3)),
        zeit_s=max(10, _zahl(w.get("AI_AGENT_TIMEOUT"), 300)),
        versuche=max(0, _zahl(w.get("AI_MAX_RETRIES"), 2)),
        freigabe_claude=_wahr(w.get("AI_REQUIRE_CLAUDE_APPROVAL"), True),
        bezahlt_erlaubt=_wahr(w.get("AI_ALLOW_PAID_API"), False),
        tokens_protokollieren=_wahr(w.get("AI_LOG_TOKEN_USAGE"), True),
        kosten_protokollieren=_wahr(w.get("AI_LOG_COSTS"), True),
        budget_usd_monat=budget,
    )
