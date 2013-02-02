from lmkp.tests.moderation_base import ModerationBase
from lmkp.tests.create_base import CreateBase
from lmkp.tests.create_activities import create_url

from lmkp.models.meta import DBSession as Session
from lmkp.models.database_objects import *
from lmkp.views.activity_protocol3 import ActivityProtocol3

class ModerationActivities1(ModerationBase):
    
    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testNumber = 1
        self.testDescription = 'Moderate a new Activity with mandatory keys'
        self.identifier1 = '43c040ff-229a-461b-85b2-ad5da0db56e5'
        self.a1 = None
        self.createBase = CreateBase()
        
    def testSetup(self):

        # Check that there is no Activity yet
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 0,
            'Activity exists already.'
        )) is not True:
            return False

        # Create an Activity
        diff = self.createBase.getSomeWholeDiff(
            'activities',
            self.createBase.getSomeActivityTags(1),
            self.identifier1,
            1,
            'add',
            geometry = self.createBase.getSomeGeometryDiff('LA')
        )

        # Make sure it is there
        created = self.createBase.doCreate(create_url, diff, self.getUser(1))
        self.a1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            (created is True and self.a1 is not None),
            'Activity exists already.'
        )) is not True:
            return False

        # Make sure there is only one version
        if (self.handleResult(
            self.countVersions(Activity, self.identifier1) == 1,
            'There was more than one Activity created.'
        )) is not True:
            return False

        return True

    def doTest(self):

        # Make sure the item is pending
        if (self.handleResult(
            self.a1.get_status_id() == 1,
            'Activity was not pending initially.'
        )) is not True:
            return False
        
        # Review and accept version 1
        if (self.handleResult(
            self.doReview(self.identifier1, 1, 1) is True,
            'Activity could not be reviewed.'
        )) is not True:
            return False

        # Query the item again to check that it is now active
        self.a1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1.get_status_id() == 2,
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

class ModerationActivities2(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testNumber = 2
        self.testDescription = 'Moderate a new Activity with mandatory keys'
        self.identifier1 = 'a00b0732-96b4-499d-9e0e-6e393e668c70'
        self.a1 = None
        self.createBase = CreateBase()

    def testSetup(self):

        self.a1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        print "****"
        print self.a1

        return self.a1 is not None

    def doTest(self):


        print "---"
        print self.findKeyValue(self.a1, 'Year of agreement', 2000)
        # Accept version 4
        #request = self.doReview(self.identifier1, 4, 1)

        # Make sure that version 4 is active now



        return True