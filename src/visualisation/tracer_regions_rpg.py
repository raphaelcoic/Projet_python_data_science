import matplotlib.pyplot as plt
import numpy as np

from src.visualisation.tracer_filieres_rpg import COULEURS_FILIERES, ORDRE_FILIERES


def tracer_regions_rpg(stats_regions, parts_reg_filieres):
    """Compare la surface agricole (SAU), la taille des parcelles et la spécialisation culturale des 12 régions.

    stats_regions : DataFrame indexé par région (ordonné pour l'affichage) avec les colonnes
        'surface_Mha', 'mediane_ha' et 'moyenne_ha'.
    parts_reg_filieres : DataFrame indexé par région avec une colonne par filière (% de la SAU régionale).
    """
    ordre = list(stats_regions.index)
    parts = parts_reg_filieres.reindex(index=ordre, columns=ORDRE_FILIERES, fill_value=0)
    y = np.arange(len(ordre))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.5, 6.2), sharey=True, gridspec_kw={"width_ratios": [1, 1.35]})

    # Panneau gauche : surface agricole déclarée par région + taille médiane et moyenne des parcelles
    barres = ax1.barh(y, stats_regions["surface_Mha"].to_numpy(), color="#2a78d6", alpha=0.85, height=0.65)
    ax1.set_yticks(y)
    ax1.set_yticklabels(ordre)
    ax1.invert_yaxis()
    ax1.set_xlim(0, stats_regions["surface_Mha"].max() * 1.78)
    ax1.set_xlabel("surface agricole déclarée (millions d'ha)")
    ax1.set_title("SAU déclarée et taille des parcelles par région")

    for barre, (_, ligne) in zip(barres, stats_regions.iterrows()):
        w = barre.get_width()
        ax1.text(
            w + 0.06,
            barre.get_y() + barre.get_height() / 2,
            f"{w:.2f} M ha (méd. {ligne['mediane_ha']:.1f} / moy. {ligne['moyenne_ha']:.1f} ha)",
            va="center",
            fontsize=8.2,
        )

    # Panneau droit : profil cultural 100 % empilé par région
    gauche = np.zeros(len(ordre))
    for filiere in ORDRE_FILIERES:
        valeurs = parts[filiere].to_numpy()
        ax2.barh(
            y,
            valeurs,
            left=gauche,
            color=COULEURS_FILIERES[filiere],
            edgecolor="white",
            linewidth=0.5,
            height=0.65,
            label=filiere,
        )
        gauche += valeurs

    ax2.set_xlim(0, 100)
    ax2.set_xlabel("part de la SAU régionale (%)")
    ax2.set_title("Spécialisation culturale des 12 régions (RPG 2023)")
    ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=4, fontsize=8.5, frameon=False)

    fig.tight_layout()
    return fig
