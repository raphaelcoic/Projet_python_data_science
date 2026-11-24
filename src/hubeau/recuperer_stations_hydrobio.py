from src.hubeau.interroger_hubeau import interroger_hubeau

URL = "https://hubeau.eaufrance.fr/api/v1/hydrobio/stations_hydrobio"
FIELDS = "code_station_hydrobio,libelle_station_hydrobio,libelle_cours_eau,longitude,latitude"
TAILLE_MAX = 5000  # un département fait au plus quelques centaines de stations


def recuperer_stations_hydrobio(code_dep):
    """Récupère les stations où sont calculés les indices biologiques d'un département.

    code_dep : code du département en texte sur 2 caractères ("01", "28", "95").
    Renvoie un DataFrame avec une ligne par station.
    """
    params = {
        "code_departement": code_dep,
        "size": TAILLE_MAX,
        "fields": FIELDS,
    }
    return interroger_hubeau(URL, params).rename(columns={
        "code_station_hydrobio": "code_station",
        "libelle_station_hydrobio": "libelle_station",
        "libelle_cours_eau": "nom_cours_eau",
    })
