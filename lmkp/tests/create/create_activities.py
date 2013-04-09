from lmkp.tests.create.create_base import CreateBase

from lmkp.models.meta import DBSession as Session
from lmkp.models.database_objects import *
from lmkp.views.activity_protocol3 import ActivityProtocol3

import logging
log = logging.getLogger(__name__)

"""
CA 01
"""
class CreateActivities01(CreateBase):
    
    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "CA01"
        self.testDescription = 'It is possible to create a new Activity'
        self.identifier1 = '58be3840-6bda-11e2-bcfd-0800200c9a61'
        self.a1v1 = None
        
    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity exists already'
        )) is not True:
            return False

        return True
        
    def doTest(self, verbose=False):

        diff = self.getSomeWholeDiff(
            'activities',
            self.getSomeActivityTags(1),
            self.identifier1,
            1,
            'add',
            self.getSomeGeometryDiff('Laos')
        )

        if verbose is True:
            log.debug('Diff to create a1v1:\n%s' % diff)
        
        # Create the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'New Activity could not be created at all.'
        )) is not True:
            return False
        
        # Find the created Activity
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1 is not None,
            'New Activity was created but not found.'
        )) is not True:
            return False
        
        # Make sure there is only one version of the Activity
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 1,
            'There was more than one version of the Activity created.'
        )) is not True:
            return False
        
        # Make sure the Activity has all the taggroups
        if (self.handleResult(
            self.countTaggroups(self.a1v1) == len(self.getSomeActivityTags(1)),
            'New Activity has not all taggroups.'
        )) is not True:
            return False

        # Make sure the Activity has status 'pending'
        if (self.handleResult(
            self.a1v1.get_status_id() == 1,
            'New Activity has not status "pending".'
        )) is not True:
            return False

        return True

"""
CA 02
"""
class CreateActivities02(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "CA02"
        self.testDescription = 'Only logged in users can create a new Activity'
        self.identifier1 = '2a889f80-e571-471a-82b7-e1a2eac47a16'
        self.a1v1 = None

    def testSetup(self):

        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity exists already'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):
        
        diff = self.getSomeWholeDiff(
            'activities',
            self.getSomeActivityTags(1),
            self.identifier1,
            1,
            'add'
        )

        if verbose is True:
            log.debug('Diff to create a1v1:\n%s' % diff)
        
        # Try to do the create without authentication
        import requests
        import json
        session = requests.Session()
        
        cookies = dict(_PROFILE_='Laos')
        headers = {'content-type': 'application/json'}

        request = session.post(
            self.getCreateUrl('activities'), 
            data=json.dumps(diff), 
            headers=headers, 
            cookies=cookies
        )
        
        if (self.handleResult(
            request.status_code == 200,
            'The new Activity was created even when user was not logged in.'
        )) is not True:
            return False
        
        # Make sure that the Activity was not created
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'There was a version of the Activity created by an anonymous user.'
        )) is not True:
            return False

        return True
    
"""
CA 03
"""
class CreateActivities03(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "CA03"
        self.testDescription = 'New Activities can be created with a specific identifier'
        self.identifier1 = '8e4ae658-0a10-4614-8cb0-b3326a3882e0'
        self.a1v1 = None

    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity exists already'
        )) is not True:
            return False

        return True
    
    def doTest(self, verbose=False):
        
        diff = self.getSomeWholeDiff(
            'activities',
            self.getSomeActivityTags(1),
            self.identifier1,
            1,
            'add',
            self.getSomeGeometryDiff('Laos')
        )

        if verbose is True:
            log.debug('Diff to create a1v1:\n%s' % diff)
        
        # Create the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'New Activity could not be created at all.'
        )) is not True:
            return False
        
        # Find the created Activity
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1 is not None,
            'New Activity was created but not found.'
        )) is not True:
            return False
        
        # Make sure there is only one version of the Activity
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 1,
            'There was more than one version of the Activity created.'
        )) is not True:
            return False
        
        # Make sure the Activity has all the taggroups (7)
        if (self.handleResult(
            self.countTaggroups(self.a1v1) == 6,
            'New Activity has not all taggroups.'
        )) is not True:
            return False
        
        return True

