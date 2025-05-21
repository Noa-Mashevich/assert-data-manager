# fmt: off
# TODO: remove, this is for debugging available end-points.
# import pprint

from django.urls import path, include
from rest_framework import routers

from .element import (
    ElementViewSet,
    ElementVersionViewSet,
    ElementVersionChangesViewSet,
)
from .room import (
    RoomViewSet,
    RoomVersionViewSet,
    RoomVersionChangesViewSet,
)
from .validator import ValidatorViewSet


router = routers.DefaultRouter()

router.register(r'element', ElementViewSet, basename='element')
router.register(r'element/(?P<element_id>[\d]+)/version', ElementVersionViewSet, basename='element-id-version')
router.register(r'element/(?P<element_id>[\d]+)/version/(?P<version_id>[\d]+)/changes', ElementVersionChangesViewSet, basename='element-id-version-id-changes')

router.register(r'room', RoomViewSet, basename='room')
router.register(r'room/(?P<room_id>[\d]+)/version', RoomVersionViewSet, basename='room-id-version')
router.register(r'room/(?P<room_id>[\d]+)/version/(?P<version_id>[\d]+)/changes', RoomVersionChangesViewSet, basename='room-id-version-id-changes')

router.register(r'validator', ValidatorViewSet, basename='validator')

urlpatterns = [
    path('', include(router.urls)),
]

# TODO: remove, this is for debugging available end-points.
# pprint.pprint(router.get_urls())
