from geopy.distance import vincenty

from ride.models import Ride, Pothole


def get_distance(loc1, loc2):
    lat_lon1 = (loc1.lattitude, loc1.longitude)
    lat_lon2 = (loc2.lattitude, loc2.longitude)
    return vincenty(lat_lon1, lat_lon2).meters


def run():
    rides = Ride.objects.all()
    cnt = 0
    for ride in rides:
        phs = Pothole.objects.filter(ride=ride).order_by('pk')
        n = len(phs)
        for i in range(n - 1):
            t1 = int(phs[i].event_timestamp)
            t2 = int(phs[i + 1].event_timestamp)
            if abs(t2 - t1) <= 1500:
                p1 = phs[i]
                p2 = phs[i + 1]
                if t1 > t2:
                    p1 = phs[i + 1]
                    p2 = phs[i]
                # dist = get_distance(p1.location, p2.location)
                # event_timestamp = (t1 + t2) // 2
                # p1.event_timestamp = str(event_timestamp)
                # p1.location.lattitude = (p1.location.lattitude + p2.location.lattitude) / 2
                # p1.location.longitude = (p1.location.longitude + p2.location.longitude) / 2
                # p1.location.speed = (p1.location.speed + p2.location.speed) / 2
                # bearing_diff = p1.location.bearing - p2.location.bearing
                # if bearing_diff > 300:
                #     bmin = min(p1.location.bearing, p2.location.bearing)
                #     bmax = max(p1.location.bearing, p2.location.bearing)
                #     bmin += 360
                #     bearing_diff = bmin - bmax
                #     p1.location.bearing = ((bmax + bmin) / 2) % 360
                # else:
                #     p1.location.bearing = (p1.location.bearing + p2.location.bearing) / 2
                # if bearing_diff >= 10:
                print("==================")
                print(p1)
                print(p2)
                print(p1.location)
                print(p2.location)
                # print("distance = {}".format(dist))
                # print("bearing diff = {}".format(bearing_diff))
                # p1.save()
                print("saving p1 {}".format(p1))
                p2.location.delete()
                p2.delete()
                cnt += 1
                print("deleting p2 = {}".format(p2))
                print("time diff = {}".format(t2 - t1))
                print("==================")
    print("deleted {} potholes".format(cnt))
