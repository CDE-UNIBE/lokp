from lmkp.tests.create_base import CreateBase
from lmkp.tests.moderation_base import ModerationBase

from lmkp.models.meta import DBSession as Session
from lmkp.models.database_objects import *
from lmkp.views.activity_protocol3 import ActivityProtocol3

import logging
log = logging.getLogger(__name__)

class EditActivities1(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "EA1"
        self.testDescription = 'Edit an active Activity'
        self.identifier1 = 'cbe22b14-525a-4578-aa80-df961aa0b747'
        self.a1v1 = None
        self.a1v2 = None
        self.moderationBase = ModerationBase()

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
            profile = 'LA'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created'
        )) is not True:
            return False

        # Review and accept version 1
        if (self.handleResult(
            self.moderationBase.doReview('activities', self.identifier1, 1, 1) is True,
            'Activity could not be reviewed'
        )) is not True:
            return False

        # Query the item again to check that it is now active
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 2,
            'Activity is not active after approving.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Prepare the values
        key = 'Contract area (ha)'
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
        oldTags = {key: oldValue}
        deleteTags = self.getTagDiffsFromTags(oldTags, 'delete')
        newTags = {key: newValue}
        addTags = self.getTagDiffsFromTags(newTags, 'add')

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
            self.countTaggroups(self.a1v2) == 7,
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

class EditActivities2(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "EA2"
        self.testDescription = 'Edit a first pending Activity'
        self.identifier1 = '177b8a03-bd2d-49db-aea4-1f27d3912121'
        self.a1v1 = None
        self.a1v2 = None
        self.moderationBase = ModerationBase()

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
            profile = 'LA'
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

        # Prepare the values
        key = 'Contract area (ha)'
        oldValue = 100
        newValue = 50

        # Check that the old value is there
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
        oldTags = {key: oldValue}
        deleteTags = self.getTagDiffsFromTags(oldTags, 'delete')
        newTags = {key: newValue}
        addTags = self.getTagDiffsFromTags(newTags, 'add')

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
            self.countTaggroups(self.a1v2) == 7,
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

class EditActivities3(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "EA3"
        self.testDescription = 'Edit two tags of a taggroup of an active Activity'
        self.identifier1 = '5dd1e511-5d33-4cb5-95a1-1a5ada35352b'
        self.a1v1 = None
        self.a1v2 = None
        self.moderationBase = ModerationBase()

    def testSetup(self, verbose=False):

        # Create and check a first Activity
        self.a1v1 = self.createAndCheckFirstItem(
            self,
            'activities',
            Activity,
            self.getCreateUrl('activities'),
            self.getSomeActivityTags(2),
            self.identifier1,
            self.getUser(1),
            profile = 'LA'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created'
        )) is not True:
            return False

        # Review and accept version 1
        if (self.handleResult(
            self.moderationBase.doReview('activities', self.identifier1, 1, 1) is True,
            'Activity could not be reviewed'
        )) is not True:
            return False

        # Query the item again to check that it is now active
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 2,
            'Activity is not active after approving.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Prepare the values
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
            self.countTaggroups(self.a1v2) == 7,
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