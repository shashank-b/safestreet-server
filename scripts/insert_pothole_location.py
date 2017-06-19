import csv
import math
from bisect import bisect
from collections import deque
from io import StringIO

from ride.models import Ride, Pothole, Location


def sd_and_max_min(eq):
    sum_az = 0
    min_az = 1000
    max_az = -1000
    for e in eq:
        min_az = min(min_az, e[1])
        max_az = max(max_az, e[1])
        sum_az += e[1]
    mean_az = sum_az / len(eq)
    sq_sum = 0
    for e in eq:
        sq_sum += (e[1] - mean_az) ** 2
    return max_az - min_az, math.sqrt(sq_sum / len(eq))


def smooth(smq):
    s = 0
    for e in smq:
        s += e[1]
    return smq[-1][0], s / len(smq)


def get_nearest_loc(gps_list, gps_index, time):
    min_diff = abs(gps_list[gps_index][0] - time)
    min_index = gps_index
    if gps_index - 1 >= 0:
        if abs(gps_list[gps_index - 1][0] - time) < min_diff:
            min_diff = abs(gps_list[gps_index - 1][0] - time)
            min_index = gps_index - 1
    if gps_index + 1 < len(gps_list):
        if abs(gps_list[gps_index + 1][0] - time) < min_diff:
            min_index = gps_index + 1
    return min_index


def run():
    rides = Ride.objects.filter(rider=None)
    for ride in rides:
        # ride.gps_log.open("r")
        gps_text = ride.gps_log.read().decode("utf-8")
        acc_text = ride.acc_log.read().decode("utf-8")
        # gps_text = ride.acc_log.read().decode("utf-8")
        acc_reader = csv.DictReader(StringIO(acc_text))
        gps_reader = csv.DictReader(StringIO(gps_text))

        reor_acc = []
        gps_list = []
        smooth_acc = deque()
        event_win = deque()
        for line in acc_reader:
            reor_acc.append((int(line.get("time")), float(line.get('reaz')), line.get('event_flag')))
        for line in gps_reader:
            gps_list.append((int(line.get('time')), float(line.get('lat')), float(line.get('lon')),
                             float(line.get('speed')), float(line.get('bearing')), float(line.get('accuracy'))))
        # print(reor_acc)

        prev_time = None
        s = 0
        events = []
        for az in reor_acc:
            smooth_acc.append(az)
            s += az[1]
            cur_time = az[0]
            if prev_time is None:
                prev_time = cur_time
            # print(cur_time - prev_time)
            prev_time = cur_time
            while abs(smooth_acc[-1][0] - smooth_acc[0][0]) >= 500:
                s -= smooth_acc.popleft()[1]
            if len(smooth_acc) > 0:
                time, smooth_az = smooth_acc[-1][0], s / len(smooth_acc)
                event_win.append((time, smooth_az))
            while abs(event_win[-1][0] - event_win[0][0]) >= 1000:
                event_win.popleft()
                # print("ew out")

            if az[2] == "e":
                max_min, sd = sd_and_max_min(event_win)
                # print("time = {}, mm = {:.2f}, sd = {:.2f}".format(az[0] / 1000, max_min, sd))
                events.append((az[0], max_min, sd, "e"))
            else:
                max_min, sd = sd_and_max_min(event_win)
                if max_min >= 2 or sd >= math.sqrt(.2):
                    events.append((az[0], max_min, sd, "o"))
                    # print("time = {}, mm = {:.2f}, sd = {:.2f}*".format(az[0] / 1000, max_min, sd))
        # events.sort()
        i = 0
        n = len(events)

        gps_list.sort()
        for e in events:
            e = list(e)
            e[1] = float(e[1])  # max-min
            e[2] = float(e[2])  # sd
            if e[3] == "e":
                time = e[0]
                j = i
                max_min = e[1]
                sd = e[2]
                while j < n and abs(events[j][0] - events[i][0]) <= 1000:
                    ttime = events[j][0]
                    tmax_min = events[j][1]
                    tsd = events[j][2]
                    j += 1
                    if tmax_min >= max_min:
                        if tmax_min == max_min:
                            if tsd > sd:
                                time = ttime
                                max_min = tmax_min
                                sd = tsd
                        else:
                            time = ttime
                            max_min = tmax_min
                            sd = tsd
                gps_index = bisect(gps_list, (time, 0, 0, 0))
                if 0 <= gps_index < len(gps_list):
                    g_index = get_nearest_loc(gps_list, gps_index, time)
                    gtime = gps_list[g_index][0]
                    lat = gps_list[g_index][1]
                    lon = gps_list[g_index][2]
                    speed = gps_list[g_index][3]
                    bearing = gps_list[g_index][4]
                    accuracy = gps_list[g_index][5]
                    time_diff = abs(time - gtime) / 1000
                    if time_diff <= 1:
                        p = Pothole()
                        p.ride = ride
                        p.sd = sd
                        p.max_min = max_min
                        p.event_timestamp = time
                        loc = Location()
                        loc.lattitude = lat
                        loc.longitude = lon
                        loc.speed = speed * 3.6  # in kmph
                        loc.bearing = bearing
                        loc.accuracy = accuracy
                        loc.save()
                        p.location = loc
                        p.save()

                        # print(
                        #     "atime = {} gtime = {} diff = {} max-min = {:.2f} sd = {:.2f} lat = {} lon = {} speed = {"
                        #     "}".format(
                        #         time,
                        #         gtime,
                        #         time_diff,
                        #         max_min,
                        #         sd,
                        #         lat,
                        #         lon,
                        #         speed)
                        # )

            i += 1
            # if len(e) == 4 and e[3] == "y":
            #     print("gtime = {}, mm = {:.2f}, sd = {:.2f}".format(e[0], e[1], e[2]))
            # elif len(e) == 4 and e[3] == "o":
            #     print("otime = {}, mm = {:.2f}, sd = {:.2f}".format(e[0], e[1], e[2]))
            # else:
            #     print("xtime = {}, mm = {:.2f}, sd = {:.2f}".format(e[0], e[1], e[2]))




            # print(event_win)

            # else:
            #     print(az[0])
            # if line.get('event_flag') =="e":
            #     print(line)
            # for line in gps_reader:
            #     if line.get("near_pothole")=="y":
            #         print(line)


            # ride.gps_log.close()
