from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
from difflib import get_close_matches
from pathlib import Path

geolocator = Nominatim(user_agent="noalerts_bot")

CITY_FILE = Path(__file__).with_name("ua_cities.txt")
with open(CITY_FILE, encoding="utf-8") as f:
    CITY_LIST = [c.strip() for c in f if c.strip()]

def suggest_cities(name: str) -> list[str]:
    return get_close_matches(name, CITY_LIST, n=3, cutoff=0.6)

async def resolve_city(name: str) -> str | None:
    """Fuzzy match a Ukrainian city and return canonical name if found."""
    candidate = get_close_matches(name, CITY_LIST, n=1, cutoff=0.6)
    query = candidate[0] if candidate else name
    try:
        location = geolocator.geocode(f"{query}, Ukraine", language="en")
    except GeocoderUnavailable:
        return None
    if location and location.raw.get("address", {}).get("country_code") == "ua":
        address = location.raw.get("address", {})
        return (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or location.address.split(",")[0].strip()
        )
    return None

async def reverse_geocode(lat: float, lon: float) -> str | None:
    try:
        location = geolocator.reverse((lat, lon), language="en")
    except GeocoderUnavailable:
        return None
    if location and location.raw.get("address", {}).get("country_code") == "ua":
        address = location.raw.get("address", {})
        return (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or location.address.split(",")[0].strip()
        )
    return None
