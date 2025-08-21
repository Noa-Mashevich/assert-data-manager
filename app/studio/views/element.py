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

from django.core.exceptions import ObjectDoesNotExist
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

        return Element.objects.by_latest_valid()

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

    # for testing
    @extend_schema(
        description="Update element data with custom values - SIMPLE, NO VERSIONING!",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'data': {
                        'type': 'object',
                        'description': 'The new data to set for the element',
                    }
                },
            }
        },
        responses=ElementWriteResponseSerializer,
    )
    @action(detail=True, methods=['post'])
    def update_data(self, request, pk):
        """
        Simple endpoint to update element data - NO VERSIONING, NO DUPLICATES!
        Just updates the current version's data.
        """
        element = Element.objects.get(pk=pk)

        # Get the new data from request
        new_data = request.data.get('data', {})

        # Get current data
        current_data = element.latest_element_data

        # Save old data for comparison
        old_data = current_data.data.copy()

        # Update the data
        current_data.data = new_data
        current_data.save()

        # Generate change records
        from studio.models.element_data_change import ElementDataChange

        ElementDataChange.objects.create_from_data_comparison(
            None, current_data  # No previous version since we're updating same version
        )

        serializer = ElementUpgradeSerializer(instance=element)
        return Response(serializer.data)

    # For TESTING - APIgateway for updating + upgrading versions with new data
    @extend_schema(
        description="Create a new version of the element with updated data",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'data': {
                        'type': 'object',
                        'description': 'The new data to add to the new version',
                    },
                    'additional_info': {
                        'type': 'object',
                        'description': 'Additional information to include in the new version',
                    },
                },
            }
        },
        responses=ElementWriteResponseSerializer,
    )
    @action(detail=True, methods=['post'])
    def upgrade_with_data(self, request, pk):
        """
        Create a new version of the element and add the provided data.
        This will increment the version number and create a new ElementData record.
        """
        try:
            element = Element.objects.get(pk=pk)

            # Get the new data from request
            new_data = request.data.get('data', {})
            additional_info = request.data.get('additional_info', {})

            # Create a new version using the proper method
            element.upgrade()

            # Get the new version that was just created
            new_version = element.latest_element_data

            # Combine the data
            combined_data = {**new_data, **additional_info}

            # Update the new version with the combined data
            new_version.data = combined_data
            new_version.save(is_updating=True)

            # Generate change records by comparing with previous version
            from studio.models.element_data_change import ElementDataChange

            previous_version = element.previous_element_data

            # Only create change records if there's a previous version to compare with
            if previous_version is not None:
                ElementDataChange.objects.create_from_data_comparison(
                    previous_version, new_version
                )

            serializer = ElementUpgradeSerializer(instance=element)
            return Response(serializer.data)

        except ObjectDoesNotExist:
            return Response(
                {"error": f"Element with ID {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to upgrade element: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
