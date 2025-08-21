from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from rest_framework import (
    mixins,
    status,
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
    RoomWriteResponseSerializer,
    RoomUpgradeSerializer,
    RoomVersionSerializer,
)
from studio.serializers.room_data_change import RoomDataChangeSerializer


@extend_schema_view(
    list=extend_schema(
        description="Returns all rooms with their latest versions.",
        responses=RoomReadSerializer,
    ),
    create=extend_schema(
        description="Creates and returns a new room.",
        responses=RoomWriteResponseSerializer,
    ),
    retrieve=extend_schema(
        description="Returns a room with its latest version.",
        responses=RoomReadSerializer,
    ),
    destroy=extend_schema(
        description="Removes a room and all its versions.",
    ),
)
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

        return Room.objects.by_latest_valid()

    @extend_schema(
        description="Creates and returns a new room version.",
        request=None,
        responses=RoomWriteResponseSerializer,
    )
    @action(detail=True, methods=['post'])
    def upgrade(self, request, pk):
        room = Room.objects.get(pk=pk)
        room.upgrade()
        serializer = RoomUpgradeSerializer(instance=room)
        return Response(serializer.data)

    # For TESTING - APIgateway for updating + upgrading versions with new data
    @extend_schema(
        description="Create a new version of the room with updated data",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'data': {
                        'type': 'object',
                        'description': 'The room data including stretch lines, outline, elements, and properties',
                        'properties': {
                            'room_name': {
                                'type': 'string',
                                'description': 'Name of the room (e.g., "Conference Room A")',
                            },
                            'room_type': {
                                'type': 'string',
                                'description': 'Type of room (e.g., "conference", "office", "bathroom")',
                            },
                            'floor_number': {
                                'type': 'integer',
                                'description': 'Floor number where the room is located',
                            },
                            'area_sqm': {
                                'type': 'number',
                                'description': 'Room area in square meters',
                            },
                            'ceiling_height': {
                                'type': 'number',
                                'description': 'Ceiling height in meters',
                            },
                            'stretch_lines': {
                                'type': 'array',
                                'description': 'Room structural lines with 3D coordinates',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'max': {'type': 'number'},
                                        'firstPoint': {
                                            'type': 'object',
                                            'properties': {
                                                'X': {'type': 'number'},
                                                'Y': {'type': 'number'},
                                                'Z': {'type': 'number'},
                                            },
                                        },
                                        'secondPoint': {
                                            'type': 'object',
                                            'properties': {
                                                'X': {'type': 'number'},
                                                'Y': {'type': 'number'},
                                                'Z': {'type': 'number'},
                                            },
                                        },
                                        'type': {
                                            'type': 'string',
                                            'example': 'ReferenceLine',
                                        },
                                    },
                                },
                            },
                            'Outline': {
                                'type': 'array',
                                'description': 'Room outline points with 3D coordinates',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'X': {'type': 'number'},
                                        'Y': {'type': 'number'},
                                        'Z': {'type': 'number'},
                                    },
                                },
                            },
                            'elements': {
                                'type': 'array',
                                'description': 'Room elements like doors, windows, furniture',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'integer'},
                                        'type': {'type': 'string', 'example': 'door'},
                                        'position': {
                                            'type': 'object',
                                            'properties': {
                                                'x': {'type': 'number'},
                                                'y': {'type': 'number'},
                                            },
                                        },
                                        'dimensions': {
                                            'type': 'object',
                                            'properties': {
                                                'width': {'type': 'number'},
                                                'height': {'type': 'number'},
                                            },
                                        },
                                    },
                                },
                            },
                            'lighting': {
                                'type': 'object',
                                'description': 'Lighting configuration',
                                'properties': {
                                    'natural_light': {'type': 'boolean'},
                                    'artificial_lights': {'type': 'integer'},
                                    'dimmer_controls': {'type': 'boolean'},
                                },
                            },
                            'ventilation': {
                                'type': 'object',
                                'description': 'Ventilation and HVAC configuration',
                                'properties': {
                                    'air_conditioning': {'type': 'boolean'},
                                    'heating': {'type': 'boolean'},
                                    'air_exchange_rate': {'type': 'number'},
                                },
                            },
                            'technology': {
                                'type': 'object',
                                'description': 'Technology and equipment',
                                'properties': {
                                    'projector': {'type': 'boolean'},
                                    'video_conferencing': {'type': 'boolean'},
                                    'sound_system': {'type': 'boolean'},
                                    'whiteboard': {'type': 'boolean'},
                                },
                            },
                        },
                    },
                    'additional_info': {
                        'type': 'object',
                        'description': 'Additional room metadata and information',
                        'properties': {
                            'building': {
                                'type': 'string',
                                'description': 'Building name',
                            },
                            'wing': {
                                'type': 'string',
                                'description': 'Building wing or section',
                            },
                            'access_level': {
                                'type': 'string',
                                'description': 'Access level or floor designation',
                            },
                            'maintenance_contact': {
                                'type': 'string',
                                'description': 'Contact for maintenance issues',
                            },
                            'capacity': {
                                'type': 'integer',
                                'description': 'Room capacity (number of people)',
                            },
                            'booking_system': {
                                'type': 'string',
                                'description': 'Room booking system used',
                            },
                            'last_renovation': {
                                'type': 'string',
                                'format': 'date',
                                'description': 'Date of last renovation',
                            },
                        },
                    },
                },
                'required': ['data'],
            }
        },
        responses=RoomWriteResponseSerializer,
    )
    @action(detail=True, methods=['post'])
    def upgrade_with_data(self, request, pk):
        """
        Create a new version of the room and add the provided data.
        This will increment the version number and create a new RoomData record.
        """
        room = Room.objects.get(pk=pk)

        # Get the new data from request
        new_data = request.data.get('data', {})
        additional_info = request.data.get('additional_info', {})

        # Create a new version using the proper method
        room.upgrade()

        # Get the new version that was just created
        new_version = room.latest_room_data

        # Combine the data
        combined_data = {**new_data, **additional_info}

        # Update the new version with the combined data
        new_version.data = combined_data
        new_version.save(is_updating=True)

        # Generate change records by comparing with previous version
        from studio.models.room_data_change import RoomDataChange

        previous_version = room.previous_room_data

        RoomDataChange.objects.create_from_data_comparison(previous_version, new_version)

        serializer = RoomUpgradeSerializer(instance=room)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        description="Returns all versions of a room.",
        responses=RoomVersionSerializer,
    ),
    create=extend_schema(
        exclude=True,
    ),
    retrieve=extend_schema(
        description="Returns a specific version of a room.",
        responses=RoomVersionSerializer,
    ),
    destroy=extend_schema(
        description="Removes a specific version of a room.",
    ),
)
class RoomVersionViewSet(mixins.DestroyModelMixin, viewsets.ReadOnlyModelViewSet):
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

    def destroy(self, request, *args, **kwargs):
        version_id = int(kwargs['pk'])
        room_data = self.get_queryset().get(version=version_id)
        room_data.destroy()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(
        description="Returns all changes related to a specific version of a room.",
        responses=RoomDataChangeSerializer,
    ),
    create=extend_schema(
        exclude=True,
    ),
    retrieve=extend_schema(
        exclude=True,
    ),
    destroy=extend_schema(
        exclude=True,
    ),
)
class RoomVersionChangesViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        room_id = int(self.kwargs['room_id'])
        version_id = int(self.kwargs['version_id'])
        room_data = RoomData.objects.filter(room_id=room_id, version=version_id).first()
        return RoomDataChange.objects.filter(room_data_id=room_data.id)

    def get_serializer_class(self):
        return RoomDataChangeSerializer
