import csv
import os

from ride.models import Ride, App, Phone
from serverPothole.settings import MEDIA_ROOT

# BASE_DIRECTORY = "/home/vikrant/Downloads/data"


def get_time_stamp_acc_and_gps_data(event):
    i = 0
    for e in event:
        parts = e.split(",")
        if len(parts) == 10:
            return parts[-1], event[:i], event[i:]
        i += 1
    return "0", [], []


def get_serial(phone_identity):
    return phone_identity.split(".")[-4]


def get_app_version(phone_identity):
    return ".".join(phone_identity.split(".")[-3:])


def get_new_files(phone_identity, app_version, time):
    a_filename = ".".join(["acc.car", phone_identity, time, app_version, "txt"])
    g_filename = ".".join(["gps.car", phone_identity, time, app_version, "txt"])
    # print(a_filename,g_filename)
    if not os.path.exists(MEDIA_ROOT):
        os.makedirs(os.path.join(MEDIA_ROOT,"uploads"))
    a_file = open(os.path.join(MEDIA_ROOT, "uploads", a_filename), "w")
    g_file = open(os.path.join(MEDIA_ROOT, "uploads", g_filename), "w")
    r = Ride()
    r.acc_log.name = a_file.name.replace(MEDIA_ROOT + "/", "")
    r.gps_log.name = g_file.name.replace(MEDIA_ROOT + "/", "")

    app_version_db_obj = App.objects.filter(version=app_version)
    if app_version_db_obj.exists():
        r.app_version = app_version_db_obj[0]
    else:
        av = App(version=app_version)
        av.save()
        r.app_version = av

    phone_name, phone_serial = phone_identity.split(".")
    phone = Phone.objects.filter(name=phone_name, serial=phone_serial)
    if phone.exists():
        r.phone = phone[0]
    else:
        phone = Phone(name=phone_name, serial=phone_serial)
        phone.save()
        r.phone = phone
    r.save()
    print("ride_id {} phone_id {} app_version {}".format(r.id, r.phone_id, r.app_version_id))
    print("time,ax,ay,az,reaz,event_flag", file=a_file)
    print("time,lat,lon,accuracy,speed,bearing,near_pothole,sd,max_min,gps_time", file=g_file)
    return a_file, g_file


def run():
    with open("scripts/data.csv", "r") as f:
        reader = csv.DictReader(f)
        data = []
        for line in reader:
            data.append(line['payload'])
        # if not os.path.exists(BASE_DIRECTORY):
        #     os.makedirs(BASE_DIRECTORY)
        acc_gps_dict = {}
        for row in data:
            event = row.strip("[]").split(";")
            phone_identity = event.pop()
            timestamp, acc_rows, gps_rows = get_time_stamp_acc_and_gps_data(event)
            key = phone_identity
            if acc_gps_dict.get(key) is not None:
                acc_gps_dict[key].append((timestamp, acc_rows, gps_rows))
            else:
                acc_gps_dict[key] = [(timestamp, acc_rows, gps_rows)]

        for key in acc_gps_dict:
            phone_identity = key.replace(" ", "_")
            phone_identity = phone_identity.replace(".", "_", 2)
            app_version = get_app_version(phone_identity)
            phone_identity = phone_identity.replace("." + app_version, "")

            L = acc_gps_dict[key]
            L.sort()
            prev_time = None
            flag = True
            a_file = g_file = None
            for e in L:
                curr_time = int(e[0])
                if flag:
                    flag = False
                    a_file, g_file = get_new_files(phone_identity, app_version, e[0])
                    # print(a_file.name,g_file.name)

                if prev_time is None:
                    prev_time = curr_time

                time_diff = (curr_time - prev_time) // 1000000

                if time_diff >= 1000:
                    if a_file is not None:
                        # print(a_file.name,g_file.name)
                        a_file.close()
                        g_file.close()
                        a_file, g_file = get_new_files(phone_identity, app_version, e[0])

                for a in e[1]:
                    print(a, file=a_file)
                for g in e[2]:
                    print(g, file=g_file)
            a_file.close()
            g_file.close()
