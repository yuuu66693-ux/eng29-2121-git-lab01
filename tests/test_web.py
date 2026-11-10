import unittest

from app import app


class TestWebApp(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_get_index_returns_200_and_form(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn("<form", html)
        self.assertIn('name="vcc"', html)
        self.assertIn('name="r1"', html)
        self.assertIn('name="r2"', html)
        self.assertIn('name="rc"', html)
        self.assertIn('name="re"', html)
        self.assertIn('name="beta"', html)
        self.assertIn('name="vbe"', html)
        self.assertIn('action="/calculate"', html)

    def test_post_calculate_reference_case_shows_results(self):
        data = {
            "vcc": "12",
            "r1": "100000",
            "r2": "22000",
            "rc": "2200",
            "re": "1000",
            "beta": "100",
            "vbe": "0.7",
        }
        resp = self.client.post("/calculate", data=data)
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        # key numeric results (allow formatting differences)
        self.assertIn("1.942", html)
        self.assertIn("8.052", html)
        self.assertTrue(("1.230" in html) or ("1.229" in html) or ("0.00123" in html))
        self.assertRegex(html.lower(), r"active")

    def test_post_invalid_input_shows_error_no_crash(self):
        data = {
            "vcc": "12",
            "r1": "0",
            "r2": "22000",
            "rc": "2200",
            "re": "1000",
            "beta": "100",
            "vbe": "0.7",
        }
        resp = self.client.post("/calculate", data=data)
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True).lower()
        self.assertTrue("error" in html or "invalid" in html or "must" in html or "greater" in html)


if __name__ == "__main__":
    unittest.main()
