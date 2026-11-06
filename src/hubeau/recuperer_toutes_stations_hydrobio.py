import pandas as pd

from src.geo.liste_departements import liste_departements
from src.hubeau.recuperer_stations_hydrobio import recuperer_stations_hydrobio


def recuperer_toutes_stations_hydrobio():
    """Récupère les stations hydrobiologiques des 94 départements de métropole continentale."""
    resultats = []
    for dep in liste_departements():
        resultats.append(recuperer_stations_hydrobio(dep))
    return pd.concat(resultats, ignore_index=True)
