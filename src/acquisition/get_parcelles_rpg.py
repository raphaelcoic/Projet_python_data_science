"""
Acquisition des parcelles agricoles du Registre Parcellaire Graphique (RPG)
par appels API au service WFS de la Géoplateforme IGN (https://data.geopf.fr/wfs)
et sélection harmonisée des 13 variables d'intérêt du projet pour tous les
millésimes (2010 à 2025, notamment 2013, 2023 et 2025).

Variables retenues pour le projet (`COLONNES_PROJET_RPG`) :
    id_parcelle, annee, code_dep, nom_dep, surface_ha,
    categorie_culture, libelle_categorie,
    code_culture, libelle_culture, code_groupe, libelle_groupe,
    bio, geometry

Source : https://www.data.gouv.fr/datasets/rpg (IGN / ASP)

Exemple
-------
>>> from src.acquisition.get_parcelles_rpg import get_parcelles_rpg
>>> gdf_2023 = get_parcelles_rpg(departements=["90"], annee=2023)
>>> gdf_2013 = get_parcelles_rpg(departements=["90"], annee=2013)
"""

from __future__ import annotations

import re
import time
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests
import shapely
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

WFS_URL = "https://data.geopf.fr/wfs/ows"
PAGE_SIZE = 5000  # maximum imposé par le serveur WFS de la Géoplateforme

# Couches départementales ADMIN-EXPRESS (même service WFS)
COUCHE_DEP_FILTRE = "ADMINEXPRESS-COG-CARTO-PE.LATEST:departement"  # très simplifiée -> filtre serveur
COUCHE_DEP_ATTRIB = "ADMINEXPRESS-COG-CARTO.LATEST:departement"  # plus précise -> attribution du département

# Chemin du cache local des contours départementaux (conservé à la racine de data/processed/rpg)
CHEMIN_CACHE_CONTOURS_DEP = Path("data/processed/rpg/_contours_departements.parquet")

# Les 13 variables strictement retenues pour le projet
COLONNES_PROJET_RPG: list[str] = [
    "id_parcelle",
    "annee",
    "code_dep",
    "nom_dep",
    "surface_ha",
    "categorie_culture",
    "libelle_categorie",
    "code_culture",
    "libelle_culture",
    "code_groupe",
    "libelle_groupe",
    "bio",
    "geometry",
]

# Libellés des grandes catégories de culture (champ cat_cult_p)
CATEGORIES_CULTURE: dict[str, str] = {
    "TA": "Terres arables",
    "PP": "Prairies permanentes",
    "CP": "Cultures permanentes",
    "SB": "Surfaces boisées",
}

# Référentiel harmonisé des 28 groupes de cultures du RPG (utilisé notamment pour 2013 et en secours)
LIBELLES_GROUPES_RPG: dict[str, str] = {
    "1": "Blé tendre",
    "2": "Maïs grain et ensilage",
    "3": "Orge",
    "4": "Autres céréales",
    "5": "Colza",
    "6": "Tournesol",
    "7": "Autres oléagineux",
    "8": "Protéagineux",
    "9": "Plantes à fibres",
    "10": "Semences",
    "11": "Gel (surfaces gelées sans production)",
    "12": "Gel industriel",
    "13": "Autres gels",
    "14": "Riz",
    "15": "Légumineuses à grains",
    "16": "Fourrage",
    "17": "Estives et landes",
    "18": "Prairies permanentes",
    "19": "Prairies temporaires",
    "20": "Vergers",
    "21": "Vignes",
    "22": "Fruits à coque",
    "23": "Oliviers",
    "24": "Autres cultures industrielles",
    "25": "Légumes ou fleurs",
    "26": "Canne à sucre",
    "27": "Arboriculture",
    "28": "Divers",
}

# Correspondance Groupe de cultures -> Grande catégorie de culture (TA, PP, CP, NA)
GROUPE_VERS_CATEGORIE: dict[str, str] = {
    "1": "TA", "2": "TA", "3": "TA", "4": "TA", "5": "TA",
    "6": "TA", "7": "TA", "8": "TA", "9": "TA", "10": "TA",
    "11": "TA", "12": "TA", "13": "TA", "14": "TA", "15": "TA",
    "16": "TA", "17": "PP", "18": "PP", "19": "TA",
    "20": "CP", "21": "CP", "22": "CP", "23": "CP",
    "24": "TA", "25": "TA", "26": "CP", "27": "CP", "28": "NA",
}

