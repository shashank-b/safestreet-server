from csv import DictReader
from pathlib import Path

DATA_FILE_FULL_PATH = "media/data/data.csv"

JS_FILE_FULL_PATH = "media/data/data1.js"

LAT = 'lat'
LON = 'lon'
ACCURACY = 'accuracy'
SPEED = 'speed'
BEARING = 'bearing'
REPORTER_ID = 'reporter_id'
TRIP_ID = 'trip_id'


def run():
    data_file = Path(DATA_FILE_FULL_PATH)
    js_file = Path(JS_FILE_FULL_PATH)
    with data_file.open("r") as f_read_csv:
        reader = DictReader(f_read_csv)
        f_write_js = js_file.open("w")
        print("var data=[", file=f_write_js, end="")
        for row in reader:
            lat = row[LAT]
            lon = row[LON]
            acc = row[ACCURACY]
            speed = row[SPEED]
            bearing = row[BEARING]
            reporter_id = row[REPORTER_ID]
            trip_id = row[TRIP_ID]
            print("[{0},{1},{2},{3},{4},{5},{6}],".format(
                lat,
                lon,
                acc,
                speed,
                bearing,
                reporter_id,
                trip_id),
                file=f_write_js,
                end=""
            )
        print("]", file=f_write_js, end="")
        f_write_js.close()
