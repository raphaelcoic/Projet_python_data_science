def agreger_pesticides_zones(parcelles_pesticides, parcelles_zones):
    """Somme par zone hydrographique et par année les quantités de pesticides attribuées aux parcelles.

    parcelles_pesticides : DataFrame d'un ou plusieurs fichiers parcelles_pesticides_<annee>.parquet
    (id_parcelle, annee et les colonnes *_kg).
    parcelles_zones : DataFrame renvoyé par associer_parcelles_zones.
    Une parcelle partagée entre plusieurs zones donne à chacune sa part des quantités.
    Renvoie un DataFrame : code_zone, annee et les colonnes *_kg (en kg de substance active).
    """
    colonnes = [c for c in parcelles_pesticides.columns if c.endswith("_kg")]
    lignes = parcelles_pesticides.merge(parcelles_zones, on="id_parcelle")
    lignes[colonnes] = lignes[colonnes].mul(lignes["part"], axis=0)
    return lignes.groupby(["code_zone", "annee"], as_index=False)[colonnes].sum().astype({"annee": "int64"})
