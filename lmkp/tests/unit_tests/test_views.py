import unittest
import pytest
from webtest import TestApp
from pyramid.paster import get_appsettings

from lmkp import main
from lmkp.tests.unit_tests.base import *


@pytest.mark.usefixtures("db_session")
class LoginTests(unittest.TestCase):
    def setUp(self):
        settings = get_appsettings(CONFIG_FILE)
        app = main({}, settings=settings)
        self.testapp = TestApp(app)
        
    def test_root(self):
        """
        The root page (/) is available.
        """
        res = self.testapp.get('/')
        self.assertEqual(res.status_int, 200)
        self.assertIn(b'Land Observatory', res.body)