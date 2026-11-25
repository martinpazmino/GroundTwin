# Bericht: Routine `doku_pflege`

**Datum:** 2026-11-25  
**Zweig:** `agy/routine-doku_pflege` (Basis: `origin/main` @ `de49a8a`)

## Was geprüft

1. **`python -m agenten doku`:** 81 Markdown-Dateien geprüft (Links, Anker, D/P-Bereiche in `CLAUDE.md`) → `0 Fehler`. Alle `docs/*.md` haben Frontmatter und `Up:`-Verweise (außer `docs/README.md`).
2. **`CHANGELOG.md` gegen Commits auf `origin/main`:** Alle verhaltensändernden Commits seit `0da913a` waren unter `[Unreleased]` erfasst bis auf die Fehlerbehebung in `7918e7f` (`services/modeler/baugrundmodell/bodenkennwerte.py:169-174`, `pruefen()` wirft `ValueError` → HTTP 400 statt 500 bei nicht-dict `zuordnung`, getestet in `tests/test_bodenkennwerte_app.py:108-113`).
3. **Doku ↔ Code:**
   - Alle 109 Entscheidungen (`D1`–`D109`), die in `CLAUDE.md` oder `docs/*.md` zitiert werden, stehen in `docs/11_decisions.md`.
   - Alle 21 Einträge in `docs/feature_map.json` zeigen mit `doku` auf die Datei, die die jeweilige Funktion beschreibt.
   - Genannte Pfade, Module und Befehle in `docs/*.md` gegen `git ls-files` und `python -m agenten --help` geprüft.

## Was geändert

- `CHANGELOG.md:62-65`: unter `[Unreleased]` einen Abschnitt `### Fixed` für `bodenkennwerte` (`ValueError`/HTTP 400 statt 500 aus Commit `7918e7f`) ergänzt.
- `docs/12_public_corpus.md:28,30,49`: `screen_corpus.py` auf den aktuellen Pfad `benchmark/screen_corpus.py` korrigiert.
- `docs/20_lage_pruefung_viewer.md:211-215`: sichtbare Link-Texte (`apps/web/src/main.ts`, `kamera.ts`, `lage.ts`, `rahmen.ts`, `streamlit.ts`) an die bereits aktualisierten Link-Ziele (`../apps/web/src/viewer/viewer.ts`, `kamera.ts`, `lage.ts`, `rahmen.ts`, `kanal.ts`) angeglichen.
- `docs/ARCHITECTURE_BAUGRUNDMODELL.md:820`: sichtbaren Link-Text `apps/web/src/main.ts` an das Link-Ziel `../apps/web/src/viewer/viewer.ts` angeglichen.

## Was offen ist (Widersprüche / nicht entschieden)

- **`docs/29_groundtwin_analysis.md`:** Frontmatter (`status: accepted`, Zeile 6) und §§8.1–8.3 (`A1`–`A3 built`, Zeilen 140–230) widersprechen Zeile 15 (`Decision D108 (proposed)` — in `docs/11_decisions.md` ist `D108` `accepted`), Zeilen 17–18 (`Status: proposed, nothing built`) sowie der Statusspalte in §6 (Zeilen 122–125, z. B. DAUB `not built`, Grundwasserfläche `kinds mixed, #26`).
- **`docs/05_sondierungen.md`:** Zeile 17 (`CPT: design`) und Zeilen 84–85 (`Not wired into the model, IFC, BoreholeML or the app yet (parts 2–4 of #27)`) widersprechen §§6–8 desselben Dokuments (Zeilen 152–238, Teile 2–4 umgesetzt) sowie #28/#29 in `CHANGELOG.md`.
- **`docs/25_laender_dgm_lod2_research.md`:** Tabelle/Fußnote (Zeilen 30–46, 52, 67–68) führen `NI-DGM1`, `NI-LOD2-GML`, `MV-DGM1` als `aktiv: false` und `RP`/`BY`/`MV`/`SN` LoD2 als `geprueft_nicht_aufgenommen`, während der Nachtrag (Zeilen 62–64), `docs/README.md:43` und `services/geodaten/geodaten/dienste.json` alle sieben Dienste als `aktiv: true` (`status: geprueft`) führen.
- **`docs/27_ground_analysis_gempy.md`:** Entwurfstabelle/Phasenliste (Zeilen 218, 231) nennen `vergleich.py` und `orientierung.py` unter `services/analyse/baugrundanalyse/`, während laut §6.3 (Zeilen 329, 337) und `git ls-files` die Orientierung in `implizit.py` liegt und weder `vergleich.py` noch `orientierung.py` existiert. Zudem nennt Zeile 242 den historischen G1-Stand `15` Tests (aktuell 38 `def test_`-Funktionen in `services/analyse/tests/`).
- **`docs/31_agent_guardrails.md`:** Frontmatter nennt `status: proposed` (Zeile 6), obwohl §3 (`Built (2026-11-20)`) und §6 (`Scheduled routines`) umgesetzt sind; Zeile 102 nennt unter `§5 Next steps` das geplante Kommando `python -m agenten app <funktion>` (noch nicht in `agenten/__main__.py`).
- **Abweichende Test-/Prüfzahlen in älteren Schnappschüssen:** `docs/18_layer_modeler.md:24` (`31` Modeler-Tests vs. aktuell 61 `def test_`-Funktionen), `docs/21_app_schritte_normen.md:937-941` (`63` Modeler / `173` App / `55` E2E-Prüfungen Stand 2026-11-05 vs. `docs/31_agent_guardrails.md:32` mit `58` E2E-Prüfungen).
