from lmkp.tests.create_base import CreateBase

from lmkp.models.meta import DBSession as Session
from lmkp.models.database_objects import *
from lmkp.views.activity_protocol3 import ActivityProtocol3

import logging
log = logging.getLogger(__name__)

class CreateActivities1(CreateBase):
    
    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "CA1"
        self.testDescription = 'Create new Activity with mandatory keys'
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
        
        # Create the Activitiy
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
        
        # Make sure the Activity has all the taggroups (7)
        if (self.handleResult(
            self.countTaggroups(self.a1v1) == 7,
            'New Activity has not all taggroups.'
        )) is not True:
            return False
        
        return True

#TODO: Temporary
class CreateActivities2(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testId = "CA2"
        self.testDescription = 'Create new Activity with all mandatory keys'
        self.identifier1 = '2a889f80-e571-471a-82b7-e1a2eac47a16'
        self.a1v1 = None

    def testSetup(self):

#        print "**** TEST 2 ***"

        return True

    def doTest(self, verbose=False):

#        print "*** TEST 2"

        return True