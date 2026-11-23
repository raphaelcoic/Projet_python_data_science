
from pathlib import Path

import requests


URL = (
    "https://www.data.gouv.fr/api/1/datasets/r/"
    "6f664bd4-f27d-4e33-8ca7-c197c6adf217"
)

NOM_FICHIER = (
    "quantite-totale-de-produit-phytosanitaire-achetee-en-france-departement.csv"
)


def recuperer_pesticides(dossier="data/raw"):
    """Télécharge le fichier CSV des achats de produits phytosanitaires.

    Si le fichier existe déjà, il est réutilisé.
    Renvoie le chemin local du fichier CSV.
    """
    dossier = Path(dossier)
    fichier = dossier / NOM_FICHIER

    if fichier.exists():
        return fichier

    dossier.mkdir(parents=True, exist_ok=True)
    temporaire = fichier.with_suffix(".csv.tmp")

    try:
        with requests.get(URL, stream=True, timeout=300) as reponse:
            reponse.raise_for_status()

            with open(temporaire, "wb") as f:
                for bloc in reponse.iter_content(chunk_size=1 << 20):
                    if bloc:
                        f.write(bloc)

        temporaire.replace(fichier)

    finally:
        if temporaire.exists():
            temporaire.unlink()

    return fichier
