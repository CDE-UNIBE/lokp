from lmkp.tests.create_base import CreateBase

from lmkp.models.meta import DBSession as Session
from lmkp.models.database_objects import *
from lmkp.views.activity_protocol3 import ActivityProtocol3

create_url = 'http://localhost:6543/activities'

class CreateActivities1(CreateBase):
    
    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.testNumber = 1
        self.testDescription = 'Create new Activity with mandatory keys'
        self.identifier1 = '58be3840-6bda-11e2-bcfd-0800200c9a61'
        self.a1 = None
        
    def testSetup(self):
        
        return self.countVersions(Activity, self.identifier1) == 0
        
    def doTest(self):
        
        diff = {}
        activities = []
        
        activities.append(self.putItemDiffTogether(
            taggroups = self.kvToTaggroups(self.getSomeActivityTags(1)),
            id = self.identifier1,
            version = 1
        ))
        
        diff['activities'] = activities
        
        
        x = self.createDiff('activities', [
            self.createItemDiff(
                self.identifier1,
                1,
                
            )
        ]) 
        
        
        diff2 = self.createActivityDiff()
        
        print "****"
        print diff
        print "****"
        print diff2
        
        # Create the Activitiy
        if (self.handleResult(
            self.doCreate(create_url, diff, self.getUser(1)), 
            'New Activity could not be created at all.'
        )) is not True:
            return False
        
        # Find the created Activity
        self.a1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.a1 is not None,
            'New Activity was created but not found.'
        )) is not True:
            return False
        
        # Make sure the Activity has all the taggroups (7)
        if (self.handleResult(
            self.countTaggroups(self.a1) == 7,
            'New Activity has not all taggroups.'
        )) is not True:
            return False
        
        
        return True