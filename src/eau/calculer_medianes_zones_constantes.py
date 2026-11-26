import pandas as pd


def calculer_medianes_zones_constantes(eau_zones_hydro, indices):
    """Médiane nationale de chaque indice, année par année, sur les zones suivies toutes les années.

    eau_zones_hydro : DataFrame avec code_zone, annee et une colonne par indice (une ligne par zone et par année).
    indices : liste des indices, par exemple ["I2M2", "IBD", "IPR"].
    On garde, pour chaque indice, les seules zones qui ont une valeur chaque année : la liste des zones
    ne change pas d'une année à l'autre, et l'extension du réseau de suivi ne crée pas de faux sauts.
    Renvoie un DataFrame indexé par année, avec une colonne par indice.
    """
    nb_annees = eau_zones_hydro["annee"].nunique()
    medianes = {}
    for indice in indices:
        annees_suivies = eau_zones_hydro.groupby("code_zone")[indice].count()
        zones_constantes = annees_suivies.index[annees_suivies == nb_annees]
        eau_constante = eau_zones_hydro[eau_zones_hydro["code_zone"].isin(zones_constantes)]
        medianes[indice] = eau_constante.groupby("annee")[indice].median()
    return pd.DataFrame(medianes)
