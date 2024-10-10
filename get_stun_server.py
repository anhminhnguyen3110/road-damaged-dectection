import requests
import math

GEO_LOC_URL = "https://raw.githubusercontent.com/pradt2/always-online-stun/master/geoip_cache.txt"
IPV4_URL = "https://raw.githubusercontent.com/pradt2/always-online-stun/master/valid_ipv4s.txt"
GEO_USER_URL = "https://geolocation-db.com/json"

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth's surface using the Haversine formula.

    Parameters:
    - lat1, lon1: Latitude and longitude of the first point in degrees.
    - lat2, lon2: Latitude and longitude of the second point in degrees.

    Returns:
    - Distance between the two points in kilometers.
    """
    R = 6371  # Earth's radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi, delta_lambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_stun_server():
    try:
        # Fetch geolocation data for STUN servers
        geo_locs_response = requests.get(GEO_LOC_URL)
        geo_locs_response.raise_for_status()
        geo_locs = geo_locs_response.json()
    except (requests.RequestException, ValueError) as e:
        print(f"Failed to fetch STUN servers' geolocation data: {e}")
        return None

    try:
        # Fetch user's geolocation data
        user_geo_response = requests.get(GEO_USER_URL)
        user_geo_response.raise_for_status()
        user_data = user_geo_response.json()
        user_lat, user_lon = float(user_data["latitude"]), float(user_data["longitude"])
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"Failed to fetch user geolocation data: {e}")
        return None

    try:
        # Fetch list of STUN servers
        ipv4_response = requests.get(IPV4_URL)
        ipv4_response.raise_for_status()
        stun_servers = ipv4_response.text.strip().split('\n')
    except requests.RequestException as e:
        print(f"Failed to fetch STUN servers list: {e}")
        return None

    closest_server = None
    min_distance = float('inf')

    for server in stun_servers:
        server = server.strip()
        if not server:
            continue
        try:
            ip, port = server.split(':')
            server_lat, server_lon = geo_locs.get(ip, (None, None))
            if server_lat is None or server_lon is None:
                continue
            server_lat, server_lon = float(server_lat), float(server_lon)
            distance = haversine_distance(user_lat, user_lon, server_lat, server_lon)
            if distance < min_distance:
                min_distance = distance
                closest_server = server
        except (ValueError, TypeError):
            continue

    if closest_server:
        print(f"Closest free STUN server: {closest_server}")
    else:
        print("No closest STUN server found.")
    return closest_server