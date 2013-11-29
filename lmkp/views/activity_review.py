from lmkp.models.meta import DBSession as Session
from lmkp.views.activity_protocol3 import ActivityProtocol3
from lmkp.views.review import BaseReview
import logging

log = logging.getLogger(__name__)

class ActivityReview(BaseReview):

    def __init__(self, request):
        super(ActivityReview, self).__init__(request)
        self.protocol = ActivityProtocol3(Session)