# Correspondance exacte Code culture (3 lettres) -> Grande catégorie de culture (issue du RPG 2025 + PAC)
CULTURE_VERS_CATEGORIE: dict[str, str] = {
    "AAR": "TA", "ACA": "TA", "ACP": "CP", "AFG": "TA", "AGR": "CP", "AIL": "TA",
    "AME": "TA", "ANA": "TA", "ARA": "TA", "ARP": "CP", "ART": "TA", "AVH": "TA",
    "AVO": "CP", "AVP": "TA", "BCA": "CP", "BCF": "CP", "BCI": "CP", "BCP": "CP",
    "BCR": "CP", "BDH": "TA", "BDP": "TA", "BDT": "TA", "BEA": "CP", "BEF": "CP",
    "BEI": "CP", "BEP": "CP", "BER": "CP", "BFP": "TA", "BFS": "NA", "BOR": "NA",
    "BOP": "PP", "BTA": "NA", "BTH": "TA", "BTN": "TA", "BTP": "TA", "BVF": "TA",
    "CAB": "CP", "CAC": "CP", "CAE": "PP", "CAF": "TA", "CAG": "TA", "CAH": "TA",
    "CAR": "TA", "CBT": "CP", "CCN": "TA", "CEE": "PP", "CEL": "TA", "CHU": "TA",
    "CHV": "TA", "CML": "TA", "CPL": "TA", "CSA": "CP", "CSF": "CP", "CSI": "CP",
    "CSP": "CP", "CSR": "CP", "CSS": "NA", "CTG": "CP", "CZH": "TA", "CZP": "TA",
    "EPE": "TA", "EPI": "TA", "FEV": "TA", "FLA": "TA", "FLP": "CP", "FNU": "TA",
    "FRA": "TA", "FVL": "TA", "FVP": "TA", "GES": "TA", "GRA": "TA", "HBL": "CP",
    "HPC": "TA", "J5M": "TA", "J6P": "TA", "J6S": "TA", "JAC": "TA", "JNO": "TA",
    "LAV": "CP", "LBF": "TA", "LDH": "TA", "LDP": "TA", "LEC": "TA", "LIF": "TA",
    "LIH": "TA", "LIP": "TA", "LOT": "TA", "LUZ": "TA", "MCR": "TA", "MCS": "TA",
    "MCT": "CP", "MDI": "TA", "MID": "TA", "MIE": "TA", "MIS": "TA", "MLC": "TA",
    "MLF": "TA", "MLG": "TA", "MLO": "TA", "MLS": "TA", "MLT": "TA", "MOH": "TA",
    "MOT": "TA", "MPA": "TA", "MPC": "TA", "MRS": "NA", "MSW": "CP", "NOS": "CP",
    "NOX": "CP", "NVT": "TA", "NYG": "TA", "OAG": "TA", "OEI": "TA", "OHR": "TA",
    "OIG": "TA", "OLI": "CP", "ORH": "TA", "ORP": "TA", "PAG": "TA", "PCH": "TA",
    "PCL": "TA", "PEP": "CP", "PEV": "CP", "PFR": "CP", "PHF": "TA", "PHI": "TA",
    "PHS": "TA", "PIS": "CP", "PME": "CP", "POR": "TA", "POT": "TA", "PPH": "PP",
    "PPP": "CP", "PPR": "TA", "PRF": "CP", "PRL": "PP", "PRU": "CP", "PSL": "TA",
    "PTC": "TA", "PTR": "TA", "PVP": "TA", "PVT": "CP", "PWT": "CP", "RDI": "TA",
    "RGA": "TA", "RIZ": "TA", "ROS": "CP", "RVI": "CP", "SAG": "NA", "SAI": "TA",
    "SBO": "SB", "SGH": "TA", "SGP": "TA", "SHD": "CP", "SIN": "NA", "SNA": "NA",
    "SNE": "NA", "SNU": "NA", "SOG": "TA", "SOJ": "TA", "SPH": "PP", "SPL": "PP",
    "SRS": "TA", "TAB": "TA", "TBT": "TA", "TCR": "CP", "TOM": "TA", "TRE": "TA",
    "TRN": "TA", "TRU": "CP", "TTH": "TA", "TTP": "TA", "VES": "TA", "VET": "CP",
    "VGD": "CP", "VNL": "CP", "VRC": "CP", "VRG": "CP", "VRN": "CP", "VRT": "CP",
    "ZZZ": "NA",
}

