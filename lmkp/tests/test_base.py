import logging

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from lmkp.models.meta import DBSession as Session
from lmkp.models.database_objects import Stakeholder_Role

log = logging.getLogger(__name__)

class Test_Base(object):
    
    def __init__(self):
        self.results = []
    
    def query0ne(self, query):
        try:
            result = query.one()
        except NoResultFound:
            return False
        except MultipleResultsFound:
            return False
        return result
    
    def countVersions(self, mappedClass, identifier):
        
        return Session.query(
                mappedClass.id
            ).\
            filter(mappedClass.identifier == identifier).\
            count()

    def getUser(self, userid):
        if userid == 0:
            return None
        if userid == 1:
            username = 'user1'
        elif userid == 2:
            username = 'user2'
        elif userid == 3:
            username = 'user3'
        elif userid == 4:
            username = 'user4'
        else:
            return None

        if username is not None:
            password = 'asdf'

            return {
                'username': username,
                'password': password
            }

        return None

    def getStakeholderRole(self, id):
        q = Session.query(Stakeholder_Role).get(id)
        if q is not None:
            return {
                'id': q.id,
                'name': q.name
            }
        return None

    def findKey(self, feature, key):
        
        found = 0
        for taggroup in feature.get_taggroups():
            tag = taggroup.get_tag_by_key(key)
            if tag is not None:
                found += 1
        
        if found > 1:
            log.debug('Key (%s) found more than once (%s times)' %
                      (key, found))

        return found == 1
    
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

    def findTgidByKeyValue(self, feature, key, value):

        for taggroup in feature.get_taggroups():
            tag = taggroup.get_tag_by_key(key)
            if tag is not None and tag.get_value() == str(value):
                return taggroup.get_tg_id()

        return None

    def countTaggroups(self, feature):
        return len(feature.get_taggroups())

    def countTags(self, feature):
        count = 0
        for taggroup in feature.get_taggroups():
            count += len(taggroup.get_tags())
        return count
    
    def handleResult(self, success, msg):
        self.results.append(Test_Result(success, msg))
        if success is not True:
            return False
        return True

    def getDetailsUrl(self, type, uid, **kwargs):
        url = None
        if type == 'activities':
            url = 'http://localhost:6543/activities/'
        elif type == 'stakeholders':
            url = 'http://localhost:6543/stakeholders/'

        if url is None:
            return None

        if kwargs.pop('public', False) is True:
            url += 'public/'
    
        return url + 'json/' + uid

    def getFilterUrl(self, type, filterColumns, filterValues, **kwargs):

        url = ''

        if type == 'activities':
            url += 'http://localhost:6543/activities/'
            prefix = 'a'

        elif type == 'stakeholders':
            url += 'http://localhost:6543/stakeholders/'
            prefix = 'sh'

        if kwargs.pop('public', False) is True:
            url += 'public/'

        url += 'json?'

        filters = []
        for i, c in enumerate(filterColumns):
            filters.append('%s__%s__like=%s' % (prefix, c, filterValues[i]))

        return url + '&'.join(filters)

class Test_Result(object):
    
    def __init__(self, success, msg):
        self.success = success
        self.msg = msg


# Some sample for Activity Tests
"""

class TestName00(TheBase):
    
    # TheBase: CreateBase / EditBase / ModerationBase
    
    def __init__(self, request):
        super(TheBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "XX00"
        self.testDescription = 'DESCRIPTION'
        self.identifier1 = 'IDENTIFIER'
        self.a1v1 = None

    def testSetup(self):
        return True
    
    def doTest(self, verbose=False):
        return True

"""