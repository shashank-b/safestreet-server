from rest_framework import generics

from ride.api.serializers import RideSerializer
from ride.models import Ride, User


class RideCreateView(generics.CreateAPIView):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer

    def perform_create(self, serializer):
        email = self.request.POST['rider']
        try:
            rider = User.objects.get(email=email)
        except User.DoesNotExist:
            rider = User(email=email)
            rider.save()
        serializer.save(rider=rider)
