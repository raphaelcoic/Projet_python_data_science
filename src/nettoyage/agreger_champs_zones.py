import pandas as pd

CLE = ["code_zone", "code_groupe_culture", "libelle_groupe_culture"]
COLONNES = ["code_zone", "code_groupe", "libelle_groupe", "surface_ha"]


def agreger_champs_zones(parcelles, zones, polygones):
    """Agrège les parcelles du RPG à la zone hydrographique × groupe de cultures (surfaces en hectares).

    parcelles : GeoDataFrame de data/processed/rpg/rpg_2023_national.parquet, dont la géométrie
    point_reference est le representative_point de chaque parcelle.
    zones : GeoDataFrame renvoyé par recuperer_zones_hydro.
    polygones : GeoDataFrame renvoyé par recuperer_polygones_rpg, contour des grandes parcelles.
    Une grande parcelle est partagée entre les zones qu'elle touche, au prorata de la surface.
    Les autres vont entières dans la zone qui contient leur point.
    Renvoie un DataFrame avec les colonnes de champs_zones.parquet.
    """
    parcelles = parcelles.drop_duplicates("id_parcelle").to_crs(zones.crs)
    a_decouper = parcelles["id_parcelle"].isin(polygones["id_parcelle"])

    entieres = parcelles[~a_decouper].sjoin(zones[["code_zone", "geometry"]], predicate="within")

    attributs = pd.DataFrame(parcelles.loc[a_decouper].drop(columns="point_reference"))
    contours = polygones.merge(attributs, on="id_parcelle").to_crs(zones.crs)
    contours.geometry = contours.make_valid()
    contours["surface_contour"] = contours.area
    morceaux = contours.overlay(zones[["code_zone", "geometry"]], keep_geom_type=True)
    morceaux["surface_ha"] = morceaux["surface_ha"] * morceaux.area / morceaux["surface_contour"]

    toutes = pd.concat([entieres[COLONNES], morceaux[COLONNES]])
    toutes = toutes.rename(columns={
        "code_groupe": "code_groupe_culture",
        "libelle_groupe": "libelle_groupe_culture",
    })
    return toutes.groupby(CLE, as_index=False)["surface_ha"].sum()
