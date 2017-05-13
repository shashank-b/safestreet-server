import sys
from time import sleep

import requests

from ride.models import PotholeCluster

API_KEY = "AIzaSyDxEK0HgdHN_tGNLQ8hPC41GExS4KzGjtE"
BASE_URL = "https://roads.googleapis.com/v1/nearestRoads?points={0}&key={1}"
# INPUT_CSV_FILE_PATH = "../media/data/markers.csv"
# OUTPUT_CSV_FILE_PATH = "../media/data/markers_snapped.csv"

MAX_NUM_OF_QUERIES_PER_REQUEST = 100


def get_query_string(locs):
    lat_series = []
    lon_series = []
    for l in locs:
        lat_series.append(l.center_lat)
        lon_series.append(l.center_lon)
    lat_lon_list = list(zip(lat_series, lon_series))
    new_lat_lon_list = []
    for t in lat_lon_list:
        new_lat_lon_list.append(",".join(list(map(str, t))))
    return "|".join(new_lat_lon_list)


def nearest_road_api():
    cnt = 1
    locations = PotholeCluster.objects.filter(snapped_lat=0)
    N = len(locations) // MAX_NUM_OF_QUERIES_PER_REQUEST
    print("len locs = {}".format(len(locations)))
    for i in range(N):
        lo = i * MAX_NUM_OF_QUERIES_PER_REQUEST
        hi = (i + 1) * MAX_NUM_OF_QUERIES_PER_REQUEST
        locs = locations[lo:hi]
        query_str = get_query_string(locs)
        # print(query_str)
        url = BASE_URL.format(query_str, API_KEY)
        try:
            print("processing request no " + str(cnt), file=sys.stderr)
            print("sending request ", file=sys.stderr)
            response = requests.get(url).json()
            print("received response ", file=sys.stderr)
        except Exception as e:
            print("error occured at count " + str(cnt), file=sys.stderr)
            continue
        point_list = response.get("snappedPoints")
        duplicate_indexes = set()
        indexes = set()
        for point in point_list:
            idx = point.get('originalIndex')
            if idx not in indexes:
                indexes.add(idx)
            else:
                duplicate_indexes.add(idx)
        print(duplicate_indexes)
        for point in point_list:
            lat = float(point.get("location").get("latitude"))
            lon = float(point.get("location").get("longitude"))
            index = point.get('originalIndex')
            if index not in duplicate_indexes:
                # print(lo, index, lo + index, len(locs))
                locations[lo + index].snapped_lat = lat
                locations[lo + index].snapped_lon = lon
                locations[lo + index].save()
        cnt += 1
        sleep(0.2)
        # break


def run():
    nearest_road_api()
