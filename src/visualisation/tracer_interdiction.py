import pandas as pd


def tracer_interdiction(base, molecule, annee, indice, ax):
    """Compare l'évolution d'un indice dans les zones les plus et les moins exposées à une molécule interdite.

    base : base finale, une ligne par zone et par année.
    molecule : nom de la molécule, par exemple "isoproturon".
    annee : première année où ses achats s'effondrent.
    On garde les zones suivies avant et après l'interdiction. Leur exposition est la quantité de la
    molécule attribuée par hectare, en moyenne avant l'interdiction ; on les coupe en quatre groupes
    de même taille. On trace, chaque année, l'indice médian du quart le moins exposé (bleu)
    et du quart le plus exposé (rouge), avec une ligne pointillée à l'interdiction.
    """
    colonne = molecule.replace("-", "_") + "_kg_ha"
    avant = base[base["annee"] < annee].groupby("code_zone")
    apres = base[base["annee"] >= annee].groupby("code_zone")

    suivies = avant[indice].mean().dropna().index.intersection(apres[indice].mean().dropna().index)  # suivies avant et après
    exposition = avant[colonne].mean().loc[suivies]
    rang = exposition.rank(method="first")  # départage les nombreuses zones sans achat, pour des quarts de même taille
    quart = pd.qcut(rang, 4, labels=["moins exposées", "Q2", "Q3", "plus exposées"])

    for nom, couleur in [("moins exposées", "#2a78d6"), ("plus exposées", "#d62728")]:
        zones = quart.index[quart == nom]
        serie = base[base["code_zone"].isin(zones)].groupby("annee")[indice].median()
        ax.plot(serie.index, serie, color=couleur, marker="o", markersize=3, label=f"zones les {nom}")
    ax.axvline(annee - 0.5, color="black", linestyle="--", linewidth=1)
    ax.set_title(f"{molecule} (interdit en {annee})")
    ax.set_xlabel("année")
    ax.set_ylabel(f"{indice} médian")
    if indice == "IPR":
        ax.invert_yaxis()
