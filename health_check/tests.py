import unittest

import requests


class HealthCheckTestCase(unittest.TestCase):
    def test_health_check_endpoint(self):
        url = 'http://0.0.0.0:8000/'
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        expected_data = {
            "status_code": 200,
            "detail": "ok",
            "result": "working",
        }
        self.assertEqual(response.json(), expected_data)
