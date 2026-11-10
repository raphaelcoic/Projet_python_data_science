import subprocess
from pathlib import Path

import requests

RELEASE = "donnees-v1"
URL = f"https://github.com/raphaelcoic/Projet_python_data_science/releases/download/{RELEASE}"


def telecharger_donnee(chemin, creer=None):
    """Renvoie le chemin local d'un fichier de données, à passer ensuite à read_parquet.

    chemin : emplacement local du fichier, par exemple "data/geo/zones_hydro.parquet".
    creer : fonction sans argument qui renvoie un DataFrame ou un GeoDataFrame.
    Si le fichier manque en local, il est téléchargé depuis la release donnees-v1.
    S'il n'est pas non plus dans la release, il est créé avec creer(), puis déposé
    dans la release avec gh (droits d'écriture sur le dépôt).
    """
    chemin = Path(chemin)
    if chemin.exists():
        return chemin
    chemin.parent.mkdir(parents=True, exist_ok=True)
    reponse = requests.get(f"{URL}/{chemin.name}", timeout=300)
    if reponse.status_code != 404 or creer is None:
        reponse.raise_for_status()
        chemin.write_bytes(reponse.content)
        return chemin
    creer().to_parquet(chemin, index=False)
    subprocess.run(["gh", "release", "upload", RELEASE, str(chemin), "--clobber"], check=True)
    return chemin
