import os
import zipfile

from ride.models import PotholeCluster


def run():
    pc = PotholeCluster.objects.get(pk=201)
    potholes = pc.pothole_set.all()
    path = str(pc.id)
    if not os.path.exists(path):
        os.makedirs(path)
    for p in potholes:
        filename = p.event_timestamp + "_" + str(p.ride.id)
        event_timestamp = int(p.event_timestamp)
        fw = open(os.path.join(path, filename), "w")
        try:
            zip_file = zipfile.ZipFile(p.ride.acc_log)
            file_names = zip_file.namelist()
        except zipfile.BadZipFile as ex:
            # print(gps_file)
            continue
        for file_name in file_names:
            with zip_file.open(file_name) as f:
                first = True
                for line in f:
                    line = line.decode("utf-8").strip()
                    if first:  # skip the first header row
                        header = line.split(",")
                        print(line, file=fw)
                        if len(header) < 4:
                            break
                        first = False
                        continue
                    parts = line.split(",")
                    timestamp = int(parts[0])
                    # print(parts)
                    if len(parts) == 4:
                        if (event_timestamp - timestamp) <= 15000 or (timestamp - event_timestamp) <= 3000:
                            print(line, file=fw)
                f.close()
        fw.close()
        zip_file.close()
        p.ride.acc_log.close()
