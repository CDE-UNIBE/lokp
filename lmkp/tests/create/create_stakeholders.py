from lmkp.tests.create.create_base import CreateBase

from lmkp.models.meta import DBSession as Session
from lmkp.models.database_objects import *
from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3

import logging
log = logging.getLogger(__name__)

"""
CS 01
"""
class CreateStakeholders01(CreateBase):

    def __init__(self, request):
        super(CreateBase, self).__init__()
        self.request = request
        self.protocol = StakeholderProtocol3(Session)
        self.testId = 'CS01'
        self.testDescription = 'It is possible to create a new Stakeholder'
        self.identifier1 = 'e6b3168b-2043-443b-83bd-cc0de7dc28c5'
        self.s1v1 = None

    def testSetup(self):
        # Make sure the item does not yet exist
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 0,
            'Stakeholder exists already'
        )) is not True:
            return False

        return True

    def doTest(self, verbose=False):

        diff = self.getSomeWholeDiff(
            'stakeholders',
            self.getSomeStakeholderTags(1),
            self.identifier1,
            1,
            'add'
        )

        if verbose is True:
            log.debug('Diff to create s1v1:\n%s' % diff)

        # Create the Stakeholder
        if (self.handleResult(
            self.doCreate(self.getCreateUrl('stakeholders'), diff, self.getUser(1)),
            'New Stakeholder could not be created at all.'
        )) is not True:
            return False

        # Find the created Stakeholder
        self.s1v1 = self.protocol.read_one_by_version(
            self.request, self.identifier1, 1
        )
        if (self.handleResult(
            self.s1v1 is not None,
            'New Stakeholder was created but not found.'
        )) is not True:
            return False

        # Make sure there is only one version of the Stakeholder
        if (self.handleResult(
            self.countVersions(Stakeholder, self.identifier1) == 1,
            'There was more than one version of the Stakeholder created.'
        )) is not True:
            return False

        # Make sure the Stakeholder has all the taggroups
        if (self.handleResult(
            self.countTaggroups(self.s1v1) == len(self.getSomeStakeholderTags(1)),
            'New Stakeholder has not all taggroups.'
        )) is not True:
            return False

        # Make sure the Stakeholder has status 'pending'
        if (self.handleResult(
            self.s1v1.get_status_id() == 1,
            'New Stakeholder has not status "pending".'
        )) is not True:
            return False

        return True