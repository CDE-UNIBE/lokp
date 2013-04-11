from lmkp.tests.create.create_base import CreateBase

from lmkp.models.meta import DBSession as Session
from lmkp.models.database_objects import *
from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3

import logging
log = logging.getLogger(__name__)

"""
CS 01
"""
class CreateStakeholders01(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'CS01'
        self.testDescription = 'It is possible to create a new Stakeholder'
        self.identifier1 = 'e6b3168b-2043-443b-83bd-cc0de7dc28c5'
        self.s1v1 = None

    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder exists already'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        diff = self.getSomeWholeDiff(
            'stakeholders',
            self.getSomeStakeholderTags(1),
            self.identifier1,
            1,
            'add'
        )

        if verbose is True:
            log.debug('Diff to create s1v1:\n%s' % diff)

        # Create the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(1)),
            'New Stakeholder could not be created at all.'
        )) is not True:
            return False

        # Find the created Stakeholder
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1 is not None,
            'New Stakeholder was created but not found.'
        )) is not True:
            return False

        # Make sure there is only one version of the Stakeholder
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 1,
            'There was more than one version of the Stakeholder created.'
        )) is not True:
            return False

        # Make sure the Stakeholder has all the taggroups
        if (self.handleResult(
            self.countTaggroups(self.s1v1) == len(self.getSomeStakeholderTags(1)),
            'New Stakeholder has not all taggroups.'
        )) is not True:
            return False

        # Make sure the Stakeholder has status 'pending'
        if (self.handleResult(
            self.s1v1.get_status_id() == 1,
            'New Stakeholder has not status "pending".'
        )) is not True:
            return False

        return True

"""
CS 02
"""
class CreateStakeholders02(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'CS02'
        self.testDescription = 'Only logged in users can create a new Stakeholder'
        self.identifier1 = '9016073e-b22a-47ab-bda4-de138004082c'
        self.s1v1 = None

    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder exists already'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        diff = self.getSomeWholeDiff(
            'stakeholders',
            self.getSomeStakeholderTags(1),
            self.identifier1,
            1,
            'add'
        )

        if verbose is True:
            log.debug('Diff to create s1v1:\n%s' % diff)

        # Try to do the create without authentication
        import requests
        import json
        session = requests.Session()
        session.auth = ()

        headers = {'content-type': 'application/json'}

        request = session.post(
            self.getCreateUrl('stakeholders'),
            data=json.dumps(diff),
            headers=headers
        )

        if (self.handleResult(
            request.status_code == 200,
            'The new Stakeholder was created even when user was not logged in.'
        )) is not True:
            return False

        # Make sure that the Activity was not created
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'There was a version of the Stakeholder created by an anonymous user.'
        )) is not True:
            return False

        return True

"""
CS 03
"""
class CreateStakeholders03(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'CS03'
        self.testDescription = 'New Stakeholders can be created with a specific identifier'
        self.identifier1 = '3aecc37f-d4ad-48dd-95cc-851b4d3d9976'
        self.s1v1 = None

    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder exists already'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        diff = self.getSomeWholeDiff(
            'stakeholders',
            self.getSomeStakeholderTags(1),
            self.identifier1,
            1,
            'add'
        )

        if verbose is True:
            log.debug('Diff to create s1v1:\n%s' % diff)

        # Create the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(1)),
            'New Stakeholder could not be created at all.'
        )) is not True:
            return False

        # Find the created Stakeholder
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1 is not None,
            'New Stakeholder was created but not found.'
        )) is not True:
            return False

        # Make sure there is only one version of the Stakeholder
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 1,
            'There was more than one version of the Stakeholder created.'
        )) is not True:
            return False

        # Make sure the Stakeholder has all the taggroups (7)
        if (self.handleResult(
            self.countTaggroups(self.s1v1) == len(self.getSomeStakeholderTags(1)),
            'New Stakeholder has not all taggroups.'
        )) is not True:
            return False

        return True

