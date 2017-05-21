import zipfile

from ride.models import Ride, Pothole


def run():
    tmin = 0
    pothole_count = 0
    rides = Ride.objects.all()
    for ride in rides:
        acc_log = ride.acc_log
        try:
            zip_file = zipfile.ZipFile(acc_log)
            file_names = zip_file.namelist()
        except zipfile.BadZipFile as ex:
            print("bad zip file =  {0}".format(acc_log.name))
            continue
        total_time = 0
        prev_time = -1
        next_time = -1
        for file_name in file_names:
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
                                if prev_time == -1:
                                    prev_time = time
                                    next_time = time
                                else:
                                    total_time += (next_time - prev_time)
                                    prev_time = next_time
                                    next_time = time
                            except Exception as ex:
                                print(ex)
                                continue
                                # print(time, ax, ay, az)
                    f.close()
            except Exception as ex:
                print(ex)
        zip_file.close()
        acc_log.close()
        count = len(Pothole.objects.filter(ride_id=ride.id))
        total_time = total_time / (1000 * 60)
        print("{},{}".format(total_time, count))
        if count > 0:
            pothole_count += count
            tmin += total_time
    print("time = {}, count = {}".format(tmin,pothole_count))
