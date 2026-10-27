import numpy as np
import pyproj
import shapely
from matplotlib.path import Path as MplPath


def construire_chemins_groupes(
    geoms: np.ndarray,
    grp_codes: np.ndarray,
    n_groupes: int,
    crs_cible: object = 2154,
) -> tuple[dict[int, MplPath], tuple[float, float, float, float]]:
    """
    Extrait de manière vectorisée (Shapely 2 + PyProj + NumPy) tous les anneaux des
    polygones et construit un unique `matplotlib.path.Path` composite par groupe de
    cultures, par découpage contigu sans copie mémoire.

    geoms : géométries en EPSG:4326 ; grp_codes : numéro de groupe (0 à n_groupes - 1) de chaque géométrie.
    Renvoie ({numéro de groupe: chemin}, emprise (xmin, ymin, xmax, ymax) dans `crs_cible`).
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
