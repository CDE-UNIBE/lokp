import unittest
from pyramid import testing

import transaction
from sqlalchemy.orm.exc import FlushError
from sqlalchemy.exc import IntegrityError

from ..tests import database_setup
from ..models.database_objects import Stakeholder_Role

class StakeholderRolesTest(unittest.TestCase):
    
    def setUp(self):
        self.session = database_setup._initTestingDB()
        self.config = testing.setUp()
        
    def tearDown(self):
        self.session.remove()
        self.config = testing.tearDown()
        
    def test_StakeholderRoles_insert(self):
        count = self.session.query(Stakeholder_Role).count()
        self.assertEqual(count, 0)
        s = Stakeholder_Role(id=1, name='test role', description='Just testing. Sample value.')
        self.session.add(s)
        count = self.session.query(Stakeholder_Role).count()
        self.assertNotEqual(count, 0)
        self.assertEqual(count, 1)
        q = self.session.query(Stakeholder_Role).first()
        self.assertEqual(s, q)
        s2 = Stakeholder_Role(id=2, name='no description')
        self.session.add(s2)
        count = self.session.query(Stakeholder_Role).count()
        self.assertEqual(count, 2)
        
    def test_Stakeholder_Role_uniqueId(self):
        # add first role, count should be 1
        s1 = Stakeholder_Role(id=1, name='test role 1', description='Just testing. First sample value.')
        self.session.add(s1)
        # it is not possible to add first role again, count should still be 1
        self.session.add(s1)
        count = self.session.query(Stakeholder_Role).count()
        self.assertEqual(count, 1)
        # try to add second role with same id
        s2 = Stakeholder_Role(id=1, name='test role 2', description='Still testing. Same id but different name.')
        with self.assertRaises(FlushError):
            self.session.add(s2)
            count = self.session.query(Stakeholder_Role).count()
            self.assertEqual(count, 1)

    def test_Stakeholder_Role_uniqueName(self):
        # add first role, count should be 1
        s1 = Stakeholder_Role(id=1, name='test role 1', description='Just testing. First sample value.')
        self.session.add(s1)
        # it is not possible to add first role again, count should still be 1
        self.session.add(s1)
        count = self.session.query(Stakeholder_Role).count()
        self.assertEqual(count, 1)
        # try to add second role with same name
        s2 = Stakeholder_Role(id=2, name='test role 1', description='Still testing. Different id but same name.')
        with self.assertRaises(IntegrityError):
            self.session.add(s2)
            count = self.session.query(Stakeholder_Role).count()
            self.assertEqual(count, 1)