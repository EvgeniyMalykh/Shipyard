from rest_framework.filters import OrderingFilter, SearchFilter


class ShipyardSearchFilter(SearchFilter):
    search_param = "q"


class ShipyardOrderingFilter(OrderingFilter):
    ordering_param = "sort"
