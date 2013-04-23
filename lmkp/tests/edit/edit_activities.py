from lmkp.tests.create.create_base import CreateBase
from lmkp.tests.moderate.moderation_base import ModerationBase

from lmkp.models.meta import DBSession as Session
from lmkp.models.database_objects import *
from lmkp.views.activity_protocol3 import ActivityProtocol3

import logging
log = logging.getLogger(__name__)

"""
EA 01
"""
class EditActivities01(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'EA01'
        self.testDescription = 'It is possible to edit an Activity'
        self.identifier1 = 'cbe22b14-525a-4578-aa80-df961aa0b747'
        self.a1v1 = None
        self.a1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeActivityTags(1),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        key = 'Intended area (ha)'
        oldValue = 100
        newValue = 50

        # Check that the old value is there
        if (self.handleResult(
            (self.findKeyValue(self.a1v1, key, oldValue) is True and
            self.findKeyValue(self.a1v1, key, newValue) is False),
            'Initial values not correct'
        )) is not True:
            return False

        # Find and check the tg_id
        tg_id = self.findTgidByKeyValue(self.a1v1, key, oldValue)
        if (self.handleResult(
            tg_id is not None,
            'The tg_id of taggroup to update was not found.'
        )) is not True:
            return False

        # Prepare tags
        deleteTags = self.getTagDiffsFromTags({key: oldValue}, 'delete')
        addTags = self.getTagDiffsFromTags({key: newValue}, 'add')

        # Prepare taggroup
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags
        }

        # Put together the diff
        activityDiff = self.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )
        diff = {'activities': [activityDiff]}

        if verbose is True:
            log.debug('Diff to update a1v1:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'The Activity could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier1)
                and self.a1v2 is not None),
            'Version 2 of the updated Activity was not found.'
        )) is not True:
            return False

        # Check that the new Activity has the updated value
        if (self.handleResult(
            (self.findKeyValue(self.a1v2, key, newValue) is True and
            self.findKeyValue(self.a1v2, key, oldValue) is False),
            'Values were not updated correctly.'
        )) is not True:
            return False

        # Check that no additional taggroup was created
        if (self.handleResult(
            self.countTaggroups(self.a1v2) == len(self.getSomeActivityTags(1)),
            'New Activity has not all taggroups.'
        )) is not True:
            return False

        # Check that the new version is pending
        if (self.handleResult(
            self.a1v2.get_status_id() == 1,
            'The updated version of the Activity is not pending.'
        )) is not True:
            return False

        # Check that the old version is still active (query it again)
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 2,
            'The old version of the Activity is not active anymore.'
        )) is not True:
            return False

        return True

"""
EA 02
"""
class EditActivities02(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'EA02'
        self.testDescription = 'Only logged in users can edit an Activity'
        self.identifier1 = 'a810df20-ff53-4005-b5b1-8457df073179'
        self.a1v1 = None
        self.a1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeActivityTags(1),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        key = 'Intended area (ha)'
        oldValue = 100
        newValue = 50

        # Check that the old value is there
        if (self.handleResult(
            (self.findKeyValue(self.a1v1, key, oldValue) is True and
            self.findKeyValue(self.a1v1, key, newValue) is False),
            'Initial values not correct'
        )) is not True:
            return False

        # Find and check the tg_id
        tg_id = self.findTgidByKeyValue(self.a1v1, key, oldValue)
        if (self.handleResult(
            tg_id is not None,
            'The tg_id of taggroup to update was not found.'
        )) is not True:
            return False

        # Prepare tags
        deleteTags = self.getTagDiffsFromTags({key: oldValue}, 'delete')
        addTags = self.getTagDiffsFromTags({key: newValue}, 'add')
        # Prepare taggroup
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags
        }

        # Put together the diff
        activityDiff = self.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )
        diff = {'activities': [activityDiff]}

        if verbose is True:
            log.debug('Diff to update a1v1:\n%s' % diff)

        # Try to do the edit without authentication
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
            'The Activity was edited even when user was not logged in.'
        )) is not True:
            return False

        # Check that no new Activity was created
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.a1v2 is None,
            'There was a second version (created by not logged in user) found'
        )) is not True:
            return False

        # Make sure that there is only 1 version
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 1,
            'There was a edited version of the Activity created by an anonymous user.'
        )) is not True:
            return False

        # Check that the old version is still active (query it again)
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 2,
            'The old version of the Activity is not active anymore.'
        )) is not True:
            return False

        return True

"""
EA 03
"""
class EditActivities03(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'EA03'
        self.testDescription = 'Edit a first pending Activity sets the first version to \'edited\''
        self.identifier1 = '177b8a03-bd2d-49db-aea4-1f27d3912121'
        self.a1v1 = None
        self.a1v2 = None

    def testSetup(self, verbose=False):

        # Create and check a first Activity
        self.a1v1 = self.createAndCheckFirstItem(
            self,
            'activities',
            Activity,
            self.getCreateUrl('activities'),
            self.getSomeActivityTags(1),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )
        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created.'
        )) is not True:
            return False

        # Make sure the Activity is pending
        if (self.handleResult(
            self.a1v1.get_status_id() == 1,
            'First Activity is not pending.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        key = 'Intended area (ha)'
        oldValue = 100
        newValue = 50

        # Check that the old value is there
        if (self.handleResult(
            (self.findKeyValue(self.a1v1, key, oldValue) is True and
            self.findKeyValue(self.a1v1, key, newValue) is False),
            'Initial values not correct'
        )) is not True:
            return False

        # Find and check the tg_id
        tg_id = self.findTgidByKeyValue(self.a1v1, key, oldValue)
        if (self.handleResult(
            tg_id is not None,
            'The tg_id of taggroup to update was not found.'
        )) is not True:
            return False

        # Prepare tags
        deleteTags = self.getTagDiffsFromTags({key: oldValue}, 'delete')
        addTags = self.getTagDiffsFromTags({key: newValue}, 'add')

        # Prepare taggroup
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags
        }

        # Put together the diff
        activityDiff = self.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )
        diff = {'activities': [activityDiff]}

        if verbose is True:
            log.debug('Diff to update a1v1:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'The Activity could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier1)
                and self.a1v2 is not None),
            'Version 2 of the updated Activity was not found.'
        )) is not True:
            return False

        # Check that the new Activity has the updated value
        if (self.handleResult(
            (self.findKeyValue(self.a1v2, key, newValue) is True and
            self.findKeyValue(self.a1v2, key, oldValue) is False),
            'Values were not updated correctly.'
        )) is not True:
            return False

        # Check that no additional taggroup was created
        if (self.handleResult(
            self.countTaggroups(self.a1v2) == len(self.getSomeActivityTags(1)),
            'New Activity has not all taggroups.'
        )) is not True:
            return False

        # Check that the new version is pending
        if (self.handleResult(
            self.a1v2.get_status_id() == 1,
            'The updated version of the Activity is not pending.'
        )) is not True:
            return False

        # Check that the old version is set to 'edited' (query it again)
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 6,
            'The old version of the Activity was not set to edited.'
        )) is not True:
            return False

        return True

