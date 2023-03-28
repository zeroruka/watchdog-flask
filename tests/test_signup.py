import json

from tests.BaseCase import BaseCase


class SignupTest(BaseCase):
    def test_signup(self):
        response = self.app.post('/api/register/', data=json.dumps(dict(
            username='test',
            password='test'
        )), content_type='application/json')
        self.assertEqual(int, type(response.json['id']))
        self.assertEqual(response.status_code, 201)

    def test_duplicate_signup(self):
        username = "test"
        password = "test"
        payload = json.dumps({
            "username": username,
            "password": password
        })
        self.app.post('/api/register/', data=payload, content_type='application/json')
        response = self.app.post('/api/register/', data=payload, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "User already exists")
