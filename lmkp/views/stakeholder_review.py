from lmkp.models.meta import DBSession as Session
from lmkp.views.review import BaseReview
from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3


class StakeholderReview(BaseReview):

    def __init__(self, request):
        super(StakeholderReview, self).__init__(request)
        self.protocol = StakeholderProtocol3(Session)