"""
CS 04
"""
class CreateStakeholders04(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'CS04'
        self.testDescription = 'New Stakeholders can be created without an identifier'
        self.identifier1 = None
        self.s1v1 = None

    def testSetup(self):
        return True

    def doTest(self, verbose=False):

        diff = self.getSomeWholeDiff(
            'stakeholders',
            self.getSomeStakeholderTags(1),
            None,
            1,
            'add'
        )

        if verbose is True:
            log.debug('Diff to create s1v1:\n%s' % diff)

        import requests
        import json
        session = requests.Session()

        user = self.getUser(1)
        session.auth = (user['username'], user['password'])

        headers = {'content-type': 'application/json'}

        request = session.post(
            self.getCreateUrl('stakeholders'),
            data=json.dumps(diff),
            headers=headers
        )

        if (self.handleResult(
            request.status_code == 201,
            'The new Stakeholder could not be created.'
        )) is not True:
            return False

        json = request.json()

        if (self.handleResult(
            'created' in json and json['created'] is True,
            'Server response ("created") after creating new Stakeholder is not correct.'
        )) is not True:
            return False

        if (self.handleResult(
            'data' in json and len(json['data']) == 1,
            'Server response ("data") after creating new Stakeholder is not correct.'
        )) is not True:
            return False

        data = json['data'][0]
        if (self.handleResult(
            'id' in data,
            'Server response ("id" in data) after creating new Stakeholder is not correct.'
        )) is not True:
            return False

        self.identifier1 = data['id']
        # Try to find the Stakeholder with the newly created uid
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1 is not None,
            'New Stakeholder was created but not found.'
        )) is not True:
            return False

        # Check that there is one (and only one) version
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 1,
            'There is not only one version of the Stakeholder.'
        )) is not True:
            return False

        return True

"""
CS 05
"""
class CreateStakeholders05(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'CS05'
        self.testDescription = 'Mandatory keys are not necessary to create a new Stakeholder'
        self.identifier1 = 'bd074334-c935-4def-b1a1-7691b683bfe4'
        self.s1v1 = None

    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder exists already'
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
            self.getSomeStakeholderTags(3),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created'
        )) is not True:
            return False

        # Not all the mandatory keys are there
        if (self.handleResult(
            (self.findKey(self.s1v1, 'Country of origin') is False),
            'The missing mandatory keys are suddenly there.'
        )) is not True:
            return False

        return True

"""
CS 06
"""
class CreateStakeholders06(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'CS06'
        self.testDescription = 'Inexistent keys (not defined in YAML) cannot be used to create a new Stakeholder'
        self.identifier1 = '9b308612-8940-45bf-917a-3fb244800216'
        self.s1v1 = None

    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder exists already'
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
            'stakeholders',
            tags,
            self.identifier1,
            1,
            'add'
        )

        if verbose is True:
            log.debug('Diff to create s1v1:\n%s' % diff)

        # Try to do the create
        import requests
        import json
        session = requests.Session()

        user = self.getUser(1)
        session.auth = (user['username'], user['password'])

        headers = {'content-type': 'application/json'}

        request = session.post(
            self.getCreateUrl('stakeholders'),
            data=json.dumps(diff),
            headers=headers
        )

        if (self.handleResult(
            request.status_code == 400,
            'The new Stakeholder was created even though it has keys not defined in yaml.'
        )) is not True:
            return False

        # Make sure that the Stakeholder was not created
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'There was a version of the Stakeholder with undefined keys created.'
        )) is not True:
            return False

        return True

"""
CA 07
"""
class CreateStakeholders07(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'CS07'
        self.testDescription = 'New Stakeholders can contain more than one tag per taggroup'
        self.identifier1 = 'c6ffe340-b3ce-4758-8a26-5c0829d92c0c'
        self.s1v1 = None

    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder exists already'
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
            self.getSomeStakeholderTags(2),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created'
        )) is not True:
            return False

        # Make sure the Stakeholder has all the taggroups
        if (self.handleResult(
            self.countTaggroups(self.s1v1) == len(self.getSomeStakeholderTags(2)),
            'New Stakeholder has not all taggroups.'
        )) is not True:
            return False

        # There are more tags than taggroups
        if (self.handleResult(
            self.countTags(self.s1v1) > len(self.getSomeStakeholderTags(2)),
            'New Stakeholder has not more tags than taggroups'
        )) is not True:
            return False

        return True

