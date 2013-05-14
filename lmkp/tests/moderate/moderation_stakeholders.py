from lmkp.tests.moderate.moderation_base import ModerationBase
from lmkp.tests.create.create_base import CreateBase

from lmkp.models.meta import DBSession as Session
from lmkp.models.database_objects import *
from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3


"""
MS 01
"""
class ModerationStakeholders01(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'MS01'
        self.testDescription = 'It is possible to review a Stakeholder'
        self.identifier1 = '73944f2b-b136-4a17-9edd-fbf360358bb0'
        self.s1v1 = None
        self.createBase = CreateBase()

    def testSetup(self, vebose=False):

        # Create and check a first Stakeholder
        self.s1v1 = self.createBase.createAndCheckFirstItem(
            self,
            'stakeholders',
            Stakeholder,
            self.createBase.getCreateUrl('stakeholders'),
            self.createBase.getSomeStakeholderTags(1),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Make sure the item is pending
        if (self.handleResult(
            self.s1v1.get_status_id() == 1,
            'Stakeholder was not pending initially.'
        )) is not True:
            return False

        # Review and accept version 1
        if (self.handleResult(
            self.doReview('stakeholders', self.identifier1, 1, 1) is True,
            'Stakeholder could not be reviewed.'
        )) is not True:
            return False

        # Query the item again to check that it is now active
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1.get_status_id() == 2,
            'Stakeholder is not active after approving.'
        )) is not True:
            return False

        # Make sure there no other version was created
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 1,
            'Review of an active Stakeholder created more than one version.'
        )) is not True:
            return False

        return True

"""
MS 02
"""
class ModerationStakeholders02(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'MS02'
        self.testDescription = 'Only logged in users with moderation privileges can review a Stakeholder'
        self.identifier1 = '0be01ae3-e8ca-4ce7-9322-76a8f0f50451'
        self.s1v1 = None
        self.createBase = CreateBase()

    def testSetup(self, verbose=False):

        # Create and check a first Stakeholder
        self.s1v1 = self.createBase.createAndCheckFirstItem(
            self,
            'stakeholders',
            Stakeholder,
            self.createBase.getCreateUrl('stakeholders'),
            self.createBase.getSomeStakeholderTags(1),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Make sure the item is pending
        if (self.handleResult(
            self.s1v1.get_status_id() == 1,
            'Stakeholder was not pending initially.'
        )) is not True:
            return False

        # Prepare general stuff needed for moderation
        import requests
        import json
        # Prepare payload
        payload = {
            'version': 1,
            'identifier': self.identifier1,
            'review_decision': 1,
            'comment_textarea': ''
        }

        """
        Not logged in
        """
        session = requests.Session()
        session.auth = ()
        cookies = dict(_PROFILE_='Laos')

        request = session.post(
            self.getReviewUrl('stakeholders'),
            data=payload,
            cookies=cookies
        )

        # Make sure the review request returned 401
        if (self.handleResult(
            request.status_code == 401,
            'The request to do a review as "not logged in" did not return 401 (unauthorized)'
        )) is not True:
            return False

        # Make sure the Stakeholder was not reviewed
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1.get_status_id() == 1,
            'The pending Stakeholder was reviewed by request as "not logged in"'
        )) is not True:
            return False

        """
        User 3 (normal user)
        """
        session = requests.Session()
        user = self.getUser(3)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Laos')

        request = session.post(
            self.getReviewUrl('stakeholders'),
            data=payload,
            cookies=cookies
        )

        # Make sure the review request returned 401
        if (self.handleResult(
            request.status_code == 401,
            'The request to do a review as "user3" did not return 401 (unauthorized)'
        )) is not True:
            return False

        # Make sure the Stakeholder was not reviewed
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1.get_status_id() == 1,
            'The pending Stakeholder was reviewed by request as "user3"'
        )) is not True:
            return False

        """
        User 2 (Cambodia moderator)
        """
        session = requests.Session()
        user = self.getUser(2)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Laos')

        request = session.post(
            self.getReviewUrl('stakeholders'),
            data=payload,
            cookies=cookies
        )

        # Make sure the review request returned 401
        if (self.handleResult(
            request.status_code == 401,
            'The request to do a review as "user2" in Laos profile did not return 401 (unauthorized)'
        )) is not True:
            return False

        # Make sure the Stakeholder was not reviewed
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1.get_status_id() == 1,
            'The pending Stakeholder was reviewed by request as "user2" in Laos profile'
        )) is not True:
            return False

        session = requests.Session()
        user = self.getUser(2)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Cambodia')

        request = session.post(
            self.getReviewUrl('stakeholders'),
            data=payload,
            cookies=cookies
        )

        try:
            json = request.json()
            reviewSuccess = True
        except:
            reviewSuccess = False
        if (self.handleResult(
            reviewSuccess is True and json['success'] is True,
            'Review request as user2 in Cambodia profile failed.'
        )) is not True:
            return False

        # Make sure the Stakeholder is not pending anymore
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1.get_status_id() == 2,
            'The pending Stakeholder reviewed by user2 in Cambodia profile is not active after review'
        )) is not True:
            return False

        # Make sure there no other version was created
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 1,
            'Review of an active Stakeholder created more than one version.'
        )) is not True:
            return False

        return True

