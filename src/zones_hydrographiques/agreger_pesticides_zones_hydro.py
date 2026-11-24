from src.pesticides.constantes_pesticides import LISTE_COLONNES_MOLECULES, MOLECULES


def agreger_pesticides_zones_hydro(doses, parcelles, parcelles_zones_hydro):
    """Quantités de pesticides attribuées à chaque zone hydrographique, par année.

    doses : DataFrame renvoyé par calculer_doses_pesticides_groupes.
    parcelles : DataFrame de parcelles_rpg_2023.parquet (id_parcelle, code_dep, libelle_groupe, surface_ha).
    parcelles_zones_hydro : DataFrame renvoyé par associer_parcelles_zones_hydro.
    Une parcelle reçoit dose × surface, et une parcelle partagée entre plusieurs zones en donne à
    chacune sa part. Comme la dose ne dépend que du département et du groupe de cultures, on somme
    d'abord les surfaces de chaque zone par département et groupe, puis on les multiplie par les doses.
    Renvoie un DataFrame : code_zone, annee et une colonne par molécule (glyphosate_kg, ..., en kg de substance active).
    """
    surfaces = parcelles_zones_hydro.merge(parcelles[["id_parcelle", "code_dep", "libelle_groupe", "surface_ha"]], on="id_parcelle")
    surfaces["surface_ha"] *= surfaces["part"]
    surfaces = surfaces.groupby(["code_zone", "code_dep", "libelle_groupe"], as_index=False)["surface_ha"].sum()
    lignes = surfaces.merge(doses, on=["code_dep", "libelle_groupe"])
    lignes["kg"] = lignes["surface_ha"] * lignes["dose_kg_ha"]
    kg = lignes.pivot_table(index=["code_zone", "annee"], columns="molecule", values="kg", aggfunc="sum", fill_value=0)
    kg = kg.reindex(columns=MOLECULES, fill_value=0)
    kg.columns = LISTE_COLONNES_MOLECULES
    return kg.reset_index().astype({"annee": "int64"})
