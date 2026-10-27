"""
Acquisition et sauvegarde incrémentale en GeoParquet des millésimes du RPG,
un fichier par département, filtrés sur les 13 variables du projet.

Arborescence produite :
    data/processed/rpg/
    ├── _contours_departements.parquet
    ├── rpg2013/
    │   ├── rpg_2013_01.parquet
    │   └── ...
    └── rpg2023/
        ├── rpg_2023_01.parquet
        └── ...

Exécution directe (depuis la racine du dépôt) :
    python -m src.agriculture.sauvegarder_parcelles_rpg
"""

from __future__ import annotations

import time
from pathlib import Path

from src.agriculture.constantes_rpg import COLONNES_PROJET_RPG, COUCHE_DEP_FILTRE, DOSSIER_RPG
from src.agriculture.dossier_millesime_rpg import dossier_millesime_rpg
from src.agriculture.filtrer_colonnes_parquet import filtrer_colonnes_parquet
from src.agriculture.recuperer_departements_ign import recuperer_departements_ign
from src.agriculture.recuperer_parcelles_rpg import recuperer_parcelles_rpg


def _ecrire(gdf, f: Path) -> None:
    """Écrit le fichier départemental de façon atomique (fichier temporaire puis renommage)."""
    tmp = f.with_suffix(".parquet.tmp")
    gdf[COLONNES_PROJET_RPG].to_parquet(tmp, index=False)
    tmp.replace(f)


def sauvegarder_parcelles_rpg(
    dossier: str | Path = DOSSIER_RPG,
    departements: list[str] | None = None,
    annee: int = 2025,
    ecraser: bool = False,
    **kwargs,
) -> list[Path]:
    """
    Appelle `recuperer_parcelles_rpg` département par département et écrit un fichier
    ``data/processed/rpg/rpg{annee}/rpg_{annee}[_bio]_{dep}.parquet`` par département,
    contenant strictement les 13 variables `COLONNES_PROJET_RPG`.

    Les fichiers déjà présents dans `rpg{annee}/` sont sautés (et automatiquement
    filtrés sur les 13 colonnes s'ils contenaient d'anciennes colonnes), ce qui
    permet de reprendre après une coupure réseau.
    """
    dossier_cible = dossier_millesime_rpg(dossier, annee)
    dossier_cible.mkdir(parents=True, exist_ok=True)
    if departements is None:
        departements = sorted(recuperer_departements_ign(COUCHE_DEP_FILTRE)["code_dep"])

    suffixe = "_bio" if kwargs.get("bio_uniquement") else ""
    fichiers: list[Path] = []
    t_debut = time.time()
    n_deps = len(departements)
    echecs: list[str] = []

    for idx, dep in enumerate(departements, start=1):
        f = dossier_cible / f"rpg_{annee}{suffixe}_{dep}.parquet"
        if f.exists() and not ecraser:
            filtrer_colonnes_parquet(f, f, COLONNES_PROJET_RPG)
            print(f"[{idx:>3}/{n_deps}] [{dep}] Déjà présent ({f.relative_to(dossier_cible.parent)})", flush=True)
            fichiers.append(f)
            continue

        gdf = None
        for tentative in range(1, 6):
            try:
                gdf = recuperer_parcelles_rpg(departements=[dep], annee=annee, verbose=True, **kwargs)
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
            _ecrire(gdf, f)
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
            gdf = recuperer_parcelles_rpg(departements=[dep], annee=annee, verbose=True, **kwargs)
            if len(gdf):
                _ecrire(gdf, f)
                fichiers.append(f)
                print(f"          -> Sauvegardé au second passage : {f.name} ({len(gdf):,} parcelles)", flush=True)
        except Exception as err:
            print(f"          [!] Échec définitif sur {dep} en {annee} : {err}", flush=True)

    return fichiers


if __name__ == "__main__":
    # Télécharge les millésimes 2013 et 2023 du projet (les départements déjà présents sont sautés).
    for annee_cible in (2013, 2023):
        print("=" * 72, flush=True)
        print(f"Démarrage de l'acquisition du millésime RPG {annee_cible}", flush=True)
        print("=" * 72, flush=True)
        sauvegarder_parcelles_rpg(annee=annee_cible, ecraser=False, max_workers=12)
