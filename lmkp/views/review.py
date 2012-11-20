from lmkp.models.meta import DBSession as Session
from lmkp.views.activity_protocol3 import ActivityProtocol3
from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
from lmkp.views.views import BaseView
import logging

log = logging.getLogger(__name__)

class BaseReview(BaseView):

    def __init__(self, request):
        self.request = request
        self.activity_protocol3 = ActivityProtocol3(Session)
        self.stakeholder_protocol3 = StakeholderProtocol3(Session)

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

    def _review_one_version(self, obj, uid, version):

        table = []

        # First write the headers
        header_row = []
        header_row.append({'class': 'title', 'tags': [
                          {'key': 'version', 'value': obj.get_version()},
                          {'key': 'status', 'value': obj.get_status()}
                          ]})

        table.append(header_row)

        for taggroup in obj.get_taggroups():

            tags = []
            
            for t in taggroup.get_tags():
                tags.append({'key': t.get_key(), 'value': t.get_value()})
            table.append([{'class': '', 'tags': tags}])



        return {'data': table}