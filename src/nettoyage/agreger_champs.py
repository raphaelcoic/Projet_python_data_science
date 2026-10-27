CLE = ["code_dep", "code_groupe_culture"]


def agreger_champs(parcelles):
    """Agrège les parcelles du RPG au département × groupe de cultures (surfaces en hectares).

    parcelles : parcelles d'un millésime, par exemple data/processed/rpg/rpg_2023_national.parquet
    (colonnes code_dep, code_groupe, libelle_groupe, surface_ha).
    Renvoie un DataFrame avec les colonnes de champs.parquet.
    """
    champs = parcelles.groupby(["code_dep", "code_groupe", "libelle_groupe"], as_index=False).agg(
        surface_ha=("surface_ha", "sum"),
    )
    return champs.rename(columns={
        "code_groupe": "code_groupe_culture",
        "libelle_groupe": "libelle_groupe_culture",
    })