"""
EA 04
"""
class EditActivities04(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'EA04'
        self.testDescription = 'Edit two tags of a taggroup of an active Activity'
        self.identifier1 = '5dd1e511-5d33-4cb5-95a1-1a5ada35352b'
        self.a1v1 = None
        self.a1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeActivityTags(2),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        key1 = 'Intention of Investment'
        oldValue1 = 'Conservation'
        newValue1 = 'Agriculture'
        key2 = 'Animals'
        oldValue2 = 'Bees'
        newValue2 = 'Cattle'

        # Check that the old values are there
        if (self.handleResult(
            (self.findKeyValue(self.a1v1, key1, oldValue1) is True and
            self.findKeyValue(self.a1v1, key1, newValue1) is False and
            self.findKeyValue(self.a1v1, key2, oldValue2) is True and
            self.findKeyValue(self.a1v1, key2, newValue2) is False),
            'Initial values not correct'
        )) is not True:
            return False

        # Find and check the tg_id
        tg_id1 = self.findTgidByKeyValue(self.a1v1, key1, oldValue1)
        tg_id2 = self.findTgidByKeyValue(self.a1v1, key2, oldValue2)
        if (self.handleResult(
            tg_id1 is not None and tg_id2 is not None and tg_id1 == tg_id2,
            'The tg_id of taggroup to update was not found.'
        )) is not True:
            return False

        # Prepare tags
        oldTags = {
            key1: oldValue1,
            key2: oldValue2
        }
        deleteTags = self.getTagDiffsFromTags(oldTags, 'delete')
        newTags = {
            key1: newValue1,
            key2: newValue2
        }
        addTags = self.getTagDiffsFromTags(newTags, 'add')

        # Prepare taggroup
        taggroup = {
            'tg_id': tg_id1,
            'tags': deleteTags + addTags
        }

        # Put together the diff
        activityDiff = self.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )
        diff = {'activities': [activityDiff]}

        if verbose is True:
            log.debug('Diff to update a1v1:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'The Activity could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier1)
                and self.a1v2 is not None),
            'Version 2 of the updated Activity was not found.'
        )) is not True:
            return False

        # Check that the new Activity has the updated values
        if (self.handleResult(
            (self.findKeyValue(self.a1v2, key1, newValue1) is True and
            self.findKeyValue(self.a1v2, key1, oldValue1) is False and
            self.findKeyValue(self.a1v2, key2, newValue2) is True and
            self.findKeyValue(self.a1v2, key2, oldValue2) is False),
            'Values were not updated correctly.'
        )) is not True:
            return False

        # Check that the updated values are both in the same taggroup
        tg_id1 = self.findTgidByKeyValue(self.a1v2, key1, newValue1)
        tg_id2 = self.findTgidByKeyValue(self.a1v2, key2, newValue2)
        if (self.handleResult(
            tg_id1 is not None and tg_id2 is not None and tg_id1 == tg_id2,
            'The updated values are not in the same taggroup.'
        )) is not True:
            return False

        # Check that no additional taggroup was created
        if (self.handleResult(
            self.countTaggroups(self.a1v2) == len(self.getSomeActivityTags(2)),
            'New Activity has not all taggroups.'
        )) is not True:
            return False

        # Check that the new version is pending
        if (self.handleResult(
            self.a1v2.get_status_id() == 1,
            'The updated version of the Activity is not pending.'
        )) is not True:
            return False

        # Check that the old version is still active (query it again)
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 2,
            'The old version of the Activity is not active anymore.'
        )) is not True:
            return False

        return True

"""
EA 05
"""
class EditActivities05(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'EA05'
        self.testDescription = 'Add a new Taggroup'
        self.identifier1 = '7529ee0e-fb78-4fe8-9a95-818d0b072856'
        self.a1v1 = None
        self.a1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeActivityTags(1),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        newKey = 'Remark'
        newValue = 'This is a remark'

        diff = self.getSomeWholeDiff(
            'activities',
            [{newKey: newValue}],
            self.identifier1,
            1,
            'add'
        )

        if verbose is True:
            log.debug('Diff to update a1v1:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'The Activity could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier1)
                and self.a1v2 is not None),
            'Version 2 of the updated Activity was not found.'
        )) is not True:
            return False

        # Check that the new Activity has the new value
        if (self.handleResult(
            self.findKeyValue(self.a1v2, newKey, newValue) is True,
            'The key/value of the new taggroup was not found.'
        )) is not True:
            return False

        # Check that the new Activity has a new taggroup
        if (self.handleResult(
            self.countTaggroups(self.a1v2) == len(self.getSomeActivityTags(1))+1,
            'New Activity has not all taggroups.'
        )) is not True:
            return False

        # Check that the new version is pending
        if (self.handleResult(
            self.a1v2.get_status_id() == 1,
            'The updated version of the Activity is not pending.'
        )) is not True:
            return False

        # Check that the old version is still active (query it again)
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 2,
            'The old version of the Activity is not active anymore.'
        )) is not True:
            return False
        
        return True

"""
EA 06
"""
class EditActivities06(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'EA06'
        self.testDescription = 'Add a new Tag to a Taggroup'
        self.identifier1 = '41cb0d0e-3f3e-433a-b587-6dee49ece8be'
        self.a1v1 = None
        self.a1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeActivityTags(2),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        newKey = 'Remark'
        newValue = 'This is a remark'
        inTaggroupWithKey = 'Spatial Accuracy'
        inTaggroupWithValue = '1km to 10km'

        # Find and check the tg_id
        tg_id = self.findTgidByKeyValue(self.a1v1, inTaggroupWithKey, inTaggroupWithValue)
        if (self.handleResult(
            tg_id is not None,
            'The tg_id of taggroup to update was not found.'
        )) is not True:
            return False

        # Prepare tags
        addTags = self.getTagDiffsFromTags({newKey: newValue}, 'add')
        # Prepare taggroup
        taggroup = {
            'tg_id': tg_id,
            'tags': addTags
        }

        # Put together the diff
        activityDiff = self.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )
        diff = {'activities': [activityDiff]}

        if verbose is True:
            log.debug('Diff to update a1v1:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'The Activity could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier1)
                and self.a1v2 is not None),
            'Version 2 of the updated Activity was not found.'
        )) is not True:
            return False

        # Check that the new Activity has the new value
        if (self.handleResult(
            self.findKeyValue(self.a1v2, newKey, newValue) is True,
            'The key/value of the new taggroup was not found.'
        )) is not True:
            return False

        # Check that the new Activity still has the same number of taggroups
        if (self.handleResult(
            self.countTaggroups(self.a1v2) == len(self.getSomeActivityTags(2)),
            'New Activity has not all taggroups.'
        )) is not True:
            return False

        # Check that the Tag was inserted in the correct taggroup
        if (self.handleResult(
            tg_id == self.findTgidByKeyValue(self.a1v2, newKey, newValue),
            'The new tag was not inserted in the correct taggroup'
        )) is not True:
            return False

        # Check that the new version is pending
        if (self.handleResult(
            self.a1v2.get_status_id() == 1,
            'The updated version of the Activity is not pending.'
        )) is not True:
            return False

        # Check that the old version is still active (query it again)
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 2,
            'The old version of the Activity is not active anymore.'
        )) is not True:
            return False

        return True

