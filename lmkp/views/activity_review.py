__author__ = "Adrian Weber, Centre for Development and Environment, University of Bern"
__date__ = "$Nov 20, 2012 4:05:32 PM$"

from lmkp.models.database_objects import Activity
from lmkp.models.meta import DBSession as Session
from lmkp.views.review import BaseReview
import logging
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from sqlalchemy.sql.functions import max

log = logging.getLogger(__name__)

class ActivityReview(BaseReview):

    @view_config(route_name='activities_review_versions', renderer='lmkp:templates/review_versions.mak', permission='moderate')
    def review_activity(self):
        """
        Review to versions together
        """

        # Get the activity identifier
        uid = self.request.matchdict.get('uid', None)

        additional_vars = {}
        additional_vars['identifier'] = uid
        additional_vars['next_url'] = self.request.route_url('activities_review_versions', uid=uid)
        additional_vars['type'] = 'activities'

        # Get the current active version number
        o = Session.query(Activity.version).filter(Activity.activity_identifier == uid).filter(Activity.fk_status == 2).first()

        # If there is no active version yet, just show the first version
        if o is None:

            # Show the first version
            version = 1

            # Set the first version as version to review
            additional_vars['version'] = version

            activity = self.activity_protocol3.read_one_by_version(self.request, uid, version)

            return dict(self._review_one_version(activity, uid, version).items() + additional_vars.items())

        # Get the latest version number
        l = Session.query(max(Activity.version)).filter(Activity.activity_identifier == uid).first()
        old_version = int(o[0])
        new_version = old_version + 1
        latest_version = int(l[0])

        # Some logging
        log.debug("active version: %s" % old_version)
        log.debug("pending version: %s" % new_version)
        log.debug("latest version: %s" % latest_version)

        # Raise an exception is new version number is less than the old version number
        if new_version < old_version:
            raise HTTPBadRequest("Pending version must be newer than active version.")

        # Get the old version
        old = self.activity_protocol3.read_one_by_version(self.request, uid, old_version)

        # Get the new version
        try:
            new = self.activity_protocol3.read_one_by_version(self.request, uid, new_version)
        # If there is no newer version, catch the exception and redirect the page
        # to the standard html view
        except IndexError as e:
            return HTTPFound(self.request.route_url('activities_read_one_active', output='html', uid=uid))

        additional_vars['version'] = new_version
        return dict(self._compare_taggroups(old, new).items() + additional_vars.items())

    @view_config(route_name='activities_compare', renderer='lmkp:templates/compare_versions.mak', permission='moderate')
    #@view_config(route_name='activities_compare', renderer='json', permission='moderate')
    def compare_activity(self, uid=None):

        uid = self.request.matchdict.get('uid', None)

        return self.compare_activity_by_versions(uid, 1, 1)

    @view_config(route_name='activities_compare_versions', renderer='lmkp:templates/compare_versions.mak', permission='moderate')
    #@view_config(route_name='activities_compare_versions', renderer='json', permission='moderate')
    def compare_activity_by_versions(self, uid=None, old_version=None, new_version=None):

        if uid is None:
            uid = self.request.matchdict.get('uid', None)

        if old_version is None:
            old_version = int(self.request.matchdict.get('old', 1))

        if new_version is None:
            new_version = int(self.request.matchdict.get('new', 1))

        if new_version < old_version:
            raise HTTPBadRequest("Reference version %s is older than new version %s" % (old_version, new_version))

        old = self.activity_protocol3.read_one_by_version(self.request, uid, old_version)

        try:
            new = self.activity_protocol3.read_one_by_version(self.request, uid, new_version)
        except IndexError:
            return HTTPFound(self.request.route_url('activities_compare_versions', uid=uid, old=old_version, new=str(new_version-1)))

        available_versions = []
        for i in Session.query(Activity.version).filter(Activity.activity_identifier == uid):
            available_versions.append(i[0])

        compare_url = "/activities/compare/%s" % uid

        add_ons = {
        'available_versions': available_versions,
        'compare_url': compare_url,
        'ref_version': old_version,
        'new_version': new_version,
        'type': 'activities',
        'other_type': 'stakeholders'
        }
        return dict(self._compare_taggroups(old, new).items() + add_ons.items())
