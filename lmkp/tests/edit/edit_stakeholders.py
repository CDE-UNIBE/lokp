from lmkp.tests.create.create_base import CreateBase
from lmkp.tests.moderate.moderation_base import ModerationBase

from lmkp.models.meta import DBSession as Session
from lmkp.models.database_objects import *
from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3

import logging
log = logging.getLogger(__name__)

"""
ES 01
"""
class EditStakeholders01(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'ES01'
        self.testDescription = 'It is possible to edit a Stakeholder'
        self.identifier1 = 'aa5379d1-f640-45f5-8cc4-cc06974266d0'
        self.s1v1 = None
        self.s1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeStakeholderTags(1),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        key = 'Country of origin'
        oldValue = 'China'
        newValue = 'Vietnam'

        # Check that the old value is there
        if (self.handleResult(
            (self.findKeyValue(self.s1v1, key, oldValue) is True and
            self.findKeyValue(self.s1v1, key, newValue) is False),
            'Initial values not correct'
        )) is not True:
            return False

        # Find and check the tg_id
        tg_id = self.findTgidByKeyValue(self.s1v1, key, oldValue)
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
        stakeholderDiff = self.getItemDiff(
            'stakeholders',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )
        diff = {'stakeholders': [stakeholderDiff]}

        if verbose is True:
            log.debug('Diff to update s1v1:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(1)),
            'The Stakeholder could not be updated.'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier1)
                and self.s1v2 is not None),
            'Version 2 of the updated Stakeholder was not found.'
        )) is not True:
            return False

        # Check that the new Stakeholder has the updated value
        if (self.handleResult(
            (self.findKeyValue(self.s1v2, key, newValue) is True and
            self.findKeyValue(self.s1v2, key, oldValue) is False),
            'Values were not updated correctly.'
        )) is not True:
            return False

        # Check that no additional taggroup was created
        if (self.handleResult(
            self.countTaggroups(self.s1v2) == len(self.getSomeStakeholderTags(1)),
            'New Stakeholder has not all taggroups.'
        )) is not True:
            return False

        # Check that the new version is pending
        if (self.handleResult(
            self.s1v2.get_status_id() == 1,
            'The updated version of the Stakeholder is not pending.'
        )) is not True:
            return False

        # Check that the old version is still active (query it again)
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1.get_status_id() == 2,
            'The old version of the Stakeholder is not active anymore.'
        )) is not True:
            return False

        return True

"""
ES 02
"""
class EditStakeholders02(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'ES02'
        self.testDescription = 'Only logged in users can edit a Stakeholder'
        self.identifier1 = '495bb901-6c8b-4ec8-92eb-82e0f045fd8b'
        self.s1v1 = None
        self.s1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeStakeholderTags(1),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        key = 'Country of origin'
        oldValue = 'China'
        newValue = 'Vietnam'

        # Check that the old value is there
        if (self.handleResult(
            (self.findKeyValue(self.s1v1, key, oldValue) is True and
            self.findKeyValue(self.s1v1, key, newValue) is False),
            'Initial values not correct'
        )) is not True:
            return False

        # Find and check the tg_id
        tg_id = self.findTgidByKeyValue(self.s1v1, key, oldValue)
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
        stakeholderDiff = self.getItemDiff(
            'stakeholders',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )
        diff = {'stakeholders': [stakeholderDiff]}

        if verbose is True:
            log.debug('Diff to update s1v1:\n%s' % diff)

        # Try to do the edit without authentication
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
            'The Stakeholder was edited even when user was not logged in.'
        )) is not True:
            return False

        # Check that no new Stakeholder was created
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.s1v2 is None,
            'There was a second version (created by not logged in user) found'
        )) is not True:
            return False

        # Make sure that there is only 1 version
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 1,
            'There was a edited version of the Stakeholder created by an anonymous user.'
        )) is not True:
            return False

        # Check that the old version is still active (query it again)
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1.get_status_id() == 2,
            'The old version of the Stakeholder is not active anymore.'
        )) is not True:
            return False

        return True

