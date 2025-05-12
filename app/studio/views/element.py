from rest_framework import mixins, viewsets

from server.pagination import LargeResultsSetPagination

from studio.models.element import Element
from studio.models.element_data_change import ElementDataChange
from studio.serializers.element import (
    ElementReadSerializer,
    ElementWriteSerializer,
    ElementVersionsReadSerializer,
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
            element_id = self.kwargs['pk']
            return Element.objects.filter(pk=element_id)

        element_with_latest_valid = [
            x for x in Element.objects.all() if x.latest_valid_element_data is not None
        ]
        return ElementQuerySet(element_with_latest_valid, model=Element)


class ElementVersionViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        element_id = int(self.kwargs['element_id'])
        return Element.objects.filter(pk=element_id)

    def get_serializer_class(self):
        return ElementVersionsReadSerializer


class ElementVersionChangesViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        # TODO
        return ElementDataChange.objects.all()

    def get_serializer_class(self):
        return ElementDataChangeReadSerializer
