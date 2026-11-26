import matplotlib.pyplot as plt
import numpy as np

COULEURS_FILIERES = {
    "Céréales à paille": "#2a78d6",
    "Oléagineux & indus.": "#f1a340",
    "Maïs": "#e66101",
    "Vignes & vergers": "#7b3294",
    "Légumes & fleurs": "#d01c8b",
    "Prairies perm. & estives": "#2ca25f",
    "Prairies temp. & fourrages": "#99d8c9",
    "Gel & divers": "#969696",
}

ORDRE_FILIERES = [
    "Céréales à paille",
    "Oléagineux & indus.",
    "Maïs",
    "Légumes & fleurs",
    "Vignes & vergers",
    "Prairies temp. & fourrages",
    "Prairies perm. & estives",
    "Gel & divers",
]


def tracer_filieres_rpg(parcelles, stats_filieres):
    """Compare, pour chaque grande filière du RPG, la taille des parcelles et la concentration géographique.

    parcelles : DataFrame contenant les colonnes 'filiere' et 'surface_ha'.
    stats_filieres : DataFrame indexé par filière (ordonné pour l'affichage) avec les colonnes
        'gini_dep' et 'premier_dep'.
    """
    ordre = list(stats_filieres.index)
    couleurs = [COULEURS_FILIERES.get(f, "#2a78d6") for f in ordre]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4.8), sharey=True)

    # Panneau gauche : distribution des surfaces (échelle logarithmique, boîte Q25-Q75, moustaches D1-D9)
    groupes = parcelles.groupby("filiere")["surface_ha"]
    donnees = [groupes.get_group(f).to_numpy() for f in ordre]
    bp = ax1.boxplot(
        donnees,
        positions=np.arange(len(ordre)),
        orientation="horizontal",
        patch_artist=True,
        showfliers=False,
        whis=(10, 90),
        widths=0.6,
        medianprops={"color": "#111111", "linewidth": 1.8},
    )
    for patch, couleur in zip(bp["boxes"], couleurs):
        patch.set_facecolor(couleur)
        patch.set_alpha(0.75)

    ax1.set_yticks(np.arange(len(ordre)))
    ax1.set_yticklabels(ordre)
    ax1.invert_yaxis()
    ax1.set_xscale("log")
    ax1.set_xlabel("surface d'une parcelle en ha (échelle log ; boîte Q25–Q75, moustaches D1–D9)")
    ax1.set_title("Taille des parcelles par filière")

    # Panneau droit : concentration géographique entre départements (indice de Gini)
    y = np.arange(len(ordre))
    barres = ax2.barh(y, stats_filieres["gini_dep"], color=couleurs, alpha=0.85, height=0.62)
    ax2.set_xlim(0, 1.12)
    ax2.set_xlabel("indice de Gini entre départements (0 = uniforme, 1 = concentré)")
    ax2.set_title("Concentration départementale des surfaces")

    for barre, (_, ligne) in zip(barres, stats_filieres.iterrows()):
        w = barre.get_width()
        ax2.text(
            w + 0.015,
            barre.get_y() + barre.get_height() / 2,
            f"{w:.2f}  ({ligne['premier_dep']})",
            va="center",
            fontsize=8.5,
        )

    fig.tight_layout()
    return fig
