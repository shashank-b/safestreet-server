import math
import zipfile
from collections import deque

from sklearn.svm import SVC

from ride.models import Ride


def get_pothole_timestamps(gps_log):
    pothole_timestamp_list = []
    try:
        zip_file = zipfile.ZipFile(gps_log)
        file_names = zip_file.namelist()
    except zipfile.BadZipFile as ex:
        print("bad zip file" + gps_log.name)
        return pothole_timestamp_list
    for file_name in file_names:
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
                # print(parts)
                if (len(parts) >= 7) and parts[6] == "y":
                    try:
                        timestamp = int(parts[0])
                        lat = float(parts[1])
                        lon = float(parts[2])
                        speed = float(parts[4]) * 3.6
                        bearing = float(parts[5])
                        pothole_timestamp_list.append((timestamp, lat, lon, speed, bearing))
                    except Exception as ex:
                        print(ex)
                        continue
            f.close()
    zip_file.close()
    gps_log.close()
    return pothole_timestamp_list


fw = None


def init():
    global fw
    fw = open("media/data/pothole_pred.csv", "w")
    print("lat,lon,bearing,speed,sd,max_min,intensity,trip_id", file=fw)


def run():
    init()
    reorient()
    fw.close()
    # unordered_timestamps()


def unordered_timestamps():
    trips = Ride.objects.all()
    for trip in trips:
        acc_log = trip.acc_log
        prev_time = None

        # pothole_timestamps = get_pothole_timestamps(trip.gps_log)
        # if len(pothole_timestamps) == 0:
        #     continue
        try:
            zip_file = zipfile.ZipFile(acc_log)
            file_names = zip_file.namelist()
        except zipfile.BadZipFile as ex:
            print("bad zip file {0}".format(acc_log.name))

        try:
            for file_name in file_names:
                timestamps = []
                # print(file_name)
                # print(cnt)
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
                            time = int(parts[0])
                            if prev_time is None:
                                prev_time = time
                            if time - prev_time < 0:
                                print(time, acc_log.name)
                            prev_time = time
                    f.close()
            acc_log.close()
            zip_file.close()
        except Exception as ex:
            print(ex)


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
                                                                     self.max_min, self.intensity,self.trip_id)


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
    return max_az - min_az, math.sqrt(sq_sum / len(eq)), mean_az


def print_deque(eq, pothole_report_time):
    max_min, sd, mean_az = sd_and_max_min(eq)
    # for e in eq:
    #     print(e)
    print("sd = {:.2f}, max-min = {:.2f} mean_az = {:.2f} len = {} st = {} et={}, dt = {} pt = {}".format(sd, max_min,
                                                                                                          mean_az,
                                                                                                          len(eq),
                                                                                                          eq[0].time,
                                                                                                          eq[-1].time,
                                                                                                          eq[-1].time -
                                                                                                          eq[0].time,
                                                                                                          pothole_report_time))


def smooth(smq):
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