# Seule l'édition 2025 (RPG v4) du WFS contient le label bio au niveau de la parcelle.
ANNEES_AVEC_BIO = {2025}

# Départements d'Outre-Mer (DROM)
DEPARTEMENTS_OUTRE_MER = {"971", "972", "973", "974", "976"}


# --------------------------------------------------------------------------- #
# Outils HTTP / WFS
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=1)
def _session() -> requests.Session:
    """Session HTTP avec relance automatique (erreurs 429 / 5xx, coupures réseau)."""
    s = requests.Session()
    retry = Retry(
        total=6,
        backoff_factor=2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    s.mount("https://", HTTPAdapter(max_retries=retry, pool_maxsize=32))
    return s


def _wfs(params: dict, timeout: int = 180) -> requests.Response:
    base = {"SERVICE": "WFS", "VERSION": "2.0.0"}
    r = _session().get(WFS_URL, params={**base, **params}, timeout=timeout)
    r.raise_for_status()
    return r


def _couche_parcelles(annee: int) -> str:
    if annee == 2025:
        return "LANDUSE.AGRICULTURE2025:parcelles_graphiques"
    if 2015 <= annee <= 2024:
        return f"RPG.{annee}:parcelles_graphiques"
    if 2010 <= annee <= 2014:
        return f"RPG.{annee}:rpg_{annee}"
    raise ValueError("Année non disponible sur le WFS : choisir entre 2010 et 2025.")


def _couche_codes_cultures(annee: int) -> str:
    if annee == 2025:
        return "LANDUSE.AGRICULTURE2025:codes_cultures"
    if annee in (2022, 2023, 2024):
        return f"RPG.{annee}:codes_cultures"
    # Pas de table de codes publiée en WFS avant 2022 : on prend 2023 (la plus complète avec 372 codes)
    return "RPG.2023:codes_cultures"


@lru_cache(maxsize=None)
def _schema(couche: str) -> tuple[str, tuple[str, ...]]:
    """Retourne (nom du champ géométrie, noms des champs attributaires) d'une couche."""
    xsd = _wfs({"REQUEST": "DescribeFeatureType", "TYPENAMES": couche}).text
    elements = re.findall(r'<xsd:element[^>]*name="([^"]+)"[^>]*type="([^"]+)"', xsd)
    geom = next(n for n, t in elements if t.startswith("gml:"))
    champs = tuple(
        n for n, t in elements
        if not t.startswith("gml:") and ":" in t and n != couche.split(":")[1]
    )
    return geom, champs


def _proprietes_wfs_utiles(annee: int, geom_champ: str, champs: tuple[str, ...]) -> str:
    """
    Construit la liste `PROPERTYNAME` minimale à demander au serveur WFS afin de
    ne pas transférer sur le réseau les colonnes non retenues pour le projet.
    """
    if 2010 <= annee <= 2014:
        candidats = ("num_ilot", "surf_graph", "surf_cultu", "code_cultu", "nom_cultu")
    elif annee == 2025:
        candidats = ("num_ilot", "num_parcel", "surf_parc", "cat_cult_p", "code_cultu", "code_group", "bio")
    else:
        candidats = ("id_parcel", "surf_parc", "cat_cult_p", "code_cultu", "code_group", "bio")

    retenus = [c for c in candidats if c in champs]
    retenus.append(geom_champ)
    return ",".join(retenus)


def _page_avec_total(
    couche: str,
    cql: str,
    start: int,
    tri: str,
    propertyname: str | None = None,
) -> tuple[int, list[dict]]:
    params = {
        "REQUEST": "GetFeature",
        "TYPENAMES": couche,
        "OUTPUTFORMAT": "application/json",
        "CQL_FILTER": cql,
        "SORTBY": tri,  # tri stable indispensable pour paginer sans doublon ni trou
        "COUNT": PAGE_SIZE,
        "STARTINDEX": start,
    }
    if propertyname:
        params["PROPERTYNAME"] = propertyname
    r = _wfs(params)
    js = r.json()
    return int(js.get("numberMatched") or 0), js["features"]


# --------------------------------------------------------------------------- #
# Référentiels (départements, codes cultures) — récupérés une fois par session
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=None)
def _departements(couche: str) -> gpd.GeoDataFrame:
    if CHEMIN_CACHE_CONTOURS_DEP.exists():
        try:
            gdf_cache = gpd.read_parquet(CHEMIN_CACHE_CONTOURS_DEP)
            _ = gdf_cache.sindex
            return gdf_cache
        except Exception:
            pass

    geom_champ, _ = _schema(couche)
    r = _wfs(
        {
            "REQUEST": "GetFeature",
            "TYPENAMES": couche,
            "OUTPUTFORMAT": "application/json",
            "PROPERTYNAME": f"code_insee,nom_officiel,{geom_champ}",
            "COUNT": 200,
        },
        timeout=300,
    )
    gdf = gpd.GeoDataFrame.from_features(r.json()["features"], crs=4326)
    gdf = gdf.rename(columns={"code_insee": "code_dep", "nom_officiel": "nom_dep"})[
        ["code_dep", "nom_dep", "geometry"]
    ]
    if couche == COUCHE_DEP_ATTRIB:
        try:
            CHEMIN_CACHE_CONTOURS_DEP.parent.mkdir(parents=True, exist_ok=True)
            gdf.to_parquet(CHEMIN_CACHE_CONTOURS_DEP, index=False)
        except Exception:
            pass
    _ = gdf.sindex  # pré-construit l'index spatial une seule fois
    return gdf


