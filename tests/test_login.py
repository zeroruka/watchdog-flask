import json

from tests.BaseCase import BaseCase


class LoginTest(BaseCase):
    def test_successful_login(self):
        username = "test"
        password = "test"
        payload = json.dumps({
            "username": username,
            "password": password
        })
        self.app.post('/api/register/', data=payload, content_type='application/json')
        response = self.app.post('/api/login/', data=payload, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(str, type(response.json['token']))

    def test_unsuccessful_login(self):
        username = "test"
        password = "test"
        payload = {
            "username": username,
            "password": password
        }
        self.app.post('/api/register/', data=json.dumps(payload), content_type='application/json')
        payload['password'] = "wrongpassword"
        response = self.app.post('/api/login/', data=json.dumps(payload), content_type='application/json')

        self.assertEqual(response.status_code, 401)

