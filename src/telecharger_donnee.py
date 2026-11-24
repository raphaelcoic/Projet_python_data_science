import subprocess
import warnings
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
       (droits d'écriture sur le dépôt). Si le dépôt échoue, le fichier reste en local et un
       avertissement le signale.
    """
    chemin = Path(chemin)
    if chemin.exists() and not recalculer:
        return chemin
    chemin.parent.mkdir(parents=True, exist_ok=True)
    if not recalculer:
        reponse = requests.get(f"{URL}/{chemin.name}", timeout=300)
        if reponse.ok:
            chemin.write_bytes(reponse.content)
            return chemin
    if creer is None:
        raise FileNotFoundError(f"{chemin.name} n'est ni en local ni dans la release {RELEASE}, et aucune fonction creer n'est donnée.")
    creer().to_parquet(chemin, index=False)
    try:  # --clobber : remplace la copie de la release
        subprocess.run(["gh", "release", "upload", RELEASE, str(chemin), "--clobber"], check=True)
    except (OSError, subprocess.CalledProcessError):  # gh absent, pas connecté ou sans droits d'écriture
        warnings.warn(f"{chemin.name} est créé en local mais n'a pas été déposé dans la release {RELEASE}.")
    return chemin
