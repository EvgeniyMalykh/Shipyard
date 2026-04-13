class HealthCheckView(APIView):
    """
    GET /health/
    Returns 200 always — suitable for load balancer liveness probe.
    {"status": "ok"}
    """
    permission_classes = [AllowAny]
    authentication_classes = []


class ReadinessView(APIView):
    """
    GET /ready/
    Checks DB and Redis connectivity.
    Returns 200 if all dependencies are reachable, 503 otherwise.
    {"status": "ok"|"degraded", "checks": {"db": "ok", "redis": "ok"}}
    """
    permission_classes = [AllowAny]
    authentication_classes = []