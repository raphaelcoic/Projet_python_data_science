import requests
import pandas as pd

URL = "https://hubeau.eaufrance.fr/api/v1/hydrobio/indices"
CODES_INDICES = "7613,5856,7036"  # I2M2 (invertébrés), IBD (diatomées), IPR (poissons)
FIELDS = (
    "code_station_hydrobio,code_departement,date_prelevement,"
    "code_indice,resultat_indice,code_qualification"
)
TAILLE_MAX = 10000  # taille de page maximale de l'API, assez pour un département


def recuperer_indices(code_dep):
    """Récupère les indices biologiques (I2M2, IBD, IPR) des rivières d'un département, de 2013 à 2023.

    code_dep : code du département en texte sur 2 caractères ("01", "28", "95").
    Renvoie un DataFrame avec une ligne par indice calculé (station × date × indice).
    """
    params = {
        "code_departement": code_dep,
        "code_indice": CODES_INDICES,
        "date_debut_prelevement": "2013-01-01",
        "date_fin_prelevement": "2023-12-31",
        "size": TAILLE_MAX,
        "fields": FIELDS,
    }
    reponse = requests.get(URL, params=params)
    while not reponse.ok:  # l'API renvoie parfois une erreur 503 qui passe quand on relance
        reponse = requests.get(URL, params=params)
    return pd.DataFrame(reponse.json()["data"]).drop(columns="geometry")  # geometry est renvoyée même hors de fields
