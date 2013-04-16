from lmkp.tests.moderate.moderation_base import ModerationBase
from lmkp.tests.create.create_base import CreateBase

from lmkp.models.meta import DBSession as Session
from lmkp.models.database_objects import *
from lmkp.views.activity_protocol3 import ActivityProtocol3

"""
MA 01
"""
class ModerationActivities01(ModerationBase):
    
    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "MA01"
        self.testDescription = 'It is possible to review an Activity'
        self.identifier1 = '93c040ff-229a-461b-85b2-ad5da0db56e1'
        self.a1v1 = None
        self.createBase = CreateBase()
        
    def testSetup(self, vebose=False):

        # Create and check a first Activity
        self.a1v1 = self.createBase.createAndCheckFirstItem(
            self,
            'activities',
            Activity,
            self.createBase.getCreateUrl('activities'),
            self.createBase.getSomeActivityTags(1),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Make sure the item is pending
        if (self.handleResult(
            self.a1v1.get_status_id() == 1,
            'Activity was not pending initially.'
        )) is not True:
            return False
        
        # Review and accept version 1
        if (self.handleResult(
            self.doReview('activities', self.identifier1, 1, 1) is True,
            'Activity could not be reviewed.'
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

        # Make sure there no other version was created
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 1,
            'Review of an active Activity created more than one version.'
        )) is not True:
            return False

        return True

"""
MA 02
"""
class ModerationActivities02(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "MA02"
        self.testDescription = 'Only logged in users with moderation privileges can review an Activity'
        self.identifier1 = 'a00b0732-96b4-499d-9e0e-6e393e668c76'
        self.a1v1 = None
        self.createBase = CreateBase()

    def testSetup(self, verbose=False):

        # Create and check a first Activity
        self.a1v1 = self.createBase.createAndCheckFirstItem(
            self,
            'activities',
            Activity,
            self.createBase.getCreateUrl('activities'),
            self.createBase.getSomeActivityTags(1),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Make sure the item is pending
        if (self.handleResult(
            self.a1v1.get_status_id() == 1,
            'Activity was not pending initially.'
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
            self.getReviewUrl('activities'),
            data=payload,
            cookies=cookies
        )

        # Make sure the review request returned 401
        if (self.handleResult(
            request.status_code == 401,
            'The request to do a review as "not logged in" did not return 401 (unauthorized)'
        )) is not True:
            return False

        # Make sure the Activity was not reviewed
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 1,
            'The pending Activity was reviewed by request as "not logged in"'
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
            self.getReviewUrl('activities'),
            data=payload,
            cookies=cookies
        )

        # Make sure the review request returned 401
        if (self.handleResult(
            request.status_code == 401,
            'The request to do a review as "user3" did not return 401 (unauthorized)'
        )) is not True:
            return False

        # Make sure the Activity was not reviewed
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 1,
            'The pending Activity was reviewed by request as "user3"'
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
            self.getReviewUrl('activities'),
            data=payload,
            cookies=cookies
        )

        # Make sure the review request returned 401
        if (self.handleResult(
            request.status_code == 401,
            'The request to do a review as "user2" in Lao profile did not return 401 (unauthorized)'
        )) is not True:
            return False

        # Make sure the Activity was not reviewed
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 1,
            'The pending Activity was reviewed by request as "user2" in Lao profile'
        )) is not True:
            return False

        session = requests.Session()
        user = self.getUser(2)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Cambodia')

        request = session.post(
            self.getReviewUrl('activities'),
            data=payload,
            cookies=cookies
        )

        # Make sure the review request returned 401
        if (self.handleResult(
            request.status_code == 401,
            'The request to do a review as "user2" in Cambodia profile did not return 401 (unauthorized)'
        )) is not True:
            return False

        # Make sure the Activity was not reviewed
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 1,
            'The pending Activity was reviewed by request as "2" in Cambodia profile'
        )) is not True:
            return False

        """
        User 1 (Laos moderator)
        """
        session = requests.Session()
        user = self.getUser(1)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Cambodia')

        request = session.post(
            self.getReviewUrl('activities'),
            data=payload,
            cookies=cookies
        )

        # Make sure the review request returned 401
        if (self.handleResult(
            request.status_code == 401,
            'The request to do a review as "user1" in Cambodia profile did not return 401 (unauthorized)'
        )) is not True:
            return False

        # Make sure the Activity was not reviewed
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 1,
            'The pending Activity was reviewed by request as "user1" in Cambodia profile'
        )) is not True:
            return False

        session = requests.Session()
        user = self.getUser(1)
        session.auth = (user['username'], user['password'])
        cookies = dict(_PROFILE_='Laos')

        request = session.post(
            self.getReviewUrl('activities'),
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
            'Review request as user1 in Lao profile failed.'
        )) is not True:
            return False

        # Make sure the Activity is not pending anymore
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 2,
            'The pending Activity reviewed by user1 in Lao profile is not active after review'
        )) is not True:
            return False

        # Make sure there no other version was created
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 1,
            'Review of an active Activity created more than one version.'
        )) is not True:
            return False

        return True
    
