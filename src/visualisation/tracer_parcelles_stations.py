from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from src.visualisation.tracer_filieres_rpg import COULEURS_FILIERES, ORDRE_FILIERES


def tracer_parcelles_stations(contours, zones_hydro, stations, contour_dep, titre, ax, cadre=None):
    """Carte des parcelles par filière, des limites des zones hydrographiques et des stations de mesure.

    contours : GeoDataFrame des parcelles avec les colonnes filiere et geometry (Lambert 93).
    zones_hydro : GeoDataFrame renvoyé par recuperer_zones_hydro.
    stations : GeoDataFrame des stations de mesure (Lambert 93), tracées en points rouges pour les localiser.
    contour_dep : GeoDataFrame du contour du département, tracé en pointillés.
    cadre : (xmin, ymin, xmax, ymax) en Lambert 93 pour zoomer ; par défaut, toutes les parcelles.
    """
    xmin, ymin, xmax, ymax = contours.total_bounds if cadre is None else cadre
    contours.plot(ax=ax, color=contours["filiere"].map(COULEURS_FILIERES), linewidth=0)
    zones_hydro.cx[xmin:xmax, ymin:ymax].boundary.plot(ax=ax, color="black", linewidth=0.8)
    contour_dep.boundary.plot(ax=ax, color="#555555", linewidth=1.5, linestyle="--")

    visibles = stations.cx[xmin:xmax, ymin:ymax]
    ax.scatter(visibles.geometry.x, visibles.geometry.y, s=60, color="red", edgecolor="black", linewidth=1, zorder=4)

    presentes = [f for f in ORDRE_FILIERES if f in set(contours["filiere"])]
    legende = [Patch(color=COULEURS_FILIERES[f], label=f) for f in presentes]
    legende.append(Line2D([], [], marker="o", linestyle="", markersize=8, markerfacecolor="red",
                          markeredgecolor="black", label="station de mesure"))
    ax.legend(handles=legende, loc="lower left", fontsize=7, framealpha=0.9)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_title(titre)
    ax.set_axis_off()
