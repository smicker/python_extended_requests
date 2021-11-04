#!/usr/bin/python3

# IMPORTANT!! Before running those tests, please get a temporary test url from
# this page http://ptsv2.com/ and modify the TEST_POSTFIX_URL constant below.

# Run those tests from the project folder (the parent folder to this file) with:
# python3 -m unittest discover -s tests -t .

import unittest
from requests.models import HTTPError, ConnectionError
import src.web_caller as wc

TEST_BASE_URL = "http://ptsv2.com/"
TEST_POSTFIX_URL = "/t/8ut6c-1636028392/post"

class TestWebCaller(unittest.TestCase):
    """Test cases for web_caller"""

    def test_simple_get(self):
        webcaller = wc.WebCaller()
        response = webcaller.web_get(TEST_BASE_URL + TEST_POSTFIX_URL)
        self.assertEqual(response.text, "Thank you for this dump. I hope you have a lovely day!",
            "Should be: Thank you for this dump. I hope you have a lovely day!")
        self.assertEqual(response.status_code, 200, "Should be 200")
        webcaller.close()

    def test_simple_post(self):
        webcaller = wc.WebCaller()
        response = webcaller.web_post(TEST_BASE_URL + TEST_POSTFIX_URL)
        self.assertEqual(response.text, "Thank you for this dump. I hope you have a lovely day!",
            "Should be: Thank you for this dump. I hope you have a lovely day!")
        self.assertEqual(response.status_code, 200, "Should be 200")
        webcaller.close()

    def test_base_url_get(self):
        webcaller = wc.WebCaller(base_url=TEST_BASE_URL)
        response = webcaller.web_get(TEST_POSTFIX_URL)
        self.assertEqual(response.text, "Thank you for this dump. I hope you have a lovely day!",
            "Should be: Thank you for this dump. I hope you have a lovely day!")
        self.assertEqual(response.status_code, 200, "Should be 200")
        webcaller.close()

    def test_base_url_post(self):
        webcaller = wc.WebCaller(base_url=TEST_BASE_URL)
        response = webcaller.web_post(TEST_POSTFIX_URL)
        self.assertEqual(response.text, "Thank you for this dump. I hope you have a lovely day!",
            "Should be: Thank you for this dump. I hope you have a lovely day!")
        self.assertEqual(response.status_code, 200, "Should be 200")
        webcaller.close()

    def test_throw_on_problem_get_exception(self):
        webcaller = wc.WebCaller()
        with self.assertRaises(HTTPError):
            webcaller.web_get("https://api.github.com/user/repos?page=1")
        webcaller.close()

    def test_throw_on_problem_get_response(self):
        webcaller = wc.WebCaller()
        try:
            webcaller.web_get("https://api.github.com/user/repos?page=1")
        except HTTPError as err:
            self.assertIn("401", str(err), "Should return 401")
        webcaller.close()

    def test_connectionerror_get_exception(self):
        webcaller = wc.WebCaller(retries=0)
        with self.assertRaises(ConnectionError):
            webcaller.web_get("https://www.sunet.com")
        webcaller.close()

    def test_connectionerror_get_response(self):
        webcaller = wc.WebCaller(retries=0)
        try:
            webcaller.web_get("https://www.sunet.com")
        except ConnectionError as err:
            self.assertIn("SSLCertVerificationError", str(err), "Should return 'SSLCertVerificationError'")
        webcaller.close()

    def test_get_with_basic_auth(self):
        webcaller = wc.WebCaller(base_url=TEST_BASE_URL)
        webcaller.set_basic_auth("Kalle", "LOPPAN")
        self.assertEqual(webcaller.auth.username, "Kalle", "Should be 'Kalle'")
        self.assertEqual(webcaller.auth.password, "LOPPAN", "Should be 'LOPPAN'")

        response = webcaller.web_get(TEST_POSTFIX_URL)
        self.assertEqual(response.text, "Thank you for this dump. I hope you have a lovely day!",
            "Should be: Thank you for this dump. I hope you have a lovely day!")
        self.assertEqual(response.status_code, 200, "Should be 200")
        webcaller.close()

    def test_default_retries(self):
        webcaller = wc.WebCaller()
        adapter = webcaller.web.get_adapter("http://")
        self.assertEqual(adapter.max_retries.total, wc.DEFAULT_MAX_RETRIES, f"Should be {wc.DEFAULT_MAX_RETRIES}")
        webcaller.close()

    def test_custom_retries(self):
        webcaller = wc.WebCaller(retries=10)
        adapter = webcaller.web.get_adapter("http://")
        self.assertEqual(adapter.max_retries.total, 10, "Should be 10")
        webcaller.close()

    def test_none_retries(self):
        webcaller = wc.WebCaller(retries=0)
        adapter = webcaller.web.get_adapter("http://")
        self.assertEqual(adapter.max_retries.total, 0, "Should be 0")
        webcaller.close()

    def test_negative_retries(self):
        webcaller = wc.WebCaller(retries=-5)
        adapter = webcaller.web.get_adapter("http://")
        self.assertEqual(adapter.max_retries.total, 0, "Should be 0")
        webcaller.close()

    def test_retry_strategy(self):
        webcaller = wc.WebCaller()
        adapter = webcaller.web.get_adapter("http://")
        self.assertEqual(adapter.max_retries.status_forcelist,
            [429, 500, 502, 503, 504], "Should be [429, 500, 502, 503, 504]")
        self.assertEqual(adapter.max_retries.allowed_methods,
            ['HEAD', 'GET', 'PUT', 'DELETE', 'OPTIONS', 'TRACE', 'POST'], "Should be ['HEAD', 'GET', 'PUT', 'DELETE', 'OPTIONS', 'TRACE', 'POST']")
        self.assertEqual(adapter.max_retries.backoff_factor, wc.DEFAULT_BACKOFF_FACTOR, f"Should be {wc.DEFAULT_BACKOFF_FACTOR}")
        webcaller.close()

    def test_default_timeout(self):
        webcaller = wc.WebCaller()
        adapter = webcaller.web.get_adapter("http://")
        self.assertEqual(adapter.timeout, wc.DEFAULT_TIMEOUT, f"Should be {wc.DEFAULT_TIMEOUT}")
        webcaller.close()

    def test_custom_timeout(self):
        webcaller = wc.WebCaller(timeout=10)
        adapter = webcaller.web.get_adapter("http://")
        self.assertEqual(adapter.timeout, 10, "Should be 10")
        webcaller.close()

    def test_none_timeout(self):
        webcaller = wc.WebCaller(timeout=None)
        adapter = webcaller.web.get_adapter("http://")
        self.assertEqual(adapter.timeout, None, "Should be None")
        webcaller.close()

    def test_post_with_data(self):
        webcaller = wc.WebCaller()

        data: dict = {
            "Name": "Charlie",
            "Profession": "Programming"
        }

        response = webcaller.web_post(TEST_BASE_URL + TEST_POSTFIX_URL, data=data)
        self.assertEqual(response.text, "Thank you for this dump. I hope you have a lovely day!",
            "Should be: Thank you for this dump. I hope you have a lovely day!")
        self.assertEqual(response.status_code, 200, "Should be 200")
        webcaller.close()

    def test_post_with_json(self):
        webcaller = wc.WebCaller()

        data: dict = {
            "Name": "Charlie",
            "Profession": "Programming"
        }

        response = webcaller.web_post(TEST_BASE_URL + TEST_POSTFIX_URL, json=data)
        self.assertEqual(response.text, "Thank you for this dump. I hope you have a lovely day!",
            "Should be: Thank you for this dump. I hope you have a lovely day!")
        self.assertEqual(response.status_code, 200, "Should be 200")
        webcaller.close()

    def test_header(self):
        webcaller = wc.WebCaller()

        headers: dict = {
            "My-Header": "MyData"
        }

        response = webcaller.web_post(TEST_BASE_URL + TEST_POSTFIX_URL, headers=headers)
        self.assertEqual(response.text, "Thank you for this dump. I hope you have a lovely day!",
            "Should be: Thank you for this dump. I hope you have a lovely day!")
        self.assertEqual(response.status_code, 200, "Should be 200")
        webcaller.close()

if __name__ == '__main__':
    unittest.main()