"""
MA 03
"""
class ModerationActivities03(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'MA03'
        self.testDescription = 'Activities can only be reviewed within the profile boundaries of the moderator'
        self.identifier1 = 'a013512e-7267-499f-bc46-845c1a94b77d'
        self.a1v1 = None
        self.createBase = CreateBase()

    def testSetup(self, verbose=False):

        diff = self.createBase.getSomeWholeDiff(
            'activities',
            self.createBase.getSomeActivityTags(1),
            self.identifier1,
            1,
            'add',
            {
                'type': 'Point',
                'coordinates': [
                    49,
                    6
                ]
            }
        )

        if verbose is True:
            log.debug('Diff to create a1v1:\n%s' % diff)

        # Create the Activity
        if (self.handleResult(
            self.createBase.doCreate(self.createBase.getCreateUrl('activities'), diff, self.getUser(1)),
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

        return True

    def doTest(self, verbose=False):

        # Make sure the item is pending
        if (self.handleResult(
            self.a1v1.get_status_id() == 1,
            'Activity was not pending initially.'
        )) is not True:
            return False

        import requests
        session = requests.Session()
        user = self.getUser(1)
        session.auth = (user['username'], user['password'])

        cookies = dict(_PROFILE_='Laos')
        payload = {
            'version': 1,
            'identifier': self.identifier1,
            'review_decision': 1,
            'comment_textarea': ''
        }

        request = session.post(
            self.getReviewUrl('activities'),
            data=payload,
            cookies=cookies
        )

        # Make sure the review request returned 401
        if (self.handleResult(
            request.status_code == 401,
            'Laos moderator was able to do a review request although activity is not in profile bounds'
        )) is not True:
            return False

        # Make sure the Activity was not reviewed
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 1,
            'The pending Activity not situated in Laos was reviewed by user1 (Laos moderator)'
        )) is not True:
            return False

        return True

"""
MA 04
"""
class ModerationActivities04(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'MA04'
        self.testDescription = 'Rejecting a pending version sets it to \'rejected\''
        self.identifier1 = '97853010-520c-48a8-99cb-9f52fb35641f'
        self.a1v1 = None
        self.createBase = CreateBase()

    def testSetup(self, vebose=False):

        # Create and check a first Activity
        self.a1v1 = self.createBase.createAndCheckFirstItem(
            self,
            'activities',
            Activity,
            self.createBase.getCreateUrl('activities'),
            self.createBase.getSomeActivityTags(1),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Make sure the item is pending
        if (self.handleResult(
            self.a1v1.get_status_id() == 1,
            'Activity was not pending initially.'
        )) is not True:
            return False

        # Review and reject version 1
        if (self.handleResult(
            self.doReview('activities', self.identifier1, 1, 2) is True,
            'Activity could not be reviewed.'
        )) is not True:
            return False

        # Query the item again to check that it is now rejected
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 5,
            'Activity is not rejected after rejecting a version.'
        )) is not True:
            return False

        # Make sure there no other version was created
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 1,
            'Rejecting of an Activity created more than one version.'
        )) is not True:
            return False

        return True

