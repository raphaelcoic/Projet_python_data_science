"""Calcul des doses moyennes par hectare pour chaque (département, année, groupe RPG)."""

from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from src.agregation.parcelles_pesticides.charger_matrice_correspondance import (
    charger_matrice_correspondance,
)
from src.agregation.parcelles_pesticides.constantes_agregation import (
    CHEMIN_CORRESPONDANCE_DEFAUT,
    CHEMIN_DOSES_DEFAUT,
    CHEMIN_PARCELLES_DEFAUT,
    CHEMIN_PESTICIDES_DEFAUT,
    MOLECULES,
)


def _agreger_surfaces_dep_groupe(chemin_parcelles, taille_lot=1_000_000):
    """Calcule la surface totale (en ha) par (code_dep, libelle_groupe) en lecture par lots."""
    fichier = pq.ParquetFile(Path(chemin_parcelles))
    cumul = {}

    for lot in fichier.iter_batches(
        batch_size=taille_lot,
        columns=["code_dep", "libelle_groupe", "surface_ha"],
    ):
        df_lot = lot.to_pandas()
        sommes = df_lot.groupby(["code_dep", "libelle_groupe"], sort=False)["surface_ha"].sum()
        for cle, val in sommes.items():
            cumul[cle] = cumul.get(cle, 0.0) + float(val)

    index = pd.MultiIndex.from_tuples(list(cumul.keys()), names=["code_dep", "libelle_groupe"])
    surfaces = pd.Series(list(cumul.values()), index=index, name="surface_groupe_ha")
    return surfaces.unstack(fill_value=0.0)


