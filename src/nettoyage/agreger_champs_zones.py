import geopandas as gpd

CLE = ["code_zone", "code_groupe_culture", "libelle_groupe_culture"]


def agreger_champs_zones(parcelles, zones):
    """Agrège des parcelles du RPG à la zone hydrographique × groupe de cultures (surfaces en hectares).

    parcelles : GeoDataFrame d'un fichier départemental, par exemple data/processed/rpg/rpg2023/rpg_2023_35.parquet.
    zones : GeoDataFrame renvoyé par recuperer_zones_hydro.
    Chaque parcelle va entière dans la zone qui contient son representative_point.
    Renvoie un DataFrame avec code_zone, code_groupe_culture, libelle_groupe_culture et surface_ha.
    """
    points = gpd.GeoDataFrame(
        parcelles[["code_groupe", "libelle_groupe", "surface_ha"]],
        geometry=parcelles.representative_point().to_crs(zones.crs),
    )
    rattachees = points.sjoin(zones[["code_zone", "geometry"]], predicate="within")
    rattachees = rattachees.rename(columns={
        "code_groupe": "code_groupe_culture",
        "libelle_groupe": "libelle_groupe_culture",
    })
    return rattachees.groupby(CLE, as_index=False)["surface_ha"].sum()
