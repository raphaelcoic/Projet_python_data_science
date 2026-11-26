import matplotlib.pyplot as plt
import numpy as np

from src.visualisation.tracer_filieres_rpg import COULEURS_FILIERES, ORDRE_FILIERES


def tracer_zoom_departements(parcelles, pesticides, noms_dep, codes_dep, annee=2023):
    """Compare le profil cultural (filières) et l'intensité d'achats de pesticides sur une sélection de départements.

    parcelles : DataFrame contenant 'code_dep', 'filiere' et 'surface_ha'.
    pesticides : DataFrame contenant 'code_dep', 'annee', 'substance' et 'quantite_kg'.
    noms_dep : Series indexée par code_dep donnant le nom du département.
    codes_dep : liste ordonnée des codes départementaux à afficher.
    annee : année retenue pour les achats de pesticides (2023 par défaut).
    """
    sous_parcelles = parcelles[parcelles["code_dep"].isin(codes_dep)]
    piv = (
        sous_parcelles.pivot_table(index="code_dep", columns="filiere", values="surface_ha", aggfunc="sum", fill_value=0)
        .reindex(index=codes_dep, columns=ORDRE_FILIERES, fill_value=0)
    )
    parts = piv.div(piv.sum(axis=1), axis=0) * 100

    surface_tot = sous_parcelles.groupby("code_dep")["surface_ha"].sum().reindex(codes_dep)
    mediane_ha = sous_parcelles.groupby("code_dep")["surface_ha"].median().reindex(codes_dep)

    pest_annee = pesticides[(pesticides["annee"] == annee) & (pesticides["code_dep"].isin(codes_dep))]
    achats = pest_annee.groupby("code_dep")["quantite_kg"].sum().reindex(codes_dep, fill_value=0)
    kg_par_ha = achats / surface_tot
    mol_top = (
        pest_annee.groupby(["code_dep", "substance"])["quantite_kg"]
        .sum()
        .unstack(fill_value=0)
        .idxmax(axis=1)
        .reindex(codes_dep)
    )

    etiquettes = [f"{noms_dep[c]} ({c})" for c in codes_dep]
    y = np.arange(len(codes_dep))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.2), sharey=True, gridspec_kw={"width_ratios": [1.45, 1]})

    # Panneau gauche : profil cultural 100 % empilé
    gauche = np.zeros(len(codes_dep))
    for filiere in ORDRE_FILIERES:
        valeurs = parts[filiere].to_numpy()
        ax1.barh(
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

    ax1.set_yticks(y)
    ax1.set_yticklabels(etiquettes)
    ax1.invert_yaxis()
    ax1.set_xlim(0, 100)
    ax1.set_xlabel("part de la surface agricole déclarée (%)")
    ax1.set_title("Répartition des surfaces par filière (RPG 2023)")
    ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=4, fontsize=8.5, frameon=False)

    # Panneau droit : achats des 10 molécules par hectare agricole + molécule dominante et parcelle médiane
    barres = ax2.barh(y, kg_par_ha.to_numpy(), color="#e6550d", alpha=0.85, height=0.62)
    ax2.set_xlim(0, kg_par_ha.max() * 1.78)
    ax2.set_xlabel(f"achats des 10 molécules en {annee} (kg / ha agricole)")
    ax2.set_title(f"Intensité d'achats ({annee}) et molécule n°1")

    for barre, code in zip(barres, codes_dep):
        w = barre.get_width()
        ax2.text(
            w + 0.04,
            barre.get_y() + barre.get_height() / 2,
            f"{w:.2f} kg/ha · {mol_top[code]} (méd. {mediane_ha[code]:.1f} ha)",
            va="center",
            fontsize=8.5,
        )

    fig.tight_layout()
    return fig
