from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from rest_framework import (
    mixins,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from server.pagination import LargeResultsSetPagination

from studio.models.element import Element
from studio.models.element_data import ElementData
from studio.models.element_data_change import ElementDataChange
from studio.serializers.element import (
    ElementReadSerializer,
    ElementWriteSerializer,
    ElementWriteResponseSerializer,
    ElementUpgradeSerializer,
    ElementVersionReadSerializer,
)
from studio.serializers.element_data_change import ElementDataChangeSerializer


class ElementQuerySet(list):
    def __init__(self, *args, model, **kwargs):
        self.model = model
        super().__init__(*args, **kwargs)

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self


@extend_schema_view(
    list=extend_schema(
        description="Returns all elements with their latest versions.",
        responses=ElementReadSerializer,
    ),
    create=extend_schema(
        description="Creates and returns a new element.",
        responses=ElementWriteResponseSerializer,
    ),
    retrieve=extend_schema(
        description="Returns an element with its latest version.",
        responses=ElementReadSerializer,
    ),
    destroy=extend_schema(
        description="Removes an element and all its versions.",
    ),
)
class ElementViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.ReadOnlyModelViewSet
):
    pagination_class = LargeResultsSetPagination

    def perform_create(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.destroy()

    def get_serializer_class(self):
        if self.action == 'create':
            return ElementWriteSerializer
        return ElementReadSerializer

    def get_queryset(self):
        if 'pk' in self.kwargs:
            element_id = int(self.kwargs['pk'])
            return Element.objects.filter(pk=element_id)

        element_with_latest_valid = [
            x for x in Element.objects.all() if x.latest_valid_element_data is not None
        ]
        return ElementQuerySet(element_with_latest_valid, model=Element)

    @extend_schema(
        description="Creates and returns a new element version.",
        request=None,
        responses=ElementWriteResponseSerializer,
    )
    @action(detail=True, methods=['post'])
    def upgrade(self, request, pk):
        element = Element.objects.get(pk=pk)
        element.upgrade()
        serializer = ElementUpgradeSerializer(instance=element)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        description="Returns all versions of an element.",
        responses=ElementVersionReadSerializer,
    ),
    create=extend_schema(
        exclude=True,
    ),
    retrieve=extend_schema(
        description="Returns a specific version of an element.",
        responses=ElementVersionReadSerializer,
    ),
    destroy=extend_schema(
        description="Removes a specific version of an element.",
    ),
)
class ElementVersionViewSet(mixins.DestroyModelMixin, viewsets.ReadOnlyModelViewSet):
    def get_serializer_class(self):
        return ElementVersionReadSerializer

    def get_queryset(self):
        element_id = int(self.kwargs['element_id'])
        return ElementData.objects.filter(element_id=element_id)

    def retrieve(self, request, *args, **kwargs):
        version_id = int(kwargs['pk'])
        element_data = self.get_queryset().get(version=version_id)
        serializer = ElementVersionReadSerializer(element_data)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        version_id = int(kwargs['pk'])
        element_data = self.get_queryset().get(version=version_id)
        element_data.destroy()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(
        description="Returns all changes related to a specific version of an element.",
        responses=ElementDataChangeSerializer,
    ),
    create=extend_schema(
        exclude=True,
    ),
    retrieve=extend_schema(
        exclude=True,
    ),
    destroy=extend_schema(
        exclude=True,
    ),
)
class ElementVersionChangesViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        element_id = int(self.kwargs['element_id'])
        version_id = int(self.kwargs['version_id'])
        element_data = ElementData.objects.filter(
            element_id=element_id, version=version_id
        ).first()
        return ElementDataChange.objects.filter(element_data_id=element_data.id)

    def get_serializer_class(self):
        return ElementDataChangeSerializer
