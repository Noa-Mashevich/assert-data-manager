from django.http import HttpResponse
from http import HTTPStatus
from rest_framework import (
    mixins,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from studio.models import Validator
from studio.serializers import ValidatorResponseSerializer


class ValidatorViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    @action(detail=False, methods=['post'])
    def validate(self, request):
        try:
            validator = Validator(data=request.data)
            validator.validate()
            serializer = ValidatorResponseSerializer(instance=validator)
            return Response(serializer.data)
        except Exception as e:
            return HttpResponse(f'{e}', status=HTTPStatus.BAD_REQUEST)
