"""
URL Mapping for Web version of the app
All web related links have to be served from here
"""
from django.conf.urls import url

from .views import AllComplaints, RawPotholeMap, ClusteredPotholeMap, DistanceView, DetailDistanceView

urlpatterns = [
    url(r'^$', AllComplaints.as_view(), name='all_complaints'),
    url(r'^raw_pothole_map/$', RawPotholeMap.as_view(), name='raw_pothole_map'),
    url(r'^clustered_pothole_map/$', ClusteredPotholeMap.as_view(), name='clustered_pothole_map'),
    url(r'^allComplaints$', AllComplaints.as_view(), name='all_complaints'),
    url(r'^distances/$', DistanceView.as_view(), name='distance_total'),
    url(r'^distances/(?P<id>\d+)/$', DetailDistanceView.as_view(), name='distance_details'),
]
