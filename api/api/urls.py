from django.contrib import admin
from django.urls import path

from rest_framework import routers

from base.views import *

router = routers.DefaultRouter()
router.register(r'telegram-users', TelegramUserViewSet, basename="telegram-user")
router.register(r'word', WordViewSet, basename="word")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
