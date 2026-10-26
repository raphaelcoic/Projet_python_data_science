def taux_par_departement(eau, molecule):
    """Taux de quantification d'une molécule par département, sur toute la période.

    eau : table eau.parquet avec la colonne molecule (jointure avec molecules.csv).
    Renvoie un DataFrame avec code_dep et taux_quantification.
    """
    somme = eau[eau["molecule"] == molecule].groupby("code_dep", as_index=False)[
        ["nb_quantifications", "nb_analyses"]
    ].sum()
    somme["taux_quantification"] = somme["nb_quantifications"] / somme["nb_analyses"]
    return somme[["code_dep", "taux_quantification"]]
