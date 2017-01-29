"""
This file basically contains views for the web page rendering
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.views import APIView


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


class RawPotholeMap(TemplateView):
    template_name = 'web/raw_pothole_map.html'


class ClusteredPotholeMap(TemplateView):
    template_name = 'web/clustered_pothole_map.html'
