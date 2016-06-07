from rest_framework import serializers
from .models import AutomatedPotholes
from .models import RideDetails

class AutomatedPotholeEntrySerializer(serializers.ModelSerializer):
    #Lat = serializers.CharField(source='latitude')
    #Long = serializers.CharField(source='longitude')

    class Meta:
        model = AutomatedPotholes
        fields = ('id','reporter', 'win_size','vehicle_type', 'latitude', 'longitude', 'classifier_output', 'detection_time')

class RideDetailsEntrySerializer(serializers.ModelSerializer):
    #Lat = serializers.CharField(source='latitude')
    #Long = serializers.CharField(source='longitude')

    class Meta:
        model = RideDetails
        fields = ('id','reporter','vehicle_type', 'start_time', 'stop_time', 'speed', 'distance', 'pothole_count')
