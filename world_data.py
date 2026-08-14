"""Travel country registry, user defaults, and passport computation helpers for the World Update."""

from typing import TypedDict
import pandas as pd

class CountryInfo(TypedDict):
    name: str
    flag: str
    continent: str
    lat: float
    lon: float

# Default home base countries per user
USER_DEFAULT_COUNTRIES: dict[str, str] = {
    "Bea": "NL",   # Netherlands 🇳🇱
    "Fer": "FR",   # France 🇫🇷
    "Cris": "CZ",  # Czech Republic 🇨🇿
}

DEFAULT_COUNTRY = "ES"  # System fallback

def get_user_default_country(user: str) -> str:
    """Returns the default home base country code for a given user."""
    return USER_DEFAULT_COUNTRIES.get(user, DEFAULT_COUNTRY)

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


def compute_passport_stats(transactions: list[dict], user: str, default_country: str) -> dict:
    """Compute travel passport statistics from coin_transactions for a specific user."""
    countries_visited = set()
    continents_reached = set()
    drinks_abroad = 0
    total_logged_with_country = 0
    country_counts: dict[str, int] = {}

    if transactions:
        for tx in transactions:
            if tx.get("user_name") == user and tx.get("transaction_type") == "drink_log":
                meta = tx.get("metadata", {})
                country_code = meta.get("country") if isinstance(meta, dict) else None
                if country_code and country_code in TRAVEL_COUNTRIES:
                    total_logged_with_country += 1
                    countries_visited.add(country_code)
                    continents_reached.add(TRAVEL_COUNTRIES[country_code]["continent"])
                    
                    if country_code != default_country:
                        drinks_abroad += 1
                    
                    country_counts[country_code] = country_counts.get(country_code, 0) + 1

    most_visited_foreign = None
    if country_counts:
        foreign_counts = {k: v for k, v in country_counts.items() if k != default_country}
        if foreign_counts:
            most_visited_code = max(foreign_counts, key=foreign_counts.get)
            most_visited_foreign = (most_visited_code, foreign_counts[most_visited_code])

    diversity_score = (len(countries_visited) / len(TRAVEL_COUNTRIES)) * 100 if TRAVEL_COUNTRIES else 0.0

    return {
        "countries_visited": countries_visited,
        "continents_reached": continents_reached,
        "drinks_abroad": drinks_abroad,
        "total_logged_with_country": total_logged_with_country,
        "most_visited_foreign": most_visited_foreign,
        "country_counts": country_counts,
        "diversity_score": diversity_score
    }

def get_travel_leaderboard(transactions: list[dict], users: list[str]) -> list[dict]:
    """Returns sorted list of travel stats for leaderboard."""
    leaderboard = []
    
    from data_processing import get_user_preferences
    prefs = get_user_preferences(transactions, users)
    
    for u in users:
        u_def = prefs.get(u, {}).get("default_country", get_user_default_country(u))
        stats = compute_passport_stats(transactions or [], u, u_def)
        leaderboard.append({
            "user": u,
            "countries": len(stats["countries_visited"]),
            "continents": len(stats["continents_reached"]),
            "drinks_abroad": stats["drinks_abroad"],
            "diversity": stats["diversity_score"]
        })
        
    leaderboard.sort(key=lambda x: (x["countries"], x["continents"], x["drinks_abroad"]), reverse=True)
    return leaderboard
