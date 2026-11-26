def agreger_pesticides(pesticides_nettoyes, molecules):
    """Garde les molécules suivies et additionne leurs achats : une ligne par département, année et molécule.

    pesticides_nettoyes : DataFrame renvoyé par nettoyer_pesticides.
    molecules : liste des molécules à garder (MOLECULES dans constantes_pesticides.py).
    Une molécule peut avoir plusieurs lignes la même année dans un département (statut biocontrôle,
    classe de danger, sels regroupés). Parmi les 10 molécules suivies, seul le cuivre est concerné :
    ses 8 sels, regroupés par nettoyer_pesticides, sont additionnés ici.
    Renvoie un DataFrame : code_dep, nom_dep, annee, substance, quantite_kg (en kg de substance active).
    """
    suivies = pesticides_nettoyes[pesticides_nettoyes["substance"].isin(molecules)]
    return suivies.groupby(["code_dep", "nom_dep", "annee", "substance"], as_index=False)["quantite_kg"].sum()
