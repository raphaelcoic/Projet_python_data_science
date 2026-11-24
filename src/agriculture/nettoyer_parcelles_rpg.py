def nettoyer_parcelles_rpg(parcelles):
    """Retire les doublons et les parcelles de surface nulle.

    parcelles : DataFrame avec les colonnes id_parcelle et surface_ha.
    Dans l'archive 2023, aucun identifiant n'est en double, et environ 8 500 parcelles ont
    une surface déclarée de 0 ha (miettes de moins de 0,005 ha, surtout du groupe 28 « Divers »).
    Renvoie le DataFrame nettoyé.
    """
    parcelles = parcelles.drop_duplicates(subset="id_parcelle")
    return parcelles[parcelles["surface_ha"] > 0]
