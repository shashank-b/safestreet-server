import bisect
import math
import zipfile
from collections import deque

from sklearn.svm import SVC

from ride.models import Ride


def run():
    reorient()


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


def print_error(ret):
    if ret == G.NO_POINT_CLOSE_TO_9_8:
        return "no point close to 9.8"
    if ret == G.NO_POINT_CLOSE_TO_REPORT:
        return "no point close to report"
    if ret == G.READ_FROM_NEXT_ACC_FILE:
        return "reading from next acc file"
    if ret == G.SUCCESS:
        return "successs"
    return "invalid"


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


def reor_acc(acc, mean_ax, mean_ay, mean_az):
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
    else:
        return A(acc)
    return A((acc.time, new_ax, new_ay, new_az))


def get_intensity(acc_rows, ph, trip):
    # print("finding event_index")
    event_timestamp = int(ph.event_timestamp)
    event_index = bisect.bisect(acc_rows, (event_timestamp,))
    start_index = event_index - 1
    if event_index == len(acc_rows):
        print("reading acc from next file")
        return G.READ_FROM_NEXT_ACC_FILE

    if abs(acc_rows[event_index][0] - event_timestamp) >= 1000:
        print("event_index is not close to acc time")
        print("event_index = {} len(acc_rows) = {} acc_rows[-1].time = {}, event_timestamp =  {}"
              .format(event_index,
                      len(acc_rows),
                      acc_rows[-1][0],
                      ph.event_timestamp))

        at_et = abs(acc_rows[event_index][0] - event_timestamp)
        print("a.time = {} event_timestamp= {} |at-et| = {} acc_log = {}"
              .format(acc_rows[event_index][0],
                      ph.event_timestamp,
                      at_et,
                      trip.acc_log.name))
        return G.NO_POINT_CLOSE_TO_REPORT

    # print("going 15 second back")
    while start_index > 0 and (acc_rows[event_index][0] - acc_rows[start_index][0]) <= 15000:
        start_index -= 1

    # event queue of 1 second
    eq = deque()
    # smooth reoriented az queue of .5 second
    smq = deque()
    cnt = 0
    sum_ax = 0
    sum_ay = 0
    sum_az = 0
    # print("starting from 15 seconds back and going till 13")
    while start_index < len(acc_rows) and acc_rows[start_index][0] <= (acc_rows[event_index][0] - 2500):
        a = A(acc_rows[start_index])
        if a.is_close_to_9_8():
            sum_ax += a.ax
            sum_ay += a.ay
            sum_az += a.az
            cnt += 1
        start_index += 1

    if cnt != 0:
        mean_ax = sum_ax / cnt
        mean_ay = sum_ay / cnt
        mean_az = sum_az / cnt
        # print("calculating mean for reor")
    else:
        # print(trip.id,"no point close to 9.8")
        return G.NO_POINT_CLOSE_TO_9_8
    # print("adding 500 ms worth of smooth data to smooth queue")
    while start_index < len(acc_rows) and acc_rows[start_index][0] <= (acc_rows[event_index][0] - 2000):
        a = A(acc_rows[start_index])
        smq.append(reor_acc(a, mean_ax, mean_ay, mean_az))
        start_index += 1

    # et -1 to et + 1 select maximum sd to gps location
    # print("calulating max sd in event window")

    sd = -1
    max_min = -1
    while start_index < len(acc_rows) and acc_rows[start_index][0] < (acc_rows[event_index][0] + 1000):
        racc = reor_acc(A(acc_rows[start_index]), mean_ax, mean_ay, mean_az)
        smq.append(racc)
        sacc = smooth(smq)
        # print("racc = {}".format(sacc.az))
        eq.append(sacc)
        if (eq[-1].time - eq[0].time) >= 1000:
            max_min_tmp,sd_tmp = sd_and_max_min(eq)
            if max_min_tmp > max_min:
                # print("setting sd to {}".format(sd))
                sd = sd_tmp
                max_min = max_min_tmp

        while (eq[-1].time - eq[0].time) >= 1000:
            eq.popleft()
        while (smq[-1].time - smq[0].time) >= 500:
            smq.popleft()
        start_index += 1

    ph.sd = sd
    ph.max_min = max_min
    return G.SUCCESS


def load_model():
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
    return clf


def get_acc_rows(acc_log, hz50=True):
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
        print("not sorted")
        acc_rows.sort()
    return acc_rows


def is_sorted(lst):
    return all(x <= y for x, y in zip(lst, lst[1:]))


def reorient():
    trips = Ride.objects.all().order_by('acc_log')
    clf = load_model()
    j = 0
    n = len(trips)
    acc_rows1 = []
    acc_rows2 = []
    acc_rows3 = []
    # pallc = []
    hz50 = True
    while j < n:
        print("=============")
        trip = trips[j]
        print("trip = {}".format(trip))

        if j == 0:
            acc_rows2 = get_acc_rows(trips[j].acc_log, hz50=hz50)
        if j + 1 < n:
            acc_rows3 = get_acc_rows(trips[j + 1].acc_log, hz50=hz50)

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
            print("a[0]:{},a[-1]:{} len(acc_row) : {} , len(a1) : {}, len(a2) : {}, len(a3): {}".format(
                acc_rows[0][0], acc_rows[-1][0], len(acc_rows), len(acc_rows1), len(acc_rows2), len(acc_rows3)))

            phs = trip.pothole_set.all()
            for ph in phs:
                get_intensity(acc_rows, ph, trip)
                ph.intensity = clf.decision_function_shape([(ph.max_min, ph.sd)])[0]
                # pallc.append(ph)
                # print(ph)
                ph.save()
        else:
            print("len of acc_rows is zero")
        acc_rows1 = acc_rows2
        acc_rows2 = acc_rows3
        # print_gps_row(gps_rows, trip)
        trips[j].acc_log.close()
        j += 1

        # not_changed = 0
        # changed = 0
        # total = 0
        # fw = open("logs/50hzVs10hz_10.csv", "w")
        # print("id,sd2,m2", file=fw)
        # for p1 in pallc:
        #     # p2 = Pothole.objects.get(pk=p1.id)
        #     if p1.sd != -1:
        #         total += 1
        #         # if p1.sd != p2.sd or p1.max_min != p2.max_min:
        #         print("{},{:.2f},{:.2f}".format(p1.id, p1.sd, p1.max_min), file=fw)
        #         # changed += 1
        #         # else:
        #         #     not_changed += 1
        # print("total = {}, changed = {}, not_changed = {}".format(total, changed, not_changed))
        # fw.close()
