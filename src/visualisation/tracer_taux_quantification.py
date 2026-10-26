import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, PercentFormatter

COULEUR_MERE = "#2a78d6"  # molécule vendue
COULEUR_METABOLITE = "#eb6834"  # produit de dégradation


def tracer_taux_quantification(analyses, periode):
    """Trace le taux de quantification par période, un panneau par molécule mère.

    analyses : analyses nettoyées, avec les colonnes molecule et molecule_mere.
    periode : colonne en abscisse ("annee" ou "mois").
    """
    taux = analyses.groupby(["molecule_mere", periode, "molecule"])["quantifie"].mean().unstack()
    meres = taux.index.get_level_values("molecule_mere").unique()
    fig, axes = plt.subplots(1, len(meres), figsize=(3.2 * len(meres), 3.2), sharey=True)
    for ax, mere in zip(axes, meres):
        for molecule, serie in taux.loc[mere].dropna(axis=1, how="all").items():
            couleur = COULEUR_MERE if molecule == mere else COULEUR_METABOLITE
            ax.plot(serie.index, serie, color=couleur, linewidth=2, label=molecule)
        ax.set_title(mere)
        ax.set_xlabel(periode)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=4))
        ax.legend(frameon=False, fontsize=8)
    axes[0].set_ylim(bottom=0)
    axes[0].yaxis.set_major_formatter(PercentFormatter(1))
    axes[0].set_ylabel("taux de quantification")
    fig.tight_layout()
    return fig
