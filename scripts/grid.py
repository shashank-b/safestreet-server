import operator
from math import floor, ceil

import numpy as np
from sklearn.cluster import KMeans

MIN_LAT = 500
MAX_LAT = -500
MIN_LON = 500
MAX_LON = -500
INCR_LAT = 0.001
INCR_LON = INCR_LAT

MERGE_CLOSE_FILE_PATH = "../media/data/merge_data.csv"
with open(MERGE_CLOSE_FILE_PATH) as fr:
    header_len = -1
    for line in fr:
        parts = line.split(",")
        if header_len == -1:
            header_len = len(parts)
            continue
        if len(parts) == header_len:
            lat = float(parts[0])
            lon = float(parts[1])
            MIN_LAT = min(MIN_LAT, lat)
            MAX_LAT = max(MAX_LAT, lat)

            MIN_LON = min(MIN_LON, lon)
            MAX_LON = max(MAX_LON, lon)

            # print(min_lat, max_lat)

            # print(min_lon, max_lon)
            # num_rows = (max_lat - min_lat) / .001
            # num_cols = (max_lon - min_lon) / .001
            # num_rows, num_cols = (int(ceil(num_rows)), int(ceil(num_cols)))
            # print(num_rows, num_cols)
            # print(num_rows*num_cols)

NUM_ROWS = (MAX_LAT - MIN_LAT) / INCR_LAT
NUM_COLS = (MAX_LON - MIN_LON) / INCR_LON
NUM_ROWS, NUM_COLS = (int(ceil(NUM_ROWS)), int(ceil(NUM_COLS)))
GRIDS = {}
# 0 -> lat,
# 1 -> lon,
# 2 -> accuracy,
# 3 -> speed,
# 4 -> bearing,
# 5 -> reporter_id,
# 7 -> trip_id
LAT_INDEX = 0
LONG_INDEX = 1
SPEED_INDEX = 2
BEARING_INDEX = 3
TRIP_ID_INDEX = 4

with open(MERGE_CLOSE_FILE_PATH) as fr:
    header_len = -1
    for line in fr:
        parts = line.split(",")
        if header_len == -1:
            header_len = len(parts)
            continue
        if len(parts) == header_len:
            lat = float(parts[0])
            lon = float(parts[1])
            speed = float(parts[3])
            bearing = float(parts[4])
            trip_id = int(parts[6])
            r = int(floor((lat - MIN_LAT) / INCR_LAT))
            c = int(floor((lon - MIN_LON) / INCR_LON))
            index = str(r) + "," + str(c)
            val = (lat, lon, speed, bearing, trip_id)
            if index in GRIDS:
                GRIDS[index].append(val)
            else:
                GRIDS[index] = [val]


def get_k(grid):
    """
    tuple = (lat,lon,speed,bearing,trip_id)
    :param grid:
    :type grid: list of tuples
    :return:
    :rtype:
    """
    # for
    trip_id_count = {}
    for location in grid:
        trip_id = location[TRIP_ID_INDEX]
        if trip_id not in trip_id_count:
            trip_id_count[trip_id] = 1
        else:
            trip_id_count[trip_id] += 1
    pothole_count_list = list(trip_id_count.values())
    pothole_count_list.sort()
    median_index = len(pothole_count_list) - 1
    median_index //= 2
    return pothole_count_list[median_index]


def get_cluster(grid, k):
    lat_long_list = []
    for location in grid:
        lat_long_list.append((location[LAT_INDEX], location[LONG_INDEX]))

    X = np.array(lat_long_list)
    kmeans = KMeans(n_clusters=k).fit(X)
    return kmeans


