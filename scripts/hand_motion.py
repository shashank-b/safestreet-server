from ride.models import PotholeCluster

min_lat, max_lat = 19.11926, 19.1313226
min_lon, max_lon = 72.9119468, 72.9222894

import bisect
import math
import os
import zipfile

from ride.models import Ride

min_lat, max_lat = 19.11926, 19.1313226
min_lon, max_lon = 72.9119468, 72.9222894


class A(object):
    def __init__(self, acc_tup):
        self.time = acc_tup[0]
        self.ax = acc_tup[1]
        self.ay = acc_tup[2]
        self.az = acc_tup[3]

    def mag(self):
        return math.sqrt(self.ax ** 2 + self.ay ** 2 + self.az ** 2)

    def is_close_to_9_8(self):
        return abs(self.mag() - 9.8) <= .5

    def __str__(self):
        return "{},{:.2f},{:.2f},{:.2f}".format(self.time, self.ax, self.ay, self.az)


class G(object):
    NO_POINT_CLOSE_TO_REPORT = 2
    NO_POINT_CLOSE_TO_9_8 = 3
    SUCCESS = 0
    READ_FROM_NEXT_ACC_FILE = 4

    def __init__(self, gps_tup):
        self.time = gps_tup[0]
        self.lat = gps_tup[1]
        self.lon = gps_tup[2]
        self.speed = gps_tup[3]
        self.bearing = gps_tup[4]
        self.sd = -1
        self.max_min = -1
        self.intensity = -1
        self.trip_id = -1

    def __str__(self):
        return "{:.6f},{:.6f},{},{:.2f},{:.2f},{:.2f},{:.2f},{}".format(self.lat, self.lon, self.bearing, self.speed,
                                                                        self.sd,
                                                                        self.max_min, self.intensity, self.trip_id)


def close_to_9_8(acc_row):
    ax = acc_row[1]
    ay = acc_row[2]
    az = acc_row[3]
    return math.sqrt(ax ** 2 + ay ** 2 + az ** 2)


def sd_and_max_min(eq):
    sum_az = 0
    min_az = 1000
    max_az = -1000
    for e in eq:
        min_az = min(min_az, e.az)
        max_az = max(max_az, e.az)
        sum_az += e.az
    mean_az = sum_az / len(eq)
    sq_sum = 0
    for e in eq:
        sq_sum += (e.az - mean_az) ** 2
    return max_az - min_az, math.sqrt(sq_sum / len(eq))


def smooth(smq):
    # print("calculating smooth acc")
    sum_ax = 0
    sum_ay = 0
    sum_az = 0
    for e in smq:
        sum_ax += e.ax
        sum_ay += e.ay
        sum_az += e.az
    sum_ax /= len(smq)
    sum_ay /= len(smq)
    sum_az /= len(smq)
    return A((smq[-1].time, sum_ax, sum_ay, sum_az))


def reor_acc(mean_ax, mean_ay, mean_az):
    deno = mean_az * mean_az + mean_ax * mean_ax
    if deno != 0:
        # print("reorienting {}".format(acc))
        theta_y = math.asin(mean_ax / math.sqrt(deno))

        # Rotation across X axis
        theta_x = math.atan2(math.sqrt(mean_ax * mean_ax + mean_az * mean_az), mean_ay)

        # Tweak used to handle data for different coordinate axes
        if mean_az > 0:
            theta_y = -theta_y
            theta_x = -theta_x
    return theta_x, theta_y


def is_sorted(lst):
    return all(x <= y for x, y in zip(lst, lst[1:]))


def get_acc_rows(acc_log):
    acc_rows = []
    try:
        zip_file = zipfile.ZipFile(acc_log)
        file_names = zip_file.namelist()
    except zipfile.BadZipFile as ex:
        print("bad zip file =  {0}".format(acc_log.name))
        return acc_rows
    cnt = 0
    for file_name in file_names:
        # print(file_name)
        # print(cnt)
        try:
            with zip_file.open(file_name) as f:
                # pass
                first = True
                for line in f:
                    line = line.decode("utf-8").strip()
                    if first:  # skip the first header row
                        header = line.split(",")
                        if len(header) != 4:
                            break
                        first = False
                        continue
                    parts = line.split(",")
                    if len(parts) == 4:
                        try:
                            time = int(parts[0])
                            ax = float(parts[1])
                            ay = float(parts[2])
                            az = float(parts[3])
                        except Exception as ex:
                            print(ex)
                            continue
                        # print(time, ax, ay, az)
                        # if hz50 or cnt % 5 == 0:
                        acc_rows.append((time, ax, ay, az))
                        cnt += 1
                # print(pothole_timestamps)
                # print(timestamps)
                # print("========")
                f.close()
        except Exception as ex:
            print(ex)
    zip_file.close()
    # acc_log.close()
    if not is_sorted(acc_rows):
        # print("not sorted")
        acc_rows.sort()
    return acc_rows


