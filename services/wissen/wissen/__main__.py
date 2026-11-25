"""python -m wissen [groesse ...]: Katalog pruefen und zeigen, was mit diesen Groessen rechenbar ist."""
import json
import sys

from . import katalog, planen, pruefen

fehler = pruefen()
print(f"{len(katalog())} Eintraege, " + ("Katalog in Ordnung" if not fehler else f"{len(fehler)} Fehler"))
for f in fehler:
    print("  -", f)
if len(sys.argv) > 1:
    print(json.dumps(planen(sys.argv[1:]), ensure_ascii=False, indent=1))
sys.exit(1 if fehler else 0)
