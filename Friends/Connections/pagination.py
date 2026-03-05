from rest_framework.pagination import PageNumberPagination

# I know It is stupid that i am repeting the code but i am planing on changing ech of them as all dont require page_size to be 10 they might be more or less
class PendingRequestPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

class ListFriendsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

class IsPendingRequestPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50