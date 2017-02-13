"""
URL Mapping for Web version of the app
All web related links have to be served from here
"""
from django.conf.urls import url

from .views import AllComplaints, RawPotholeMap, DBScanMap, DistanceView, DetailDistanceView, PrivacyPolicyView, \
    KmeansMap

urlpatterns = [
    url(r'^$', AllComplaints.as_view(), name='all_complaints'),
    url(r'^raw_pothole_map/$', RawPotholeMap.as_view(), name='raw_pothole_map'),
    url(r'^clustered_pothole_map/$', DBScanMap.as_view(), name='clustered_pothole_map'),
    url(r'^kmeans/$', KmeansMap.as_view(), name='kmeans_map'),
    url(r'^allComplaints$', AllComplaints.as_view(), name='all_complaints'),
    url(r'^distances/$', DistanceView.as_view(), name='distance_total'),
    url(r'^distances/(?P<id>\d+)/$', DetailDistanceView.as_view(), name='distance_details'),
    url(r'^privacypolicy/$', PrivacyPolicyView.as_view(), name='privacy_policy'),
]
