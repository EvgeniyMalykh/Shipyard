def shipyard_exception_handler(exc, context):
    """
    Wraps DRF's default handler.
    All error responses follow the shape:
    {
        "error": {
            "code":    "validation_error",
            "message": "Human-readable summary",
            "detail":  { ... field-level errors }
        }
    }
    """