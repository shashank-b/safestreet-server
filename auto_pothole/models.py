from django.db import models

from user.models import User


class AutomatedPotholes(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    event_data = models.TextField()
    vehicle_type = models.CharField(max_length=1, default='D')
    win_size = models.IntegerField(null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    classifier_output = models.CharField(max_length=1, default='0')
    classifier_probability = models.FloatField(null=True)
    classifier_intensity = models.FloatField(null=True)
    event_speed = models.FloatField(null=True)
    detection_time = models.DateTimeField(null=True)
    partial_distance = models.FloatField(null=True)

    def __str__(self):
        return "Id: %d, ReporterId: %d, Data: %c" % (self.id, self.reporter.id, self.classifier_output)


class RideDetails(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=1, default='D')
    start_time = models.DateTimeField(null=True)
    stop_time = models.DateTimeField(null=True)
    speed = models.FloatField(null=True)
    distance = models.FloatField(null=True)
    app_version = models.TextField()
    pothole_count = models.IntegerField(null=True)
    phone_model = models.TextField(null=True)

    def __str__(self):
        return "Id: %d, ReporterId: %d" % (self.id, self.reporter.id)
