from pathlib import Path

import py7zr
import requests

NOM = "RPG_2-2__GPKG_LAMB93_FXX_2023-01-01"
URL = f"https://data.geopf.fr/telechargement/download/RPG/{NOM}/{NOM}.7z"


def recuperer_rpg_ign(dossier="data/raw/rpg_ign"):
    """Télécharge et décompresse l'archive nationale du RPG 2023 publiée par l'IGN.

    dossier : dossier où ranger l'archive (2,75 Go) et son contenu décompressé.
    L'archive contient un GeoPackage des parcelles (Lambert 93, France métropolitaine avec la Corse).
    Renvoie le chemin du GeoPackage des parcelles.
    """
    dossier = Path(dossier)
    archive = dossier / f"{NOM}.7z"
    if not archive.exists():
        dossier.mkdir(parents=True, exist_ok=True)
        with requests.get(URL, stream=True, timeout=300) as reponse:
            reponse.raise_for_status()
            with open(archive.with_suffix(".tmp"), "wb") as f:
                for bloc in reponse.iter_content(chunk_size=1 << 20):
                    f.write(bloc)
        archive.with_suffix(".tmp").replace(archive)
    if not list(dossier.rglob("*.gpkg")):
        with py7zr.SevenZipFile(archive) as fichier_7z:
            fichier_7z.extractall(dossier)
    return max(dossier.rglob("*.gpkg"), key=lambda chemin: chemin.stat().st_size)
