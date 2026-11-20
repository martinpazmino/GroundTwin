# Routine: Regel-Audit (Prosa → Prüfung, docs/31 §5.4)

**Erlaubt:** `docs/31_agent_guardrails.md` (Abschnitt *Regel-Audit* am Ende), der Bericht. Keine Tests ändern
(`tests/test_hausregeln.py` ist geschützt; neue Prüfungen schreibt Claude nach deinem Vorschlag).

1. Nimm jede Regel aus `CLAUDE.md` (Working rules, App/model/viewer) und `docs/16_lessons_learned.md` (P, E, G, L, W, X …).
2. Ordne sie ein: **Prüfung** (nenne den Test, der sie erzwingt: `tests/test_hausregeln.py::…`, Modultest, CI-Schritt),
   **prüfbar, aber Prosa** (schlage die Prüfung in zwei Sätzen vor: was gesucht wird, welche Meldung), **nur Urteil**
   (braucht einen Menschen, z. B. „allgemeine Regeln statt Ausnahmen je PDF“).
3. Tabelle *Regel-Audit* in docs/31 aktualisieren (Regel, Quelle, Einordnung, Test oder Vorschlag). Höchstens drei neue
   Vorschläge je Lauf, die mit dem größten Nutzen zuerst.
4. Prüfe zusätzlich, ob eine `BESTAND`-Liste in `tests/test_hausregeln.py` einen Eintrag hat, der nicht mehr nötig ist
   (der Test `test_bestand_der_importe_ist_noch_noetig` sagt es); dann im Bericht nennen.
5. Regeln 3–6 aus `agenten/routinen/README.md`.
