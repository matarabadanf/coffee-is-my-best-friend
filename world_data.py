import json
import os
import urllib.parse
import urllib.request
from typing import TypedDict
import pandas as pd

# Local persistent geocode cache for custom cities
_GEOCODE_CACHE_FILE = os.path.join(os.path.dirname(__file__), ".city_geocache.json")
_GEOCODE_CACHE: dict[str, list[float]] = {}

def _load_geocode_cache():
    global _GEOCODE_CACHE
    if os.path.exists(_GEOCODE_CACHE_FILE):
        try:
            with open(_GEOCODE_CACHE_FILE, "r", encoding="utf-8") as f:
                _GEOCODE_CACHE = json.load(f)
        except Exception:
            _GEOCODE_CACHE = {}

def _save_geocode_cache():
    try:
        with open(_GEOCODE_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_GEOCODE_CACHE, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

_load_geocode_cache()

# User brand colors for map pins and UI elements (Fer is rebeccapurple)
USER_MAP_COLORS = {
    "Fer": "#663399",   # rebeccapurple
    "Bea": "#F43F5E",   # Rose / Coral
    "Cris": "#0284C7",  # Sky Blue
    "All": "#D97706"    # Amber
}

class CountryInfo(TypedDict):
    name: str
    flag: str
    continent: str
    lat: float
    lon: float

# Default home base countries & cities per user
USER_DEFAULT_COUNTRIES: dict[str, str] = {
    "Bea": "NL",   # Netherlands 🇳🇱
    "Fer": "FR",   # France 🇫🇷
    "Cris": "CZ",  # Czech Republic 🇨🇿
}

USER_DEFAULT_CITIES: dict[str, str] = {
    "Bea": "Amsterdam",
    "Fer": "Paris",
    "Cris": "Prague",
}

DEFAULT_COUNTRY = "ES"  # System fallback
DEFAULT_CITY = "Madrid"

def get_user_default_country(user: str) -> str:
    """Returns the default home base country code for a given user."""
    return USER_DEFAULT_COUNTRIES.get(user, DEFAULT_COUNTRY)

def get_user_default_city(user: str) -> str:
    """Returns the default home base city for a given user."""
    return USER_DEFAULT_CITIES.get(user, DEFAULT_CITY)

# Comprehensive ISO 3166-1 alpha-2 country and territory registry with coordinates & flag emojis
TRAVEL_COUNTRIES: dict[str, CountryInfo] = {
    # ── Europe ──
    "AD": {"name": "Andorra", "flag": "🇦🇩", "continent": "Europe", "lat": 42.5063, "lon": 1.5218},
    "AL": {"name": "Albania", "flag": "🇦🇱", "continent": "Europe", "lat": 41.3275, "lon": 19.8187},
    "AT": {"name": "Austria", "flag": "🇦🇹", "continent": "Europe", "lat": 48.2082, "lon": 16.3738},
    "BA": {"name": "Bosnia and Herzegovina", "flag": "🇧🇦", "continent": "Europe", "lat": 43.8563, "lon": 18.4131},
    "BE": {"name": "Belgium", "flag": "🇧🇪", "continent": "Europe", "lat": 50.8503, "lon": 4.3517},
    "BG": {"name": "Bulgaria", "flag": "🇧🇬", "continent": "Europe", "lat": 42.6977, "lon": 23.3219},
    "CH": {"name": "Switzerland", "flag": "🇨🇭", "continent": "Europe", "lat": 46.9480, "lon": 7.4474},
    "CY": {"name": "Cyprus", "flag": "🇨🇾", "continent": "Europe", "lat": 35.1856, "lon": 33.3823},
    "CZ": {"name": "Czech Republic", "flag": "🇨🇿", "continent": "Europe", "lat": 50.0755, "lon": 14.4378},
    "DE": {"name": "Germany", "flag": "🇩🇪", "continent": "Europe", "lat": 52.5200, "lon": 13.4050},
    "DK": {"name": "Denmark", "flag": "🇩🇰", "continent": "Europe", "lat": 55.6761, "lon": 12.5683},
    "EE": {"name": "Estonia", "flag": "🇪🇪", "continent": "Europe", "lat": 59.4370, "lon": 24.7536},
    "ES": {"name": "Spain", "flag": "🇪🇸", "continent": "Europe", "lat": 40.4168, "lon": -3.7038},
    "FI": {"name": "Finland", "flag": "🇫🇮", "continent": "Europe", "lat": 60.1699, "lon": 24.9384},
    "FO": {"name": "Faroe Islands", "flag": "🇫🇴", "continent": "Europe", "lat": 62.0079, "lon": -6.7900},
    "FR": {"name": "France", "flag": "🇫🇷", "continent": "Europe", "lat": 48.8566, "lon": 2.3522},
    "GB": {"name": "United Kingdom", "flag": "🇬🇧", "continent": "Europe", "lat": 51.5074, "lon": -0.1278},
    "GI": {"name": "Gibraltar", "flag": "🇬🇮", "continent": "Europe", "lat": 36.1408, "lon": -5.3536},
    "GR": {"name": "Greece", "flag": "🇬🇷", "continent": "Europe", "lat": 37.9838, "lon": 23.7275},
    "HR": {"name": "Croatia", "flag": "🇭🇷", "continent": "Europe", "lat": 45.8150, "lon": 15.9819},
    "HU": {"name": "Hungary", "flag": "🇭🇺", "continent": "Europe", "lat": 47.4979, "lon": 19.0402},
    "IE": {"name": "Ireland", "flag": "🇮🇪", "continent": "Europe", "lat": 53.3498, "lon": -6.2603},
    "IS": {"name": "Iceland", "flag": "🇮🇸", "continent": "Europe", "lat": 64.1466, "lon": -21.9426},
    "IT": {"name": "Italy", "flag": "🇮🇹", "continent": "Europe", "lat": 41.9028, "lon": 12.4964},
    "LI": {"name": "Liechtenstein", "flag": "🇱🇮", "continent": "Europe", "lat": 47.1410, "lon": 9.5209},
    "LT": {"name": "Lithuania", "flag": "🇱🇹", "continent": "Europe", "lat": 54.6872, "lon": 25.2797},
    "LU": {"name": "Luxembourg", "flag": "🇱🇺", "continent": "Europe", "lat": 49.6116, "lon": 6.1319},
    "LV": {"name": "Latvia", "flag": "🇱🇻", "continent": "Europe", "lat": 56.9496, "lon": 24.1052},
    "MC": {"name": "Monaco", "flag": "🇲🇨", "continent": "Europe", "lat": 43.7384, "lon": 7.4246},
    "MD": {"name": "Moldova", "flag": "🇲🇩", "continent": "Europe", "lat": 47.0105, "lon": 28.8638},
    "ME": {"name": "Montenegro", "flag": "🇲🇪", "continent": "Europe", "lat": 42.4304, "lon": 19.2594},
    "MK": {"name": "North Macedonia", "flag": "🇲🇰", "continent": "Europe", "lat": 41.9973, "lon": 21.4280},
    "MT": {"name": "Malta", "flag": "🇲🇹", "continent": "Europe", "lat": 35.8989, "lon": 14.5146},
    "NL": {"name": "Netherlands", "flag": "🇳🇱", "continent": "Europe", "lat": 52.3676, "lon": 4.9041},
    "NO": {"name": "Norway", "flag": "🇳🇴", "continent": "Europe", "lat": 59.9139, "lon": 10.7522},
    "PL": {"name": "Poland", "flag": "🇵🇱", "continent": "Europe", "lat": 52.2297, "lon": 21.0122},
    "PT": {"name": "Portugal", "flag": "🇵🇹", "continent": "Europe", "lat": 38.7223, "lon": -9.1393},
    "RO": {"name": "Romania", "flag": "🇷🇴", "continent": "Europe", "lat": 44.4268, "lon": 26.1025},
    "RS": {"name": "Serbia", "flag": "🇷🇸", "continent": "Europe", "lat": 44.7866, "lon": 20.4489},
    "SE": {"name": "Sweden", "flag": "🇸🇪", "continent": "Europe", "lat": 59.3293, "lon": 18.0686},
    "SI": {"name": "Slovenia", "flag": "🇸🇮", "continent": "Europe", "lat": 46.0569, "lon": 14.5058},
    "SK": {"name": "Slovakia", "flag": "🇸🇰", "continent": "Europe", "lat": 48.1486, "lon": 17.1077},
    "SM": {"name": "San Marino", "flag": "🇸🇲", "continent": "Europe", "lat": 43.9424, "lon": 12.4578},
    "UA": {"name": "Ukraine", "flag": "🇺🇦", "continent": "Europe", "lat": 50.4501, "lon": 30.5234},
    "VA": {"name": "Vatican City", "flag": "🇻🇦", "continent": "Europe", "lat": 41.9029, "lon": 12.4534},

    # ── North & Central America ──
    "AG": {"name": "Antigua and Barbuda", "flag": "🇦🇬", "continent": "North America", "lat": 17.1274, "lon": -61.8468},
    "BS": {"name": "Bahamas", "flag": "🇧🇸", "continent": "North America", "lat": 25.0343, "lon": -77.3963},
    "BB": {"name": "Barbados", "flag": "🇧🇧", "continent": "North America", "lat": 13.1939, "lon": -59.5432},
    "BZ": {"name": "Belize", "flag": "🇧🇿", "continent": "North America", "lat": 17.2510, "lon": -88.7590},
    "CA": {"name": "Canada", "flag": "🇨🇦", "continent": "North America", "lat": 45.4215, "lon": -75.6972},
    "CR": {"name": "Costa Rica", "flag": "🇨🇷", "continent": "North America", "lat": 9.9281, "lon": -84.0907},
    "CU": {"name": "Cuba", "flag": "🇨🇺", "continent": "North America", "lat": 23.1136, "lon": -82.3666},
    "DM": {"name": "Dominica", "flag": "🇩🇲", "continent": "North America", "lat": 15.3092, "lon": -61.3794},
    "DO": {"name": "Dominican Republic", "flag": "🇩🇴", "continent": "North America", "lat": 18.4861, "lon": -69.9312},
    "GD": {"name": "Grenada", "flag": "🇬🇩", "continent": "North America", "lat": 12.0561, "lon": -61.7488},
    "GT": {"name": "Guatemala", "flag": "🇬🇹", "continent": "North America", "lat": 14.6349, "lon": -90.5069},
    "HN": {"name": "Honduras", "flag": "🇭🇳", "continent": "North America", "lat": 14.0723, "lon": -87.1921},
    "HT": {"name": "Haiti", "flag": "🇭🇹", "continent": "North America", "lat": 18.5944, "lon": -72.3074},
    "JM": {"name": "Jamaica", "flag": "🇯🇲", "continent": "North America", "lat": 17.9712, "lon": -76.7928},
    "KN": {"name": "Saint Kitts and Nevis", "flag": "🇰🇳", "continent": "North America", "lat": 17.3578, "lon": -62.7830},
    "LC": {"name": "Saint Lucia", "flag": "🇱🇨", "continent": "North America", "lat": 14.0101, "lon": -60.9875},
    "MX": {"name": "Mexico", "flag": "🇲🇽", "continent": "North America", "lat": 19.4326, "lon": -99.1332},
    "NI": {"name": "Nicaragua", "flag": "🇳🇮", "continent": "North America", "lat": 12.1150, "lon": -86.2362},
    "PA": {"name": "Panama", "flag": "🇵🇦", "continent": "North America", "lat": 8.9824, "lon": -79.5199},
    "PR": {"name": "Puerto Rico", "flag": "🇵🇷", "continent": "North America", "lat": 18.4655, "lon": -66.1057},
    "SV": {"name": "El Salvador", "flag": "🇸🇻", "continent": "North America", "lat": 13.6929, "lon": -89.2182},
    "TT": {"name": "Trinidad and Tobago", "flag": "🇹🇹", "continent": "North America", "lat": 10.6549, "lon": -61.5019},
    "US": {"name": "United States", "flag": "🇺🇸", "continent": "North America", "lat": 38.9072, "lon": -77.0369},
    "VC": {"name": "Saint Vincent and the Grenadines", "flag": "🇻🇨", "continent": "North America", "lat": 13.1600, "lon": -61.2248},

    # ── South America ──
    "AR": {"name": "Argentina", "flag": "🇦🇷", "continent": "South America", "lat": -34.6037, "lon": -58.3816},
    "BO": {"name": "Bolivia", "flag": "🇧🇴", "continent": "South America", "lat": -16.4897, "lon": -68.1193},
    "BR": {"name": "Brazil", "flag": "🇧🇷", "continent": "South America", "lat": -15.7975, "lon": -47.8919},
    "CL": {"name": "Chile", "flag": "🇨🇱", "continent": "South America", "lat": -33.4489, "lon": -70.6693},
    "CO": {"name": "Colombia", "flag": "🇨🇴", "continent": "South America", "lat": 4.7110, "lon": -74.0721},
    "EC": {"name": "Ecuador", "flag": "🇪🇨", "continent": "South America", "lat": -0.1807, "lon": -78.4678},
    "GY": {"name": "Guyana", "flag": "🇬🇾", "continent": "South America", "lat": 6.8013, "lon": -58.1551},
    "PE": {"name": "Peru", "flag": "🇵🇪", "continent": "South America", "lat": -12.0464, "lon": -77.0428},
    "PY": {"name": "Paraguay", "flag": "🇵🇾", "continent": "South America", "lat": -25.2637, "lon": -57.5759},
    "SR": {"name": "Suriname", "flag": "🇸🇷", "continent": "South America", "lat": 5.8520, "lon": -55.2038},
    "UY": {"name": "Uruguay", "flag": "🇺🇾", "continent": "South America", "lat": -34.9011, "lon": -56.1645},
    "VE": {"name": "Venezuela", "flag": "🇻🇪", "continent": "South America", "lat": 10.4806, "lon": -66.9036},

    # ── Asia ──
    "AE": {"name": "United Arab Emirates", "flag": "🇦🇪", "continent": "Asia", "lat": 24.4539, "lon": 54.3773},
    "AF": {"name": "Afghanistan", "flag": "🇦🇫", "continent": "Asia", "lat": 34.5553, "lon": 69.2075},
    "AM": {"name": "Armenia", "flag": "🇦🇲", "continent": "Asia", "lat": 40.1792, "lon": 44.4991},
    "AZ": {"name": "Azerbaijan", "flag": "🇦🇿", "continent": "Asia", "lat": 40.4093, "lon": 49.8671},
    "BD": {"name": "Bangladesh", "flag": "🇧🇩", "continent": "Asia", "lat": 23.8103, "lon": 90.4125},
    "BH": {"name": "Bahrain", "flag": "🇧🇭", "continent": "Asia", "lat": 26.2285, "lon": 50.5860},
    "BN": {"name": "Brunei", "flag": "🇧🇳", "continent": "Asia", "lat": 4.9031, "lon": 114.9398},
    "BT": {"name": "Bhutan", "flag": "🇧🇹", "continent": "Asia", "lat": 27.4728, "lon": 89.6393},
    "CN": {"name": "China", "flag": "🇨🇳", "continent": "Asia", "lat": 39.9042, "lon": 116.4074},
    "GE": {"name": "Georgia", "flag": "🇬🇪", "continent": "Asia", "lat": 41.7151, "lon": 44.8271},
    "HK": {"name": "Hong Kong", "flag": "🇭🇰", "continent": "Asia", "lat": 22.3193, "lon": 114.1694},
    "ID": {"name": "Indonesia", "flag": "🇮🇩", "continent": "Asia", "lat": -6.2088, "lon": 106.8456},
    "IL": {"name": "Israel", "flag": "🇮🇱", "continent": "Asia", "lat": 31.7683, "lon": 35.2137},
    "IN": {"name": "India", "flag": "🇮🇳", "continent": "Asia", "lat": 28.6139, "lon": 77.2090},
    "IQ": {"name": "Iraq", "flag": "🇮🇶", "continent": "Asia", "lat": 33.3152, "lon": 44.3661},
    "IR": {"name": "Iran", "flag": "🇮🇷", "continent": "Asia", "lat": 35.6892, "lon": 51.3890},
    "JO": {"name": "Jordan", "flag": "🇯🇴", "continent": "Asia", "lat": 31.9454, "lon": 35.9284},
    "JP": {"name": "Japan", "flag": "🇯🇵", "continent": "Asia", "lat": 35.6762, "lon": 139.6503},
    "KG": {"name": "Kyrgyzstan", "flag": "🇰🇬", "continent": "Asia", "lat": 42.8746, "lon": 74.5698},
    "KH": {"name": "Cambodia", "flag": "🇰🇭", "continent": "Asia", "lat": 11.5564, "lon": 104.9282},
    "KR": {"name": "South Korea", "flag": "🇰🇷", "continent": "Asia", "lat": 37.5665, "lon": 126.9780},
    "KW": {"name": "Kuwait", "flag": "🇰🇼", "continent": "Asia", "lat": 29.3759, "lon": 47.9774},
    "KZ": {"name": "Kazakhstan", "flag": "🇰🇿", "continent": "Asia", "lat": 51.1694, "lon": 71.4491},
    "LA": {"name": "Laos", "flag": "🇱🇦", "continent": "Asia", "lat": 17.9757, "lon": 102.6331},
    "LB": {"name": "Lebanon", "flag": "🇱🇧", "continent": "Asia", "lat": 33.8938, "lon": 35.5018},
    "LK": {"name": "Sri Lanka", "flag": "🇱🇰", "continent": "Asia", "lat": 6.9271, "lon": 79.8612},
    "MM": {"name": "Myanmar", "flag": "🇲🇲", "continent": "Asia", "lat": 19.7633, "lon": 96.0785},
    "MN": {"name": "Mongolia", "flag": "🇲🇳", "continent": "Asia", "lat": 47.8864, "lon": 106.9057},
    "MO": {"name": "Macau", "flag": "🇲🇴", "continent": "Asia", "lat": 22.1987, "lon": 113.5439},
    "MV": {"name": "Maldives", "flag": "🇲🇻", "continent": "Asia", "lat": 4.1755, "lon": 73.5093},
    "MY": {"name": "Malaysia", "flag": "🇲🇾", "continent": "Asia", "lat": 3.1390, "lon": 101.6869},
    "NP": {"name": "Nepal", "flag": "🇳🇵", "continent": "Asia", "lat": 27.7172, "lon": 85.3240},
    "OM": {"name": "Oman", "flag": "🇴🇲", "continent": "Asia", "lat": 23.5880, "lon": 58.3829},
    "PH": {"name": "Philippines", "flag": "🇵🇭", "continent": "Asia", "lat": 14.5995, "lon": 120.9842},
    "PK": {"name": "Pakistan", "flag": "🇵🇰", "continent": "Asia", "lat": 33.6844, "lon": 73.0479},
    "QA": {"name": "Qatar", "flag": "🇶🇦", "continent": "Asia", "lat": 25.2854, "lon": 51.5310},
    "SA": {"name": "Saudi Arabia", "flag": "🇸🇦", "continent": "Asia", "lat": 24.7136, "lon": 46.6753},
    "SG": {"name": "Singapore", "flag": "🇸🇬", "continent": "Asia", "lat": 1.3521, "lon": 103.8198},
    "SY": {"name": "Syria", "flag": "🇸🇾", "continent": "Asia", "lat": 33.5138, "lon": 36.2765},
    "TH": {"name": "Thailand", "flag": "🇹🇭", "continent": "Asia", "lat": 13.7563, "lon": 100.5018},
    "TJ": {"name": "Tajikistan", "flag": "🇹🇯", "continent": "Asia", "lat": 38.5598, "lon": 68.7870},
    "TL": {"name": "Timor-Leste", "flag": "🇹🇱", "continent": "Asia", "lat": -8.5569, "lon": 125.5603},
    "TM": {"name": "Turkmenistan", "flag": "🇹🇲", "continent": "Asia", "lat": 37.9601, "lon": 58.3261},
    "TR": {"name": "Turkey", "flag": "🇹🇷", "continent": "Asia", "lat": 39.9334, "lon": 32.8597},
    "TW": {"name": "Taiwan", "flag": "🇹🇼", "continent": "Asia", "lat": 25.0330, "lon": 121.5654},
    "UZ": {"name": "Uzbekistan", "flag": "🇺🇿", "continent": "Asia", "lat": 41.2995, "lon": 69.2401},
    "VN": {"name": "Vietnam", "flag": "🇻🇳", "continent": "Asia", "lat": 21.0285, "lon": 105.8542},
    "YE": {"name": "Yemen", "flag": "🇾🇪", "continent": "Asia", "lat": 15.3694, "lon": 44.1910},

    # ── Africa ──
    "AO": {"name": "Angola", "flag": "🇦🇴", "continent": "Africa", "lat": -8.8390, "lon": 13.2894},
    "BF": {"name": "Burkina Faso", "flag": "🇧🇫", "continent": "Africa", "lat": 12.3714, "lon": -1.5197},
    "BI": {"name": "Burundi", "flag": "🇧🇮", "continent": "Africa", "lat": -3.3731, "lon": 29.9189},
    "BJ": {"name": "Benin", "flag": "🇧🇯", "continent": "Africa", "lat": 6.4969, "lon": 2.6289},
    "BW": {"name": "Botswana", "flag": "🇧🇼", "continent": "Africa", "lat": -24.6282, "lon": 25.9231},
    "CD": {"name": "DR Congo", "flag": "🇨🇩", "continent": "Africa", "lat": -4.4419, "lon": 15.2663},
    "CF": {"name": "Central African Republic", "flag": "🇨🇫", "continent": "Africa", "lat": 4.3947, "lon": 18.5582},
    "CG": {"name": "Congo", "flag": "🇨🇬", "continent": "Africa", "lat": -4.2634, "lon": 15.2429},
    "CI": {"name": "Ivory Coast", "flag": "🇨🇮", "continent": "Africa", "lat": 6.8276, "lon": -5.2893},
    "CM": {"name": "Cameroon", "flag": "🇨🇲", "continent": "Africa", "lat": 3.8480, "lon": 11.5021},
    "CV": {"name": "Cape Verde", "flag": "🇨🇻", "continent": "Africa", "lat": 14.9330, "lon": -23.5133},
    "DJ": {"name": "Djibouti", "flag": "🇩🇯", "continent": "Africa", "lat": 11.5721, "lon": 43.1456},
    "DZ": {"name": "Algeria", "flag": "🇩🇿", "continent": "Africa", "lat": 36.7538, "lon": 3.0588},
    "EG": {"name": "Egypt", "flag": "🇪🇬", "continent": "Africa", "lat": 30.0444, "lon": 31.2357},
    "ET": {"name": "Ethiopia", "flag": "🇪🇹", "continent": "Africa", "lat": 9.0320, "lon": 38.7482},
    "GA": {"name": "Gabon", "flag": "🇬🇦", "continent": "Africa", "lat": 0.4162, "lon": 9.4673},
    "GH": {"name": "Ghana", "flag": "🇬🇭", "continent": "Africa", "lat": 5.6037, "lon": -0.1870},
    "GM": {"name": "Gambia", "flag": "🇬🇲", "continent": "Africa", "lat": 13.4549, "lon": -16.5790},
    "GN": {"name": "Guinea", "flag": "🇬🇳", "continent": "Africa", "lat": 9.6412, "lon": -13.5784},
    "GQ": {"name": "Equatorial Guinea", "flag": "🇬🇶", "continent": "Africa", "lat": 3.7504, "lon": 8.7371},
    "GW": {"name": "Guinea-Bissau", "flag": "🇬🇼", "continent": "Africa", "lat": 11.8636, "lon": -15.5977},
    "KE": {"name": "Kenya", "flag": "🇰🇪", "continent": "Africa", "lat": -1.2921, "lon": 36.8219},
    "KM": {"name": "Comoros", "flag": "🇰🇲", "continent": "Africa", "lat": -11.7172, "lon": 43.2473},
    "LR": {"name": "Liberia", "flag": "🇱🇷", "continent": "Africa", "lat": 6.3156, "lon": -10.8074},
    "LS": {"name": "Lesotho", "flag": "🇱🇸", "continent": "Africa", "lat": -29.3151, "lon": 27.4869},
    "LY": {"name": "Libya", "flag": "🇱🇾", "continent": "Africa", "lat": 32.8872, "lon": 13.1913},
    "MA": {"name": "Morocco", "flag": "🇲🇦", "continent": "Africa", "lat": 34.0209, "lon": -6.8416},
    "MG": {"name": "Madagascar", "flag": "🇲🇬", "continent": "Africa", "lat": -18.8792, "lon": 47.5079},
    "ML": {"name": "Mali", "flag": "🇲🇱", "continent": "Africa", "lat": 12.6392, "lon": -8.0029},
    "MR": {"name": "Mauritania", "flag": "🇲🇷", "continent": "Africa", "lat": 18.0735, "lon": -15.9582},
    "MU": {"name": "Mauritius", "flag": "🇲🇺", "continent": "Africa", "lat": -20.1609, "lon": 57.5012},
    "MW": {"name": "Malawi", "flag": "🇲🇼", "continent": "Africa", "lat": -13.9626, "lon": 33.7741},
    "MZ": {"name": "Mozambique", "flag": "🇲🇿", "continent": "Africa", "lat": -25.9692, "lon": 32.5732},
    "NA": {"name": "Namibia", "flag": "🇳🇦", "continent": "Africa", "lat": -22.5609, "lon": 17.0658},
    "NE": {"name": "Niger", "flag": "🇳🇪", "continent": "Africa", "lat": 13.5116, "lon": 2.1254},
    "NG": {"name": "Nigeria", "flag": "🇳🇬", "continent": "Africa", "lat": 9.0765, "lon": 7.3986},
    "RW": {"name": "Rwanda", "flag": "🇷🇼", "continent": "Africa", "lat": -1.9706, "lon": 30.1044},
    "SC": {"name": "Seychelles", "flag": "🇸🇨", "continent": "Africa", "lat": -4.6796, "lon": 55.4920},
    "SD": {"name": "Sudan", "flag": "🇸🇩", "continent": "Africa", "lat": 15.5007, "lon": 32.5599},
    "SL": {"name": "Sierra Leone", "flag": "🇸🇱", "continent": "Africa", "lat": 8.4840, "lon": -13.2299},
    "SN": {"name": "Senegal", "flag": "🇸🇳", "continent": "Africa", "lat": 14.7167, "lon": -17.4677},
    "SO": {"name": "Somalia", "flag": "🇸🇴", "continent": "Africa", "lat": 2.0469, "lon": 45.3182},
    "SS": {"name": "South Sudan", "flag": "🇸🇸", "continent": "Africa", "lat": 4.8594, "lon": 31.5713},
    "ST": {"name": "São Tomé and Príncipe", "flag": "🇸🇹", "continent": "Africa", "lat": 0.3302, "lon": 6.7327},
    "SZ": {"name": "Eswatini", "flag": "🇸🇿", "continent": "Africa", "lat": -26.3054, "lon": 31.1367},
    "TD": {"name": "Chad", "flag": "🇹🇩", "continent": "Africa", "lat": 12.1348, "lon": 15.0557},
    "TG": {"name": "Togo", "flag": "🇹🇬", "continent": "Africa", "lat": 6.1375, "lon": 1.2123},
    "TN": {"name": "Tunisia", "flag": "🇹🇳", "continent": "Africa", "lat": 36.8065, "lon": 10.1815},
    "TZ": {"name": "Tanzania", "flag": "🇹🇿", "continent": "Africa", "lat": -6.1630, "lon": 35.7516},
    "UG": {"name": "Uganda", "flag": "🇺🇬", "continent": "Africa", "lat": 0.3476, "lon": 32.5825},
    "ZA": {"name": "South Africa", "flag": "🇿🇦", "continent": "Africa", "lat": -25.7479, "lon": 28.2293},
    "ZM": {"name": "Zambia", "flag": "🇿🇲", "continent": "Africa", "lat": -15.3875, "lon": 28.3228},
    "ZW": {"name": "Zimbabwe", "flag": "🇿🇼", "continent": "Africa", "lat": -17.8252, "lon": 31.0335},

    # ── Oceania ──
    "AU": {"name": "Australia", "flag": "🇦🇺", "continent": "Oceania", "lat": -35.2809, "lon": 149.1300},
    "FJ": {"name": "Fiji", "flag": "🇫🇯", "continent": "Oceania", "lat": -18.1416, "lon": 178.4419},
    "FM": {"name": "Micronesia", "flag": "🇫🇲", "continent": "Oceania", "lat": 6.9172, "lon": 158.1584},
    "KI": {"name": "Kiribati", "flag": "🇰🇮", "continent": "Oceania", "lat": 1.4518, "lon": 172.9717},
    "MH": {"name": "Marshall Islands", "flag": "🇲🇭", "continent": "Oceania", "lat": 7.1315, "lon": 171.1845},
    "NR": {"name": "Nauru", "flag": "🇳🇷", "continent": "Oceania", "lat": -0.5228, "lon": 166.9315},
    "NZ": {"name": "New Zealand", "flag": "🇳🇿", "continent": "Oceania", "lat": -41.2865, "lon": 174.7762},
    "PG": {"name": "Papua New Guinea", "flag": "🇵🇬", "continent": "Oceania", "lat": -9.4438, "lon": 147.1803},
    "PW": {"name": "Palau", "flag": "🇵🇼", "continent": "Oceania", "lat": 7.5004, "lon": 134.6243},
    "SB": {"name": "Solomon Islands", "flag": "🇸🇧", "continent": "Oceania", "lat": -9.4456, "lon": 159.9729},
    "TO": {"name": "Tonga", "flag": "🇹🇴", "continent": "Oceania", "lat": -21.1790, "lon": -175.1982},
    "TV": {"name": "Tuvalu", "flag": "🇹🇻", "continent": "Oceania", "lat": -8.5375, "lon": 179.1962},
    "VU": {"name": "Vanuatu", "flag": "🇻🇺", "continent": "Oceania", "lat": -17.7333, "lon": 168.3273},
    "WS": {"name": "Samoa", "flag": "🇼🇸", "continent": "Oceania", "lat": -13.8333, "lon": -171.7667},
}

# ── Curated Cities Registry & Exact Coordinates ──
POPULAR_CITIES: dict[str, list[str]] = {
    "NL": ["Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven", "Groningen", "Maastricht"],
    "FR": ["Paris", "Lyon", "Marseille", "Bordeaux", "Nice", "Toulouse", "Strasbourg", "Lille", "Nantes"],
    "CZ": ["Prague", "Brno", "Ostrava", "Plzen", "Liberec", "Olomouc", "Ceske Budejovice"],
    "ES": ["Madrid", "Barcelona", "Valencia", "Seville", "Malaga", "Bilbao", "Granada", "Palma", "Guadalajara", "Alcobendas", "Toledo", "Zaragoza", "Alicante", "Murcia", "San Sebastian", "Salamanca"],
    "IT": ["Rome", "Milan", "Florence", "Venice", "Naples", "Bologna", "Turin"],
    "DE": ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne", "Stuttgart", "Dresden"],
    "GB": ["London", "Edinburgh", "Manchester", "Birmingham", "Glasgow", "Bristol", "Oxford", "Cambridge"],
    "AT": ["Vienna", "Salzburg", "Innsbruck", "Graz"],
    "CH": ["Zurich", "Geneva", "Bern", "Basel", "Lucerne"],
    "BE": ["Brussels", "Antwerp", "Ghent", "Bruges"],
    "PT": ["Lisbon", "Porto", "Faro", "Coimbra"],
    "GR": ["Athens", "Thessaloniki", "Heraklion"],
    "PL": ["Warsaw", "Krakow", "Gdansk", "Wroclaw"],
    "SE": ["Stockholm", "Gothenburg", "Malmo"],
    "NO": ["Oslo", "Bergen", "Trondheim"],
    "DK": ["Copenhagen", "Aarhus", "Odense"],
    "FI": ["Helsinki", "Tampere", "Turku"],
    "IE": ["Dublin", "Cork", "Galway"],
    "US": ["New York", "San Francisco", "Seattle", "Los Angeles", "Chicago", "Boston", "Austin", "Miami"],
    "CA": ["Toronto", "Vancouver", "Montreal", "Ottawa"],
    "MX": ["Mexico City", "Guadalajara", "Monterrey", "Cancun"],
    "JP": ["Tokyo", "Kyoto", "Osaka", "Sapporo", "Fukuoka"],
    "KR": ["Seoul", "Busan", "Incheon"],
    "CN": ["Beijing", "Shanghai", "Shenzhen", "Guangzhou"],
    "TW": ["Taipei", "Kaohsiung"],
    "HK": ["Hong Kong"],
    "SG": ["Singapore"],
    "TH": ["Bangkok", "Chiang Mai", "Phuket"],
    "VN": ["Hanoi", "Ho Chi Minh City", "Da Nang"],
    "ID": ["Jakarta", "Bali", "Bandung"],
    "IN": ["New Delhi", "Mumbai", "Bengaluru"],
    "AU": ["Sydney", "Melbourne", "Brisbane", "Perth"],
    "NZ": ["Auckland", "Wellington", "Christchurch"],
    "BR": ["Sao Paulo", "Rio de Janeiro", "Brasilia"],
    "AR": ["Buenos Aires", "Cordoba", "Mendoza"],
    "CO": ["Bogota", "Medellin", "Cartagena"],
    "CL": ["Santiago", "Valparaiso"],
    "PE": ["Lima", "Cusco"],
    "ZA": ["Cape Town", "Johannesburg", "Durban"],
    "EG": ["Cairo", "Alexandria"],
    "MA": ["Marrakech", "Casablanca", "Rabat"],
    "TR": ["Istanbul", "Ankara", "Izmir"],
    "AE": ["Dubai", "Abu Dhabi"],
}

CITY_COORDINATES: dict[tuple[str, str], tuple[float, float]] = {
    # Netherlands
    ("NL", "amsterdam"): (52.3676, 4.9041),
    ("NL", "rotterdam"): (51.9244, 4.4777),
    ("NL", "the hague"): (52.0705, 4.3007),
    ("NL", "utrecht"): (52.0907, 5.1214),
    ("NL", "eindhoven"): (51.4416, 5.4697),
    ("NL", "groningen"): (53.2194, 6.5665),
    ("NL", "maastricht"): (50.8514, 5.6910),
    # France
    ("FR", "paris"): (48.8566, 2.3522),
    ("FR", "lyon"): (45.7640, 4.8357),
    ("FR", "marseille"): (43.2965, 5.3698),
    ("FR", "bordeaux"): (44.8378, -0.5792),
    ("FR", "nice"): (43.7102, 7.2620),
    ("FR", "toulouse"): (43.6047, 1.4442),
    ("FR", "strasbourg"): (48.5734, 7.7521),
    ("FR", "lille"): (50.6292, 3.0573),
    ("FR", "nantes"): (47.2184, -1.5536),
    # Czech Republic
    ("CZ", "prague"): (50.0755, 14.4378),
    ("CZ", "brno"): (49.1951, 16.6068),
    ("CZ", "ostrava"): (49.8209, 18.2625),
    ("CZ", "plzen"): (49.7384, 13.3736),
    ("CZ", "liberec"): (50.7671, 15.0562),
    ("CZ", "olomouc"): (49.5938, 17.2509),
    ("CZ", "ceske budejovice"): (48.9745, 14.4743),
    # Spain
    ("ES", "madrid"): (40.4168, -3.7038),
    ("ES", "barcelona"): (41.3879, 2.1699),
    ("ES", "valencia"): (39.4699, -0.3763),
    ("ES", "seville"): (37.3891, -5.9845),
    ("ES", "malaga"): (36.7213, -4.4214),
    ("ES", "bilbao"): (43.2630, -2.9350),
    ("ES", "granada"): (37.1773, -3.5986),
    ("ES", "palma"): (39.5696, 2.6502),
    ("ES", "guadalajara"): (40.6327, -3.1646),
    ("ES", "alcobendas"): (40.5400, -3.6358),
    ("ES", "toledo"): (39.8559, -4.0243),
    ("ES", "alcala de henares"): (40.4820, -3.3640),
    ("ES", "getafe"): (40.3071, -3.7332),
    ("ES", "leganes"): (40.3282, -3.7635),
    ("ES", "mostoles"): (40.3223, -3.8649),
    ("ES", "alcorcon"): (40.3458, -3.8249),
    ("ES", "fuenlabrada"): (40.2842, -3.7942),
    ("ES", "san sebastian"): (43.3183, -1.9812),
    ("ES", "santander"): (43.4623, -3.8099),
    ("ES", "oviedo"): (43.3619, -5.8494),
    ("ES", "salamanca"): (40.9701, -5.6635),
    ("ES", "valladolid"): (41.6523, -4.7245),
    ("ES", "zaragoza"): (41.6488, -0.8891),
    ("ES", "alicante"): (38.3452, -0.4810),
    ("ES", "murcia"): (37.9922, -1.1307),
    ("ES", "cordoba"): (37.8882, -4.7794),
    ("ES", "cadiz"): (36.5271, -6.2886),
    # Italy
    ("IT", "rome"): (41.9028, 12.4964),
    ("IT", "milan"): (45.4642, 9.1900),
    ("IT", "florence"): (43.7696, 11.2558),
    ("IT", "venice"): (45.4408, 12.3155),
    ("IT", "naples"): (40.8518, 14.2681),
    ("IT", "bologna"): (44.4949, 11.3426),
    ("IT", "turin"): (45.0703, 7.6869),
    # Germany
    ("DE", "berlin"): (52.5200, 13.4050),
    ("DE", "munich"): (48.1351, 11.5820),
    ("DE", "hamburg"): (53.5511, 9.9937),
    ("DE", "frankfurt"): (50.1109, 8.6821),
    ("DE", "cologne"): (50.9375, 6.9603),
    ("DE", "stuttgart"): (48.7758, 9.1829),
    ("DE", "dresden"): (51.0504, 13.7373),
    # UK
    ("GB", "london"): (51.5074, -0.1278),
    ("GB", "edinburgh"): (55.9533, -3.1883),
    ("GB", "manchester"): (53.4808, -2.2426),
    ("GB", "birmingham"): (52.4862, -1.8904),
    ("GB", "glasgow"): (55.8642, -4.2518),
    ("GB", "bristol"): (51.4545, -2.5879),
    ("GB", "oxford"): (51.7520, -1.2577),
    ("GB", "cambridge"): (52.2053, 0.1218),
    # Austria & Switzerland
    ("AT", "vienna"): (48.2082, 16.3738),
    ("AT", "salzburg"): (47.8095, 13.0550),
    ("AT", "innsbruck"): (47.2692, 11.4041),
    ("AT", "graz"): (47.0707, 15.4395),
    ("CH", "zurich"): (47.3769, 8.5417),
    ("CH", "geneva"): (46.2044, 6.1432),
    ("CH", "bern"): (46.9480, 7.4474),
    ("CH", "basel"): (47.5596, 7.5886),
    # Belgium & Portugal
    ("BE", "brussels"): (50.8503, 4.3517),
    ("BE", "antwerp"): (51.2194, 4.4025),
    ("BE", "ghent"): (51.0543, 3.7174),
    ("BE", "bruges"): (51.2093, 3.2247),
    ("PT", "lisbon"): (38.7223, -9.1393),
    ("PT", "porto"): (41.1579, -8.6291),
    # Other Global Hubs
    ("US", "new york"): (40.7128, -74.0060),
    ("US", "san francisco"): (37.7749, -122.4194),
    ("US", "seattle"): (47.6062, -122.3321),
    ("US", "los angeles"): (34.0522, -118.2437),
    ("US", "chicago"): (41.8781, -87.6298),
    ("CA", "toronto"): (43.6532, -79.3832),
    ("CA", "vancouver"): (49.2827, -123.1207),
    ("JP", "tokyo"): (35.6762, 139.6503),
    ("JP", "kyoto"): (35.0116, 135.7681),
    ("JP", "osaka"): (34.6937, 135.5023),
    ("KR", "seoul"): (37.5665, 126.9780),
    ("CN", "beijing"): (39.9042, 116.4074),
    ("CN", "shanghai"): (31.2304, 121.4737),
    ("AU", "sydney"): (-33.8688, 151.2093),
    ("AU", "melbourne"): (-37.8136, 144.9631),
    ("BR", "sao paulo"): (-23.5505, -46.6333),
    ("AR", "buenos aires"): (-34.6037, -58.3816),
    ("CO", "bogota"): (4.7110, -74.0721),
    ("TR", "istanbul"): (41.0082, 28.9784),
    ("AE", "dubai"): (25.2048, 55.2708),
    ("SG", "singapore"): (1.3521, 103.8198),
}

CAPITAL_CITIES: set[tuple[str, str]] = {
    ("NL", "amsterdam"), ("FR", "paris"), ("CZ", "prague"), ("ES", "madrid"),
    ("IT", "rome"), ("DE", "berlin"), ("GB", "london"), ("AT", "vienna"),
    ("CH", "bern"), ("BE", "brussels"), ("PT", "lisbon"), ("GR", "athens"),
    ("PL", "warsaw"), ("SE", "stockholm"), ("NO", "oslo"), ("DK", "copenhagen"),
    ("FI", "helsinki"), ("IE", "dublin"), ("US", "washington"), ("CA", "ottawa"),
    ("JP", "tokyo"), ("KR", "seoul"), ("CN", "beijing"), ("AU", "canberra"),
    ("NZ", "wellington"), ("BR", "brasilia"), ("AR", "buenos aires"), ("CO", "bogota"),
    ("TR", "ankara"), ("EG", "cairo"), ("MA", "rabat"),
}

FAMOUS_COFFEE_CITIES: set[str] = {
    "vienna", "rome", "seattle", "melbourne", "kyoto", "istanbul",
    "bogota", "addis ababa", "paris", "naples", "san francisco", "amsterdam", "prague"
}

def get_country_options() -> list[str]:
    """Returns formatted, alphabetically-sorted list for st.selectbox: ['🇦🇫 Afghanistan', '🇦🇱 Albania', ...]"""
    sorted_items = sorted(TRAVEL_COUNTRIES.values(), key=lambda x: x["name"])
    return [f"{c['flag']} {c['name']}" for c in sorted_items]

def get_country_code_from_option(option: str) -> str:
    """Reverse-lookup: '🇪🇸 Spain' -> 'ES'"""
    for code, info in TRAVEL_COUNTRIES.items():
        if f"{info['flag']} {info['name']}" == option:
            return code
    return DEFAULT_COUNTRY

def get_option_from_code(code: str) -> str:
    """Forward-lookup: 'ES' -> '🇪🇸 Spain'"""
    info = TRAVEL_COUNTRIES.get(code, TRAVEL_COUNTRIES[DEFAULT_COUNTRY])
    return f"{info['flag']} {info['name']}"

def get_flag_img_html(code: str, width: int = 24, height: int = 18) -> str:
    """Returns an HTML img tag from flagcdn for crisp flag visuals across all browsers."""
    c = code.lower()
    return f'<img src="https://flagcdn.com/w40/{c}.png" width="{width}" height="{height}" style="vertical-align: -2px; margin-right: 6px; border-radius: 2px; box-shadow: 0 1px 3px rgba(0,0,0,0.18);" alt="{code}"/>'

def normalize_city_name(city: str) -> str:
    """Cleans and title-cases city string."""
    if not city:
        return ""
    return city.strip().title()

def get_cities_for_country(country_code: str) -> list[str]:
    """Returns list of popular cities for a country, defaulting to capital/country name if unlisted."""
    if country_code in POPULAR_CITIES:
        return POPULAR_CITIES[country_code]
    country_info = TRAVEL_COUNTRIES.get(country_code)
    return [country_info["name"]] if country_info else ["Central"]

def geocode_city_online(country_code: str, city_name: str) -> tuple[float, float] | None:
    """Queries OpenStreetMap Nominatim with structured city & country parameters for precise municipality coordinates."""
    c_code = country_code.upper()
    
    # 1. Structured query with countrycodes filter
    params = {
        "city": city_name,
        "countrycodes": c_code.lower(),
        "format": "json",
        "limit": "5"
    }
    url = f"https://nominatim.openstreetmap.org/search?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "CoffeeIsMyBestFriend/2.0 (CityTravel)"})
    
    try:
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and len(data) > 0:
                for d in data:
                    if d.get("class") in ["place", "boundary"] and d.get("type") in ["city", "town", "administrative", "village", "municipality"]:
                        return (float(d["lat"]), float(d["lon"]))
                return (float(data[0]["lat"]), float(data[0]["lon"]))
    except Exception:
        pass
        
    # 2. Fallback query with q= and countrycodes
    c_info = TRAVEL_COUNTRIES.get(c_code)
    country_name = c_info["name"] if c_info else c_code
    fallback_params = {
        "q": f"{city_name}, {country_name}",
        "countrycodes": c_code.lower(),
        "format": "json",
        "limit": "5"
    }
    fallback_url = f"https://nominatim.openstreetmap.org/search?{urllib.parse.urlencode(fallback_params)}"
    req_fb = urllib.request.Request(fallback_url, headers={"User-Agent": "CoffeeIsMyBestFriend/2.0 (CityTravel)"})
    
    try:
        with urllib.request.urlopen(req_fb, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and len(data) > 0:
                for d in data:
                    if d.get("class") in ["place", "boundary"] and d.get("type") in ["city", "town", "administrative", "village", "municipality"]:
                        return (float(d["lat"]), float(d["lon"]))
                return (float(data[0]["lat"]), float(data[0]["lon"]))
    except Exception:
        pass
        
    return None

def get_city_coordinates(country_code: str, city: str) -> tuple[float, float]:
    """Returns (lat, lon) for any city in a given country. Checks static catalog, local geocache, and online geocoder with centroid fallback."""
    c_code = country_code.upper()
    c_name = normalize_city_name(city).lower()
    cache_key = f"{c_code}:{c_name}"
    
    # 1. Static dictionary lookup
    if (c_code, c_name) in CITY_COORDINATES:
        return CITY_COORDINATES[(c_code, c_name)]
        
    # 2. Local persistent cache lookup
    if cache_key in _GEOCODE_CACHE:
        cached = _GEOCODE_CACHE[cache_key]
        return (cached[0], cached[1])
        
    # 3. Dynamic online geocoding (e.g. Alcobendas, Delft, Heidelberg, etc.)
    online_coords = geocode_city_online(c_code, normalize_city_name(city))
    if online_coords:
        _GEOCODE_CACHE[cache_key] = [online_coords[0], online_coords[1]]
        _save_geocode_cache()
        return online_coords
        
    # 4. Fallback to country centroid
    country_info = TRAVEL_COUNTRIES.get(c_code)
    if country_info:
        return (country_info["lat"], country_info["lon"])
    return (0.0, 0.0)

def is_capital_city(country_code: str, city: str) -> bool:
    """Checks if a city is a recognized national capital."""
    return (country_code.upper(), normalize_city_name(city).lower()) in CAPITAL_CITIES

def is_coffee_capital(city: str) -> bool:
    """Checks if a city is in the legendary coffee metropolises registry."""
    return normalize_city_name(city).lower() in FAMOUS_COFFEE_CITIES

def compute_passport_stats(
    transactions: list[dict], 
    user: str = None, 
    default_country: str = None, 
    default_city: str = None,
    drink_type: str = "all",
    clicks_data: list[dict] = None
) -> dict:
    """Compute comprehensive country and city travel passport statistics with multi-user, beverage & clicks synchronization."""
    countries_visited = set()
    continents_reached = set()
    cities_visited = set()
    drinks_abroad = 0
    total_logged_with_location = 0
    country_counts: dict[str, int] = {}
    city_counts: dict[tuple[str, str], int] = {}
    city_users_breakdown: dict[tuple[str, str], dict[str, int]] = {}
    country_cities_map: dict[str, set[str]] = {}
    capital_cities_visited = set()
    coffee_capitals_visited = set()

    is_all_users = (user is None or user == "All" or user == "All Crew")
    def_country = default_country or (get_user_default_country(user) if not is_all_users else DEFAULT_COUNTRY)
    def_city = default_city or (get_user_default_city(user) if not is_all_users else "Madrid")

    # Reconcile with clicks_data if provided (so deleted clicks are purged from location stats)
    valid_txs = []
    if transactions:
        all_drink_txs = [t for t in transactions if t.get("transaction_type") == "drink_log"]
        if clicks_data is not None:
            click_user_counts: dict[str, int] = {}
            for c in clicks_data:
                c_user = c.get("user_name")
                click_user_counts[c_user] = click_user_counts.get(c_user, 0) + 1

            txs_by_user: dict[str, list[dict]] = {}
            for tx in all_drink_txs:
                tx_u = tx.get("user_name")
                if tx_u not in txs_by_user:
                    txs_by_user[tx_u] = []
                txs_by_user[tx_u].append(tx)
                
            for tx_u, u_tx_list in txs_by_user.items():
                max_allowed = click_user_counts.get(tx_u, 0)
                sorted_u_txs = sorted(u_tx_list, key=lambda x: str(x.get("created_at", "")), reverse=True)[:max_allowed]
                valid_txs.extend(sorted_u_txs)
        else:
            valid_txs = all_drink_txs

    # Incorporate direct location from clicks_data if location JSON or country/city columns exist in clicks table
    if clicks_data:
        has_direct_loc_clicks = any(
            (isinstance(c.get("location"), dict) and c["location"].get("country")) or ("country" in c and c["country"]) 
            for c in clicks_data
        )
        if has_direct_loc_clicks:
            direct_tx_format = []
            for c in clicks_data:
                loc = c.get("location")
                if isinstance(loc, dict) and loc.get("country"):
                    direct_tx_format.append({
                        "user_name": c.get("user_name"),
                        "created_at": c.get("created_at"),
                        "metadata": {
                            "country": loc.get("country"),
                            "city": loc.get("city"),
                            "drink_id": c.get("drink_id", 1)
                        }
                    })
                elif c.get("country"):
                    direct_tx_format.append({
                        "user_name": c.get("user_name"),
                        "created_at": c.get("created_at"),
                        "metadata": {
                            "country": c.get("country"),
                            "city": c.get("city"),
                            "drink_id": c.get("drink_id", 1)
                        }
                    })
            if direct_tx_format:
                valid_txs = direct_tx_format

    for tx in valid_txs:
        tx_user = tx.get("user_name")
        if not is_all_users and tx_user != user:
            continue

        meta = tx.get("metadata", {})
        if not isinstance(meta, dict):
            continue

        # Beverage Type Filtering
        d_id = meta.get("drink_id")
        d_name = str(meta.get("drink", "")).lower()
        if drink_type == "coffee":
            if d_id is not None and d_id not in [1, 3]:
                continue
            if d_id is None and "coffee" not in d_name:
                continue
        elif drink_type == "tea":
            if d_id is not None and d_id not in [2, 4]:
                continue
            if d_id is None and "tea" not in d_name:
                continue

        country_code = meta.get("country")
        city_name = meta.get("city") or (get_cities_for_country(country_code)[0] if country_code else None)
        
        if country_code and country_code in TRAVEL_COUNTRIES:
            norm_city = normalize_city_name(city_name)
            total_logged_with_location += 1
            countries_visited.add(country_code)
            continents_reached.add(TRAVEL_COUNTRIES[country_code]["continent"])
            
            if norm_city:
                cities_visited.add((country_code, norm_city))
                city_key = (country_code, norm_city)
                city_counts[city_key] = city_counts.get(city_key, 0) + 1
                
                if city_key not in city_users_breakdown:
                    city_users_breakdown[city_key] = {}
                city_users_breakdown[city_key][tx_user] = city_users_breakdown[city_key].get(tx_user, 0) + 1
                
                if country_code not in country_cities_map:
                    country_cities_map[country_code] = set()
                country_cities_map[country_code].add(norm_city)

                if is_capital_city(country_code, norm_city):
                    capital_cities_visited.add((country_code, norm_city))
                if is_coffee_capital(norm_city):
                    coffee_capitals_visited.add(norm_city)

            # Determine if drink is abroad
            user_home_country = get_user_default_country(tx_user) if is_all_users else def_country
            if country_code != user_home_country:
                drinks_abroad += 1
            
            country_counts[country_code] = country_counts.get(country_code, 0) + 1

    most_visited_foreign = None
    if country_counts:
        foreign_counts = {k: v for k, v in country_counts.items() if k != def_country}
        if foreign_counts:
            most_visited_code = max(foreign_counts, key=foreign_counts.get)
            most_visited_foreign = (most_visited_code, foreign_counts[most_visited_code])

    most_visited_city = None
    if city_counts:
        top_city_key = max(city_counts, key=city_counts.get)
        most_visited_city = (top_city_key, city_counts[top_city_key])

    diversity_score = (len(countries_visited) / len(TRAVEL_COUNTRIES)) * 100 if TRAVEL_COUNTRIES else 0.0

    return {
        "countries_visited": countries_visited,
        "continents_reached": continents_reached,
        "cities_visited": cities_visited,
        "drinks_abroad": drinks_abroad,
        "total_logged_with_location": total_logged_with_location,
        "most_visited_foreign": most_visited_foreign,
        "most_visited_city": most_visited_city,
        "country_counts": country_counts,
        "city_counts": city_counts,
        "city_users_breakdown": city_users_breakdown,
        "country_cities_map": country_cities_map,
        "capital_cities_visited": capital_cities_visited,
        "coffee_capitals_visited": coffee_capitals_visited,
        "diversity_score": diversity_score
    }

def get_travel_leaderboard(transactions: list[dict], users: list[str], clicks_data: list[dict] = None) -> list[dict]:
    """Returns sorted list of travel stats including unique cities for leaderboard."""
    leaderboard = []
    
    from data_processing import get_user_preferences
    prefs = get_user_preferences(transactions, users)
    
    for u in users:
        u_def_country = prefs.get(u, {}).get("default_country", get_user_default_country(u))
        u_def_city = prefs.get(u, {}).get("default_city", get_user_default_city(u))
        stats = compute_passport_stats(transactions or [], u, u_def_country, u_def_city)
        leaderboard.append({
            "user": u,
            "cities": len(stats["cities_visited"]),
            "countries": len(stats["countries_visited"]),
            "continents": len(stats["continents_reached"]),
            "drinks_abroad": stats["drinks_abroad"],
            "diversity": stats["diversity_score"]
        })
        
    leaderboard.sort(key=lambda x: (x["cities"], x["countries"], x["continents"], x["drinks_abroad"]), reverse=True)
    return leaderboard