"""
CA 04
"""
class CreateActivities04(CreateBase):
    
    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "CA04"
        self.testDescription = 'New Activities can be created without an identifier'
        self.identifier1 = None
        self.a1v1 = None

    def testSetup(self):
        return True
    
    def doTest(self, verbose=False):
        
        diff = self.getSomeWholeDiff(
            'activities',
            self.getSomeActivityTags(1),
            None,
            1,
            'add',
            self.getSomeGeometryDiff('Laos')
        )
        
        if verbose is True:
            log.debug('Diff to create a1v1:\n%s' % diff)
        
        import requests
        import json
        session = requests.Session()
        
        user = self.getUser(1)
        session.auth = (user['username'], user['password'])
        
        cookies = dict(_PROFILE_='Laos')
        headers = {'content-type': 'application/json'}

        request = session.post(
            self.getCreateUrl('activities'), 
            data=json.dumps(diff), 
            headers=headers, 
            cookies=cookies
        )
        
        if (self.handleResult(
            request.status_code == 201,
            'The new Activity could not be created.'
        )) is not True:
            return False
        
        json = request.json()
        
        if (self.handleResult(
            'created' in json and json['created'] is True,
            'Server response ("created") after creating new Activity is not correct.'
        )) is not True:
            return False
        
        if (self.handleResult(
            'data' in json and len(json['data']) == 1,
            'Server response ("data") after creating new Activity is not correct.'
        )) is not True:
            return False
        
        data = json['data'][0]
        if (self.handleResult(
            'id' in data,
            'Server response ("id" in data) after creating new Activity is not correct.'
        )) is not True:
            return False
        
        self.identifier1 = data['id']
        # Try to find the Activity with the newly created uid
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1 is not None,
            'New Activity was created but not found.'
        )) is not True:
            return False
        
        # Check that there is one (and only one) version
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 1,
            'There is not only one version of the Activity.'
        )) is not True:
            return False
        
        return True

"""
CA 05
"""
class CreateActivities05(CreateBase):
    
    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "CA05"
        self.testDescription = 'Mandatory keys are not necessary to create a new Activity'
        self.identifier1 = 'be884215-f296-4fe2-9c28-d585ab4eb21f'
        self.a1v1 = None

    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity exists already'
        )) is not True:
            return False
        
        return True
    
    def doTest(self, verbose=False):
        
        # Create and check a first Activity
        self.a1v1 = self.createAndCheckFirstItem(
            self,
            'activities',
            Activity,
            self.getCreateUrl('activities'),
            self.getSomeActivityTags(3),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created'
        )) is not True:
            return False
        
        # Not all the mandatory keys are there
        if (self.handleResult(
            (self.findKey(self.a1v1, 'Data source') is False and 
            self.findKey(self.a1v1, 'Intention of Investment') is False),
            'The missing mandatory keys are suddenly there.'
        )) is not True:
            return False
        
        return True

"""
CA 06
"""
class CreateActivities06(CreateBase):
        
    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "CA06"
        self.testDescription = 'Inexistent keys (not defined in YAML) cannot be used to create a new Activity'
        self.identifier1 = '069e1859-6ea4-4170-a9fb-aa554c90ecfb'
        self.a1v1 = None

    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity exists already'
        )) is not True:
            return False
        
        return True
    
    def doTest(self, verbose=False):
        
        # Create some nonsense Tags
        tags = [
            {
                'My own key 1': 'Some value'
            }, {
                'Custom key 2': 'Other value'
            }
        ]
        
        diff = self.getSomeWholeDiff(
            'activities',
            tags,
            self.identifier1,
            1,
            'add',
            self.getSomeGeometryDiff('Laos')
        )
        
        if verbose is True:
            log.debug('Diff to create a1v1:\n%s' % diff)
        
        # Try to do the create
        import requests
        import json
        session = requests.Session()
        
        user = self.getUser(1)
        session.auth = (user['username'], user['password'])
        
        cookies = dict(_PROFILE_='Laos')
        headers = {'content-type': 'application/json'}

        request = session.post(
            self.getCreateUrl('activities'), 
            data=json.dumps(diff), 
            headers=headers, 
            cookies=cookies
        )
        
        if (self.handleResult(
            request.status_code == 400,
            'The new Activity was created even though it has keys not defined in yaml.'
        )) is not True:
            return False
        
        # Make sure that the Activity was not created
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'There was a version of the Activity with undefined keys created.'
        )) is not True:
            return False
        
        return True

