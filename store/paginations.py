from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination


class CustomPagePagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'p'
    page_size_query_params = 'data'
    max_page_size = 30
    last_page_strings = ('last', 'end')


class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = 'l'
    offset_query_param = 'o'
    max_limit = "30"