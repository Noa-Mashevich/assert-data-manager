from rest_framework.serializers import ModelSerializer

from studio.models.element_data_change import ElementDataChange


class ElementDataChangeSerializer(ModelSerializer):
    class Meta:
        model = ElementDataChange
        fields = [
            'type',
            'description',
        ]