"""
MA 05
"""
class ModerationActivities05(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'MA05'
        self.testDescription = 'Reviewing a version which is not based on the active version leads to the creation of a new, recalculated version'
        self.identifier1 = 'acdbeacf-c366-4f28-87bc-ec0415429df4'
        self.a1v1 = None
        self.a1v2 = None
        self.a1v3 = None
        self.a1v4 = None
        self.createBase = CreateBase()

        self.key1 = None
        self.oldValue1 = None
        self.newValue1 = None
        self.key2 = None
        self.oldValue2 = None
        self.newValue2 = None

    def testSetup(self, verbose=False):

        """
        Create a first active version
        """

        # Make sure the Activity does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity exists already'
        )) is not True:
            return False

        # Create, moderate and check Activity
        self.a1v1 = self.createBase.createModerateCheckFirstItem(
            self,
            'activities',
            Activity,
            self.createBase.getCreateUrl('activities'),
            self.createBase.getSomeActivityTags(4, uid=self.identifier1),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created or reviewed.'
        )) is not True:
            return False

        # The values to change
        self.key1 = 'Intention of Investment'
        self.oldValue1 = 'Agriculture'
        self.newValue1 = 'Mining'

        self.key2 = 'Intended area (ha)'
        self.oldValue2 = 100
        self.newValue2 = 50

        """
        v2 (by user 2 > based on v1)
        """
        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.a1v1, self.key1, self.oldValue1)
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
        diff = {'activities': [self.createBase.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update a1v1:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.createBase.doCreate(self.createBase.getCreateUrl('activities'), diff, self.getUser(2)),
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
        tg_id = self.findTgidByKeyValue(self.a1v1, self.key2, self.oldValue2)
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
        diff = {'activities': [self.createBase.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update a1v2:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.createBase.doCreate(self.createBase.getCreateUrl('activities'), diff, self.getUser(3)),
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
            (self.findKeyValue(self.a1v2, self.key1, self.oldValue1) is False and
                self.findKeyValue(self.a1v2, self.key1, self.newValue1) is True),
            'Version 2 does not contain the changes made by user 2'
        )) is not True:
            return False

        # Check that v2 does not contain the second change
        if (self.handleResult(
            (self.findKeyValue(self.a1v2, self.key2, self.oldValue2) is True and
                self.findKeyValue(self.a1v2, self.key2, self.newValue2) is False),
            'Version 2 also contains the second change'
        )) is not True:
            return False

        # Check that v3 does contain only the second change
        if (self.handleResult(
            (self.findKeyValue(self.a1v3, self.key1, self.oldValue1) is True and
                self.findKeyValue(self.a1v3, self.key1, self.newValue1) is False),
            'Version 3 also contains the changes made by user 2'
        )) is not True:
            return False

        # Check that v3 contains both changes
        if (self.handleResult(
            (self.findKeyValue(self.a1v3, self.key2, self.oldValue2) is False and
                self.findKeyValue(self.a1v3, self.key2, self.newValue2) is True),
            'Version 3 does not contain the changes made by user 3'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Count all versios to make sure there are 3
        initialVersionCount = self.countVersions(Activity, self.identifier1)
        if (self.handleResult(
            initialVersionCount == 3,
            'There are not 3 Versions available initially'
        )) is not True:
            return False

        # First, review and accept v2
        if (self.handleResult(
            self.doReview('activities', self.identifier1, 2, 1) is True,
            'Activity v2 could not be reviewed.'
        )) is not True:
            return False

        # Query the item again to check that it is now active
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.a1v2.get_status_id() == 2,
            'Activity v2 is not active after approving it.'
        )) is not True:
            return False

         # Make sure that v1 is now inactive
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 3,
            'Activity v1 not inactive after approving v2'
        )) is not True:
            return False

        # Make sure there was no other version created
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == initialVersionCount,
            'Approving v2 created another version'
        )) is not True:
            return False

        # Then review and accept v3
        if (self.handleResult(
            self.doReview('activities', self.identifier1, 3, 1) is True,
            'Activity v3 could not be reviewed.'
        )) is not True:
            return False

        # This should have created another version
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == initialVersionCount + 1,
            'Approving v3 did not create another version'
        )) is not True:
            return False

        # Query v3 again to check that it is now edited
        self.a1v3 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 3
        )
        if (self.handleResult(
            self.a1v3.get_status_id() == 6,
            'Activity v3 is edited after approving it'
        )) is not True:
            return False

        # Query v2 again to check that it is not inactive
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.a1v2.get_status_id() == 3,
            'Activity v2 is not inactive after approving v3'
        )) is not True:
            return False

        # A new version (4) should be available
        self.a1v4 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 4
        )
        if (self.handleResult(
            self.a1v4.get_status_id() == 2,
            'Newly created version 4 (recalculated) is not active'
        )) is not True:
            return False

        # Version 4 should contain both the changes made to v2 and v3
        if (self.handleResult(
            (self.findKeyValue(self.a1v4, self.key1, self.oldValue1) is False and
                self.findKeyValue(self.a1v4, self.key1, self.newValue1) is True),
            'Recalculated version 4 does not contain the changes made by user 2'
        )) is not True:
            return False
        if (self.handleResult(
            (self.findKeyValue(self.a1v4, self.key2, self.oldValue2) is False and
                self.findKeyValue(self.a1v4, self.key2, self.newValue2) is True),
            'Recalculated version 4 does not contain the changes made by user 3'
        )) is not True:
            return False

        return True

