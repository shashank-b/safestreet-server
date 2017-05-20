from rest_framework import serializers

from ride.models import Ride, User, Pothole, Grid, PotholeCluster


class RideSerializer(serializers.ModelSerializer):
    rider = serializers.EmailField()

    class Meta:
        model = Ride
        fields = ('id', 'gps_log', 'acc_log', 'rider')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email')


# class PotholeClusterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PotholeCluster
#         fields = ('id', 'center_lat', 'center_lon', 'snapped_lat', 'snapped_lon', 'speed', 'accuracy', 'bearing')
#
#
# class GridSerializer(serializers.ModelSerializer):
#     pothole_cluster = serializers.RelatedField(source='')
#     class Meta:
#         model = Grid
#         fields = ('id', 'row', 'col', 'pothole_cluster')
#
#
# class PotholeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Pothole
#         fields = ('id',)
