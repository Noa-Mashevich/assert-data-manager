from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from studio.models.room import (
    Room,
    RoomCategory,
)
from studio.serializers.room_data import (
    RoomDataReadSerializer,
    RoomDataWriteSerializer,
)


class RoomWriteSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = [
            'name',
            'category',
            'function',
            'type',
        ]

    def validate(self, data):
        name = data.get('name')
        if name is None or len(name) <= 0:
            raise serializers.ValidationError('Name is not valid')

        category = data.get('category')
        if category is None or category not in set(RoomCategory):
            raise serializers.ValidationError('Category is not valid')

        function = data.get('function')
        if function is None or len(function) <= 0:
            raise serializers.ValidationError('Function is not valid')

        return data

    def to_representation(self, data):
        return RoomWriteResponseSerializer(context=self.context).to_representation(data)


class RoomWriteResponseSerializer(ModelSerializer):
    room_data = RoomDataWriteSerializer(source='latest_room_data')

    class Meta:
        model = Room
        fields = [
            'id',
            'name',
            'category',
            'function',
            'type',
            'room_data',
        ]


class RoomReadSerializer(ModelSerializer):
    room_data = RoomDataWriteSerializer(source='latest_valid_room_data')

    class Meta:
        model = Room
        fields = [
            'id',
            'name',
            'category',
            'function',
            'type',
            'room_data',
        ]


class RoomUpgradeSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = []

    def to_representation(self, data):
        return RoomWriteResponseSerializer(context=self.context).to_representation(data)


class RoomVersionSerializer(ModelSerializer):
    id = serializers.IntegerField(source='room_id')
    name = serializers.CharField(source='room.name')
    category = serializers.IntegerField(source='room.category')
    function = serializers.CharField(source='room.function')
    type = serializers.CharField(source='room.type')
    room_data = RoomDataReadSerializer(source='*')

    class Meta:
        model = Room
        fields = [
            'id',
            'name',
            'category',
            'function',
            'type',
            'room_data',
        ]
