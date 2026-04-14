from rest_framework.versioning import URLPathVersioning


class ShipyardVersioning(URLPathVersioning):
    allowed_versions = ["v1"]
    default_version = "v1"
    version_param = "version"
