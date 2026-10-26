import requests
import geopandas as gpd

URL = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"


def recuperer_departements():
    """Récupère les contours simplifiés des 96 départements de métropole.

    Renvoie un GeoDataFrame avec code_dep, nom_dep et geometry (EPSG:4326).
    """
    reponse = requests.get(URL, timeout=60)
    reponse.raise_for_status()
    departements = gpd.GeoDataFrame.from_features(reponse.json(), crs="EPSG:4326")
    return departements.rename(columns={"code": "code_dep", "nom": "nom_dep"})
