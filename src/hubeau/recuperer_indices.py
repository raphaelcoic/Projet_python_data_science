import requests
import pandas as pd

URL = "https://hubeau.eaufrance.fr/api/v1/hydrobio/indices"
CODES_INDICES = "7613,5856,7036"  # I2M2 (invertébrés), IBD (diatomées), IPR (poissons)
FIELDS = (
    "code_station_hydrobio,code_departement,date_prelevement,"
    "code_indice,resultat_indice,code_qualification"
)
TAILLE_MAX = 10000  # taille de page maximale de cette API (un département fait au plus ~1 800 indices sur 2015-2022)
NB_ESSAIS = 4  # l'API fait des timeouts aléatoires qui passent quand on relance


def recuperer_indices(code_dep):
    """Récupère les indices biologiques (I2M2, IBD, IPR) des rivières d'un département, de 2015 à 2022.

    code_dep : code du département en texte sur 2 caractères ("01", "28", "2A").
    Renvoie un DataFrame avec une ligne par indice calculé (station × date × indice).
    """
    params = {
        "code_departement": code_dep,
        "code_indice": CODES_INDICES,
        "date_debut_prelevement": "2015-01-01",
        "date_fin_prelevement": "2022-12-31",
        "size": TAILLE_MAX,
        "fields": FIELDS,
    }
    for essai in range(NB_ESSAIS):
        try:
            reponse = requests.get(URL, params=params, timeout=120)
            break
        except requests.exceptions.Timeout:
            print(f"Timeout pour le département {code_dep} (essai {essai + 1}/{NB_ESSAIS})")
            if essai == NB_ESSAIS - 1:
                raise
    reponse.raise_for_status()
    return pd.DataFrame(reponse.json()["data"]).drop(columns="geometry")  # geometry est renvoyée même hors de fields
