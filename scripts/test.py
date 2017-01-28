from ride.models import Ride


def run():
    trips = Ride.objects.all()
    for trip in trips:
        gps_file = trip.gps_log
        if gps_file.name.find("_") > 0:
            print(gps_file)
        # try:
        #     zip_file = zipfile.ZipFile(gps_file)
        #     file_names = zip_file.namelist()
        # except zipfile.BadZipFile as ex:
        #     print(gps_file)
        #     continue
        # for file_name in file_names:
        #     # print(file_name)
        #     cnt += 1
        #     # print(cnt)
        #     with zip_file.open(file_name) as f:
        #         # pass
        #         first = True
        #         header = ""
        #         for line in f:
        #             line = line.decode("utf-8")
        #             if first:
        #                 first = False
        #                 header = line.split(",")



        #         f.close()
        # zip_file.close()
        # gps_file.close()
        # print("num files {0}".format(cnt))
