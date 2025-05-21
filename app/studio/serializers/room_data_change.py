from rest_framework.serializers import ModelSerializer

from studio.models.room_data_change import RoomDataChange


class RoomDataChangeSerializer(ModelSerializer):
    class Meta:
        model = RoomDataChange
        fields = [
            'type',
            'description',
        ]
