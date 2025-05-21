from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.request import Request
from rest_framework.response import Response


@extend_schema(
    exclude=True,
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def health(request: Request) -> Response:
    return Response(
        {
            "status": "ok",
            "timestamp": timezone.now(),
        }
    )
