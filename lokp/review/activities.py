from lokp.models import DBSession
from lokp.protocols.activity_protocol import ActivityProtocol
from lokp.review.review import BaseReview


class ActivityReview(BaseReview):

    def __init__(self, request):
        super(ActivityReview, self).__init__(request)
        self.protocol = ActivityProtocol(DBSession)
