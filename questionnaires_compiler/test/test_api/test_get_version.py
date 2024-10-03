import json

from django.test import TestCase, Client

from django_core.versioninfo import VERSION


class TestGetApplicationVersion(TestCase):

    def setUp(self) -> None:
        self.client = Client()

        self.path_to_call = "/version"
        self.expected_response = {"version": VERSION, "commit": None}

    def test_get_version(self):
        response = self.client.get(path=self.path_to_call)
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.expected_response, json.loads(response.content))