"""
ES 03
"""
class EditStakeholders03(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'ES03'
        self.testDescription = 'Edit a first pending Stakeholder leaves the first version to \'pending\''
        self.identifier1 = 'd0c0d35a-96ca-44bd-a43e-dda7688c9641'
        self.s1v1 = None
        self.s1v2 = None

    def testSetup(self, verbose=False):

        # Create and check a first Stakeholder
        self.s1v1 = self.createAndCheckFirstItem(
            self,
            'stakeholders',
            Stakeholder,
            self.getCreateUrl('stakeholders'),
            self.getSomeStakeholderTags(1),
            self.identifier1,
            self.getUser(1)
        )
        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created.'
        )) is not True:
            return False

        # Make sure the Stakeholder is pending
        if (self.handleResult(
            self.s1v1.get_status_id() == 1,
            'First Stakeholder is not pending.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        key = 'Country of origin'
        oldValue = 'China'
        newValue = 'Vietnam'

        # Check that the old value is there
        if (self.handleResult(
            (self.findKeyValue(self.s1v1, key, oldValue) is True and
            self.findKeyValue(self.s1v1, key, newValue) is False),
            'Initial values not correct'
        )) is not True:
            return False

        # Find and check the tg_id
        tg_id = self.findTgidByKeyValue(self.s1v1, key, oldValue)
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
        stakeholderDiff = self.getItemDiff(
            'stakeholders',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )
        diff = {'stakeholders': [stakeholderDiff]}

        if verbose is True:
            log.debug('Diff to update s1v1:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(1)),
            'The Stakeholder could not be updated.'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier1)
                and self.s1v2 is not None),
            'Version 2 of the updated Stakeholder was not found.'
        )) is not True:
            return False

        # Check that the new Stakeholder has the updated value
        if (self.handleResult(
            (self.findKeyValue(self.s1v2, key, newValue) is True and
            self.findKeyValue(self.s1v2, key, oldValue) is False),
            'Values were not updated correctly.'
        )) is not True:
            return False

        # Check that no additional taggroup was created
        if (self.handleResult(
            self.countTaggroups(self.s1v2) == len(self.getSomeStakeholderTags(1)),
            'New Stakeholder has not all taggroups.'
        )) is not True:
            return False

        # Check that the new version is pending
        if (self.handleResult(
            self.s1v2.get_status_id() == 1,
            'The updated version of the Stakeholder is not pending.'
        )) is not True:
            return False

        # Check that the old version is also still pending (query it again)
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1.get_status_id() == 1,
            'The old version of the Stakeholder is not still pending.'
        )) is not True:
            return False

        return True

"""
ES 04
"""
class EditStakeholders04(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'ES04'
        self.testDescription = 'Edit two tags of a taggroup of an active Stakeholder'
        self.identifier1 = '0af0ecb6-b4ac-4662-91ae-56d69bb63fec'
        self.s1v1 = None
        self.s1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeStakeholderTags(2),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        key1 = 'Country of origin'
        oldValue1 = 'Vietnam'
        newValue1 = 'Thailand'
        key2 = 'Economic Sector'
        oldValue2 = 'Mining'
        newValue2 = 'Agriculture'

        # Check that the old values are there
        if (self.handleResult(
            (self.findKeyValue(self.s1v1, key1, oldValue1) is True and
            self.findKeyValue(self.s1v1, key1, newValue1) is False and
            self.findKeyValue(self.s1v1, key2, oldValue2) is True and
            self.findKeyValue(self.s1v1, key2, newValue2) is False),
            'Initial values not correct'
        )) is not True:
            return False

        # Find and check the tg_id
        tg_id1 = self.findTgidByKeyValue(self.s1v1, key1, oldValue1)
        tg_id2 = self.findTgidByKeyValue(self.s1v1, key2, oldValue2)
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
        stakeholderDiff = self.getItemDiff(
            'stakeholders',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )
        diff = {'stakeholders': [stakeholderDiff]}

        if verbose is True:
            log.debug('Diff to update s1v1:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(1)),
            'The Stakeholder could not be updated.'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier1)
                and self.s1v2 is not None),
            'Version 2 of the updated Stakeholder was not found.'
        )) is not True:
            return False

        # Check that the new Stakeholder has the updated values
        if (self.handleResult(
            (self.findKeyValue(self.s1v2, key1, newValue1) is True and
            self.findKeyValue(self.s1v2, key1, oldValue1) is False and
            self.findKeyValue(self.s1v2, key2, newValue2) is True and
            self.findKeyValue(self.s1v2, key2, oldValue2) is False),
            'Values were not updated correctly.'
        )) is not True:
            return False

        # Check that the updated values are both in the same taggroup
        tg_id1 = self.findTgidByKeyValue(self.s1v2, key1, newValue1)
        tg_id2 = self.findTgidByKeyValue(self.s1v2, key2, newValue2)
        if (self.handleResult(
            tg_id1 is not None and tg_id2 is not None and tg_id1 == tg_id2,
            'The updated values are not in the same taggroup.'
        )) is not True:
            return False

        # Check that no additional taggroup was created
        if (self.handleResult(
            self.countTaggroups(self.s1v2) == len(self.getSomeStakeholderTags(2)),
            'New Stakeholder has not all taggroups.'
        )) is not True:
            return False

        # Check that the new version is pending
        if (self.handleResult(
            self.s1v2.get_status_id() == 1,
            'The updated version of the Stakeholder is not pending.'
        )) is not True:
            return False

        # Check that the old version is still active (query it again)
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1.get_status_id() == 2,
            'The old version of the Stakeholder is not active anymore.'
        )) is not True:
            return False

        return True