"""
CA 07
"""
class CreateActivities07(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "CA07"
        self.testDescription = 'New Activities can contain more than one tag per taggroup'
        self.identifier1 = 'eaa7d04a-b087-4036-b811-b65538473bf1'
        self.a1v1 = None

    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity exists already'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Create and check a first Activity
        self.a1v1 = self.createAndCheckFirstItem(
            self,
            'activities',
            Activity,
            self.getCreateUrl('activities'),
            self.getSomeActivityTags(2),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created'
        )) is not True:
            return False

        # Make sure the Activity has all the taggroups
        if (self.handleResult(
            self.countTaggroups(self.a1v1) == len(self.getSomeActivityTags(2)),
            'New Activity has not all taggroups.'
        )) is not True:
            return False

        # There are more tags than taggroups
        if (self.handleResult(
            self.countTags(self.a1v1) > len(self.getSomeActivityTags(2)),
            'New Activity has not more tags than taggroups'
        )) is not True:
            return False

        return True

"""
CA 08
"""
class CreateActivities08(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "CA08"
        self.testDescription = 'Without a valid geometry, a new Activity cannot be created'
        self.identifier1 = '4cef69be-16e2-4418-929e-fc113d44f8e6'
        self.a1v1 = None

    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity exists already'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        noGeomDiff = self.getSomeWholeDiff(
            'activities',
            self.getSomeActivityTags(1),
            self.identifier1,
            1,
            'add'
        )

        if verbose is True:
            log.debug('Diff to create a1v1 without a geometry:\n%s' % noGeomDiff)

        import requests
        import json
        session = requests.Session()

        user = self.getUser(1)
        session.auth = (user['username'], user['password'])

        cookies = dict(_PROFILE_='Laos')
        headers = {'content-type': 'application/json'}

        request = session.post(
            self.getCreateUrl('activities'),
            data=json.dumps(noGeomDiff),
            headers=headers,
            cookies=cookies
        )

        if (self.handleResult(
            request.status_code == 400,
            'The new Activity was created even though it has no geometry.'
        )) is not True:
            return False

        # Make sure that the Activity was not created
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'There was a version of the Activity without geometry created.'
        )) is not True:
            return False

        # Repeat the procedure with a diff having an invalid geometry
        invalidGeomDiff = self.getSomeWholeDiff(
            'activities',
            self.getSomeActivityTags(1),
            self.identifier1,
            1,
            'add',
            {'type': 'Point', 'coordinates': ['blabla1', 'blabla2']}
        )
        if verbose is True:
            log.debug('Diff to create a1v1 with an invalid geometry:\n%s' % invalidGeomDiff)
        session = requests.Session()
        user = self.getUser(1)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Laos')
        headers = {'content-type': 'application/json'}
        request = session.post(
            self.getCreateUrl('activities'),
            data=json.dumps(invalidGeomDiff),
            headers=headers,
            cookies=cookies
        )
        if (self.handleResult(
            request.status_code == 400,
            'The new Activity was created even though it has an invalid geometry.'
        )) is not True:
            return False
        # Make sure that the Activity was not created
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'There was a version of the Activity with an invalid geometry created.'
        )) is not True:
            return False

        # Repeat the procedure with a diff having a polygon geometry
#        polygonGeomDiff = self.getSomeWholeDiff(
#            'activities',
#            self.getSomeActivityTags(1),
#            self.identifier1,
#            1,
#            'add',
#            {'type': 'Polygon', 'coordinates': [
#                [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]
#            ]}
#        )
#        if verbose is True:
#            log.debug('Diff to create a1v1 with a polygon geometry:\n%s' % polygonGeomDiff)
#        session = requests.Session()
#        user = self.getUser(1)
#        session.auth = (user['username'], user['password'])
#        cookies = dict(_PROFILE_='Laos')
#        headers = {'content-type': 'application/json'}
#        request = session.post(
#            self.getCreateUrl('activities'),
#            data=json.dumps(polygonGeomDiff),
#            headers=headers,
#            cookies=cookies
#        )
#        if (self.handleResult(
#            request.status_code == 400,
#            'The new Activity was created even though it has a polygon geometry.'
#        )) is not True:
#            return False
#        # Make sure that the Activity was not created
#        if (self.handleResult(
#            self.countVersions(Activity, self.identifier1) == 0,
#            'There was a version of the Activity with a polygon geometry created.'
#        )) is not True:
#            return False

        return True

