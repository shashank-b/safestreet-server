"""
This file basically contains views for the web page rendering
"""
from django.db.models import Sum
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.views import APIView

from ride.models import Distance, User


class AllComplaints(APIView):
    """
    renders a map which displays all the reports of potholes/speed-breakers
    on it
    """

    def get(self, request):
        """
        simple get request
        """
        return render(request, 'web/complaints.html')


def get_pothole_by_grid(request, gid):
    return render(request, 'web/nearrest_road_kmeans_pothole_map_gid.html', {'gid': gid})


class RawPotholeMap(TemplateView):
    template_name = 'web/intensity.html'


class PrivacyPolicyView(TemplateView):
    template_name = 'web/privacypolicy.html'


class DBScanMap(TemplateView):
    template_name = 'web/clustered_pothole_map.html'


class KmeansMap(TemplateView):
    template_name = 'web/kmeans_pothole_map.html'


class TestMap(TemplateView):
    template_name = 'web/testplot.html'


class TestMap1(TemplateView):
    template_name = 'web/testplot1.html'


class NearrestRoadMap(TemplateView):
    template_name = 'web/nearrest_road_kmeans_pothole_map2.html'


def total_distance(distances):
    tot = 0
    for dist in distances:
        tot += dist['total_dist']
    return tot


class DistanceView(TemplateView):
    template_name = 'web/total_distance.html'

    def get_context_data(self, **kwargs):
        context = super(DistanceView, self).get_context_data(**kwargs)
        distances = Distance.objects.values('user__id', 'user__email').annotate(total_dist=Sum('distance')).order_by(
            '-total_dist')
        context['distance_details'] = distances

        context['total_distance'] = total_distance(distances)

        # context['distance_details'] = Distance.objects.all()
        return context


class DetailDistanceView(TemplateView):
    template_name = 'web/user_distance_details.html'

    def get_context_data(self, **kwargs):
        context = super(DetailDistanceView, self).get_context_data(**kwargs)
        id = self.kwargs['id']
        distances = Distance.objects.filter(user__id=id).values('date').annotate(total_dist=Sum('distance')).order_by(
            '-date')
        context['distance_details'] = distances

        context['total_distance'] = total_distance(distances)
        context['email'] = User.objects.filter(pk=id)[0].email

        # context['distance_details'] = Distance.objects.all()
        return context
