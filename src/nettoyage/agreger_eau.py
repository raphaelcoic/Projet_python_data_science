CLE = ["code_dep", "annee", "indice"]


def agreger_eau(indices):
    """Agrège les indices biologiques nettoyés au département × année × indice.

    indices : DataFrame renvoyé par nettoyer_indices.
    Renvoie un DataFrame avec les colonnes de eau.parquet.
    """
    return indices.groupby(CLE, as_index=False).agg(
        nb_stations=("code_station", "nunique"),
        nb_prelevements=("valeur", "size"),
        valeur_moyenne=("valeur", "mean"),
        valeur_mediane=("valeur", "median"),
    )
