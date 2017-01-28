from rest_framework import serializers

from ride.models import Ride, User


class RideSerializer(serializers.ModelSerializer):
    rider = serializers.EmailField()

    class Meta:
        model = Ride
        fields = ('id', 'gps_log','acc_log', 'rider')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email')
