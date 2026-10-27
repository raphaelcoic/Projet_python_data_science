from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.transforms import Affine2D

from src.agriculture.constantes_rpg import COUCHE_DEP_ATTRIB, DEPARTEMENTS_OUTRE_MER, PALETTE_GROUPES
from src.agriculture.recuperer_departements_ign import recuperer_departements_ign
from src.visualisation.construire_chemins_groupes import construire_chemins_groupes


def tracer_carte_groupes_cultures(
    gdf: gpd.GeoDataFrame,
    code_dep: str = "90",
    fichier_sortie: str | Path | None = None,
    afficher_contour_dep: bool = True,
    dpi: int = 220,
) -> Path:
    """
    Génère une carte des parcelles agricoles d'un département colorées par `libelle_groupe`.

    gdf : parcelles renvoyées par `recuperer_parcelles_rpg`.
    Par défaut, la carte est enregistrée dans output/figures/carte_rpg_{code_dep}_groupes.png.
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
    couleurs = {grp: PALETTE_GROUPES[i % len(PALETTE_GROUPES)] for i, grp in enumerate(groupes)}
    grp_to_id = {grp: i for i, grp in enumerate(groupes)}
    grp_codes = lib_grp.map(grp_to_id).to_numpy(dtype=np.int32)

    chemins, (xmin, ymin, xmax, ymax) = construire_chemins_groupes(
        sub.geometry.to_numpy(),
        grp_codes,
        len(groupes),
        crs_cible=crs_cible,
    )

    dep_geom = None
    if afficher_contour_dep:
        try:
            deps = recuperer_departements_ign(COUCHE_DEP_ATTRIB)
        except Exception:
            deps = None  # la carte reste lisible sans le contour
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

    # Rastérisation directe des chemins sur un tampon Agg (bien plus rapide que GeoPandas.plot)
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
            renderer.draw_path(gc, path, trans, mcolors.to_rgba(couleurs[grp], alpha=1.0))

    img = np.asarray(renderer.buffer_rgba())

    fig, ax = plt.subplots(figsize=(13, 10), facecolor="white")
    ax.set_facecolor("#f8f9fa")

    if dep_geom is not None:
        dep_geom.plot(ax=ax, color="#eef0f2", edgecolor="none", zorder=1)

    ax.imshow(img, extent=[xmin, xmax, ymin, ymax], origin="upper", interpolation="none", zorder=2)

    if dep_geom is not None:
        dep_geom.plot(ax=ax, facecolor="none", edgecolor="#222222", linewidth=1.2, zorder=3)

    nom_dep = sub["nom_dep"].dropna().iloc[0] if not sub["nom_dep"].dropna().empty else code_dep
    annee = int(sub["annee"].dropna().iloc[0]) if not sub["annee"].dropna().empty else 2025
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

    if fichier_sortie is None:
        fichier_sortie = Path(f"output/figures/carte_rpg_{code_dep}_groupes.png")
    fichier_sortie = Path(fichier_sortie)
    fichier_sortie.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    fig.savefig(fichier_sortie, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return fichier_sortie