@lru_cache(maxsize=None)
def _table_codes(couche: str) -> pd.DataFrame:
    r = _wfs({"REQUEST": "GetFeature", "TYPENAMES": couche, "OUTPUTFORMAT": "application/json"})
    df = pd.DataFrame([f["properties"] for f in r.json()["features"]])
    df.columns = [c.lower() for c in df.columns]
    return df.rename(
        columns={
            "code": "code_culture",
            "libelle": "libelle_culture",
            "code_groupe_culture": "code_groupe",
            "libelle_groupe_culture": "libelle_groupe",
        }
    )


def _libelles_cultures(annee: int) -> tuple[dict[str, str], dict[str, str]]:
    """Retourne ({code_culture: libellé}, {code_groupe: libellé du groupe})."""
    codes = _table_codes(_couche_codes_cultures(annee))
    cultures = dict(zip(codes["code_culture"], codes["libelle_culture"]))
    if "libelle_groupe" not in codes:
        codes = _table_codes(_couche_codes_cultures(2025))
    groupes = {
        **LIBELLES_GROUPES_RPG,
        **dict(zip(codes["code_groupe"].astype(str), codes["libelle_groupe"])),
    }
    return cultures, groupes


def _tuiles_bbox(code_dep: str, geom_champ: str, pas: float = 0.45) -> list[str]:
    """
    Découpe l'emprise du département en une grille de boîtes englobantes (BBOX)
    ajustées au polygone du département.
    """
    deps = _departements(COUCHE_DEP_FILTRE)
    sel = deps.loc[deps["code_dep"] == code_dep, "geometry"]
    if sel.empty:
        raise ValueError(f"Département inconnu : {code_dep!r}")
    geom = sel.iloc[0].buffer(0.01)  # ~1 km de marge autour du contour généralisé
    minx, miny, maxx, maxy = geom.bounds
    nx = max(1, int(((maxx - minx) // pas) + 1))
    ny = max(1, int(((maxy - miny) // pas) + 1))
    dx = (maxx - minx) / nx
    dy = (maxy - miny) / ny
    tuiles = []
    for i in range(nx):
        for j in range(ny):
            cell = shapely.box(
                minx + i * dx,
                miny + j * dy,
                minx + (i + 1) * dx,
                miny + (j + 1) * dy,
            )
            inter = geom.intersection(cell)
            if not inter.is_empty:
                bx0, by0, bx1, by1 = inter.bounds
                tuiles.append(
                    f"BBOX({geom_champ},{bx0:.5f},{by0:.5f},{bx1:.5f},{by1:.5f},'EPSG:4326')"
                )
    return tuiles


# --------------------------------------------------------------------------- #
# Récupération d'un département
# --------------------------------------------------------------------------- #
def _parcelles_departement(
    code_dep: str,
    annee: int,
    filtres: list[str],
    max_workers: int,
    verbose: bool,
) -> gpd.GeoDataFrame:
    couche = _couche_parcelles(annee)
    geom_champ, champs = _schema(couche)
    if "id_parcel" in champs:
        tri = "id_parcel"
    elif {"num_ilot", "num_parcel"} <= set(champs):
        tri = "num_ilot,num_parcel"
    elif "num_ilot" in champs:
        tri = "num_ilot"
    else:
        tri = champs[0]

    propertyname = _proprietes_wfs_utiles(annee, geom_champ, champs)
    tuiles_cql = [
        " AND ".join([bbox_cql, *filtres])
        for bbox_cql in _tuiles_bbox(code_dep, geom_champ)
    ]

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        premieres = list(
            ex.map(lambda cql: _page_avec_total(couche, cql, 0, tri, propertyname), tuiles_cql)
        )
        pages_suivantes = [
            (cql, s)
            for cql, (n_tuile, _) in zip(tuiles_cql, premieres)
            for s in range(PAGE_SIZE, n_tuile, PAGE_SIZE)
        ]
        n_req = len(tuiles_cql) + len(pages_suivantes)
        n_cand = sum(n_tuile for n_tuile, _ in premieres)
        if verbose:
            print(
                f"  [{code_dep}] {n_cand:>9,} parcelles candidates ({len(tuiles_cql)} tuiles) -> {n_req} requêtes",
                flush=True,
            )
        if n_cand == 0:
            return gpd.GeoDataFrame()

        suites = (
            list(
                ex.map(
                    lambda args: _page_avec_total(couche, args[0], args[1], tri, propertyname)[1],
                    pages_suivantes,
                )
            )
            if pages_suivantes
            else []
        )

    # Déduplication rapide par identifiant WFS avant construction des géométries Shapely
    uniques: dict[str, dict] = {}
    for _, feats in premieres:
        for f in feats:
            uniques[f.get("id") or id(f)] = f
    for feats in suites:
        for f in feats:
            uniques[f.get("id") or id(f)] = f

    gdf = gpd.GeoDataFrame.from_features(list(uniques.values()), crs=4326)

    # Attribution du département : point intérieur de la parcelle dans le contour ADMIN-EXPRESS.
    deps = _departements(COUCHE_DEP_ATTRIB)
    pts = gpd.GeoDataFrame(geometry=gdf.geometry.representative_point(), crs=4326)
    joint = gpd.sjoin(pts, deps[["code_dep", "geometry"]], how="left", predicate="within")
    joint = joint[~joint.index.duplicated(keep="first")]
    # Parcelles littorales dont le point tombe hors du trait de côte généralisé -> département demandé
    gdf["code_dep"] = joint["code_dep"].fillna(code_dep)
    gdf = gdf[gdf["code_dep"] == code_dep].copy()

    if verbose:
        print(f"  [{code_dep}] {len(gdf):>9,} parcelles retenues ({time.time() - t0:.1f} s)", flush=True)
    return gdf


def _dedupliquer_parcelles(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Supprime les vrais doublons serveur (même `id_parcelle` et même géométrie WKB,
    ex. Corrèze 19 en 2013) tout en conservant et désambiguïsant les parcelles
    distinctes qui partageraient un numéro local `id_parcel` (ex. DROM en 2023).
    """
    gdf["_wkb"] = shapely.to_wkb(gdf.geometry.to_numpy())
    gdf = gdf.drop_duplicates(["id_parcelle", "_wkb"]).drop(columns=["_wkb"]).copy()
    if gdf["id_parcelle"].duplicated().any():
        rang = gdf.groupby("id_parcelle").cumcount()
        masque = rang > 0
        gdf.loc[masque, "id_parcelle"] = (
            gdf.loc[masque, "id_parcelle"] + "_" + rang[masque].astype(str)
        )
    return gdf


def _mise_en_forme(gdf: gpd.GeoDataFrame, annee: int, avec_libelles: bool) -> gpd.GeoDataFrame:
    """
    Harmonise les colonnes entre les différentes générations du RPG (2010-2014,
    2015-2024 et 2025) et sélectionne uniquement les 13 variables `COLONNES_PROJET_RPG`.
    """
    if 2010 <= annee <= 2014:
        # RPG v1 (ex. 2013) : îlots anonymisés avec groupe de culture majoritaire (01 à 28)
        gdf["id_parcelle"] = gdf["num_ilot"].astype(str)
        gdf = _dedupliquer_parcelles(gdf)

        surf_g = pd.to_numeric(gdf.get("surf_graph"), errors="coerce")
        surf_c = pd.to_numeric(gdf.get("surf_cultu"), errors="coerce")
        gdf["surface_ha"] = surf_g.fillna(surf_c)

        code_raw = gdf["code_cultu"].astype(str).str.strip()
        code_grp = code_raw.str.lstrip("0").replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
        gdf["code_groupe"] = code_grp
        gdf["code_culture"] = code_raw

        if avec_libelles:
            nom_secours = (
                gdf["nom_cultu"].astype(str).str.capitalize()
                if "nom_cultu" in gdf
                else pd.Series(pd.NA, index=gdf.index)
            )
            gdf["libelle_groupe"] = gdf["code_groupe"].map(LIBELLES_GROUPES_RPG).fillna(nom_secours)
            gdf["libelle_culture"] = gdf["libelle_groupe"]
        else:
            gdf["libelle_groupe"] = pd.NA
            gdf["libelle_culture"] = pd.NA

        gdf["categorie_culture"] = gdf["code_groupe"].map(GROUPE_VERS_CATEGORIE)
        gdf["libelle_categorie"] = gdf["categorie_culture"].map(CATEGORIES_CULTURE)
        gdf["bio"] = pd.Series(pd.NA, index=gdf.index, dtype="boolean")
    else:
        # RPG v2/v3 (2015-2024, ex. 2023) et RPG v4 (2025) : parcelles graphiques
        gdf = gdf.rename(
            columns={
                "surf_parc": "surface_ha",
                "cat_cult_p": "categorie_culture",
                "code_cultu": "code_culture",
                "code_group": "code_groupe",
            }
        )
        if "id_parcel" in gdf:
            gdf["id_parcelle"] = gdf["id_parcel"].astype(str)
        else:  # RPG v4 (2025) : identifiant = îlot anonyme + numéro de parcelle
            gdf["id_parcelle"] = gdf["num_ilot"].astype(str) + "_" + gdf["num_parcel"].astype(str)
        gdf = _dedupliquer_parcelles(gdf)

        gdf["surface_ha"] = pd.to_numeric(gdf["surface_ha"], errors="coerce")
        if "code_groupe" in gdf:
            gdf["code_groupe"] = (
                gdf["code_groupe"]
                .astype(str)
                .str.strip()
                .str.lstrip("0")
                .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "<NA>": pd.NA})
            )
        else:
            gdf["code_groupe"] = pd.NA

        if avec_libelles:
            cultures, groupes = _libelles_cultures(annee)
            gdf["libelle_culture"] = gdf["code_culture"].map(cultures)
            gdf["libelle_groupe"] = gdf["code_groupe"].map(groupes)
        else:
            gdf["libelle_culture"] = pd.NA
            gdf["libelle_groupe"] = pd.NA

        if "categorie_culture" not in gdf:
            gdf["categorie_culture"] = (
                gdf["code_culture"]
                .map(CULTURE_VERS_CATEGORIE)
                .fillna(gdf["code_groupe"].map(GROUPE_VERS_CATEGORIE))
            )
        else:
            manquants_cat = gdf["categorie_culture"].isna()
            if manquants_cat.any():
                gdf.loc[manquants_cat, "categorie_culture"] = (
                    gdf.loc[manquants_cat, "code_culture"]
                    .map(CULTURE_VERS_CATEGORIE)
                    .fillna(gdf.loc[manquants_cat, "code_groupe"].map(GROUPE_VERS_CATEGORIE))
                )
        gdf["libelle_categorie"] = gdf["categorie_culture"].map(CATEGORIES_CULTURE)

        if "bio" not in gdf:
            gdf["bio"] = pd.NA  # label bio non diffusé par le WFS avant 2025
        gdf["bio"] = gdf["bio"].astype("boolean")

    gdf["annee"] = int(annee)
    deps = _departements(COUCHE_DEP_ATTRIB)[["code_dep", "nom_dep"]]
    gdf = gdf.merge(deps, on="code_dep", how="left")

    for col in COLONNES_PROJET_RPG:
        if col not in gdf:
            gdf[col] = pd.NA

    return gpd.GeoDataFrame(gdf[COLONNES_PROJET_RPG], geometry="geometry", crs=4326)


# --------------------------------------------------------------------------- #
# Fonction publique
# --------------------------------------------------------------------------- #
def get_parcelles_rpg(
    departements: list[str] | str | None = None,
    annee: int = 2025,
    bio_uniquement: bool = False,
    codes_cultures: list[str] | None = None,
    avec_libelles: bool = True,
    max_workers: int = 12,
    verbose: bool = True,
) -> gpd.GeoDataFrame:
    """
    Construit la table des parcelles agricoles du RPG par appels à l'API WFS de l'IGN
    et sélectionne strictement les 13 variables du projet (`COLONNES_PROJET_RPG`).

    Parameters
    ----------
    departements : str | list[str] | None
        Codes INSEE des départements (ex. ``"35"``, ``["2A", "2B", "974"]``).
        ``None`` = France entière (préférer `sauvegarder_parcelles_rpg` pour ce cas).
    annee : int
        Millésime du RPG (2010 à 2025, notamment 2013, 2023 et 2025).
    bio_uniquement : bool
        Ne garder que les parcelles déclarées en agriculture biologique (2025 uniquement).
    codes_cultures : list[str] | None
        Filtre serveur optionnel sur les codes culture (ex. ``["BTH", "MIS", "VRC"]``).
    avec_libelles : bool
        Ajoute les libellés des cultures et des groupes de cultures.
    max_workers : int
        Nombre de requêtes WFS simultanées (8 par défaut).
    verbose : bool
        Affiche l'avancement.

    Returns
    -------
    geopandas.GeoDataFrame (EPSG:4326) contenant exactement les 13 colonnes :
        id_parcelle, annee, code_dep, nom_dep, surface_ha,
        categorie_culture, libelle_categorie,
        code_culture, libelle_culture, code_groupe, libelle_groupe,
        bio, geometry
    """
    if bio_uniquement and annee not in ANNEES_AVEC_BIO:
        raise ValueError(f"Le label bio n'est disponible via l'API que pour : {sorted(ANNEES_AVEC_BIO)}")

    if departements is None:
        departements = sorted(_departements(COUCHE_DEP_FILTRE)["code_dep"])
    elif isinstance(departements, str):
        departements = [departements]
    departements = [str(d).zfill(2) for d in departements]

    filtres = []
    if bio_uniquement:
        filtres.append("bio=true")
    if codes_cultures:
        filtres.append("code_cultu IN (" + ",".join(f"'{c}'" for c in codes_cultures) + ")")

    if verbose:
        print(f"RPG {annee} - {len(departements)} département(s)", flush=True)
    morceaux = [
        _parcelles_departement(dep, annee, filtres, max_workers, verbose) for dep in departements
    ]
    morceaux = [m for m in morceaux if len(m)]
    if not morceaux:
        return gpd.GeoDataFrame(columns=COLONNES_PROJET_RPG, geometry="geometry", crs=4326)

    gdf = gpd.GeoDataFrame(pd.concat(morceaux, ignore_index=True), crs=4326)
    return _mise_en_forme(gdf, annee, avec_libelles)