"""
MS 03
"""
class ModerationStakeholders03(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'MS03'
        self.testDescription = 'Rejecting a pending version sets it to "rejected"'
        self.identifier1 = 'e117ecec-f398-40c1-8d9e-cdc3572c527e'
        self.s1v1 = None
        self.createBase = CreateBase()

    def testSetup(self, verbose=False):

        # Create and check a first Stakeholder
        self.s1v1 = self.createBase.createAndCheckFirstItem(
            self,
            'stakeholders',
            Stakeholder,
            self.createBase.getCreateUrl('stakeholders'),
            self.createBase.getSomeStakeholderTags(1),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Make sure the item is pending
        if (self.handleResult(
            self.s1v1.get_status_id() == 1,
            'Stakeholder was not pending initially.'
        )) is not True:
            return False

        # Review and reject version 1
        if (self.handleResult(
            self.doReview('stakeholders', self.identifier1, 1, 2) is True,
            'Stakeholder could not be reviewed.'
        )) is not True:
            return False

        # Query the item again to check that it is now rejected
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1.get_status_id() == 5,
            'Stakeholder is not rejected after rejecting a version.'
        )) is not True:
            return False

        # Make sure there no other version was created
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 1,
            'Rejecting of an Stakeholder created more than one version.'
        )) is not True:
            return False

        return True

"""
MS 04
"""
class ModerationStakeholders04(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'MS04'
        self.testDescription = 'Reviewing a version which is not based on the active version leads to the creation of a new, recalculated version'
        self.identifier1 = '9377db6b-c422-474e-b368-baa1661d2919'
        self.s1v1 = None
        self.s1v2 = None
        self.s1v3 = None
        self.s1v4 = None
        self.createBase = CreateBase()

        self.key1 = 'Country of origin'
        self.oldValue1 = 'China'
        self.newValue1 = 'Vietnam'
        self.key2 = 'Name'
        self.oldValue2 = 'Stakeholder A'
        self.newValue2 = 'Stakeholder B'

    def testSetup(self, verbose=False):

        """
        Create a first active version
        """

        # Make sure the Stakeholder does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder exists already'
        )) is not True:
            return False

        # Create, moderate and check Stakeholder
        self.s1v1 = self.createBase.createModerateCheckFirstItem(
            self,
            'stakeholders',
            Stakeholder,
            self.createBase.getCreateUrl('stakeholders'),
            self.createBase.getSomeStakeholderTags(4, uid=self.identifier1),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created or reviewed.'
        )) is not True:
            return False


        """
        v2 (by user 2 > based on v1)
        """
        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.s1v1, self.key1, self.oldValue1)
        if (self.handleResult(
            tg_id is not None,
            'The tg_id of taggroup to change was not found.'
        )) is not True:
            return False

        # Prepare the diff
        deleteTags = self.createBase.getTagDiffsFromTags({self.key1: self.oldValue1}, 'delete')
        addTags = self.createBase.getTagDiffsFromTags({self.key1: self.newValue1}, 'add')
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags
        }
        diff = {'stakeholders': [self.createBase.getItemDiff(
            'stakeholders',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update s1v1:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.createBase.doCreate(self.createBase.getCreateUrl('stakeholders'), diff, self.getUser(2)),
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
        tg_id = self.findTgidByKeyValue(self.s1v1, self.key2, self.oldValue2)
        if (self.handleResult(
            tg_id is not None,
            'The tg_id of taggroup to change was not found.'
        )) is not True:
            return False

        # Prepare the diff
        deleteTags = self.createBase.getTagDiffsFromTags({self.key2: self.oldValue2}, 'delete')
        addTags = self.createBase.getTagDiffsFromTags({self.key2: self.newValue2}, 'add')
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags
        }
        diff = {'stakeholders': [self.createBase.getItemDiff(
            'stakeholders',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update s1v2:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.createBase.doCreate(self.createBase.getCreateUrl('stakeholders'), diff, self.getUser(3)),
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

        # Check that the status of v2 is 'pending'
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

        # Check that v2 does contain only the first change
        if (self.handleResult(
            (self.findKeyValue(self.s1v2, self.key1, self.oldValue1) is False and
                self.findKeyValue(self.s1v2, self.key1, self.newValue1) is True),
            'Version 2 does not contain the changes made by user 2'
        )) is not True:
            return False

        # Check that v2 does not contain the second change
        if (self.handleResult(
            (self.findKeyValue(self.s1v2, self.key2, self.oldValue2) is True and
                self.findKeyValue(self.s1v2, self.key2, self.newValue2) is False),
            'Version 2 also contains the second change'
        )) is not True:
            return False

        # Check that v3 does contain only the second change
        if (self.handleResult(
            (self.findKeyValue(self.s1v3, self.key1, self.oldValue1) is True and
                self.findKeyValue(self.s1v3, self.key1, self.newValue1) is False),
            'Version 3 also contains the changes made by user 2'
        )) is not True:
            return False

        # Check that v3 contains both changes
        if (self.handleResult(
            (self.findKeyValue(self.s1v3, self.key2, self.oldValue2) is False and
                self.findKeyValue(self.s1v3, self.key2, self.newValue2) is True),
            'Version 3 does not contain the changes made by user 3'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Count all versios to make sure there are 3
        initialVersionCount = self.countVersions(Stakeholder, self.identifier1)
        if (self.handleResult(
            initialVersionCount == 3,
            'There are not 3 Versions available initially'
        )) is not True:
            return False

        # First, review and accept v2
        if (self.handleResult(
            self.doReview('stakeholders', self.identifier1, 2, 1) is True,
            'Stakeholder v2 could not be reviewed.'
        )) is not True:
            return False

        # Query the item again to check that it is now active
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.s1v2.get_status_id() == 2,
            'Stakeholder v2 is not active after approving it.'
        )) is not True:
            return False

         # Make sure that v1 is now inactive
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1.get_status_id() == 3,
            'Stakeholder v1 not inactive after approving v2'
        )) is not True:
            return False

        # Make sure there was no other version created
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == initialVersionCount,
            'Approving v2 created another version'
        )) is not True:
            return False

        # Then review and accept v3
        if (self.handleResult(
            self.doReview('stakeholders', self.identifier1, 3, 1) is True,
            'Stakeholder v3 could not be reviewed.'
        )) is not True:
            return False

        # This should have created another version
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == initialVersionCount + 1,
            'Approving v3 did not create another version'
        )) is not True:
            return False

        # Query v3 again to check that it is now edited
        self.s1v3 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 3
        )
        if (self.handleResult(
            self.s1v3.get_status_id() == 6,
            'Stakeholder v3 is edited after approving it'
        )) is not True:
            return False

        # Query v2 again to check that it is not inactive
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.s1v2.get_status_id() == 3,
            'Stakeholder v2 is not inactive after approving v3'
        )) is not True:
            return False

        # A new version (4) should be available
        self.s1v4 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 4
        )
        if (self.handleResult(
            self.s1v4.get_status_id() == 2,
            'Newly created version 4 (recalculated) is not active'
        )) is not True:
            return False

        # Version 4 should contain both the changes made to v2 and v3
        if (self.handleResult(
            (self.findKeyValue(self.s1v4, self.key1, self.oldValue1) is False and
                self.findKeyValue(self.s1v4, self.key1, self.newValue1) is True),
            'Recalculated version 4 does not contain the changes made by user 2'
        )) is not True:
            return False
        if (self.handleResult(
            (self.findKeyValue(self.s1v4, self.key2, self.oldValue2) is False and
                self.findKeyValue(self.s1v4, self.key2, self.newValue2) is True),
            'Recalculated version 4 does not contain the changes made by user 3'
        )) is not True:
            return False

        return True

