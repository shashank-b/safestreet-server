from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    url(r'^rides/$', views.RideCreateView.as_view(), name='ride-list'),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
