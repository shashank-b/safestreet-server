from django.db import models


# Create your models here.
# def get_file_path(instance, filename):
# return the path where where you want to save the uploaded file
# return instance.rider.email + "/" + filename


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
