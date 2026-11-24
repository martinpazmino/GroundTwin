# Bericht: Routine `dienste_pruefen`

**Datum:** 2026-11-23  
**Zweig:** `agy/routine-dienste_pruefen` (Basis: `origin/main` @ `4820105`)

## Was geprüft

Ausführung auf dem Rechner des Nutzers im Worktree `gt-routine`:

```text
C:\Users\HP\Geo_Agent\GroundTwin\.venv\Scripts\python.exe scripts/dienste_pruefen.py
Python 3.13.0 · Windows 11 · OpenSSL 3.0.15 3 Sep 2024 · certifi 2026.10.23
```

Geprüft wurden alle 57 Einträge aus `services/geodaten/geodaten/dienste.json`: **56 ok**, **1 Fehler** (Rückgabewert `1`).

## Dienste mit Fehler

| ID | Land | Art | Host | Fehler (Art & Meldung) | Seit wann |
|---|---|---|---|---|---|
| `DE-BGR-WMS` | Deutschland (`dienste.json:89-142`) | Bohrungen (`wms-kopf`) | `services.bgr.de` | Verbindung abgewiesen / nicht erreichbar (kein DNS-/TLS-/HTTP-Code): `nicht erreichbar ([WinError 10061] No connection could be made because the target machine actively refused it)` | `2026-11-23` (erster Bericht; letztes Prüfdatum in `dienste.json:108`: `2026-11-09`) |

*Hinweis zu weiteren Einträgen (`ok` nach `scripts/dienste_pruefen.py:43-44`):* Die Portale `NI` (`portal-bohrungen`, `nibis.lbeg.de`: HTTP 401), `HB-DGM` (`portal-dgm`, `geoportal.bremen.de`: HTTP 404) und `HB-LOD2` (`portal-gebaeude`, `geoportal.bremen.de`: HTTP 404) antworten mit gültigem TLS-Zertifikat und zählen im Skript als erreichbar.

## Vergleich mit dem letzten Bericht

Kein früherer Bericht unter `agenten/routinen/berichte/dienste_pruefen.md` vorhanden (Ersterstellung). Daher fällt kein Dienst nachweislich zweimal hintereinander aus („Issue vorschlagen“ entfällt für diesen Lauf).

## Was geändert

- Neu angelegt: `agenten/routinen/berichte/dienste_pruefen.md`
- Unverändert: `services/geodaten/geodaten/dienste.json` (gemäß Regel)

## Offen

- `DE-BGR-WMS` (`https://services.bgr.de/wms/geologie/gbl/`) beim nächsten Lauf erneut prüfen; falls weiterhin nicht erreichbar, Issue vorschlagen.
