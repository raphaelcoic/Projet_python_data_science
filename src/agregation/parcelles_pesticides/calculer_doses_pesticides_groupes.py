import pandas as pd

from src.agregation.parcelles_pesticides.constantes_agregation import MOLECULES_PAR_GROUPE


def calculer_doses_pesticides_groupes(parcelles, pesticides):
    """Dose de chaque molécule par hectare de chaque groupe de cultures qui l'utilise, par département et par année.

    parcelles : DataFrame de parcelles_rpg_2023.parquet (code_dep, libelle_groupe, surface_ha).
    pesticides : DataFrame renvoyé par preparer_pesticides (code_dep, annee, substance, quantite_kg).
    Les achats d'une molécule dans un département sont répartis entre les groupes qui l'utilisent
    (MOLECULES_PAR_GROUPE), au prorata de leur surface : tous ces groupes ont la même dose,
    achats / surface des groupes utilisateurs du département. Si le département n'en a aucune
    (Paris, Hauts-de-Seine pour deux molécules), la dose vaut 0 et ces achats ne sont attribués à personne.
    Renvoie un DataFrame : code_dep, annee, libelle_groupe, molecule, dose_kg_ha.
    """
    utilise = pd.DataFrame(
        [(groupe, molecule) for groupe, molecules in MOLECULES_PAR_GROUPE.items() for molecule in molecules],
        columns=["libelle_groupe", "molecule"],
    )
    surfaces = parcelles.groupby(["code_dep", "libelle_groupe"], as_index=False)["surface_ha"].sum()
    eligible = surfaces.merge(utilise, on="libelle_groupe").groupby(["code_dep", "molecule"], as_index=False)["surface_ha"].sum()
    doses = pesticides.rename(columns={"substance": "molecule"}).merge(eligible, on=["code_dep", "molecule"], how="left")
    doses["dose_kg_ha"] = (doses["quantite_kg"] / doses["surface_ha"]).where(doses["surface_ha"] > 0, 0.0)
    return doses.merge(utilise, on="molecule")[["code_dep", "annee", "libelle_groupe", "molecule", "dose_kg_ha"]]