"""
ES 05
"""
class EditStakeholders05(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'ES05'
        self.testDescription = 'Add a new Taggroup'
        self.identifier1 = 'fec5b114-0ee2-4980-b3d9-f9970f23072c'
        self.s1v1 = None
        self.s1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeStakeholderTags(2),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        newKey = 'Address'
        newValue = 'Address A'

        diff = self.getSomeWholeDiff(
            'stakeholders',
            [{newKey: newValue}],
            self.identifier1,
            1,
            'add'
        )

        if verbose is True:
            log.debug('Diff to update s1v1:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(1)),
            'The Stakeholder could not be updated.'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier1)
                and self.s1v2 is not None),
            'Version 2 of the updated Stakeholder was not found.'
        )) is not True:
            return False

        # Check that the new Stakeholder has the new value
        if (self.handleResult(
            self.findKeyValue(self.s1v2, newKey, newValue) is True,
            'The key/value of the new taggroup was not found.'
        )) is not True:
            return False

        # Check that the new Stakeholder has a new taggroup
        if (self.handleResult(
            self.countTaggroups(self.s1v2) == len(self.getSomeStakeholderTags(1))+1,
            'New Stakeholder has not all taggroups.'
        )) is not True:
            return False

        # Check that the new version is pending
        if (self.handleResult(
            self.s1v2.get_status_id() == 1,
            'The updated version of the Stakeholder is not pending.'
        )) is not True:
            return False

        # Check that the old version is still active (query it again)
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1.get_status_id() == 2,
            'The old version of the Stakeholder is not active anymore.'
        )) is not True:
            return False

        return True

"""
ES 06
"""
class EditStakeholders06(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'ES06'
        self.testDescription = 'Add a new Tag to a Taggroup'
        self.identifier1 = '4b509e55-ccf4-4af5-8ad6-6112389770f9'
        self.s1v1 = None
        self.s1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeStakeholderTags(2),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        newKey = 'Address'
        newValue = 'Address B'
        inTaggroupWithKey = 'Name'
        inTaggroupWithValue = 'Stakeholder X'

        # Find and check the tg_id
        tg_id = self.findTgidByKeyValue(self.s1v1, inTaggroupWithKey, inTaggroupWithValue)
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
        stakeholderDiff = self.getItemDiff(
            'stakeholders',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )
        diff = {'stakeholders': [stakeholderDiff]}

        if verbose is True:
            log.debug('Diff to update s1v1:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(1)),
            'The Stakeholder could not be updated.'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier1)
                and self.s1v2 is not None),
            'Version 2 of the updated Stakeholder was not found.'
        )) is not True:
            return False

        # Check that the new Stakeholder has the new value
        if (self.handleResult(
            self.findKeyValue(self.s1v2, newKey, newValue) is True,
            'The key/value of the new taggroup was not found.'
        )) is not True:
            return False

        # Check that the new Stakeholder still has the same number of taggroups
        if (self.handleResult(
            self.countTaggroups(self.s1v2) == len(self.getSomeStakeholderTags(2)),
            'New Stakeholder has not all taggroups.'
        )) is not True:
            return False

        # Check that the Tag was inserted in the correct taggroup
        if (self.handleResult(
            tg_id == self.findTgidByKeyValue(self.s1v2, newKey, newValue),
            'The new tag was not inserted in the correct taggroup'
        )) is not True:
            return False

        # Check that the new version is pending
        if (self.handleResult(
            self.s1v2.get_status_id() == 1,
            'The updated version of the Stakeholder is not pending.'
        )) is not True:
            return False

        # Check that the old version is still active (query it again)
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1.get_status_id() == 2,
            'The old version of the Stakeholder is not active anymore.'
        )) is not True:
            return False

        return True

