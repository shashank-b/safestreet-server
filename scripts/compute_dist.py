import datetime
import zipfile
from collections import deque

from geopy.distance import vincenty

from ride.models import Ride, Distance
from scripts.helper import DBHelper, DB_FILE_NAME

UTC_OFFSET = 19800


def compute_distance(lat_lon1, lat_lon2):
    """
    return distance between lat_lon1 and lat_lon2 in meters
    :param lat_lon1:
    :type lat_lon1:
    :param lat_lon2:
    :type lat_lon2:
    :return:
    :rtype:
    """
    return vincenty(lat_lon1, lat_lon2).meters


def get_distance_and_date(gps_log):
    """

    :param gps_log:
    :type gps_log:
    :return:
    :rtype:
    """
    dist = 0
    temp_dist = 0
    date = None
    try:
        zip_file = zipfile.ZipFile(gps_log)
        file_names = zip_file.namelist()
    except zipfile.BadZipFile as ex:
        print("bad zip file {0}".format(gps_log.name))
        return 0, None
    for file_name in file_names:
        q = deque()
        # print(file_name)
        # print(cnt)
        with zip_file.open(file_name) as f:
            # pass
            first = True
            for line in f:
                line = line.decode("utf-8").strip()
                if first:  # skip the first header row
                    header = line.split(",")
                    if len(header) < 7:
                        break
                    first = False
                    continue
                parts = line.split(",")
                if len(parts) == 2:
                    gps_timestamp = int(parts[0].split(' ')[-1])
                    date = datetime.datetime.utcfromtimestamp(gps_timestamp / 1000 + UTC_OFFSET)

                # print(parts)
                if len(parts) == 7:
                    lat = parts[1]
                    lon = parts[2]
                    lat_lon = (lat, lon)
                    # speed in kmph
                    q.append(lat_lon)
                    lat_lon_last = q[-1]
                    lat_lon_first = q[0]
                    temp_dist = compute_distance(lat_lon_last, lat_lon_first)
                    if temp_dist >= 50:
                        dist += temp_dist
                        temp_dist = 0
                        while len(q) > 1:
                            q.popleft()
            if dist > 0:
                dist += temp_dist
            f.close()
    zip_file.close()
    gps_log.close()
    return dist, date




def run():
    db = DBHelper(DB_FILE_NAME)
    id = db.get_last_processed_row_id()
    print("id = {0}".format(id))
    trips = Ride.objects.filter(pk__gt=id).order_by('pk')
    for trip in trips:
        # print(trip.gps_log.name)
        distance = Distance()
        distance.user = trip.rider
        dist, date = get_distance_and_date(trip.gps_log)
        if dist > 0 and date is not None:
            distance.distance, distance.date = dist, date
            print(dist, date, trip.gps_log.name)
            distance.save()
        id = trip.id
    db.update_last_processed_row_id(id)

# Distance.objects.values('user','date').annotate(total_dist=Sum('dis tance'))
