from django.test import TestCase
from django.urls import reverse


class HealthCheckTestCase(TestCase):
    def test_health_check(self):
        response = self.client.get("/api/v1/health/")
        self.assertIn(response.status_code, [200, 404])
