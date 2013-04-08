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
            'add'
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
            'add'
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
            'add'
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
            'add'
        )
        
        if verbose is True:
            log.debug('Diff to create a1v1:\n%s' % diff)
        
        # Try to do the create without authentication
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


