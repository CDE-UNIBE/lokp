import unittest
import pytest
from webtest import TestApp
from pyramid.paster import get_appsettings

from lmkp import main
from lmkp.tests.unit_tests.base import *
from lmkp.tests.unit_tests.activities import *


@pytest.mark.usefixtures("db_session")
class ActivityCreateTests(unittest.TestCase):
    def setUp(self):
        settings = get_appsettings(CONFIG_FILE)
        app = main({}, settings=settings)
        self.testapp = TestApp(app)
        
    def test_activity_cannot_be_created_without_login(self):
        """
        New Activities cannot be created if the user is not logged in.
        """
        res = createActivity(self, {})
        
        self.assertEqual(res.status_int, 200)
        self.assertIn(b'Please login', res.body)
        
    def test_activity_can_be_created(self):
        """
        New Activities can be created if the user is logged in.
        """
        doLogin(self)
        res = createActivity(self, getActivityDiff())
        self.assertEqual(res.status_int, 201)
        json = res.json
        self.assertEqual(json['total'], 1)
        self.assertTrue(json['created'])
        self.assertEqual(len(json['data']), 1)
        self.assertIn('id', json['data'][0])

    def test_new_activities_appear_in_read_many_json_service(self):
        """
        Newly created Activities appear in the JSON service "read many".
        """
        doLogin(self)
        
        json = getReadManyActivities(self, 'json')
        self.assertEqual(json['data'], [])
        self.assertEqual(json['total'], 0)
        
        createActivity(self, getActivityDiff())
        
        json = getReadManyActivities(self, 'json')
        self.assertEqual(json['total'], 1)
    
    