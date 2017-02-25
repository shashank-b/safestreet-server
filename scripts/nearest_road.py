import sys
from time import sleep

import requests
from numpy import genfromtxt
from pandas import DataFrame

API_KEY = "AIzaSyBnrUwvw1vstLchyusZbXIyEZTaGROP3aE"
BASE_URL = "https://roads.googleapis.com/v1/nearestRoads?points={0}&key={1}"
KMEANS_CSV_FILE_PATH = "../media/data/kmeans_cluster.csv"
MAX_NUM_OF_REQUESTS = 100

data = genfromtxt(KMEANS_CSV_FILE_PATH, names=True, delimiter=',')
data = DataFrame(data)

lats = data['lat']
lons = data['lon']

N = len(lats) // MAX_NUM_OF_REQUESTS


def get_query_string(lat_series, lon_series):
    lat_lon_list = list(zip(lat_series, lon_series))
    new_lat_lon_list = []
    for t in lat_lon_list:
        new_lat_lon_list.append(",".join(list(map(str, t))))
    return "|".join(new_lat_lon_list)


print(data.head())


def nearest_road_api():
    cnt = 1
    for i in range(N):
        lo = i * 100
        hi = (i + 1) * 100
        query_str = get_query_string(lats[lo:hi], lons[lo:hi])
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
                data['lat'][lo + index] = lat
                data['lon'][lo + index] = lon
        cnt += 1
        sleep(0.2)
        # break

nearest_road_api()
print(data.head())

NEAREST_ROAD_KMEANS_CSV_FILE_PATH = "../media/data/nearrest_road_kmeans.csv"
header_row_list = ['grid_id', 'direction']
data[header_row_list] = data[header_row_list].astype(int)
data.to_csv(NEAREST_ROAD_KMEANS_CSV_FILE_PATH, index=False)

NEARREST_ROAD_KMEANS_JS_DATA_FILE_PATH = "../media/data/nearrest_road_kmeans.js"

from helper import from_csv_to_js
from_csv_to_js(NEAREST_ROAD_KMEANS_CSV_FILE_PATH, NEARREST_ROAD_KMEANS_JS_DATA_FILE_PATH)
