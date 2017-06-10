import csv
import datetime

from ride.models import GroundTruthPotholeLocation


def run():
    with open('scripts/ground_truth.csv', 'r') as csvfile:
        ground_truth = csv.DictReader(csvfile)
        for row in ground_truth:
            g = GroundTruthPotholeLocation()
            g.latitude = row.get('lat')
            g.longitude = row.get('lon')
            g.description = row.get('desc')
            g.reported_date = datetime.datetime.strptime(row.get('date'), "%d-%m-%Y").date()
            g.save()