"""
CA 09
"""
class CreateActivities09(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "CA09"
        self.testDescription = 'New Activities can be created with an existing Stakeholder'
        self.identifier1 = '910c52ce-7e0c-4028-b46e-9edd131fc2f6'
        self.a1v1 = None

        from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
        self.otherProtocol = StakeholderProtocol3(Session)
        self.identifier2 = '91972cf9-8fa6-4d7f-873d-e88eea514884'
        self.s1v1 = None
        self.s1v2 = None
        self.invRole1 = self.getStakeholderRole(6)

    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity exists already'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Create and check a first Stakeholder
        self.s1v1 = self.createAndCheckFirstItem(
            self,
            'stakeholders',
            Stakeholder,
            self.getCreateUrl('stakeholders'),
            self.getSomeStakeholderTags(1),
            self.identifier2,
            self.getUser(1),
            protocol = self.otherProtocol
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created'
        )) is not True:
            return False

        # Make sure the Stakeholder has not involvement
        if (self.handleResult(
            len(self.s1v1.get_involvements()) == 0,
            'Newly created Stakeholder already has an involvement.'
        )) is not True:
            return False

        diff = self.getSomeWholeDiff(
            'activities',
            self.getSomeActivityTags(1),
            self.identifier1,
            1,
            'add',
            self.getSomeGeometryDiff('Laos'),
            involvements = [
                {
                    'id': self.identifier2,
                    'version': 1,
                    'role': self.invRole1['id'],
                    'op': 'add'
                }
            ]
        )

        if verbose is True:
            log.debug('Diff to create s1v1:\n%s' % diff)

        # Create the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'New Activity could not be created at all.'
        )) is not True:
            return False

        # Find the created Activity
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1 is not None,
            'New Activity was created but not found.'
        )) is not True:
            return False

        # Make sure there is only one version of the Activity
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 1,
            'There was more than one version of the Activity created.'
        )) is not True:
            return False

        # Make sure the Activity has all the taggroups
        if (self.handleResult(
            self.countTaggroups(self.a1v1) == len(self.getSomeActivityTags(1)),
            'New Activity has not all taggroups.'
        )) is not True:
            return False

        # Make sure the Activity has status 'pending'
        if (self.handleResult(
            self.a1v1.get_status_id() == 1,
            'New Activity has not status "pending".'
        )) is not True:
            return False

        # Make sure the first Stakeholder still has no involvement
        if (self.handleResult(
            len(self.s1v1.get_involvements()) == 0,
            'Stakeholder version 1 suddenly has an involvement.'
        )) is not True:
            return False

        # Make sure the first Stakeholder is still pending
        if (self.handleResult(
            self.s1v1.get_status_id() == 1,
            'Stakeholder version 1 is not "pending" anymore.'
        )) is not True:
            return False

        # Make sure the Activity has an involvement
        if (self.handleResult(
            len(self.a1v1.get_involvements()) == 1,
            'Newly created Activity does not have an involvement.'
        )) is not True:
            return False

        # Make sure there was a second version of the Stakeholder created
        self.s1v2 = self.otherProtocol.read_one_by_version(
            self.request, self.identifier2, 2
        )
        if (self.handleResult(
            self.s1v2 is not None,
            'There was no new version of the Stakeholder created.'
        )) is not True:
            return False

        # Make sure the newly created version of the Stakeholder has an involvement
        if (self.handleResult(
            len(self.s1v2.get_involvements()) == 1,
            'Newly created Stakeholder version does not have an involvement.'
        )) is not True:
            return False

        # Make sure the new Stakeholder version is pending
        if (self.handleResult(
            self.s1v2.get_status_id() == 1,
            'Stakeholder version 2 is not "pending".'
        )) is not True:
            return False

        # Make sure the involvements point to the other object
        if (self.handleResult(
            self.a1v1.find_involvement_by_guid(self.identifier2) is not None,
            'Involvement of Activity does not point to correct Stakeholder'
        )) is not True:
            return False
        if (self.handleResult(
            self.s1v2.find_involvement_by_guid(self.identifier1) is not None,
            'Involvement of Stakeholder does not point to correct Activity'
        )) is not True:
            return False
        if (self.handleResult(
            self.a1v1.find_involvement(self.identifier2, self.invRole1['name'], 2) is not None,
            'Involvement of Activity does not point to correct Stakeholder version'
        )) is not True:
            return False
        if (self.handleResult(
            self.s1v2.find_involvement(self.identifier1, self.invRole1['name'], 1) is not None,
            'Involvement of Stakeholder does not point to correct Activity version'
        )) is not True:
            return False

        return True

