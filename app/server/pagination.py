from rest_framework.pagination import LimitOffsetPagination


class LargeResultsSetPagination(LimitOffsetPagination):
    default_limit = 100
    max_page_size = 1000
