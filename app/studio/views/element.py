from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from server.pagination import LargeResultsSetPagination

from studio.models.element import Element
from studio.models.element_data import ElementData
from studio.models.element_data_change import ElementDataChange
from studio.serializers.element import (
    ElementReadSerializer,
    ElementWriteSerializer,
    ElementUpgradeSerializer,
    ElementVersionsReadSerializer,
    ElementVersionReadSerializer,
)
from studio.serializers.element_data_change import ElementDataChangeReadSerializer


class ElementQuerySet(list):
    def __init__(self, *args, model, **kwargs):
        self.model = model
        super().__init__(*args, **kwargs)

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self


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

    @action(detail=True, methods=['post'])
    def upgrade(self, request, pk):
        element = Element.objects.get(pk=pk)
        element.upgrade()
        serializer = ElementUpgradeSerializer(instance=element)
        return Response(serializer.data)


class ElementVersionsViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        element_id = int(self.kwargs['element_id'])
        return Element.objects.filter(pk=element_id)

    def get_serializer_class(self):
        return ElementVersionsReadSerializer


class ElementVersionViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        element_id = int(self.kwargs['element_id'])
        return ElementData.objects.filter(element_id=element_id)

    def get_serializer_class(self):
        return ElementVersionReadSerializer


class ElementVersionChangesViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        element_id = int(self.kwargs['element_id'])
        version_id = int(self.kwargs['version_id'])
        element_data = ElementData.objects.filter(
            element_id=element_id, version=version_id
        ).first()
        return ElementDataChange.objects.filter(element_data_id=element_data.id)

    def get_serializer_class(self):
        return ElementDataChangeReadSerializer
