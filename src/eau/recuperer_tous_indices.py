from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from src.geo.liste_departements import liste_departements
from src.eau.recuperer_indices import recuperer_indices

REQUETES_SIMULTANEES = 8  # environ 1 min 15 pour les 94 départements, contre 10 min un par un


def recuperer_tous_indices():
    """Récupère les indices biologiques des rivières des 94 départements de métropole continentale, de 2013 à 2023.

    Les départements sont demandés 8 à la fois.
    """
    with ThreadPoolExecutor(REQUETES_SIMULTANEES) as executeur:
        resultats = list(executeur.map(recuperer_indices, liste_departements()))
    return pd.concat(resultats, ignore_index=True)
