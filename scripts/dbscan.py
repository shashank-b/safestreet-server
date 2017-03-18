import numpy as np
import pandas as pd
from geopy.distance import great_circle
from shapely.geometry import MultiPoint
from sklearn.cluster import DBSCAN

CSV_FILE_NAME = "db_scan_data.csv"
# 25 meters
MIN_CLUSTER_DISTANCE = .025

CLUSTERED_DATA_FILE_FULL_PATH = "media/data/dbscan_data.js"
DATA_FILE_FULL_PATH = "media/data/data.csv"


def get_centermost_point(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)


def run():
    # generate_csv()
    df = pd.read_csv(DATA_FILE_FULL_PATH)
    coords = df.as_matrix(columns=['lat', 'lon'])
    kms_per_radian = 6371.0088
    epsilon = MIN_CLUSTER_DISTANCE / kms_per_radian
    db = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
    cluster_labels = db.labels_
    num_clusters = len(set(cluster_labels))
    clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])
    print('Number of clusters: {}'.format(num_clusters))
    centermost_points = clusters.map(get_centermost_point)
    with open(CLUSTERED_DATA_FILE_FULL_PATH, "w") as fw:
        print("var data = [\n", file=fw, end="")
        for points in centermost_points:
            print("[{0:.6f},{1:.6f}],".format(points[0], points[1]), file=fw, end="")
        print("]", file=fw, end="")

        # lats, lons = zip(*centermost_points)

