from .models import User

from rest_framework import serializers

class UserEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('Name', 'Address', 'HomeLocation', 'City', 'Phone', 'Email', 'FbId',
         'Rating', 'Credit', 'DeActivate')