"""
EA 07
"""
class EditActivities07(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'EA07'
        self.testDescription = 'Delete a Taggroup'
        self.identifier1 = '2d3fd552-81f6-4fe2-b47f-b468e53fd78b'
        self.a1v1 = None
        self.a1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeActivityTags(2),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        oldKey = 'Spatial Accuracy'
        oldValue = '1km to 10km'

        # The tg_id needs to be known!

        # Find and check the tg_id
        tg_id = self.findTgidByKeyValue(self.a1v1, oldKey, oldValue)
        if (self.handleResult(
            tg_id is not None,
            'The tg_id of taggroup to delete was not found.'
        )) is not True:
            return False

        # Prepare tags
        deleteTags = self.getTagDiffsFromTags({oldKey: oldValue}, 'delete')
        # Prepare taggroup
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags,
            'op': 'delete'
        }

        # Put together the diff
        activityDiff = self.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )
        diff = {'activities': [activityDiff]}

        if verbose is True:
            log.debug('Diff to update a1v1:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'The Activity could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier1)
                and self.a1v2 is not None),
            'Version 2 of the updated Activity was not found.'
        )) is not True:
            return False

        # Check that the new Activity does not have the old value anymore
        if (self.handleResult(
            self.findKeyValue(self.a1v2, oldKey, oldValue) is not True,
            'The key/value of the new taggroup still found.'
        )) is not True:
            return False

        # Check that the new Activity does not have the same number of taggroups anymore
        if (self.handleResult(
            self.countTaggroups(self.a1v2) == len(self.getSomeActivityTags(2))-1,
            'New Activity has not all taggroups.'
        )) is not True:
            return False

        # Check that the new version is pending
        if (self.handleResult(
            self.a1v2.get_status_id() == 1,
            'The updated version of the Activity is not pending.'
        )) is not True:
            return False

        # Check that the old version is still active (query it again)
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 2,
            'The old version of the Activity is not active anymore.'
        )) is not True:
            return False

        return True

"""
EA 08
"""
class EditActivities08(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'EA08'
        self.testDescription = 'Delete a Tag of a Taggroup'
        self.identifier1 = '33320812-23bf-4f89-a6e9-7864cf4c6e5c'
        self.a1v1 = None
        self.a1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeActivityTags(2),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        oldKey = 'Negotiation Status'
        oldValue = 'Oral agreement'

        # The tg_id needs to be known!

        # Find and check the tg_id
        tg_id = self.findTgidByKeyValue(self.a1v1, oldKey, oldValue)
        if (self.handleResult(
            tg_id is not None,
            'The tg_id of taggroup to delete was not found.'
        )) is not True:
            return False

        # Prepare tags
        deleteTags = self.getTagDiffsFromTags({oldKey: oldValue}, 'delete')
        # Prepare taggroup
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags,
            'op': 'delete'
        }

        # Put together the diff
        activityDiff = self.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )
        diff = {'activities': [activityDiff]}

        if verbose is True:
            log.debug('Diff to update a1v1:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'The Activity could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier1)
                and self.a1v2 is not None),
            'Version 2 of the updated Activity was not found.'
        )) is not True:
            return False

        # Check that the new Activity does not have the old value anymore
        if (self.handleResult(
            self.findKeyValue(self.a1v2, oldKey, oldValue) is not True,
            'The key/value of the new taggroup still found.'
        )) is not True:
            return False

        # Check that the new Activity does still have the same number of taggroups
        if (self.handleResult(
            self.countTaggroups(self.a1v2) == len(self.getSomeActivityTags(2)),
            'New Activity has not all taggroups.'
        )) is not True:
            return False

        # Check that the new version is pending
        if (self.handleResult(
            self.a1v2.get_status_id() == 1,
            'The updated version of the Activity is not pending.'
        )) is not True:
            return False

        # Check that the old version is still active (query it again)
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 2,
            'The old version of the Activity is not active anymore.'
        )) is not True:
            return False

        return True

"""
EA 09
"""
class EditActivities09(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'EA09'
        self.testDescription = 'Add an Involvement'
        self.identifier1 = 'b6a9c634-e42a-46f1-b5b0-129ca7c37106'
        self.a1v1 = None
        self.a1v2 = None

        from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
        self.otherProtocol = StakeholderProtocol3(Session)
        self.identifier2 = 'b5a9f8de-9230-4051-9471-3c5648c0da00'
        self.s1v1 = None
        self.invRole1 = self.getStakeholderRole(6)

    def testSetup(self, verbose=False):

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
            self.getSomeActivityTags(1),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Create a Stakeholder to do an edit on the Activity
        diff = self.getSomeWholeDiff(
            'stakeholders',
            self.getSomeStakeholderTags(1),
            self.identifier2,
            1,
            'add',
            involvements = [
                {
                    'id': self.identifier1,
                    'version': 1,
                    'role': self.invRole1['id'],
                    'op': 'add'
                }
            ]
        )

        if verbose is True:
            log.debug('Diff to update a1v1:\n%s' % diff)

        # Create the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(3)),
            'The Stakeholder could not be created.'
        )) is not True:
            return False

        # Check that the Stakeholder was created
        self.s1v1 = self.otherProtocol.read_one_by_version(
            self.request, self.identifier2, 1
        )
        if (self.handleResult(
            self.s1v1 is not None,
            'The Stakeholder was not created'
        )) is not True:
            return False
        if (self.handleResult(
            self.s1v1.get_status_id() == 1,
            'The created Stakeholder is not pending'
        )) is not True:
            return False

        # Check that the Stakeholder has an involvement
        if (self.handleResult(
            len(self.s1v1.get_involvements()) == 1,
            'The Stakeholder does not have an Involvement'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier1)
                and self.a1v2 is not None),
            'Version 2 of the updated Activity was not found.'
        )) is not True:
            return False

        # Check that the new Activity has an involvement
        if (self.handleResult(
            len(self.a1v2.get_involvements()) == 1,
            'Activity v2 does not have an Involvement'
        )) is not True:
            return False

        return True

"""
EA 10
"""
class EditActivities10(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'EA10'
        self.testDescription = 'Delete an Involvement'
        self.identifier1 = 'ab38c573-c6f9-4b25-9362-bdc0a5e3bfbe'
        self.a1v1 = None
        self.a1v2 = None
        self.a1v3 = None

        from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
        self.otherProtocol = StakeholderProtocol3(Session)
        self.identifier2 = 'ab028931-3a36-4255-8463-a3f25b1f0e0c'
        self.s1v1 = None
        self.s1v2 = None
        self.s1v3 = None
        self.invRole1 = self.getStakeholderRole(6)

        self.moderationBase = ModerationBase()

    def testSetup(self, verbose=False):

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
            self.getSomeActivityTags(1),
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
            self.getSomeStakeholderTags(1),
            self.identifier2,
            self.getUser(1),
            protocol = self.otherProtocol
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created or reviewed.'
        )) is not True:
            return False

        # Create a new Involvement
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

        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'New Activity (with involvement) could not be created at all.'
        )) is not True:
            return False

        # Review the Activity (this will also review the Stakeholder)
        if (self.handleResult(
            self.moderationBase.doReview(
                'activities', self.identifier1, 2, 1
            ) is True,
            'The Activity (with involvement) could not be reviewed.'
        )) is not True:
            return False

        # Find the created Activity
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.a1v2 is not None,
            'New Activity (with involvement) was created but not found.'
        )) is not True:
            return False

        # Make sure it is active
        if (self.handleResult(
            self.a1v2.get_status_id() == 2,
            'New Activity (with involvement) is not active after review.'
        )) is not True:
            return False

        # Find the created Stakeholder
        self.s1v2 = self.otherProtocol.read_one_by_version(
            self.request, self.identifier2, 2
        )
        if (self.handleResult(
            self.s1v2 is not None,
            'New Stakeholder (with involvement) was created but not found.'
        )) is not True:
            return False

        # Make sure it is active
        if (self.handleResult(
            self.s1v2.get_status_id() == 2,
            'New Stakeholder (with involvement) is not active after review.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Create a Stakeholder to do an edit on the Activity
        diff = self.getSomeWholeDiff(
            'activities',
            [],
            self.identifier1,
            2,
            'add',
            involvements = [
                {
                    'id': self.identifier2,
                    'version': 2,
                    'role': self.invRole1['id'],
                    'op': 'delete'
                }
            ]
        )

        if verbose is True:
            log.debug('Diff to update a1v2:\n%s' % diff)

        # Create the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(3)),
            'The Activity (without Involvement) could not be created.'
        )) is not True:
            return False

        # Check that the Activity was created
        self.a1v3 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 3
        )
        if (self.handleResult(
            self.a1v3 is not None,
            'The Activity (without Involvement) was not created'
        )) is not True:
            return False
        if (self.handleResult(
            self.a1v3.get_status_id() == 1,
            'The created Activity (without Involvement) is not pending'
        )) is not True:
            return False

        # Check that the Activity has no involvement
        if (self.handleResult(
            len(self.a1v3.get_involvements()) == 0,
            'The Activity (without Involvement) still has an Involvement'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s1v3 = self.otherProtocol.read_one_by_version(
            self.request, self.identifier2, 3
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier2)
                and self.s1v3 is not None),
            'Version 3 of the updated Stakeholder (without Involvement) was not found.'
        )) is not True:
            return False

        # Check that the new Stakeholder has an involvement
        if (self.handleResult(
            len(self.a1v3.get_involvements()) == 0,
            'Stakeholder (without Involvement) does have an Involvement'
        )) is not True:
            return False

        return True

