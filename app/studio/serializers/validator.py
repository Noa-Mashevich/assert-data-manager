from rest_framework.serializers import ModelSerializer

from studio.models import Validator


class ValidatorResponseSerializer(ModelSerializer):
    class Meta:
        model = Validator
        fields = ['schema_version', 'validation_message']
