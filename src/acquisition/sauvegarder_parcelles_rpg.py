"""
Acquisition et sauvegarde incrémentale en GeoParquet des millésimes du RPG
(notamment 2013, 2023 et 2025), organisés dans des sous-dossiers `rpg20XX`
sous `data/processed/rpg/` et filtrés sur les 13 variables du projet.

Arborescence produite :
    data/processed/rpg/
    ├── _contours_departements.parquet
    ├── rpg2013/
    │   ├── rpg_2013_01.parquet
    │   └── ...
    ├── rpg2023/
    │   ├── rpg_2023_01.parquet
    │   └── ...
    └── rpg2025/
        ├── rpg_2025_01.parquet
        └── ...

Exemples
--------
>>> from src.acquisition.sauvegarder_parcelles_rpg import (
...     filtrer_et_organiser_parquets_existants,
...     sauvegarder_parcelles_rpg,
... )
>>> filtrer_et_organiser_parquets_existants("data/processed/rpg")
>>> sauvegarder_parcelles_rpg("data/processed/rpg", annee=2013)
>>> sauvegarder_parcelles_rpg("data/processed/rpg", annee=2023)
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

import pyarrow.parquet as pq

# Permet d'exécuter ce fichier directement (ex. bouton Run dans VS Code ou `python src/acquisition/sauvegarder_parcelles_rpg.py`)
_RACINE_PROJET = Path(__file__).resolve().parents[2]
if str(_RACINE_PROJET) not in sys.path:
    sys.path.insert(0, str(_RACINE_PROJET))

from src.acquisition.get_parcelles_rpg import (
    COLONNES_PROJET_RPG,
    COUCHE_DEP_FILTRE,
    _departements,
    get_parcelles_rpg,
)


def dossier_millesime_rpg(
    dossier_racine: str | Path = "data/processed/rpg",
    annee: int = 2025,
) -> Path:
    """
    Retourne le chemin du sous-dossier `rpg20XX` correspondant au millésime `annee`.
    Si `dossier_racine` pointe déjà vers `.../rpg20XX`, il est retourné tel quel.
    """
    p = Path(dossier_racine)
    nom_attendu = f"rpg{annee}"
    if p.name.lower() == nom_attendu.lower():
        return p
    return p / nom_attendu


def _filtrer_colonnes_parquet(
    source: Path,
    destination: Path,
    colonnes: list[str] = COLONNES_PROJET_RPG,
) -> bool:
    """
    Lit un fichier GeoParquet existant, conserve uniquement `colonnes` dans l'ordre
    exact du projet (en préservant les métadonnées GeoParquet) et l'écrit dans `destination`.
    Retourne `True` si une réécriture/déplacement a eu lieu.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    schema_actuel = pq.read_schema(source)
    noms_actuels = schema_actuel.names

    meme_emplacement = source.resolve() == destination.resolve()
    colonnes_identiques = noms_actuels == list(colonnes)

    if meme_emplacement and colonnes_identiques:
        return False

    colonnes_presentes = [c for c in colonnes if c in noms_actuels]
    table = pq.read_table(source, columns=colonnes_presentes)

    tmp = destination.with_suffix(".parquet.tmp")
    pq.write_table(table, tmp)
    tmp.replace(destination)

    if not meme_emplacement and source.exists():
        source.unlink()
    return True


