class StandardResultsSetPagination(PageNumberPagination):
    page_size             = 20
    page_size_query_param = "page_size"
    max_page_size         = 100

class CursorResultsSetPagination(CursorPagination):
    page_size   = 20
    ordering    = "-created_at"   # Use for time-series lists (invoices, audit logs)