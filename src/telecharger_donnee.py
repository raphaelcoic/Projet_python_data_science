from pathlib import Path

import requests

URL = "https://github.com/raphaelcoic/Projet_python_data_science/releases/download/donnees-v1"


def telecharger_donnee(chemin):
    """Télécharge un fichier depuis la release donnees-v1 s'il est absent en local.

    chemin : emplacement local du fichier, par exemple "data/geo/zones_hydro.parquet".
    Renvoie ce chemin, à passer ensuite à read_parquet.
    """
    chemin = Path(chemin)
    if not chemin.exists():
        reponse = requests.get(f"{URL}/{chemin.name}", timeout=300)
        reponse.raise_for_status()
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_bytes(reponse.content)
    return chemin
