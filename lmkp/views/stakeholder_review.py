__author__ = "Adrian Weber, Centre for Development and Environment, University of Bern"
__date__ = "$Nov 20, 2012 4:05:40 PM$"

from lmkp.config import check_valid_uuid
from lmkp.models.database_objects import Stakeholder
from lmkp.models.meta import DBSession as Session
from lmkp.views.review import BaseReview
from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
from lmkp.views.config import get_mandatory_keys
import logging
import json
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.httpexceptions import HTTPForbidden
from pyramid.view import view_config
from pyramid_handlers import action

log = logging.getLogger(__name__)

class StakeholderReview(BaseReview):

    def __init__(self, request):
        super(StakeholderReview, self).__init__(request)
        self.protocol = StakeholderProtocol3(Session)

    @view_config(route_name='stakeholders_moderate_item', renderer='lmkp:templates/moderation.mak', permission='moderate')
    def stakeholders_moderate_item(self):

        self._handle_parameters()

        # Get the uid from the request
        uid = self.request.matchdict.get('uid', None)

        # Check if uid is valid
        if check_valid_uuid(uid) is True:
            c = Session.query(Stakeholder).\
                filter(Stakeholder.stakeholder_identifier == uid).\
                count()
        else:
            c = 0

        if c == 0:
            return {
                'openItem': 'true',
                'type': '',
                'identifier': ''
            }

        return {
            'openItem': 'true',
            'type': 'stakeholders',
            'identifier': uid
        }

    @action(name='html', renderer='lmkp:templates/compare_versions.mak')
    def compare_html(self):
        # TODO: It is to be decided if this view is still needed or not.

        uid = self.request.matchdict.get('uid', None)

        available_versions = self._get_available_versions(Stakeholder, uid)

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
            Stakeholder, uid
        )

        result = self.get_comparison(
            Stakeholder, uid, ref_version_number, new_version_number
        )

        return result

    @view_config(route_name='stakeholders_review_versions_html', renderer='lmkp:templates/review_versions.mak', permission='moderate')
    def review_stakeholder_html(self):
        # TODO: It is to be decided if this view is still needed or not.
        """
        Review active with oldest pending version
        """

        # Get the activity identifier
        uid = self.request.matchdict.get('uid', None)

        c = Session.query(Stakeholder).filter(Stakeholder.identifier == uid).count()

        if c == 0:
            raise HTTPNotFound("Activity with identifier %s does not exist." % uid)

        active_version, pending_version = self._get_active_pending_versions(Stakeholder, uid)

        return {'metadata': {'identifier': uid, 'version': pending_version}}
    
    @view_config(route_name='stakeholders_review_versions_json', renderer='json', permission='moderate')
    def review_stakeholder_json(self):
        """
        Review two stakeholder versions together
        """

        # Get the activity identifier
        uid = self.request.matchdict.get('uid', None)

        try:
            active_version, pending_version = self._get_valid_versions(
                Stakeholder, uid, review=True
            )
        except HTTPForbidden:
            return {
                'success': False,
                'msg': 'This Stakeholder has no reviewable pending version.'
            }

        result = self.get_comparison(
            Stakeholder, uid, active_version, pending_version, review=True
        )

        if 'to_delete' not in result or result['to_delete'] is not True:
            # Check if all mandatory keys are there and if not which are missing
            pending_feature = self.protocol.read_one_by_version(
                self.request, uid, pending_version
            )
            pending_feature.mark_complete(get_mandatory_keys(self.request, 'sh'))
            missing_keys = pending_feature._missing_keys

            if len(missing_keys) > 0:
                result['missing_keys'] = missing_keys

        return result
