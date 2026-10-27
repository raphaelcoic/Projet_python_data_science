from pathlib import Path

import pyarrow.parquet as pq

from src.agriculture.constantes_rpg import COLONNES_PROJET_RPG


def filtrer_colonnes_parquet(
    source: Path,
    destination: Path,
    colonnes: list[str] = COLONNES_PROJET_RPG,
) -> bool:
    """
    Lit un fichier GeoParquet existant, conserve uniquement `colonnes` dans l'ordre
    exact du projet (en préservant les métadonnées GeoParquet) et l'écrit dans `destination`.
    Retourne `True` si une réécriture/déplacement a eu lieu.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    noms_actuels = pq.read_schema(source).names

    meme_emplacement = source.resolve() == destination.resolve()
    colonnes_identiques = noms_actuels == list(colonnes)

    if meme_emplacement and colonnes_identiques:
        return False

    colonnes_presentes = [c for c in colonnes if c in noms_actuels]
    table = pq.read_table(source, columns=colonnes_presentes)

    tmp = destination.with_suffix(".parquet.tmp")
    pq.write_table(table, tmp)
    tmp.replace(destination)

    if not meme_emplacement and source.exists():
        source.unlink()
    return True
