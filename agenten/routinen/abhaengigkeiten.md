# Routine: Abhängigkeiten (nur Bericht)

**Erlaubt:** nur der Bericht. `constraints.txt` und `package-lock.json` nie ändern (D81: Claude erneuert sie nach
Prüfung mit `pip freeze`).

1. Python: in einer frischen venv `pip install -r requirements.txt -c constraints.txt`, dann `pip list --outdated` und
   `pip-audit` (falls vorhanden; sonst `pip install pip-audit` nur in dieser venv).
2. Web: in `apps/web` `npm ci`, `npm outdated`, `npm audit --omit=dev`.
3. Bericht: Sicherheitsmeldungen zuerst (Paket, Version, CVE, behoben ab), dann Hauptversionen, die fehlen.
   web-ifc bleibt bei 0.0.77 (X9): nur melden, wenn es eine Sicherheitsmeldung gibt.
4. Neue Abhängigkeit oder neue Lizenz in einer Unterabhängigkeit: mit Lizenz nennen (`THIRD_PARTY_LICENSES.md`, AGPL).
5. Bericht auf den Zweig `agy/routine-abhaengigkeiten` (Regeln 1, 4, 6 aus `agenten/routinen/README.md`).
