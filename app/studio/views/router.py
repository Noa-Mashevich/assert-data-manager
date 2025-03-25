# fmt: off
from django.urls import path, include
from rest_framework import routers

from .validator import ValidatorViewSet

router = routers.DefaultRouter()

router.register(r'validator', ValidatorViewSet, basename='studio')

urlpatterns = [
    path('', include(router.urls)),
]
