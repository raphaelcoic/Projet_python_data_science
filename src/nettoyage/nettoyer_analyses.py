CODE_UNITE_UGL = "133"  # code SANDRE de l'unité µg/L
CODE_NON_FAITE = "0"  # code remarque : analyse non faite
CODE_QUANTIFIE = "1"  # code remarque : molécule quantifiée


def nettoyer_analyses(analyses):
    """Nettoie les analyses de rivière brutes renvoyées par recuperer_toutes_analyses.

    Garde les résultats en µg/L, retire les analyses non faites et les doublons,
    puis ajoute annee, quantifie, concentration_ugl (0 si non quantifiée) et milieu.
    Renvoie un DataFrame avec une ligne par analyse.
    """
    analyses = analyses[
        (analyses["code_unite"] == CODE_UNITE_UGL)
        & (analyses["code_remarque"] != CODE_NON_FAITE)
    ].drop_duplicates()  # analyses saisies deux fois dans la base
    analyses["annee"] = analyses["date_prelevement"].str[:4].astype(int)
    analyses["quantifie"] = analyses["code_remarque"] == CODE_QUANTIFIE
    analyses["concentration_ugl"] = analyses["resultat"].where(analyses["quantifie"], 0)
    analyses["milieu"] = "riviere"
    analyses = analyses.rename(columns={"code_parametre": "code_sandre"})
    return analyses[
        ["code_dep", "annee", "milieu", "code_sandre", "code_station",
         "date_prelevement", "quantifie", "concentration_ugl"]
    ]