"""
MS 05
"""
class ModerationStakeholders05(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'MS05'
        self.testDescription = 'Versions do not have to be reviewed chronologically'
        self.identifier1 = '468b0389-a079-4d43-a62a-af5b7a164f90'
        self.s1v1 = None
        self.s1v2 = None
        self.s1v3 = None
        self.s1v4 = None
        self.identifier2 = '885b6b0d-b90f-4391-914a-f53973df3070'
        self.s2v1 = None
        self.s2v2 = None
        self.s2v3 = None
        self.s2v4 = None
        self.createBase = CreateBase()

        self.key1 = 'Country of origin'
        self.oldValue1 = 'China'
        self.newValue1 = 'Vietnam'
        self.key2 = 'Name'
        self.oldValue2 = 'Stakeholder A'
        self.newValue2 = 'Stakeholder B'

    def testSetup(self, verbose=False):

        """
        S1: Create a first active version
        """
        # Make sure the Stakeholder does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder 1 exists already'
        )) is not True:
            return False

        # Create, moderate and check Stakeholder 1
        self.s1v1 = self.createBase.createModerateCheckFirstItem(
            self,
            'stakeholders',
            Stakeholder,
            self.createBase.getCreateUrl('stakeholders'),
            self.createBase.getSomeStakeholderTags(4, uid=self.identifier1),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder 1 was not created or reviewed.'
        )) is not True:
            return False

        """
        S2: Create a first active version
        """
        # Make sure the Stakeholder does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier2) == 0,
            'Stakeholder 2 exists already'
        )) is not True:
            return False

        # Create, moderate and check Stakeholder 2
        self.s2v1 = self.createBase.createModerateCheckFirstItem(
            self,
            'stakeholders',
            Stakeholder,
            self.createBase.getCreateUrl('stakeholders'),
            self.createBase.getSomeStakeholderTags(4, uid=self.identifier2),
            self.identifier2,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s2v1 is not None and self.s2v1 is not False,
            'Stakeholder 2 was not created or reviewed.'
        )) is not True:
            return False

        """
        s1v2 (by user 2 > based on s1v1)
        """
        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.s1v1, self.key1, self.oldValue1)
        if (self.handleResult(
            tg_id is not None,
            'S1: The tg_id of taggroup to change was not found.'
        )) is not True:
            return False

        # Prepare the diff
        deleteTags = self.createBase.getTagDiffsFromTags({self.key1: self.oldValue1}, 'delete')
        addTags = self.createBase.getTagDiffsFromTags({self.key1: self.newValue1}, 'add')
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags
        }
        diff = {'stakeholders': [self.createBase.getItemDiff(
            'stakeholders',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update s1v1:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.createBase.doCreate(self.createBase.getCreateUrl('stakeholders'), diff, self.getUser(2)),
            'The Stakeholder 1 could not be updated.'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier1)
                and self.s1v2 is not None),
            'Version 2 of the updated Stakeholder 1 was not found.'
        )) is not True:
            return False

        """
        s2v2 (by user 2 > based on s1v1)
        """
        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.s2v1, self.key1, self.oldValue1)
        if (self.handleResult(
            tg_id is not None,
            'S2: The tg_id of taggroup to change was not found.'
        )) is not True:
            return False

        # Prepare the diff
        deleteTags = self.createBase.getTagDiffsFromTags({self.key1: self.oldValue1}, 'delete')
        addTags = self.createBase.getTagDiffsFromTags({self.key1: self.newValue1}, 'add')
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags
        }
        diff = {'stakeholders': [self.createBase.getItemDiff(
            'stakeholders',
            id = self.identifier2,
            version = 1,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update s2v1:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.createBase.doCreate(self.createBase.getCreateUrl('stakeholders'), diff, self.getUser(2)),
            'The Stakeholder 2 could not be updated.'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s2v2 = self.protocol.read_one_by_version(
            self.request, self.identifier2, 2
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier2)
                and self.s2v2 is not None),
            'Version 2 of the updated Stakeholder 2 was not found.'
        )) is not True:
            return False

        """
        s1v3 (by user 3 > based on v1)
        """
        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.s1v1, self.key2, self.oldValue2)
        if (self.handleResult(
            tg_id is not None,
            'S1: The tg_id of taggroup to change was not found.'
        )) is not True:
            return False

        # Prepare the diff
        deleteTags = self.createBase.getTagDiffsFromTags({self.key2: self.oldValue2}, 'delete')
        addTags = self.createBase.getTagDiffsFromTags({self.key2: self.newValue2}, 'add')
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags
        }
        diff = {'stakeholders': [self.createBase.getItemDiff(
            'stakeholders',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update s1v2:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.createBase.doCreate(self.createBase.getCreateUrl('stakeholders'), diff, self.getUser(3)),
            'The Stakeholder 1 could not be updated.'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s1v3 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 3
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier1)
                and self.s1v3 is not None),
            'Version 3 of the updated Stakeholder 1 was not found.'
        )) is not True:
            return False

        """
        s2v3 (by user 3 > based on v1)
        """
        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.s2v1, self.key2, self.oldValue2)
        if (self.handleResult(
            tg_id is not None,
            'S2: The tg_id of taggroup to change was not found.'
        )) is not True:
            return False

        # Prepare the diff
        deleteTags = self.createBase.getTagDiffsFromTags({self.key2: self.oldValue2}, 'delete')
        addTags = self.createBase.getTagDiffsFromTags({self.key2: self.newValue2}, 'add')
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags
        }
        diff = {'stakeholders': [self.createBase.getItemDiff(
            'stakeholders',
            id = self.identifier2,
            version = 1,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update s2v2:\n%s' % diff)

        # Update the Stakeholder
        if (self.handleResult(
            self.createBase.doCreate(self.createBase.getCreateUrl('stakeholders'), diff, self.getUser(3)),
            'The Stakeholder 2 could not be updated.'
        )) is not True:
            return False

        # Check that a new Stakeholder was created
        self.s2v3 = self.protocol.read_one_by_version(
            self.request, self.identifier2, 3
        )
        if (self.handleResult(
            (self.countVersions(Stakeholder, self.identifier2)
                and self.s2v3 is not None),
            'Version 3 of the updated Stakeholder 2 was not found.'
        )) is not True:
            return False

        # Re-query v2
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )

        # Check that the status of v2 is 'pending'
        if (self.handleResult(
            self.s1v2.get_status_id() == 1,
            'S1: The status of version 2 is not "pending"'
        )) is not True:
            return False

        # Re-query v2
        self.s2v2 = self.protocol.read_one_by_version(
            self.request, self.identifier2, 2
        )

        # Check that the status of v2 is 'pending'
        if (self.handleResult(
            self.s2v2.get_status_id() == 1,
            'S2: The status of version 2 is not "pending"'
        )) is not True:
            return False

        # Check that the status of v3 is 'pending'
        if (self.handleResult(
            self.s1v3.get_status_id() == 1,
            'S1: The status of version 3 is not "pending"'
        )) is not True:
            return False

        # Check that the status of v3 is 'pending'
        if (self.handleResult(
            self.s2v3.get_status_id() == 1,
            'S2: The status of version 3 is not "pending"'
        )) is not True:
            return False

        # Check that v2 does contain only the first change
        if (self.handleResult(
            (self.findKeyValue(self.s1v2, self.key1, self.oldValue1) is False and
                self.findKeyValue(self.s1v2, self.key1, self.newValue1) is True),
            'S1: Version 2 does not contain the changes made by user 2'
        )) is not True:
            return False

        # Check that v2 does not contain the second change
        if (self.handleResult(
            (self.findKeyValue(self.s1v2, self.key2, self.oldValue2) is True and
                self.findKeyValue(self.s1v2, self.key2, self.newValue2) is False),
            'S2: Version 2 also contains the second change'
        )) is not True:
            return False

        # Check that v2 does contain only the first change
        if (self.handleResult(
            (self.findKeyValue(self.s2v2, self.key1, self.oldValue1) is False and
                self.findKeyValue(self.s2v2, self.key1, self.newValue1) is True),
            'S2: Version 2 does not contain the changes made by user 2'
        )) is not True:
            return False

        # Check that v2 does not contain the second change
        if (self.handleResult(
            (self.findKeyValue(self.s2v2, self.key2, self.oldValue2) is True and
                self.findKeyValue(self.s2v2, self.key2, self.newValue2) is False),
            'S2: Version 2 also contains the second change'
        )) is not True:
            return False

        # Check that v3 does contain only the second change
        if (self.handleResult(
            (self.findKeyValue(self.s1v3, self.key1, self.oldValue1) is True and
                self.findKeyValue(self.s1v3, self.key1, self.newValue1) is False),
            'S1: Version 3 also contains the changes made by user 2'
        )) is not True:
            return False

        # Check that v3 contains both changes
        if (self.handleResult(
            (self.findKeyValue(self.s1v3, self.key2, self.oldValue2) is False and
                self.findKeyValue(self.s1v3, self.key2, self.newValue2) is True),
            'S1: Version 3 does not contain the changes made by user 3'
        )) is not True:
            return False

        # Check that v3 does contain only the second change
        if (self.handleResult(
            (self.findKeyValue(self.s2v3, self.key1, self.oldValue1) is True and
                self.findKeyValue(self.s2v3, self.key1, self.newValue1) is False),
            'S2: Version 3 also contains the changes made by user 2'
        )) is not True:
            return False

        # Check that v3 contains both changes
        if (self.handleResult(
            (self.findKeyValue(self.s2v3, self.key2, self.oldValue2) is False and
                self.findKeyValue(self.s2v3, self.key2, self.newValue2) is True),
            'S2: Version 3 does not contain the changes made by user 3'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        """
        S1
        """
        # Count all versios to make sure there are 3
        initialVersionCount = self.countVersions(Stakeholder, self.identifier1)
        if (self.handleResult(
            initialVersionCount == 3,
            'A1: There are not 3 Versions available initially'
        )) is not True:
            return False

        # First, review and accept v2
        if (self.handleResult(
            self.doReview('stakeholders', self.identifier1, 2, 1) is True,
            'Stakeholder 1 v2 could not be reviewed.'
        )) is not True:
            return False

        # Query the item again to check that it is now active
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.s1v2.get_status_id() == 2,
            'Stakeholder 1 v2 is not active after approving it.'
        )) is not True:
            return False

         # Make sure that v1 is now inactive
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1.get_status_id() == 3,
            'Stakeholder 1 v1 not inactive after approving v2'
        )) is not True:
            return False

        # Make sure there was no other version created
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == initialVersionCount,
            'Approving 1 v2 created another version'
        )) is not True:
            return False

        # Then review and accept v3
        if (self.handleResult(
            self.doReview('stakeholders', self.identifier1, 3, 1) is True,
            'Stakeholder 1 v3 could not be reviewed.'
        )) is not True:
            return False

        # This should have created another version
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == initialVersionCount + 1,
            'Approving 1 v3 did not create another version'
        )) is not True:
            return False

        # Query v3 again to check that it is now edited
        self.s1v3 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 3
        )
        if (self.handleResult(
            self.s1v3.get_status_id() == 6,
            'Stakeholder 1 v3 is edited after approving it'
        )) is not True:
            return False

        # Query v2 again to check that it is not inactive
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.s1v2.get_status_id() == 3,
            'Stakeholder 1 v2 is not inactive after approving v3'
        )) is not True:
            return False

        # A new version (4) should be available
        self.s1v4 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 4
        )
        if (self.handleResult(
            self.s1v4.get_status_id() == 2,
            'Newly created version 4 (recalculated) of Stakeholder 1 is not active'
        )) is not True:
            return False

        # Version 4 should contain both the changes made to v2 and v3
        if (self.handleResult(
            (self.findKeyValue(self.s1v4, self.key1, self.oldValue1) is False and
                self.findKeyValue(self.s1v4, self.key1, self.newValue1) is True),
            'Recalculated version 4 of Stakeholder 1 does not contain the changes made by user 2'
        )) is not True:
            return False
        if (self.handleResult(
            (self.findKeyValue(self.s1v4, self.key2, self.oldValue2) is False and
                self.findKeyValue(self.s1v4, self.key2, self.newValue2) is True),
            'Recalculated version 4 of Stakeholder 1 does not contain the changes made by user 3'
        )) is not True:
            return False

        """
        S2
        """
        # Count all versios to make sure there are 3
        initialVersionCount = self.countVersions(Stakeholder, self.identifier2)
        if (self.handleResult(
            initialVersionCount == 3,
            'S2: There are not 3 Versions available initially'
        )) is not True:
            return False

        # First, review and accept v3
        if (self.handleResult(
            self.doReview('stakeholders', self.identifier2, 3, 1) is True,
            'Stakeholder 2 v3 could not be reviewed.'
        )) is not True:
            return False

        # Query the item again to check that it is now active
        self.s2v3 = self.protocol.read_one_by_version(
            self.request, self.identifier2, 3
        )
        if (self.handleResult(
            self.s2v3.get_status_id() == 2,
            'Stakeholder 2 v3 is not active after approving it.'
        )) is not True:
            return False

         # Make sure that v1 is now inactive
        self.s2v1 = self.protocol.read_one_by_version(
            self.request, self.identifier2, 1
        )
        if (self.handleResult(
            self.s2v1.get_status_id() == 3,
            'Stakeholder 2 v1 not inactive after approving v2'
        )) is not True:
            return False

        # Make sure there was no other version created
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier2) == initialVersionCount,
            'Approving 2 v2 created another version'
        )) is not True:
            return False

        # Then review and accept v2
        if (self.handleResult(
            self.doReview('stakeholders', self.identifier2, 2, 1) is True,
            'Stakeholder 2 v2 could not be reviewed.'
        )) is not True:
            return False

        # This should have created another version
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier2) == initialVersionCount + 1,
            'Approving 2 v2 did not create another version'
        )) is not True:
            return False

        # Query v2 again to check that it is now edited
        self.s2v2 = self.protocol.read_one_by_version(
            self.request, self.identifier2, 2
        )
        if (self.handleResult(
            self.s2v2.get_status_id() == 6,
            'Stakeholder 2 v2 is edited after approving it'
        )) is not True:
            return False

        # Query v3 again to check that it is not inactive
        self.s2v3 = self.protocol.read_one_by_version(
            self.request, self.identifier2, 3
        )
        if (self.handleResult(
            self.s2v3.get_status_id() == 3,
            'Stakeholder 2 v3 is not inactive after approving v3'
        )) is not True:
            return False

        # A new version (4) should be available
        self.s2v4 = self.protocol.read_one_by_version(
            self.request, self.identifier2, 4
        )
        if (self.handleResult(
            self.s2v4.get_status_id() == 2,
            'Newly created version 4 (recalculated) of Stakeholder 2 is not active'
        )) is not True:
            return False

        # Version 4 should contain both the changes made to v2 and v3
        if (self.handleResult(
            (self.findKeyValue(self.s2v4, self.key1, self.oldValue1) is False and
                self.findKeyValue(self.s2v4, self.key1, self.newValue1) is True),
            'Recalculated version 4 of Stakeholder 2 does not contain the changes made by user 2'
        )) is not True:
            return False
        if (self.handleResult(
            (self.findKeyValue(self.s2v4, self.key2, self.oldValue2) is False and
                self.findKeyValue(self.s2v4, self.key2, self.newValue2) is True),
            'Recalculated version 4 of Stakeholder 2 does not contain the changes made by user 3'
        )) is not True:
            return False

        return True

