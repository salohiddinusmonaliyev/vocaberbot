from django.shortcuts import render


from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny

from .models import *

from .serializer import *

# Create your views here.
class TelegramUserViewSet(viewsets.ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    permission_classes = [AllowAny]

class WordViewSet(viewsets.ModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    permission_classes = [AllowAny]
