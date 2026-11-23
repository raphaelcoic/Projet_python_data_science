from pathlib import Path

import py7zr
import requests

URL = "https://data.geopf.fr/telechargement/download/RPG/{nom}/{nom}.7z"


def telecharger_archive_ign(nom, dossier):
    """Télécharge et décompresse une archive du RPG publiée par l'IGN, si ce n'est pas déjà fait.

    nom : nom de l'archive, par exemple "RPG_2-2__GPKG_LAMB93_FXX_2023-01-01".
    dossier : dossier où ranger l'archive et son contenu décompressé.
    Renvoie le dossier décompressé (il porte le nom de l'archive).
    """
    dossier = Path(dossier)
    archive = dossier / f"{nom}.7z"
    if not archive.exists():
        dossier.mkdir(parents=True, exist_ok=True)
        with requests.get(URL.format(nom=nom), stream=True, timeout=300) as reponse:
            reponse.raise_for_status()
            with open(archive.with_suffix(".tmp"), "wb") as f:
                for bloc in reponse.iter_content(chunk_size=1 << 20):
                    f.write(bloc)
        archive.with_suffix(".tmp").replace(archive)
    if not (dossier / nom).exists():
        with py7zr.SevenZipFile(archive) as fichier_7z:
            fichier_7z.extractall(dossier)
    return dossier / nom
