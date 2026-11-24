"""Construction en streaming (faible mémoire) de la table parcelles × pesticides pour une année."""

import gc
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from src.agregation.parcelles_pesticides.constantes_agregation import (
    CHEMIN_PARCELLES_DEFAUT,
    COLONNES_MOLECULES,
    COLONNES_PARCELLES_CONSERVEES,
    DOSSIER_SORTIE_DEFAUT,
    LISTE_COLONNES_MOLECULES,
    MOLECULES,
)


def construire_parcelles_pesticides_annee(
    annee,
    doses,
    chemin_parcelles=CHEMIN_PARCELLES_DEFAUT,
    dossier_sortie=DOSSIER_SORTIE_DEFAUT,
    taille_lot=500_000,
):
    """Construit et enregistre ``parcelles_pesticides_<annee>.parquet`` par lots.

    Lit ``parcelles_rpg_2023.parquet`` par lots de ``taille_lot`` lignes (sans jamais charger
    les 9,74 millions de parcelles × 17 colonnes simultanément en RAM), retire ``code_culture``
    et ``categorie_culture``, ajoute ``annee`` (``int16``) et les 10 colonnes molécules
    (``float32``, en kg), puis écrit au fil de l'eau en Parquet compressé ZSTD.

    Paramètres
    ----------
    annee : int
        Année des ventes de pesticides (ex. ``2023``).
    doses : pd.DataFrame
        Table renvoyée par ``calculer_doses_pesticides_groupes``.
    chemin_parcelles : str ou Path
        Chemin vers ``parcelles_rpg_2023.parquet``.
    dossier_sortie : str ou Path
        Dossier où écrire ``parcelles_pesticides_<annee>.parquet``.
    taille_lot : int
        Nombre de parcelles traitées par lot en mémoire (défaut : 500 000).

    Renvoie
    -------
    dict
        Résumé de contrôle qualité pour l'année (chemin, nombre de lignes, sommes totales
        par molécule en ``float64``, valeurs négatives ou manquantes).
    """
    annee = int(annee)
    doses_an = doses[doses["annee"] == annee]
    if doses_an.empty:
        raise ValueError(f"Aucune dose disponible pour l'année {annee}.")

    # Préparation d'une table de recherche dense (n_dep, n_groupes, 10) en float64
    deps = sorted(doses_an["code_dep"].unique())
    groupes = sorted(doses_an["libelle_groupe"].unique())
    dep_vers_idx = {d: i for i, d in enumerate(deps)}
    grp_vers_idx = {g: i for i, g in enumerate(groupes)}

    colonnes_doses = [f"dose_{m.replace('-', '_')}_kg_ha" for m in MOLECULES]
    grille_doses = np.zeros((len(deps), len(groupes), len(MOLECULES)), dtype=np.float64)

    idx_d = doses_an["code_dep"].map(dep_vers_idx).to_numpy()
    idx_g = doses_an["libelle_groupe"].map(grp_vers_idx).to_numpy()
    grille_doses[idx_d, idx_g, :] = doses_an[colonnes_doses].to_numpy(dtype=np.float64)

    dossier_sortie = Path(dossier_sortie)
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    chemin_sortie = dossier_sortie / f"parcelles_pesticides_{annee}.parquet"
    temporaire = chemin_sortie.with_suffix(".parquet.tmp")

    schema = pa.schema([
        ("id_parcelle", pa.string()),
        ("annee", pa.int16()),
        ("code_dep", pa.string()),
        ("nom_dep", pa.string()),
        ("surface_ha", pa.float64()),
        ("code_groupe", pa.string()),
        ("libelle_groupe", pa.string()),
        *[(col, pa.float32()) for col in LISTE_COLONNES_MOLECULES],
    ])

    fichier_source = pq.ParquetFile(Path(chemin_parcelles))
    nb_lignes = 0
    nb_negatifs = 0
    nb_non_finis = 0
    sommes_molecules = np.zeros(len(MOLECULES), dtype=np.float64)

    try:
        with pq.ParquetWriter(
            temporaire,
            schema=schema,
            compression="zstd",
            use_dictionary=True,
        ) as ecrivain:
            for lot in fichier_source.iter_batches(
                batch_size=taille_lot,
                columns=COLONNES_PARCELLES_CONSERVEES,
            ):
                df_lot = lot.to_pandas()
                n = len(df_lot)
                nb_lignes += n

                codes_dep = df_lot["code_dep"].map(dep_vers_idx).to_numpy()
                codes_grp = df_lot["libelle_groupe"].map(grp_vers_idx).to_numpy()
                if (codes_dep < 0).any() or np.isnan(codes_dep).any():
                    raise ValueError("Département inconnu détecté dans les parcelles.")
                if (codes_grp < 0).any() or np.isnan(codes_grp).any():
                    raise ValueError("Groupe de cultures inconnu détecté dans les parcelles.")

                surfaces = df_lot["surface_ha"].to_numpy(dtype=np.float64)
                # Calcul en float64 pour la précision, puis stockage en float32 pour économiser 50 % d'espace
                quantites_f64 = grille_doses[codes_dep, codes_grp, :] * surfaces[:, np.newaxis]
                quantites_f32 = quantites_f64.astype(np.float32)

                nb_negatifs += int((quantites_f32 < 0).sum())
                nb_non_finis += int((~np.isfinite(quantites_f32)).sum())
                sommes_molecules += quantites_f32.sum(axis=0, dtype=np.float64)

                colonnes_arrow = {
                    "id_parcelle": pa.array(df_lot["id_parcelle"], type=pa.string()),
                    "annee": pa.array(np.full(n, annee, dtype=np.int16), type=pa.int16()),
                    "code_dep": pa.array(df_lot["code_dep"], type=pa.string()),
                    "nom_dep": pa.array(df_lot["nom_dep"], type=pa.string()),
                    "surface_ha": pa.array(surfaces, type=pa.float64()),
                    "code_groupe": pa.array(df_lot["code_groupe"], type=pa.string()),
                    "libelle_groupe": pa.array(df_lot["libelle_groupe"], type=pa.string()),
                }
                for j, col_nom in enumerate(LISTE_COLONNES_MOLECULES):
                    colonnes_arrow[col_nom] = pa.array(quantites_f32[:, j], type=pa.float32())

                ecrivain.write_table(pa.table(colonnes_arrow, schema=schema))

                del df_lot, quantites_f64, quantites_f32, colonnes_arrow

        temporaire.replace(chemin_sortie)
    finally:
        if temporaire.exists():
            temporaire.unlink()
        gc.collect()

    return {
        "annee": annee,
        "chemin": str(chemin_sortie),
        "taille_mo": round(chemin_sortie.stat().st_size / (1024 * 1024), 2),
        "nb_lignes": nb_lignes,
        "nb_negatifs": nb_negatifs,
        "nb_non_finis": nb_non_finis,
        "sommes_kg": {
            COLONNES_MOLECULES[m]: float(sommes_molecules[j])
            for j, m in enumerate(MOLECULES)
        },
    }
