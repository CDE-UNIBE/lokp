import unittest
from selenium import webdriver
from lmkp.tests.functional_tests import *


class ModerationTests(unittest.TestCase):
    
    def setUp(self):
        self.driver = webdriver.Firefox()
    
    def tearDown(self):
        self.driver.quit()
    
    def test_approve_activity(self):
        """
        Test that a new Activity can be approved.
        """
        
        doLogin(self.driver)
        
        uid = doCreateActivity(self.driver)
        link = createUrl('/activities/html/%s' % uid)

        # Check that it is pending and there is a moderation link
        self.driver.get(link)
        self.assertTrue(checkIsPending(self.driver))
        reviewLink = self.driver.find_element_by_xpath("//a[contains(@href, '/activities/review/')]")
        self.assertIn(REVIEW_LINK, reviewLink.text)
        
        self.driver.get(reviewLink.get_attribute('href'))
        self.assertIn(DEAL_MODERATION_TITLE, self.driver.title)
        btn = self.driver.find_element_by_xpath("//button[contains(concat(' ', @class, ' '), ' btn-success ') and contains(text(), '%s')]" % APPROVE_BUTTON)
        btn.click()
        
        self.assertTrue(checkElExists(self.driver, 'class_name', 'alert-success'))
        
        # Make sure the Activity is not pending anymore
        self.driver.get(link)
        self.assertFalse(checkIsPending(self.driver))
    
    def test_approve_activity_with_new_involvement(self):
        """
        Test that a new Activity with a new involvement can be approved.
        """
        
        doLogin(self.driver)
        
        aUid = doCreateActivity(self.driver, createSH=True)
        
        # Check that the Activity cannot be reviewed because of the pending SH
        self.driver.get(createUrl('/activities/review/%s' % aUid))
        self.driver.find_element_by_xpath("//button[contains(concat(' ', @class, ' '), ' disabled ') and contains(text(), '%s')]" % APPROVE_BUTTON)
        self.assertTrue(checkElExists(self.driver, 'class_name', 'alert-missing-mandatory-keys'))
        
        # Make sure the Stakeholder can be reviewed and do this
        self.driver.find_element_by_xpath("//a[contains(@href, '/stakeholders/review/')]").click()
        self.assertIn(STAKEHOLDER_MODERATION_TITLE, self.driver.title)
        self.driver.find_element_by_xpath("//button[contains(concat(' ', @class, ' '), ' btn-success ') and contains(text(), '%s')]" % APPROVE_BUTTON).click()
        
        # Make sure there is a Success message and a notice that the Activity 
        # can now be reviewed.
        self.assertTrue(checkElExists(self.driver, 'class_name', 'alert-success'))
        self.assertIn('You had to review this', self.driver.page_source)
        self.driver.find_element_by_link_text('Click here to return to the Activity and review it.').click()
        
        # Make sure the Activity can now be reviewed.
        self.assertIn(DEAL_MODERATION_TITLE, self.driver.title)
        self.driver.find_element_by_xpath("//button[contains(concat(' ', @class, ' '), ' btn-success ') and contains(text(), '%s')]" % APPROVE_BUTTON).click()
        
        # Make sure the Activity is not pending anymore
        self.driver.get(createUrl('/activities/html/%s' % aUid))
        self.assertFalse(checkIsPending(self.driver))
        
        # Go to Stakeholder and make sure it is not pending anymore
        self.driver.find_element_by_link_text(DEAL_STAKEHOLDER_LINK).click()
        self.assertFalse(checkIsPending(self.driver))
        
        
        