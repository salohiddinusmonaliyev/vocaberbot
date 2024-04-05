from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from .models import TelegramUser, Word


# Serializers define the API representation.
class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = '__all__'

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = '__all__'

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = '__all__'

class TestItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = '__all__'