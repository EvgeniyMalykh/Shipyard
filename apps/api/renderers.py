from rest_framework.renderers import JSONRenderer


class ShipyardJSONRenderer(JSONRenderer):
    charset = "utf-8"
