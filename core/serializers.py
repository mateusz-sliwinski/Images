# 3rd-party
from rest_framework.serializers import ModelSerializer

# Project
from core.models import Images
from core.models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        field = ['id', 'name', 'tier']


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Images
        field = '__all__'
