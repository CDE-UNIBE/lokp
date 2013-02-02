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
    
    def getItemDiff(self, itemType, **kwargs):
        
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

        if itemType == 'activities':
            geometry = kwargs.pop('geometry', None)
            if geometry is not None:
                diff['geometry'] = geometry

            involvements = kwargs.pop('stakeholders', None)
            if involvements is not None:
                diff['activities'] = involvements

        elif itemType == 'stakeholders':
            involvements = kwargs.pop('activities', None)
            if involvements is not None:
                diff['activities'] = involvements

        return diff

    def getSomeWholeDiff(self, itemType, tags, identifier, version, op,
        geometry=None):
        """
        Wrapper to get the diff for an item. All the stuff from the diff has the
        same 'op'. Can be used to create an Activity or a Stakeholder.
        """

        # Get the tag diffs and put them into taggroups
        taggroups = []
        for t in tags:
            taggroups.append({
                'op': op,
                'tags': self.getTagDiffsFromTags(t, op)
            })

        singleItemDiff = self.getItemDiff(
            itemType,
            id = identifier,
            version = version,
            taggroups = taggroups,
            geometry = geometry
        )

        return {itemType: [singleItemDiff]}

    def getTagDiffsFromTags(self, kv, op):
        tags = []
        for k in kv.keys():
            tagDiff = {}
            tagDiff['key'] = k
            tagDiff['value'] = kv[k]
            tagDiff['op'] = op
            tags.append(tagDiff)
        return tags
        
        
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

    def getSomeGeometryDiff(self, profile):

        if profile == 'LA':
            return {
                'type': 'Point',
                'coordinates': [
                    102.43437290193, 20.163276384469
                ]
            }

        return {}


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
        