import requests
import logging

from lmkp.tests.test_base import Test_Base

log = logging.getLogger(__name__)

class ModerationBase(Test_Base):

    def __init__(self):
        pass

    def doReview(self, itemType, identifier, version, decision, comment=''):

        """

        """
        moderator = self.getUser(2)
        profile = 'LA'


        # Initialize Session
        session = requests.Session()

        # Authentification
        session.auth = (moderator['username'], moderator['password'])

        # Prepare cookies
        cookies = dict(_PROFILE_=profile)

        # Prepare payload
        payload = {
            'version': version,
            'identifier': identifier,
            'review_decision': decision,
            'comment_textarea': comment
        }

        # Do the post request
        # TODO!!!
        request = session.post(self.getReviewUrl(itemType), data=payload, cookies=cookies)

        try:
            json = request.json()
            return json['success']
        except:
            print "*** Request failed with response: %s" % request
            return False

    def getReviewUrl(self, itemType):
        if itemType == 'activities':
            return 'http://localhost:6543/activities/review'
        elif itemType == 'stakeholders':
            return 'http://localhost:6543/stakeholders/review'
        else:
            return None