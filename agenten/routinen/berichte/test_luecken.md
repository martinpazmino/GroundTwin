# Bericht: Routine `test_luecken`

**Datum:** 2026-11-22  
**Zweig:** `agy/routine-test_luecken` (Basis: `origin/main`)

## Issue vorschlagen

- **`bk.pruefen` wirft `AttributeError` (HTTP 500) statt `ValueError` (HTTP 400) bei ungültiger `zuordnung`:**  
  `services/modeler/baugrundmodell/bodenkennwerte.py:169-172` ruft `(zuordnung or {}).items()` ohne `isinstance(zuordnung, dict)`-Prüfung auf. Wird über `POST /api/projekt/{sig}/aendern` die Operation `{"op": "bodenkennwerte", "zuordnung": ["ungueltig"]}` gesendet (`ui/projekt.py:746`), stürzt der Aufruf mit `AttributeError` (HTTP 500) ab statt mit `ValueError` (HTTP 400, wie bei `homogenbereiche.pruefen` in `services/modeler/baugrundmodell/homogenbereiche.py:62-63`).  
  Abgesichert ohne Code-Änderung als `xfail(strict=True)` in `tests/test_bodenkennwerte_app.py::test_ungueltige_zuordnung_als_400`.

## Was geprüft

- **Gewählte Funktion aus `docs/feature_map.json`:** `einheiten-bodenkennwerte` (`GET /api/projekt/{sig}/bodenkennwerte`, Operation `bodenkennwerte`; bisher nur 2 Tests, `e2e: []`, kein Fehlerfall- und kein Löschtest).
- **Mutationen-Gegenprobe (Schritt 3):** `ui/projekt.py:746` vorübergehend geändert auf `p.bodenkennwerte = bk.pruefen(op.get("zuordnung"), refs) or p.bodenkennwerte` → `pytest tests/test_bodenkennwerte_app.py -k test_zuordnung_entfernen_und_fehlerfaelle` schlug mit `FAILED` fehl (`AssertionError`, Meldung blieb `"Bodenkennwerte aus dem Gutachten: 1 Einheiten zugeordnet"` statt `"Bodenkennwerte entfernt"`). Änderung vollständig zurückgenommen → Test wieder grün.
- **Prüfläufe nach letzter Änderung:**
  - `pytest -v tests/test_bodenkennwerte_app.py`: 5 passed, 1 xfailed.
  - `pytest -q tests/test_hausregeln.py tests/test_funktionskarte.py`: 16 passed.
  - `python -m agenten doku`: 78 Dateien, 0 Fehler.

## Was geändert

- `tests/test_bodenkennwerte_app.py`:
  - `test_zuordnung_entfernen_und_fehlerfaelle`: prüft `GET /api/projekt/nichtda/bodenkennwerte` (`404`), Setzen und Entfernen (`zuordnung: None` → `"Bodenkennwerte entfernt"`, kein `CPset_Bodenkennwerte_Gutachten` mehr im neu gebauten IFC) sowie Leeren bei ausschließlich unbekannten Verweisen.
  - `test_ungueltige_zuordnung_als_400`: `xfail(strict=True)` für nicht-dict `zuordnung` (`400` erwartet, aktuell `500`).
- `docs/feature_map.json`: `tests/test_bodenkennwerte_app.py::test_zuordnung_entfernen_und_fehlerfaelle` in `einheiten-bodenkennwerte.beweis.tests` ergänzt.

## Was offen ist

- Issue für die Typprüfung in `services/modeler/baugrundmodell/bodenkennwerte.py:169-172` anlegen/beheben (`isinstance(zuordnung, dict)` → `ValueError`, dann `xfail` entfernen).
- Für `einheiten-bodenkennwerte` gibt es weiterhin keine E2E-Prüfung in `scripts/check_app.mjs` (`e2e: []`).
