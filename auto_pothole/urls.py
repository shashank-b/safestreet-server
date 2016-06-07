from django.conf.urls import url, include

from .views import AddPothole
from .views import AllRideDetail

urlpatterns = [
    url(r'^add_pothole$', AddPothole.as_view(), name='add_pothole'),
    url(r'^get_potholes/$', AddPothole.as_view(), name='get_pothole'),
    url(r'^allride_details/(?P<pk>[0-9]+)/$', AllRideDetail.as_view(), name='all_ride_details')
]
