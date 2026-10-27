"""
Visualisation cartographique des parcelles agricoles du RPG par groupe de cultures
(`libelle_groupe`), pour un département ou pour la France entière.

Compatible avec l'arborescence par millésime `data/processed/rpg/rpg20XX/`
(notamment `rpg2013`, `rpg2023`, `rpg2025`) et le cache des contours départementaux
`data/processed/rpg/_contours_departements.parquet`.

Exemples
--------
>>> from src.visualisation.carte_parcelles_rpg import (
...     tracer_carte_groupes_cultures,
...     tracer_carte_france_groupes_cultures,
... )
>>> tracer_carte_france_groupes_cultures(
...     dossier_parquet="data/processed/rpg",
...     annee=2025,
... )
"""

from __future__ import annotations

import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pyproj
import shapely
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.path import Path as MplPath
from matplotlib.transforms import Affine2D

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.acquisition.get_parcelles_rpg import (
    COUCHE_DEP_ATTRIB,
    DEPARTEMENTS_OUTRE_MER,
    _departements,
)
from src.acquisition.sauvegarder_parcelles_rpg import dossier_millesime_rpg

# Palette qualitative distincte (28 couleurs lisibles pour les groupes de cultures)
PALETTE_GROUPES = [
    "#31a354", "#2b8cbe", "#e34a33", "#feb24c", "#756bb1",
    "#fd8d3c", "#41b6c4", "#dd1c77", "#addd8e", "#636363",
    "#8856a7", "#a6611a", "#018571", "#d7191c", "#2c7bb6",
    "#fdae61", "#abd9e9", "#df65b0", "#74c476", "#9e9ac8",
    "#bdbdbd", "#f768a1", "#bf812d", "#35978f", "#c994c7",
    "#80cdc1", "#dfc27d", "#bababa",
]

# Emprise de repli en Lambert-93 (EPSG:2154) pour la France métropolitaine + Corse
_EMPRISE_METRO_2154 = (99_000.0, 6_049_000.0, 1_243_000.0, 7_111_000.0)


def _racine_rpg(dossier: str | Path) -> Path:
    """
    Si `dossier` est un sous-dossier `rpg20XX`, remonte au dossier parent `data/processed/rpg`
    où est stocké `_contours_departements.parquet`.
    """
    p = Path(dossier)
    if p.name.lower().startswith("rpg20") and len(p.name) == 7:
        return p.parent
    return p


def _charger_contours_departements(
    dossier_cache: str | Path = "data/processed/rpg",
) -> gpd.GeoDataFrame | None:
    """
    Charge les contours départementaux ADMIN-EXPRESS depuis le fichier
    `data/processed/rpg/_contours_departements.parquet` (ou via le WFS en cas d'absence).
    """
    racine = _racine_rpg(dossier_cache)
    cache_path = racine / "_contours_departements.parquet"
    if cache_path.exists():
        try:
            return gpd.read_parquet(cache_path)
        except Exception:
            pass
    try:
        deps = _departements(COUCHE_DEP_ATTRIB)
        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            deps.to_parquet(cache_path, index=False)
        except Exception:
            pass
        return deps
    except Exception:
        return None


def _construire_chemins_groupes(
    geoms: np.ndarray,
    grp_codes: np.ndarray,
    n_groupes: int,
    crs_cible: object = 2154,
) -> tuple[dict[int, MplPath], tuple[float, float, float, float]]:
    """
    Extrait de manière vectorisée (Shapely 2 + PyProj + NumPy) tous les anneaux des
    polygones et construit un unique `matplotlib.path.Path` composite par groupe de
    cultures, par découpage contigu sans copie mémoire.
    """
    order = np.argsort(grp_codes, kind="stable")
    grp_sorted = grp_codes[order]
    geoms_sorted = geoms[order]

    polys, poly_idx = shapely.get_parts(geoms_sorted, return_index=True)
    if len(polys) == 0:
        return {}, (0.0, 0.0, 1.0, 1.0)

    if hasattr(shapely, "orient_polygons"):
        polys = shapely.orient_polygons(polys)
    rings, ring_poly_idx = shapely.get_rings(polys, return_index=True)
    coords, ring_idx = shapely.get_coordinates(rings, return_index=True)
    if len(coords) == 0:
        return {}, (0.0, 0.0, 1.0, 1.0)

    transformer = pyproj.Transformer.from_crs(4326, crs_cible, always_xy=True)
    x, y = transformer.transform(coords[:, 0], coords[:, 1])
    xy = np.column_stack([x, y])

    n_verts = len(xy)
    ring_changes = np.flatnonzero(np.diff(ring_idx)) + 1
    ring_starts = np.concatenate(([0], ring_changes))
    ring_ends = np.concatenate((ring_changes - 1, [n_verts - 1]))

    codes = np.full(n_verts, MplPath.LINETO, dtype=np.uint8)
    codes[ring_starts] = MplPath.MOVETO
    codes[ring_ends] = MplPath.CLOSEPOLY

    vert_grp = grp_sorted[poly_idx[ring_poly_idx[ring_idx]]]
    ids = np.arange(n_groupes, dtype=vert_grp.dtype)
    v_starts = np.searchsorted(vert_grp, ids, side="left")
    v_ends = np.searchsorted(vert_grp, ids, side="right")

    chemins: dict[int, MplPath] = {}
    for g_id in range(n_groupes):
        s, e = int(v_starts[g_id]), int(v_ends[g_id])
        if s < e:
            p = MplPath(xy[s:e], codes[s:e], _interpolation_steps=1)
            p.should_simplify = False
            chemins[g_id] = p

    bounds = (float(x.min()), float(y.min()), float(x.max()), float(y.max()))
    return chemins, bounds


