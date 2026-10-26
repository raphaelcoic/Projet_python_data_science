import pandas as pd


def comparer_departement(indices, code_dep):
    """Compare un département à la France, indice par indice.

    indices : indices nettoyés (colonnes code_dep, indice, code_station, valeur).
    Renvoie un DataFrame avec, pour chaque indice, le nombre de stations du département,
    sa médiane, la médiane France et son rang parmi les départements (1 = meilleure qualité).
    """
    medianes = indices.groupby(["code_dep", "indice"])["valeur"].median().unstack()
    rangs = medianes.rank(ascending=False, method="min")
    rangs["IPR"] = medianes["IPR"].rank(method="min")  # pour l'IPR, bas = bonne qualité
    return pd.DataFrame({
        "nb_stations": indices[indices["code_dep"] == code_dep].groupby("indice")["code_station"].nunique(),
        "mediane_departement": medianes.loc[code_dep],
        "mediane_france": indices.groupby("indice")["valeur"].median(),
        "rang": rangs.loc[code_dep],
    })
