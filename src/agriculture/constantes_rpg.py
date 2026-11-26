"""
Référentiels du RPG : groupes de cultures, catégories et nomenclature des cultures.

Source : https://www.data.gouv.fr/datasets/rpg (IGN / ASP).
"""

# Nomenclature officielle des cultures 2023 (code culture -> libellé), publiée par l'IGN
URL_NOMENCLATURE_CULTURES_2023 = "https://data.geopf.fr/annexes/ressources/documentation/REF_CULTURES_GROUPES_CULTURES_2023.csv"

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

# Libellés des grandes catégories de culture
CATEGORIES_CULTURE: dict[str, str] = {
    "TA": "Terres arables",
    "PP": "Prairies permanentes",
    "CP": "Cultures permanentes",
    "SB": "Surfaces boisées",
}

# Regroupement des groupes de cultures du RPG en 8 grandes filières agronomiques
FILIERES_RPG: dict[str, str] = {
    "Blé tendre": "Céréales à paille",
    "Orge": "Céréales à paille",
    "Autres céréales": "Céréales à paille",
    "Riz": "Céréales à paille",
    "Maïs grain et ensilage": "Maïs",
    "Colza": "Oléagineux & indus.",
    "Tournesol": "Oléagineux & indus.",
    "Autres oléagineux": "Oléagineux & indus.",
    "Protéagineux": "Oléagineux & indus.",
    "Légumineuses à grains": "Oléagineux & indus.",
    "Plantes à fibres": "Oléagineux & indus.",
    "Autres cultures industrielles": "Oléagineux & indus.",
    "Canne à sucre": "Oléagineux & indus.",
    "Vignes": "Vignes & vergers",
    "Vergers": "Vignes & vergers",
    "Fruits à coque": "Vignes & vergers",
    "Oliviers": "Vignes & vergers",
    "Légumes ou fleurs": "Légumes & fleurs",
    "Prairies permanentes": "Prairies perm. & estives",
    "Estives et landes": "Prairies perm. & estives",
    "Prairies temporaires": "Prairies temp. & fourrages",
    "Fourrage": "Prairies temp. & fourrages",
    "Gel (surfaces gelées sans production)": "Gel & divers",
    "Divers": "Gel & divers",
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
