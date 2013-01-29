from lmkp.tests.moderation_base import ModerationBase

from lmkp.models.meta import DBSession as Session
from lmkp.models.database_objects import *
from lmkp.views.activity_protocol3 import ActivityProtocol3

class ModerationActivities1(ModerationBase):

    def __init__(self, request):
        super(ModerationBase, self).__init__()
        self.request = request
        self.protocol = ActivityProtocol3(Session)
        self.identifier = '67716dff-1154-4f97-878f-936105e867b4'
        self.a1 = None

    def testSetUp(self):

        self.a1 = self.protocol.read_one_by_version(
            self.request, self.identifier, 1
        )
        print "****"
        print self.a1

        return self.a1 is not None

    def doTest(self):


        print "---"
        print self.findKeyValue(self.a1, 'Year of agreement', 2000)
        # Accept version 4
        #request = self.doRequest(self.identifier, 4, 1)

        # Make sure that version 4 is active now



        return True