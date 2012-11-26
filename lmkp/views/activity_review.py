__author__ = "Adrian Weber, Centre for Development and Environment, University of Bern"
__date__ = "$Nov 20, 2012 4:05:32 PM$"

from lmkp.models.database_objects import Activity
from lmkp.models.meta import DBSession as Session
from lmkp.views.activity_protocol3 import ActivityProtocol3
from lmkp.views.review import BaseReview
import logging
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config
from pyramid_handlers import action

log = logging.getLogger(__name__)

class ActivityReview(BaseReview):

    def __init__(self, request):
        super(ActivityReview, self).__init__(request)
        self.activity_protocol3 = ActivityProtocol3(Session)
        
    @action(name='html', renderer='lmkp:templates/compare_versions.mak', permission='moderate')
    def compare_html(self):

        uid = self.request.matchdict.get('uid', None)

        available_versions = []
        for i in Session.query(Activity.version).\
            filter(Activity.activity_identifier == uid).\
            order_by(Activity.version):
            available_versions.append(i[0])

        additional_params = {
        'available_versions': available_versions
        }

        return additional_params

    @action(name='json', renderer='json', permission='moderate')
    def compare_json(self):

        # Get the uid from the request
        uid = self.request.matchdict.get('uid', None)

        # Try to get the versions or set reference and new version to 1
        versions = self.request.matchdict.get('versions')
        try:
            ref_version = int(versions[0])
        except IndexError:
            ref_version = 1
        except ValueError as e:
            raise HTTPBadRequest("ValueError: %s" % e)

        try:
            new_version = int(versions[1])
        except IndexError:
            new_version = 1
        except ValueError as e:
            raise HTTPBadRequest("ValueError: %s" % e)

	# Get the old, reference Activity object
	ref = self.activity_protocol3.read_one_by_version(self.request, uid, ref_version)

        # Try to get the new activity object
        try:
            new = self.activity_protocol3.read_one_by_version(self.request, uid, new_version)
        except IndexError:
            return HTTPSeeOther(self.request.route_url('activities_compare_versions', action='json', uid=uid, versions=(old_version, (new_version-1))))

        # Request also the metadata
        metadata = {}
        metadata['ref_title'], metadata['new_title'] = \
            self._get_active_pending_version_descriptions(Activity, uid, ref_version, new_version)

        result = dict(self._compare_taggroups(ref, new).items() + {'metadata': metadata}.items())

        return result

    @view_config(route_name='activities_review_versions_html', renderer='lmkp:templates/review_versions.mak', permission='moderate')
    def review_activity_html(self):
        """
        Review active with oldest pending version
        """

        # Get the activity identifier
        uid = self.request.matchdict.get('uid', None)

        c = Session.query(Activity).filter(Activity.activity_identifier == uid).count()

        if c == 0:
            raise HTTPNotFound("Activity with identifier %s does not exist." % uid)

        active_version, pending_version = self._get_active_pending_versions(Activity, uid)

        return {'metadata': {'identifier': uid, 'version': pending_version}}

    @view_config(route_name='activities_review_versions_json', renderer='json', permission='moderate')
    def review_activity_json(self):
        """
        Review two activity versions together
        """

        # Get the activity identifier
        uid = self.request.matchdict.get('uid', None)

        additional_vars = {}
        additional_vars['identifier'] = uid
        additional_vars['next_url'] = self.request.route_url('activities_review_versions_html', uid=uid)
        additional_vars['type'] = 'activities'

        active_version, pending_version = self._get_active_pending_versions(Activity, uid)

        # Some logging
        log.debug("active version: %s" % active_version)
        log.debug("pending version: %s" % pending_version)

        active = pending = None
        # Get the active version
        if active_version is not None:
            active = self.activity_protocol3.read_one_by_version(self.request, uid, active_version)

        # Get the new version
        if pending_version is not None:
            pending = self.activity_protocol3.read_one_by_version(self.request, uid, pending_version)

        additional_vars['active_title'], additional_vars['pending_title'] = \
            self._get_active_pending_version_descriptions(Activity, uid, active_version, pending_version)
        additional_vars['version'] = pending_version
        return dict(self._compare_taggroups(active, pending).items() + {'metadata': additional_vars}.items())