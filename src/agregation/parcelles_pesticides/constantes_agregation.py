"""Les 10 molécules suivies et les groupes de cultures du RPG qui les utilisent."""

MOLECULES = [
    "glyphosate", "s-metolachlore", "isoproturon", "chlorotoluron",  # herbicides
    "cuivre", "boscalid", "tebuconazole",  # fongicides
    "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",  # insecticides
]

# Colonnes de quantités, en kg de substance active : glyphosate_kg, s_metolachlore_kg, ...
LISTE_COLONNES_MOLECULES = [f"{m.replace('-', '_')}_kg" for m in MOLECULES]

# Molécules utilisées par chaque groupe de cultures du RPG (usages agricoles 2013-2023), d'après les
# homologations E-Phy (Anses) et les guides des instituts techniques (Arvalis, Terres Inovia, IFV, CTIFL).
# Détail des sources : notebooks/exploration/tf_correspondance_groupes_molecules.ipynb
MOLECULES_PAR_GROUPE = {
    "Blé tendre": [
        "glyphosate", "isoproturon", "chlorotoluron",
        "boscalid", "tebuconazole",
        "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Orge": [
        "glyphosate", "isoproturon", "chlorotoluron",
        "boscalid", "tebuconazole",
        "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Maïs grain et ensilage": [
        "glyphosate", "s-metolachlore",
        "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Légumes ou fleurs": [
        # Inclut la pomme de terre, le maraîchage et l'horticulture ornementale
        "glyphosate", "s-metolachlore",
        "cuivre", "boscalid", "tebuconazole",
        "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Autres céréales": [
        # Blé dur, triticale, seigle, avoine + sorgho (s-metolachlore)
        "glyphosate", "s-metolachlore", "isoproturon", "chlorotoluron",
        "boscalid", "tebuconazole",
        "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Divers": [],
    "Prairies permanentes": [],
    "Tournesol": [
        "glyphosate", "s-metolachlore",
        "boscalid",
        "cypermethrine",
    ],
    "Gel (surfaces gelées sans production)": [],
    "Autres cultures industrielles": [
        # Betterave sucrière, chicorée, houblon, tabac, PPAM
        "glyphosate", "s-metolachlore",
        "cuivre", "boscalid", "tebuconazole",
        "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Colza": [
        "glyphosate",
        "boscalid", "tebuconazole",
        "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Fourrage": [
        # Luzerne, trèfle, mélanges fourragers (destruction interculture + ravageurs luzerne)
        "glyphosate",
        "chlorpyriphos-ethyl",
    ],
    "Autres oléagineux": [
        # Soja (s-metolachlore), lin oléagineux, moutarde, navette
        "glyphosate", "s-metolachlore",
        "boscalid", "tebuconazole",
        "cypermethrine",
    ],
    "Prairies temporaires": [
        # Destruction / rénovation avant implantation
        "glyphosate",
    ],
    "Protéagineux": [
        # Pois protéagineux, féverole, lupin
        "glyphosate",
        "boscalid", "tebuconazole",
        "cypermethrine",
    ],
    "Estives et landes": [],
    "Vergers": [
        "glyphosate",
        "cuivre", "boscalid", "tebuconazole",
        "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Plantes à fibres": [
        # Lin fibres, chanvre
        "glyphosate",
        "tebuconazole",
        "cypermethrine",
    ],
    "Légumineuses à grains": [
        # Lentille, pois chiche, haricots/pois secs
        "glyphosate",
        "boscalid", "tebuconazole",
        "cypermethrine",
    ],
    "Vignes": [
        "glyphosate",
        "cuivre", "boscalid", "tebuconazole",
        "imidaclopride", "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Fruits à coque": [
        # Noyer, noisetier, châtaignier, amandier
        "glyphosate",
        "cuivre",
        "cypermethrine", "chlorpyriphos-ethyl",
    ],
    "Oliviers": [
        "glyphosate",
        "cuivre",
        "cypermethrine",
    ],
    "Riz": [
        # Désherbage interculture avant semis
        "glyphosate",
    ],
}
