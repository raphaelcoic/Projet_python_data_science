import requests
import geopandas as gpd

from src.geo.liste_departements import liste_departements

URL = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"


def recuperer_departements():
    """Récupère les contours simplifiés des 94 départements du périmètre (métropole continentale, hors Corse).

    Renvoie un GeoDataFrame avec code_dep, nom_dep et geometry (EPSG:4326).
    """
    reponse = requests.get(URL, timeout=60)
    reponse.raise_for_status()
    departements = gpd.GeoDataFrame.from_features(reponse.json(), crs="EPSG:4326")
    departements = departements.rename(columns={"code": "code_dep", "nom": "nom_dep"})
    return departements[departements["code_dep"].isin(liste_departements())].reset_index(drop=True)
