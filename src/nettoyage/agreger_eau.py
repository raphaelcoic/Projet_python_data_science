SEUIL_UGL = 0.1  # norme eau potable par pesticide, en µg/L
CLE = ["code_dep", "annee", "milieu", "code_sandre"]


def agreger_eau(analyses):
    """Agrège les analyses nettoyées au département × année × milieu × molécule.

    analyses : DataFrame renvoyé par nettoyer_analyses.
    Renvoie un DataFrame avec les colonnes de eau.parquet (voir docs/contrat_donnees.md).
    """
    analyses = analyses.assign(depassement=analyses["concentration_ugl"] > SEUIL_UGL)
    eau = analyses.groupby(CLE, as_index=False).agg(
        nb_stations=("code_station", "nunique"),
        nb_analyses=("code_station", "size"),
        nb_quantifications=("quantifie", "sum"),
        concentration_moyenne_ugl=("concentration_ugl", "mean"),
        concentration_max_ugl=("concentration_ugl", "max"),
        nb_depassements=("depassement", "sum"),
    )
    eau["taux_quantification"] = eau["nb_quantifications"] / eau["nb_analyses"]
    return eau[
        CLE + ["nb_stations", "nb_analyses", "nb_quantifications", "taux_quantification",
               "concentration_moyenne_ugl", "concentration_max_ugl", "nb_depassements"]
    ]
