# Routine: Doku-Pflege (CHANGELOG, Links, Doku ↔ Code)

**Erlaubt:** `CHANGELOG.md`, `docs/*.md` (nicht `docs/11_decisions.md` Spalte *Status*, nicht `docs/16_lessons_learned.md`).

1. `python -m agenten doku`: jede gemeldete Stelle beheben (tote Links, fehlende Up/Related, Frontmatter).
2. CHANGELOG: jeder Commit auf main seit dem letzten Lauf, der Verhalten ändert, hat eine Zeile unter [Unreleased]
   (Added/Changed/Fixed, mit Issue oder docs-Verweis). Reine Wartung bleibt draußen.
3. Doku ↔ Code, nur melden oder offensichtlich korrigieren:
   - Pfade, Module, Befehle, die in `docs/` genannt werden, gibt es noch (`git ls-files`).
   - Jede Entscheidung, die in CLAUDE.md oder docs zitiert wird (`D1xx`), steht in `docs/11_decisions.md`.
   - Jede `doku`-Angabe in `docs/feature_map.json` zeigt auf die Datei, die die Funktion wirklich beschreibt.
4. Inhaltliche Widersprüche (zwei Dokumente sagen Verschiedenes): nicht entscheiden, in den Bericht.
5. Regeln 3–6 aus `agenten/routinen/README.md`.
