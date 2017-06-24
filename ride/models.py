import json

from django.core.serializers import serialize
from django.db import models


# Create your models here.
# def get_file_path(instance, filename):
# return the path where where you want to save the uploaded file
# return instance.rider.email + "/" + filename

class Constants(object):
    anchor_lat = 9.09023
    anchor_lon = 72.786138
    null_intensity = -100
    null_lat = null_lon = 0
    null_sd = null_max_min = null_speed = null_accuracy = null_bearing = -1


class Phone(models.Model):
    name = models.CharField(max_length=80, blank=True, null=True)
    serial = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return "{},{}".format(self.name, self.serial)


class App(models.Model):
    version = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return "{}".format(self.version)


class User(models.Model):
    email = models.EmailField()

    def __str__(self):
        raw_data = serialize('python', [self])
        output = json.dumps(raw_data[0]['fields'])
        return "pk:{}|{}".format(self.id, output)


class Ride(models.Model):
    rider = models.ForeignKey(User, related_name='rider', blank=True, null=True)
    # file = models.FileField(upload_to='uploads')
    gps_log = models.FileField(upload_to='uploads', blank=True, null=True)
    acc_log = models.FileField(upload_to='uploads')

    phone = models.ForeignKey(
        Phone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    app_version = models.ForeignKey(
        App,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    is_processed = models.BooleanField(default=False)

    def get_phone_serial(self):
        parts = self.acc_log.name.split('.')
        if len(parts) == 9:
            return self.acc_log.name.split('.')[3]
        return self.acc_log.name.split('.')[2]

    def get_app_version(self):
        parts = self.acc_log.name.split('.')
        if len(parts) == 5:
            return "0.0.0"
        if len(parts) == 9:
            return ".".join(parts[5:-1])
        else:
            return ".".join(parts[4:-1])

    # def __str__(self):
    #     return "user: \n{}\n {}\ngps_log = {}\nacc_log = {}\nis_processed = {}".format(self.rider, self.gps_log,
    #                                                                                self.acc_log, self.is_processed)

    def __str__(self):
        # this gives you a list of dicts
        raw_data = serialize('python', [self])
        output = json.dumps(raw_data[0]['fields'])
        return "pk:{}|{}".format(self.id, output)


class Distance(models.Model):
    user = models.ForeignKey(User)
    distance = models.FloatField(default=0)
    date = models.DateField()

    def __str__(self):
        raw_data = serialize('python', [self])
        output = json.dumps(raw_data[0]['fields'])
        return "pk:{}|{}".format(self.id, output)


class Location(models.Model):
    lattitude = models.FloatField(default=Constants.null_lat)
    longitude = models.FloatField(default=Constants.null_lon)
    snapped_lat = models.FloatField(default=Constants.null_lat)
    snapped_lon = models.FloatField(default=Constants.null_lon)
    # in kmph
    speed = models.FloatField(default=Constants.null_speed)
    # in meters
    accuracy = models.FloatField(default=Constants.null_accuracy)
    # in degree
    bearing = models.FloatField(default=Constants.null_bearing)

    def __str__(self):
        # this gives you a list of dicts
        raw_data = serialize('python', [self])
        output = json.dumps(raw_data[0]['fields'])
        return "pk:{}|{}".format(self.id, output)


class Grid(models.Model):
    row = models.IntegerField(default=0)
    col = models.IntegerField(default=0)

    def __str__(self):
        raw_data = serialize('python', [self])
        output = json.dumps(raw_data[0]['fields'])
        return "pk: {}|{}".format(self.id, output)


class PotholeCluster(models.Model):
    center_lat = models.FloatField(default=Constants.null_lat)
    center_lon = models.FloatField(default=Constants.null_lon)
    snapped_lat = models.FloatField(default=Constants.null_lat)
    snapped_lon = models.FloatField(default=Constants.null_lon)
    # avgspeed  in kmph
    speed = models.FloatField(default=Constants.null_speed)
    # in meters
    accuracy = models.FloatField(default=Constants.null_accuracy)
    # avg bearing in degree
    bearing = models.FloatField(default=Constants.null_bearing)
    grid = models.ForeignKey(
        Grid,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        raw_data = serialize('python', [self])
        output = json.dumps(raw_data[0]['fields'])
        return "pk = {}|{}".format(self.id, output)

    def get_bearing(self):
        if self.bearing != -1:
            return self.bearing
        potholes = self.pothole_set.all()
        bearings = [pothole.location.bearing for pothole in potholes]
        bearings.sort()
        i = 0
        if bearings[-1] >= 350:
            while bearings[-1] - bearings[i] >= 340:
                if bearings[i] <= 10:
                    bearings[i] += 360
                    i += 1
        self.bearing = sum(bearings) / len(bearings) % 360
        self.save()
        return self.bearing

    def get_snapped_or_center_lat(self):
        return self.snapped_lat if self.snapped_lat != 0 else self.center_lat

    def get_snapped_or_center_lon(self):
        return self.snapped_lon if self.snapped_lon != 0 else self.center_lon

    def get_size(self):
        return len(self.pothole_set.all())

    def get_avg_intensity(self):
        sint = 0
        cnt = 0
        for p in self.pothole_set.all():
            if p.intensity > 0:
                sint += p.intensity
                cnt += 1
        if cnt > 0:
            return sint / cnt
        return -100


class Pothole(models.Model):
    ride = models.ForeignKey(
        Ride,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    event_timestamp = models.CharField(default="0", max_length=20)
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    pothole_cluster = models.ForeignKey(
        PotholeCluster,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    sd = models.FloatField(default=Constants.null_sd)
    max_min = models.FloatField(default=Constants.null_max_min)
    intensity = models.FloatField(default=Constants.null_intensity)

    def __str__(self):
        raw_data = serialize('python', [self])
        output = json.dumps(raw_data[0]['fields'])
        return "pk : {}|{}".format(self.id, output)


class GroundTruthPotholeLocation(models.Model):
    latitude = models.FloatField(default=Constants.null_lat)
    longitude = models.FloatField(default=Constants.null_lon)
    description = models.TextField(blank=True, null=True)
    reported_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return "lat:{}, lon:{}, desc:{}, date:{}".format(self.latitude, self.longitude, self.description,
                                                         self.reported_date)