def reoriented_az(acc_rows, gps_rows):
    # raw queue of 15 seconds
    q = deque()
    # event queue of 1 second
    eq = deque()
    # smooth reoriented az queue of .5 second
    smq = deque()
    cnt = 0
    sum_ax = 0
    sum_ay = 0
    sum_az = 0
    for acc_row in acc_rows:
        acc = A(acc_row)
        # print(acc.mag())
        q.append(acc)
        if len(q) > 0 and q[-1].time - q[0].time >= 15000:
            out = q.popleft()
            if out.is_close_to_9_8():
                sum_ax -= out.ax
                sum_ay -= out.ay
                sum_az -= out.az
                cnt -= 1
        if len(q) >= 5 * 15 and cnt != 0:
            mean_ax = sum_ax / cnt
            mean_ay = sum_ay / cnt
            mean_az = sum_az / cnt
            deno = mean_az * mean_az + mean_ax * mean_ax

            if deno != 0:
                theta_y = math.asin(mean_ax / math.sqrt(deno))

                # Rotation across X axis
                theta_x = math.atan2(math.sqrt(mean_ax * mean_ax + mean_az * mean_az), mean_ay)

                # Tweak used to handle data for different coordinate axes
                if mean_az > 0:
                    theta_y = -theta_y
                    theta_x = -theta_x

                cos_y = math.cos(theta_y)
                sin_y = math.sin(theta_y)
                cos_x = math.cos(theta_x)
                sin_x = math.sin(theta_x)

                x = acc.ax
                y = acc.ay
                z = acc.az

                tmp = -x * sin_y + z * cos_y
                new_ax = x * cos_y + z * sin_y
                new_az = y * cos_x - tmp * sin_x
                new_ay = y * sin_x + tmp * cos_x

                smq.append(A((acc.time, new_ax, new_ay, new_az)))
                smooth_az = smooth(smq)
                while len(smq) > 0 and smq[-1].time - smq[0].time > 500:
                    smq.popleft()
                eq.append(smooth_az)
            if len(eq) > 0 and eq[-1].time - eq[0].time >= 1000:
                # max_minus_min_win, sd, mean = sd_and_max_min(eq)
                max_min, sd, mean = sd_and_max_min(eq)
                for g in gps_rows:
                    if eq[0].time <= g.time <= eq[-1].time:
                        # print_deque(eq, g.time)
                        if sd > g.sd:
                            g.sd = sd
                            g.max_min = max_min
                while eq[-1].time - eq[0].time >= 500:
                    eq.popleft()
                    # print(
                    #     "{}|{:.2f},{:.2f},{:.2f}|{:.2f},{:.2f}".format(acc, new_ax, new_ay, new_az, sd,
                    # max_minus_min_win))
        if acc.is_close_to_9_8():
            sum_ax += acc.ax
            sum_ay += acc.ay
            sum_az += acc.az
            cnt += 1


clf = None


def load_model():
    global clf
    x = []
    y = []
    for l in open('staticfiles/model/data-smooth.csv'):
        vals = l.split(',')
        x.append([vals[0], vals[1]])
        y.append(vals[2])

    clf = SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0, degree=3,
              kernel='linear', max_iter=-1, probability=True, random_state=None,
              shrinking=True, tol=0.001, verbose=False)
    clf.fit(x, y)


def get_pothole_info(acc_rows, gps_rows):
    # for gps_row in gps_rows:
    #     pothole_detection_timestamp = gps_row[0]
    #     index = bisect(acc_rows, (pothole_detection_timestamp,))
    reoriented_az(acc_rows, gps_rows)


def print_pothole_reports(gps_rows):
    for g in gps_rows:
        print(g.time, end=",")
    print("len ={}".format(len(gps_rows)))


def print_gps_row(gps_rows,trip):
    # gps_file_name = None
    # acc_file_name = None
    # cnt = 0
    for g in gps_rows:
        # if g.sd == -1:
        #     cnt +=1
        #     gps_file_name = gps_file.name
        #     acc_file_name = acc_file.name
        if g.sd != -1:
            feature_vector = [g.sd, g.max_min]
            pred = clf.predict([feature_vector])[0]
            if pred.strip() == '1':
                dist = clf.decision_function([feature_vector])
                g.intensity = dist[0]
                g.trip_id = trip.id
                print(g, file=fw)


def reorient():
    load_model()
    trips = Ride.objects.all()
    for trip in trips:
        acc_log = trip.acc_log
        gps_rows = get_pothole_timestamps(trip.gps_log)
        if len(gps_rows) == 0:
            continue
        try:
            zip_file = zipfile.ZipFile(acc_log)
            file_names = zip_file.namelist()
        except zipfile.BadZipFile as ex:
            print("bad zip file {0}".format(acc_log.name))
            continue
        try:
            for file_name in file_names:
                acc_rows = []
                # print(file_name)
                # print(cnt)
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
                            acc_rows.append((time, ax, ay, az))
                    # print(pothole_timestamps)
                    # print(timestamps)
                    # print("========")
                    f.close()
            acc_rows.sort()
            gps_rows.sort()
            if len(gps_rows) > 10:
                for i in range(len(gps_rows)):
                    gps_rows[i] = G(gps_rows[i])
                get_pothole_info(acc_rows, gps_rows)
                # print_pothole_reports(gps_rows)
                print_gps_row(gps_rows,trip)
            acc_log.close()
            zip_file.close()
        except Exception as ex:
            print(trip.acc_log.name,trip.gps_log.name)
            print(ex)
