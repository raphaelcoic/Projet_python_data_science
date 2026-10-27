NOMS_INDICES = {"7613": "I2M2", "5856": "IBD", "7036": "IPR"}
CODE_CORRECTE = "1"  # code qualification : donnée correcte
VALEUR_ABSENTE = 999  # valeur codée de l'IPR quand l'indice n'est pas calculable


def nettoyer_indices(indices):
    """Nettoie les indices biologiques bruts renvoyés par recuperer_tous_indices.

    Garde les valeurs qualifiées « correctes », retire les valeurs codées 999,
    puis ajoute annee et le nom de l'indice.
    Renvoie un DataFrame avec une ligne par indice calculé.
    """
    indices = indices[
        (indices["code_qualification"] == CODE_CORRECTE)
        & (indices["resultat_indice"] < VALEUR_ABSENTE)
    ].drop_duplicates()
    indices = indices.rename(columns={
        "code_departement": "code_dep",
        "code_station_hydrobio": "code_station",
        "resultat_indice": "valeur",
    })
    indices["annee"] = indices["date_prelevement"].str[:4].astype(int)
    indices["indice"] = indices["code_indice"].map(NOMS_INDICES)
    return indices[
        ["code_dep", "annee", "indice", "code_station", "date_prelevement", "valeur"]
    ]
