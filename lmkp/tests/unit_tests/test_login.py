import unittest
from webtest import TestApp
from pyramid.paster import get_appsettings
from lmkp import main


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        config_uri = 'test.ini'
        settings = get_appsettings(config_uri)
        app = main({}, settings=settings)
        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertIn(b'Land Observatory', res.body)

    def test_login_page_is_available(self):
        res = self.testapp.get('/login')
        self.assertEqual(res.status_int, 200)
        self.assertIn(b'Login', res.body)

