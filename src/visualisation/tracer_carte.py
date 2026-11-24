def tracer_carte(contours, valeurs, colonne, titre, ax, cmap="Blues", centrer=False, cle="code_zone"):
    """Carte colorée selon une colonne (par défaut bleu clair = faible, foncé = élevé).

    contours : GeoDataFrame avec la clé et geometry (zones hydrographiques ou départements).
    valeurs : DataFrame avec la clé et la colonne à représenter.
    cmap : palette ("Blues_r" pour inverser : foncé = faible ; "RdBu" pour un taux d'évolution).
    centrer : True pour une échelle symétrique autour de 0 (taux d'évolution).
    cle : colonne de jointure, "code_zone" ou "code_dep".
    L'échelle va du 2e au 98e centile, pour que quelques valeurs extrêmes ne l'écrasent pas.
    Les contours sans valeur sont en gris.
    """
    carte = contours.merge(valeurs, on=cle, how="left")
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
