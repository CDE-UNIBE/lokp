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
            'add',
            self.getSomeGeometryDiff('Laos')
        )

        if verbose is True:
            log.debug('Diff to create a1v1:\n%s' % diff)
        
        # Try to do the create without authentication
        import requests
        import json
        session = requests.Session()
        session.auth = ()
        
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
            self.countTaggroups(self.a1v1) == len(self.getSomeActivityTags(1)),
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

        self.request.cookies['_PROFILE_'] = 'global'

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

"""
CA 12
"""
class CreateActivities12(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "CA12"
        self.testDescription = 'Newly created Activities (pending) are only visible to moderators of current profile or the user who created it'
        self.identifier1 = '13b71742-b670-437d-a393-f439d137e4c0'
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
            self.getSomeActivityTags(4, uid=self.identifier1),
            self.identifier1,
            self.getUser(3),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created'
        )) is not True:
            return False

        import requests
        import json

        # Public
        session = requests.Session()
        session.auth = ()
        headers = {'content-type': 'application/json'}
        request = session.get( # Explicit
            self.getDetailsUrl('activities', self.identifier1),
            headers=headers
        )

        # Make sure a request to get the details of the Activity can be made
        if (self.handleResult(
            request.status_code == 200,
            'The request to get details of an Activity failed'
        )) is not True:
            return False

        json = request.json()

        # Make sure the response has the correct form
        if (self.handleResult(
            'total' in json and 'data' in json,
            'The response of the request to query an Activity (explicit) does not have the correct form'
        )) is not True:
            return False

        # Public should not see the pending Activity
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'The public sees the pending Activity (explicit) although it should not'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = ()
        request = session.get( # Filtered
            self.getFilterUrl('activities', ['Remark'], [self.identifier1]),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'The public sees the pending Activity (filtered) although it should not.'
        )) is not True:
            return False

        # Public should not see pending Activity when using public query
        session = requests.Session()
        session.auth = ()
        request = session.get( # Explicit, public query
            self.getDetailsUrl('activities', self.identifier1, public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'Public sees a pending Activity with public query and querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = ()
        request = session.get( # Filtered
            self.getFilterUrl('activities', ['Remark'], [self.identifier1], public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'Public sees a pending Activity with public query and using a filter to find it.'
        )) is not True:
            return False


        # User 3 (editor who created the A) should see the pending Activity
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        request = session.get( # Explicit
            self.getDetailsUrl('activities', self.identifier1),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'User 3 (editor of the Activity) does not see his own Activity when querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        request = session.get( # Filtered
            self.getFilterUrl('activities', ['Remark'], [self.identifier1]),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'User 3 (editor of the Activity) does not see his own pending Activity when using a filter to find it.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        request = session.get( # Explicit, public query
            self.getDetailsUrl('activities', self.identifier1, public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 3 sees a pending Activity with public query and querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        request = session.get( # Filtered
            self.getFilterUrl('activities', ['Remark'], [self.identifier1], public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 3 sees a pending Activity with public query and using a filter to find it.'
        )) is not True:
            return False

        # User 2 (moderator of Cambodia profile) should not see the pending A.
        session = requests.Session()
        user = self.getUser(2)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Cambodia')
        request = session.get( # Explicit, with Cambodia profile
            self.getDetailsUrl('activities', self.identifier1),
            headers=headers,
            cookies=cookies
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 2 (Cambodia moderator) sees a pending Activity in Laos with Cambodia profile selected and querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Laos')
        request = session.get( # Explicit, with Laos profile
            self.getDetailsUrl('activities', self.identifier1),
            headers=headers,
            cookies=cookies
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 2 (Cambodia moderator) sees a pending Activity in Laos with Laos profile selected and querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        cookies = dict(_PROFILE_='Cambodia')
        session.auth = (user['username'], user['password'])
        request = session.get( # Filtered, with Cambodia profile
            self.getFilterUrl('activities', ['Remark'], [self.identifier1]),
            headers=headers,
            cookies=cookies
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 2 (Cambodia moderator) sees a pending Activity in Laos with Cambodia profile selected and using a filter to find it.'
        )) is not True:
            return False
        session = requests.Session()
        cookies = dict(_PROFILE_='Laos')
        session.auth = (user['username'], user['password'])
        request = session.get( # Filtered, with Laos profile
            self.getFilterUrl('activities', ['Remark'], [self.identifier1]),
            headers=headers,
            cookies=cookies
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 2 (Cambodia moderator) sees a pending Activity in Laos with Laos profile selected and using a filter to find it.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        request = session.get( # Explicit, public query
            self.getDetailsUrl('activities', self.identifier1, public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 2 sees a pending Activity with public query and querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        request = session.get( # Filtered
            self.getFilterUrl('activities', ['Remark'], [self.identifier1], public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 2 sees a pending Activity with public query and using a filter to find it.'
        )) is not True:
            return False


        # User 1 (moderator of Laos profile) should see the pending A, but only
        # in his profile
        session = requests.Session()
        user = self.getUser(1)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Laos')
        request = session.get( # Explicit, with Laos profile
            self.getDetailsUrl('activities', self.identifier1),
            headers=headers,
            cookies=cookies
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'User 1 (Laos moderator) does not see the pending Activity in Laos with Laos profile selected and querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        user = self.getUser(1)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Cambodia')
        request = session.get( # Explicit, with Cambodia profile
            self.getDetailsUrl('activities', self.identifier1),
            headers=headers,
            cookies=cookies
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 1 (Laos moderator) sees the pending Activity in Laos with Cambodia profile selected and querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Laos')
        request = session.get( # Filtered, with Laos profile
            self.getFilterUrl('activities', ['Remark'], [self.identifier1]),
            headers=headers,
            cookies=cookies
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'User 1 (Laos moderator) does not see the pending Activity in Laos with Laos profile selected and using a filter to find it.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Cambodia')
        request = session.get( # Filtered, with Cambodia profile
            self.getFilterUrl('activities', ['Remark'], [self.identifier1]),
            headers=headers,
            cookies=cookies
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 1 (Laos moderator) sees the pending Activity in Laos with Cambodia profile selected and using a filter to find it.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        request = session.get( # Explicit, public query
            self.getDetailsUrl('activities', self.identifier1, public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 1 sees a pending Activity with public query and querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        request = session.get( # Filtered
            self.getFilterUrl('activities', ['Remark'], [self.identifier1], public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 1 sees a pending Activity with public query and using a filter to find it.'
        )) is not True:
            return False


        # User 4 should not see the pending Activity
        session = requests.Session()
        user = self.getUser(4)
        session.auth = (user['username'], user['password'])
        request = session.get( # Explicit
            self.getDetailsUrl('activities', self.identifier1),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 4 sees a pending Activity when querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        request = session.get( # Filtered
            self.getFilterUrl('activities', ['Remark'], [self.identifier1]),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 4 sees a pending Activity when using a filter to find it.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        request = session.get( # Explicit, public query
            self.getDetailsUrl('activities', self.identifier1, public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 4 sees a pending Activity with public query and querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        request = session.get( # Filtered
            self.getFilterUrl('activities', ['Remark'], [self.identifier1], public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 4 sees a pending Activity with public query and using a filter to find it.'
        )) is not True:
            return False

        return True

"""
CA 13
"""
class CreateActivities13(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "CA13"
        self.testDescription = 'Newly created involvements (pending) are only visible to moderators of current profile or the user who created it'
        self.identifier1 = '966b52fe-0e80-435d-bc91-0614f57a3c14'
        self.a1v1 = None
        self.a1v2 = None

        from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
        self.otherProtocol = StakeholderProtocol3(Session)
        self.identifier2 = '5974f7b3-a31d-443e-b994-3f12f8d7c60e'
        self.s1v1 = None
        self.s1v2 = None
        self.invRole1 = self.getStakeholderRole(6)

    def testSetup(self):

        # Make sure the Activity does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity exists already'
        )) is not True:
            return False

        # Create, moderate and check a first Activity
        self.a1v1 = self.createModerateCheckFirstItem(
            self,
            'activities',
            Activity,
            self.getCreateUrl('activities'),
            self.getSomeActivityTags(4, uid=self.identifier1),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created or reviewed.'
        )) is not True:
            return False

        # Make sure the Stakeholder does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier2) == 0,
            'Stakeholder exists already'
        )) is not True:
            return False

        # Create, moderate and check a first Stakeholder
        self.s1v1 = self.createModerateCheckFirstItem(
            self,
            'stakeholders',
            Stakeholder,
            self.getCreateUrl('stakeholders'),
            self.getSomeStakeholderTags(4, uid=self.identifier2),
            self.identifier2,
            self.getUser(1),
            protocol = self.otherProtocol
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Create a new involvement between the two items
        diff = self.getSomeWholeDiff(
            'activities',
            [],
            self.identifier1,
            1,
            'add',
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
            log.debug('Diff to create a1v2:\n%s' % diff)

        # Create the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(3)),
            'New Activity (through involvement) could not be created at all.'
        )) is not True:
            return False

        """
        Basic testing
        """

        # Find the created Activity
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.a1v2 is not None,
            'New Activity (through involvement) was created but not found.'
        )) is not True:
            return False

        # Find the created Stakeholder
        self.s1v2 = self.otherProtocol.read_one_by_version(
            self.request, self.identifier2, 2
        )
        if (self.handleResult(
            self.s1v2 is not None,
            'New Stakeholder (through involvement) was created but not found.'
        )) is not True:
            return False

        # Make sure there really are two versions of each
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 2,
            'There do not exist 2 versions of the Activity'
        )) is not True:
            return False
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier2) == 2,
            'There do not exist 2 versions of the Stakeholder'
        )) is not True:
            return False

        # Make sure the first version is still active
        if (self.handleResult(
            self.a1v1.get_status_id() == 2,
            'The first version of the Activity is not active anymore'
        )) is not True:
            return False
        if (self.handleResult(
            self.s1v1.get_status_id() == 2,
            'The first version of the Stakeholder is not active anymore'
        )) is not True:
            return False

        # Make sure the second version is pending
        if (self.handleResult(
            self.a1v2.get_status_id() == 1,
            'The second version of the Activity is not pending'
        )) is not True:
            return False
        if (self.handleResult(
            self.s1v2.get_status_id() == 1,
            'The second version of the Stakeholder is not pending'
        )) is not True:
            return False

        import requests
        import json
        headers = {'content-type': 'application/json'}

        """
        Public
        """

        # Public:
        session = requests.Session()
        session.auth = ()
        request = session.get( # Explicit
            self.getDetailsUrl('activities', self.identifier1),
            headers=headers
        )

        # Make sure a request to get the details of the Activity can be made
        if (self.handleResult(
            request.status_code == 200,
            'The request to get details of an Activity failed'
        )) is not True:
            return False

        json = request.json()

        # Make sure the response has the correct form
        if (self.handleResult(
            'total' in json and 'data' in json,
            'The response of the request to query an Activity (explicit) does not have the correct form'
        )) is not True:
            return False

        # Public should only see the active Activity
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'The public also sees the pending Activity (explicit) although it should not'
        )) is not True:
            return False
        # Public should not see any involvement
        if (self.handleResult(
            'involvements' not in json['data'][0],
            'The Activity (explicit) the public sees contains involvements when it should not'
        )) is not True:
            return False

        session = requests.Session()
        session.auth = ()
        request = session.get( # Filtered
            self.getFilterUrl('activities', ['Remark'], [self.identifier1]),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'Public does not see only one version of the Activity using a filter to find it.'
        )) is not True:
            return False

        # Public should only see the active Activity when using public query
        # Explicit
        session = requests.Session()
        session.auth = ()
        request = session.get( # Explicit, public query
            self.getDetailsUrl('activities', self.identifier1, public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'Public also sees the pending Activity with public query and querying it explicitely.'
        )) is not True:
            return False

        # Public should only see the active Activity when using public query
        # Filtered
        session = requests.Session()
        session.auth = ()
        request = session.get( # Filtered
            self.getFilterUrl('activities', ['Remark'], [self.identifier1], public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'Public does not see only one version of Activity with public query and using a filter to find it.'
        )) is not True:
            return False

        # Public should only see the active Stakeholder
        # Explicit
        session = requests.Session()
        session.auth = ()
        request = session.get( # Explicit, public query
            self.getDetailsUrl('stakeholders', self.identifier2),
            headers=headers
        )
        # Make sure a request to get the details of the Stakeholder can be made
        if (self.handleResult(
            request.status_code == 200,
            'The request to get details of an Stakeholder failed'
        )) is not True:
            return False
        json = request.json()
        # Make sure the response has the correct form
        if (self.handleResult(
            'total' in json and 'data' in json,
            'The response of the request to query a Stakeholder (explicit) does not have the correct form'
        )) is not True:
            return False
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'The public also sees the pending Stakeholder (explicit) although it should not'
        )) is not True:
            return False
        # Public should not see any involvement
        if (self.handleResult(
            'involvements' not in json['data'][0],
            'The Stakeholder (explicit) the public sees contains involvements when it should not'
        )) is not True:
            return False

        # Public should only see the active Stakeholder
        # Filtered
        session = requests.Session()
        session.auth = ()
        request = session.get( # Filtered
            self.getFilterUrl('stakeholders', ['Address'], [self.identifier2]),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'Public does not see only one version of the Stakeholder using a filter to find it.'
        )) is not True:
            return False

        # Public should only see the active Stakeholder when using public query
        # Explicit
        session = requests.Session()
        session.auth = ()
        request = session.get( # Explicit, public query
            self.getDetailsUrl('stakeholders', self.identifier2, public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'Public also sees the pending Stakeholder with public query and querying it explicitely.'
        )) is not True:
            return False

        # Public should only see the active Stakeholder when using public query
        # Filtered
        session = requests.Session()
        session.auth = ()
        request = session.get( # Filtered
            self.getFilterUrl('stakeholders', ['Address'], [self.identifier2], public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'Public does not see only one version of Stakeholder with public query and using a filter to find it.'
        )) is not True:
            return False

        """
        User 3 (editor who created the Activity).
        Should see the pending Item as well as the pending Involvement.
        """

        # User3 should see both the active and the pending Activity
        # A, explicit
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        request = session.get(
            self.getDetailsUrl('activities', self.identifier1),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 2 and len(json['data']) == 2,
            'User3 does not see 2 Activities (1 pending, 1 active) explicitely'
        )) is not True:
            return False
        if (self.handleResult(
            json['data'][0]['status_id'] == 1,
            'The first Activity User3 sees explicitely is not pending'
        )) is not True:
            return False
        if (self.handleResult(
            'involvements' in json['data'][0],
            'The pending Activity (explicit) User3 sees contains no involvements'
        )) is not True:
            return False

        # User3 should see both the active and the pending Stakeholder
        # SH, explicit
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        request = session.get(
            self.getDetailsUrl('stakeholders', self.identifier2),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 2 and len(json['data']) == 2,
            'User3 does not see 2 Stakeholders (1 pending, 1 active) explicitely'
        )) is not True:
            return False
        if (self.handleResult(
            json['data'][0]['status_id'] == 1,
            'The first Stakeholder User3 sees explicitely is not pending'
        )) is not True:
            return False
        if (self.handleResult(
            'involvements' in json['data'][0],
            'The pending Stakeholder (explicit) User3 sees contains no involvements'
        )) is not True:
            return False

        # User3 should only see the active Activity when using the public query
        # A, explicit, public
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        request = session.get( # Explicit
            self.getDetailsUrl('activities', self.identifier1, public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'User3 does not see only 1 Activity (1 active) explicitely with public query'
        )) is not True:
            return False
        if (self.handleResult(
            json['data'][0]['status_id'] == 2,
            'The first Activity User3 sees explicitely with public query is not active'
        )) is not True:
            return False
        if (self.handleResult(
            'involvements' not in json['data'][0],
            'The Activity (explicit) User3 sees with public query contains involvements'
        )) is not True:
            return False

        # User3 should only see the active Stakeholder when using the public query
        # SH, explicit, public
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        request = session.get( # Explicit
            self.getDetailsUrl('stakeholders', self.identifier2, public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'User3 does not see only 1 Stakeholder (1 active) explicitely with public query'
        )) is not True:
            return False
        if (self.handleResult(
            json['data'][0]['status_id'] == 2,
            'The first Stakeholder User3 sees explicitely with public query is not active'
        )) is not True:
            return False
        if (self.handleResult(
            'involvements' not in json['data'][0],
            'The Stakeholder (explicit) User3 sees with public query contains involvements'
        )) is not True:
            return False

        # User3 should see only the latest pending Activity
        # A, filtered
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        request = session.get(
            self.getFilterUrl('activities', ['Remark'], [self.identifier1]),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'User3 does not see any Activity filtered'
        )) is not True:
            return False
        if (self.handleResult(
            json['data'][0]['status_id'] == 1,
            'The filtered Activity User3 sees is not pending'
        )) is not True:
            return False
        if (self.handleResult(
            'involvements' in json['data'][0],
            'The pending Activity (filtered) User3 sees contains no involvements'
        )) is not True:
            return False

        # User3 should see only the latest pending Stakeholder
        # SH, filtered
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        request = session.get(
            self.getFilterUrl('stakeholders', ['Address'], [self.identifier2]),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'User3 does not see any Stakeholder filtered'
        )) is not True:
            return False
        if (self.handleResult(
            json['data'][0]['status_id'] == 1,
            'The filtered Stakeholder User3 sees is not pending'
        )) is not True:
            return False
        if (self.handleResult(
            'involvements' in json['data'][0],
            'The pending Stakeholder (filtered) User3 sees contains no involvements'
        )) is not True:
            return False

        # User3 should only see the active Activity when using the public query
        # A, filtered, public
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        request = session.get(
            self.getFilterUrl('activities', ['Remark'], [self.identifier1], public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'User3 does not see any Activity filtered with public query'
        )) is not True:
            return False
        if (self.handleResult(
            json['data'][0]['status_id'] == 2,
            'The filtered Activity User3 sees is not active'
        )) is not True:
            return False
        if (self.handleResult(
            'involvements' not in json['data'][0],
            'The Activity (filtered) User3 sees contains an involvement'
        )) is not True:
            return False

        # User3 should only see the active Stakeholder when using the public query
        # SH, filtered, public
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        request = session.get(
            self.getFilterUrl('stakeholders', ['Address'], [self.identifier2], public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'User3 does not see any Stakeholder filtered with public query'
        )) is not True:
            return False
        if (self.handleResult(
            json['data'][0]['status_id'] == 2,
            'The filtered Stakeholder User3 sees is not active'
        )) is not True:
            return False
        if (self.handleResult(
            'involvements' not in json['data'][0],
            'The Stakeholder (filtered) User3 sees contains an involvement'
        )) is not True:
            return False
   

        """
        User 1 (Moderator of Laos profile)
        Should see the pending Item as well as the pending Involvement.
        """
        # User1 should see both the active and the pending Activity
        # A, explicit, Laos
        session = requests.Session()
        user = self.getUser(1)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Laos')
        request = session.get(
            self.getDetailsUrl('activities', self.identifier1),
            headers=headers,
            cookies=cookies
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 2 and len(json['data']) == 2,
            'User1 does not see 2 Activities (1 pending, 1 active) explicitely'
        )) is not True:
            return False
        if (self.handleResult(
            json['data'][0]['status_id'] == 1,
            'The first Activity User1 sees explicitely is not pending'
        )) is not True:
            return False
        if (self.handleResult(
            'involvements' in json['data'][0],
            'The pending Activity (explicit) User1 sees contains no involvements'
        )) is not True:
            return False

        # User1 should only see the pending Activity in the Cambodia profile
        # A, explicit, Cambodia
        session = requests.Session()
        user = self.getUser(1)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Cambodia')
        request = session.get(
            self.getDetailsUrl('activities', self.identifier1),
            headers=headers,
            cookies=cookies
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'User1 in Cambodia profile does not see only the active Activity explicitely'
        )) is not True:
            return False
        if (self.handleResult(
            json['data'][0]['status_id'] == 2,
            'The first Activity User1 sees explicitely in Cambodia profile is not active'
        )) is not True:
            return False
        if (self.handleResult(
            'involvements' not in json['data'][0],
            'The active Activity (explicit) User1 sees in Cambodia profile contains involvements'
        )) is not True:
            return False

        # User1 should see both the active and the pending Stakeholder
        # SH, explicit
        session = requests.Session()
        user = self.getUser(1)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Laos')
        request = session.get(
            self.getDetailsUrl('stakeholders', self.identifier2),
            headers=headers,
            cookies=cookies
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 2 and len(json['data']) == 2,
            'User1 does not see 2 Stakeholders (1 pending, 1 active) explicitely'
        )) is not True:
            return False
        if (self.handleResult(
            json['data'][0]['status_id'] == 1,
            'The first Stakeholder User1 sees explicitely is not pending'
        )) is not True:
            return False
        if (self.handleResult(
            'involvements' in json['data'][0],
            'The pending Stakeholder (explicit) User1 sees contains no involvements'
        )) is not True:
            return False

        # User1 should only see the pending Stakeholder in the Cambodia profile
        # SH, explicit, Cambodia
        session = requests.Session()
        user = self.getUser(1)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Cambodia')
        request = session.get(
            self.getDetailsUrl('stakeholders', self.identifier2),
            headers=headers,
            cookies=cookies
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'User1 in Cambodia profile does not see only the active Stakeholder explicitely'
        )) is not True:
            return False
        if (self.handleResult(
            json['data'][0]['status_id'] == 2,
            'The first Stakeholder User1 sees explicitely in Cambodia profile is not active'
        )) is not True:
            return False
        if (self.handleResult(
            'involvements' not in json['data'][0],
            'The active Stakeholder (explicit) User1 sees in Cambodia profile contains involvements'
        )) is not True:
            return False

        return True

"""
CA 14
"""
class CreateActivities14(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "CA14"
        self.testDescription = 'Freetext values are inserted in the currently selected language'
        self.identifier1 = '573737e3-70e9-43d7-9051-3b00a839ef08'
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
            self.getSomeActivityTags(4, uid=self.identifier1),
            self.identifier1,
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

        cookies = dict(_LOCALE_='fr')
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

        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1 is not None,
            'New Activity was created but not found.'
        )) is not True:
            return False

        # Test the language by doing a database query
        q = Session.query(A_Value).\
            filter(A_Value.fk_language == 3).\
            filter(A_Value.value == self.identifier1)

        if (self.handleResult(
            len(q.all()) == 1,
            'The value in the selected language was not found'
        )) is not True:
            return False

        return True
