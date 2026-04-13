class RequestIDMiddleware:
    """
    Injects a unique X-Request-ID header into every request and response.
    Used for log correlation and Sentry tracing.
    """

class CurrentTeamMiddleware:
    """
    Reads X-Team-ID header and attaches the resolved Team to request.team.
    Used by permission classes and views to avoid repeated DB lookups.
    """