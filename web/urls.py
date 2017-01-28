"""
URL Mapping for Web version of the app
All web related links have to be served from here
"""
from django.conf.urls import url

from .views import AllComplaints, RawPotholeMap

urlpatterns = [
    url(r'^$', AllComplaints.as_view(), name='all_complaints'),
    url(r'^raw_pothole_map/$', RawPotholeMap.as_view(), name='raw_pothole_map'),
    url(r'^allComplaints$', AllComplaints.as_view(), name='all_complaints')
]
