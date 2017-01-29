import zipfile

from ride.models import Ride

DATA_FILE_FULL_PATH = "media/data/data1.js"


def run():
    trips = Ride.objects.all()
    with open(DATA_FILE_FULL_PATH, "w") as fw:
        print("var data = [ ", file=fw, end="")
        for trip in trips:
            gps_file = trip.gps_log
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
                        if first:
                            header = line.split(",")
                            if len(header) < 7:
                                break
                            first = False
                            continue
                        parts = line.split(",")
                        # print(parts)
                        if (len(parts) == 7) and parts[6] == "y":
                            lat = parts[1]
                            lon = parts[2]
                            acc = parts[3]
                            speed = float(parts[4]) * 3.6
                            bearing = parts[5]
                            print("[{0},{1},{2},{3},{4}],".format(
                                lat, lon, acc, speed, bearing), file=fw, end=""
                            )

                    f.close()
            zip_file.close()
            gps_file.close()
        print("]", file=fw, end="")
