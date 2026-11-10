import geopandas as gpd

from src.agriculture.requete_wfs import requete_wfs

TAILLE_PAQUET = 200


def recuperer_polygones_rpg(ids, annee=2023):
    """Récupère sur le WFS de l'IGN le contour des parcelles du RPG demandées.

    ids : identifiants des parcelles (colonne id_parcelle du fichier national).
    annee : millésime du RPG, entre 2015 et 2024.
    Les parcelles sont demandées par paquets de 200, pour que l'URL reste courte.
    Renvoie un GeoDataFrame (EPSG:4326) avec id_parcelle et geometry, une ligne par parcelle.
    """
    ids = sorted(set(ids))
    objets = []
    for debut in range(0, len(ids), TAILLE_PAQUET):
        paquet = ids[debut:debut + TAILLE_PAQUET]
        reponse = requete_wfs({
            "REQUEST": "GetFeature",
            "TYPENAMES": f"RPG.{annee}:parcelles_graphiques",
            "OUTPUTFORMAT": "application/json",
            "CQL_FILTER": "id_parcel IN (" + ",".join(f"'{i}'" for i in paquet) + ")",
            "PROPERTYNAME": "id_parcel,geom",
            "COUNT": 5000,
        })
        objets += reponse.json()["features"]
    polygones = gpd.GeoDataFrame.from_features(objets, crs=4326)
    polygones = polygones.rename(columns={"id_parcel": "id_parcelle"})
    return polygones.drop_duplicates("id_parcelle")[["id_parcelle", "geometry"]]
