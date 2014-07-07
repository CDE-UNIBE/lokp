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
        
    def test_login_page_is_available(self):
        """
        The Login page is available.
        """
        res = self.testapp.get('/login')
        self.assertEqual(res.status_int, 200)
        self.assertIn(b'Login', res.body)
    
    def test_login_form_cannot_be_submitted_empty(self):
        """
        The Login form cannot be submitted with empty values.
        """
        res = self.testapp.get('/login')
        form = res.form
        form['login'] = ''
        form['password'] = ''
        res = form.submit('form.submitted')
        
        self.assertEqual(res.status_int, 200)
        self.assertIn(b'Login', res.body)
        self.assertIn(b'Login failed', res.body)
        
    def test_login_form_submit(self):
        """
        The Login form can be submitted with correct credentials.
        """
        res = self.testapp.get('/map')
        self.assertIn(b'Login', res.body)
        
        res = self.testapp.get('/login')
        form = res.form
        
        form['login'] = USERNAME
        form['password'] = PASSWORD
        res = form.submit('form.submitted')
        
        self.assertEqual(res.status_int, 302)
        
        res = res.follow()
        
        self.assertEqual(res.status_int, 200)
        self.assertIn(b'Land Observatory', res.body)
        
        self.assertNotIn(b'Login', res.body)
        self.assertIn('admin', res.body)
    