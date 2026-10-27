from __future__ import annotations

import re
from pathlib import Path

from src.agriculture.constantes_rpg import COLONNES_PROJET_RPG, DOSSIER_RPG
from src.agriculture.dossier_millesime_rpg import dossier_millesime_rpg
from src.agriculture.filtrer_colonnes_parquet import filtrer_colonnes_parquet


def organiser_parquets_rpg(
    dossier_racine: str | Path = DOSSIER_RPG,
    verbose: bool = True,
) -> dict[int, list[Path]]:
    """
    Range tous les fichiers `rpg_{annee}_{dep}.parquet` présents dans `dossier_racine`
    (ou déjà dans `rpg20XX/`) vers leur sous-dossier `data/processed/rpg/rpg{annee}/`
    et filtre leurs colonnes pour ne conserver strictement que les 13 variables
    de `COLONNES_PROJET_RPG`.

    Utile une seule fois pour migrer d'anciens fichiers ; `sauvegarder_parcelles_rpg`
    écrit directement au bon endroit. Le fichier `_contours_departements.parquet`
    est laissé à la racine de `data/processed/rpg/`.
    """
    racine = Path(dossier_racine)
    if not racine.exists():
        return {}

    motif = re.compile(r"^rpg_(\d{4})(?:_bio)?_([0-9A-Za-z]+)\.parquet$")
    candidats = list(racine.glob("rpg_*.parquet")) + list(racine.glob("rpg*/rpg_*.parquet"))

    par_annee: dict[int, list[Path]] = {}
    nb_modifies = 0

    for src in sorted(set(candidats)):
        m = motif.match(src.name)
        if not m:
            continue
        annee = int(m.group(1))
        dst = dossier_millesime_rpg(racine, annee) / src.name
        if filtrer_colonnes_parquet(src, dst, COLONNES_PROJET_RPG):
            nb_modifies += 1
        par_annee.setdefault(annee, []).append(dst)

    if verbose:
        for annee, fichiers in sorted(par_annee.items()):
            print(
                f"[RPG {annee}] {len(fichiers)} fichiers organisés et filtrés (13 variables) "
                f"dans {dossier_millesime_rpg(racine, annee)}",
                flush=True,
            )
        print(f"Total fichiers déplacés ou réécrits : {nb_modifies}", flush=True)

    return par_annee
