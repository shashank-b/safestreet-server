from django.shortcuts import render

from .models import User
from django.http import Http404

from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class UserList(APIView):
	"""
	Add user or get all users
	"""
	def get(self, request, format=None):
		users = User.objects.all()
		serializer = UserEntrySerializer(users, many=True)
		return Response(serializer.data)

	def post(self, request, format=None):
		serializer = UserEntrySerializer(data = request.data)       
		if serializer.is_valid():
			serializer.save()  
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetail(APIView):
	"""
    Retrieve, update or delete a user instance.
    """
	def get_object(self, pk):
		try:
			return User.objects.get(pk=pk)
		except User.DoesNotExist:
			raise Http404

	def get(self, request, pk, format=None):
		user = self.get_object(pk)
		user = UserEntrySerializer(user)
		return Response(user.data)

	def put(self, request, pk, format=None):
		user = self.get_object(pk)
		serializer = UserEntrySerializer(data = request.data)       
		if serializer.is_valid():
			serializer.save()  
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk, format=None):
		user = self.get_object(pk)
		user.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)