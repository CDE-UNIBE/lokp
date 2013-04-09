import logging
import requests
import random
import decimal

from lmkp.tests.test_base import Test_Base

class CreateBase(Test_Base):
    
    def __init__(self):
        self.results = []
    
    def doCreate(self, url, diff, user, profile = 'Laos'):
        
        import json
        
        session = requests.Session()
        
        if user is not None:
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

            involvements = kwargs.pop('involvements', None)
            if involvements is not None:
                diff['stakeholders'] = involvements

        elif itemType == 'stakeholders':
            involvements = kwargs.pop('involvements', None)
            if involvements is not None:
                diff['activities'] = involvements

        return diff

    def createAndCheckFirstItem(self, testObject, itemType, mappedClass, url,
        tags, identifier, user, profile='Laos', **kwargs):
        """
        Wrapper to create a new item and check if it is there or not.
        """

        protocol = kwargs.pop('protocol', testObject.protocol);

        # Check that the item does not yet exist
        if (testObject.handleResult(
            self.countVersions(mappedClass, identifier) == 0,
            'Item (%s) exists already.' % itemType
        )) is not True:
            return False

        # Prepare a geometry if needed
        geometry = (self.getSomeGeometryDiff(profile)
            if itemType == 'activities' else None)

        # Prepare a diff
        diff = self.getSomeWholeDiff(
            itemType,
            tags,
            identifier,
            1,
            'add',
            geometry = geometry
        )

        # Create it
        created = self.doCreate(url, diff, user)

        # Check if it is there
        item = protocol.read_one_by_version(
            testObject.request, identifier, 1
        )

        # Check if it is there
        if (testObject.handleResult(
            (created is True and item is not None),
            'Item (%s) exists already.' % itemType
        )) is not True:
            return False

        # Make sure there is only one version
        if (testObject.handleResult(
            self.countVersions(mappedClass, identifier) == 1,
            'There was more than one Item (%s) created.' % itemType
        )) is not True:
            return False

        return item

    def getSomeWholeDiff(self, itemType, tags, identifier, version, op,
        geometry=None, **kwargs):
        """
        Wrapper to get the diff for an item. All the stuff from the diff has the
        same 'op'. Can be used to create an Activity or a Stakeholder.
        """

        involvements = kwargs.pop('involvements', None)

        # Get the tag diffs and put them into taggroups
        taggroups = []
        for t in tags:

            # Set the first tag of each taggroup as main tag
            maintag = None
            for k, v in t.iteritems():
                if maintag is None:
                    maintag = {
                        'key': k,
                        'value': v
                    }

            taggroups.append({
                'op': op,
                'tags': self.getTagDiffsFromTags(t, op),
                'main_tag': maintag
            })

        singleItemDiff = self.getItemDiff(
            itemType,
            id = identifier,
            version = version,
            taggroups = taggroups,
            geometry = geometry,
            involvements = involvements
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


    def getSomeGeometryDiff(self, profile):

        if profile == 'Laos':
            return {
                'type': 'Point',
                'coordinates': [
                    float(102 + decimal.Decimal(str(random.random()))),
                    float(19 + decimal.Decimal(str(random.random())))
                ]
            }

        return {}

    def getSomeStakeholderTags(self, switch):

        if switch == 1:
            # Very simple, all mandatory keys there. One Tag per Taggroup
            return [
                {
                    'Name': 'Stakeholder A'
                }, {
                    'Country of origin': 'China'
                }
            ]
        return []

    def getSomeActivityTags(self, switch):
        
        if switch == 1:
            # Very simple, all mandatory keys there. One Tag per Taggroup.
            return [
                {
                    'Intended area (ha)': 100
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
                }
            ]
        if switch == 2:
            # All mandatory keys there, sometimes 2 Tags in a Taggroup.
            return [
                {
                    'Intended area (ha)': 200
                }, {
                    'Country': 'Laos'
                }, {
                    'Data source': 'Company sources'
                }, {
                    'Intention of Investment': 'Conservation',
                    'Animals': 'Bees'
                }, {
                    'Negotiation Status': 'Oral agreement',
                    'Current area in operation (ha)': 50
                }, {
                    'Spatial Accuracy': '1km to 10km'
                }
            ]
        if switch == 3:
            # Not all mandatory keys there. 
            # Missing are 'Data source' and 'Intention of Investment'
            return [
                {
                    'Intended area (ha)': 100
                }, {
                    'Country': 'Laos'
                }, {
                    'Negotiation Status': 'Contract signed'
                }, {
                    'Spatial Accuracy': '100m to 1km'
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

    def getCreateUrl(self, itemType):
        if itemType == 'activities':
            return 'http://localhost:6543/activities'
        elif itemType == 'stakeholders':
            return 'http://localhost:6543/stakeholders'
        return None