"""
EA 11
"""
class EditActivities11(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'EA11'
        self.testDescription = 'Delete the Maintag of a Taggroup'
        self.identifier1 = '553c89f6-9083-40bb-b65a-8c17e90b8c09'
        self.a1v1 = None
        self.a1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeActivityTags(2),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        oldKey = 'Current area in operation (ha)'
        oldValue = 50
        otherKey = 'Negotiation Status'
        otherValue = 'Oral agreement'

        # The tg_id needs to be known!

        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.a1v1, oldKey, oldValue)
        if (self.handleResult(
            tg_id is not None,
            'The tg_id of taggroup to delete was not found.'
        )) is not True:
            return False

        # Get the taggroup with this tg_id
        taggroup = self.a1v1.find_taggroup_by_tg_id(tg_id)

        # Get the main tag of this taggroup
        maintag = taggroup.get_tag_by_id(taggroup.get_maintag_id())

        # Make sure the values to change are the maintag
        if (self.handleResult(
            maintag.get_value() == str(oldValue) and maintag.get_key() == str(oldKey),
            'The tag to remove is not the maintag'
        )) is not True:
            return False

        # Prepare the diff
        deleteTags = self.getTagDiffsFromTags({oldKey: oldValue}, 'delete')
        # Prepare taggroup
        taggroupDiff = {
            'tg_id': tg_id,
            'tags': deleteTags,
            'op': 'delete'
        }
        # Put together the diff
        activityDiff = self.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroupDiff]
        )
        diff = {'activities': [activityDiff]}

        if verbose is True:
            log.debug('Diff to update a1v1:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'The Activity could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier1)
                and self.a1v2 is not None),
            'Version 2 of the updated Activity was not found.'
        )) is not True:
            return False

        # Check that the new Activity does not have the old value anymore
        if (self.handleResult(
            self.findKeyValue(self.a1v2, oldKey, oldValue) is not True,
            'The key/value of the new taggroup still found.'
        )) is not True:
            return False

        # Check the new maintag
        # Get the taggroup with this tg_id
        taggroup2 = self.a1v2.find_taggroup_by_tg_id(tg_id)

        # Get the main tag of this taggroup
        maintag2 = taggroup2.get_tag_by_id(taggroup2.get_maintag_id())

        # Check that the new Activity does not have the old value anymore
        if (self.handleResult(
            maintag2 is not None,
            'The new Activity does not have a maintag anymore'
        )) is not True:
            return False

        # Make sure the new main tag is the other tag remaining in the taggroup
        if (self.handleResult(
            maintag2.get_key() == otherKey and maintag2.get_value() == otherValue,
            'The new Activity has a wrong maintag'
        )) is not True:
            return False

        return True

"""
EA 12
"""
class EditActivities12(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'EA12'
        self.testDescription = 'Edit a Maintag'
        self.identifier1 = '572a388f-7c14-48c0-b3b3-ad9bf09b6526'
        self.a1v1 = None
        self.a1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeActivityTags(2),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        key = 'Intention of Investment'
        oldValue = 'Conservation'
        newValue = 'Agriculture'

        # The tg_id needs to be known!

        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.a1v1, key, oldValue)
        if (self.handleResult(
            tg_id is not None,
            'The tg_id of taggroup to change was not found.'
        )) is not True:
            return False

        # Get the taggroup with this tg_id
        taggroup = self.a1v1.find_taggroup_by_tg_id(tg_id)

        # Get the main tag of this taggroup
        maintag = taggroup.get_tag_by_id(taggroup.get_maintag_id())

        # Make sure the values to change are the maintag
        if (self.handleResult(
            maintag.get_value() == str(oldValue) and maintag.get_key() == str(key),
            'The tag to change is not the maintag'
        )) is not True:
            return False

        # Prepare the diff
        deleteTags = self.getTagDiffsFromTags({key: oldValue}, 'delete')
        addTags = self.getTagDiffsFromTags({key: newValue}, 'add')

        mainTag = {
            'key': key,
            'value': newValue
        }

        # Prepare taggroup
        taggroupDiff = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags,
            'main_tag': mainTag
        }
        # Put together the diff
        activityDiff = self.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroupDiff]
        )
        diff = {'activities': [activityDiff]}

        if verbose is True:
            log.debug('Diff to update a1v1:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'The Activity could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier1)
                and self.a1v2 is not None),
            'Version 2 of the updated Activity was not found.'
        )) is not True:
            return False

        # Check that the new Activity does not have the old value anymore
        if (self.handleResult(
            self.findKeyValue(self.a1v2, key, oldValue) is not True,
            'The value of the old taggroup was still found.'
        )) is not True:
            return False

        # Check the new maintag
        # Get the taggroup with this tg_id
        taggroup2 = self.a1v2.find_taggroup_by_tg_id(tg_id)

        # Get the main tag of this taggroup
        maintag2 = taggroup2.get_tag_by_id(taggroup2.get_maintag_id())

        # Check that the new Activity does not have the old value anymore
        if (self.handleResult(
            maintag2 is not None,
            'The new Activity does not have a maintag anymore'
        )) is not True:
            return False

        # Make sure the new main tag is the newly set tag
        if (self.handleResult(
            maintag2.get_key() == key and maintag2.get_value() == newValue,
            'The new Activity has a wrong maintag'
        )) is not True:
            return False

        return True