"""
ES 07
"""
class EditStakeholders07(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'ES07'
        self.testDescription = 'Delete a Taggroup'
        self.identifier1 = '2839faf2-67f1-4357-a47b-9994e04313ef'
        self.s1v1 = None
        self.s1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeStakeholderTags(2),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        oldKey1 = 'Country of origin'
        oldValue1 = 'Vietnam'
        oldKey2 = 'Economic Sector'
        oldValue2 = 'Mining'

        # The tg_id needs to be known!

        # Find and check the tg_id
        tg_id = self.findTgidByKeyValue(self.s1v1, oldKey1, oldValue1)
        if (self.handleResult(
            tg_id is not None,
            'The tg_id of taggroup to delete was not found.'
        )) is not True:
            return False

        # Prepare tags
        deleteTags = self.getTagDiffsFromTags({
            oldKey1: oldValue1,
            oldKey2: oldValue2
        }, 'delete')
        # Prepare taggroup
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags,
            'op': 'delete'
        }

        # Put together the diff
        stakeholderDiff = self.getItemDiff(
            'stakeholders',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )
        diff = {'stakeholders': [stakeholderDiff]}

        if verbose is True:
            log.debug('Diff to update s1v1:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(1)),
            'The Stakeholder could not be updated.'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier1)
                and self.s1v2 is not None),
            'Version 2 of the updated Stakeholder was not found.'
        )) is not True:
            return False

        # Check that the new Stakeholder does not have the old value anymore
        if (self.handleResult(
            self.findKeyValue(self.s1v2, oldKey1, oldValue1) is not True,
            'The key/value of the new taggroup still found.'
        )) is not True:
            return False

        # Check that the new Stakeholder does not have the same number of taggroups anymore
        if (self.handleResult(
            self.countTaggroups(self.s1v2) == len(self.getSomeStakeholderTags(2))-1,
            'New Stakeholder has not all taggroups.'
        )) is not True:
            return False

        # Check that the new version is pending
        if (self.handleResult(
            self.s1v2.get_status_id() == 1,
            'The updated version of the Stakeholder is not pending.'
        )) is not True:
            return False

        # Check that the old version is still active (query it again)
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1.get_status_id() == 2,
            'The old version of the Stakeholder is not active anymore.'
        )) is not True:
            return False

        return True

"""
ES 08
"""
class EditStakeholders08(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'ES08'
        self.testDescription = 'Delete a Tag of a Taggroup'
        self.identifier1 = '68f4fab2-3f2c-410d-80bc-d8052b02936f'
        self.s1v1 = None
        self.s1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeStakeholderTags(2),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        oldKey = 'Economic Sector'
        oldValue = 'Mining'

        # The tg_id needs to be known!

        # Find and check the tg_id
        tg_id = self.findTgidByKeyValue(self.s1v1, oldKey, oldValue)
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
        stakeholderDiff = self.getItemDiff(
            'stakeholders',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )
        diff = {'stakeholders': [stakeholderDiff]}

        if verbose is True:
            log.debug('Diff to update s1v1:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(1)),
            'The Stakeholder could not be updated.'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier1)
                and self.s1v2 is not None),
            'Version 2 of the updated Stakeholder was not found.'
        )) is not True:
            return False

        # Check that the new Stakeholder does not have the old value anymore
        if (self.handleResult(
            self.findKeyValue(self.s1v2, oldKey, oldValue) is not True,
            'The key/value of the new taggroup still found.'
        )) is not True:
            return False

        # Check that the new Stakeholder does still have the same number of taggroups
        if (self.handleResult(
            self.countTaggroups(self.s1v2) == len(self.getSomeStakeholderTags(2)),
            'New Stakeholder has not all taggroups.'
        )) is not True:
            return False

        # Check that the new version is pending
        if (self.handleResult(
            self.s1v2.get_status_id() == 1,
            'The updated version of the Stakeholder is not pending.'
        )) is not True:
            return False

        # Check that the old version is still active (query it again)
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1.get_status_id() == 2,
            'The old version of the Stakeholder is not active anymore.'
        )) is not True:
            return False

        return True

