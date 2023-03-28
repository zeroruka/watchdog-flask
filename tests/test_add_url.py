import json

from tests.BaseCase import BaseCase

urls = [{"url": "https://www.ebay.com.sg/sch/i.html?_from=R40&_nkw=malaya+notes&_sacat=0&_sop=10&_ipg=120",
         "name": "Malaya Notes"},
        {"url": "https://www.ebay.com.sg/sch/i.html?_from=R40&_nkw=singapore+notes&_sacat=0&_sop=10&_ipg=120",
         "name": "SG notes"},
        {"url": "https://www.ebay.com.sg/sch/i.html?_from=R40&_nkw=viet+notes&_sacat=0&_sop=10&_ipg=120",
         "name": "viet notes"}]


class TestAddUrl(BaseCase):
    def test_add_url(self):
        username = "test"
        password = "test"
        user_payload = json.dumps({
            "username": username,
            "password": password
        })
        self.app.post('/api/register/', data=user_payload, content_type='application/json')
        response = self.app.post('/api/login/', data=user_payload, content_type='application/json')
        login_token = response.json['token']

        for url in urls:
            url_payload = json.dumps(url)
            response = self.app.put("/api/scraper/",
                                    data=url_payload,
                                    headers={"Content-Type": "application/json",
                                             "Authorization": f"Bearer {login_token}"})
            self.assertEqual(response.status_code, 201)
