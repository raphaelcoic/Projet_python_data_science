from pathlib import Path

import requests

RELEASE = "donnees-v1"
URL = f"https://github.com/raphaelcoic/Projet_python_data_science/releases/download/{RELEASE}"


def recuperer_release(nom, dossier="data/processed"):
    """Télécharge un fichier de la release donnees-v1, si ce n'est pas déjà fait.

    nom : nom du fichier dans la release, par exemple "parcelles_zones_hydro.parquet".
    dossier : dossier où le ranger.
    Seuls les fichiers qui prennent plus de 5 minutes à calculer sont dans la release.
    Renvoie le chemin local du fichier.
    """
    chemin = Path(dossier) / nom
    if not chemin.exists():
        chemin.parent.mkdir(parents=True, exist_ok=True)
        with requests.get(f"{URL}/{nom}", stream=True, timeout=300) as reponse:
            reponse.raise_for_status()
            with open(chemin.with_suffix(".tmp"), "wb") as f:
                for bloc in reponse.iter_content(chunk_size=1 << 20):
                    f.write(bloc)
        chemin.with_suffix(".tmp").replace(chemin)
    return chemin