"""
MA 06
"""
class ModerationActivities06(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'MA06'
        self.testDescription = 'Versions do not have to be reviewed chronologically'
        self.identifier1 = '1145b971-a4cd-4429-9953-254582005ea9'
        self.a1v1 = None
        self.a1v2 = None
        self.a1v3 = None
        self.a1v4 = None
        self.identifier2 = '13f1a37b-3477-4935-ab7b-29f702c64437'
        self.a2v1 = None
        self.a2v2 = None
        self.a2v3 = None
        self.a2v4 = None
        self.createBase = CreateBase()

        self.key1 = None
        self.oldValue1 = None
        self.newValue1 = None
        self.key2 = None
        self.oldValue2 = None
        self.newValue2 = None

    def testSetup(self, verbose=False):

        """
        A1: Create a first active version
        """
        # Make sure the Activity does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity 1 exists already'
        )) is not True:
            return False

        # Create, moderate and check Activity 1
        self.a1v1 = self.createBase.createModerateCheckFirstItem(
            self,
            'activities',
            Activity,
            self.createBase.getCreateUrl('activities'),
            self.createBase.getSomeActivityTags(4, uid=self.identifier1),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity 1 was not created or reviewed.'
        )) is not True:
            return False

        """
        A2: Create a first active version
        """
        # Make sure the Activity does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier2) == 0,
            'Activity 2 exists already'
        )) is not True:
            return False

        # Create, moderate and check Activity 2
        self.a2v1 = self.createBase.createModerateCheckFirstItem(
            self,
            'activities',
            Activity,
            self.createBase.getCreateUrl('activities'),
            self.createBase.getSomeActivityTags(4, uid=self.identifier2),
            self.identifier2,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a2v1 is not None and self.a2v1 is not False,
            'Activity 2 was not created or reviewed.'
        )) is not True:
            return False

        # The values to change
        self.key1 = 'Intention of Investment'
        self.oldValue1 = 'Agriculture'
        self.newValue1 = 'Mining'

        self.key2 = 'Intended area (ha)'
        self.oldValue2 = 100
        self.newValue2 = 50

        """
        A1v2 (by user 2 > based on A1v1)
        """
        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.a1v1, self.key1, self.oldValue1)
        if (self.handleResult(
            tg_id is not None,
            'A1: The tg_id of taggroup to change was not found.'
        )) is not True:
            return False

        # Prepare the diff
        deleteTags = self.createBase.getTagDiffsFromTags({self.key1: self.oldValue1}, 'delete')
        addTags = self.createBase.getTagDiffsFromTags({self.key1: self.newValue1}, 'add')
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags
        }
        diff = {'activities': [self.createBase.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update a1v1:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.createBase.doCreate(self.createBase.getCreateUrl('activities'), diff, self.getUser(2)),
            'The Activity 1 could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier1)
                and self.a1v2 is not None),
            'Version 2 of the updated Activity 1 was not found.'
        )) is not True:
            return False

        """
        A2v2 (by user 2 > based on A1v1)
        """
        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.a2v1, self.key1, self.oldValue1)
        if (self.handleResult(
            tg_id is not None,
            'A2: The tg_id of taggroup to change was not found.'
        )) is not True:
            return False

        # Prepare the diff
        deleteTags = self.createBase.getTagDiffsFromTags({self.key1: self.oldValue1}, 'delete')
        addTags = self.createBase.getTagDiffsFromTags({self.key1: self.newValue1}, 'add')
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags
        }
        diff = {'activities': [self.createBase.getItemDiff(
            'activities',
            id = self.identifier2,
            version = 1,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update a2v1:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.createBase.doCreate(self.createBase.getCreateUrl('activities'), diff, self.getUser(2)),
            'The Activity 2 could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a2v2 = self.protocol.read_one_by_version(
            self.request, self.identifier2, 2
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier2)
                and self.a2v2 is not None),
            'Version 2 of the updated Activity 2 was not found.'
        )) is not True:
            return False

        """
        A1v3 (by user 3 > based on v1)
        """
        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.a1v1, self.key2, self.oldValue2)
        if (self.handleResult(
            tg_id is not None,
            'A1: The tg_id of taggroup to change was not found.'
        )) is not True:
            return False

        # Prepare the diff
        deleteTags = self.createBase.getTagDiffsFromTags({self.key2: self.oldValue2}, 'delete')
        addTags = self.createBase.getTagDiffsFromTags({self.key2: self.newValue2}, 'add')
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags
        }
        diff = {'activities': [self.createBase.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update a1v2:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.createBase.doCreate(self.createBase.getCreateUrl('activities'), diff, self.getUser(3)),
            'The Activity 1 could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a1v3 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 3
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier1)
                and self.a1v3 is not None),
            'Version 3 of the updated Activity 1 was not found.'
        )) is not True:
            return False

        """
        A2v3 (by user 3 > based on v1)
        """
        # Find and check the tg_id where the values are in
        tg_id = self.findTgidByKeyValue(self.a2v1, self.key2, self.oldValue2)
        if (self.handleResult(
            tg_id is not None,
            'A2: The tg_id of taggroup to change was not found.'
        )) is not True:
            return False

        # Prepare the diff
        deleteTags = self.createBase.getTagDiffsFromTags({self.key2: self.oldValue2}, 'delete')
        addTags = self.createBase.getTagDiffsFromTags({self.key2: self.newValue2}, 'add')
        taggroup = {
            'tg_id': tg_id,
            'tags': deleteTags + addTags
        }
        diff = {'activities': [self.createBase.getItemDiff(
            'activities',
            id = self.identifier2,
            version = 1,
            taggroups = [taggroup]
        )]}

        if verbose is True:
            log.debug('Diff to update a2v2:\n%s' % diff)

        # Update the Activity
        if (self.handleResult(
            self.createBase.doCreate(self.createBase.getCreateUrl('activities'), diff, self.getUser(3)),
            'The Activity 2 could not be updated.'
        )) is not True:
            return False

        # Check that a new Activity was created
        self.a2v3 = self.protocol.read_one_by_version(
            self.request, self.identifier2, 3
        )
        if (self.handleResult(
            (self.countVersions(Activity, self.identifier2)
                and self.a2v3 is not None),
            'Version 3 of the updated Activity 2 was not found.'
        )) is not True:
            return False

        # Re-query v2
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )

        # Check that the status of v2 is 'pending'
        if (self.handleResult(
            self.a1v2.get_status_id() == 1,
            'A1: The status of version 2 is not "pending"'
        )) is not True:
            return False

        # Re-query v2
        self.a2v2 = self.protocol.read_one_by_version(
            self.request, self.identifier2, 2
        )

        # Check that the status of v2 is 'pending'
        if (self.handleResult(
            self.a2v2.get_status_id() == 1,
            'A2: The status of version 2 is not "pending"'
        )) is not True:
            return False

        # Check that the status of v3 is 'pending'
        if (self.handleResult(
            self.a1v3.get_status_id() == 1,
            'A1: The status of version 3 is not "pending"'
        )) is not True:
            return False

        # Check that the status of v3 is 'pending'
        if (self.handleResult(
            self.a2v3.get_status_id() == 1,
            'A2: The status of version 3 is not "pending"'
        )) is not True:
            return False

        # Check that v2 does contain only the first change
        if (self.handleResult(
            (self.findKeyValue(self.a1v2, self.key1, self.oldValue1) is False and
                self.findKeyValue(self.a1v2, self.key1, self.newValue1) is True),
            'A1: Version 2 does not contain the changes made by user 2'
        )) is not True:
            return False

        # Check that v2 does not contain the second change
        if (self.handleResult(
            (self.findKeyValue(self.a1v2, self.key2, self.oldValue2) is True and
                self.findKeyValue(self.a1v2, self.key2, self.newValue2) is False),
            'A2: Version 2 also contains the second change'
        )) is not True:
            return False

        # Check that v2 does contain only the first change
        if (self.handleResult(
            (self.findKeyValue(self.a2v2, self.key1, self.oldValue1) is False and
                self.findKeyValue(self.a2v2, self.key1, self.newValue1) is True),
            'A2: Version 2 does not contain the changes made by user 2'
        )) is not True:
            return False

        # Check that v2 does not contain the second change
        if (self.handleResult(
            (self.findKeyValue(self.a2v2, self.key2, self.oldValue2) is True and
                self.findKeyValue(self.a2v2, self.key2, self.newValue2) is False),
            'A2: Version 2 also contains the second change'
        )) is not True:
            return False

        # Check that v3 does contain only the second change
        if (self.handleResult(
            (self.findKeyValue(self.a1v3, self.key1, self.oldValue1) is True and
                self.findKeyValue(self.a1v3, self.key1, self.newValue1) is False),
            'A1: Version 3 also contains the changes made by user 2'
        )) is not True:
            return False

        # Check that v3 contains both changes
        if (self.handleResult(
            (self.findKeyValue(self.a1v3, self.key2, self.oldValue2) is False and
                self.findKeyValue(self.a1v3, self.key2, self.newValue2) is True),
            'A1: Version 3 does not contain the changes made by user 3'
        )) is not True:
            return False

        # Check that v3 does contain only the second change
        if (self.handleResult(
            (self.findKeyValue(self.a2v3, self.key1, self.oldValue1) is True and
                self.findKeyValue(self.a2v3, self.key1, self.newValue1) is False),
            'A2: Version 3 also contains the changes made by user 2'
        )) is not True:
            return False

        # Check that v3 contains both changes
        if (self.handleResult(
            (self.findKeyValue(self.a2v3, self.key2, self.oldValue2) is False and
                self.findKeyValue(self.a2v3, self.key2, self.newValue2) is True),
            'A2: Version 3 does not contain the changes made by user 3'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        """
        A1
        """
        # Count all versios to make sure there are 3
        initialVersionCount = self.countVersions(Activity, self.identifier1)
        if (self.handleResult(
            initialVersionCount == 3,
            'A1: There are not 3 Versions available initially'
        )) is not True:
            return False

        # First, review and accept v2
        if (self.handleResult(
            self.doReview('activities', self.identifier1, 2, 1) is True,
            'Activity 1 v2 could not be reviewed.'
        )) is not True:
            return False

        # Query the item again to check that it is now active
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.a1v2.get_status_id() == 2,
            'Activity 1 v2 is not active after approving it.'
        )) is not True:
            return False

         # Make sure that v1 is now inactive
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 3,
            'Activity 1 v1 not inactive after approving v2'
        )) is not True:
            return False

        # Make sure there was no other version created
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == initialVersionCount,
            'Approving 1 v2 created another version'
        )) is not True:
            return False

        # Then review and accept v3
        if (self.handleResult(
            self.doReview('activities', self.identifier1, 3, 1) is True,
            'Activity 1 v3 could not be reviewed.'
        )) is not True:
            return False

        # This should have created another version
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == initialVersionCount + 1,
            'Approving 1 v3 did not create another version'
        )) is not True:
            return False

        # Query v3 again to check that it is now edited
        self.a1v3 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 3
        )
        if (self.handleResult(
            self.a1v3.get_status_id() == 6,
            'Activity 1 v3 is edited after approving it'
        )) is not True:
            return False

        # Query v2 again to check that it is not inactive
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.a1v2.get_status_id() == 3,
            'Activity 1 v2 is not inactive after approving v3'
        )) is not True:
            return False

        # A new version (4) should be available
        self.a1v4 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 4
        )
        if (self.handleResult(
            self.a1v4.get_status_id() == 2,
            'Newly created version 4 (recalculated) of Activity 1 is not active'
        )) is not True:
            return False

        # Version 4 should contain both the changes made to v2 and v3
        if (self.handleResult(
            (self.findKeyValue(self.a1v4, self.key1, self.oldValue1) is False and
                self.findKeyValue(self.a1v4, self.key1, self.newValue1) is True),
            'Recalculated version 4 of Activity 1 does not contain the changes made by user 2'
        )) is not True:
            return False
        if (self.handleResult(
            (self.findKeyValue(self.a1v4, self.key2, self.oldValue2) is False and
                self.findKeyValue(self.a1v4, self.key2, self.newValue2) is True),
            'Recalculated version 4 of Activity 1 does not contain the changes made by user 3'
        )) is not True:
            return False

        """
        A2
        """
        # Count all versios to make sure there are 3
        initialVersionCount = self.countVersions(Activity, self.identifier2)
        if (self.handleResult(
            initialVersionCount == 3,
            'A2: There are not 3 Versions available initially'
        )) is not True:
            return False

        # First, review and accept v3
        if (self.handleResult(
            self.doReview('activities', self.identifier2, 3, 1) is True,
            'Activity 2 v3 could not be reviewed.'
        )) is not True:
            return False

        # Query the item again to check that it is now active
        self.a2v3 = self.protocol.read_one_by_version(
            self.request, self.identifier2, 3
        )
        if (self.handleResult(
            self.a2v3.get_status_id() == 2,
            'Activity 2 v3 is not active after approving it.'
        )) is not True:
            return False

         # Make sure that v1 is now inactive
        self.a2v1 = self.protocol.read_one_by_version(
            self.request, self.identifier2, 1
        )
        if (self.handleResult(
            self.a2v1.get_status_id() == 3,
            'Activity 2 v1 not inactive after approving v2'
        )) is not True:
            return False

        # Make sure there was no other version created
        if (self.handleResult(
            self.countVersions(Activity, self.identifier2) == initialVersionCount,
            'Approving 2 v2 created another version'
        )) is not True:
            return False

        # Then review and accept v2
        if (self.handleResult(
            self.doReview('activities', self.identifier2, 2, 1) is True,
            'Activity 2 v2 could not be reviewed.'
        )) is not True:
            return False

        # This should have created another version
        if (self.handleResult(
            self.countVersions(Activity, self.identifier2) == initialVersionCount + 1,
            'Approving 2 v2 did not create another version'
        )) is not True:
            return False

        # Query v2 again to check that it is now edited
        self.a2v2 = self.protocol.read_one_by_version(
            self.request, self.identifier2, 2
        )
        if (self.handleResult(
            self.a2v2.get_status_id() == 6,
            'Activity 2 v2 is edited after approving it'
        )) is not True:
            return False

        # Query v3 again to check that it is not inactive
        self.a2v3 = self.protocol.read_one_by_version(
            self.request, self.identifier2, 3
        )
        if (self.handleResult(
            self.a2v3.get_status_id() == 3,
            'Activity 2 v3 is not inactive after approving v3'
        )) is not True:
            return False

        # A new version (4) should be available
        self.a2v4 = self.protocol.read_one_by_version(
            self.request, self.identifier2, 4
        )
        if (self.handleResult(
            self.a2v4.get_status_id() == 2,
            'Newly created version 4 (recalculated) of Activity 2 is not active'
        )) is not True:
            return False

        # Version 4 should contain both the changes made to v2 and v3
        if (self.handleResult(
            (self.findKeyValue(self.a2v4, self.key1, self.oldValue1) is False and
                self.findKeyValue(self.a2v4, self.key1, self.newValue1) is True),
            'Recalculated version 4 of Activity 2 does not contain the changes made by user 2'
        )) is not True:
            return False
        if (self.handleResult(
            (self.findKeyValue(self.a2v4, self.key2, self.oldValue2) is False and
                self.findKeyValue(self.a2v4, self.key2, self.newValue2) is True),
            'Recalculated version 4 of Activity 2 does not contain the changes made by user 3'
        )) is not True:
            return False

        return True

