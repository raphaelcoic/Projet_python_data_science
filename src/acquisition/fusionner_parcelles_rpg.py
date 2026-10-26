"""
Fusion des fichiers départementaux du RPG en un fichier Parquet national unique
par millésime (ex. 2013 et 2023), allégé de la colonne géométrique (`geometry`)
et filtré sur le périmètre d'étude (France métropolitaine continentale :
hors DROM `971–976` et hors Corse `2A`, `2B`).

Fichiers générés par défaut :
    data/processed/rpg/
    ├── rpg_2013_national.parquet
    └── rpg_2023_national.parquet

Exemples
--------
>>> from src.acquisition.fusionner_parcelles_rpg import (
...     fusionner_millesime_rpg,
...     fusionner_tous_millesimes_rpg,
... )
>>> fusionner_tous_millesimes_rpg(annees=[2013, 2023])
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

# Permet d'exécuter ce fichier directement (ex. bouton Run dans VS Code ou `python src/acquisition/fusionner_parcelles_rpg.py`)
_RACINE_PROJET = Path(__file__).resolve().parents[2]
if str(_RACINE_PROJET) not in sys.path:
    sys.path.insert(0, str(_RACINE_PROJET))

from src.acquisition.get_parcelles_rpg import COLONNES_PROJET_RPG
from src.acquisition.sauvegarder_parcelles_rpg import dossier_millesime_rpg

# Départements exclus du périmètre d'étude (DROM + Corse)
DEPARTEMENTS_EXCLUS_DEFAUT: tuple[str, ...] = (
    "2A",
    "2B",
    "971",
    "972",
    "973",
    "974",
    "976",
)

# Les 12 variables tabulaires retenues (sans la colonne `geometry` pour alléger la taille)
COLONNES_TABULAIRES_RPG: list[str] = [
    col for col in COLONNES_PROJET_RPG if col != "geometry"
]


def _nettoyer_metadonnees_geo(table: pa.Table) -> pa.Table:
    """
    Supprime la clé de métadonnée GeoParquet (`b'geo'`) lorsqu'on retire la colonne
    `geometry`, afin d'obtenir un fichier Parquet tabulaire standard propre.
    """
    meta = table.schema.metadata
    if not meta or b"geo" not in meta:
        return table
    nouvelles_meta = {k: v for k, v in meta.items() if k != b"geo"}
    return table.replace_schema_metadata(nouvelles_meta)


def fusionner_millesime_rpg(
    annee: int,
    dossier_racine: str | Path = "data/processed/rpg",
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
        raise FileNotFoundError(
            f"Le sous-dossier du millésime {annee} est introuvable : {dossier_annee}"
        )

    if fichier_sortie is None:
        sortie = racine / f"rpg_{annee}_national.parquet"
    else:
        sortie = Path(fichier_sortie)

    if sortie.exists() and not ecraser:
        if verbose:
            taille_mo = sortie.stat().st_size / (1024 * 1024)
            print(
                f"[RPG {annee}] Fichier national déjà présent : {sortie} ({taille_mo:.1f} Mo)",
                flush=True,
            )
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
        raise RuntimeError(
            f"Aucun fichier départemental retenu pour le millésime {annee} dans {dossier_annee}"
        )

    tables: list[pa.Table] = []
    for _, f in fichiers_retenus:
        noms_dispo = pq.read_schema(f).names
        cols_a_lire = [c for c in colonnes_cibles if c in noms_dispo]
        t = pq.read_table(f, columns=cols_a_lire)
        tables.append(_nettoyer_metadonnees_geo(t))

    table_nationale = pa.concat_tables(tables, promote_options="default")
    table_nationale = _nettoyer_metadonnees_geo(table_nationale)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    tmp = sortie.with_suffix(".parquet.tmp")
    pq.write_table(table_nationale, tmp, compression="snappy")
    tmp.replace(sortie)

    if verbose:
        duree = time.time() - t0
        taille_mo = sortie.stat().st_size / (1024 * 1024)
        surf_totale = pc_sum_surface(table_nationale)
        print(
            f"[RPG {annee}] Fusion terminée en {duree:.2f} s -> {sortie}\n"
            f"           Départements retenus : {len(fichiers_retenus)} "
            f"(exclus : {', '.join(sorted(exclus_set))})\n"
            f"           Parcelles / îlots    : {table_nationale.num_rows:,}\n"
            f"           Surface totale (SAU) : {surf_totale:,.1f} ha ({surf_totale / 1e6:.2f} M ha)\n"
            f"           Variables ({ len(table_nationale.column_names) })       : "
            f"{', '.join(table_nationale.column_names)}\n"
            f"           Taille du fichier    : {taille_mo:.1f} Mo",
            flush=True,
        )

    return sortie


def pc_sum_surface(table: pa.Table) -> float:
    """Calcule rapidement la somme de `surface_ha` sur une Table PyArrow."""
    import pyarrow.compute as pc

    if "surface_ha" not in table.column_names or table.num_rows == 0:
        return 0.0
    val = pc.sum(table["surface_ha"]).as_py()
    return float(val) if val is not None else 0.0


def fusionner_tous_millesimes_rpg(
    annees: list[int] | tuple[int, ...] = (2013, 2023),
    dossier_racine: str | Path = "data/processed/rpg",
    departements_exclus: tuple[str, ...] | list[str] = DEPARTEMENTS_EXCLUS_DEFAUT,
    colonnes: list[str] | None = None,
    ecraser: bool = True,
    verbose: bool = True,
) -> dict[int, Path]:
    """
    Génère les fichiers Parquet nationaux (sans `geometry`, hors Corse et DROM)
    pour l'ensemble des millésimes spécifiés dans `annees`.
    """
    resultats: dict[int, Path] = {}
    for annee in annees:
        resultats[annee] = fusionner_millesime_rpg(
            annee=annee,
            dossier_racine=dossier_racine,
            departements_exclus=departements_exclus,
            colonnes=colonnes,
            ecraser=ecraser,
            verbose=verbose,
        )
    return resultats


if __name__ == "__main__":
    # Exécution directe : fusionne les fichiers départementaux de 2013 et 2023
    # en deux fichiers Parquet nationaux (hors Corse 2A/2B, hors DROM 971-976 et sans `geometry`).
    DOSSIER_RPG = _RACINE_PROJET / "data" / "processed" / "rpg"
    MILLESIMES_PROJET = (2013, 2023)

    fusionner_tous_millesimes_rpg(
        annees=MILLESIMES_PROJET,
        dossier_racine=DOSSIER_RPG,
        departements_exclus=DEPARTEMENTS_EXCLUS_DEFAUT,
        ecraser=True,
        verbose=True,
    )
