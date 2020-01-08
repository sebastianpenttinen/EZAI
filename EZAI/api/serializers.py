from django.contrib.auth import get_user_model  
from rest_framework import serializers  
from .models import MLModel

User = get_user_model()

class UserSerializer(serializers.HyperlinkedModelSerializer): 
    class Meta: 
        model = User 
        fields = ('url', 'username', 'email')

class MLModelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MLModel
        fields =('title', 'description', 'file')
