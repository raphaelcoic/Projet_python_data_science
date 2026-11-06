CLE = ["code_zone", "code_groupe_culture", "libelle_groupe_culture"]


def agreger_champs_zones(parcelles, zones):
    """Agrège les parcelles du RPG à la zone hydrographique × groupe de cultures (surfaces en hectares).

    parcelles : GeoDataFrame de data/processed/rpg/rpg_2023_national.parquet, dont la géométrie
    point_reference est le representative_point de chaque parcelle.
    zones : GeoDataFrame renvoyé par recuperer_zones_hydro.
    Chaque parcelle va entière dans la zone qui contient son point.
    Renvoie un DataFrame avec les colonnes de champs_zones.parquet.
    """
    rattachees = parcelles.to_crs(zones.crs).sjoin(zones[["code_zone", "geometry"]], predicate="within")
    rattachees = rattachees.rename(columns={
        "code_groupe": "code_groupe_culture",
        "libelle_groupe": "libelle_groupe_culture",
    })
    return rattachees.groupby(CLE, as_index=False)["surface_ha"].sum()
