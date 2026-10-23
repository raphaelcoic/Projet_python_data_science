import requests
import pandas as pd

URL = "https://hubeau.eaufrance.fr/api/v2/qualite_rivieres/station_pc"
FIELDS = (
    "code_station,libelle_station,code_departement,"
    "code_cours_eau,"
    "longitude,latitude,date_creation,date_arret"
)
TAILLE_MAX = 20000  # taille de page maximale de l'API (le plus gros département, l'Isère, a 954 stations)


def recuperer_stations(code_dep):
    """Récupère les stations de mesure de la qualité des rivières d'un département.

    code_dep : code du département en texte sur 2 caractères ("01", "28", "2A").
    Renvoie un DataFrame avec une ligne par station.
    """
    params = {
        "code_departement": code_dep,
        "size": TAILLE_MAX,
        "fields": FIELDS,
    }
    reponse = requests.get(URL, params=params, timeout=120)
    reponse.raise_for_status()
    return pd.DataFrame(reponse.json()["data"])