import matplotlib.pyplot as plt


def tracer_evolution_indices(medianes):
    """Trace la médiane nationale de chaque indice par année, un panneau par indice.

    medianes : DataFrame indexé par année, avec une colonne par indice (calculer_medianes_zones_constantes).
    L'axe de l'IPR est inversé pour que, sur les trois panneaux, le haut signifie une meilleure qualité.
    """
    fig, axes = plt.subplots(1, len(medianes.columns), figsize=(12, 3.2))
    for ax, indice in zip(axes, medianes.columns):
        ax.plot(medianes.index, medianes[indice], color="#2a78d6", linewidth=2, marker="o", markersize=3)
        ax.set_title(indice)
        ax.set_xlabel("année")
        if indice == "IPR":
            ax.invert_yaxis()
    axes[0].set_ylabel("médiane des zones")
    fig.tight_layout()
    return fig
