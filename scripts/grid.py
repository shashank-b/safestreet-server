import operator
from math import floor

import numpy as np
from sklearn.cluster import KMeans

from ride.models import Pothole, PotholeCluster, Grid

INCR_LAT = 0.001
INCR_LON = INCR_LAT


class Constants(object):
    anchor_lat = 9.09023
    anchor_lon = 72.786138
    INCR_LAT = 0.001
    INCR_LON = INCR_LAT


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
INTENSITY_INDEX = 5


def get_k(list_of_potholes):
    """
    :param list_of_potholes: list of models.Pothole
    :type list_of_potholes: list of models.Pothole
    :return:
    :rtype: int
    """
    trip_id_count = {}
    for pothole in list_of_potholes:
        trip_id = pothole.ride.id
        if trip_id not in trip_id_count:
            trip_id_count[trip_id] = 1
        else:
            trip_id_count[trip_id] += 1
    pothole_count_list = list(trip_id_count.values())
    pothole_count_list.sort()
    median_index = len(pothole_count_list)
    median_index //= 2
    return pothole_count_list[median_index]


def get_cluster(grid, k):
    lat_long_list = []
    for pothole in grid:
        lat_long_list.append(
            (pothole.location.lattitude, pothole.location.longitude)
        )
    X = np.array(lat_long_list)
    kmeans = KMeans(n_clusters=k).fit(X)
    return kmeans


def separate_direction(list_of_potholes):
    """
    :param list_of_potholes: list of model.Pothole
    :type list
    :return:
    :rtype:
    grid = [model.Pothole, model.Pothole]
    """
    list_of_potholes.sort(key=operator.attrgetter('location.bearing'), reverse=True)
    partition_index = 0
    prev_loc = None
    for pothole in list_of_potholes:
        if prev_loc is None:
            prev_loc = pothole
            continue
        if prev_loc.location.bearing - pothole.location.bearing >= 150:
            break
        partition_index += 1
    # print(partition_index)
    # smaller bearing
    # grid1 = [180,179,0]
    grid1 = list_of_potholes[partition_index + 1:]

    # larger bearing
    # grid2 = [359,355,340]
    grid2 = list_of_potholes[:partition_index + 1]

    # moving 0-10 degree bearing to grid2 with bearing = bearing + 360
    if len(grid2) > 0 and grid2[0].location.bearing > 350:
        while len(grid1) > 0 and grid1[-1].location.bearing < 10:
            loc = grid1.pop()
            # loc.location.bearing += 360
            grid2.append(loc)
    if len(grid1) == 0 and len(grid2) > 0 and grid2[0].location.bearing <= 180:
        return grid2, grid1
    return grid1, grid2


def get_avg_bearing(cluster_id, labels_, pothole_points):
    bearings = []
    cluster_size = 0
    for i in range(len(labels_)):
        if labels_[i] == cluster_id:
            bearings.append(pothole_points[i][BEARING_INDEX])
            cluster_size += 1
    return np.mean(bearings) % 360, cluster_size


def get_clusters_with_bearing(kmeans, pothole_points):
    clustered_points = []
    cluster_id = 0
    for cluster in kmeans.cluster_centers_:
        avg_bearing, cluster_size = get_avg_bearing(cluster_id, kmeans.labels_, pothole_points)
        lat_center = cluster[0]
        lon_center = cluster[1]
        clustered_points.append((lat_center, lon_center, avg_bearing, cluster_size))
        cluster_id += 1
    return clustered_points


# KMEANS_CSV_FILE_PATH = "../media/data/pothole_clusters_with_intensity.csv"
# fw = open(KMEANS_CSV_FILE_PATH, "w")
# print("lat,lon,bearing,speed,intensity,grid_id,label", file=fw)


# direction = 0 and direction = 1 have bearing difference of 150

def save_clusters_to_db(k, list_of_potholes):
    if len(list_of_potholes) == 0:
        return
    kmeans = get_cluster(list_of_potholes, min(k, len(list_of_potholes)))
    current_cluster_id = -1
    for i in range(len(kmeans.labels_)):
        pothole = list_of_potholes[i]
        label = kmeans.labels_[i]
        center_lat = kmeans.cluster_centers_[label][0]
        center_lon = kmeans.cluster_centers_[label][1]
        if current_cluster_id < label:
            row = (center_lat - Constants.anchor_lat) // Constants.INCR_LAT
            col = (center_lon - Constants.anchor_lon) // Constants.INCR_LON
            gs = Grid.objects.filter(row=row, col=col)
            if gs.exists():
                grid = gs[0]
            else:
                grid = Grid(row=row, col=col)
                grid.save()
            pc = PotholeCluster.objects.filter(
                center_lat=center_lat,
                center_lon=center_lon
            )
            if not pc.exists():
                pc = PotholeCluster(
                    center_lat=center_lat,
                    center_lon=center_lon,
                    grid=grid
                )
                pc.save()
            else:
                pc = pc[0]
            current_cluster_id = label
        pothole.pothole_cluster = pc
        pothole.save()


def run():
    potholes = Pothole.objects.filter(intensity__gt=0)
    for pothole in potholes:
        lat = pothole.location.lattitude
        lon = pothole.location.longitude
        r = int(floor((lat - Constants.anchor_lat) / INCR_LAT))
        c = int(floor((lon - Constants.anchor_lon) / INCR_LON))
        index = str(r) + "," + str(c)
        val = pothole
        if index in GRIDS:
            GRIDS[index].append(val)
        else:
            GRIDS[index] = [val]

    for grid_key in GRIDS:
        list_of_potholes = GRIDS[grid_key]
        g1, g2 = separate_direction(list_of_potholes)
        k = get_k(list_of_potholes)
        save_clusters_to_db(k, g1)
        save_clusters_to_db(k, g2)
