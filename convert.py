import sys
import xml.etree.ElementTree as ET
# from pyproj import Transformer
import eviltransform
from tqdm import tqdm  # Import tqdm for the progress bar

# def gcj02_to_wgs84(lon, lat):
#     transformer = Transformer.from_crs("EPSG:4490", "EPSG:4326")  # WGS-84 to GCJ-02
#     return transformer.transform(lon, lat)

def convert_gpx_gcj02_to_wgs84(gpx_content, total_points):
    root = ET.fromstring(gpx_content)
    for i, trkpt in tqdm(enumerate(root.findall(".//{http://www.topografix.com/GPX/1/1}trkpt")), total=total_points, desc="Converting GPX"):
        lon = float(trkpt.attrib["lon"])
        lat = float(trkpt.attrib["lat"])
        # new_lon, new_lat = gcj02_to_wgs84(lon, lat)
        new_lat, new_lon = eviltransform.gcj2wgs(lat, lon)
        print(lon, lat, new_lon, new_lat)
        trkpt.attrib["lon"] = str(new_lon)
        trkpt.attrib["lat"] = str(new_lat)

    return ET.tostring(root, encoding="unicode")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python gpx_converter.py input.gpx output.gpx")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

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

        print("Conversion successful!")
    except Exception as e:
        print(f"An error occurred: {e}")
