"""
Constantes et référentiels partagés par les fonctions RPG (Registre Parcellaire Graphique).

Source : https://www.data.gouv.fr/datasets/rpg (IGN / ASP), servi par le WFS de la Géoplateforme.
"""

from pathlib import Path

WFS_URL = "https://data.geopf.fr/wfs/ows"
PAGE_SIZE = 5000  # maximum imposé par le serveur WFS de la Géoplateforme

# Couches départementales ADMIN-EXPRESS (même service WFS)
COUCHE_DEP_FILTRE = "ADMINEXPRESS-COG-CARTO-PE.LATEST:departement"  # très simplifiée -> filtre serveur
COUCHE_DEP_ATTRIB = "ADMINEXPRESS-COG-CARTO.LATEST:departement"  # plus précise -> attribution du département

# Dossier des fichiers RPG et cache local des contours départementaux (précis)
DOSSIER_RPG = Path("data/processed/rpg")
CHEMIN_CACHE_CONTOURS_DEP = DOSSIER_RPG / "_contours_departements.parquet"

# Les 13 variables strictement retenues pour le projet
COLONNES_PROJET_RPG: list[str] = [
    "id_parcelle",
    "annee",
    "code_dep",
    "nom_dep",
    "surface_ha",
    "categorie_culture",
    "libelle_categorie",
    "code_culture",
    "libelle_culture",
    "code_groupe",
    "libelle_groupe",
    "bio",
    "geometry",
]

# Les 12 variables tabulaires (sans `geometry`, pour les fichiers nationaux allégés)
COLONNES_TABULAIRES_RPG: list[str] = [col for col in COLONNES_PROJET_RPG if col != "geometry"]

# Libellés des grandes catégories de culture (champ cat_cult_p)
CATEGORIES_CULTURE: dict[str, str] = {
    "TA": "Terres arables",
    "PP": "Prairies permanentes",
    "CP": "Cultures permanentes",
    "SB": "Surfaces boisées",
}

# Référentiel harmonisé des 28 groupes de cultures du RPG (utilisé notamment pour 2013 et en secours)
LIBELLES_GROUPES_RPG: dict[str, str] = {
    "1": "Blé tendre",
    "2": "Maïs grain et ensilage",
    "3": "Orge",
    "4": "Autres céréales",
    "5": "Colza",
    "6": "Tournesol",
    "7": "Autres oléagineux",
    "8": "Protéagineux",
    "9": "Plantes à fibres",
    "10": "Semences",
    "11": "Gel (surfaces gelées sans production)",
    "12": "Gel industriel",
    "13": "Autres gels",
    "14": "Riz",
    "15": "Légumineuses à grains",
    "16": "Fourrage",
    "17": "Estives et landes",
    "18": "Prairies permanentes",
    "19": "Prairies temporaires",
    "20": "Vergers",
    "21": "Vignes",
    "22": "Fruits à coque",
    "23": "Oliviers",
    "24": "Autres cultures industrielles",
    "25": "Légumes ou fleurs",
    "26": "Canne à sucre",
    "27": "Arboriculture",
    "28": "Divers",
}

# Correspondance Groupe de cultures -> Grande catégorie de culture (TA, PP, CP, NA)
GROUPE_VERS_CATEGORIE: dict[str, str] = {
    "1": "TA", "2": "TA", "3": "TA", "4": "TA", "5": "TA",
    "6": "TA", "7": "TA", "8": "TA", "9": "TA", "10": "TA",
    "11": "TA", "12": "TA", "13": "TA", "14": "TA", "15": "TA",
    "16": "TA", "17": "PP", "18": "PP", "19": "TA",
    "20": "CP", "21": "CP", "22": "CP", "23": "CP",
    "24": "TA", "25": "TA", "26": "CP", "27": "CP", "28": "NA",
}

