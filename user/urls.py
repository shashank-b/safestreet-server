from django.conf.urls import url, include
from rest_framework import routers, serializers, viewsets
from .views import UserList, UserDetail, UserGetComplaintForReview, UserFromEmail

urlpatterns = [
    url(r'^$', UserList.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', UserDetail.as_view()),
    url(r'^userFromEmail/$', UserFromEmail.as_view()),
    url(r'^(?P<pk>[0-9]+)/complaintForReview$', UserGetComplaintForReview.as_view()),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]