def get_intensity(acc_rows, ph, trip, fw):
    # print("finding event_index")
    event_timestamp = int(ph.event_timestamp)
    event_index = bisect.bisect(acc_rows, (event_timestamp,))
    start_index = event_index - 1
    if event_index == len(acc_rows):
        # print("reading acc from next file")
        return G.READ_FROM_NEXT_ACC_FILE

    if abs(acc_rows[event_index][0] - event_timestamp) >= 1000:
        return G.NO_POINT_CLOSE_TO_REPORT

    # print("going 15 second back")
    while start_index > 0 and (acc_rows[event_index][0] - acc_rows[start_index][0]) <= 15000:
        start_index -= 1

    cnt = 0
    sum_ax = 0
    sum_ay = 0
    sum_az = 0

    # print("starting from 15 seconds back and going till 13")
    while start_index < len(acc_rows) and acc_rows[start_index][0] <= (acc_rows[event_index][0] + 1000):
        a = A(acc_rows[start_index])
        if a.is_close_to_9_8():
            sum_ax += a.ax
            sum_ay += a.ay
            sum_az += a.az
            cnt += 1
        if cnt != 0:
            mean_ax = sum_ax / cnt
            mean_ay = sum_ay / cnt
            mean_az = sum_az / cnt
            theta_x, theta_y = reor_acc(mean_ax, mean_ay, mean_az)
            print("{},{:.2f},{:.2f}".format(acc_rows[start_index][0], math.degrees(theta_x), math.degrees(theta_y)), file=fw)
        start_index += 1


def reorient(p, fw):
    trips = Ride.objects.all().order_by('acc_log')
    k = 0
    for trip in trips:
        if trip.id == p.ride.id:
            break
        k += 1

    j = k
    n = len(trips)
    acc_rows1 = []
    acc_rows2 = []
    acc_rows3 = []
    if j < n:
        print("=============")
        if j - 1 >= 0:
            acc_rows1 = get_acc_rows(trips[j - 1].acc_log)
        if j:
            acc_rows2 = get_acc_rows(trips[j].acc_log)
        if j + 1 < n:
            acc_rows3 = get_acc_rows(trips[j + 1].acc_log)

        t1 = t2 = t3 = t4 = 0
        if len(acc_rows1) > 0:
            t1 = acc_rows1[-1][0]
        if len(acc_rows2) > 0:
            t2 = acc_rows2[0][0]
            t3 = acc_rows2[-1][0]
        if j + 1 < n:
            if len(acc_rows3) > 0:
                t4 = acc_rows3[0][0]

        serial1 = '1'
        serial3 = '3'
        if j >= 1:
            serial1 = trips[j - 1].get_phone_serial()
        serial2 = trips[j].get_phone_serial()
        if (j + 1) < n:
            serial3 = trips[j + 1].get_phone_serial()
        acc_rows = []
        if (j - 1) >= 0 and t2 > t1 and (t2 - t1) <= 50 and serial1 == serial2:
            acc_rows = acc_rows1 + acc_rows2
        if (j + 1) < n and t4 > t3 and (t4 - t3) <= 50 and serial2 == serial3:
            if len(acc_rows) == 0:
                acc_rows = acc_rows2 + acc_rows3
            else:
                acc_rows += acc_rows3

        if len(acc_rows) == 0:
            acc_rows = acc_rows2

        if len(acc_rows) > 0:
            get_intensity(acc_rows, p, trips[j], fw)

        else:
            pass
        if acc_rows1:
            trips[j - 1].acc_log.close()
        if acc_rows3:
            trips[j + 1].acc_log.close()
        if acc_rows2:
            trips[j].acc_log.close()


def extract_info(pc):
    data_dir = os.path.join("data3", str(pc.id))
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    for p in pc.pothole_set.all():
        fw = open(os.path.join(data_dir, p.event_timestamp), "w")
        print("time,theta_x,theta_y",file=fw)
        reorient(p, fw)
        fw.close()


def run():
    pcs = PotholeCluster.objects.all()
    for pc in pcs:
        lat = pc.center_lat
        lon = pc.center_lon
        in_lat = min_lat <= lat <= max_lat
        in_lon = min_lon <= lon <= max_lon
        if in_lat and in_lon:
            extract_info(pc)
