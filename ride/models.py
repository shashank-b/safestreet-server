from django.db import models


# Create your models here.
# def get_file_path(instance, filename):
# return the path where where you want to save the uploaded file
# return instance.rider.email + "/" + filename

class Constants(object):
    anchor_lat = 9.09023
    anchor_lon = 72.786138


class User(models.Model):
    email = models.EmailField()

    def __unicode__(self):
        return "{0}".format(self.email)


class Ride(models.Model):
    rider = models.ForeignKey(User, related_name='rider', blank=True, null=True)
    # file = models.FileField(upload_to='uploads')
    gps_log = models.FileField(upload_to='uploads')
    acc_log = models.FileField(upload_to='uploads')
    is_processed = models.BooleanField(default=False)


class Distance(models.Model):
    user = models.ForeignKey(User)
    distance = models.FloatField(default=0)
    date = models.DateField()

    def __unicode__(self):
        return "email: {0} date: {1} distance: {2}".format(self.user.email, self.date, self.distance)


class Location(models.Model):
    lattitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    snapped_lat = models.FloatField(default=0)
    snapped_lon = models.FloatField(default=0)
    # in kmph
    speed = models.FloatField(default=-1)
    # in meters
    accuracy = models.FloatField(default=-1)
    # in degree
    bearing = models.FloatField(default=-1)


class Grid(models.Model):
    row = models.IntegerField(default=0)
    col = models.IntegerField(default=0)


class PotholeCluster(models.Model):
    center_lat = models.FloatField(default=0)
    center_lon = models.FloatField(default=0)
    snapped_lat = models.FloatField(default=0)
    snapped_lon = models.FloatField(default=0)
    # avgspeed  in kmph
    speed = models.FloatField(default=-1)
    # in meters
    accuracy = models.FloatField(default=-1)
    # avg bearing in degree
    bearing = models.FloatField(default=-1)
    grid = models.ForeignKey(
        Grid,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

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
    sd = models.FloatField(default=-1)
    max_min = models.FloatField(default=-1)
    intensity = models.FloatField(default=-100)
