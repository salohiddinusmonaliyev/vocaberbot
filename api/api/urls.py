from django.contrib import admin
from django.urls import path

from rest_framework import routers

from base.views import *

router = routers.DefaultRouter()
router.register(r'telegram-users', TelegramUserViewSet, basename="telegram-user")
router.register(r'word', WordViewSet, basename="word")
router.register(r'test', TestViewSet, basename="test")
router.register(r'test-item', TestItemViewSet, basename="tet-item")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
