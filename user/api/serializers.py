"""
Serializers for user class
"""
from rest_framework import serializers

from user.models import User


class UserEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for entry in user table. id, Credit, Rating, DeActivate can be changed only by admin
    or server
    """

    class Meta:
        model = User
        read_only_fields = ('id', 'credit', 'rating', 'deactivate')
        fields = ('id', 'name', 'address', 'home_location', 'city',
                  'phone', 'email', 'rating', 'credit', 'deactivate')
