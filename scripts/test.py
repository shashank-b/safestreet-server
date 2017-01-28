import zipfile

from ride.models import Ride


def run():
    trips = Ride.objects.all()
    for trip in trips:
        gps_file = trip.gps_log
        zip_file = zipfile.ZipFile(gps_file)
        file_names = zip_file.namelist()
        for file_name in file_names:
            with zip_file.open(file_name) as f:
                for line in f:
                    print(line)
