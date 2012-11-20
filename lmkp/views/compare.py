from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session
from lmkp.views.activity_protocol3 import ActivityProtocol3
from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
from lmkp.views.views import BaseView
import logging
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config
from sqlalchemy.sql.functions import max

log = logging.getLogger(__name__)

class ReviewView(BaseView):

    def __init__(self, request):
        self.request = request
        self.activity_protocol3 = ActivityProtocol3(Session)
        self.stakeholder_protocol3 = StakeholderProtocol3(Session)

    @view_config(route_name='activities_review_versions', renderer='lmkp:templates/review_versions.mak', permission='moderate')
    def review_activities(self):
        #uid = "d2a680ca-014b-4873-87f4-d588aa9fd839"
        uid = self.request.matchdict.get('uid', None)

        o = Session.query(Activity.version).filter(Activity.activity_identifier == uid).filter(Activity.fk_status == 2).first()
        l = Session.query(max(Activity.version)).filter(Activity.activity_identifier == uid).first()
        old_version = int(o[0])
        new_version = old_version + 1
        latest_version = int(l[0])

        log.debug("active version: %s" % old_version)
        log.debug("pending version: %s" % new_version)
        log.debug("latest version: %s" % latest_version)
        log.debug(new_version <= old_version)

        if new_version < old_version:
            raise HTTPBadRequest("Pending version must be newer than active version.")

        old = self.activity_protocol3.read_one_by_version(self.request, uid, old_version)

        new = self.activity_protocol3.read_one_by_version(self.request, uid, new_version)
        
        if latest_version > new_version:
            new_window_location = "/activities/review/%s" % uid
            button_text = "Review and continue"
        else:
            new_window_location = "/activities/html/%s" % uid
            button_text = "Review and return"
        return dict(self._compare_taggroups(old, new).items() + {'button_text': button_text, 'window_location': new_window_location}.items())

    @view_config(route_name='activities_compare', renderer='lmkp:templates/compare_versions.mak', permission='moderate')
    def compare_activities(self, uid=None):

        uid = self.request.matchdict.get('uid', None)

        return self.compare_activities_versions(uid, 1, 1)

    @view_config(route_name='activities_compare_versions', renderer='lmkp:templates/compare_versions.mak', permission='moderate')
    def compare_activities_versions(self, uid=None, old_version=None, new_version=None):

        if uid is None:
            uid = self.request.matchdict.get('uid', None)

        if old_version is None:
            old_version = self.request.matchdict.get('old', 1)

        if new_version is None:
            new_version = self.request.matchdict.get('new', 1)

        if new_version < old_version:
            raise HTTPBadRequest("Reference version %s is older than new version %s" % (old_version, new_version))

        old = self.activity_protocol3.read_one_by_version(self.request, uid, old_version)

        new = self.activity_protocol3.read_one_by_version(self.request, uid, new_version)

        available_versions = []
        for i in Session.query(Activity.version).filter(Activity.activity_identifier == uid):
            available_versions.append(i[0])

        compare_url = "/activities/compare/%s" % uid

        add_ons = {
        'available_versions': available_versions,
        'compare_url': compare_url,
        'ref_version': old_version,
        'new_version': new_version
        }
        return dict(self._compare_taggroups(old, new).items() + add_ons.items())

    @view_config(route_name='stakeholders_compare_versions', renderer='lmkp:templates/compare_versions.mak')
    def compare_stakeholders(self):

        #uid = "d2a680ca-014b-4873-87f4-d588aa9fd839"
        uid = self.request.matchdict.get('uid', None)

        #old_version = 1
        old_version = self.request.matchdict.get('old_version', None)

        # new_version = 3
        new_version = self.request.matchdict.get('new_version', None)

        if new_version <= old_version:
            raise HTTPBadRequest()

        old = self.stakeholder_protocol3.read_one_by_version(self.request, uid, old_version)

        new = self.stakeholder_protocol3.read_one_by_version(self.request, uid, new_version)

        return self._compare_taggroups(old, new)

    def _compare_taggroups(self, old, new):

        table = []

        # First write the headers
        header_row = []
        header_row.append({'class': 'title', 'tags': [
                          {'key': 'version', 'value': old.get_version()},
                          {'key': 'status', 'value': old.get_status()}
                          ]})

        header_row.append({'class': 'title', 'tags': [
                          {'key': 'version', 'value': new.get_version()},
                          {'key': 'status', 'value': new.get_status()}
                          ]})

        table.append(header_row)

        # TODO: Compare also the geometry!!

        # Loop the old and check for the same taggroup in the new one
        for old_taggroup in old.get_taggroups():
            new_taggroup = new.find_taggroup_by_tg_id(old_taggroup.get_tg_id())

            # The taggroup does not exist anymore:
            if new_taggroup is None:
                current_row = []
                old_tags = []
                for t in old_taggroup.get_tags():
                    old_tags.append({'key': t.get_key(),
                                    'value': t.get_value()})
                    current_row.append({'class': 'remove', 'tags': old_tags})
                    current_row.append({'class': '', 'tags': []})
                table.append(current_row)

            # The taggroup does still exist:
            elif new_taggroup is not None:
                # Compare the old taggroup with the new one
                taggroup_has_changed = False

                if new_taggroup is None:
                    taggroup_has_changed = True

                old_tags = []
                for t in old_taggroup.get_tags():

                    if new_taggroup.get_tag_by_key(t.get_key()) is None:
                        taggroup_has_changed = True
                    elif new_taggroup.get_tag_by_key(t.get_key()).get_value() != t.get_value():
                        taggroup_has_changed = True

                # Test also the other way round
                for t in new_taggroup.get_tags():
                    if old_taggroup.get_tag_by_key(t.get_key()) is None:
                        taggroup_has_changed = True

                current_row = []
                old_tags_class = new_tags_class = ''
                if taggroup_has_changed:
                    old_tags_class = 'remove'
                    new_tags_class = 'add'

                # Write the old one
                old_tags = []
                for t in old_taggroup.get_tags():
                    old_tags.append({'key': t.get_key(),
                                    'value': t.get_value()})
                current_row.append({'class': old_tags_class, 'tags': old_tags})
                # Write the new one
                new_tags = []
                for t in new_taggroup.get_tags():
                    new_tags.append({'key': t.get_key(),
                                    'value': t.get_value()})
                current_row.append({'class': new_tags_class, 'tags': new_tags})

                table.append(current_row)

        # Search for new taggroups
        for new_taggroup in new.get_taggroups():

            if old.find_taggroup_by_tg_id(new_taggroup.get_tg_id()) is None:
                current_row = []
                current_row.append({'class': '', 'tags': []})
                # Write the new one
                new_tags = []
                for t in new_taggroup.get_tags():
                    new_tags.append({'key': t.get_key(),
                                    'value': t.get_value()})
                current_row.append({'class': 'add', 'tags': new_tags})

                table.append(current_row)

        # TODO Compare the involvements properly

        # Finally compare also the involvments but NOT the tags of the involved stakeholders
        for inv in old.get_involvements():

            new_inv = new.find_involvement_by_guid(inv.get_guid())

            # Involvement has been deleted
            if new_inv == None:
                current_row = []

                # Write the old one
                old_tags = []
                old_tags.append({'key': 'role',
                                'value': inv.get_role()})
                old_tags.append({'key': 'guid',
                                'value': inv.get_uid()})
                current_row.append({'class': 'remove', 'tags': old_tags})
                # Write the new one
                current_row.append({'class': '', 'tags': []})

                table.append(current_row)

            # Role has changed
            elif inv.get_role_id() != new_inv.get_role_id():
                current_row = []

                # Write the old one
                old_tags = []
                old_tags.append({'key': 'role',
                                'value': inv.get_role()})
                old_tags.append({'key': 'guid',
                                'value': inv.get_uid()})
                current_row.append({'class': 'remove', 'tags': old_tags})
                # Write the new one
                new_tags = []
                new_tags.append({'key': 'role',
                                'value': new_inv.get_role()})
                new_tags.append({'key': 'guid',
                                'value': new_inv.get_uid()})
                current_row.append({'class': 'add', 'tags': new_tags})

                table.append(current_row)

        # Find new involvements:
        for inv in new.get_involvements():

            old_inv = old.find_involvement_by_guid(inv.get_guid())

            if old_inv is None:
                current_row = []

                # Write the old one
                current_row.append({'class': '', 'tags': []})
                # Write the new one
                new_tags = []
                new_tags.append({'key': 'role',
                                'value': inv.get_role()})
                new_tags.append({'key': 'guid',
                                'value': inv.get_uid()})
                current_row.append({'class': 'add', 'tags': new_tags})

                table.append(current_row)


        return {'data': table}