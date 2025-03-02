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
    try:
        latitude = float(lat)
        longitude = -float(lon)  # Negative for west longitude
        
        # Validate and constrain coordinates to valid ranges
        if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
            return None
            
        return [longitude, latitude]
    except ValueError:
        return None

# Initialize a list to hold GeoJSON features
features = []

# Split the data into sections based on track identifiers
tracks = re.split(r'\n(?=\d{6})', data)  # Split on date stamps

for track in tracks:
    if not track.strip():  # Skip empty tracks
        continue
        
    lines = track.splitlines()
    if not lines:  # Skip if no lines
        continue
        
    try:
        # Extract any track identifier after the timestamp
        track_match = re.search(r'\d{6}\s+([A-Z]+)', lines[0])
        if track_match:
            track_id = track_match.group(1)
        else:
            continue
    except IndexError:
        continue
    
    # Print for debugging
    print(f"Processing track: {track_id}")
    joined_lines = '\n'.join(lines)  # Create the joined string first
    print(f"Found waypoints: {pattern.findall(joined_lines)}")
    
    # Extract waypoint sequences from the track using re.findall
    waypoints = pattern.findall(joined_lines)
    
    # Skip tracks with no valid waypoints
    if not waypoints:
        continue

    # Convert waypoints to coordinates and filter out invalid ones
    coordinates = [convert_to_coordinates(wp) for wp in waypoints]
    coordinates = [coord for coord in coordinates if coord is not None]
    
    # Validate coordinates
    if len(coordinates) < 2:  # LineString needs at least 2 points
        continue

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

def calculate_bounds(features):
    """Calculate the bounding box for all coordinates"""
    lons = []
    lats = []
    for feature in features:
        coords = feature["geometry"]["coordinates"]
        for lon, lat in coords:
            lons.append(lon)
            lats.append(lat)
    
    if not lons or not lats:
        return None
        
    return [
        [min(lons), min(lats)],  # Southwest corner
        [max(lons), max(lats)]   # Northeast corner
    ]

# Create the GeoJSON structure with bounds
bounds = calculate_bounds(features)
geojson = {
    "type": "FeatureCollection",
    "features": features,
    "bbox": [
        bounds[0][0],  # min longitude
        bounds[0][1],  # min latitude
        bounds[1][0],  # max longitude
        bounds[1][1]   # max latitude
    ] if bounds else None
}

# Save to a GeoJSON file
with open('nat_tracks.geojson', 'w') as f:
    json.dump(geojson, f, indent=4)

print("GeoJSON file 'nat_tracks.geojson' has been created.")
