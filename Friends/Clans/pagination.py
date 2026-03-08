from rest_framework.pagination import PageNumberPagination


class UserOwnedClansPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10


class UserJoinedClansPaginaton(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class PopularClanPagination(PageNumberPagination):
    page_size = 10
    page_size_query_description = "page_size"
    max_page_size = 20