"""
CS 08
"""
class CreateStakeholders08(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'CS08'
        self.testDescription = 'New Stakeholders can be created with an existing Activity'
        self.identifier1 = 'a3d3ea51-12ac-4830-9609-d03d178bba82'
        self.s1v1 = None

        from lmkp.views.activity_protocol3 import ActivityProtocol3
        self.otherProtocol = ActivityProtocol3(Session)
        self.identifier2 = '360436a5-08a9-4fe2-8472-f93f093954f7'
        self.a1v1 = None
        self.a1v2 = None
        self.invRole1 = self.getStakeholderRole(6)

    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder exists already'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        self.request.cookies['_PROFILE_'] = 'global'

        # Create and check a first Activity
        self.a1v1 = self.createAndCheckFirstItem(
            self,
            'activities',
            Activity,
            self.getCreateUrl('activities'),
            self.getSomeActivityTags(1),
            self.identifier2,
            self.getUser(1),
            geometry = self.getSomeGeometryDiff('Laos'),
            protocol = self.otherProtocol
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created'
        )) is not True:
            return False

        # Make sure the Activity has not involvement
        if (self.handleResult(
            len(self.a1v1.get_involvements()) == 0,
            'Newly created Activity already has an involvement.'
        )) is not True:
            return False

        diff = self.getSomeWholeDiff(
            'stakeholders',
            self.getSomeStakeholderTags(1),
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
            log.debug('Diff to create a1v1:\n%s' % diff)

        # Create the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(1)),
            'New Stakeholder could not be created at all.'
        )) is not True:
            return False

        # Find the created Stakeholder
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1 is not None,
            'New Stakeholder was created but not found.'
        )) is not True:
            return False

        # Make sure there is only one version of the Stakeholder
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 1,
            'There was more than one version of the Stakeholder created.'
        )) is not True:
            return False

        # Make sure the Stakeholder has all the taggroups
        if (self.handleResult(
            self.countTaggroups(self.s1v1) == len(self.getSomeStakeholderTags(1)),
            'New Stakeholder has not all taggroups.'
        )) is not True:
            return False

        # Make sure the Stakeholder has status 'pending'
        if (self.handleResult(
            self.s1v1.get_status_id() == 1,
            'New Stakeholder has not status "pending".'
        )) is not True:
            return False

        # Make sure the first Activity still has no involvement
        if (self.handleResult(
            len(self.a1v1.get_involvements()) == 0,
            'Activity version 1 suddenly has an involvement.'
        )) is not True:
            return False

        # Make sure the first Activity is still pending
        if (self.handleResult(
            self.a1v1.get_status_id() == 1,
            'Activity version 1 is not "pending" anymore.'
        )) is not True:
            return False

        # Make sure the Stakeholder has an involvement
        if (self.handleResult(
            len(self.s1v1.get_involvements()) == 1,
            'Newly created Stakeholder does not have an involvement.'
        )) is not True:
            return False

        # Make sure there was a second version of the Activity created
        self.a1v2 = self.otherProtocol.read_one_by_version(
            self.request, self.identifier2, 2
        )
        if (self.handleResult(
            self.a1v2 is not None,
            'There was no new version of the Activity created.'
        )) is not True:
            return False

        # Make sure the newly created version of the Activity has an involvement
        if (self.handleResult(
            len(self.a1v2.get_involvements()) == 1,
            'Newly created Activity version does not have an involvement.'
        )) is not True:
            return False

        # Make sure the new Activity version is pending
        if (self.handleResult(
            self.a1v2.get_status_id() == 1,
            'Activity version 2 is not "pending".'
        )) is not True:
            return False

        # Make sure the involvements point to the other object
        if (self.handleResult(
            self.s1v1.find_involvement_by_guid(self.identifier2) is not None,
            'Involvement of Stakeholder does not point to correct Activity'
        )) is not True:
            return False
        if (self.handleResult(
            self.a1v2.find_involvement_by_guid(self.identifier1) is not None,
            'Involvement of Activity does not point to correct Stakeholder'
        )) is not True:
            return False
        if (self.handleResult(
            self.s1v1.find_involvement(self.identifier2, self.invRole1['name'], 2) is not None,
            'Involvement of Stakeholder does not point to correct Activity version'
        )) is not True:
            return False
        if (self.handleResult(
            self.a1v2.find_involvement(self.identifier1, self.invRole1['name'], 1) is not None,
            'Involvement of Activity does not point to correct Stakeholder version'
        )) is not True:
            return False

        return True

