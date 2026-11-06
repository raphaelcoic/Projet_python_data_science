import requests
import geopandas as gpd

URL = "https://services.sandre.eaufrance.fr/geo/topage2019"
PARAMS = {
    "SERVICE": "WFS",
    "VERSION": "2.0.0",
    "REQUEST": "GetFeature",
    "TYPENAMES": "sa:BassinVersantTopographique_FXX_Topage2019",
    "COUNT": 7000,  # une seule requête : la pagination de ce service perd des zones sans erreur
    "OUTPUTFORMAT": "application/json; subtype=geojson",
    "SRSNAME": "EPSG:2154",
}


def recuperer_zones_hydro():
    """Récupère les 6 190 zones hydrographiques de France métropolitaine (BD TOPAGE, Sandre).

    Renvoie un GeoDataFrame avec code_zone, nom_zone, surface_zone_ha et geometry (EPSG:2154).
    """
    reponse = requests.get(URL, params=PARAMS, timeout=300)
    reponse.raise_for_status()
    zones = gpd.GeoDataFrame.from_features(reponse.json(), crs="EPSG:2154")
    zones = zones.rename(columns={"CdOH": "code_zone", "TopoOH": "nom_zone"})
    zones["surface_zone_ha"] = zones.area / 10000
    return zones[["code_zone", "nom_zone", "surface_zone_ha", "geometry"]]
