__author__ = "Adrian Weber, Centre for Development and Environment, University of Bern"
__date__ = "$Nov 20, 2012 4:05:32 PM$"

from lmkp.models.database_objects import Activity
from lmkp.models.database_objects import Changeset
from lmkp.models.meta import DBSession as Session
from lmkp.views.review import BaseReview
import logging
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from sqlalchemy.sql.functions import max
from pyramid_handlers import action

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

    @action(name='html', renderer='lmkp:templates/compare_versions.mak', permission='moderate')
    def compare_activity_html(self, uid=None):

        uid = self.request.matchdict.get('uid', None)

        if uid is None:
            uid = self.request.matchdict.get('uid', None)

        available_versions = []
        for i in Session.query(Activity.version).filter(Activity.activity_identifier == uid):
            available_versions.append(i[0])

        additional_params = {
        'available_versions': available_versions
        }

        return additional_params

    @action(name='json', renderer='json', permission='moderate')
    def compare_activity_by_versions_json(self):

        uid = self.request.matchdict.get('uid', None)

        versions = self.request.matchdict.get('versions')
        try:
            old_version = int(versions[0])
        except:
            old_version = 1

        try:
            new_version = int(versions[1])
        except:
            new_version = 1

        old = self.activity_protocol3.read_one_by_version(self.request, uid, old_version)

        ref_timestamp = Session.query(Changeset.timestamp).join(Activity).filter(Activity.activity_identifier == uid).filter(Activity.version == old_version).first()
        new_timestamp = Session.query(Changeset.timestamp).join(Activity).filter(Activity.activity_identifier == uid).filter(Activity.version == new_version).first()

        additional_params = {
        'ref_title': "Version %s as of %s" % (old_version, ref_timestamp[0].strftime('%H:%M, %d-%b-%Y')),
        'new_title': "Version %s as of %s" % (new_version, new_timestamp[0].strftime('%H:%M, %d-%b-%Y'))
        }

        try:
            new = self.activity_protocol3.read_one_by_version(self.request, uid, new_version)
        except IndexError:
            return HTTPSeeOther(self.request.route_url('activities_compare_versions', action='json', uid=uid, old=old_version, new=str(new_version-1)))

        result = dict(self._compare_taggroups(old, new).items() + additional_params.items())

        return result
