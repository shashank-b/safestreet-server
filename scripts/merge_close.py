from geopy.distance import vincenty

INVALID_LAT_LON = (-500, -500)
MERGE_CLOSE_FILE_PATH = "../media/data/merge_data.csv"


def merge():
    with open("../media/data/data.csv") as fr:
        fw = open(MERGE_CLOSE_FILE_PATH, "w")
        header_len = -1
        prev_lat_lon = INVALID_LAT_LON
        prev_line = ""
        for line in fr:
            line = line.strip()
            parts = line.split(",")
            if header_len == -1:
                print(line, file=fw)
                header_len = len(parts)
                continue
            if len(parts) == header_len:
                lat = float(parts[0])
                lon = float(parts[1])
                speed = parts[2]
                current_lat_lon = (lat, lon)
                speed = float(parts[3])
                bearing = float(parts[4])
                trip_id = int(parts[6])
                if prev_lat_lon != INVALID_LAT_LON and vincenty(prev_lat_lon, current_lat_lon).meters > 10:
                    print(prev_line, file=fw)
                else:
                    print(prev_line)
                prev_line = line
                prev_lat_lon = current_lat_lon
        fw.close()
merge()
