import logging
import requests
import random
import decimal

from lmkp.tests.test_base import Test_Base
from lmkp.tests.moderate.moderation_base import ModerationBase

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

    def createModerateCheckFirstItem(self, testObject, itemType, mappedClass,
        url, tags, identifier, user, profile='Laos', **kwargs):
        """
        Wrapper to create a new item, review it (set active) and check if it is
        there or not.
        """

        protocol = kwargs.get('protocol', testObject.protocol);

        # Create the item
        o = self.createAndCheckFirstItem(testObject, itemType, mappedClass, url,
            tags, identifier, user, profile, **kwargs)

        if (testObject.handleResult(
            o is not None and o is not False,
            'The item could not be created.'
        )) is not True:
            return False

        # Moderate the item
        mb = ModerationBase()

        # Try to review the item
        if (testObject.handleResult(
            mb.doReview(itemType, identifier, o.get_version(), 1) is True,
            'The item could not be reviewed.'
        )) is not True:
            return False

        # Query the reviewed item
        reviewed_o = protocol.read_one_by_version(
            testObject.request, identifier, 1
        )

        # Make sure it is active
        if (testObject.handleResult(
            reviewed_o.get_status_id() == 2,
            'The item was not set to active during review.'
        )) is not True:
            return False

        return reviewed_o

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
            'Item (%s) was not really created.' % itemType
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
        setMaintags = kwargs.get('setMaintags', True)
        addTgids = kwargs.get('addTgids', False)

        # Get the tag diffs and put them into taggroups
        taggroups = []
        for i, t in enumerate(tags):

            tag = {
                'op': op,
                'tags': self.getTagDiffsFromTags(t, op)
            }

            if setMaintags is True:
                # Set the first tag of each taggroup as main tag
                maintag = None
                for k, v in t.iteritems():
                    if maintag is None:
                        maintag = {
                            'key': k,
                            'value': v
                        }
                tag['main_tag'] = maintag

            if addTgids is True:
                # Add the tg_ids
                tag['tg_id'] = i + 1

            taggroups.append(tag)

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

    def getSomeStakeholderTags(self, switch, **kwargs):

        if switch == 1:
            # Very simple, all mandatory keys there. One Tag per Taggroup
            return [
                {
                    'Name': 'Stakeholder A'
                }, {
                    'Country of origin': 'China'
                }
            ]
        if switch == 2:
            # All mandatory keys there, with 2 Tags in a Taggroup.
            return [
                {
                    'Name': 'Stakeholder X',
                    'Website': 'http://url.com'
                }, {
                    'Country of origin': 'Vietnam',
                    'Economic Sector': 'Mining'
                }
            ]
        if switch == 3:
            # Not all mandatory keys there.
            # Missing is 'Country of origin'
            return [
                {
                    'Name': 'Stakeholder B'
                }
            ]
        if switch == 4:
            # Basically the simple keys as above but with additional taggroup
            # containing "Address: [UUID]" allowing to find this specific
            # Stakeholder through filters
            uid = kwargs.pop('uid', '-')
            return [
                {
                    'Name': 'Stakeholder A'
                }, {
                    'Country of origin': 'China'
                }, {
                    'Address': uid
                }
            ]
        return []

    def getSomeActivityTags(self, switch, **kwargs):
        
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
        if switch == 4:
            # Basically the simple keys as above but with additional taggroup
            # containing "Remark: [UUID]" allowing to find this specific 
            # Activity through filters
            uid = kwargs.pop('uid', '-')
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
                }, {
                    'Remark': uid
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