def tracer_carte_groupes_cultures(
    gdf: gpd.GeoDataFrame,
    code_dep: str = "90",
    fichier_sortie: str | Path = "carte_rpg_90_groupes.png",
    afficher_contour_dep: bool = True,
    dpi: int = 220,
) -> Path:
    """
    Génère une carte des parcelles agricoles d'un département colorées par `libelle_groupe`.
    """
    code_dep = str(code_dep).zfill(2)
    sub = gdf[gdf["code_dep"] == code_dep]
    if sub.empty:
        raise ValueError(f"Aucune parcelle trouvée pour le département {code_dep!r}.")

    crs_cible = sub.estimate_utm_crs() if code_dep in DEPARTEMENTS_OUTRE_MER else 2154
    lib_grp = sub["libelle_groupe"].fillna("Non renseigné")

    surfaces_groupes = (
        sub.assign(libelle_groupe=lib_grp)
        .groupby("libelle_groupe")["surface_ha"]
        .sum()
        .sort_values(ascending=False)
    )
    groupes = list(surfaces_groupes.index)
    couleurs = {
        grp: PALETTE_GROUPES[i % len(PALETTE_GROUPES)]
        for i, grp in enumerate(groupes)
    }
    grp_to_id = {grp: i for i, grp in enumerate(groupes)}
    grp_codes = lib_grp.map(grp_to_id).to_numpy(dtype=np.int32)

    chemins, (xmin, ymin, xmax, ymax) = _construire_chemins_groupes(
        sub.geometry.to_numpy(),
        grp_codes,
        len(groupes),
        crs_cible=crs_cible,
    )

    dep_geom = None
    if afficher_contour_dep:
        deps = _charger_contours_departements()
        if deps is not None:
            dep_sub = deps[deps["code_dep"] == code_dep]
            if not dep_sub.empty:
                dep_geom = dep_sub.to_crs(crs_cible)
                b_minx, b_miny, b_maxx, b_maxy = dep_geom.total_bounds
                xmin = min(xmin, float(b_minx))
                ymin = min(ymin, float(b_miny))
                xmax = max(xmax, float(b_maxx))
                ymax = max(ymax, float(b_maxy))

    pad_x = (xmax - xmin) * 0.04
    pad_y = (ymax - ymin) * 0.04
    xmin, xmax = xmin - pad_x, xmax + pad_x
    ymin, ymax = ymin - pad_y, ymax + pad_y

    h_px = max(800, int(10 * dpi))
    w_px = max(800, int(round(h_px * (xmax - xmin) / max(1e-6, ymax - ymin))))
    renderer = RendererAgg(w_px, h_px, dpi)
    gc = renderer.new_gc()
    gc.set_antialiased(True)
    gc.set_linewidth(0.0)

    sx = w_px / (xmax - xmin)
    sy = h_px / (ymax - ymin)
    trans = Affine2D().translate(-xmin, -ymin).scale(sx, sy)

    for g_id, grp in enumerate(groupes):
        path = chemins.get(g_id)
        if path is not None:
            rgba = mcolors.to_rgba(couleurs[grp], alpha=1.0)
            renderer.draw_path(gc, path, trans, rgba)

    img = np.asarray(renderer.buffer_rgba())

    fig, ax = plt.subplots(figsize=(13, 10), facecolor="white")
    ax.set_facecolor("#f8f9fa")

    if dep_geom is not None:
        dep_geom.plot(ax=ax, color="#eef0f2", edgecolor="none", zorder=1)

    ax.imshow(
        img,
        extent=[xmin, xmax, ymin, ymax],
        origin="upper",
        interpolation="none",
        zorder=2,
    )

    if dep_geom is not None:
        dep_geom.plot(ax=ax, facecolor="none", edgecolor="#222222", linewidth=1.2, zorder=3)

    nom_dep = (
        sub["nom_dep"].dropna().iloc[0]
        if "nom_dep" in sub and not sub["nom_dep"].dropna().empty
        else code_dep
    )
    annee = (
        int(sub["annee"].dropna().iloc[0])
        if "annee" in sub and not sub["annee"].dropna().empty
        else 2025
    )
    surf_tot = sub["surface_ha"].sum()

    ax.set_title(
        f"Parcelles agricoles par groupe de cultures — {nom_dep} ({code_dep})\n"
        f"RPG {annee} • {len(sub):,} parcelles • {surf_tot:,.0f} ha déclarés".replace(",", " "),
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    ax.set_axis_off()

    handles = [
        mpatches.Patch(
            color=couleurs[grp],
            label=f"{grp} ({surfaces_groupes[grp]:,.0f} ha)".replace(",", " "),
        )
        for grp in groupes
    ]
    ax.legend(
        handles=handles,
        title="Groupe de cultures (surface déclarée)",
        title_fontsize=10,
        fontsize=8.5,
        loc="center left",
        bbox_to_anchor=(1.01, 0.5),
        frameon=True,
        facecolor="white",
        edgecolor="#cccccc",
    )

    fichier_sortie = Path(fichier_sortie)
    fichier_sortie.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    fig.savefig(fichier_sortie, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return fichier_sortie


def _lire_stats_departement(
    f: Path,
    inclure_drom_legende: bool,
) -> tuple[str, int, pd.Series | None]:
    """Lit uniquement les métadonnées légères d'un fichier Parquet départemental."""
    tbl = pq.read_table(f, columns=["code_dep", "libelle_groupe", "surface_ha"])
    if tbl.num_rows == 0:
        return "", 0, None
    df_meta = tbl.to_pandas()
    code_dep = str(df_meta["code_dep"].iloc[0])
    if not inclure_drom_legende and code_dep in DEPARTEMENTS_OUTRE_MER:
        return code_dep, 0, None
    df_meta["libelle_groupe"] = df_meta["libelle_groupe"].fillna("Non renseigné")
    return code_dep, len(df_meta), df_meta.groupby("libelle_groupe")["surface_ha"].sum()


def _preparer_departement_france(
    f: Path,
    grp_to_id: dict[str, int],
    n_groupes: int,
) -> dict[int, MplPath]:
    """Charge un département métropolitain et construit ses chemins vectoriels en Lambert-93."""
    tbl = pq.read_table(f, columns=["libelle_groupe", "geometry"])
    if tbl.num_rows == 0:
        return {}
    geoms = shapely.from_wkb(tbl["geometry"].to_numpy(zero_copy_only=False))
    lib_grp = tbl["libelle_groupe"].to_pandas().fillna("Non renseigné")
    grp_codes = lib_grp.map(grp_to_id).to_numpy(dtype=np.int32)
    chemins, _ = _construire_chemins_groupes(geoms, grp_codes, n_groupes, crs_cible=2154)
    return chemins


def tracer_carte_france_groupes_cultures(
    dossier_parquet: str | Path = "data/processed/rpg",
    fichier_sortie: str | Path | None = None,
    annee: int = 2025,
    inclure_drom_legende: bool = True,
    dpi: int = 250,
    max_workers: int | None = None,
) -> Path:
    """
    Génère la carte de France entière des parcelles agricoles colorées par `libelle_groupe`
    à partir des fichiers Parquet départementaux situés dans `data/processed/rpg/rpg{annee}/`
    (`rpg_{annee}_{dep}.parquet`).

    L'extraction des anneaux, la projection Lambert-93 et la rastérisation C++ (`RendererAgg`)
    sont vectorisées et parallélisées afin de traiter les ~9,8 millions de parcelles en
    quelques secondes avec une empreinte mémoire bornée.
    """
    dossier_base = Path(dossier_parquet)
    dossier_annee = dossier_millesime_rpg(dossier_base, annee)

    if dossier_annee.exists():
        fichiers = sorted(dossier_annee.glob(f"rpg_{annee}_*.parquet"))
    else:
        fichiers = sorted(dossier_base.glob(f"rpg_{annee}_*.parquet"))

    if not fichiers:
        raise FileNotFoundError(
            f"Aucun fichier rpg_{annee}_*.parquet trouvé dans {dossier_annee} ni dans {dossier_base}"
        )

    if fichier_sortie is None:
        fichier_sortie = Path(f"data/processed/carte_rpg_{annee}_france_groupes.png")

    if max_workers is None:
        max_workers = min(8, os.cpu_count() or 4)

    # 1. Passe légère parallélisée (sans géométrie) pour calculer les surfaces nationales
    stats_list = []
    nb_total = 0
    fichiers_metro: list[Path] = []

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        resultats_meta = list(
            ex.map(lambda f: _lire_stats_departement(f, inclure_drom_legende), fichiers)
        )

    for f, (code_dep, n_rows, serie_surf) in zip(fichiers, resultats_meta):
        if serie_surf is not None:
            nb_total += n_rows
            stats_list.append(serie_surf)
        if code_dep and code_dep not in DEPARTEMENTS_OUTRE_MER:
            fichiers_metro.append(f)

    surfaces_groupes = (
        pd.concat(stats_list)
        .groupby(level=0)
        .sum()
        .sort_values(ascending=False)
    )
    groupes = list(surfaces_groupes.index)
    couleurs = {
        grp: PALETTE_GROUPES[i % len(PALETTE_GROUPES)]
        for i, grp in enumerate(groupes)
    }
    grp_to_id = {grp: i for i, grp in enumerate(groupes)}
    rgba_par_id = [mcolors.to_rgba(couleurs[grp], alpha=1.0) for grp in groupes]

    # 2. Chargement des contours départementaux depuis data/processed/rpg/_contours_departements.parquet
    deps_gdf = _charger_contours_departements(dossier_base)
    deps_metro = None
    if deps_gdf is not None:
        try:
            deps_metro = deps_gdf[~deps_gdf["code_dep"].isin(DEPARTEMENTS_OUTRE_MER)].to_crs(2154)
        except Exception:
            deps_metro = None

    if deps_metro is not None and not deps_metro.empty:
        xmin, ymin, xmax, ymax = (float(v) for v in deps_metro.total_bounds)
    else:
        xmin, ymin, xmax, ymax = _EMPRISE_METRO_2154

    pad_x = (xmax - xmin) * 0.02
    pad_y = (ymax - ymin) * 0.02
    xmin, xmax = xmin - pad_x, xmax + pad_x
    ymin, ymax = ymin - pad_y, ymax + pad_y

    # 3. Rastérisation directe sur tampon C++ RendererAgg partagé (mémoire constante ~60 Mo)
    h_px = max(1200, int(14 * dpi))
    w_px = max(1200, int(round(h_px * (xmax - xmin) / (ymax - ymin))))
    renderer = RendererAgg(w_px, h_px, dpi)
    gc = renderer.new_gc()
    gc.set_antialiased(True)
    gc.set_linewidth(0.0)

    sx = w_px / (xmax - xmin)
    sy = h_px / (ymax - ymin)
    trans = Affine2D().translate(-xmin, -ymin).scale(sx, sy)

    n_groupes = len(groupes)
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        for chemins_dep in ex.map(
            lambda f: _preparer_departement_france(f, grp_to_id, n_groupes),
            fichiers_metro,
        ):
            for g_id, path in chemins_dep.items():
                renderer.draw_path(gc, path, trans, rgba_par_id[g_id])

    img = np.asarray(renderer.buffer_rgba())

    # 4. Assemblage de la figure finale
    fig, ax = plt.subplots(figsize=(16, 14), facecolor="white")
    ax.set_facecolor("#f8f9fa")

    if deps_metro is not None and not deps_metro.empty:
        deps_metro.plot(ax=ax, color="#eef0f2", edgecolor="none", zorder=1)

    ax.imshow(
        img,
        extent=[xmin, xmax, ymin, ymax],
        origin="upper",
        interpolation="none",
        zorder=2,
    )

    if deps_metro is not None and not deps_metro.empty:
        deps_metro.plot(ax=ax, facecolor="none", edgecolor="#333333", linewidth=0.45, zorder=3)

    surf_tot = surfaces_groupes.sum()
    ax.set_title(
        f"Parcelles agricoles par groupe de cultures — France ({len(fichiers)} départements)\n"
        f"RPG {annee} • {nb_total:,} parcelles • {surf_tot:,.0f} ha déclarés".replace(",", " "),
        fontsize=14,
        fontweight="bold",
        pad=16,
    )
    ax.set_axis_off()

    handles = [
        mpatches.Patch(
            color=couleurs[grp],
            label=f"{grp} ({surfaces_groupes[grp]:,.0f} ha)".replace(",", " "),
        )
        for grp in groupes
    ]
    ax.legend(
        handles=handles,
        title="Groupe de cultures (surface déclarée)",
        title_fontsize=10.5,
        fontsize=8.5,
        loc="center left",
        bbox_to_anchor=(1.01, 0.5),
        frameon=True,
        facecolor="white",
        edgecolor="#cccccc",
    )

    fichier_sortie = Path(fichier_sortie)
    fichier_sortie.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    fig.savefig(fichier_sortie, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return fichier_sortie


if __name__ == "__main__":
    import time as _time

    t0 = _time.time()
    sortie = tracer_carte_france_groupes_cultures()
    print(f"Carte générée dans {sortie} en {_time.time() - t0:.1f} s")