"""
MS06
"""
class ModerationStakeholders06(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'MS06'
        self.testDescription = 'A version without all mandatory keys cannot be set to "active"'
        self.identifier1 = 'e743ce58-8f19-471a-bcc7-d29af664d371'
        self.s1v1 = None
        self.createBase = CreateBase()

    def testSetup(self, verbose=False):

        """
        Create a first active version with missing mandatory keys
        """
        # Make sure the Stakeholder does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder 1 exists already'
        )) is not True:
            return False

        # Create, moderate and check Stakeholder 1
        self.s1v1 = self.createBase.createAndCheckFirstItem(
            self,
            'stakeholders',
            Stakeholder,
            self.createBase.getCreateUrl('stakeholders'),
            self.createBase.getSomeStakeholderTags(3),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder 1 was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Query the item again
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )

        # Make sure the item is pending
        if (self.handleResult(
            self.s1v1.get_status_id() == 1,
            'Stakeholder was not pending initially.'
        )) is not True:
            return False

        # Try to review and accept version 1
        if (self.handleResult(
            self.doReview('stakeholders', self.identifier1, 1, 1) is False,
            'Stakeholder could be approved although it does not contain all mandatory keys'
        )) is not True:
            return False

        # Try to review it again, manually
        # Prepare general stuff needed for moderation
        import requests
        import json
        # Prepare payload
        payload = {
            'version': 1,
            'identifier': self.identifier1,
            'review_decision': 1,
            'comment_textarea': ''
        }

        session = requests.Session()
        user = self.getUser(1)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Laos')

        request = session.post(
            self.getReviewUrl('stakeholders'),
            data=payload,
            cookies=cookies
        )

        # Make sure the review request returned 400
        if (self.handleResult(
            request.status_code == 400,
            'The request to do a review on an Stakeholder with missing mandatory keys did not return error code 400'
        )) is not True:
            return False

        # Query the item again to check that it is still pending
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1.get_status_id() == 1,
            'Stakeholder is not pending anymore after approvement (which should have failed)'
        )) is not True:
            return False

        # Try to review and reject version 1
        if (self.handleResult(
            self.doReview('stakeholders', self.identifier1, 1, 2) is True,
            'Stakeholder with missing mandatory keys could not be rejected'
        )) is not True:
            return False

        # Query the item again to check that it is now rejected
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1.get_status_id() == 5,
            'Stakeholder is not rejected after rejecting it in review'
        )) is not True:
            return False

        # Make sure there no other version was created
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 1,
            'Review (reject) of an Stakeholder with missing mandatory keys created more than one version.'
        )) is not True:
            return False

        return True

