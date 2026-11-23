import subprocess
from pathlib import Path

import requests

RELEASE = "donnees-v1"
URL = f"https://github.com/raphaelcoic/Projet_python_data_science/releases/download/{RELEASE}"


def telecharger_donnee(chemin, creer=None, recalculer=False):
    """Renvoie le chemin local d'un fichier de données, à passer ensuite à read_parquet.

    chemin : emplacement local du fichier, par exemple "data/geo/zones_hydro.parquet".
    creer : fonction sans argument qui renvoie un DataFrame ou un GeoDataFrame.
    recalculer : True pour régénérer le fichier avec creer() et remplacer sa copie dans la release.
    1. Si le fichier existe en local, on le prend.
    2. Sinon, on le télécharge depuis la release donnees-v1.
    3. S'il n'y est pas, on le crée avec creer(), puis on le dépose dans la release avec gh
       (droits d'écriture sur le dépôt).
    """
    chemin = Path(chemin)
    if chemin.exists() and not recalculer:
        return chemin
    chemin.parent.mkdir(parents=True, exist_ok=True)
    if not recalculer:
        reponse = requests.get(f"{URL}/{chemin.name}")
        if reponse.ok:
            chemin.write_bytes(reponse.content)
            return chemin
    creer().to_parquet(chemin, index=False)
    subprocess.run(["gh", "release", "upload", RELEASE, str(chemin), "--clobber"])  # --clobber : remplace la copie de la release
    return chemin
