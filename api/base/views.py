from django.shortcuts import render


from rest_framework import status, viewsets

from .models import *

from .serializer import *

# Create your views here.
class TelegramUserViewSet(viewsets.ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer

class WordViewSet(viewsets.ModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer

class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer

class TestItemViewSet(viewsets.ModelViewSet):
    queryset = TestItem.objects.all()
    serializer_class = TestItemSerializer