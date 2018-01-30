from lokp.models import DBSession
from lokp.protocols.stakeholder_protocol import StakeholderProtocol
from lokp.review.review import BaseReview


class StakeholderReview(BaseReview):

    def __init__(self, request):
        super(StakeholderReview, self).__init__(request)
        self.protocol = StakeholderProtocol(DBSession)
