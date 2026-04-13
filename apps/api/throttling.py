class BurstRateThrottle(UserRateThrottle):
    scope = "burst"         # 60/min — default for authenticated users

class SustainedRateThrottle(UserRateThrottle):
    scope = "sustained"     # 1000/day

class AnonBurstThrottle(AnonRateThrottle):
    scope = "anon_burst"    # 20/min for unauthenticated

class AuthEndpointThrottle(AnonRateThrottle):
    scope = "auth"          # 10/min — stricter for login/register to deter brute force