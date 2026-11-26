def tracer_indice_et_achats(medianes, achats, indice, molecule, ax):
    """Trace l'indice médian de chaque année (en noir) et les achats d'une molécule (en orange, axe de droite).

    medianes : DataFrame indexé par année, avec une colonne par indice.
    achats : DataFrame indexé par année, avec une colonne par molécule, en tonnes.
    L'axe de l'IPR est inversé pour que le haut signifie toujours une meilleure qualité.
    """
    ax.plot(medianes.index, medianes[indice], color="black", linewidth=2, marker="o", markersize=4)
    ax.set_ylabel(f"{indice} médian")
    if indice == "IPR":
        ax.invert_yaxis()
    droite = ax.twinx()
    droite.plot(achats.index, achats[molecule], color="#e6550d", linewidth=2)
    droite.set_ylabel(f"achats de {molecule} (t)", color="#e6550d")
    droite.set_ylim(bottom=0)
    droite.grid(False)
    ax.set_xlabel("année")
