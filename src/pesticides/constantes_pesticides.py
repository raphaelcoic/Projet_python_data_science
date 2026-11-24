"""Les 10 molécules suivies, choisies pour leur effet sur les cours d'eau (notebook tf_selection_molecules_eau)."""

MOLECULES = [
    "glyphosate", "s-metolachlore", "isoproturon", "chlorotoluron",  # herbicides
    "cuivre", "boscalid", "tebuconazole",  # fongicides
    "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",  # insecticides
]

# Colonnes de quantités, en kg de substance active : glyphosate_kg, s_metolachlore_kg, ...
LISTE_COLONNES_MOLECULES = [f"{m.replace('-', '_')}_kg" for m in MOLECULES]
