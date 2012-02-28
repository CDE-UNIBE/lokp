import unittest
from pyramid import testing

import transaction
from sqlalchemy.orm.exc import FlushError
from sqlalchemy.exc import IntegrityError

from ..tests import database_setup
#from ..models.database_objects import Activity, A_Event, A_Tag, User, Status

class ActivityTest(unittest.TestCase):
    
    def setUp(self):
        self.session = database_setup._initTestingDB()
        self.config = testing.setUp()
        
    def tearDown(self):
        self.session.remove()
        self.config = testing.tearDown()

    def test_Activity_insert(self):
        self.assertEqual(self.session.query(Activity).count(), 0)
        event1 = A_Event(geometry="Point(10 20)", source="source1")
        event1.activity = Activity()
        event1.user = User(username="user", password="pw", email="me@you.com")
        event1.status = Status(id=10, name="status")
        event1.tags.append(A_Tag(key="tag1", value="value1"))
        self.session.add(event1)
        self.assertEqual(self.session.query(Activity).count(), 1)