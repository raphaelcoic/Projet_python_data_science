"""
Fusion des fichiers départementaux du RPG en un fichier Parquet national unique
par millésime, allégé du polygone complet (`geometry`) mais enrichi du point de
référence intérieur de chaque parcelle (`point_reference`, calculé via
`GeoSeries.representative_point()`), et filtré sur le périmètre d'étude
(France métropolitaine continentale : hors DROM et hors Corse).

Fichier généré par défaut : data/processed/rpg/rpg_{annee}_national.parquet
"""

from __future__ import annotations

import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import geopandas as gpd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import shapely

from src.agriculture.constantes_rpg import (
    COLONNE_POINT_REFERENCE,
    COLONNES_TABULAIRES_RPG,
    DEPARTEMENTS_EXCLUS_DEFAUT,
    DOSSIER_RPG,
)
from src.agriculture.dossier_millesime_rpg import dossier_millesime_rpg


def _adapter_metadonnees_geoparquet_point(
    meta: dict[bytes, bytes] | None,
    nom_colonne_point: str = COLONNE_POINT_REFERENCE,
) -> dict[bytes, bytes]:
    """
    Met à jour les métadonnées GeoParquet (`b'geo'`) pour remplacer la colonne
    polygonale `geometry` par la colonne ponctuelle `point_reference` (Point EPSG:4326),
    afin que `geopandas.read_parquet()` et `pyarrow.parquet.read_table()` fonctionnent
    tous deux nativement.
    """
    nouvelles_meta = dict(meta or {})
    if b"geo" in nouvelles_meta:
        try:
            geo_dict = json.loads(nouvelles_meta[b"geo"].decode("utf-8"))
            cols_geo = geo_dict.get("columns", {})
            ancien_meta_geom = cols_geo.get("geometry") or next(iter(cols_geo.values()), {})
            nouveau_meta_point = {
                "encoding": "WKB",
                "geometry_types": ["Point"],
            }
            if "crs" in ancien_meta_geom:
                nouveau_meta_point["crs"] = ancien_meta_geom["crs"]
            geo_dict["primary_column"] = nom_colonne_point
            geo_dict["columns"] = {nom_colonne_point: nouveau_meta_point}
            nouvelles_meta[b"geo"] = json.dumps(geo_dict).encode("utf-8")
            return nouvelles_meta
        except Exception:
            pass
    return {k: v for k, v in nouvelles_meta.items() if k != b"geo"}


def _charger_departement_avec_point_reference(
    fichier: Path,
    colonnes_tabulaires: list[str],
    ajouter_point_reference: bool = True,
    nom_colonne_point: str = COLONNE_POINT_REFERENCE,
) -> pa.Table:
    """
    Lit un fichier Parquet départemental, calcule le point de référence de chaque
    parcelle avec la méthode `GeoSeries.representative_point()` de GeoPandas, et
    retourne une Table PyArrow allégée du polygone `geometry`.
    """
    noms_dispo = pq.read_schema(fichier).names
    cols_a_lire = [c for c in colonnes_tabulaires if c in noms_dispo]

    if ajouter_point_reference and "geometry" in noms_dispo:
        t = pq.read_table(fichier, columns=[*cols_a_lire, "geometry"])
        wkb_polygones = t["geometry"].to_numpy(zero_copy_only=False)
        gs_polygones = gpd.GeoSeries.from_wkb(wkb_polygones, crs=4326)
        pts_ref = gs_polygones.representative_point()
        wkb_points = shapely.to_wkb(pts_ref.to_numpy())

        t_sans_poly = t.drop(["geometry"])
        t_finale = t_sans_poly.append_column(
            nom_colonne_point,
            pa.array(wkb_points, type=pa.binary()),
        )
        return t_finale.replace_schema_metadata(
            _adapter_metadonnees_geoparquet_point(t.schema.metadata, nom_colonne_point)
        )

    t = pq.read_table(fichier, columns=cols_a_lire)
    meta = {k: v for k, v in (t.schema.metadata or {}).items() if k != b"geo"}
    return t.replace_schema_metadata(meta)


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
    ajouter_point_reference: bool = True,
    ecraser: bool = True,
    max_workers: int | None = None,
    verbose: bool = True,
) -> Path:
    """
    Fusionne les fichiers Parquet départementaux d'un millésime (`rpg{annee}/rpg_{annee}_{dep}.parquet`)
    en un seul fichier Parquet national (sans le polygone `geometry`, avec `point_reference`
    calculé via `representative_point()`, et hors Corse/DROM).

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
        Colonnes tabulaires à conserver avant ajout de `point_reference`.
        Par défaut : les 12 colonnes de `COLONNES_TABULAIRES_RPG`.
    ajouter_point_reference : bool
        Si `True` (défaut), calcule et ajoute `point_reference` via `representative_point()`
        de GeoPandas pour chaque parcelle.
    ecraser : bool
        Si `False` et que le fichier de sortie existe déjà, il n'est pas recalculé.
    max_workers : int | None
        Nombre de threads pour le calcul parallèle des points de référence par département.
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

    if max_workers is None:
        max_workers = min(8, os.cpu_count() or 4)

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        tables = list(
            ex.map(
                lambda item: _charger_departement_avec_point_reference(
                    item[1],
                    colonnes_cibles,
                    ajouter_point_reference=ajouter_point_reference,
                ),
                fichiers_retenus,
            )
        )

    meta_ref = tables[0].schema.metadata
    table_nationale = pa.concat_tables(tables, promote_options="default")
    if meta_ref:
        table_nationale = table_nationale.replace_schema_metadata(meta_ref)

    sortie.parent.mkdir(parents=True, exist_ok=True)
    tmp = sortie.with_suffix(".parquet.tmp")
    pq.write_table(table_nationale, tmp, compression="snappy")
    tmp.replace(sortie)

    if verbose:
        duree = time.time() - t0
        taille_mo = sortie.stat().st_size / (1024 * 1024)
        surf_totale = _somme_surface(table_nationale)
        print(
            f"[RPG {annee}] Fusion + representative_point() terminée en {duree:.2f} s -> {sortie}\n"
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
