import pandas as pd

from src.hubeau.liste_departements import liste_departements
from src.hubeau.recuperer_stations import recuperer_stations


def recuperer_toutes_stations():
    """Récupère les stations de qualité des rivières des 96 départements de métropole."""
    resultats = []
    for dep in liste_departements():
        resultats.append(recuperer_stations(dep))
    return pd.concat(resultats, ignore_index=True)