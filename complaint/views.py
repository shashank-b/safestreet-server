from django.shortcuts import render

from .models import Complaint
from django.http import Http404

from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ComplaintList(APIView):
	"""
	Add complaint or get all complaints
	"""
	def get(self, request, format=None):
		complaints = Complaint.objects.all()
		serializer = ComplaintEntrySerializer(complaints, many=True)
		return Response(serializer.data)

	def post(self, request, format=None):
		serializer = ComplaintAddSerializer(data = request.data)       
		if serializer.is_valid():
			serializer.save()  
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ComplaintDetail(APIView):
	"""
    Retrieve, update or delete a complaint instance.
    """
	def get_object(self, pk):
		try:
			return Complaint.objects.get(pk=pk)
		except Complaint.DoesNotExist:
			raise Http404

	def get(self, request, pk, format=None):
		complaint = self.get_object(pk)
		complaint = ComplaintEntrySerializer(complaint)
		return Response(complaint.data)

	def put(self, request, pk, format=None):
		complaint = self.get_object(pk)
		serializer = ComplaintAddSerializer(data = request.data)       
		if serializer.is_valid():
			serializer.save()  
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk, format=None):
		complaint = self.get_object(pk)
		complaint.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)