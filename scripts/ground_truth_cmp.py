from geopy.distance import vincenty

from ride.models import GroundTruthPotholeLocation, PotholeCluster


def run():
    gphs = GroundTruthPotholeLocation.objects.all()
    pcs = PotholeCluster.objects.all()
    L = []
    for ph in gphs:
        min_dist = 100000
        lat_lon1 = (ph.latitude, ph.longitude)
        for pc in pcs:
            lat_lon2 = (pc.get_snapped_or_center_lat(), pc.get_snapped_or_center_lon())
            min_dist = min(vincenty(lat_lon1, lat_lon2).meters, min_dist)
        print("{},{},dist = {}".format(lat_lon1[0], lat_lon1[1], min_dist))
        L.append(min_dist)
    L.sort()
    print(L)