"""
EA 13
"""
class EditActivities13(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'EA13'
        self.testDescription = 'Edit the geometry of an Activity'
        self.identifier1 = 'e8b043c4-9d6c-46a6-9642-0d2176c4d867'
        self.a1v1 = None
        self.a1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeActivityTags(1),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Save the old geometry
        oldGeom = wkb.loads(str(self.a1v1.get_geometry().geom_wkb))

        # Create a new geometry
        newGeometry = self.getSomeGeometryDiff('Laos')

        # Make sure the new geometry is not the old one
        if (self.handleResult(
            newGeometry['coordinates'][0] != oldGeom.x and newGeometry['coordinates'][1] != oldGeom.y,
            'The newly created geometry is the same as the old one'
        )) is not True:
            return False

        # Put together the diff
        activityDiff = self.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 1,
            geometry = newGeometry
        )
        diff = {'activities': [activityDiff]}

        if verbose is True:
            log.debug('Diff to update a1v1:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'The Activity could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier1)
                and self.a1v2 is not None),
            'Version 2 of the updated Activity was not found.'
        )) is not True:
            return False
        
        # Check that the new Activity does not have the old geomtry anymore
        newGeom = wkb.loads(str(self.a1v2.get_geometry().geom_wkb))
        if (self.handleResult(
            newGeom.x != oldGeom.x and newGeom.y != oldGeom.y,
            'The new Activity still has the old geometry'
        )) is not True:
            return False

        return True

"""
EA 14
"""
class EditActivities14(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'EA14'
        self.testDescription = 'Delete an Activity'
        self.identifier1 = '100182e3-ee29-4cba-861e-9d68e3360352'
        self.a1v1 = None
        self.a1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeActivityTags(1),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        diff = self.getSomeWholeDiff(
            'activities',
            self.getSomeActivityTags(1),
            self.identifier1,
            1,
            'delete',
            setMaintags = False,
            addTgids = True
        )

        if verbose is True:
            log.debug('Diff to update a1v1:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'The Activity could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier1)
                and self.a1v2 is not None),
            'Version 2 of the updated Activity was not found.'
        )) is not True:
            return False

        # Check that the new Activity only has one (empty) taggroup
        if (self.handleResult(
            len(self.a1v2.get_taggroups()) == 1,
            'Version 2 does not only have one (empty) taggroup'
        )) is not True:
            return False

        # Check that the taggroup only has one (empty) tag
        tg = self.a1v2.get_taggroups()[0]
        if (self.handleResult(
            len(tg.get_tags()) == 1,
            'The taggroup of version 2 does not only have one (empty) tag'
        )) is not True:
            return False

        # Check that the tag only has empty key and value
        t = tg.get_tags()[0]
        if (self.handleResult(
            t.get_key() is None and t.get_value() is None,
            'The tag of version 2 is not empty'
        )) is not True:
            return False

        return True

"""
EA 15
"""
class EditActivities15(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'EA15'
        self.testDescription = 'Edit a own pending Activity sets it to "edited"'
        self.identifier1 = '473e58b4-3b36-4e81-ad48-e213738def98'
        self.a1v1 = None
        self.a1v2 = None
        self.a1v3 = None

    def testSetup(self, vebose=False):

        # Make sure the Activity does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity exists already'
        )) is not True:
            return False

        # Create, moderate and check Activity
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

        return True

    def doTest(self, verbose=False):

        # The values to change
        key1 = 'Intention of Investment'
        oldValue1 = 'Agriculture'
        newValue1 = 'Mining'

        key2 = 'Intended area (ha)'
        oldValue2 = 100
        newValue2 = 50

        """
        v2
        """
        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.a1v1, key1, oldValue1)
        if (self.handleResult(
            tg_id is not None,
            'The tg_id of taggroup to change was not found.'
        )) is not True:
            return False

        # Prepare the diff
        deleteTags = self.getTagDiffsFromTags({key1: oldValue1}, 'delete')
        addTags = self.getTagDiffsFromTags({key1: newValue1}, 'add')
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags
        }
        diff = {'activities': [self.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update a1v1:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'The Activity could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier1)
                and self.a1v2 is not None),
            'Version 2 of the updated Activity was not found.'
        )) is not True:
            return False

        """
        v3
        """
        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.a1v2, key2, oldValue2)
        if (self.handleResult(
            tg_id is not None,
            'The tg_id of taggroup to change was not found.'
        )) is not True:
            return False

        # Prepare the diff
        deleteTags = self.getTagDiffsFromTags({key2: oldValue2}, 'delete')
        addTags = self.getTagDiffsFromTags({key2: newValue2}, 'add')
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags
        }
        diff = {'activities': [self.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 2,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update a1v2:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'The Activity could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v3 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 3
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier1)
                and self.a1v3 is not None),
            'Version 3 of the updated Activity was not found.'
        )) is not True:
            return False

        # Re-query v2
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )

        # Check that the status of v2 is not 'edited'
        if (self.handleResult(
            self.a1v2.get_status_id() == 6,
            'The status of version 2 is not "edited"'
        )) is not True:
            return False

        # Check that the status of v3 is 'pending'
        if (self.handleResult(
            self.a1v3.get_status_id() == 1,
            'The status of version 3 is not "pending"'
        )) is not True:
            return False

        # Check that v2 does contain the first change
        if (self.handleResult(
            (self.findKeyValue(self.a1v2, key1, oldValue1) is False and
                self.findKeyValue(self.a1v2, key1, newValue1) is True),
            'The new value of v2 was not correctly set'
        )) is not True:
            return False

        # Check that v2 does not contain the second change
        if (self.handleResult(
            (self.findKeyValue(self.a1v2, key2, oldValue2) is True and
                self.findKeyValue(self.a1v2, key2, newValue2) is False),
            'Version 2 also contains the second change'
        )) is not True:
            return False

        # Check that v3 contains both changes
        if (self.handleResult(
            (self.findKeyValue(self.a1v3, key1, oldValue1) is False and
                self.findKeyValue(self.a1v3, key1, newValue1) is True),
            'Version 3 does not contain the changes made to version 2'
        )) is not True:
            return False

        # Check that v3 contains both changes
        if (self.handleResult(
            (self.findKeyValue(self.a1v3, key2, oldValue2) is False and
                self.findKeyValue(self.a1v3, key2, newValue2) is True),
            'Version 3 does not contain the changes made to version 3'
        )) is not True:
            return False

        return True