"""
ES 09
"""
class EditStakeholders09(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'ES09'
        self.testDescription = 'Add an Involvement'
        self.identifier1 = '9895f1d3-17c8-4b86-b9ea-1ce37e0b5c8c'
        self.s1v1 = None
        self.s1v2 = None

        from lmkp.views.activity_protocol3 import ActivityProtocol3
        self.otherProtocol = ActivityProtocol3(Session)
        self.identifier2 = '594ddd7e-f98c-4f64-8928-1ac4c4faa132'
        self.a1v1 = None
        self.invRole1 = self.getStakeholderRole(6)

    def testSetup(self, verbose=False):

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
            self.getSomeStakeholderTags(2),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Create a Activity to do an edit on the Activity
        diff = self.getSomeWholeDiff(
            'activities',
            self.getSomeActivityTags(1),
            self.identifier2,
            1,
            'add',
            self.getSomeGeometryDiff('Laos'),
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
            log.debug('Diff to update s1v1:\n%s' % diff)

        # Create the Activity
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(3)),
            'The Activity could not be created.'
        )) is not True:
            return False

        # Check that the Activity was created
        self.a1v1 = self.otherProtocol.read_one_by_version(
            self.request, self.identifier2, 1
        )
        if (self.handleResult(
            self.a1v1 is not None,
            'The Activity was not created'
        )) is not True:
            return False
        if (self.handleResult(
            self.a1v1.get_status_id() == 1,
            'The created Activity is not pending'
        )) is not True:
            return False

        # Check that the Activity has an involvement
        if (self.handleResult(
            len(self.a1v1.get_involvements()) == 1,
            'The Activity does not have an Involvement'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier1)
                and self.s1v2 is not None),
            'Version 2 of the updated Stakeholder was not found.'
        )) is not True:
            return False

        # Check that the new Stakeholder has an involvement
        if (self.handleResult(
            len(self.s1v2.get_involvements()) == 1,
            'Stakeholder v2 does not have an Involvement'
        )) is not True:
            return False

        return True

