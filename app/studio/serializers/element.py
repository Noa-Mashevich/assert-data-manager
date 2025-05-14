from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from studio.models.element import (
    Element,
    ElementCategory,
)
from studio.serializers.element_data import (
    ElementDataReadSerializer,
    ElementDataWriteSerializer,
)


class ElementWriteSerializer(ModelSerializer):
    class Meta:
        model = Element
        fields = [
            'name',
            'category',
        ]

    def validate(self, data):
        name = data.get('name')
        if name is None or len(name) <= 0:
            raise serializers.ValidationError('Name is not valid')

        category = data.get('category')
        if category is None or category not in set(ElementCategory):
            raise serializers.ValidationError('Category is not valid')

        return data

    def to_representation(self, data):
        return ElementWriteResponseSerializer(context=self.context).to_representation(
            data
        )


class ElementWriteResponseSerializer(ModelSerializer):
    element_data = ElementDataWriteSerializer(source='latest_element_data')

    class Meta:
        model = Element
        fields = [
            'id',
            'name',
            'category',
            'element_data',
        ]


class ElementReadSerializer(ModelSerializer):
    element_data = ElementDataReadSerializer(source='latest_valid_element_data')

    class Meta:
        model = Element
        fields = [
            'id',
            'name',
            'category',
            'element_data',
        ]


class ElementUpgradeSerializer(ModelSerializer):
    class Meta:
        model = Element
        fields = []

    def to_representation(self, data):
        return ElementWriteResponseSerializer(context=self.context).to_representation(
            data
        )


class ElementVersionsReadSerializer(ModelSerializer):
    versions = ElementDataReadSerializer(many=True, read_only=True)

    class Meta:
        model = Element
        fields = [
            'id',
            'name',
            'category',
            'versions',
        ]


class ElementVersionReadSerializer(ModelSerializer):
    id = serializers.IntegerField(source='element_id')
    name = serializers.CharField(source='element.name')
    category = serializers.IntegerField(source='element.category')
    element_data = ElementDataReadSerializer(source='*')

    class Meta:
        model = Element
        fields = [
            'id',
            'name',
            'category',
            'element_data',
        ]
