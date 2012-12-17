__author__ = "Adrian Weber, Centre for Development and Environment, University of Bern"
__date__ = "$Nov 20, 2012 4:05:40 PM$"

from lmkp.models.database_objects import Stakeholder
from lmkp.models.meta import DBSession as Session
from lmkp.views.review import BaseReview
from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
import logging
import json
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config
from pyramid_handlers import action

log = logging.getLogger(__name__)

class StakeholderReview(BaseReview):

    def __init__(self, request):
        super(StakeholderReview, self).__init__(request)
        self.stakeholder_protocol3 = StakeholderProtocol3(Session)

    @action(name='html', renderer='lmkp:templates/compare_versions.mak')
    def compare_html(self):

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

        # Get the uid from the request
        uid = self.request.matchdict.get('uid', None)

        ref_version, new_version = self._get_valid_versions(Stakeholder, uid)

        # Get the old, reference Stakeholder object
        ref = self.stakeholder_protocol3.read_one_by_version(self.request, uid, ref_version)

        # Try to get the new stakeholder object
        new = self.stakeholder_protocol3.read_one_by_version(self.request, uid, new_version)

        # Request also the metadata
        metadata = {}
        metadata['ref_title'], metadata['new_title'] = \
            self._get_active_pending_version_descriptions(Stakeholder, uid, ref_version, new_version)
        metadata['ref_version'] = ref_version
        metadata['new_version'] = new_version

        result = dict(self._compare_taggroups(ref, new).items() + {'metadata': metadata}.items())

        return result

    @view_config(route_name='stakeholders_review_versions_html', renderer='lmkp:templates/review_versions.mak', permission='moderate')
    def review_stakeholder_html(self):
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

        additional_vars = {}
        additional_vars['identifier'] = uid
        additional_vars['next_url'] = self.request.route_url('stakeholders_review_versions_html', uid=uid)
        additional_vars['type'] = 'stakeholders'

        active_version, pending_version = self._get_active_pending_versions(Stakeholder, uid)

        # Some logging
        log.debug("active version: %s" % active_version)
        log.debug("pending version: %s" % pending_version)

        active = pending = None
        # Get the active version
        if active_version is not None:
            active = self.stakeholder_protocol3.read_one_by_version(self.request, uid, active_version)

        # Get the new version
        if pending_version is not None:
            pending = self.stakeholder_protocol3.read_one_by_version(self.request, uid, pending_version)

        additional_vars['active_title'], additional_vars['pending_title'] = \
            self._get_active_pending_version_descriptions(Stakeholder, uid, active_version, pending_version)
        additional_vars['version'] = pending_version
        return dict(self._compare_taggroups(active, pending).items() + {'metadata': additional_vars}.items())