"""
MS07
"""
class ModerationStakeholders07(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'MS07'
        self.testDescription = 'Reviewing an Involvement from Stakeholder is not possible'
        self.identifier1 = '9a7144fa-a36d-4ce5-8494-4127ea6627f1'
        self.s1v1 = None
        self.s1v2 = None
        self.createBase = CreateBase()

        from lmkp.views.activity_protocol3 import ActivityProtocol3
        self.otherProtocol = ActivityProtocol3(Session)
        self.identifier2 = '45ef1b21-66d8-441b-8d1d-40d589fdda71'
        self.a1v1 = None
        self.a1v2 = None
        self.invRole1 = self.getStakeholderRole(6)

    def testSetup(self, verbose=False):

        """
        Create a first active version of the Stakeholder
        """
        # Make sure the Stakeholder does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder exists already'
        )) is not True:
            return False

        # Create, moderate and check Stakeholder
        self.s1v1 = self.createBase.createModerateCheckFirstItem(
            self,
            'stakeholders',
            Stakeholder,
            self.createBase.getCreateUrl('stakeholders'),
            self.createBase.getSomeStakeholderTags(4, uid=self.identifier1),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created or reviewed.'
        )) is not True:
            return False

        """
        Create a first active version of the Activity
        """
        # Make sure the Activity does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier2) == 0,
            'Activity exists already'
        )) is not True:
            return False

        # Create, moderate and check Activity
        self.a1v1 = self.createBase.createModerateCheckFirstItem(
            self,
            'activities',
            Activity,
            self.createBase.getCreateUrl('activities'),
            self.createBase.getSomeActivityTags(4, uid=self.identifier2),
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

        diff = {'activities': [self.createBase.getItemDiff(
            'activities',
            id = self.identifier2,
            version = 1,
            taggroups = [],
            involvements = [
                {
                    'id': self.identifier1,
                    'version': 1,
                    'role': self.invRole1['id'],
                    'op': 'add'
                }
            ]
        )]}

        # Update the Activity
        if (self.handleResult(
            self.createBase.doCreate(self.createBase.getCreateUrl('activities'), diff, self.getUser(2)),
            'The Activity could not be updated.'
        )) is not True:
            return False

        # Try to review and accept version 2 of the Stakeholder
        if (self.handleResult(
            self.doReview('stakeholders', self.identifier1, 2, 1) is False,
            'The Stakeholder could somehow be set active!'
        )) is not True:
            return False

        # Make sure the Stakeholder is still pending
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.s1v2.get_status_id() == 1,
            'Stakeholder (v2) is not pending anymore!'
        )) is not True:
            return False

        # Make sure the Activity is still pending
        self.a1v2 = self.otherProtocol.read_one_by_version(
            self.request, self.identifier2, 2
        )
        if (self.handleResult(
            self.a1v2.get_status_id() == 1,
            'Activity (v2) is not pending anymore!'
        )) is not True:
            return False

        return True

