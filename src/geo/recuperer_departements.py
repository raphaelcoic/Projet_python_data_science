import requests
import geopandas as gpd

URL = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"
CORSE = ["2A", "2B"]


def recuperer_departements():
    """Récupère les contours simplifiés des 94 départements de métropole continentale (hors Corse).

    Renvoie un GeoDataFrame avec code_dep, nom_dep et geometry (EPSG:4326).
    """
    reponse = requests.get(URL, timeout=60)
    reponse.raise_for_status()
    departements = gpd.GeoDataFrame.from_features(reponse.json(), crs="EPSG:4326")
    departements = departements.rename(columns={"code": "code_dep", "nom": "nom_dep"})
    return departements[~departements["code_dep"].isin(CORSE)].reset_index(drop=True)
