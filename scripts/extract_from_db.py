import zipfile
from pathlib import Path

from ride.models import Ride, Location, Pothole

DATA_FILE_FULL_PATH = "media/data/data.csv"


class Constants(object):
    anchor_lat = 9.09023
    anchor_lon = 72.786138


def run():
    # trips = Ride.objects.filter(is_processed=False)
    trips = Ride.objects.all()
    data_file = Path(DATA_FILE_FULL_PATH)

    if not data_file.is_file():
        with data_file.open("a") as fw:
            print("timestamp,lat,lon,accuracy,speed,bearing,reporter_id,trip_id", file=fw)
    with open(DATA_FILE_FULL_PATH, "a") as fw:
        for trip in trips:
            gps_file = trip.gps_log
            trip_id = trip.id
            reporter_id = trip.rider.id
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
                        if first:  # skip the first header row
                            header = line.split(",")
                            if len(header) < 7:
                                break
                            first = False
                            continue
                        parts = line.split(",")
                        # print(parts)
                        if (len(parts) >= 7) and parts[6] == "y" and len(parts) == len(header):
                            timestamp = int(parts[0])
                            lat = float(parts[1])
                            lon = float(parts[2])
                            acc = int(float(parts[3]))
                            # speed in kmph
                            speed = float(parts[4]) * 3.6
                            bearing = float(parts[5])
                            location = Location(
                                lattitude=lat,
                                longitude=lon,
                                speed=speed,
                                accuracy=acc,
                                bearing=bearing
                            )
                            # it is important to first save the location object then assign to pothole object
                            location.save()
                            pothole = Pothole(
                                event_timestamp=timestamp,
                                location=location,
                                ride=trip,
                            )
                            try:
                                pothole.save()
                            except Exception as ex:
                                print(ex)
                                print("error occurred")
                            # print(
                            #     "{:.6f},{:.6f},{:.6f},{},{:.2f},{},{},{}".format(timestamp, float(lat), float(lon),
                            #  acc,
                            #                                                      speed, bearing, reporter_id,
                            # trip_id),
                            #     file=fw, )

                    f.close()
            zip_file.close()
            gps_file.close()

            # trip.is_processed = True
            # trip.save()
