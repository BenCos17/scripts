import requests
import re
import json

# URL for NAT Track NOTAMs
url = "https://www.notams.faa.gov/common/nat.html"

# Fetch the NAT data
response = requests.get(url)
response.raise_for_status()
data = response.text

# Regex pattern to extract waypoint coordinates (e.g., 53/50)
pattern = re.compile(r'(\d{2})/(\d{2,3})')

# Function to convert waypoint to [longitude, latitude]
def convert_to_coordinates(waypoint):
    lat, lon = waypoint
    latitude = int(lat)
    longitude = -int(lon)  # Negative for west longitude
    return [longitude, latitude]

# Initialize a list to hold GeoJSON features
features = []

# Split the data into sections based on track identifiers (e.g., 'A', 'B', ...)
tracks = re.split(r'\n(?=\d{6} [A-Z]+)', data)

for track in tracks:
    lines = track.splitlines()
    track_id = lines[0].split()[1]  # Extract track identifier (e.g., 'A')
    waypoints = []

    # Extract waypoint sequences from the track
    for line in lines:
        match = re.search(r'(\d{2})/(\d{2,3})', line)
        if match:
            waypoint = match.groups()
            waypoints.append(waypoint)

    # Convert waypoints to coordinates
    coordinates = [convert_to_coordinates(wp) for wp in waypoints]

    # Create a GeoJSON feature for the track
    feature = {
        "type": "Feature",
        "properties": {
            "name": f"NAT Track {track_id}",
            "track_id": track_id
        },
        "geometry": {
            "type": "LineString",
            "coordinates": coordinates
        }
    }
    features.append(feature)

# Create the GeoJSON structure
geojson = {
    "type": "FeatureCollection",
    "features": features
}

# Save to a GeoJSON file
with open('nat_tracks.geojson', 'w') as f:
    json.dump(geojson, f, indent=4)

print("GeoJSON file 'nat_tracks.geojson' has been created.")
