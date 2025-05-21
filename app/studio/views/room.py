from rest_framework import (
    mixins,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from server.pagination import LargeResultsSetPagination

from studio.models.room import Room
from studio.models.room_data import RoomData
from studio.models.room_data_change import RoomDataChange
from studio.serializers.room import (
    RoomReadSerializer,
    RoomWriteSerializer,
    RoomUpgradeSerializer,
    RoomVersionSerializer,
)
from studio.serializers.room_data_change import RoomDataChangeSerializer


class RoomQuerySet(list):
    def __init__(self, *args, model, **kwargs):
        self.model = model
        super().__init__(*args, **kwargs)

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self


class RoomViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.ReadOnlyModelViewSet
):
    pagination_class = LargeResultsSetPagination

    def perform_create(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.destroy()

    def get_serializer_class(self):
        if self.action == 'create':
            return RoomWriteSerializer
        return RoomReadSerializer

    def get_queryset(self):
        if 'pk' in self.kwargs:
            room_id = int(self.kwargs['pk'])
            return Room.objects.filter(pk=room_id)

        room_with_latest_valid = [
            x for x in Room.objects.all() if x.latest_valid_room_data is not None
        ]
        return RoomQuerySet(room_with_latest_valid, model=Room)

    @action(detail=True, methods=['post'])
    def upgrade(self, request, pk):
        room = Room.objects.get(pk=pk)
        room.upgrade()
        serializer = RoomUpgradeSerializer(instance=room)
        return Response(serializer.data)


class RoomVersionViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        room_id = int(self.kwargs['room_id'])
        return RoomData.objects.filter(room_id=room_id)

    def get_serializer_class(self):
        return RoomVersionSerializer

    def retrieve(self, request, *args, **kwargs):
        version_id = int(kwargs['pk'])
        room_data = self.get_queryset().get(version=version_id)
        serializer = RoomVersionSerializer(room_data)
        return Response(serializer.data)


class RoomVersionChangesViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        room_id = int(self.kwargs['room_id'])
        version_id = int(self.kwargs['version_id'])
        room_data = RoomData.objects.filter(room_id=room_id, version=version_id).first()
        return RoomDataChange.objects.filter(room_data_id=room_data.id)

    def get_serializer_class(self):
        return RoomDataChangeSerializer
