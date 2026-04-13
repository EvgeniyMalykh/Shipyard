# drf-spectacular configuration
SPECTACULAR_SETTINGS = {
    "TITLE":       "Shipyard API",
    "DESCRIPTION": "SaaS Boilerplate API",
    "VERSION":     "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX":   "/api/v1/",
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
    },
}