def filtrer_et_organiser_parquets_existants(
    dossier_racine: str | Path = "data/processed/rpg",
    verbose: bool = True,
) -> dict[int, list[Path]]:
    """
    Range tous les fichiers `rpg_{annee}_{dep}.parquet` présents dans `dossier_racine`
    (ou déjà dans `rpg20XX/`) vers leur sous-dossier `data/processed/rpg/rpg{annee}/`
    et filtre leurs colonnes pour ne conserver strictement que les 13 variables
    de `COLONNES_PROJET_RPG`.

    Le fichier `_contours_departements.parquet` est laissé directement à la racine
    de `data/processed/rpg/`.
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
        dossier_cible = dossier_millesime_rpg(racine, annee)
        dst = dossier_cible / src.name
        modifie = _filtrer_colonnes_parquet(src, dst, COLONNES_PROJET_RPG)
        if modifie:
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


def sauvegarder_parcelles_rpg(
    dossier: str | Path = "data/processed/rpg",
    departements: list[str] | None = None,
    annee: int = 2025,
    ecraser: bool = False,
    **kwargs,
) -> list[Path]:
    """
    Appelle `get_parcelles_rpg` département par département et écrit un fichier
    ``data/processed/rpg/rpg{annee}/rpg_{annee}[_bio]_{dep}.parquet`` par département,
    contenant strictement les 13 variables `COLONNES_PROJET_RPG`.

    Les fichiers déjà présents dans `rpg{annee}/` sont sautés (et automatiquement
    filtrés sur les 13 colonnes s'ils contenaient d'anciennes colonnes), ce qui
    permet de reprendre après une coupure réseau.
    """
    dossier_cible = dossier_millesime_rpg(dossier, annee)
    dossier_cible.mkdir(parents=True, exist_ok=True)
    if departements is None:
        departements = sorted(_departements(COUCHE_DEP_FILTRE)["code_dep"])

    suffixe = "_bio" if kwargs.get("bio_uniquement") else ""
    fichiers: list[Path] = []
    t_debut = time.time()
    n_deps = len(departements)

    echecs: list[str] = []

    for idx, dep in enumerate(departements, start=1):
        f = dossier_cible / f"rpg_{annee}{suffixe}_{dep}.parquet"
        if f.exists() and not ecraser:
            _filtrer_colonnes_parquet(f, f, COLONNES_PROJET_RPG)
            print(f"[{idx:>3}/{n_deps}] [{dep}] Déjà présent ({f.relative_to(dossier_cible.parent)})", flush=True)
            fichiers.append(f)
            continue

        gdf = None
        for tentative in range(1, 6):
            try:
                gdf = get_parcelles_rpg(departements=[dep], annee=annee, verbose=True, **kwargs)
                break
            except Exception as err:
                print(
                    f"          [!] Erreur tentative {tentative}/5 sur {dep} ({err}), nouvelle tentative...",
                    flush=True,
                )
                time.sleep(5 * tentative)

        if gdf is None:
            print(f"          [X] Échec temporaire sur {dep}, sera retenté en fin de parcours.", flush=True)
            echecs.append(dep)
            continue

        if len(gdf):
            tmp = f.with_suffix(".parquet.tmp")
            gdf[COLONNES_PROJET_RPG].to_parquet(tmp, index=False)
            tmp.replace(f)
            fichiers.append(f)
            ecoule = (time.time() - t_debut) / 60
            print(
                f"          -> Sauvegardé : {f.relative_to(dossier_cible.parent)} "
                f"({len(gdf):,} parcelles | {ecoule:.1f} min écoulées)",
                flush=True,
            )
        else:
            print(f"[{idx:>3}/{n_deps}] [{dep}] Aucune parcelle retenue pour {dep} en {annee}", flush=True)

    # Relance finale sur les éventuels départements ayant échoué lors du premier passage
    for dep in echecs:
        f = dossier_cible / f"rpg_{annee}{suffixe}_{dep}.parquet"
        try:
            gdf = get_parcelles_rpg(departements=[dep], annee=annee, verbose=True, **kwargs)
            if len(gdf):
                tmp = f.with_suffix(".parquet.tmp")
                gdf[COLONNES_PROJET_RPG].to_parquet(tmp, index=False)
                tmp.replace(f)
                fichiers.append(f)
                print(f"          -> Sauvegardé au second passage : {f.name} ({len(gdf):,} parcelles)", flush=True)
        except Exception as err:
            print(f"          [!] Échec définitif sur {dep} en {annee} : {err}", flush=True)

    return fichiers


if __name__ == "__main__":
    # Exécution directe : télécharge et sauvegarde les millésimes 2013 et 2023 du projet
    # (en sautant automatiquement les départements déjà présents sur le disque).
    DOSSIER_RPG = _RACINE_PROJET / "data" / "processed" / "rpg"
    MILLESIMES_PROJET = (2013, 2023)

    for annee_cible in MILLESIMES_PROJET:
        print("=" * 72, flush=True)
        print(f"Démarrage de l'acquisition du millésime RPG {annee_cible}", flush=True)
        print("=" * 72, flush=True)
        sauvegarder_parcelles_rpg(
            dossier=DOSSIER_RPG,
            annee=annee_cible,
            ecraser=False,
            max_workers=12,
        )
