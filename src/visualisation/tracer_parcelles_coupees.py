def tracer_parcelles_coupees(contours, parcelles_zones_hydro, zones_hydro, titre, ax, cadre=None):
    """Carte des parcelles coupées par une limite de zone hydrographique.

    contours : GeoDataFrame des parcelles (ID_PARCEL, geometry), par exemple extraire_contours_departement.
    parcelles_zones_hydro : DataFrame renvoyé par associer_parcelles_zones_hydro pour ces parcelles.
    zones_hydro : GeoDataFrame renvoyé par recuperer_zones_hydro.
    cadre : (xmin, ymin, xmax, ymax) en Lambert 93 pour zoomer ; par défaut, toutes les parcelles.
    Parcelles entières dans une zone en gris, parcelles coupées en rouge, limites des zones en bleu.
    """
    xmin, ymin, xmax, ymax = contours.total_bounds if cadre is None else cadre
    coupees = contours["ID_PARCEL"].isin(parcelles_zones_hydro.loc[parcelles_zones_hydro["part"] < 1, "id_parcelle"])
    contours[~coupees].plot(ax=ax, color="#cccccc", linewidth=0)
    contours[coupees].plot(ax=ax, color="#d62728", linewidth=0)
    zones_hydro.cx[xmin:xmax, ymin:ymax].boundary.plot(ax=ax, color="#2a78d6", linewidth=0.8)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_title(titre)
    ax.set_axis_off()
