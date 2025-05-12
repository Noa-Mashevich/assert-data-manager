from rest_framework.serializers import ModelSerializer

from studio.models.element import Element
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
