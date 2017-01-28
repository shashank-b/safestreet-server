from ride.models import Ride


def run():
    print("hello")
    trips = Ride.objects.all()
    for trip in trips:
        user = trip.rider
        gps_file = trip.gps_log
        acc_file = trip.acc_log
        print(user, gps_file, acc_file)
