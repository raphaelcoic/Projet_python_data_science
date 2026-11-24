"""Orchestration complète : génère une table Parquet par année (2013–2023) et vérifie la conservation."""

import argparse
import time
from pathlib import Path

import pandas as pd

from src.agregation.calculer_doses_pesticides_groupes import (
    calculer_doses_pesticides_groupes,
)
from src.agregation.constantes_agregation import (
    CHEMIN_CORRESPONDANCE_DEFAUT,
    CHEMIN_DOSES_DEFAUT,
    CHEMIN_PARCELLES_DEFAUT,
    CHEMIN_PESTICIDES_DEFAUT,
    COLONNES_MOLECULES,
    DOSSIER_SORTIE_DEFAUT,
    MOLECULES,
)
from src.agregation.construire_parcelles_pesticides_annee import (
    construire_parcelles_pesticides_annee,
)


def construire_parcelles_pesticides(
    annees=None,
    chemin_parcelles=CHEMIN_PARCELLES_DEFAUT,
    chemin_pesticides=CHEMIN_PESTICIDES_DEFAUT,
    chemin_correspondance=CHEMIN_CORRESPONDANCE_DEFAUT,
    chemin_doses=CHEMIN_DOSES_DEFAUT,
    dossier_sortie=DOSSIER_SORTIE_DEFAUT,
    taille_lot=500_000,
):
    """Exécute le pipeline d'agrégation parcelles × pesticides et produit un Parquet par année.

    Paramètres
    ----------
    annees : list[int] ou None
        Liste d'années à générer. Si ``None``, traite toutes les années présentes dans
        ``pesticides.parquet`` (2013 à 2023).
    taille_lot : int
        Taille des lots de lecture/écriture streaming (défaut : 500 000 parcelles).

    Renvoie
    -------
    pd.DataFrame
        Tableau récapitulatif par année (fichier, taille en Mo, nombre de lignes,
        écart relatif maximal de conservation des quantités).
    """
    t0 = time.time()

    print("1/3 — Calcul des doses par (code_dep, annee, libelle_groupe)...")
    doses, non_alloue = calculer_doses_pesticides_groupes(
        chemin_parcelles=chemin_parcelles,
        chemin_pesticides=chemin_pesticides,
        chemin_correspondance=chemin_correspondance,
        chemin_sortie=chemin_doses,
    )
    print(f"    Table des doses enregistrée : {chemin_doses} ({len(doses):,} lignes)")

    if not non_alloue.empty:
        total_na = non_alloue["quantite_non_allouee_kg"].sum()
        print(
            f"    Note : {len(non_alloue)} triplets (dep, annee, molecule) ont une surface "
            f"éligible nulle (total non allouable : {total_na:,.2f} kg)."
        )

    # Totaux attendus (allouables) par année et molécule pour contrôle de conservation de masse
    df_pest = pd.read_parquet(Path(chemin_pesticides))
    totaux_bruts = (
        df_pest.groupby(["annee", "substance"])["quantite_totale"]
        .sum()
        .unstack(fill_value=0.0)
        .reindex(columns=MOLECULES, fill_value=0.0)
    )
    totaux_non_alloues = (
        non_alloue.groupby(["annee", "molecule"])["quantite_non_allouee_kg"]
        .sum()
        .unstack(fill_value=0.0)
        .reindex(index=totaux_bruts.index, columns=MOLECULES, fill_value=0.0)
        if not non_alloue.empty
        else pd.DataFrame(0.0, index=totaux_bruts.index, columns=MOLECULES)
    )
    totaux_attendus = totaux_bruts - totaux_non_alloues

    annees_cibles = (
        sorted(int(a) for a in doses["annee"].unique())
        if annees is None
        else sorted(int(a) for a in annees)
    )

    print(f"2/3 — Génération des tables parcellaires annuelles ({len(annees_cibles)} années)...")
    bilans = []
    for annee in annees_cibles:
        t_an = time.time()
        res = construire_parcelles_pesticides_annee(
            annee=annee,
            doses=doses,
            chemin_parcelles=chemin_parcelles,
            dossier_sortie=dossier_sortie,
            taille_lot=taille_lot,
        )

        # Contrôle de conservation de masse sur les 10 molécules pour cette année
        ecart_rel_max = 0.0
        for m in MOLECULES:
            attendu = float(totaux_attendus.loc[annee, m])
            obtenu = res["sommes_kg"][COLONNES_MOLECULES[m]]
            if attendu > 0:
                ecart_rel = abs(obtenu - attendu) / attendu
                ecart_rel_max = max(ecart_rel_max, ecart_rel)

        duree_an = time.time() - t_an
        print(
            f"    [{annee}] {res['nb_lignes']:,} lignes | {res['taille_mo']:.1f} Mo | "
            f"écart masse max = {ecart_rel_max:.2e} | {duree_an:.1f} s"
        )
        bilans.append({
            "annee": annee,
            "chemin": res["chemin"],
            "taille_mo": res["taille_mo"],
            "nb_lignes": res["nb_lignes"],
            "nb_negatifs": res["nb_negatifs"],
            "nb_non_finis": res["nb_non_finis"],
            "ecart_masse_rel_max": ecart_rel_max,
        })

    df_bilan = pd.DataFrame(bilans)
    duree_totale = time.time() - t0
    print(
        f"3/3 — Terminé en {duree_totale:.1f} s : {len(df_bilan)} fichiers générés dans "
        f"{dossier_sortie} ({df_bilan['taille_mo'].sum():.1f} Mo au total)."
    )
    return df_bilan


def _parser_arguments():
    parser = argparse.ArgumentParser(
        description="Construit les tables Parquet annuelles parcelles × pesticides."
    )
    parser.add_argument(
        "--annees",
        nargs="+",
        type=int,
        default=None,
        help="Années à générer (par défaut : toutes les années de pesticides.parquet).",
    )
    parser.add_argument(
        "--taille-lot",
        type=int,
        default=500_000,
        help="Nombre de parcelles traitées par lot en mémoire (défaut : 500000).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parser_arguments()
    construire_parcelles_pesticides(annees=args.annees, taille_lot=args.taille_lot)
