import requests
import pandas as pd

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
    reponse = requests.get(URL, params=params)
    while not reponse.ok:  # l'API renvoie parfois une erreur 503 qui passe quand on relance
        reponse = requests.get(URL, params=params)
    stations = pd.DataFrame(reponse.json()["data"]).drop(columns="geometry")  # geometry est renvoyée même hors de fields
    return stations.rename(columns={
        "code_station_hydrobio": "code_station",
        "libelle_station_hydrobio": "libelle_station",
        "libelle_cours_eau": "nom_cours_eau",
    })
