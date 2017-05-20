from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    url(r'^rides/$', views.RideCreateView.as_view(), name='ride-list'),
    url(r'^clusters$', views.list_pothole_cluster, name='pothole_cluster_list'),
    url(r'^potholes/$', views.list_potholes, name='pothole_list'),
    url(r'^grids/$', views.list_grids, name='grid_list'),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
