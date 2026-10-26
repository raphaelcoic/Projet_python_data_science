def tracer_carte(departements, valeurs, colonne, titre, ax):
    """Carte des départements colorés selon une colonne (bleu clair = faible, foncé = élevé).

    departements : GeoDataFrame avec code_dep et geometry.
    valeurs : DataFrame avec code_dep et la colonne à représenter.
    Les départements sans valeur sont en gris.
    """
    carte = departements.merge(valeurs, on="code_dep", how="left")
    carte.plot(
        column=colonne, cmap="Blues", legend=True, ax=ax,
        edgecolor="#999999", linewidth=0.2,
        missing_kwds={"color": "#e5e5e5"},
        legend_kwds={"shrink": 0.6},
    )
    ax.set_title(titre)
    ax.set_axis_off()
