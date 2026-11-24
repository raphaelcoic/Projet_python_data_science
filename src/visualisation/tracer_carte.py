def tracer_carte(zones, valeurs, colonne, titre, ax, cmap="Blues", centrer=False):
    """Carte des zones hydrographiques colorées selon une colonne (par défaut bleu clair = faible, foncé = élevé).

    zones : GeoDataFrame avec code_zone et geometry.
    valeurs : DataFrame avec code_zone et la colonne à représenter.
    cmap : palette ("Blues_r" pour inverser : foncé = faible ; "RdBu" pour un taux d'évolution).
    centrer : True pour une échelle symétrique autour de 0 (taux d'évolution).
    L'échelle va du 2e au 98e centile, pour que quelques valeurs extrêmes ne l'écrasent pas.
    Les zones sans valeur sont en gris.
    """
    carte = zones.merge(valeurs, on="code_zone", how="left")
    vmin, vmax = carte[colonne].quantile(0.02), carte[colonne].quantile(0.98)
    if centrer:
        vmax = max(-vmin, vmax)
        vmin = -vmax
    carte.plot(
        column=colonne, cmap=cmap, legend=True, ax=ax, vmin=vmin, vmax=vmax,
        edgecolor="#999999", linewidth=0.1,
        missing_kwds={"color": "#e5e5e5"},
        legend_kwds={"shrink": 0.6, "extend": "both"},
    )
    ax.set_title(titre)
    ax.set_axis_off()
