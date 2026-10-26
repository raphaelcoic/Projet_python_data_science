import matplotlib.pyplot as plt


def tracer_evolution_indices(indices):
    """Trace la valeur médiane de chaque indice par année, un panneau par indice.

    indices : indices nettoyés (colonnes indice, annee, valeur).
    L'axe de l'IPR est inversé pour que, sur les trois panneaux, le haut signifie une meilleure qualité.
    """
    medianes = indices.groupby(["indice", "annee"])["valeur"].median()
    noms = medianes.index.get_level_values("indice").unique()
    fig, axes = plt.subplots(1, len(noms), figsize=(4 * len(noms), 3.2))
    for ax, indice in zip(axes, noms):
        ax.plot(medianes[indice].index, medianes[indice], color="#2a78d6", linewidth=2)
        ax.set_title(indice)
        ax.set_xlabel("annee")
        if indice == "IPR":
            ax.invert_yaxis()
    axes[0].set_ylabel("valeur médiane")
    fig.tight_layout()
    return fig
