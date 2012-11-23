__author__ = "Adrian Weber, Centre for Development and Environment, University of Bern"
__date__ = "$Nov 20, 2012 4:05:40 PM$"

from lmkp.models.database_objects import Changeset
from lmkp.models.database_objects import Stakeholder
from lmkp.models.meta import DBSession as Session
from lmkp.views.review import BaseReview
import logging
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from pyramid_handlers import action
from sqlalchemy.sql.functions import max

log = logging.getLogger(__name__)

class StakeholderReview(BaseReview):

    @action(name='html', renderer='lmkp:templates/compare_versions.mak', permission='moderate')
    def compare_by_version_html(self):

        uid = self.request.matchdict.get('uid', None)

        available_versions = []
        for i in Session.query(Stakeholder.version).filter(Stakeholder.stakeholder_identifier == uid):
            available_versions.append(i[0])

        additional_params = {
        'available_versions': available_versions
        }

        return additional_params

    @action(name='json', renderer='json', permission='moderate')
    def compare_stakeholder_by_versions_json(self, uid=None, versions=None):

        if uid is None:
            uid = self.request.matchdict.get('uid', None)

        if versions is None:
            versions = self.request.matchdict.get('versions', (1, 1))

        try:
            old_version = int(versions[0])
        except IndexError:
            old_version = 1
        except ValueError as e:
            raise HTTPBadRequest("ValueError: %s" % e)

        try:
            new_version = int(versions[1])
        except IndexError:
            new_version = 1
        except ValueError as e:
            raise HTTPBadRequest("ValueError: %s" % e)

        # Get the old, reference stakeholder object
        try:
            old = self.stakeholder_protocol3.read_one_by_version(self.request, uid, old_version)
        except IndexError as e:
            return HTTPFound(self.request.route_url('stakeholders_compare_versions', output=output, uid=uid, old=old_version-1, new=old_version))

        # Try to get the new stakeholder object
        try:
            new = self.stakeholder_protocol3.read_one_by_version(self.request, uid, new_version)
        except IndexError as e:
            return self.compare_stakeholder_by_versions_json(uid=uid, versions=(old_version,(new_version-1)))

        ref_timestamp = Session.query(Changeset.timestamp).join(Stakeholder).filter(Stakeholder.stakeholder_identifier == uid).filter(Stakeholder.version == old_version).first()
        new_timestamp = Session.query(Changeset.timestamp).join(Stakeholder).filter(Stakeholder.stakeholder_identifier == uid).filter(Stakeholder.version == new_version).first()

        additional_params = {
        'ref_title': "Version %s as of %s" % (old_version, ref_timestamp[0].strftime('%H:%M, %d-%b-%Y')),
        'new_title': "Version %s as of %s" % (new_version, new_timestamp[0].strftime('%H:%M, %d-%b-%Y'))
        }

        result = dict(self._compare_taggroups(old, new).items() + additional_params.items())

        return result

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