"""
CS 09
"""
class CreateStakeholders09(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'CS09'
        self.testDescription = 'Creating new Stakeholders without existing Activity creates the Stakeholder but no Involvement'
        self.identifier1 = 'c804ca17-ef12-4801-8f74-782fcc7d75c2'
        self.s1v1 = None

        from lmkp.views.activity_protocol3 import ActivityProtocol3
        self.otherProtocol = ActivityProtocol3(Session)
        self.identifier2 = 'd3dcb940-9ee6-42cd-8172-380dbe746958'
        self.a1v1 = None
        self.invRole1 = self.getStakeholderRole(6)

    def testSetup(self):
        # Make sure the Stakeholder does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder exists already'
        )) is not True:
            return False

        # Make sure the Activity does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier2) == 0,
            'Activity exists already'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        diff = self.getSomeWholeDiff(
            'stakeholders',
            self.getSomeStakeholderTags(1),
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
            log.debug('Diff to create s1v1:\n%s' % diff)

        # Create the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(1)),
            'New Stakeholder could not be created at all.'
        )) is not True:
            return False

        # Find the created Stakeholder
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1 is not None,
            'New Stakeholder was created but not found.'
        )) is not True:
            return False

        # Make sure there is only one version of the Stakeholder
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 1,
            'There was more than one version of the Stakeholder created.'
        )) is not True:
            return False

        # Make sure the Stakeholder has status 'pending'
        if (self.handleResult(
            self.s1v1.get_status_id() == 1,
            'New Stakeholder has not status "pending".'
        )) is not True:
            return False

        # Make sure the Activity was not created
        self.a1v1 = self.otherProtocol.read_one_by_version(
            self.request, self.identifier2, 1
        )
        if (self.handleResult(
            self.a1v1 is None,
            'New Activity was created.'
        )) is not True:
            return False

        # Make sure the Stakeholder has no Involvement
        if (self.handleResult(
            len(self.s1v1.get_involvements()) == 0,
            'The Stakeholder has an involvement.'
        )) is not True:
            return False

        return True

"""
CS 10
"""
class CreateStakeholders10(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'CS10'
        self.testDescription = 'The first tag of a taggroup is treated as the main tag when creating a new Stakeholder'
        self.identifier1 = 'cae4d4e2-ac49-406e-a4c8-17c445716d55'
        self.s1v1 = None

    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder exists already'
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
            self.getSomeStakeholderTags(2),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created'
        )) is not True:
            return False

        # Make sure the Stakeholder has all the taggroups
        if (self.handleResult(
            self.countTaggroups(self.s1v1) == len(self.getSomeStakeholderTags(2)),
            'New Stakeholder has not all taggroups.'
        )) is not True:
            return False

        # There are more tags than taggroups
        if (self.handleResult(
            self.countTags(self.s1v1) > len(self.getSomeStakeholderTags(2)),
            'New Stakeholder has not more tags than taggroups'
        )) is not True:
            return False

        # There is a maintag set for all taggroups
        maintagSet = True
        for tg in self.s1v1.get_taggroups():
            if tg.get_maintag_id() is None:
                maintagSet = False
        if (self.handleResult(
            maintagSet is True,
            'There is not a maintag set for each taggroup'
        )) is not True:
            return False

        # The maintag is a tag of the taggroup
        maintagIsTag = True
        for tg in self.s1v1.get_taggroups():
            if tg.get_tag_by_id(tg.get_maintag_id()) is None:
                maintagIsTag = False
        if (self.handleResult(
            maintagIsTag is True,
            'The maintag set is not one of the tags of the taggroup'
        )) is not True:
            return False

        return True