def separate_direction(grid):
    """
    :param grid: list of tuples
    :type grid:
    :return:
    :rtype:
    grid = [(lat, lon, speed, bearing, trip_id),(lat, lon, speed, bearing, trip_id)]
    """
    grid.sort(key=operator.itemgetter(BEARING_INDEX), reverse=True)
    partition_index = 0
    prev_loc = None
    for location in grid:
        if prev_loc is None:
            prev_loc = location
            continue
        if prev_loc[BEARING_INDEX] - location[BEARING_INDEX] >= 150:
            break
        partition_index += 1
    # print(partition_index)
    # smaller bearing
    # grid1 = [180,179,0]
    grid1 = grid[partition_index + 1:]

    # larger bearing
    # grid2 = [359,355,340]
    grid2 = grid[:partition_index + 1]

    # moving 0-10 degree bearing to grid2 with bearing = bearing + 360
    if len(grid2) > 0 and grid2[0][BEARING_INDEX] > 350:
        while len(grid1) > 0 and grid1[-1][BEARING_INDEX] < 10:
            loc = grid1.pop()
            new_loc = (loc[0], loc[1], loc[2], loc[3] + 360, loc[4])
            grid2.append(new_loc)
    return grid1, grid2
    # print("k = {0}".format(k))
    # for item in grid:
    # b = item[BEARING_INDEX]
    # if 0 <= b <= 10 or 0 <= (b + 10) % 360 <= 10:
    # print(item[LAT_INDEX], item[LONG_INDEX], item[BEARING_INDEX], item[SPEED_INDEX], item[TRIP_ID_INDEX])


def get_avg_bearing(cluster_id, labels_, pothole_points):
    bearings = []
    for i in range(len(labels_)):
        if labels_[i] == cluster_id:
            bearings.append(pothole_points[i][BEARING_INDEX])
    return np.mean(bearings) % 360


def get_clusters_with_bearing(kmeans, pothole_points):
    clustered_points = []
    cluster_id = 0
    for cluster in kmeans.cluster_centers_:
        avg_bearing = get_avg_bearing(cluster_id, kmeans.labels_, pothole_points)
        lat_center = cluster[0]
        lon_center = cluster[1]
        clustered_points.append((lat_center, lon_center, avg_bearing))
        cluster_id += 1
    return clustered_points


KMEANS_CSV_FILE_PATH = "../media/data/kmeans_cluster.csv"
fw = open(KMEANS_CSV_FILE_PATH, "w")
print("lat,lon,bearing,grid_id,direction", file=fw)
grid_id = 0
direction = 0
# direction = 0 and direction = 1 have bearing difference of 150
for grid_key in GRIDS:
    grid = GRIDS[grid_key]
    g1, g2 = separate_direction(grid)
    k = get_k(grid)
    # if len(g1) > 0 and len(g2) > 0:
    #     if len(g1) < k or len(g2) < k:
    #         print("k = {0}".format(k))
    #         print(g1)
    #         print(g2)
    if len(g1) > 0:
        direction = 0
        kmeans = get_cluster(g1, min(k, len(g1)))
        clustered_points = get_clusters_with_bearing(kmeans, g1)
        for cluster in clustered_points:
            print("{0:.6f},{1:.6f},{2:.2f},{3},{4}".format(cluster[0], cluster[1], cluster[2], grid_id, direction),
                  file=fw)
            # print(clustered_points)
            # print(kmeans.cluster_centers_)
            # print(g1)
    if len(g2) > 0:
        direction = 1
        kmeans = get_cluster(g2, min(k, len(g2)))
        clustered_points = get_clusters_with_bearing(kmeans, g2)
        for cluster in clustered_points:
            print("{0:.6f},{1:.6f},{2:.2f},{3},{4}".format(cluster[0], cluster[1], cluster[2], grid_id, direction),
                  file=fw)
            # print(clustered_points)
            # print(kmeans.cluster_centers_)
            # print(g2)
    grid_id += 1
fw.close()
KMEANS_JS_DATA_FILE_PATH = "../media/data/kmeans_data.js"

with open(KMEANS_CSV_FILE_PATH) as fr:
    header = None
    with open(KMEANS_JS_DATA_FILE_PATH, "w") as fw:
        print("var data = [ ", file=fw)
        for line in fr:
            if header is None:
                header = line
                continue
            print("[{0}]".format(line.strip()), file=fw, end=",")
        print("]", file=fw)
        fw.close()
    fr.close()