# Correspondance exacte Code culture (3 lettres) -> Grande catégorie de culture (issue du RPG 2025 + PAC)
CULTURE_VERS_CATEGORIE: dict[str, str] = {
    "AAR": "TA", "ACA": "TA", "ACP": "CP", "AFG": "TA", "AGR": "CP", "AIL": "TA",
    "AME": "TA", "ANA": "TA", "ARA": "TA", "ARP": "CP", "ART": "TA", "AVH": "TA",
    "AVO": "CP", "AVP": "TA", "BCA": "CP", "BCF": "CP", "BCI": "CP", "BCP": "CP",
    "BCR": "CP", "BDH": "TA", "BDP": "TA", "BDT": "TA", "BEA": "CP", "BEF": "CP",
    "BEI": "CP", "BEP": "CP", "BER": "CP", "BFP": "TA", "BFS": "NA", "BOR": "NA",
    "BOP": "PP", "BTA": "NA", "BTH": "TA", "BTN": "TA", "BTP": "TA", "BVF": "TA",
    "CAB": "CP", "CAC": "CP", "CAE": "PP", "CAF": "TA", "CAG": "TA", "CAH": "TA",
    "CAR": "TA", "CBT": "CP", "CCN": "TA", "CEE": "PP", "CEL": "TA", "CHU": "TA",
    "CHV": "TA", "CML": "TA", "CPL": "TA", "CSA": "CP", "CSF": "CP", "CSI": "CP",
    "CSP": "CP", "CSR": "CP", "CSS": "NA", "CTG": "CP", "CZH": "TA", "CZP": "TA",
    "EPE": "TA", "EPI": "TA", "FEV": "TA", "FLA": "TA", "FLP": "CP", "FNU": "TA",
    "FRA": "TA", "FVL": "TA", "FVP": "TA", "GES": "TA", "GRA": "TA", "HBL": "CP",
    "HPC": "TA", "J5M": "TA", "J6P": "TA", "J6S": "TA", "JAC": "TA", "JNO": "TA",
    "LAV": "CP", "LBF": "TA", "LDH": "TA", "LDP": "TA", "LEC": "TA", "LIF": "TA",
    "LIH": "TA", "LIP": "TA", "LOT": "TA", "LUZ": "TA", "MCR": "TA", "MCS": "TA",
    "MCT": "CP", "MDI": "TA", "MID": "TA", "MIE": "TA", "MIS": "TA", "MLC": "TA",
    "MLF": "TA", "MLG": "TA", "MLO": "TA", "MLS": "TA", "MLT": "TA", "MOH": "TA",
    "MOT": "TA", "MPA": "TA", "MPC": "TA", "MRS": "NA", "MSW": "CP", "NOS": "CP",
    "NOX": "CP", "NVT": "TA", "NYG": "TA", "OAG": "TA", "OEI": "TA", "OHR": "TA",
    "OIG": "TA", "OLI": "CP", "ORH": "TA", "ORP": "TA", "PAG": "TA", "PCH": "TA",
    "PCL": "TA", "PEP": "CP", "PEV": "CP", "PFR": "CP", "PHF": "TA", "PHI": "TA",
    "PHS": "TA", "PIS": "CP", "PME": "CP", "POR": "TA", "POT": "TA", "PPH": "PP",
    "PPP": "CP", "PPR": "TA", "PRF": "CP", "PRL": "PP", "PRU": "CP", "PSL": "TA",
    "PTC": "TA", "PTR": "TA", "PVP": "TA", "PVT": "CP", "PWT": "CP", "RDI": "TA",
    "RGA": "TA", "RIZ": "TA", "ROS": "CP", "RVI": "CP", "SAG": "NA", "SAI": "TA",
    "SBO": "SB", "SGH": "TA", "SGP": "TA", "SHD": "CP", "SIN": "NA", "SNA": "NA",
    "SNE": "NA", "SNU": "NA", "SOG": "TA", "SOJ": "TA", "SPH": "PP", "SPL": "PP",
    "SRS": "TA", "TAB": "TA", "TBT": "TA", "TCR": "CP", "TOM": "TA", "TRE": "TA",
    "TRN": "TA", "TRU": "CP", "TTH": "TA", "TTP": "TA", "VES": "TA", "VET": "CP",
    "VGD": "CP", "VNL": "CP", "VRC": "CP", "VRG": "CP", "VRN": "CP", "VRT": "CP",
    "ZZZ": "NA",
}

# Seule l'édition 2025 (RPG v4) du WFS contient le label bio au niveau de la parcelle.
ANNEES_AVEC_BIO = {2025}

# Départements d'Outre-Mer (DROM)
DEPARTEMENTS_OUTRE_MER = {"971", "972", "973", "974", "976"}

# Départements exclus du périmètre d'étude des fichiers nationaux (DROM + Corse)
DEPARTEMENTS_EXCLUS_DEFAUT: tuple[str, ...] = ("2A", "2B", "971", "972", "973", "974", "976")

# Palette qualitative distincte (28 couleurs lisibles pour les groupes de cultures)
PALETTE_GROUPES = [
    "#31a354", "#2b8cbe", "#e34a33", "#feb24c", "#756bb1",
    "#fd8d3c", "#41b6c4", "#dd1c77", "#addd8e", "#636363",
    "#8856a7", "#a6611a", "#018571", "#d7191c", "#2c7bb6",
    "#fdae61", "#abd9e9", "#df65b0", "#74c476", "#9e9ac8",
    "#bdbdbd", "#f768a1", "#bf812d", "#35978f", "#c994c7",
    "#80cdc1", "#dfc27d", "#bababa",
]