"""
MA 07
"""
class ModerationActivities07(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'MA07'
        self.testDescription = 'A version without all mandatory keys cannot be set to "active"'
        self.identifier1 = '55ea5176-5e81-434d-820b-31e2fb0ee417'
        self.a1v1 = None
        self.createBase = CreateBase()

    def testSetup(self, verbose=False):

        """
        Create a first active version with missing mandatory keys
        """
        # Make sure the Activity does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity 1 exists already'
        )) is not True:
            return False

        # Create, moderate and check Activity 1
        self.a1v1 = self.createBase.createAndCheckFirstItem(
            self,
            'activities',
            Activity,
            self.createBase.getCreateUrl('activities'),
            self.createBase.getSomeActivityTags(3),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity 1 was not created or reviewed.'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        # Query the item again
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )

        # Make sure the item is pending
        if (self.handleResult(
            self.a1v1.get_status_id() == 1,
            'Activity was not pending initially.'
        )) is not True:
            return False

        # Try to review and accept version 1
        if (self.handleResult(
            self.doReview('activities', self.identifier1, 1, 1) is False,
            'Activity could be approved although it does not contain all mandatory keys'
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
            self.getReviewUrl('activities'),
            data=payload,
            cookies=cookies
        )

        # Make sure the review request returned 400
        if (self.handleResult(
            request.status_code == 400,
            'The request to do a review on an Activity with missing mandatory keys did not return error code 400'
        )) is not True:
            return False

        # Query the item again to check that it is still pending
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 1,
            'Activity is not pending anymore after approvement (which should have failed)'
        )) is not True:
            return False

        # Try to review and reject version 1
        if (self.handleResult(
            self.doReview('activities', self.identifier1, 1, 2) is True,
            'Activity with missing mandatory keys could not be rejected'
        )) is not True:
            return False

        # Query the item again to check that it is now rejected
        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1v1.get_status_id() == 5,
            'Activity is not rejected after rejecting it in review'
        )) is not True:
            return False

        # Make sure there no other version was created
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 1,
            'Review (reject) of an Activity with missing mandatory keys created more than one version.'
        )) is not True:
            return False

        return True

