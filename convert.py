import sys
import xml.etree.ElementTree as ET
import eviltransform
from tqdm import tqdm  # Import tqdm for the progress bar
import logging
logging.basicConfig(level=logging.INFO)

def convert_gpx_gcj02_to_wgs84(gpx_content, total_points):
    root = ET.fromstring(gpx_content)
    for i, trkpt in tqdm(enumerate(root.findall(".//{http://www.topografix.com/GPX/1/1}trkpt")), total=total_points, desc="Converting GPX"):
        lon = float(trkpt.attrib["lon"])
        lat = float(trkpt.attrib["lat"])
        new_lat, new_lon = eviltransform.gcj2wgs(lat, lon)
        trkpt.attrib["lon"] = str(new_lon)
        trkpt.attrib["lat"] = str(new_lat)

    return ET.tostring(root, encoding="unicode")

def convert(input_file, output_file):
    try:
        with open(input_file, "r") as f:
            gpx_content = f.read()
        ET.register_namespace("", "http://www.topografix.com/GPX/1/1")

        # Count the number of trackpoints for progress bar
        root = ET.fromstring(gpx_content)
        total_points = len(root.findall(".//{http://www.topografix.com/GPX/1/1}trkpt"))

        converted_gpx = convert_gpx_gcj02_to_wgs84(gpx_content, total_points)

        with open(output_file, "w") as f:
            f.write(converted_gpx)

        logging.info("Successfully convert to wgs.")
    except Exception as e:
        logging.error(f"Error in wgs conversion: {e}")


def get_activity_type(file_path):
    with open(file_path, 'r') as f:
        gpx_content = f.read()
    try:
        # Parse the XML string
        root = ET.fromstring(gpx_content)

        # Find the element containing the sport type
        trk_name_element = root.find(".//{http://www.topografix.com/GPX/1/1}trk/{http://www.topografix.com/GPX/1/1}name")
        if trk_name_element is not None:
            sport_type = trk_name_element.text.strip().split(" ")[1]
            print(sport_type, type(sport_type))
            zeep2strava = {
                '户外跑步': 'Run',
                '健走': 'Walk',
                '户外骑行': 'Ride'
            }
            if sport_type not in zeep2strava:
                raise ValueError(f"Sport type {sport_type} not supported")
            return zeep2strava[sport_type]
        else:
            raise ValueError("Sport type not found in gpx file")
    except ET.ParseError:
        raise

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python gpx_converter.py input.gpx output.gpx")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    convert(input_file, output_file)
    out = get_activity_type(sys.argv[2])
    print(out)