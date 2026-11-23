def tracer_carte(departements, valeurs, colonne, titre, ax, cmap="Blues"):
    """Carte des départements colorés selon une colonne (par défaut bleu clair = faible, foncé = élevé).

    departements : GeoDataFrame avec code_dep et geometry.
    valeurs : DataFrame avec code_dep et la colonne à représenter.
    cmap : palette ("Blues_r" pour inverser : foncé = faible).
    Les départements sans valeur sont en gris.
    """
    carte = departements.merge(valeurs, on="code_dep", how="left")
    carte.plot(
        column=colonne, cmap=cmap, legend=True, ax=ax,
        edgecolor="#999999", linewidth=0.2,
        missing_kwds={"color": "#e5e5e5"},
        legend_kwds={"shrink": 0.6},
    )
    ax.set_title(titre)
    ax.set_axis_off()