"""
EA 16
"""
class EditActivities16(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'EA16'
        self.testDescription = 'Edits by different users are based on the active version'
        self.identifier1 = '73011e3b-39b5-490f-a4fa-f8ca7f073f82'
        self.a1v1 = None
        self.a1v2 = None
        self.a1v3 = None

    def testSetup(self, vebose=False):

        # Make sure the Activity does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity exists already'
        )) is not True:
            return False

        # Create, moderate and check Activity
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

        return True

    def doTest(self, verbose=False):

        # The values to change
        key1 = 'Intention of Investment'
        oldValue1 = 'Agriculture'
        newValue1 = 'Mining'

        key2 = 'Intended area (ha)'
        oldValue2 = 100
        newValue2 = 50

        """
        v2 (by user 2 > based on v1)
        """
        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.a1v1, key1, oldValue1)
        if (self.handleResult(
            tg_id is not None,
            'The tg_id of taggroup to change was not found.'
        )) is not True:
            return False

        # Prepare the diff
        deleteTags = self.getTagDiffsFromTags({key1: oldValue1}, 'delete')
        addTags = self.getTagDiffsFromTags({key1: newValue1}, 'add')
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags
        }
        diff = {'activities': [self.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update a1v1:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(2)),
            'The Activity could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier1)
                and self.a1v2 is not None),
            'Version 2 of the updated Activity was not found.'
        )) is not True:
            return False

        """
        v3 (by user 3 > based on v1)
        """
        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.a1v1, key2, oldValue2)
        if (self.handleResult(
            tg_id is not None,
            'The tg_id of taggroup to change was not found.'
        )) is not True:
            return False

        # Prepare the diff
        deleteTags = self.getTagDiffsFromTags({key2: oldValue2}, 'delete')
        addTags = self.getTagDiffsFromTags({key2: newValue2}, 'add')
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags
        }
        diff = {'activities': [self.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update a1v2:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(3)),
            'The Activity could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v3 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 3
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier1)
                and self.a1v3 is not None),
            'Version 3 of the updated Activity was not found.'
        )) is not True:
            return False

        # Re-query v2
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )

        # Check that the status of v2 is 'pending'
        if (self.handleResult(
            self.a1v2.get_status_id() == 1,
            'The status of version 2 is not "pending"'
        )) is not True:
            return False

        # Check that the status of v3 is 'pending'
        if (self.handleResult(
            self.a1v3.get_status_id() == 1,
            'The status of version 3 is not "pending"'
        )) is not True:
            return False

        # Check that v2 does contain only the first change
        if (self.handleResult(
            (self.findKeyValue(self.a1v2, key1, oldValue1) is False and
                self.findKeyValue(self.a1v2, key1, newValue1) is True),
            'Version 2 does not contain the changes made by user 2'
        )) is not True:
            return False

        # Check that v2 does not contain the second change
        if (self.handleResult(
            (self.findKeyValue(self.a1v2, key2, oldValue2) is True and
                self.findKeyValue(self.a1v2, key2, newValue2) is False),
            'Version 2 also contains the second change'
        )) is not True:
            return False

        # Check that v3 does contain only the second change
        if (self.handleResult(
            (self.findKeyValue(self.a1v3, key1, oldValue1) is True and
                self.findKeyValue(self.a1v3, key1, newValue1) is False),
            'Version 3 also contains the changes made by user 2'
        )) is not True:
            return False

        # Check that v3 contains both changes
        if (self.handleResult(
            (self.findKeyValue(self.a1v3, key2, oldValue2) is False and
                self.findKeyValue(self.a1v3, key2, newValue2) is True),
            'Version 3 does not contain the changes made by user 3'
        )) is not True:
            return False

        return True

