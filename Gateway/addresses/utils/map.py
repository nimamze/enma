import requests
from django.conf import settings

MAPIR_API_KEY = settings.MAPIR_API_KEY


class MapIrError(Exception):
    pass


def reverse_geocode(latitude: float, longitude: float) -> dict:
    try:
        resp = requests.get(
            "https://map.ir/reverse",
            params={"lat": latitude, "lon": longitude},
            headers={"x-api-key": MAPIR_API_KEY},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise MapIrError("reverse geocoding failed") from exc

    return {
        "country": data.get("country"),
        "province": data.get("province"),
        "city": data.get("city"),
        "street": data.get("last") or data.get("primary") or "",
        "alley": data.get("neighbourhood") or "",
    }
