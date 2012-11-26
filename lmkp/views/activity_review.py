__author__ = "Adrian Weber, Centre for Development and Environment, University of Bern"
__date__ = "$Nov 20, 2012 4:05:32 PM$"

from lmkp.models.database_objects import Activity
from lmkp.models.database_objects import Changeset
from lmkp.models.meta import DBSession as Session
from lmkp.views.review import BaseReview
import logging
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from pyramid_handlers import action
from sqlalchemy.sql.functions import max
from sqlalchemy.sql.functions import min

log = logging.getLogger(__name__)

class ActivityReview(BaseReview):

    @view_config(route_name='activities_review_versions_html', renderer='lmkp:templates/review_versions.mak', permission='moderate')
    def review_activity_html(self):
        """
        Review to versions together
        """

        # Get the activity identifier
        uid = self.request.matchdict.get('uid', None)

        c = Session.query(Activity).filter(Activity.activity_identifier == uid).count()

        if c == 0:
            raise HTTPNotFound("Activity with identifier %s does not exist." % uid)

        active_version, pending_version = self._get_active_pending_versions(uid)

        return {'identifier': uid, 'version': pending_version}

    @view_config(route_name='activities_review_versions_json', renderer='json', permission='moderate')
    def review_activity_json(self):
        """
        Review to versions together
        """

        # Get the activity identifier
        uid = self.request.matchdict.get('uid', None)

        additional_vars = {}
        additional_vars['identifier'] = uid
        additional_vars['next_url'] = self.request.route_url('activities_review_versions_html', uid=uid)
        additional_vars['type'] = 'activities'

        active_version, pending_version = self._get_active_pending_versions(uid)

        # Raise an exception is new version number is less than the old version number
        #if pending_version < active_version:
        #    raise HTTPBadRequest("Pending version must be newer than active version.")


        old = new = None
        # Get the old version
        if active_version is not None:
            old = self.activity_protocol3.read_one_by_version(self.request, uid, active_version)

        if pending_version is not None:
            new = self.activity_protocol3.read_one_by_version(self.request, uid, pending_version)

        active_timestamp = Session.query(Changeset.timestamp).join(Activity).filter(Activity.activity_identifier == uid).filter(Activity.version == active_version).first()
        pending_timestamp = Session.query(Changeset.timestamp).join(Activity).filter(Activity.activity_identifier == uid).filter(Activity.version == pending_version).first()

        try:
            additional_vars['ref_title'] = "Version %s as of %s" % (active_version, active_timestamp[0].strftime('%H:%M, %d-%b-%Y'));
        except TypeError:
            additional_vars['ref_title'] = ''
        try:
            additional_vars['new_title'] = "Version %s as of %s" % (pending_version, pending_timestamp[0].strftime('%H:%M, %d-%b-%Y'));
        except TypeError:
            additional_vars['new_title'] = ''

        additional_vars['version'] = pending_version
        return dict(self._compare_taggroups(old, new).items() + {'metadata': additional_vars}.items())

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

    def _get_active_pending_versions(self, uid):
        """
        Returns the current active version and the pending version to review
        """

        # Get the current active version number
        av = Session.query(Activity.version).filter(Activity.activity_identifier == uid).filter(Activity.fk_status == 2).first()

        try:
            active_version = int(av[0])
        except TypeError:
            return None, 1

        # Get the lowest pending version
        pv = Session.query(min(Activity.version)).\
            filter(Activity.activity_identifier == uid).\
            filter(Activity.fk_status == 1).\
            filter(Activity.version > active_version).\
            first()

        try:
            pending_version = int(pv[0])
        except TypeError:
            pending_version = None

        # Some logging
        log.debug("active version: %s" % active_version)
        log.debug("pending version: %s" % pending_version)

        return active_version, pending_version
