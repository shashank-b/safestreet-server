import zipfile

import numpy as np
import pandas as pd
from geopy.distance import great_circle
from shapely.geometry import MultiPoint
from sklearn.cluster import DBSCAN

from ride.models import Ride

CSV_FILE_NAME = "db_scan_data.csv"
# 25 meters
MIN_CLUSTER_DISTANCE = .025


def get_centermost_point(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)


def run():
    generate_csv()
    df = pd.read_csv(CSV_FILE_NAME)
    coords = df.as_matrix(columns=['lat', 'lon'])
    kms_per_radian = 6371.0088
    epsilon = MIN_CLUSTER_DISTANCE / kms_per_radian
    db = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
    cluster_labels = db.labels_
    num_clusters = len(set(cluster_labels))
    clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])
    print('Number of clusters: {}'.format(num_clusters))
    centermost_points = clusters.map(get_centermost_point)
    with open("media/data/dbscan_data.js", "w") as fw:
        print("var data = [\n", file=fw)
        for points in centermost_points:
            print("{{ \"lat\":{0},\"lon\":{1} }},".format(points[0], points[1]), file=fw)
        print("]", file=fw)

        # lats, lons = zip(*centermost_points)
        # rep_points = pd.DataFrame({'lon': lons, 'lat': lats})
        # rs = rep_points.apply(lambda row: df[(df['lat'] == row['lat']) & (df['lon'] == row['lon'])].iloc[0], axis=1)
        #
        # fig, ax = plt.subplots(figsize=[10, 6])
        # rs_scatter = ax.scatter(rs['lon'], rs['lat'], c='#99cc99', edgecolor='None', alpha=0.7, s=120)
        # df_scatter = ax.scatter(df['lon'], df['lat'], c='k', alpha=0.9, s=3)
        # ax.set_title('Full data set vs DBSCAN reduced set')
        # ax.set_xlabel('Longitude')
        # ax.set_ylabel('Latitude')
        # ax.legend([df_scatter, rs_scatter], ['Full set', 'Reduced set'], loc='upper right')
        # plt.show()


def generate_csv():
    trips = Ride.objects.all()
    header = "lat,lon"
    with open(CSV_FILE_NAME, "w") as fw:
        print(header, file=fw)
        for trip in trips:
            gps_file = trip.gps_log
            try:
                zip_file = zipfile.ZipFile(gps_file)
                file_names = zip_file.namelist()
            except zipfile.BadZipFile as ex:
                # print(gps_file)
                continue
            for file_name in file_names:
                # print(file_name)
                # print(cnt)
                with zip_file.open(file_name) as f:
                    # pass
                    first = True
                    for line in f:
                        line = line.decode("utf-8").strip()
                        if first:
                            header = line.split(",")
                            if len(header) < 7:
                                break
                            first = False
                            continue
                        parts = line.split(",")
                        # print(parts)
                        if (len(parts) == 7) and parts[6] == "y":
                            lat = parts[1]
                            lon = parts[2]
                            # acc = parts[3]
                            # speed = float(parts[4]) * 3.6
                            # bearing = parts[5]
                            print("{0},{1}".format(lat, lon), file=fw)
                    f.close()
            zip_file.close()
            gps_file.close()
