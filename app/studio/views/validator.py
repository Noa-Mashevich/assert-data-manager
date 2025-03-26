from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from studio.models import Validator
from studio.serializers import ValidatorResponseSerializer


class ValidatorViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    @action(detail=True, methods=['post'])
    def validate(self, request):
        validator = Validator(data=request.data)
        validator.validate()
        serializer = ValidatorResponseSerializer(instance=validator)
        return Response(serializer.data)
