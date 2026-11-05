"""Anbieter hinter einer Schnittstelle: `antworten(modell, system, text) -> Antwort` mit den Tokens, wie der Anbieter sie
meldet (gemessen, nicht geschaetzt). Gemini ueber REST (keine neue Abhaengigkeit), die Attrappe fuer Pruefungen ohne
Netz. Ein weiterer Anbieter (Anthropic, OpenAI, Ollama) ist eine weitere Klasse."""
from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{modell}:generateContent"


@dataclass
class Antwort:
    text: str
    modell: str
    tokens_ein: int = 0
    tokens_aus: int = 0
    tokens_denken: int = 0
    tokens_cache: int = 0
    dauer_ms: int = 0
    versuche: int = 1
    roh: dict = field(default_factory=dict)

    def json(self) -> dict:
        """Antwort als JSON-Objekt (die Rollen verlangen JSON); Codeblock-Zaeune werden entfernt."""
        t = self.text.strip()
        if t.startswith("```"):
            t = t.split("\n", 1)[1] if "\n" in t else t
            t = t.rsplit("```", 1)[0]
        return json.loads(t)


class AnbieterFehler(RuntimeError):
    def __init__(self, text: str, code: int = 0):
        super().__init__(text)
        self.code = code


def _tls() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    try:
        import certifi
        ctx.load_verify_locations(certifi.where())
    except ImportError:
        pass
    return ctx


class Gemini:
    name = "gemini"

    def __init__(self, schluessel: str, zeit_s: int = 300, versuche: int = 2, oeffnen=None):
        if not schluessel:
            raise AnbieterFehler("GEMINI_API_KEY fehlt (in .env oder als Umgebungsvariable)")
        self.schluessel, self.zeit_s, self.versuche = schluessel, zeit_s, versuche
        self._oeffnen = oeffnen or (lambda anfrage, zeit: urllib.request.urlopen(anfrage, timeout=zeit, context=_tls()))

    def antworten(self, modell: str, system: str, text: str, json_antwort: bool = True) -> Antwort:
        koerper = {"systemInstruction": {"parts": [{"text": system}]},
                   "contents": [{"role": "user", "parts": [{"text": text}]}],
                   "generationConfig": {"temperature": 0.2, **({"responseMimeType": "application/json"} if json_antwort else {})}}
        daten = json.dumps(koerper).encode("utf-8")
        beginn = time.monotonic()
        for versuch in range(1, self.versuche + 2):
            anfrage = urllib.request.Request(GEMINI_URL.format(modell=modell), data=daten, method="POST",
                                             headers={"Content-Type": "application/json", "x-goog-api-key": self.schluessel})
            try:
                with self._oeffnen(anfrage, self.zeit_s) as r:
                    roh = json.loads(r.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as err:
                inhalt = err.read().decode("utf-8", "replace")[:300]
                if err.code in (429, 500, 502, 503, 504) and versuch <= self.versuche:
                    time.sleep(min(30, 3 * 2 ** versuch))
                    continue
                raise AnbieterFehler(f"Gemini HTTP {err.code}: {inhalt}", err.code) from None
            except (urllib.error.URLError, TimeoutError) as err:
                if versuch <= self.versuche:
                    time.sleep(min(30, 2 ** versuch))
                    continue
                raise AnbieterFehler(f"Gemini nicht erreichbar: {err}") from None
        teile = ((roh.get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
        text_aus = "".join(t.get("text", "") for t in teile if not t.get("thought"))
        if not text_aus:
            grund = (roh.get("candidates") or [{}])[0].get("finishReason") or roh.get("promptFeedback")
            raise AnbieterFehler(f"Gemini ohne Antwort ({grund})")
        u = roh.get("usageMetadata") or {}
        return Antwort(text=text_aus, modell=roh.get("modelVersion") or modell, tokens_ein=u.get("promptTokenCount", 0),
                       tokens_aus=u.get("candidatesTokenCount", 0), tokens_denken=u.get("thoughtsTokenCount", 0),
                       tokens_cache=u.get("cachedContentTokenCount", 0),
                       dauer_ms=round((time.monotonic() - beginn) * 1000), versuche=versuch, roh=u)


class Attrappe:
    """Antwortet aus einer Liste (Pruefungen ohne Netz und ohne Schluessel); zaehlt Zeichen/4 als Tokens."""
    name = "attrappe"

    def __init__(self, antworten: list):
        self.vorrat, self.anfragen = list(antworten), []

    def antworten(self, modell: str, system: str, text: str, json_antwort: bool = True) -> Antwort:
        self.anfragen.append({"modell": modell, "system": system, "text": text})
        if not self.vorrat:
            raise AnbieterFehler("Attrappe: keine Antwort mehr")
        a = self.vorrat.pop(0)
        text_aus = a if isinstance(a, str) else json.dumps(a, ensure_ascii=False)
        return Antwort(text=text_aus, modell=modell, tokens_ein=len(system + text) // 4, tokens_aus=len(text_aus) // 4)
