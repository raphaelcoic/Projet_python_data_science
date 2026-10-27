import pandas as pd

from src.geo.liste_departements import liste_departements
from src.hubeau.recuperer_stations import recuperer_stations


def recuperer_toutes_stations():
    """Récupère les stations de qualité des rivières des 94 départements de métropole continentale."""
    resultats = []
    for dep in liste_departements():
        resultats.append(recuperer_stations(dep))
    return pd.concat(resultats, ignore_index=True)