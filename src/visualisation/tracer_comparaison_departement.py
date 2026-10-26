import matplotlib.pyplot as plt


def tracer_comparaison_departement(indices, code_dep):
    """Boîtes à moustaches de chaque indice : toutes les stations de France contre celles du département.

    indices : indices nettoyés (colonnes code_dep, indice, valeur).
    L'axe de l'IPR est inversé pour que, sur les trois panneaux, le haut signifie une meilleure qualité.
    """
    noms = sorted(indices["indice"].unique())
    fig, axes = plt.subplots(1, len(noms), figsize=(3.5 * len(noms), 3.2))
    for ax, indice in zip(axes, noms):
        valeurs = indices[indices["indice"] == indice]
        ax.boxplot(
            [valeurs["valeur"], valeurs.loc[valeurs["code_dep"] == code_dep, "valeur"]],
            tick_labels=["France", code_dep], showfliers=False,
        )
        ax.set_title(indice)
        if indice == "IPR":
            ax.invert_yaxis()
    fig.tight_layout()
    return fig
