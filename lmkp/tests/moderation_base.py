import requests
import logging

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

log = logging.getLogger(__name__)

url = 'http://localhost:6543/activities/review'

class ModerationBase(object):

    def __init__(self):
        pass


    def query0ne(self, query):
        try:
            result = query.one()
        except NoResultFound:
            return False
        except MultipleResultsFound:
            return False
        return result

    def doRequest(self, identifier, version, decision, comment=''):

        # Initialize Session
        session = requests.Session()

        # Authentification
        session.auth = ('user2', 'asdf')

        # Prepare cookies
        cookies = dict(_PROFILE_='LA')

        # Prepare payload
        payload = {
            'version': version,
            'identifier': identifier,
            'review_decision': decision,
            'comment_textarea': comment
        }

        # Do the post request
        request = session.post(url, data=payload, cookies=cookies)

        json = request.json()

        return json['success']

    def findKeyValue(self, feature, key, value):

        found = 0
        for taggroup in feature.get_taggroups():
            tag = taggroup.get_tag_by_key(key)
            if tag is not None and tag.get_value() == str(value):
                found += 1

        if found > 1:
            log.debug('Key (%s) and value (%s) found more than once (%s times)' %
                      (key, value, found))

        return found == 1
        