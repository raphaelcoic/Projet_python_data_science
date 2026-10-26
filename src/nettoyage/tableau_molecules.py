def tableau_molecules(eau):
    """Indicateurs nationaux sur toute la période, une ligne par molécule.

    eau : table eau.parquet avec la colonne molecule (jointure avec molecules.csv).
    """
    tableau = eau.assign(
        somme_concentrations=eau["concentration_moyenne_ugl"] * eau["nb_analyses"]
    ).groupby("molecule").agg(
        nb_analyses=("nb_analyses", "sum"),
        nb_quantifications=("nb_quantifications", "sum"),
        nb_depassements=("nb_depassements", "sum"),
        somme_concentrations=("somme_concentrations", "sum"),
        concentration_max_ugl=("concentration_max_ugl", "max"),
    )
    tableau["taux_quantification"] = tableau["nb_quantifications"] / tableau["nb_analyses"]
    tableau["part_depassements"] = tableau["nb_depassements"] / tableau["nb_analyses"]
    tableau["concentration_moyenne_ugl"] = tableau["somme_concentrations"] / tableau["nb_analyses"]
    return tableau[
        ["nb_analyses", "taux_quantification", "part_depassements",
         "concentration_moyenne_ugl", "concentration_max_ugl"]
    ].sort_values("taux_quantification", ascending=False)
