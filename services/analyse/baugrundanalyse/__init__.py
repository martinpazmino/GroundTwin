"""Ground Analysis (docs/27): Kreuzprobe, Unsicherheit, virtuelle Bohrung, Erkundungsvorschlag und Grundwasserflaeche
zum Schichtmodell (baugrundmodell).

Liest das Modell, aendert nie die Bohrungen. Der Modellierer liegt in services/modeler.
"""
from .grundwasser import grundwasser
from .kreuzprobe import kreuzprobe
from .unsicherheit import unsicherheit
from .unsicherheit import zusammenfassung as unsicherheit_zusammenfassung
from .virtuell import virtuelle_bohrung
from .vorschlag import vorschlaege

__all__ = ["grundwasser", "kreuzprobe", "unsicherheit", "unsicherheit_zusammenfassung", "virtuelle_bohrung", "vorschlaege", "analyse"]


def analyse(m, laeufe: int = 100, sigma_exakt: float | None = None, seed: int = 1) -> dict:
    """Kreuzprobe und Unsicherheit in einem Aufruf; als JSON schreibbar (ohne die Felder je Knoten)."""
    from .unsicherheit import SIGMA_EXAKT, zusammenfassung
    k = kreuzprobe(m)
    u = unsicherheit(m, k, laeufe=laeufe, sigma_exakt=SIGMA_EXAKT if sigma_exakt is None else sigma_exakt, seed=seed)
    return {"kreuzprobe": {x: v for x, v in k.items() if not x.startswith("_")}, "unsicherheit": zusammenfassung(u)}
