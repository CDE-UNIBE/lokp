from lmkp.tests.moderate.moderation_base import ModerationBase
from lmkp.tests.create.create_base import CreateBase

from lmkp.models.meta import DBSession as Session
from lmkp.models.database_objects import *
from lmkp.views.activity_protocol3 import ActivityProtocol3

class ModerationActivities01(ModerationBase):
    
    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "MA01"
        self.testDescription = 'Moderate a new Activity with mandatory keys'
        self.identifier1 = '93c040ff-229a-461b-85b2-ad5da0db56e1'
        self.a1v1 = None
        self.createBase = CreateBase()
        
    def testSetup(self):

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

class ModerationActivities02(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "MA02"
        self.testDescription = 'Moderate a new Activity with mandatory keys'
        self.identifier1 = 'a00b0732-96b4-499d-9e0e-6e393e668c70'
        self.a1v1 = None
        self.createBase = CreateBase()

    def testSetup(self, verbose=False):

        self.a1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        print "****"
        print self.a1v1

        return self.a1v1 is not None

    def doTest(self):


        print "---"
        print self.findKeyValue(self.a1v1, 'Year of agreement', 2000)
        # Accept version 4
        #request = self.doReview(self.identifier1, 4, 1)

        # Make sure that version 4 is active now



        return True