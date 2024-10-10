import requests

def get_stun_server():
    # Fetch geoLocs data
    response = requests.get("https://raw.githubusercontent.com/pradt2/always-online-stun/master/geoip_cache.txt")
    geoLocs = response.json()

    # Fetch latitude and longitude
    response = requests.get("https://geolocation-db.com/json")
    user_data = response.json()
    latitude, longitude = user_data["latitude"], user_data["longitude"]

    # Fetch and process IPV4 data
    response = requests.get("https://raw.githubusercontent.com/pradt2/always-online-stun/master/valid_ipv4s.txt")
    ip_addresses = response.text.strip().split('\n')

    # Find the closest STUN server
    def calculate_distance(addr):
        stunLat, stunLon = geoLocs.get(addr.split(':')[0], (0, 0))
        dist = ((latitude - stunLat) ** 2 + (longitude - stunLon) ** 2) ** 0.5
        return addr, dist

    closest_addr, _ = min(map(calculate_distance, ip_addresses), key=lambda x: x[1])

    # print("Free STUN Server :", closest_addr)  # prints the IP:PORT of the closest STUN server

    return closest_addr