"""
MS08
"""
class ModerationStakeholders08(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'MS08'
        self.testDescription = 'Activity attributes cannot be reviewed from Stakeholder side'
        self.identifier1 = 'd5e14eb3-f38f-4bc1-bc27-963b0d975bfa'
        self.s1v1 = None
        self.s1v2 = None
        self.createBase = CreateBase()

        from lmkp.views.activity_protocol3 import ActivityProtocol3
        self.otherProtocol = ActivityProtocol3(Session)
        self.identifier2 = 'd0f5b496-edcd-458c-84a9-72ca4e1135f5'
        self.a1v1 = None
        self.a1v2 = None
        self.invRole1 = self.getStakeholderRole(6)

    def testSetup(self, verbose=False):

        """
        Create a first active version of the Stakeholder
        """
        # Make sure the Stakeholder does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder exists already'
        )) is not True:
            return False

        # Create, moderate and check Stakeholder
        self.s1v1 = self.createBase.createModerateCheckFirstItem(
            self,
            'stakeholders',
            Stakeholder,
            self.createBase.getCreateUrl('stakeholders'),
            self.createBase.getSomeStakeholderTags(4, uid=self.identifier1),
            self.identifier1,
            self.getUser(1)
        )

        if (self.handleResult(
            self.s1v1 is not None and self.s1v1 is not False,
            'Stakeholder was not created or reviewed.'
        )) is not True:
            return False

        """
        Create a first active version of the Activity
        """
        # Make sure the Activity does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier2) == 0,
            'Activity exists already'
        )) is not True:
            return False

        # Create, moderate and check Activity
        self.a1v1 = self.createBase.createModerateCheckFirstItem(
            self,
            'activities',
            Activity,
            self.createBase.getCreateUrl('activities'),
            self.createBase.getSomeActivityTags(4, uid=self.identifier2),
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

        key = 'Intention of Investment'
        oldValue = 'Agriculture'
        newValue = 'Mining'

        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.a1v1, key, oldValue)
        if (self.handleResult(
            tg_id is not None,
            'The tg_id of taggroup to change was not found.'
        )) is not True:
            return False

        # Create a diff to modify the Activity and add an involvement
        deleteTags = self.createBase.getTagDiffsFromTags({key: oldValue}, 'delete')
        addTags = self.createBase.getTagDiffsFromTags({key: newValue}, 'add')
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags
        }
        diff = {'activities': [self.createBase.getItemDiff(
            'activities',
            id = self.identifier2,
            version = 1,
            taggroups = [taggroup],
            involvements = [
                {
                    'id': self.identifier1,
                    'version': 1,
                    'role': self.invRole1['id'],
                    'op': 'add'
                }
            ]
        )]}

        # Update the Activity
        if (self.handleResult(
            self.createBase.doCreate(self.createBase.getCreateUrl('activities'), diff, self.getUser(2)),
            'The Activity could not be updated.'
        )) is not True:
            return False

        # Try to review and accept version 2 of the Stakeholder
        if (self.handleResult(
            self.doReview('stakeholders', self.identifier1, 2, 1) is False,
            'Stakeholder was reviewed even though the Activity on the other side of involvement had changed attributes'
        )) is not True:
            return False

        # Query the Stakeholder to check that it is still pending
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.s1v2.get_status_id() == 1,
            'Stakeholder (v2) is not pending anymore'
        )) is not True:
            return False

        # Also make sure the Activity is still pending
        self.a1v2 = self.otherProtocol.read_one_by_version(
            self.request, self.identifier2, 2
        )
        if (self.handleResult(
            self.a1v2.get_status_id() == 1,
            'Activity (v2) is not pending anymore'
        )) is not True:
            return False

        # Try to review and accept version 2 of the Activity
        if (self.handleResult(
            self.doReview('activities', self.identifier2, 2, 1) is True,
            'The Activity could not be set active'
        )) is not True:
            return False

        # Make sure the Activity is not pending anymore
        self.a1v2 = self.otherProtocol.read_one_by_version(
            self.request, self.identifier2, 2
        )
        if (self.handleResult(
            self.a1v2.get_status_id() == 2,
            'Activity (v2) is not active!'
        )) is not True:
            return False

        # Make sure the Stakeholder is not pending anymore
        self.s1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.s1v2.get_status_id() == 2,
            'Stakeholder (v2) is not active!'
        )) is not True:
            return False

        # Make sure the Activity has a changed attribute
        if (self.handleResult(
            (self.findKeyValue(self.a1v2, key, oldValue) is False and
                self.findKeyValue(self.a1v2, key, newValue) is True),
            'The new value of v2 was not correctly set'
        )) is not True:
            return False

        # Make sure the Stakeholder has an involvement
        if (self.handleResult(
            len(self.s1v2.get_involvements()) == 1,
            'Stakeholder v2 does not have an Involvement'
        )) is not True:
            return False

        return True