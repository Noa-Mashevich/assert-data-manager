from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from studio.models.schema import Schema


class ValidatorViewSet(viewsets.GenericViewSet):
    @action(detail=True, methods=['post'])
    def validate(self, request):
        response_data = {'version': -1, 'success': False, 'error_message': ''}
        status_code = status.HTTP_400_BAD_REQUEST

        if 'version' not in request.data:
            response_data['error_message'] = 'Missing version in JSON data'
            return Response(response_data, status=status_code)

        version = request.data.get('version')
        response_data['version'] = version

        try:
            schema = Schema.objects.create_from_version(version)
            success, error_message = schema.validate(request.data)

            response_data['success'] = success
            response_data['error_message'] = error_message
            if success:
                status_code = status.HTTP_200_OK
        except Exception as e:
            response_data['error_message'] = f'Failed validating JSON data, reason: {e}'

        return Response(response_data, status=status_code)
