import os

from ride.models import PotholeCluster

min_lat, max_lat = 19.11926, 19.1313226
min_lon, max_lon = 72.9119468, 72.9222894


def run():
    pcs = PotholeCluster.objects.all()
    data_dir = "data2"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    fw = open(os.path.join(data_dir, "clustered_points.txt"), "w")
    print("lat,lon,bearing(m),cluster_size", file=fw)
    for p in pcs:
        lat = p.center_lat
        lon = p.center_lon
        in_lat = min_lat <= lat <= max_lat
        in_lon = min_lon <= lon <= max_lon
        if in_lat and in_lon:
            print("{},{},{},{}".format(lat, lon, p.get_bearing(), p.get_size()), file=fw)
    fw.close()
