import unittest
from selenium import webdriver
from lmkp.tests.functional_tests import *


class LoginTests(unittest.TestCase):
    
    def setUp(self):
        self.driver = webdriver.Firefox()

    def tearDown(self):
        self.driver.quit()


    def test_login(self):
        """
        Tests the login
        """
        
        # Make sure the user is not logged in. On Map View, the login link
        # should appear but no username.
        self.driver.get(createUrl('/map'))
        self.assertIn(MAP_VIEW_TITLE, self.driver.title)
        self.assertFalse(checkElExists(self.driver, 'link_text', USERNAME_BUTTON))
        self.assertTrue(checkElExists(self.driver, 'link_text', LOGIN_BUTTON))
        
        # Login
        self.driver.get(createUrl('/login'))
        loginfield = self.driver.find_element_by_name('login')
        loginfield.send_keys(USERNAME)
        passwordfield = self.driver.find_element_by_name('password')
        passwordfield.send_keys(PASSWORD)
        btn = self.driver.find_element_by_name('form.submitted')
        btn.click()
        
        # Check that the user is now logged in. We should be back on the Map
        # View, with the username showing instead of the login link.
        self.assertIn(MAP_VIEW_TITLE, self.driver.title)
        self.assertTrue(checkElExists(self.driver, 'link_text', USERNAME_BUTTON))
        self.assertFalse(checkElExists(self.driver, 'link_text', LOGIN_BUTTON))
    