import httpx
import polyline
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import dotenv
import os
import logging
import sys
import urllib.parse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", encoding="utf-8"),
    ]
)

dotenv.load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Make sure to set this in your .env file

def get_route(origin: str, destination: str, waypoints: list[str] = None) -> list[tuple]:
    """Fetch route from Google Routes API and return decoded coordinates."""
    if waypoints is None:
        waypoints = []
        
    def build_waypoint(s: str) -> dict:
        try:
            parts = s.split(",")
            if len(parts) == 2:
                lat = float(parts[0].strip())
                lng = float(parts[1].strip())
                return {
                    "location": {
                        "latLng": {
                            "latitude": lat,
                            "longitude": lng
                        }
                    }
                }
        except ValueError:
            pass
        return {"address": s}
        
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "routes.polyline.encodedPolyline",
    }
    
    payload = {
        "origin": build_waypoint(origin),
        "destination": build_waypoint(destination),
        "travelMode": "DRIVE"
    }
    
    if waypoints:
        payload["intermediates"] = [build_waypoint(wp) for wp in waypoints]
        
    r = httpx.post(url, headers=headers, json=payload)
    r.raise_for_status()
    data = r.json()

    if "routes" not in data or not data["routes"]:
        raise ValueError(f"API error or no routes found: {data}")

    # Decode the overview polyline (full route)
    encoded = data["routes"][0]["polyline"]["encodedPolyline"]
    return polyline.decode(encoded)  # returns [(lat, lng), ...]


def coords_to_gpx(coords: list[tuple], filename: str = "route.gpx"):
    """Convert list of (lat, lng) to a GPX file."""
    gpx = ET.Element("gpx", {
        "version": "1.1",
        "creator": "google-maps-to-gpx",
        "xmlns": "http://www.topografix.com/GPX/1/1",
    })
    trk = ET.SubElement(gpx, "trk")
    ET.SubElement(trk, "name").text = "Google Maps Route"
    trkseg = ET.SubElement(trk, "trkseg")

    for lat, lng in coords:
        ET.SubElement(trkseg, "trkpt", {"lat": str(lat), "lon": str(lng)})

    tree = ET.ElementTree(gpx)
    ET.indent(tree, space="  ")
    tree.write(filename, encoding="utf-8", xml_declaration=True)
    print(f"Saved {len(coords)} points to {filename}")


def parse_gmaps_url(url: str) -> tuple[str, str, list[str]]:
    """Parse a Google Maps Directions URL and return origin, destination, and waypoints."""
    # Handle decoded and encoded URLs
    parsed = urllib.parse.urlparse(url)
    path = urllib.parse.unquote(parsed.path)

    if "/dir/" not in path:
        raise ValueError("Invalid Google Maps directions URL. Missing '/dir/'.")

    # Extract the part after /dir/
    path_after_dir = path.split("/dir/", 1)[1]
    
    # Split by '/' and take parts until an '@' section, 'data=', or empty
    raw_points = path_after_dir.split("/")
    
    points = []
    for p in raw_points:
        if p.startswith("@") or p.startswith("data="):
            break
        # Replace '+' with space just in case
        p = p.replace("+", " ").strip()
        if p:
            points.append(p)
            
    if len(points) < 2:
        raise ValueError("URL must contain at least an origin and a destination.")
        
    return points[0], points[-1], points[1:-1]


# --- Usage ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <google_maps_url>")
        print("Falling back to default example route...")
        url = "https://www.google.com/maps/dir/Warsaw,+Poland/Łódź,+Poland/Kraków,+Poland/"
    else:
        url = sys.argv[1]

    try:
        origin, destination, waypoints = parse_gmaps_url(url)
        print(f"Origin: {origin}")
        print(f"Destination: {destination}")
        print(f"Waypoints: {waypoints}")
        
        coords = get_route(
            origin=origin,
            destination=destination,
            waypoints=waypoints,
        )
        coords_to_gpx(coords, "route.gpx")
    except Exception as e:
        logging.error(f"Failed to generate GPX: {e}")

