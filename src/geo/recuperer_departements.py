import geopandas as gpd

from src.geo.liste_departements import liste_departements

URL = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"


def recuperer_departements(avec_corse=False):
    """Récupère les contours simplifiés des 94 départements du périmètre (sans la Corse).

    avec_corse : True pour ajouter la Corse-du-Sud (2A) et la Haute-Corse (2B),
    utile pour décrire le RPG, qui couvre aussi la Corse.
    Renvoie un GeoDataFrame avec code_dep, nom_dep et geometry (EPSG:4326).
    """
    departements = gpd.read_file(URL).rename(columns={"code": "code_dep", "nom": "nom_dep"})
    codes = liste_departements() + (["2A", "2B"] if avec_corse else [])
    return departements[departements["code_dep"].isin(codes)]
