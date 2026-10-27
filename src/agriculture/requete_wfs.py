from functools import lru_cache

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.agriculture.constantes_rpg import WFS_URL


@lru_cache(maxsize=1)
def _session() -> requests.Session:
    """Session HTTP avec relance automatique (erreurs 429 / 5xx, coupures réseau)."""
    s = requests.Session()
    retry = Retry(
        total=6,
        backoff_factor=2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    s.mount("https://", HTTPAdapter(max_retries=retry, pool_maxsize=32))
    return s


def requete_wfs(params: dict, timeout: int = 180) -> requests.Response:
    """Envoie une requête WFS 2.0.0 à la Géoplateforme IGN, avec relances automatiques."""
    base = {"SERVICE": "WFS", "VERSION": "2.0.0"}
    r = _session().get(WFS_URL, params={**base, **params}, timeout=timeout)
    r.raise_for_status()
    return r
