import pandas as pd

from src.hubeau.liste_departements import liste_departements
from src.hubeau.recuperer_indices import recuperer_indices


def recuperer_tous_indices():
    """Récupère les indices biologiques des rivières des 94 départements de métropole continentale, de 2013 à 2023."""
    resultats = []
    for dep in liste_departements():
        resultats.append(recuperer_indices(dep))
    return pd.concat(resultats, ignore_index=True)
