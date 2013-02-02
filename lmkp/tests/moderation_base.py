import requests
import logging

from lmkp.tests.test_base import Test_Base

log = logging.getLogger(__name__)

# Constants
review_url = 'http://localhost:6543/activities/review'
moderator_username = 'user2'
moderator_password = 'asdf'
moderator_profile = 'LA'

class ModerationBase(Test_Base):

    def __init__(self):
        pass

    def doReview(self, identifier, version, decision, comment=''):

        # Initialize Session
        session = requests.Session()

        # Authentification
        session.auth = (moderator_username, moderator_password)

        # Prepare cookies
        cookies = dict(_PROFILE_=moderator_profile)

        # Prepare payload
        payload = {
            'version': version,
            'identifier': identifier,
            'review_decision': decision,
            'comment_textarea': comment
        }

        # Do the post request
        request = session.post(review_url, data=payload, cookies=cookies)

        try:
            json = request.json()
            return json['success']
        except:
            print "*** Request failed with response: %s" % request
            return False


        