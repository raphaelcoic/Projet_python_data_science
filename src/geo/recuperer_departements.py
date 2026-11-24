import geopandas as gpd

from src.geo.liste_departements import liste_departements

URL = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"


def recuperer_departements():
    """Récupère les contours simplifiés des 94 départements du périmètre (sans la Corse).

    Renvoie un GeoDataFrame avec code_dep, nom_dep et geometry (EPSG:4326).
    """
    departements = gpd.read_file(URL).rename(columns={"code": "code_dep", "nom": "nom_dep"})
    return departements[departements["code_dep"].isin(liste_departements())]
