import re
from functools import lru_cache

from src.agriculture.requete_wfs import requete_wfs


@lru_cache(maxsize=None)
def schema_couche_wfs(couche: str) -> tuple[str, tuple[str, ...]]:
    """Retourne (nom du champ géométrie, noms des champs attributaires) d'une couche WFS."""
    xsd = requete_wfs({"REQUEST": "DescribeFeatureType", "TYPENAMES": couche}).text
    elements = re.findall(r'<xsd:element[^>]*name="([^"]+)"[^>]*type="([^"]+)"', xsd)
    geom = next(n for n, t in elements if t.startswith("gml:"))
    champs = tuple(
        n for n, t in elements
        if not t.startswith("gml:") and ":" in t and n != couche.split(":")[1]
    )
    return geom, champs