def calculer_doses_pesticides_groupes(
    chemin_parcelles=CHEMIN_PARCELLES_DEFAUT,
    chemin_pesticides=CHEMIN_PESTICIDES_DEFAUT,
    chemin_correspondance=CHEMIN_CORRESPONDANCE_DEFAUT,
    chemin_sortie=CHEMIN_DOSES_DEFAUT,
):
    """Calcule la table des doses (kg/ha) par (code_dep, annee, libelle_groupe) et molécule.

    Formule pour un département ``d``, une année ``t``, un groupe ``g`` et une molécule ``m`` :
    - Surface éligible du département : ``S_{d,m}^{elig} = sum_{g'} I_{g',m} * S_{d,g'}``
    - Tonnage alloué au groupe ``g`` : ``Q_{d,t,m,g} = I_{g,m} * Q_{d,t,m} * S_{d,g} / S_{d,m}^{elig}``
    - Dose par hectare du groupe ``g`` : ``D_{d,t,m,g} = Q_{d,t,m,g} / S_{d,g} = I_{g,m} * Q_{d,t,m} / S_{d,m}^{elig}``

    Lorsque ``S_{d,m}^{elig} == 0`` (ex. Paris ``75`` ou Hauts-de-Seine ``92`` pour certaines
    molécules), la dose est fixée à ``0.0`` et le tonnage non alloué est recensé dans le
    second DataFrame renvoyé.

    Renvoie
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        ``(doses, non_alloue)`` où ``doses`` a pour clé ``(code_dep, annee, libelle_groupe)``
        et contient ``surface_groupe_ha`` ainsi que les 10 colonnes ``dose_<molecule>_kg_ha``.
    """
    matrice = charger_matrice_correspondance(chemin_correspondance)
    groupes = list(matrice.index)

    # 1. Surfaces S_{d,g} en lecture par lots (faible empreinte mémoire)
    surfaces_dg = _agreger_surfaces_dep_groupe(chemin_parcelles)
    groupes_rpg = set(surfaces_dg.columns)
    groupes_mat = set(groupes)
    if groupes_rpg != groupes_mat:
        raise ValueError(
            f"Désaccord sur les libellés de groupes RPG. "
            f"RPG uniquement : {sorted(groupes_rpg - groupes_mat)} ; "
            f"Correspondance uniquement : {sorted(groupes_mat - groupes_rpg)}"
        )
    surfaces_dg = surfaces_dg.reindex(columns=groupes, fill_value=0.0).sort_index()

    # 2. Surfaces éligibles par département et molécule : S_{d,m}^{elig} (94 × 10)
    surfaces_eligibles = surfaces_dg.dot(matrice.astype("float64"))

    # 3. Achats départementaux Q_{d,t,m} en format large (code_dep, annee) × 10 molécules
    df_pest = pd.read_parquet(Path(chemin_pesticides))
    df_pest = df_pest.rename(columns={"geocode_departement": "code_dep"})

    deps_rpg = set(surfaces_dg.index)
    deps_pest = set(df_pest["code_dep"].unique())
    if deps_rpg != deps_pest:
        raise ValueError(
            f"Désaccord sur les départements. "
            f"RPG uniquement : {sorted(deps_rpg - deps_pest)} ; "
            f"Pesticides uniquement : {sorted(deps_pest - deps_rpg)}"
        )

    annees = sorted(int(a) for a in df_pest["annee"].unique())
    departements = sorted(deps_rpg)

    achats = (
        df_pest.pivot_table(
            index=["code_dep", "annee"],
            columns="substance",
            values="quantite_totale",
            aggfunc="sum",
            fill_value=0.0,
        )
        .reindex(
            index=pd.MultiIndex.from_product([departements, annees], names=["code_dep", "annee"]),
            columns=MOLECULES,
            fill_value=0.0,
        )
    )

    # 4. Calcul des doses départementales D_{d,t,m} = Q_{d,t,m} / S_{d,m}^{elig}
    elig_aligne = surfaces_eligibles.reindex(achats.index.get_level_values("code_dep")).to_numpy()
    q_arr = achats.to_numpy(dtype="float64")

    with np.errstate(divide="ignore", invalid="ignore"):
        doses_dep_arr = np.where(elig_aligne > 0.0, q_arr / elig_aligne, 0.0)

    # Journal des quantités impossibles à allouer (Q > 0 mais S_elig == 0)
    masque_non_alloue = (q_arr > 0.0) & (elig_aligne == 0.0)
    lignes_non_alloue = []
    idx_dep = achats.index.get_level_values("code_dep")
    idx_an = achats.index.get_level_values("annee")
    for i, j in zip(*np.where(masque_non_alloue)):
        lignes_non_alloue.append({
            "code_dep": idx_dep[i],
            "annee": int(idx_an[i]),
            "molecule": MOLECULES[j],
            "quantite_non_allouee_kg": float(q_arr[i, j]),
        })
    non_alloue = pd.DataFrame(
        lignes_non_alloue,
        columns=["code_dep", "annee", "molecule", "quantite_non_allouee_kg"],
    )

    # 5. Expansion vers (code_dep, annee, libelle_groupe) : D_{d,t,m,g} = I_{g,m} * D_{d,t,m}
    n_dep_an = len(achats)
    n_groupes = len(groupes)
    mat_arr = matrice.to_numpy(dtype="float64")  # (n_groupes, 10)

    # Produit tensoriel : (n_dep_an, 1, 10) * (1, n_groupes, 10) -> (n_dep_an * n_groupes, 10)
    doses_3d = doses_dep_arr[:, np.newaxis, :] * mat_arr[np.newaxis, :, :]
    doses_2d = doses_3d.reshape(n_dep_an * n_groupes, len(MOLECULES))

    colonnes_doses = [f"dose_{m.replace('-', '_')}_kg_ha" for m in MOLECULES]
    df_doses = pd.DataFrame(doses_2d, columns=colonnes_doses)
    df_doses.insert(0, "libelle_groupe", np.tile(groupes, n_dep_an))
    df_doses.insert(0, "annee", np.repeat(idx_an.to_numpy(dtype="int16"), n_groupes))
    df_doses.insert(0, "code_dep", np.repeat(idx_dep.to_numpy(), n_groupes))

    # Ajout de la surface totale du groupe dans le département S_{d,g}
    surf_long = (
        surfaces_dg.stack()
        .rename("surface_groupe_ha")
        .reset_index()
    )
    df_doses = df_doses.merge(surf_long, on=["code_dep", "libelle_groupe"], how="left")
    ordre_cols = ["code_dep", "annee", "libelle_groupe", "surface_groupe_ha", *colonnes_doses]
    df_doses = df_doses[ordre_cols]

    if chemin_sortie is not None:
        chemin_sortie = Path(chemin_sortie)
        chemin_sortie.parent.mkdir(parents=True, exist_ok=True)
        temporaire = chemin_sortie.with_suffix(".parquet.tmp")
        try:
            df_doses.to_parquet(temporaire, index=False, compression="zstd")
            temporaire.replace(chemin_sortie)
        finally:
            if temporaire.exists():
                temporaire.unlink()

    return df_doses, non_alloue
