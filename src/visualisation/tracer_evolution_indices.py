import matplotlib.pyplot as plt


def tracer_evolution_indices(eau_zones_hydro):
    """Trace la médiane nationale de chaque indice par année, un panneau par indice.

    eau_zones_hydro : DataFrame renvoyé par agreger_eau_zones_hydro (une ligne par zone et par année).
    La médiane nationale d'une année est la médiane des zones suivies cette année-là.
    L'axe de l'IPR est inversé pour que, sur les trois panneaux, le haut signifie une meilleure qualité.
    """
    medianes = eau_zones_hydro.groupby("annee")[["I2M2", "IBD", "IPR"]].median()
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.2))
    for ax, indice in zip(axes, medianes.columns):
        ax.plot(medianes.index, medianes[indice], color="#2a78d6", linewidth=2)
        ax.set_title(indice)
        ax.set_xlabel("annee")
        if indice == "IPR":
            ax.invert_yaxis()
    axes[0].set_ylabel("médiane des zones")
    fig.tight_layout()
    return fig
