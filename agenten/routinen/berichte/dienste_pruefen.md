# Bericht: Routine `dienste_pruefen`

**Datum:** 2026-11-25  
**Zweig:** `agy/routine-dienste_pruefen` (Basis: `origin/main` @ `d875a8e`)

## Was geprüft

Ausführung auf dem Rechner des Nutzers im Worktree `gt-routine`:

```text
C:\Users\HP\Geo_Agent\GroundTwin\.venv\Scripts\python.exe scripts/dienste_pruefen.py
Python 3.13.0 · Windows 11 · OpenSSL 3.0.15 3 Sep 2024 · certifi 2026.10.23
```

Geprüft wurden alle 57 Einträge aus `services/geodaten/geodaten/dienste.json`: **57 ok**, **0 Fehler** (Rückgabewert `0`, `alle Dienste erreichbar`).

*Hinweis zu weiteren Einträgen (`ok` nach `scripts/dienste_pruefen.py:43-44`):* Die Portale `NI` (`portal-bohrungen`, `nibis.lbeg.de`: HTTP 401), `HB-DGM` (`portal-dgm`, `geoportal.bremen.de`: HTTP 404) und `HB-LOD2` (`portal-gebaeude`, `geoportal.bremen.de`: HTTP 404) antworten mit gültigem TLS-Zertifikat und zählen im Skript als erreichbar.

## Dienste mit Fehler

Keine – alle 57 Dienste waren erreichbar.

## Vergleich mit dem letzten Bericht

Im letzten Bericht vom `2026-11-23` fiel `DE-BGR-WMS` (Deutschland, Bohrungen / `wms-kopf`, `services.bgr.de`) wegen `[WinError 10061]` aus. In diesem Lauf antwortet `DE-BGR-WMS` wieder regulär (`35 KB in 0.2 s`).  
Damit fällt kein Dienst zweimal hintereinander aus („Issue vorschlagen“ entfällt).

## Was geändert

- Aktualisiert: `agenten/routinen/berichte/dienste_pruefen.md`
- Unverändert: `services/geodaten/geodaten/dienste.json` (gemäß Regel)

## Offen

- Keine offenen Störungen; `DE-BGR-WMS` hat sich gegenüber `2026-11-23` erholt.
