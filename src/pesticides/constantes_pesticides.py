"""Les 10 molécules suivies, choisies pour leur effet sur les cours d'eau (notebook tf_selection_molecules_eau)."""

MOLECULES = [
    "glyphosate", "s-metolachlore", "isoproturon", "chlorotoluron",  # herbicides
    "cuivre", "boscalid", "tebuconazole",  # fongicides
    "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",  # insecticides
]

# Colonnes de quantités, en kg de substance active : glyphosate_kg, s_metolachlore_kg, ...
LISTE_COLONNES_MOLECULES = [f"{m.replace('-', '_')}_kg" for m in MOLECULES]

# Les 8 sels de cuivre de la BNV-D, regroupés sous le libellé "cuivre"
VARIANTES_CUIVRE = [
    "cuivre de l'hydroxyde de cuivre",
    "cuivre de l'oxychlorure de cuivre",
    "cuivre de l'oxychlorure de cuivre (trihydroxychlorure de dicuivre)",
    "cuivre de l'oxyde cuivreux",
    "cuivre du sulfate de cuivre",
    "cuivre du sulfate tetracuivrique et tricalcique",
    "cuivre du sulfate tribasique",
    "cuivre du tallate de cuivre",
]

# Hors du périmètre : Corse et départements d'outre-mer
DEPARTEMENTS_EXCLUS = ["2A", "2B", "971", "972", "973", "974", "976"]
