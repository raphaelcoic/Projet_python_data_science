import requests
import pandas as pd

URL = "https://hubeau.eaufrance.fr/api/v2/qualite_rivieres/analyse_pc"
FIELDS = (
    "code_station,date_prelevement,code_parametre,"
    "resultat,code_unite,code_remarque"
)
TAILLE_MAX = 20000  # taille de page maximale de l'API (un département × une molécule sur 2015-2022 fait au plus ~5 600 analyses)
NB_ESSAIS = 4  # l'API fait des timeouts aléatoires qui passent quand on relance


def recuperer_analyses(code_dep, code_sandre):
    """Récupère les analyses d'une molécule dans les rivières d'un département, de 2015 à 2022.

    code_dep : code du département en texte sur 2 caractères ("01", "28", "2A").
    code_sandre : code SANDRE de la molécule en texte ("1506").
    Renvoie un DataFrame avec une ligne par analyse.
    """
    params = {
        "code_departement": code_dep,
        "code_parametre": code_sandre,
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
            print(f"Timeout pour le département {code_dep}, molécule {code_sandre} (essai {essai + 1}/{NB_ESSAIS})")
            if essai == NB_ESSAIS - 1:
                raise
    reponse.raise_for_status()
    analyses = pd.DataFrame(reponse.json()["data"])
    analyses["code_dep"] = code_dep  # l'API ne renvoie pas le département
    return analyses
