import requests
import pandas as pd

URL = "https://hubeau.eaufrance.fr/api/v1/hydrobio/stations_hydrobio"
FIELDS = "code_station_hydrobio,libelle_station_hydrobio,libelle_cours_eau,longitude,latitude"
TAILLE_MAX = 5000  # un département fait au plus quelques centaines de stations
NB_ESSAIS = 4  # l'API fait des erreurs réseau aléatoires qui passent quand on relance


def recuperer_stations_hydrobio(code_dep):
    """Récupère les stations où sont calculés les indices biologiques d'un département.

    Ce réseau n'est pas celui de recuperer_stations : environ 10 % des stations ayant
    un indice n'existent que dans cette API.

    code_dep : code du département en texte sur 2 caractères ("01", "28", "95").
    Renvoie un DataFrame avec une ligne par station.
    """
    params = {
        "code_departement": code_dep,
        "size": TAILLE_MAX,
        "fields": FIELDS,
    }
    for essai in range(NB_ESSAIS):
        try:
            reponse = requests.get(URL, params=params, timeout=120)
            break
        except requests.exceptions.RequestException:
            print(f"Erreur réseau pour le département {code_dep} (essai {essai + 1}/{NB_ESSAIS})")
            if essai == NB_ESSAIS - 1:
                raise
    reponse.raise_for_status()
    stations = pd.DataFrame(reponse.json()["data"]).drop(columns="geometry")  # geometry est renvoyée même hors de fields
    return stations.rename(columns={
        "code_station_hydrobio": "code_station",
        "libelle_station_hydrobio": "libelle_station",
        "libelle_cours_eau": "nom_cours_eau",
    })