"""
ES 10
"""
class EditStakeholders10(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'ES10'
        self.testDescription = 'Delete an Involvement'
        self.identifier1 = 'aa0b6f0a-7172-47db-a9cf-cb25e7588449'
        self.s1v1 = None
        self.s1v2 = None
        self.s1v3 = None

        from lmkp.views.activity_protocol3 import ActivityProtocol3
        self.otherProtocol = ActivityProtocol3(Session)
        self.identifier2 = '753fcc3f-3f5f-4278-a01f-d154112390e9'
        self.a1v1 = None
        self.a1v2 = None
        self.a1v3 = None
        self.invRole1 = self.getStakeholderRole(6)

        self.moderationBase = ModerationBase()

    def testSetup(self, verbose=False):

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
            self.getSomeStakeholderTags(1),
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
            self.getSomeActivityTags(1),
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

        # Create a new Involvement
        diff = self.getSomeWholeDiff(
            'activities',
            [],
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
            log.debug('Diff to create a1v2:\n%s' % diff)

        if (self.handleResult(
            self.doCreate(self.getCreateUrl('activities'), diff, self.getUser(1)),
            'New Activity (with involvement) could not be created at all.'
        )) is not True:
            return False

        # Review the Activity (this will also review the Stakeholder)
        if (self.handleResult(
            self.moderationBase.doReview(
                'activities', self.identifier2, 2, 1
            ) is True,
            'The Activity (with involvement) could not be reviewed.'
        )) is not True:
            return False

        # Find the created Stakeholder
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
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

        # Find the created Activity
        self.a1v2 = self.otherProtocol.read_one_by_version(
            self.request, self.identifier2, 2
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

        return True

    def doTest(self, verbose=False):

        # Create a Stakeholder to do an edit on the Activity
        diff = self.getSomeWholeDiff(
            'activities',
            [],
            self.identifier2,
            2,
            'add',
            involvements = [
                {
                    'id': self.identifier1,
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

        # Check that the Stakeholder was created
        self.s1v3 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 3
        )
        if (self.handleResult(
            self.s1v3 is not None,
            'The Stakeholder (without Involvement) was not created'
        )) is not True:
            return False
        if (self.handleResult(
            self.s1v3.get_status_id() == 1,
            'The created Stakeholder (without Involvement) is not pending'
        )) is not True:
            return False

        # Check that the Stakeholder has no involvement
        if (self.handleResult(
            len(self.s1v3.get_involvements()) == 0,
            'The Stakeholder (without Involvement) still has an Involvement'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v3 = self.otherProtocol.read_one_by_version(
            self.request, self.identifier2, 3
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier2)
                and self.a1v3 is not None),
            'Version 3 of the updated Activity (without Involvement) was not found.'
        )) is not True:
            return False

        # Check that the new Activity has an involvement
        if (self.handleResult(
            len(self.s1v3.get_involvements()) == 0,
            'Activity (without Involvement) does have an Involvement'
        )) is not True:
            return False

        return True

"""
ES 11
"""
class EditStakeholders11(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'ES11'
        self.testDescription = 'Delete the Maintag of a Taggroup'
        self.identifier1 = 'e06a727c-9448-4b9a-b411-05962b918cf4'
        self.s1v1 = None
        self.s1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeStakeholderTags(2),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        oldKey = 'Economic Sector'
        oldValue = 'Mining'
        otherKey = 'Country of origin'
        otherValue = 'Vietnam'

        # The tg_id needs to be known!

        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.s1v1, oldKey, oldValue)
        if (self.handleResult(
            tg_id is not None,
            'The tg_id of taggroup to delete was not found.'
        )) is not True:
            return False

        # Get the taggroup with this tg_id
        taggroup = self.s1v1.find_taggroup_by_tg_id(tg_id)

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
        stakeholderDiff = self.getItemDiff(
            'stakeholders',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroupDiff]
        )
        diff = {'stakeholders': [stakeholderDiff]}

        if verbose is True:
            log.debug('Diff to update s1v1:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(1)),
            'The Stakeholder could not be updated.'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier1)
                and self.s1v2 is not None),
            'Version 2 of the updated Stakeholder was not found.'
        )) is not True:
            return False

        # Check that the new Stakeholder does not have the old value anymore
        if (self.handleResult(
            self.findKeyValue(self.s1v2, oldKey, oldValue) is not True,
            'The key/value of the new taggroup still found.'
        )) is not True:
            return False

        # Check the new maintag
        # Get the taggroup with this tg_id
        taggroup2 = self.s1v2.find_taggroup_by_tg_id(tg_id)

        # Get the main tag of this taggroup
        maintag2 = taggroup2.get_tag_by_id(taggroup2.get_maintag_id())

        # Check that the new Activity does not have the old value anymore
        if (self.handleResult(
            maintag2 is not None,
            'The new Stakeholder does not have a maintag anymore'
        )) is not True:
            return False

        # Make sure the new main tag is the other tag remaining in the taggroup
        if (self.handleResult(
            maintag2.get_key() == otherKey and maintag2.get_value() == otherValue,
            'The new Stakeholder has a wrong maintag'
        )) is not True:
            return False

        return True

"""
ES 12
"""
class EditStakeholders12(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'ES12'
        self.testDescription = 'Edit a Maintag'
        self.identifier1 = 'f52df5fb-a9f6-46bb-bf2b-578dcf99d4ef'
        self.s1v1 = None
        self.s1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeStakeholderTags(2),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # The values to change
        key = 'Economic Sector'
        oldValue = 'Mining'
        newValue = 'Agriculture'

        # The tg_id needs to be known!

        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.s1v1, key, oldValue)
        if (self.handleResult(
            tg_id is not None,
            'The tg_id of taggroup to change was not found.'
        )) is not True:
            return False

        # Get the taggroup with this tg_id
        taggroup = self.s1v1.find_taggroup_by_tg_id(tg_id)

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
        stakeholderDiff = self.getItemDiff(
            'stakeholders',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroupDiff]
        )
        diff = {'stakeholders': [stakeholderDiff]}

        if verbose is True:
            log.debug('Diff to update s1v1:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(1)),
            'The Stakeholder could not be updated.'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier1)
                and self.s1v2 is not None),
            'Version 2 of the updated Stakeholder was not found.'
        )) is not True:
            return False

        # Check that the new Stakeholder does not have the old value anymore
        if (self.handleResult(
            self.findKeyValue(self.s1v2, key, oldValue) is not True,
            'The value of the old taggroup was still found.'
        )) is not True:
            return False

        # Check the new maintag
        # Get the taggroup with this tg_id
        taggroup2 = self.s1v2.find_taggroup_by_tg_id(tg_id)

        # Get the main tag of this taggroup
        maintag2 = taggroup2.get_tag_by_id(taggroup2.get_maintag_id())

        # Check that the new Stakeholder does not have the old value anymore
        if (self.handleResult(
            maintag2 is not None,
            'The new Stakeholder does not have a maintag anymore'
        )) is not True:
            return False

        # Make sure the new main tag is the newly set tag
        if (self.handleResult(
            maintag2.get_key() == key and maintag2.get_value() == newValue,
            'The new Stakeholder has a wrong maintag'
        )) is not True:
            return False

        return True