"""
CA 10
"""
class CreateActivities10(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "CA10"
        self.testDescription = 'Creating new Activities without existing Stakeholder creates the Activity but no Involvement.'
        self.identifier1 = '5639ddaf-b37c-4570-aaf1-d143ff159782'
        self.a1v1 = None

        from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
        self.otherProtocol = StakeholderProtocol3(Session)
        self.identifier2 = '85577acf-aaa3-40e7-88b8-ed2cdec75a21'
        self.s1v1 = None
        self.invRole1 = self.getStakeholderRole(6)

    def testSetup(self):
        # Make sure the Activity does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity exists already'
        )) is not True:
            return False

        # Make sure the Stakeholder does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier2) == 0,
            'Stakeholder exists already'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        diff = self.getSomeWholeDiff(
            'activities',
            self.getSomeActivityTags(1),
            self.identifier1,
            1,
            'add',
            self.getSomeGeometryDiff('Laos'),
            involvements = [
                {
                    'id': self.identifier2,
                    'version': 1,
                    'role': self.invRole1['id'],
                    'op': 'add'
                }
            ]
        )

        if verbose is True:
            log.debug('Diff to create s1v1:\n%s' % diff)

        # Create the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'New Activity could not be created at all.'
        )) is not True:
            return False

        # Find the created Activity
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1 is not None,
            'New Activity was created but not found.'
        )) is not True:
            return False

        # Make sure there is only one version of the Activity
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 1,
            'There was more than one version of the Activity created.'
        )) is not True:
            return False

        # Make sure the Activity has status 'pending'
        if (self.handleResult(
            self.a1v1.get_status_id() == 1,
            'New Activity has not status "pending".'
        )) is not True:
            return False

        # Make sure the Stakeholder was not created
        self.s1v1 = self.otherProtocol.read_one_by_version(
            self.request, self.identifier2, 1
        )
        if (self.handleResult(
            self.s1v1 is None,
            'New Stakeholder was created.'
        )) is not True:
            return False

        # Make sure the Activity has no Involvement
        if (self.handleResult(
            len(self.a1v1.get_involvements()) == 0,
            'The Activity has an involvement.'
        )) is not True:
            return False

        return True

"""
CA 11
"""
class CreateActivities11(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "CA11"
        self.testDescription = 'The first tag of a taggroup is treated as the main tag when creating a new Activity'
        self.identifier1 = '4406f35e-92c1-4d89-adee-6a91d89c394e'
        self.a1v1 = None

    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity exists already'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Create and check a first Activity
        self.a1v1 = self.createAndCheckFirstItem(
            self,
            'activities',
            Activity,
            self.getCreateUrl('activities'),
            self.getSomeActivityTags(2),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created'
        )) is not True:
            return False

        # Make sure the Activity has all the taggroups
        if (self.handleResult(
            self.countTaggroups(self.a1v1) == len(self.getSomeActivityTags(2)),
            'New Activity has not all taggroups.'
        )) is not True:
            return False

        # There are more tags than taggroups
        if (self.handleResult(
            self.countTags(self.a1v1) > len(self.getSomeActivityTags(2)),
            'New Activity has not more tags than taggroups'
        )) is not True:
            return False

        # There is a maintag set for all taggroups
        maintagSet = True
        for tg in self.a1v1.get_taggroups():
            if tg.get_maintag_id() is None:
                maintagSet = False
        if (self.handleResult(
            maintagSet is True,
            'There is not a maintag set for each taggroup'
        )) is not True:
            return False

        # The maintag is a tag of the taggroup
        maintagIsTag = True
        for tg in self.a1v1.get_taggroups():
            if tg.get_tag_by_id(tg.get_maintag_id()) is None:
                maintagIsTag = False
        if (self.handleResult(
            maintagIsTag is True,
            'The maintag set is not one of the tags of the taggroup'
        )) is not True:
            return False

        return True