"""
CS 11
"""
class CreateStakeholders11(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'CS11'
        self.testDescription = 'Newly created Stakeholders (pending) are only visible to all moderators or the user who created it'
        self.identifier1 = '926f8c78-c271-4fdd-b6ea-e35b8eb61661'
        self.s1v1 = None

    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder exists already'
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
            self.getSomeStakeholderTags(4, uid=self.identifier1),
            self.identifier1,
            self.getUser(3)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created'
        )) is not True:
            return False

        import requests
        import json

        """
        Public
        Should not see the pending Item
        """

        session = requests.Session()
        session.auth = ()
        headers = {'content-type': 'application/json'}
        request = session.get( # Explicit
            self.getDetailsUrl('stakeholders', self.identifier1),
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
            'The response of the request to query an Stakeholder (explicit) does not have the correct form'
        )) is not True:
            return False

        # Public should not see the pending Stakeholder
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'The public sees the pending Stakeholder (explicit) although it should not'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = ()
        request = session.get( # Filtered
            self.getFilterUrl('stakeholders', ['Address'], [self.identifier1]),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'The public sees the pending Stakeholder (filtered) although it should not.'
        )) is not True:
            return False

        # Public should not see pending Stakeholder when using public query
        session = requests.Session()
        session.auth = ()
        request = session.get( # Explicit, public query
            self.getDetailsUrl('stakeholders', self.identifier1, public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'Public sees a pending Stakeholder with public query and querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = ()
        request = session.get( # Filtered
            self.getFilterUrl('stakeholders', ['Address'], [self.identifier1], public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'Public sees a pending Stakeholder with public query and using a filter to find it.'
        )) is not True:
            return False

        """
        User 3 (editor who created the Stakeholder)
        Should see the pending Item
        """
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        request = session.get( # Explicit
            self.getDetailsUrl('stakeholders', self.identifier1),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'User 3 (editor of the Stakeholder) does not see his own Stakeholder when querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        request = session.get( # Filtered
            self.getFilterUrl('stakeholders', ['Address'], [self.identifier1]),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'User 3 (editor of the Stakeholder) does not see his own pending Stakeholder when using a filter to find it.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        request = session.get( # Explicit, public query
            self.getDetailsUrl('stakeholders', self.identifier1, public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 3 sees a pending Stakeholder with public query and querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        request = session.get( # Filtered
            self.getFilterUrl('stakeholders', ['Address'], [self.identifier1], public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 3 sees a pending Stakeholder with public query and using a filter to find it.'
        )) is not True:
            return False

        """
        User 1 (moderator of Laos profile)
        Should see the pending Stakeholder, but only in his profile
        """

        session = requests.Session()
        user = self.getUser(1)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Laos')
        request = session.get( # Explicit, with Laos profile
            self.getDetailsUrl('stakeholders', self.identifier1),
            headers=headers,
            cookies=cookies
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'User 1 (Laos moderator) does not see the pending Stakeholder with Laos profile selected and querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        user = self.getUser(1)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Cambodia')
        request = session.get( # Explicit, with Cambodia profile
            self.getDetailsUrl('stakeholders', self.identifier1),
            headers=headers,
            cookies=cookies
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 1 (Laos moderator) sees the pending Stakeholder with Cambodia profile selected and querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Laos')
        request = session.get( # Filtered, with Laos profile
            self.getFilterUrl('stakeholders', ['Address'], [self.identifier1]),
            headers=headers,
            cookies=cookies
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'User 1 (Laos moderator) does not see the pending Stakeholder with Laos profile selected and using a filter to find it.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Cambodia')
        request = session.get( # Filtered, with Cambodia profile
            self.getFilterUrl('stakeholders', ['Address'], [self.identifier1]),
            headers=headers,
            cookies=cookies
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 1 (Laos moderator) sees the pending Stakeholder with Cambodia profile selected and using a filter to find it.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        request = session.get( # Explicit, public query
            self.getDetailsUrl('stakeholders', self.identifier1, public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 1 sees a pending Stakeholder with public query and querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        request = session.get( # Filtered
            self.getFilterUrl('stakeholders', ['Address'], [self.identifier1], public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 1 sees a pending Stakeholder with public query and using a filter to find it.'
        )) is not True:
            return False

        """
        User 4 (other editor)
        Should not see the pending Stakeholder
        """

        session = requests.Session()
        user = self.getUser(4)
        session.auth = (user['username'], user['password'])
        request = session.get( # Explicit
            self.getDetailsUrl('stakeholders', self.identifier1),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 4 sees a pending Stakeholder when querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        request = session.get( # Filtered
            self.getFilterUrl('stakeholders', ['Address'], [self.identifier1]),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 4 sees a pending Stakeholder when using a filter to find it.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        request = session.get( # Explicit, public query
            self.getDetailsUrl('stakeholders', self.identifier1, public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 4 sees a pending Stakeholder with public query and querying it explicitely.'
        )) is not True:
            return False
        session = requests.Session()
        session.auth = (user['username'], user['password'])
        request = session.get( # Filtered
            self.getFilterUrl('stakeholders', ['Address'], [self.identifier1], public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 0 and len(json['data']) == 0,
            'User 4 sees a pending Stakeholder with public query and using a filter to find it.'
        )) is not True:
            return False

        return True

"""
CS 12
"""
class CreateStakeholders12(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'CS12'
        self.testDescription = 'Newly created Involvements (pending) are only visible to all moderators or the user who created it'
        self.identifier1 = '3cf7e9f8-a1f9-41be-9190-c95942a53385'
        self.s1v1 = None
        self.s1v2 = None

        from lmkp.views.activity_protocol3 import ActivityProtocol3
        self.otherProtocol = ActivityProtocol3(Session)
        self.identifier2 = '57706e2d-6eb6-4b4b-a9d2-804d8346c6a8'
        self.a1v1 = None
        self.a1v2 = None
        self.invRole1 = self.getStakeholderRole(6)

    def testSetup(self):

        # Make sure the Stakeholder does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder exists already'
        )) is not True:
            return False

        # Create, moderate and check a first Stakeholder
        self.s1v1 = self.createModerateCheckFirstItem(
            self,
            'stakeholders',
            Stakeholder,
            self.getCreateUrl('stakeholders'),
            self.getSomeStakeholderTags(4, uid=self.identifier1),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created or reviewed.'
        )) is not True:
            return False

        # Make sure the Activity does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier2) == 0,
            'Activity exists already'
        )) is not True:
            return False

        # Create, moderate and check a first Activity
        self.a1v1 = self.createModerateCheckFirstItem(
            self,
            'activities',
            Activity,
            self.getCreateUrl('activities'),
            self.getSomeActivityTags(4, uid=self.identifier2),
            self.identifier2,
            self.getUser(1),
            profile = 'Laos',
            protocol = self.otherProtocol
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Create a new involvement between the two items
        diff = self.getSomeWholeDiff(
            'stakeholders',
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
            log.debug('Diff to create s1v2:\n%s' % diff)

        # Create the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(3)),
            'New Stakeholder (through involvement) could not be created at all.'
        )) is not True:
            return False

        """
        Basic testing
        """

        # Find the created Stakeholder
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.s1v2 is not None,
            'New Stakeholder (through involvement) was created but not found.'
        )) is not True:
            return False

        # Find the created Activity
        self.a1v2 = self.otherProtocol.read_one_by_version(
            self.request, self.identifier2, 2
        )
        if (self.handleResult(
            self.a1v2 is not None,
            'New Activity (through involvement) was created but not found.'
        )) is not True:
            return False

        # Make sure there really are two versions of each
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 2,
            'There do not exist 2 versions of the Stakeholder'
        )) is not True:
            return False
        if (self.handleResult(
            self.countVersions(Activity, self.identifier2) == 2,
            'There do not exist 2 versions of the Activity'
        )) is not True:
            return False

        # Make sure the first version is still active
        if (self.handleResult(
            self.s1v1.get_status_id() == 2,
            'The first version of the Stakeholder is not active anymore'
        )) is not True:
            return False
        if (self.handleResult(
            self.a1v1.get_status_id() == 2,
            'The first version of the Activity is not active anymore'
        )) is not True:
            return False

        # Make sure the second version is pending
        if (self.handleResult(
            self.s1v2.get_status_id() == 1,
            'The second version of the Stakeholder is not pending'
        )) is not True:
            return False
        if (self.handleResult(
            self.a1v2.get_status_id() == 1,
            'The second version of the Activity is not pending'
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
            self.getDetailsUrl('stakeholders', self.identifier1),
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
            'The response of the request to query an Stakeholder (explicit) does not have the correct form'
        )) is not True:
            return False

        # Public should only see the active Stakeholder
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

        session = requests.Session()
        session.auth = ()
        request = session.get( # Filtered
            self.getFilterUrl('stakeholders', ['Address'], [self.identifier1]),
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
            self.getDetailsUrl('stakeholders', self.identifier1, public=True),
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
            self.getFilterUrl('stakeholders', ['Address'], [self.identifier1], public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'Public does not see only one version of Stakeholder with public query and using a filter to find it.'
        )) is not True:
            return False

        # Public should only see the active Activity
        # Explicit
        session = requests.Session()
        session.auth = ()
        request = session.get( # Explicit, public query
            self.getDetailsUrl('activities', self.identifier2),
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
            'The response of the request to query a Activity (explicit) does not have the correct form'
        )) is not True:
            return False
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

        # Public should only see the active Activity
        # Filtered
        session = requests.Session()
        session.auth = ()
        request = session.get( # Filtered
            self.getFilterUrl('activities', ['Remark'], [self.identifier2]),
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
            self.getDetailsUrl('activities', self.identifier2, public=True),
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
            self.getFilterUrl('activities', ['Remark'], [self.identifier2], public=True),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 1 and len(json['data']) == 1,
            'Public does not see only one version of Activity with public query and using a filter to find it.'
        )) is not True:
            return False

        """
        User 3 (editor who created the Stakeholder).
        Should see the pending Item as well as the pending Involvement.
        """

        # User3 should see both the active and the pending Stakeholder
        # SH, explicit
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        request = session.get(
            self.getDetailsUrl('stakeholders', self.identifier1),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 2 and len(json['data']) == 2,
            'User3 does not see 2 Stakeholder (1 pending, 1 active) explicitely'
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

        # User3 should see both the active and the pending Activity
        # SH, explicit
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        request = session.get(
            self.getDetailsUrl('activities', self.identifier2),
            headers=headers
        )
        json = request.json()
        if (self.handleResult(
            json['total'] == 2 and len(json['data']) == 2,
            'User3 does not see 2 Activity (1 pending, 1 active) explicitely'
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

        # User3 should only see the active Stakeholder when using the public query
        # SH, explicit, public
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        request = session.get( # Explicit
            self.getDetailsUrl('stakeholders', self.identifier1, public=True),
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

        # User3 should only see the active Activity when using the public query
        # A, explicit, public
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        request = session.get( # Explicit
            self.getDetailsUrl('activities', self.identifier2, public=True),
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

        # User3 should see only the latest pending Stakeholder
        # SH, filtered
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        request = session.get(
            self.getFilterUrl('stakeholders', ['Address'], [self.identifier1]),
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

        # User3 should see only the latest pending Activity
        # A, filtered
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        request = session.get(
            self.getFilterUrl('activities', ['Remark'], [self.identifier2]),
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

        # User3 should only see the active Stakeholder when using the public query
        # SH, filtered, public
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        request = session.get(
            self.getFilterUrl('stakeholders', ['Address'], [self.identifier1], public=True),
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

        # User3 should only see the active Activity when using the public query
        # A, filtered, public
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        request = session.get(
            self.getFilterUrl('activities', ['Remark'], [self.identifier2], public=True),
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


        """
        User 1 (Moderator of Laos profile)
        Should see the pending Item as well as the pending Involvement.
        """
        # User1 should see both the active and the pending Stakeholder
        # SH, explicit, Laos
        session = requests.Session()
        user = self.getUser(1)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Laos')
        request = session.get(
            self.getDetailsUrl('stakeholders', self.identifier1),
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
            self.getDetailsUrl('stakeholders', self.identifier1),
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

        # User1 should see both the active and the pending Activity
        # A, explicit
        session = requests.Session()
        user = self.getUser(1)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Laos')
        request = session.get(
            self.getDetailsUrl('activities', self.identifier2),
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
            self.getDetailsUrl('activities', self.identifier2),
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

        return True

"""
CS 13
"""
class CreateStakeholders13(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'CS13'
        self.testDescription = 'Freetext values are inserted in the currently selected language'
        self.identifier1 = 'f95d580a-a997-415d-8e0b-aeca44fccd43'
        self.s1v1 = None

    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder exists already'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        diff = self.getSomeWholeDiff(
            'stakeholders',
            self.getSomeStakeholderTags(4, uid=self.identifier1),
            self.identifier1,
            1,
            'add'
        )

        if verbose is True:
            log.debug('Diff to create s1v1:\n%s' % diff)

        import requests
        import json
        session = requests.Session()

        user = self.getUser(1)
        session.auth = (user['username'], user['password'])

        cookies = dict(_LOCALE_='fr')
        headers = {'content-type': 'application/json'}

        request = session.post(
            self.getCreateUrl('stakeholders'),
            data=json.dumps(diff),
            headers=headers,
            cookies=cookies
        )

        if (self.handleResult(
            request.status_code == 201,
            'The new Stakeholder could not be created.'
        )) is not True:
            return False

        json = request.json()

        if (self.handleResult(
            'created' in json and json['created'] is True,
            'Server response ("created") after creating new Stakeholder is not correct.'
        )) is not True:
            return False

        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1 is not None,
            'New Stakeholder was created but not found.'
        )) is not True:
            return False

        # Test the language by doing a database query
        q = Session.query(SH_Value).\
            filter(SH_Value.fk_language == 3).\
            filter(SH_Value.value == self.identifier1)

        if (self.handleResult(
            len(q.all()) == 1,
            'The value in the selected language was not found'
        )) is not True:
            return False

        return True