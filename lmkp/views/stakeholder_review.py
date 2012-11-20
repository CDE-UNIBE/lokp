__author__ = "Adrian Weber, Centre for Development and Environment, University of Bern"
__date__ = "$Nov 20, 2012 4:05:40 PM$"

from lmkp.models.database_objects import Stakeholder
from lmkp.models.meta import DBSession as Session
from lmkp.views.review import BaseReview
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from sqlalchemy.sql.functions import max

class StakeholderReview(BaseReview):

    @view_config(route_name='stakeholders_compare', renderer='lmkp:templates/compare_versions.mak', permission='moderate')
    def compare_stakeholders(self):
        uid = self.request.matchdict.get('uid', None)

        return self.compare_stakeholder_by_versions(uid, 1, 1)

    @view_config(route_name='stakeholders_compare_versions', renderer='lmkp:templates/compare_versions.mak')
    def compare_stakeholder_by_versions(self, uid=None, old_version=None, new_version=None):

        if uid is None:
            uid = self.request.matchdict.get('uid', None)

        if old_version is None:
            old_version = int(self.request.matchdict.get('old', None))

        if new_version is None:
            new_version = int(self.request.matchdict.get('new', None))

        if new_version < old_version:
            raise HTTPBadRequest()

        # Get the old, reference stakeholder object
        try:
            old = self.stakeholder_protocol3.read_one_by_version(self.request, uid, old_version)
        except IndexError as e:
            return HTTPFound(self.request.route_url('stakeholders_compare_versions', uid=uid, old=old_version-1, new=old_version))

        # Try to get the new stakeholder object
        try:
            new = self.stakeholder_protocol3.read_one_by_version(self.request, uid, new_version)
        except IndexError as e:
            return HTTPFound(self.request.route_url('stakeholders_compare_versions', uid=uid, old=old_version, new=new_version-1))

        available_versions = []
        for i in Session.query(Stakeholder.version).filter(Stakeholder.stakeholder_identifier == uid):
            available_versions.append(i[0])

        compare_url = self.request.route_url('stakeholders_compare', uid=uid)

        add_ons = {
        'available_versions': available_versions,
        'compare_url': compare_url,
        'ref_version': old_version,
        'new_version': new_version
        }
        return dict(self._compare_taggroups(old, new).items() + add_ons.items())

    @view_config(route_name='stakeholders_review_versions', renderer='lmkp:templates/review_versions.mak', permission='moderate')
    def review_stakeholder(self):
        """
        Review two stakeholder versions together
        """

        # Get the activity identifier
        uid = self.request.matchdict.get('uid', None)

        additional_vars = {}
        additional_vars['identifier'] = uid
        additional_vars['next_url'] = self.request.route_url('stakeholders_review_versions', uid=uid)
        additional_vars['type'] = 'stakeholders'

        # Get the current active version number
        o = Session.query(Stakeholder.version).filter(Stakeholder.stakeholder_identifier == uid).filter(Stakeholder.fk_status == 2).first()

        # If there is no active version yet, just show the first version
        if o is None:

            # Show the first version
            version = 1

            # Set the first version as version to review
            additional_vars['version'] = version

            stakeholder = self.stakeholder_protocol3.read_one_by_version(self.request, uid, version)

            return dict(self._review_one_version(stakeholder, uid, version).items() + additional_vars.items())

        # Get the latest version number
        l = Session.query(max(Stakeholder.version)).filter(Stakeholder.stakeholder_identifier == uid).first()
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
        old = self.stakeholder_protocol3.read_one_by_version(self.request, uid, old_version)

        # Get the new version
        try:
            new = self.stakeholder_protocol3.read_one_by_version(self.request, uid, new_version)
        # If there is no newer version, catch the exception and redirect the page
        # to the standard html view
        except IndexError as e:
            return HTTPFound(self.request.route_url('stakeholders_read_one_active', output='html', uid=uid))

        additional_vars['version'] = new_version
        return dict(self._compare_taggroups(old, new).items() + additional_vars.items())