from functools import lru_cache

import geopandas as gpd

from src.agriculture.constantes_rpg import CHEMIN_CACHE_CONTOURS_DEP, COUCHE_DEP_ATTRIB
from src.agriculture.requete_wfs import requete_wfs
from src.agriculture.schema_couche_wfs import schema_couche_wfs


@lru_cache(maxsize=None)
def recuperer_departements_ign(couche: str = COUCHE_DEP_ATTRIB) -> gpd.GeoDataFrame:
    """
    Contours ADMIN-EXPRESS des départements (métropole + DROM), en EPSG:4326.

    couche : COUCHE_DEP_ATTRIB (précise, mise en cache dans data/processed/rpg/)
             ou COUCHE_DEP_FILTRE (très simplifiée, pour découper les requêtes).
    Renvoie un GeoDataFrame avec code_dep, nom_dep et geometry.
    """
    if couche == COUCHE_DEP_ATTRIB and CHEMIN_CACHE_CONTOURS_DEP.exists():
        try:
            gdf_cache = gpd.read_parquet(CHEMIN_CACHE_CONTOURS_DEP)
            _ = gdf_cache.sindex
            return gdf_cache
        except Exception:
            pass

    geom_champ, _ = schema_couche_wfs(couche)
    r = requete_wfs(
        {
            "REQUEST": "GetFeature",
            "TYPENAMES": couche,
            "OUTPUTFORMAT": "application/json",
            "PROPERTYNAME": f"code_insee,nom_officiel,{geom_champ}",
            "COUNT": 200,
        },
        timeout=300,
    )
    gdf = gpd.GeoDataFrame.from_features(r.json()["features"], crs=4326)
    gdf = gdf.rename(columns={"code_insee": "code_dep", "nom_officiel": "nom_dep"})[
        ["code_dep", "nom_dep", "geometry"]
    ]
    if couche == COUCHE_DEP_ATTRIB:
        try:
            CHEMIN_CACHE_CONTOURS_DEP.parent.mkdir(parents=True, exist_ok=True)
            gdf.to_parquet(CHEMIN_CACHE_CONTOURS_DEP, index=False)
        except Exception:
            pass
    _ = gdf.sindex  # pré-construit l'index spatial une seule fois
    return gdf
