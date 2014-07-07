import unittest
import pytest
from webtest import TestApp
from pyramid.paster import get_appsettings

from lmkp import main
from lmkp.tests.unit_tests.base import *


@pytest.mark.usefixtures("db_session")
class MapTests(unittest.TestCase):
    def setUp(self):
        settings = get_appsettings(CONFIG_FILE)
        app = main({}, settings=settings)
        self.testapp = TestApp(app)
        
    def test_map_page_is_available(self):
        """
        The Map page is available.
        """
        res = self.testapp.get('/map')
        self.assertEqual(res.status_int, 200)
        self.assertIn(b'Land Observatory', res.body)
    
    def test_map_page_login_link_is_available(self):
        """
        The Map page shows a login link.
        """
        res = self.testapp.get('/map')
        self.assertIn(b'Login', res.body)