"""
ES 13
"""
class EditStakeholders13(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'ES13'
        self.testDescription = 'Delete a Stakeholder'
        self.identifier1 = '31a69b39-e625-4bec-8350-4beca1ba5394'
        self.s1v1 = None
        self.s1v2 = None

    def testSetup(self, verbose=False):

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
            self.getSomeStakeholderTags(1),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        diff = self.getSomeWholeDiff(
            'stakeholders',
            self.getSomeStakeholderTags(1),
            self.identifier1,
            1,
            'delete',
            setMaintags = False,
            addTgids = True
        )

        if verbose is True:
            log.debug('Diff to update s1v1:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(1)),
            'The Stakeholder could not be updated.'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier1)
                and self.s1v2 is not None),
            'Version 2 of the updated Stakeholder was not found.'
        )) is not True:
            return False

        # Check that the new Stakeholder only has one (empty) taggroup
        if (self.handleResult(
            len(self.s1v2.get_taggroups()) == 1,
            'Version 2 does not only have one (empty) taggroup'
        )) is not True:
            return False

        # Check that the taggroup only has one (empty) tag
        tg = self.s1v2.get_taggroups()[0]
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
ES 14
"""
class EditStakeholders14(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'ES14'
        self.testDescription = 'Edit a own pending Stakeholder sets it to "edited"'
        self.identifier1 = '4a2d0520-6281-4cd7-a875-da58091c30d1'
        self.s1v1 = None
        self.s1v2 = None
        self.s1v3 = None

    def testSetup(self, vebose=False):

        # Make sure the Stakeholder does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder exists already'
        )) is not True:
            return False

        # Create, moderate and check Stakeholder
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

        return True

    def doTest(self, verbose=False):

        # The values to change
        key1 = 'Name'
        oldValue1 = 'Stakeholder A'
        newValue1 = 'Stakeholder B'

        key2 = 'Country of origin'
        oldValue2 = 'China'
        newValue2 = 'Vietnam'

        """
        v2
        """
        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.s1v1, key1, oldValue1)
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
        diff = {'stakeholders': [self.getItemDiff(
            'stakeholders',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update s1v1:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(1)),
            'The Stakeholder could not be updated.'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier1)
                and self.s1v2 is not None),
            'Version 2 of the updated Stakeholder was not found.'
        )) is not True:
            return False

        """
        v3
        """
        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.s1v2, key2, oldValue2)
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
        diff = {'stakeholders': [self.getItemDiff(
            'stakeholders',
            id = self.identifier1,
            version = 2,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update s1v2:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(1)),
            'The Stakeholder could not be updated.'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s1v3 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 3
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier1)
                and self.s1v3 is not None),
            'Version 3 of the updated Stakeholder was not found.'
        )) is not True:
            return False

        # Re-query v2
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )

        # Check that the status of v2 is not 'edited'
        if (self.handleResult(
            self.s1v2.get_status_id() == 6,
            'The status of version 2 is not "edited"'
        )) is not True:
            return False

        # Check that the status of v3 is 'pending'
        if (self.handleResult(
            self.s1v3.get_status_id() == 1,
            'The status of version 3 is not "pending"'
        )) is not True:
            return False

        # Check that v2 does contain the first change
        if (self.handleResult(
            (self.findKeyValue(self.s1v2, key1, oldValue1) is False and
                self.findKeyValue(self.s1v2, key1, newValue1) is True),
            'The new value of v2 was not correctly set'
        )) is not True:
            return False

        # Check that v2 does not contain the second change
        if (self.handleResult(
            (self.findKeyValue(self.s1v2, key2, oldValue2) is True and
                self.findKeyValue(self.s1v2, key2, newValue2) is False),
            'Version 2 also contains the second change'
        )) is not True:
            return False

        # Check that v3 contains both changes
        if (self.handleResult(
            (self.findKeyValue(self.s1v3, key1, oldValue1) is False and
                self.findKeyValue(self.s1v3, key1, newValue1) is True),
            'Version 3 does not contain the changes made to version 2'
        )) is not True:
            return False

        # Check that v3 contains both changes
        if (self.handleResult(
            (self.findKeyValue(self.s1v3, key2, oldValue2) is False and
                self.findKeyValue(self.s1v3, key2, newValue2) is True),
            'Version 3 does not contain the changes made to version 3'
        )) is not True:
            return False

        return True

"""
ES 15
"""
class EditStakeholders15(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'ES15'
        self.testDescription = 'Edits by different users are based on the active version'
        self.identifier1 = 'efef905d-b047-48b9-8a13-3908a586b902'
        self.s1v1 = None
        self.s1v2 = None
        self.s1v3 = None

    def testSetup(self, vebose=False):

        # Make sure the Stakeholder does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder exists already'
        )) is not True:
            return False

        # Create, moderate and check Stakeholder
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

        return True

    def doTest(self, verbose=False):

        # The values to change
        key1 = 'Name'
        oldValue1 = 'Stakeholder A'
        newValue1 = 'Stakeholder B'

        key2 = 'Country of origin'
        oldValue2 = 'China'
        newValue2 = 'Vietnam'

        """
        v2 (by user2 > based on v1)
        """
        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.s1v1, key1, oldValue1)
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
        diff = {'stakeholders': [self.getItemDiff(
            'stakeholders',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update s1v1:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(2)),
            'The Stakeholder could not be updated.'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier1)
                and self.s1v2 is not None),
            'Version 2 of the updated Stakeholder was not found.'
        )) is not True:
            return False

        """
        v3 (by user 3 > based on v1)
        """
        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.s1v1, key2, oldValue2)
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
        diff = {'stakeholders': [self.getItemDiff(
            'stakeholders',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update s1v2:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(3)),
            'The Stakeholder could not be updated.'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s1v3 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 3
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier1)
                and self.s1v3 is not None),
            'Version 3 of the updated Stakeholder was not found.'
        )) is not True:
            return False

        # Re-query v2
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )

        # Check that the status of v2 is  'pending'
        if (self.handleResult(
            self.s1v2.get_status_id() == 1,
            'The status of version 2 is not "pending"'
        )) is not True:
            return False

        # Check that the status of v3 is 'pending'
        if (self.handleResult(
            self.s1v3.get_status_id() == 1,
            'The status of version 3 is not "pending"'
        )) is not True:
            return False

        # Check that v2 does contain the first change
        if (self.handleResult(
            (self.findKeyValue(self.s1v2, key1, oldValue1) is False and
                self.findKeyValue(self.s1v2, key1, newValue1) is True),
            'Version 2 does not contain the changes made by user 2'
        )) is not True:
            return False

        # Check that v2 does not contain the second change
        if (self.handleResult(
            (self.findKeyValue(self.s1v2, key2, oldValue2) is True and
                self.findKeyValue(self.s1v2, key2, newValue2) is False),
            'Version 2 also contains the second change'
        )) is not True:
            return False

        # Check that v3 contains both changes
        if (self.handleResult(
            (self.findKeyValue(self.s1v3, key1, oldValue1) is True and
                self.findKeyValue(self.s1v3, key1, newValue1) is False),
            'Version 3 does not contain the changes made by user 2'
        )) is not True:
            return False

        # Check that v3 contains both changes
        if (self.handleResult(
            (self.findKeyValue(self.s1v3, key2, oldValue2) is False and
                self.findKeyValue(self.s1v3, key2, newValue2) is True),
            'Version 3 does not contain the changes made by user 3'
        )) is not True:
            return False

        return True