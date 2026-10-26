import pandas as pd

from src.hubeau.liste_departements import liste_departements
from src.hubeau.recuperer_analyses import recuperer_analyses

CHEMIN_MOLECULES = "data/reference/molecules.csv"


def recuperer_toutes_analyses():
    """Récupère les analyses des molécules de molecules.csv dans les rivières des 96 départements, de 2015 à 2022."""
    molecules = pd.read_csv(CHEMIN_MOLECULES, dtype={"code_sandre": str})
    resultats = []
    for dep in liste_departements():
        for code_sandre in molecules["code_sandre"]:
            resultats.append(recuperer_analyses(dep, code_sandre))
    return pd.concat(resultats, ignore_index=True)
