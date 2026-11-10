"""Suchpfad: das Paket selbst und der Modellierer (services/modeler)."""
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(HIER), str(HIER.parent / "modeler")]
