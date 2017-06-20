from django.contrib import admin

# Register your models here.
from ride.models import Ride, Pothole, Phone, App, PotholeCluster, Grid, Location, GroundTruthPotholeLocation

admin.site.register(Ride)
admin.site.register(Pothole)
admin.site.register(Phone)
admin.site.register(App)
admin.site.register(PotholeCluster)
admin.site.register(Grid)
admin.site.register(Location)
admin.site.register(GroundTruthPotholeLocation)
