from src.agriculture.constantes_rpg import CATEGORIES_CULTURE, CULTURE_VERS_CATEGORIE, LIBELLES_GROUPES_RPG


def ajouter_libelles_rpg(parcelles):
    """Ajoute le libellé du groupe de cultures et la catégorie de culture de chaque parcelle.

    parcelles : DataFrame avec les colonnes code_groupe et code_culture.
    L'archive de l'IGN ne contient que les codes : les libellés viennent de constantes_rpg.
    categorie_culture vaut TA, PP, CP ou SB d'après le code culture, et reste vide pour les
    surfaces non agricoles ou non classées.
    Renvoie le DataFrame avec en plus libelle_groupe et categorie_culture.
    """
    categorie = parcelles["code_culture"].map(CULTURE_VERS_CATEGORIE)
    return parcelles.assign(
        libelle_groupe=parcelles["code_groupe"].map(LIBELLES_GROUPES_RPG),
        categorie_culture=categorie.where(categorie.isin(list(CATEGORIES_CULTURE))),
    )
