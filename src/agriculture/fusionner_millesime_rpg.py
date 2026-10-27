"""
Fusion des fichiers départementaux du RPG en un fichier Parquet national unique
par millésime, allégé de la colonne géométrique (`geometry`) et filtré sur le
périmètre d'étude (France métropolitaine continentale : hors DROM et hors Corse).

Fichier généré par défaut : data/processed/rpg/rpg_{annee}_national.parquet
"""

from __future__ import annotations

import re
import time
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from src.agriculture.constantes_rpg import COLONNES_TABULAIRES_RPG, DEPARTEMENTS_EXCLUS_DEFAUT, DOSSIER_RPG
from src.agriculture.dossier_millesime_rpg import dossier_millesime_rpg


def _nettoyer_metadonnees_geo(table: pa.Table) -> pa.Table:
    """
    Supprime la clé de métadonnée GeoParquet (`b'geo'`) lorsqu'on retire la colonne
    `geometry`, afin d'obtenir un fichier Parquet tabulaire standard propre.
    """
    meta = table.schema.metadata
    if not meta or b"geo" not in meta:
        return table
    return table.replace_schema_metadata({k: v for k, v in meta.items() if k != b"geo"})


def _somme_surface(table: pa.Table) -> float:
    """Somme de `surface_ha` sur une Table PyArrow (0 si absente ou vide)."""
    if "surface_ha" not in table.column_names or table.num_rows == 0:
        return 0.0
    val = pc.sum(table["surface_ha"]).as_py()
    return float(val) if val is not None else 0.0


def fusionner_millesime_rpg(
    annee: int,
    dossier_racine: str | Path = DOSSIER_RPG,
    fichier_sortie: str | Path | None = None,
    departements_exclus: tuple[str, ...] | list[str] = DEPARTEMENTS_EXCLUS_DEFAUT,
    colonnes: list[str] | None = None,
    ecraser: bool = True,
    verbose: bool = True,
) -> Path:
    """
    Fusionne les fichiers Parquet départementaux d'un millésime (`rpg{annee}/rpg_{annee}_{dep}.parquet`)
    en un seul fichier Parquet national tabulaire (sans `geometry` et hors Corse/DROM).

    Paramètres
    ----------
    annee : int
        Millésime du RPG à fusionner (ex. 2013, 2023).
    dossier_racine : str | Path
        Dossier racine contenant les sous-dossiers `rpg20XX/`.
    fichier_sortie : str | Path | None
        Chemin du fichier Parquet national de sortie. Par défaut :
        ``data/processed/rpg/rpg_{annee}_national.parquet``.
    departements_exclus : tuple[str, ...] | list[str]
        Codes départements à exclure (par défaut : `2A`, `2B` et DROM `971–976`).
    colonnes : list[str] | None
        Colonnes à conserver. Par défaut : les 12 colonnes de `COLONNES_TABULAIRES_RPG`
        (toutes les variables du projet sauf `geometry`).
    ecraser : bool
        Si `False` et que le fichier de sortie existe déjà, il n'est pas recalculé.
    verbose : bool
        Affiche un bilan détaillé de la fusion (nombre de départements, lignes, surface, taille).
    """
    t0 = time.time()
    racine = Path(dossier_racine)
    dossier_annee = dossier_millesime_rpg(racine, annee)

    if not dossier_annee.exists():
        raise FileNotFoundError(f"Le sous-dossier du millésime {annee} est introuvable : {dossier_annee}")

    sortie = racine / f"rpg_{annee}_national.parquet" if fichier_sortie is None else Path(fichier_sortie)

    if sortie.exists() and not ecraser:
        if verbose:
            taille_mo = sortie.stat().st_size / (1024 * 1024)
            print(f"[RPG {annee}] Fichier national déjà présent : {sortie} ({taille_mo:.1f} Mo)", flush=True)
        return sortie

    colonnes_cibles = list(colonnes) if colonnes is not None else list(COLONNES_TABULAIRES_RPG)
    exclus_set = {str(code).upper() for code in departements_exclus}

    motif = re.compile(rf"^rpg_{annee}_([0-9A-Za-z]+)\.parquet$")
    fichiers_retenus: list[tuple[str, Path]] = []

    for f in sorted(dossier_annee.glob(f"rpg_{annee}_*.parquet")):
        m = motif.match(f.name)
        if not m:
            continue
        code_dep = m.group(1).upper()
        if code_dep in exclus_set:
            continue
        fichiers_retenus.append((code_dep, f))

    if not fichiers_retenus:
        raise RuntimeError(f"Aucun fichier départemental retenu pour le millésime {annee} dans {dossier_annee}")

    tables: list[pa.Table] = []
    for _, f in fichiers_retenus:
        noms_dispo = pq.read_schema(f).names
        cols_a_lire = [c for c in colonnes_cibles if c in noms_dispo]
        tables.append(_nettoyer_metadonnees_geo(pq.read_table(f, columns=cols_a_lire)))

    table_nationale = _nettoyer_metadonnees_geo(pa.concat_tables(tables, promote_options="default"))

    sortie.parent.mkdir(parents=True, exist_ok=True)
    tmp = sortie.with_suffix(".parquet.tmp")
    pq.write_table(table_nationale, tmp, compression="snappy")
    tmp.replace(sortie)

    if verbose:
        duree = time.time() - t0
        taille_mo = sortie.stat().st_size / (1024 * 1024)
        surf_totale = _somme_surface(table_nationale)
        print(
            f"[RPG {annee}] Fusion terminée en {duree:.2f} s -> {sortie}\n"
            f"           Départements retenus : {len(fichiers_retenus)} "
            f"(exclus : {', '.join(sorted(exclus_set))})\n"
            f"           Parcelles / îlots    : {table_nationale.num_rows:,}\n"
            f"           Surface totale (SAU) : {surf_totale:,.1f} ha ({surf_totale / 1e6:.2f} M ha)\n"
            f"           Variables ({len(table_nationale.column_names)})       : "
            f"{', '.join(table_nationale.column_names)}\n"
            f"           Taille du fichier    : {taille_mo:.1f} Mo",
            flush=True,
        )

    return sortie