"""
MA 08
"""
class ModerationActivities08(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'MA08'
        self.testDescription = 'Reviewing an Involvement from Activity side implicitly also reviews the corresponding Stakeholder'
        self.identifier1 = '469007a2-09db-4d6c-9a3a-88052a30f0f9'
        self.a1v1 = None
        self.a1v2 = None
        self.createBase = CreateBase()

        from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
        self.otherProtocol = StakeholderProtocol3(Session)
        self.identifier2 = '0331fc75-d193-4602-bc61-de2ebee5283f'
        self.s1v1 = None
        self.s1v2 = None
        self.invRole1 = self.getStakeholderRole(6)

    def testSetup(self, verbose=False):

        """
        Create a first active version of the Activity
        """
        # Make sure the Activity does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity exists already'
        )) is not True:
            return False

        # Create, moderate and check Activity
        self.a1v1 = self.createBase.createModerateCheckFirstItem(
            self,
            'activities',
            Activity,
            self.createBase.getCreateUrl('activities'),
            self.createBase.getSomeActivityTags(4, uid=self.identifier1),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created or reviewed.'
        )) is not True:
            return False

        """
        Create a first active version of the Stakeholder
        """
        # Make sure the Stakeholder does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier2) == 0,
            'Stakeholder exists already'
        )) is not True:
            return False

        # Create, moderate and check Stakeholder
        self.s1v1 = self.createBase.createModerateCheckFirstItem(
            self,
            'stakeholders',
            Stakeholder,
            self.createBase.getCreateUrl('stakeholders'),
            self.createBase.getSomeStakeholderTags(4, uid=self.identifier2),
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

        diff = {'activities': [self.createBase.getItemDiff(
            'activities',
            id = self.identifier1,
            version = 1,
            taggroups = [],
            involvements = [
                {
                    'id': self.identifier2,
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

        # Try to review and accept version 2 of the Activity
        if (self.handleResult(
            self.doReview('activities', self.identifier1, 2, 1) is True,
            'The Activity could not be set active'
        )) is not True:
            return False

        # Make sure the Activity is not pending anymore
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.a1v2.get_status_id() == 2,
            'Activity (v2) is not active!'
        )) is not True:
            return False

        # Make sure the Stakeholder is not pending anymore
        self.s1v2 = self.otherProtocol.read_one_by_version(
            self.request, self.identifier2, 2
        )
        if (self.handleResult(
            self.s1v2.get_status_id() == 2,
            'Stakeholder (v2) is not active!'
        )) is not True:
            return False

        # Make sure the Activity has an involvement
        if (self.handleResult(
            len(self.a1v2.get_involvements()) == 1,
            'Activity v2 does not have an Involvement'
        )) is not True:
            return False

        return True

"""
MA 09
"""
class ModerationActivities09(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = 'MA09'
        self.testDescription = 'Activity attributes can only be reviewed from Activity side'
        self.identifier1 = '7d71a6fd-af2d-4b01-b8c2-75cb4226fe2b'
        self.a1v1 = None
        self.a1v2 = None
        self.createBase = CreateBase()

        from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
        self.otherProtocol = StakeholderProtocol3(Session)
        self.identifier2 = '848b3af6-9933-4c00-baf1-5b6ccf55122b'
        self.s1v1 = None
        self.s1v2 = None
        self.invRole1 = self.getStakeholderRole(6)

    def testSetup(self, verbose=False):

        """
        Create a first active version of the Activity
        """
        # Make sure the Activity does not yet exist
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity exists already'
        )) is not True:
            return False

        # Create, moderate and check Activity
        self.a1v1 = self.createBase.createModerateCheckFirstItem(
            self,
            'activities',
            Activity,
            self.createBase.getCreateUrl('activities'),
            self.createBase.getSomeActivityTags(4, uid=self.identifier1),
            self.identifier1,
            self.getUser(1),
            profile = 'Laos'
        )

        if (self.handleResult(
            self.a1v1 is not None and self.a1v1 is not False,
            'Activity was not created or reviewed.'
        )) is not True:
            return False

        """
        Create a first active version of the Stakeholder
        """
        # Make sure the Stakeholder does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier2) == 0,
            'Stakeholder exists already'
        )) is not True:
            return False

        # Create, moderate and check Stakeholder
        self.s1v1 = self.createBase.createModerateCheckFirstItem(
            self,
            'stakeholders',
            Stakeholder,
            self.createBase.getCreateUrl('stakeholders'),
            self.createBase.getSomeStakeholderTags(4, uid=self.identifier2),
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
            id = self.identifier1,
            version = 1,
            taggroups = [taggroup],
            involvements = [
                {
                    'id': self.identifier2,
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
            self.doReview('stakeholders', self.identifier2, 2, 1) is False,
            'Stakeholder was reviewed even though the Activity on the other side of involvement had changed attributes'
        )) is not True:
            return False

        # Query the Stakeholder to check that it is still pending
        self.s1v2 = self.otherProtocol.read_one_by_version(
            self.request, self.identifier2, 2
        )
        if (self.handleResult(
            self.s1v2.get_status_id() == 1,
            'Stakeholder (v2) is not pending anymore'
        )) is not True:
            return False

        # Also make sure the Activity is still pending
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.a1v2.get_status_id() == 1,
            'Activity (v2) is not pending anymore'
        )) is not True:
            return False

        # Try to review and accept version 2 of the Activity
        if (self.handleResult(
            self.doReview('activities', self.identifier1, 2, 1) is True,
            'The Activity could not be set active'
        )) is not True:
            return False

        # Make sure the Activity is not pending anymore
        self.a1v2 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 2
        )
        if (self.handleResult(
            self.a1v2.get_status_id() == 2,
            'Activity (v2) is not active!'
        )) is not True:
            return False

        # Make sure the Stakeholder is not pending anymore
        self.s1v2 = self.otherProtocol.read_one_by_version(
            self.request, self.identifier2, 2
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

        # Make sure the Activity has an involvement
        if (self.handleResult(
            len(self.a1v2.get_involvements()) == 1,
            'Activity v2 does not have an Involvement'
        )) is not True:
            return False

        return True