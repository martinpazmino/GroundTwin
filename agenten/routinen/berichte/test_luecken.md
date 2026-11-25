# Bericht: Routine `test_luecken`

**Datum:** 2026-11-25  
**Zweig:** `agy/routine-test_luecken` (Basis: `origin/main`)

## Was geprüft

- **Gewählte Funktion aus `docs/feature_map.json`:** `system-betrieb` (`GET /gesund`; zuvor nur 2 Tests, `e2e: []`, davon `test_ganzer_ablauf_mit_nachgebautem_cloudflared` unter Windows übersprungen; `GEO_AGENT_BENUTZER`, fehlerhafte `Authorization`-Köpfe und das Lesen von `GEO_AGENT_*` aus der Umgebung waren nicht geprüft).
- **Mutationen-Gegenprobe (Schritt 3):** `server/api.py:52` vorübergehend geändert auf `name_ok = True` → `pytest -v tests/test_server.py -k test_anmeldung_benutzer_fehlerhafte_koepfe_und_umgebung` schlug mit `FAILED` fehl (`AssertionError: assert 200 == 401` bei `auth=('falsch', 'geheim')`). Änderung vollständig zurückgenommen → Test wieder grün.
- **Prüfläufe nach letzter Änderung:**
  - `pytest -v tests/test_server.py`: 12 passed.
  - `pytest -q tests/test_hausregeln.py tests/test_funktionskarte.py`: 16 passed.
  - `python -m agenten doku`: 81 Dateien, 0 Fehler.

## Was geändert

- `tests/test_server.py` (`test_anmeldung_benutzer_fehlerhafte_koepfe_und_umgebung`): prüft `GET /gesund` ohne Anmeldung, Benutzerprüfung über `GEO_AGENT_BENUTZER` (falscher Benutzer → `401`, falsches Passwort → `401`, gültig → `200`), fehlerhafte `Authorization`-Köpfe (`Bearer`, ungültiges Base64, ungültiges UTF-8, fehlender Doppelpunkt → jeweils `401`), `GEO_AGENT_QUELLCODE` und `GEO_AGENT_MAX_MB` (`413` bei Überschreitung, `400` bei kleinem ungültigem Upload).
- `docs/feature_map.json`: `tests/test_server.py::test_anmeldung_benutzer_fehlerhafte_koepfe_und_umgebung` in `system-betrieb.beweis.tests` ergänzt.

## Was offen ist

- Für `system-betrieb` gibt es weiterhin keine E2E-Prüfung in `scripts/check_app.mjs` (`e2e: []`).
- Das in der vorherigen Runde als `xfail(strict=True)` gemeldete Issue in `services/modeler/baugrundmodell/bodenkennwerte.py:169-172` (Typprüfung `isinstance(zuordnung, dict)`) ist weiterhin offen.
