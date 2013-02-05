__date__ = "$Nov 20, 2012 4:05:32 PM$"

from geoalchemy import functions
from lmkp.models.database_objects import Activity
from lmkp.models.database_objects import Profile
from lmkp.models.meta import DBSession as Session
from lmkp.views.activity_protocol3 import ActivityProtocol3
from lmkp.views.config import get_mandatory_keys
from lmkp.views.review import BaseReview
import logging
import json
import re
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from pyramid_handlers import action
from sqlalchemy.sql.expression import or_

log = logging.getLogger(__name__)

class ActivityReview(BaseReview):

    def __init__(self, request):
        super(ActivityReview, self).__init__(request)
        self.protocol = ActivityProtocol3(Session)

    @view_config(route_name='activities_moderate_item', renderer='lmkp:templates/moderation.mak', permission='moderate')
    def activities_moderate_item(self):

        self._handle_parameters()

        # Get the uid from the request
        uid = self.request.matchdict.get('uid', None)

        # Check if uid is valid
        uuid4hex = re.compile('[0-9a-f-]{36}\Z', re.I)
        validUid = uuid4hex.match(uid) is not None

        if validUid:
            c = Session.query(Activity).\
                filter(Activity.activity_identifier == uid).\
                count()
        else:
            c = 0

        if c == 0 or not self._within_profile(uid):
            return {
                'openItem': 'true',
                'type': '',
                'identifier': ''
            }

        return {
            'openItem': 'true',
            'type': 'activities',
            'identifier': uid
        }

    @action(name='html', renderer='lmkp:templates/compare_versions.mak')
    def compare_html(self):
        # TODO: It is to be decided if this view is still needed or not.

        uid = self.request.matchdict.get('uid', None)

        available_versions = self._get_available_versions(Activity, uid)

        if len(available_versions) == 0:
            msg = "There is no Activity with identifier %s or you are not allowed to access it."
            raise HTTPNotFound(msg % uid)

        additional_params = {
        'available_versions': json.dumps(available_versions)
        }

        return additional_params

    @action(name='json', renderer='json')
    def compare_json(self):
        """
        Compare two objects (two versions): ref_object and new_object
        """

        # Get the uid from the request
        uid = self.request.matchdict.get('uid', None)

        ref_version_number, new_version_number = self._get_valid_versions(
            Activity, uid
        )

        result = self.get_comparison(
            Activity, uid, ref_version_number, new_version_number
        )

        return result

    @view_config(route_name='activities_review_versions_html', renderer='lmkp:templates/review_versions.mak', permission='moderate')
    def review_activity_html(self):
        # TODO: It is to be decided if this view is still needed or not.
        """
        Review active with oldest pending version
        """

        # Get the activity identifier
        uid = self.request.matchdict.get('uid', None)

        c = Session.query(Activity).filter(Activity.activity_identifier == uid).count()

        if not self._within_profile(uid):
            raise HTTPForbidden("Activity %s is not within your profile." % uid)

        log.debug(get_mandatory_keys(self.request, 'a'))

        if c == 0:
            raise HTTPNotFound("Activity with identifier %s does not exist." % uid)

        active_version, pending_version = self._get_active_pending_versions(Activity, uid)

        return {'metadata': {'identifier': uid, 'version': pending_version}}

    @view_config(route_name='activities_review_versions_json', renderer='json', permission='moderate')
    def review_activity_json(self):
        """
        Review two activity versions together.
        """

        # Get the activity identifier
        uid = self.request.matchdict.get('uid', None)

        if not self._within_profile(uid):
            raise HTTPForbidden("Activity %s is not within your profile." % uid)

        try:
            active_version, pending_version = self._get_valid_versions(
                Activity, uid, review=True
            )
        except HTTPForbidden:
            return {
                'success': False,
                'msg': 'This item has no reviewable pending version.'
            }

        # Some logging
#        log.debug("active version: %s" % active_version)
#        log.debug("pending version: %s" % pending_version)

        result = self.get_comparison(
            Activity, uid, active_version, pending_version, review=True
        )

        return result

    def _within_profile(self, uid):
        """
        Checks if an Activity is within the current moderator's profile
        """

        profile_filters = []
        # Get all profiles for the current moderator
        profiles = Session.query(Profile).filter(Profile.users.any(username=self.request.user.username))
        for p in profiles.all():
            profile_filters.append(functions.intersects(Activity.point, p.geometry))

        # Check if current Activity is within the moderator's profile
        if Session.query(Activity).filter(Activity.identifier == uid).filter(or_(*profile_filters)).first() is not None:
            return True

        return False