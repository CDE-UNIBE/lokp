import logging
import requests


from lmkp.tests.test_base import Test_Base

class CreateBase(Test_Base):
    
    def __init__(self):
        pass
    
    def doCreate(self, url, diff, user, profile = 'LA'):
        
        import json
        
        session = requests.Session()
        
        session.auth = (user['username'], user['password'])
        
        cookies = dict(_PROFILE_=profile)
        headers = {'content-type': 'application/json'}

        request = session.post(url, data=json.dumps(diff), headers=headers, cookies=cookies)
        
        return request.status_code == 201
    
    def createDiff(self, itemKeyword, id, version, 
        taggroups=None, involvements=None):
        
        diff = {}
        items
        
        
    def putItemDiffTogether(self, **kwargs):
        
        diff = {}
        
        taggroups = kwargs.pop('taggroups', None)
        if taggroups is not None:
            diff['taggroups'] = taggroups
        
        id = kwargs.pop('id', None)
        if id is not None:
            diff['id'] = id
        
        version = kwargs.pop('version', None)
        if version is not None:
            diff['version'] = version
        
        return diff
    
    def getUser(self, userid):
        if userid == 1:
            username = 'user1'
    
        if username is not None:
            password = 'asdf'
        
            return {
                'username': username,
                'password': password
            }
        
        return None
    
    def getSomeActivityTags(self, switch):
        
        if switch == 1:
            return [
                {
                    'Contract area (ha)': 100
                }, {
                    'Country': 'Laos'
                }, {
                    'Data source': 'Contract'
                }, {
                    'Intention of Investment': 'Agriculture'
                }, {
                    'Negotiation Status': 'Contract signed'
                }, {
                    'Spatial Accuracy': '100m to 1km'
                }, {
                    'Year of agreement': 2000
                }
            ]
        
        return []
    
    def kvToTaggroups(self, kvArray):
        taggroups = []
        for kv in kvArray:
            tags = []
            for k in kv.keys():
                tag = {}
                tag['key'] = k
                tag['value'] = kv[k]
                tags.append(tag)
            taggroups.append({'tags': tags})
        return taggroups
        