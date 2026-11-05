"""Agententeam fuer die Entwicklung von GroundTwin (docs/24): Claude plant und entscheidet, Gemini-Agenten pruefen und
diagnostizieren ueber die Gemini-API, Antigravity setzt grosse Aufgaben um, wenn der Nutzer sie startet.

Nur ein Entwicklungswerkzeug: das Produkt importiert dieses Paket nie. Agenten haben keine Werkzeuge - sie bekommen
den Kontext gepackt (kontext.py) und geben Text zurueck (Befunde, Aenderungen); Aenderungen landen nur in einem
git-Worktree, in den Arbeitsstand kommen sie nur mit `python -m agenten uebernehmen <id>` (Claudes Freigabe).
"""
