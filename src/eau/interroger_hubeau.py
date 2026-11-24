import time

import pandas as pd
import requests

ESSAIS = 5
DELAI = 120  # secondes : certains départements mettent plus de 20 s à répondre


def interroger_hubeau(url, params):
    """Interroge une API Hub'Eau et renvoie les lignes de la réponse dans un DataFrame.

    L'API renvoie parfois une erreur 5xx ou ne répond pas à temps : on relance, jusqu'à 5 essais
    en attendant un peu plus à chaque fois. Une erreur 4xx (requête invalide) s'arrête tout de suite.
    Lève une erreur si la réponse ne contient pas toutes les lignes (count) : il faudrait paginer.
    """
    for essai in range(ESSAIS):
        if essai:
            time.sleep(5 * essai)
        try:
            reponse = requests.get(url, params=params, timeout=DELAI)
        except (requests.ConnectionError, requests.Timeout):
            if essai == ESSAIS - 1:
                raise
            continue
        if reponse.status_code < 500:
            break
    reponse.raise_for_status()
    contenu = reponse.json()
    if contenu["count"] > len(contenu["data"]):
        raise ValueError(f"{url} {params} : {contenu['count']} lignes, {len(contenu['data'])} reçues. Augmenter size ou paginer.")
    return pd.DataFrame(contenu["data"]).drop(columns="geometry", errors="ignore")  # geometry est renvoyée même hors de fields