"""
EA 17
"""
class EditActivities17(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'EA17'
        self.testDescription = 'Edit the geometry of a Taggroup'
        self.identifier1 = '877cb800-ab4f-11e2-9e96-0800200c9ad2'
        self.a1v1 = None
        self.a1v2 = None
        self.a1v3 = None
        self.a1v4 = None
        self.a1v5 = None
        self.a1v6 = None

        self.moderationBase = ModerationBase()
        self.coords1 = [
            [102.0, 19.4], [102.1, 19.4], [102.1, 19.5], [102.0, 19.5], [102.0, 19.4]
        ]
        self.geom1 = None
        self.coords2 = [
            [102.2, 19.6], [102.3, 19.6], [102.3, 19.7], [102.2, 19.7], [102.2, 19.6]
        ]
        self.geom2 = None

        self.coords3 = [
            [102.4, 19.8], [102.5, 19.8], [102.5, 19.9], [102.4, 19.9], [102.4, 19.8]
        ]
        self.key3 = 'Intended area (ha)'
        self.oldValue3 = 100
        self.newValue3 = 200
        self.geom3 = None

        self.key4 = 'Intended area (ha)'
        self.oldValue4 = 200
        self.newValue4 = 300

        self.key5 = 'Intention of Investment'
        self.oldValue5 = 'Agriculture'
        self.newValue5 = 'Forestry'

    def testSetup(self, verbose=False):

        # Make sure the Activity does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity exists already'
        )) is not True:
            return False

        # Create, moderate and check a first Activity with a geometry in
        # taggroup with tg_id = 3
        diff = {
            'activities': [
                {
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [102.0598997729745, 19.421453614541]
                    },
                    'taggroups': [
                        {
                            'main_tag': {
                                'value': 'Laos',
                                'key': 'Country'
                            },
                            'tags': [
                                {
                                    'value': 'Laos',
                                    'key': 'Country',
                                    'op': 'add'
                                }
                            ],
                            'op': 'add'
                        }, {
                            'main_tag': {
                                'value': 'Contract',
                                'key': 'Data source'
                            },
                            'tags': [
                                {
                                    'value': 'Contract',
                                    'key': 'Data source',
                                    'op': 'add'
                                }
                            ],
                            'op': 'add'
                        }, {
                            'main_tag': {
                                'value': 100,
                                'key': 'Intended area (ha)'
                            },
                            'tags': [
                                {
                                    'value': 100,
                                    'key': 'Intended area (ha)',
                                    'op': 'add'
                                }
                            ],
                            'op': 'add',
                            'geometry': {
                                'type': 'Polygon',
                                'coordinates': [
                                    self.coords1
                                ]
                            }
                        }, {
                            'main_tag': {
                                'value': 'Agriculture',
                                'key': 'Intention of Investment'
                            },
                            'tags': [
                                {
                                    'value': 'Agriculture',
                                    'key': 'Intention of Investment',
                                    'op': 'add'
                                }
                            ],
                            'op': 'add'
                        }, {
                            'main_tag': {
                                'value': 'Contract signed',
                                'key': 'Negotiation Status'
                            },
                            'tags': [
                                {
                                    'value': 'Contract signed',
                                    'key': 'Negotiation Status',
                                    'op': 'add'
                                }
                            ],
                            'op': 'add'
                        }, {
                            'main_tag': {
                                'value': '100m to 1km',
                                'key': 'Spatial Accuracy'
                            },
                            'tags': [
                                {
                                    'value': '100m to 1km',
                                    'key': 'Spatial Accuracy',
                                    'op': 'add'
                                }
                            ],
                            'op': 'add'
                        }
                    ],
                    'version': 1,
                    'id': self.identifier1
                }
            ]
        }

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

        # Review and accept version 1
        if (self.handleResult(
            self.moderationBase.doReview('activities', self.identifier1, 1, 1) is True,
            'Activity could not be reviewed.'
        )) is not True:
            return False

        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1 is not None,
            'New Activity was created and reviewed but not found.'
        )) is not True:
            return False

        if (self.handleResult(
            self.a1v1.get_status_id() == 2,
            'Activity is not active after approving.'
        )) is not True:
            return False

        # Make sure the geometry is in taggroup with tg_id = 3
        q = Session.query(A_Tag_Group).\
            join(Activity).\
            filter(Activity.identifier == self.identifier1).\
            filter(Activity.version == 1).\
            filter(A_Tag_Group.tg_id == 3).\
            all()

        if (self.handleResult(
            len(q) == 1,
            'The taggroup with a geometry was not found at all'
        )) is not True:
            return False

        if (self.handleResult(
            q[0].geometry != None,
            'The taggroup does not contain a geometry'
        )) is not True:
            return False

        # Store the geometry
        self.geom1 = q[0].geometry

        return True

    def doTest(self, verbose=False):

        """
        Case 1: Change only the geometry of a taggroup (diff1)
        """

        # Create a diff to update the geometry of the taggroup
        diff1 = {
            'activities': [
                {
                    'taggroups': [
                        {
                            'tg_id': 3,
                            'tags': [],
                            'geometry': {
                                'type': 'Polygon',
                                'coordinates': [
                                    self.coords2
                                ]
                            }
                        }
                    ],
                    'version': 1,
                    'id': self.identifier1
                }
            ]
        }

        if verbose is True:
            log.debug('Diff (diff1) to update a1v1:\n%s' % diff1)

        import requests
        import json
        session = requests.Session()

        user = self.getUser(1)
        session.auth = (user['username'], user['password'])

        headers = {'content-type': 'application/json'}

        request = session.post(
            self.getCreateUrl('activities'),
            data=json.dumps(diff1),
            headers=headers
        )

        if (self.handleResult(
            request.status_code == 201,
            'The new Activity could not be created.'
        )) is not True:
            return False

        jsonresponse = request.json()

        if (self.handleResult(
            'created' in jsonresponse and jsonresponse['created'] is True,
            'Server response ("created") after updating new Activity is not correct.'
        )) is not True:
            return False

        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.a1v2 is not None,
            'Updated Activity was created but not found.'
        )) is not True:
            return False

        # Make sure it is pending
        if (self.handleResult(
            self.a1v2.get_status_id() == 1,
            'Updated Activity is not pending.'
        )) is not True:
            return False

        # Make sure it has a geometry
        q = Session.query(A_Tag_Group).\
            join(Activity).\
            filter(Activity.identifier == self.identifier1).\
            filter(Activity.version == 2).\
            filter(A_Tag_Group.tg_id == 3).\
            all()

        if (self.handleResult(
            len(q) == 1,
            'The taggroup with a geometry was not found at all'
        )) is not True:
            return False

        if (self.handleResult(
            q[0].geometry != None,
            'The taggroup does not contain a geometry'
        )) is not True:
            return False

        # Store the geometry
        self.geom2 = q[0].geometry

        from shapely import wkb
        g1 = wkb.loads(str(self.geom1.geom_wkb))
        g2 = wkb.loads(str(self.geom2.geom_wkb))

        # Make sure it is not the same geometry anymore
        if (self.handleResult(
            g1.equals(g2) is not True,
            'The updated Activity has the same geometry as the old one'
        )) is not True:
            return False

        # Review and accept version 2
        if (self.handleResult(
            self.moderationBase.doReview('activities', self.identifier1, 2, 1) is True,
            'Activity (v2) could not be reviewed.'
        )) is not True:
            return False

        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.a1v2 is not None,
            'Activity v2 was not found after reviewing it'
        )) is not True:
            return False

        if (self.handleResult(
            self.a1v2.get_status_id() == 2,
            'Activity v2 is not active after approving.'
        )) is not True:
            return False

        """
        Case 2: Change the geometry as well as the tag of a taggroup
        """

        # Create a diff to update the geometry of the taggroup
        diff2 = {
            'activities': [
                {
                    'taggroups': [
                        {
                            'tg_id': 3,
                            'tags': [
                                {
                                    'op': 'delete',
                                    'key': self.key3,
                                    'value': self.oldValue3
                                }, {
                                    'op': 'add',
                                    'key': self.key3,
                                    'value': self.newValue3
                                }
                            ],
                            'geometry': {
                                'type': 'Polygon',
                                'coordinates': [
                                    self.coords3
                                ]
                            }
                        }
                    ],
                    'version': 2,
                    'id': self.identifier1
                }
            ]
        }

        if verbose is True:
            log.debug('Diff (diff2) to update a1v2:\n%s' % diff2)

        session = requests.Session()

        user = self.getUser(1)
        session.auth = (user['username'], user['password'])

        headers = {'content-type': 'application/json'}

        request = session.post(
            self.getCreateUrl('activities'),
            data=json.dumps(diff2),
            headers=headers
        )

        if (self.handleResult(
            request.status_code == 201,
            'The new Activity could not be created.'
        )) is not True:
            return False

        jsonresponse = request.json()

        if (self.handleResult(
            'created' in jsonresponse and jsonresponse['created'] is True,
            'Server response ("created") after updating new Activity (v3) is not correct.'
        )) is not True:
            return False

        self.a1v3 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 3
        )
        if (self.handleResult(
            self.a1v3 is not None,
            'Updated Activity (v3) was created but not found.'
        )) is not True:
            return False

        # Make sure it is pending
        if (self.handleResult(
            self.a1v3.get_status_id() == 1,
            'Updated Activity (v3) is not pending.'
        )) is not True:
            return False

        # Make sure it has a geometry
        q = Session.query(A_Tag_Group).\
            join(Activity).\
            filter(Activity.identifier == self.identifier1).\
            filter(Activity.version == 3).\
            filter(A_Tag_Group.tg_id == 3).\
            all()

        if (self.handleResult(
            len(q) == 1,
            'The taggroup with a geometry was not found at all'
        )) is not True:
            return False

        if (self.handleResult(
            q[0].geometry != None,
            'The taggroup does not contain a geometry'
        )) is not True:
            return False

        # Store the geometry
        self.geom3 = q[0].geometry
        g3 = wkb.loads(str(self.geom3.geom_wkb))

        # Make sure it is not the same geometry anymore
        if (self.handleResult(
            g2.equals(g3) is not True,
            'The updated Activity (v3) has the same geometry as the old one'
        )) is not True:
            return False

        # Make sure it also has the new tag
        # Check that the new Activity has the updated value
        if (self.handleResult(
            (self.findKeyValue(self.a1v3, self.key3, self.newValue3) is True and
            self.findKeyValue(self.a1v3, self.key3, self.oldValue3) is False),
            'Values of v3 were not updated correctly.'
        )) is not True:
            return False

        # Review and accept version 3
        if (self.handleResult(
            self.moderationBase.doReview('activities', self.identifier1, 3, 1) is True,
            'Activity (v3) could not be reviewed.'
        )) is not True:
            return False

        self.a1v3 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 3
        )
        if (self.handleResult(
            self.a1v3 is not None,
            'Activity v3 was not found after reviewing it'
        )) is not True:
            return False

        if (self.handleResult(
            self.a1v3.get_status_id() == 2,
            'Activity v3 is not active after approving.'
        )) is not True:
            return False

        """
        Case 3: Change the geometry as well as the tag of a taggroup
        """

        # Create a diff to update the geometry of the taggroup
        diff3 = {
            'activities': [
                {
                    'taggroups': [
                        {
                            'tg_id': 3,
                            'tags': [
                                {
                                    'op': 'delete',
                                    'key': self.key4,
                                    'value': self.oldValue4
                                }, {
                                    'op': 'add',
                                    'key': self.key4,
                                    'value': self.newValue4
                                }
                            ]
                        }
                    ],
                    'version': 3,
                    'id': self.identifier1
                }
            ]
        }

        if verbose is True:
            log.debug('Diff (diff3) to update a1v3:\n%s' % diff3)

        session = requests.Session()

        user = self.getUser(1)
        session.auth = (user['username'], user['password'])

        headers = {'content-type': 'application/json'}

        request = session.post(
            self.getCreateUrl('activities'),
            data=json.dumps(diff3),
            headers=headers
        )

        if (self.handleResult(
            request.status_code == 201,
            'The new Activity (v4) could not be created.'
        )) is not True:
            return False

        jsonresponse = request.json()

        if (self.handleResult(
            'created' in jsonresponse and jsonresponse['created'] is True,
            'Server response ("created") after updating new Activity (v4) is not correct.'
        )) is not True:
            return False

        self.a1v4 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 4
        )
        if (self.handleResult(
            self.a1v4 is not None,
            'Updated Activity (v4) was created but not found.'
        )) is not True:
            return False

        # Make sure it is pending
        if (self.handleResult(
            self.a1v4.get_status_id() == 1,
            'Updated Activity (v4) is not pending.'
        )) is not True:
            return False

        # Make sure it has a geometry
        q = Session.query(A_Tag_Group).\
            join(Activity).\
            filter(Activity.identifier == self.identifier1).\
            filter(Activity.version == 4).\
            filter(A_Tag_Group.tg_id == 3).\
            all()

        if (self.handleResult(
            len(q) == 1,
            'The taggroup with a geometry was not found at all'
        )) is not True:
            return False

        if (self.handleResult(
            q[0].geometry != None,
            'The taggroup does not contain a geometry'
        )) is not True:
            return False

        # Store the geometry
        g4 = wkb.loads(str(q[0].geometry.geom_wkb))

        # Make sure it is still the same as in v3
        if (self.handleResult(
            g3.equals(g4) is True,
            'The updated Activity (v4) does not have the same geometry as v3'
        )) is not True:
            return False

        # Make sure it also has the new tag
        # Check that the new Activity has the updated value
        if (self.handleResult(
            (self.findKeyValue(self.a1v4, self.key4, self.newValue4) is True and
            self.findKeyValue(self.a1v4, self.key4, self.oldValue4) is False),
            'Values of v4 were not updated correctly.'
        )) is not True:
            return False

        # Review and accept version 4
        if (self.handleResult(
            self.moderationBase.doReview('activities', self.identifier1, 4, 1) is True,
            'Activity (v4) could not be reviewed.'
        )) is not True:
            return False

        self.a1v4 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 4
        )
        if (self.handleResult(
            self.a1v4 is not None,
            'Activity v4 was not found after reviewing it'
        )) is not True:
            return False

        if (self.handleResult(
            self.a1v4.get_status_id() == 2,
            'Activity v4 is not active after approving.'
        )) is not True:
            return False

        """
        Case 4: Change a tag of another taggroup
        """

        # Create a diff to update the geometry of the taggroup
        diff4 = {
            'activities': [
                {
                    'taggroups': [
                        {
                            'tg_id': 4,
                            'tags': [
                                {
                                    'op': 'delete',
                                    'key': self.key5,
                                    'value': self.oldValue5
                                }, {
                                    'op': 'add',
                                    'key': self.key5,
                                    'value': self.newValue5
                                }
                            ]
                        }
                    ],
                    'version': 4,
                    'id': self.identifier1
                }
            ]
        }

        if verbose is True:
            log.debug('Diff (diff4) to update a1v4:\n%s' % diff4)

        session = requests.Session()

        user = self.getUser(1)
        session.auth = (user['username'], user['password'])

        headers = {'content-type': 'application/json'}

        request = session.post(
            self.getCreateUrl('activities'),
            data=json.dumps(diff4),
            headers=headers
        )

        if (self.handleResult(
            request.status_code == 201,
            'The new Activity (v5) could not be created.'
        )) is not True:
            return False

        jsonresponse = request.json()

        if (self.handleResult(
            'created' in jsonresponse and jsonresponse['created'] is True,
            'Server response ("created") after updating new Activity (v5) is not correct.'
        )) is not True:
            return False

        self.a1v5 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 5
        )
        if (self.handleResult(
            self.a1v5 is not None,
            'Updated Activity (v5) was created but not found.'
        )) is not True:
            return False

        # Make sure it is pending
        if (self.handleResult(
            self.a1v5.get_status_id() == 1,
            'Updated Activity (v5) is not pending.'
        )) is not True:
            return False

        # Make sure it has a geometry
        q = Session.query(A_Tag_Group).\
            join(Activity).\
            filter(Activity.identifier == self.identifier1).\
            filter(Activity.version == 5).\
            filter(A_Tag_Group.tg_id == 3).\
            all()

        if (self.handleResult(
            len(q) == 1,
            'The taggroup with a geometry was not found at all'
        )) is not True:
            return False

        if (self.handleResult(
            q[0].geometry != None,
            'The taggroup does not contain a geometry'
        )) is not True:
            return False

        # Store the geometry
        g5 = wkb.loads(str(q[0].geometry.geom_wkb))

        # Make sure it is still the same as in v3
        if (self.handleResult(
            g3.equals(g5) is True,
            'The updated Activity (v5) does not have the same geometry as v3'
        )) is not True:
            return False

        # Make sure it also has the new tag
        # Check that the new Activity has the updated value
        if (self.handleResult(
            (self.findKeyValue(self.a1v5, self.key5, self.newValue5) is True and
            self.findKeyValue(self.a1v5, self.key5, self.oldValue5) is False),
            'Values of v4 were not updated correctly.'
        )) is not True:
            return False

        # Review and accept version 5
        if (self.handleResult(
            self.moderationBase.doReview('activities', self.identifier1, 5, 1) is True,
            'Activity (v5) could not be reviewed.'
        )) is not True:
            return False

        self.a1v5 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 5
        )
        if (self.handleResult(
            self.a1v5 is not None,
            'Activity v5 was not found after reviewing it'
        )) is not True:
            return False

        if (self.handleResult(
            self.a1v5.get_status_id() == 2,
            'Activity v5 is not active after approving.'
        )) is not True:
            return False

        """
        Case 5: Set the geometry to none
        """

        # Create a diff to update the geometry of the taggroup
        diff5 = {
            'activities': [
                {
                    'taggroups': [
                        {
                            'tg_id': 3,
                            'tags': [],
                            'geometry': {}
                        }
                    ],
                    'version': 5,
                    'id': self.identifier1
                }
            ]
        }

        if verbose is True:
            log.debug('Diff (diff5) to update a1v5:\n%s' % diff5)

        session = requests.Session()

        user = self.getUser(1)
        session.auth = (user['username'], user['password'])

        headers = {'content-type': 'application/json'}

        request = session.post(
            self.getCreateUrl('activities'),
            data=json.dumps(diff5),
            headers=headers
        )

        if (self.handleResult(
            request.status_code == 201,
            'The new Activity (v6) could not be created.'
        )) is not True:
            return False

        jsonresponse = request.json()

        if (self.handleResult(
            'created' in jsonresponse and jsonresponse['created'] is True,
            'Server response ("created") after updating new Activity (v6) is not correct.'
        )) is not True:
            return False

        self.a1v6 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 6
        )
        if (self.handleResult(
            self.a1v6 is not None,
            'Updated Activity (v6) was created but not found.'
        )) is not True:
            return False

        # Make sure it is pending
        if (self.handleResult(
            self.a1v6.get_status_id() == 1,
            'Updated Activity (v6) is not pending.'
        )) is not True:
            return False

        # Make sure it does not have a geometry
        q = Session.query(A_Tag_Group).\
            join(Activity).\
            filter(Activity.identifier == self.identifier1).\
            filter(Activity.version == 6).\
            filter(A_Tag_Group.tg_id == 3).\
            all()

        if (self.handleResult(
            len(q) == 1,
            'The taggroup was not found at all'
        )) is not True:
            return False

        if (self.handleResult(
            q[0].geometry == None,
            'The taggroup (v6) still has a geometry'
        )) is not True:
            return False

        return True
