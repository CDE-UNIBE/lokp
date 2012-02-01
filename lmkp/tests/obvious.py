import unittest
from pyramid import testing

class Obvious(unittest.TestCase):

    def setUp(self):
        request = testing.DummyRequest()
        self.string_a = "String A"
        self.string_b = "String B"
        self.string_a_copy = self.string_a
        self.none = None
        self.array_a = [1, 3, 4]
        self.number_a = 1
        self.number_b = 2
        self.config = testing.setUp(request=request)
    
    def tearDown(self):
        testing.tearDown()
        
    def test_theObvious(self):
        self.assertEqual(True, True)
        self.assertNotEqual(False, True)
        self.assertTrue(True)
        self.assertFalse(False)
        self.assertIs(self.string_a, self.string_a_copy)
        self.assertIsNot(self.string_a, self.string_b)
        self.assertIsNone(self.none)
        self.assertIn(self.number_a, self.array_a)
        self.assertNotIn(self.number_b, self.array_a)
        from types import IntType
        self.assertIsInstance(self.number_a, IntType)
        from types import StringType
        self.assertNotIsInstance(self.number_b, StringType)
    
    @unittest.expectedFailure
    def test_theObvious_fail(self):
        self.assertEqual(1, 0)