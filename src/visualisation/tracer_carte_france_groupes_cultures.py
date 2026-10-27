"""
Carte de France des parcelles agricoles du RPG par groupe de cultures, à partir
des fichiers départementaux `data/processed/rpg/rpg{annee}/rpg_{annee}_{dep}.parquet`.

Exécution directe (depuis la racine du dépôt) :
    python -m src.visualisation.tracer_carte_france_groupes_cultures
"""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import shapely
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.path import Path as MplPath
from matplotlib.transforms import Affine2D

from src.agriculture.constantes_rpg import COUCHE_DEP_ATTRIB, DEPARTEMENTS_EXCLUS_DEFAUT, DOSSIER_RPG, PALETTE_GROUPES
from src.agriculture.dossier_millesime_rpg import dossier_millesime_rpg
from src.agriculture.recuperer_departements_ign import recuperer_departements_ign
from src.visualisation.construire_chemins_groupes import construire_chemins_groupes

# Emprise de repli en Lambert-93 (EPSG:2154) pour la France métropolitaine + Corse
_EMPRISE_METRO_2154 = (99_000.0, 6_049_000.0, 1_243_000.0, 7_111_000.0)


def _lire_stats_departement(f: Path) -> tuple[int, pd.Series | None]:
    """Lit uniquement les colonnes légères d'un fichier Parquet départemental."""
    tbl = pq.read_table(f, columns=["libelle_groupe", "surface_ha"])
    if tbl.num_rows == 0:
        return 0, None
    df_meta = tbl.to_pandas()
    df_meta["libelle_groupe"] = df_meta["libelle_groupe"].fillna("Non renseigné")
    return len(df_meta), df_meta.groupby("libelle_groupe")["surface_ha"].sum()


def _preparer_departement_france(f: Path, grp_to_id: dict[str, int], n_groupes: int) -> dict[int, MplPath]:
    """Charge un département et construit ses chemins vectoriels en Lambert-93."""
    tbl = pq.read_table(f, columns=["libelle_groupe", "geometry"])
    if tbl.num_rows == 0:
        return {}
    geoms = shapely.from_wkb(tbl["geometry"].to_numpy(zero_copy_only=False))
    lib_grp = tbl["libelle_groupe"].to_pandas().fillna("Non renseigné")
    grp_codes = lib_grp.map(grp_to_id).to_numpy(dtype=np.int32)
    chemins, _ = construire_chemins_groupes(geoms, grp_codes, n_groupes, crs_cible=2154)
    return chemins


def tracer_carte_france_groupes_cultures(
    dossier_parquet: str | Path = DOSSIER_RPG,
    fichier_sortie: str | Path | None = None,
    annee: int = 2023,
    dpi: int = 250,
    max_workers: int | None = None,
) -> Path:
    """
    Génère la carte de France métropolitaine continentale (hors Corse et DROM) des parcelles
    agricoles colorées par `libelle_groupe`, à partir des fichiers Parquet départementaux
    situés dans `data/processed/rpg/rpg{annee}/`. Le projet utilise le millésime 2023.
    Par défaut, la carte est enregistrée dans output/figures/carte_rpg_{annee}_france_groupes.png.

    L'extraction des anneaux, la projection Lambert-93 et la rastérisation (`RendererAgg`)
    sont vectorisées et parallélisées afin de traiter les ~9,8 millions de parcelles en
    quelques secondes avec une empreinte mémoire bornée.
    """
    dossier_base = Path(dossier_parquet)
    dossier_annee = dossier_millesime_rpg(dossier_base, annee)

    if dossier_annee.exists():
        fichiers = sorted(dossier_annee.glob(f"rpg_{annee}_*.parquet"))
    else:
        fichiers = sorted(dossier_base.glob(f"rpg_{annee}_*.parquet"))

    # Périmètre d'étude : on écarte la Corse et les DROM (code département en fin de nom de fichier)
    fichiers = [f for f in fichiers if f.stem.split("_")[-1].upper() not in DEPARTEMENTS_EXCLUS_DEFAUT]

    if not fichiers:
        raise FileNotFoundError(
            f"Aucun fichier rpg_{annee}_*.parquet trouvé dans {dossier_annee} ni dans {dossier_base}"
        )

    if fichier_sortie is None:
        fichier_sortie = Path(f"output/figures/carte_rpg_{annee}_france_groupes.png")

    if max_workers is None:
        max_workers = min(8, os.cpu_count() or 4)

    # 1. Passe légère parallélisée (sans géométrie) pour calculer les surfaces nationales
    stats_list = []
    nb_total = 0

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        resultats_meta = list(ex.map(_lire_stats_departement, fichiers))

    for n_rows, serie_surf in resultats_meta:
        if serie_surf is not None:
            nb_total += n_rows
            stats_list.append(serie_surf)

    surfaces_groupes = pd.concat(stats_list).groupby(level=0).sum().sort_values(ascending=False)
    groupes = list(surfaces_groupes.index)
    couleurs = {grp: PALETTE_GROUPES[i % len(PALETTE_GROUPES)] for i, grp in enumerate(groupes)}
    grp_to_id = {grp: i for i, grp in enumerate(groupes)}
    rgba_par_id = [mcolors.to_rgba(couleurs[grp], alpha=1.0) for grp in groupes]

    # 2. Contours départementaux (cache data/processed/rpg/_contours_departements.parquet)
    try:
        deps_gdf = recuperer_departements_ign(COUCHE_DEP_ATTRIB)
        deps_metro = deps_gdf[~deps_gdf["code_dep"].isin(DEPARTEMENTS_EXCLUS_DEFAUT)].to_crs(2154)
    except Exception:
        deps_metro = None  # la carte reste lisible sans les contours

    if deps_metro is not None and not deps_metro.empty:
        xmin, ymin, xmax, ymax = (float(v) for v in deps_metro.total_bounds)
    else:
        xmin, ymin, xmax, ymax = _EMPRISE_METRO_2154

    pad_x = (xmax - xmin) * 0.02
    pad_y = (ymax - ymin) * 0.02
    xmin, xmax = xmin - pad_x, xmax + pad_x
    ymin, ymax = ymin - pad_y, ymax + pad_y

    # 3. Rastérisation directe sur tampon RendererAgg partagé (mémoire constante ~60 Mo)
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
        for chemins_dep in ex.map(lambda f: _preparer_departement_france(f, grp_to_id, n_groupes), fichiers):
            for g_id, path in chemins_dep.items():
                renderer.draw_path(gc, path, trans, rgba_par_id[g_id])

    img = np.asarray(renderer.buffer_rgba())

    # 4. Assemblage de la figure finale
    fig, ax = plt.subplots(figsize=(16, 14), facecolor="white")
    ax.set_facecolor("#f8f9fa")

    if deps_metro is not None and not deps_metro.empty:
        deps_metro.plot(ax=ax, color="#eef0f2", edgecolor="none", zorder=1)

    ax.imshow(img, extent=[xmin, xmax, ymin, ymax], origin="upper", interpolation="none", zorder=2)

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
    print(f"Carte générée dans {tracer_carte_france_groupes_cultures()}")
