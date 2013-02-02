import logging

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from lmkp.models.meta import DBSession as Session

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
    
    def countTaggroups(self, feature):
        return len(feature.get_taggroups())
    
    def handleResult(self, success, msg):
        self.results.append(Test_Result(success, msg))
        if success is not True:
            return False
        return True
    
class Test_Result(object):
    
    def __init__(self, success, msg):
        self.success = success
        self.msg = msg