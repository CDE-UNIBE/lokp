from lmkp.models.database_objects import Changeset
from lmkp.models.database_objects import Status
from lmkp.models.meta import DBSession as Session
from lmkp.views.activity_protocol3 import ActivityProtocol3
from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
from lmkp.views.translation import statusMap
from lmkp.views.views import BaseView
import logging
from sqlalchemy.sql.functions import min
import string

log = logging.getLogger(__name__)

class BaseReview(BaseView):

    def __init__(self, request):
        super(BaseReview, self).__init__(request)
        self._handle_parameters()

    def _compare_taggroups(self, old, new):

        table = []

        if old is None and new is not None:
            return self._write_new_taggroups(new)

        if old is not None and new is None:
            return self._write_old_taggroups(old)

        # TODO: Compare also the geometry!!

        # Loop the old and check for the same taggroup in the new one
        for old_taggroup in old.get_taggroups():
            new_taggroup = new.find_taggroup_by_tg_id(old_taggroup.get_tg_id())

            # The taggroup does not exist anymore:
            if new_taggroup is None:
                current_row = {}
                old_tags = []
                for t in old_taggroup.get_tags():
                    old_tags.append({'key': t.get_key(),
                                    'value': t.get_value()})
                    current_row['ref'] = {'class': 'remove', 'tags': old_tags}
                    current_row['new'] = {'class': '', 'tags': []}
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

                current_row = {}
                old_tags_class = new_tags_class = ''
                if taggroup_has_changed:
                    old_tags_class = 'remove'
                    new_tags_class = 'add'

                # Write the old one
                old_tags = []
                for t in old_taggroup.get_tags():
                    old_tags.append({'key': t.get_key(),
                                    'value': t.get_value()})
                current_row['ref'] = {'class': old_tags_class, 'tags': old_tags}
                # Write the new one
                new_tags = []
                for t in new_taggroup.get_tags():
                    new_tags.append({'key': t.get_key(),
                                    'value': t.get_value()})
                current_row['new'] = {'class': new_tags_class, 'tags': new_tags}

                table.append(current_row)

        # Search for new taggroups
        for new_taggroup in new.get_taggroups():

            if old.find_taggroup_by_tg_id(new_taggroup.get_tg_id()) is None:
                current_row = {}
                current_row['ref'] = {'class': '', 'tags': []}
                # Write the new one
                new_tags = []
                for t in new_taggroup.get_tags():
                    new_tags.append({'key': t.get_key(),
                                    'value': t.get_value()})
                current_row['new'] = {'class': 'add', 'tags': new_tags}

                table.append(current_row)

        # TODO Compare the involvements properly

        involvements_table = []

        # Finally compare also the involvments but NOT the tags of the involved stakeholders
        for inv in old.get_involvements():

            new_inv = new.find_involvement_by_guid(inv.get_guid())

            # Involvement has been deleted
            if new_inv == None:
                current_row = {}

                # Write the old one
                old_tags = []
                for t in inv._feature.to_tags():
                    old_tags.append(t)
                current_row['ref'] = {'class': 'remove involvement', 'tags': old_tags}
                # Write the new one
                current_row['new'] = {'class': 'involvement', 'tags': []}

                involvements_table.append(current_row)

            # Role has changed
            elif inv.get_role_id() != new_inv.get_role_id():
                current_row = {}

                # Write the old one
                old_tags = []
                for t in inv._feature.to_tags():
                    old_tags.append(t)
                current_row['ref'] = {'class': 'remove involvement', 'tags': old_tags}
                # Write the new one
                new_tags = []
                new_tags = []
                for t in new_inv._feature.to_tags():
                    new_tags.append(t)
                current_row['new'] = {'class': 'add involvement', 'tags': new_tags}

                involvements_table.append(current_row)

            else:
                current_row = {}
                # Write the old one
                old_tags = []
                for t in inv._feature.to_tags():
                    old_tags.append(t)
                current_row['ref'] = {'class': 'involvement', 'tags': old_tags}
                # Write the new one
                new_tags = []
                for t in new_inv._feature.to_tags():
                    new_tags.append(t)
                current_row['new'] = {'class': 'involvement', 'tags': new_tags}

                involvements_table.append(current_row)


        # Find new involvements:
        for inv in new.get_involvements():

            old_inv = old.find_involvement_by_guid(inv.get_guid())

            if old_inv is None:

                current_row = {}

                # Write the old one
                current_row['ref'] = {'class': '', 'tags': []}
                # Write the new one
                new_tags = []

                for t in inv._feature.to_tags():
                    new_tags.append(t)

                current_row['new'] = {'class': 'add involvement', 'tags': new_tags}

                involvements_table.append(current_row)


        return {'taggroups': table, 'involvements': involvements_table}

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

        return {'taggroups': table}

    def _write_old_taggroups(self, old):

        table = []

        # Search for new taggroups
        for old_taggroup in old.get_taggroups():

            current_row = {}
            old_tags = []
            for t in old_taggroup.get_tags():
                old_tags.append({'key': t.get_key(),
                                'value': t.get_value()})
            current_row['ref'] = {'class': '', 'tags': old_tags}

            current_row['new'] = {'class': '', 'tags': []}

            table.append(current_row)

        involvements_table = []

        # Find new involvements:
        for inv in old.get_involvements():

            current_row = {}

            old_inv_tags = []
            for t in inv._feature.to_tags():
                old_inv_tags.append(t)

            # Write the old one
            current_row['ref'] = {'class': '', 'tags': old_inv_tags}
            # Write the new one

            current_row['new'] = {'class': '', 'tags': []}

            involvements_table.append(current_row)

        return {'taggroups': table, 'involvements': involvements_table}

    def _write_new_taggroups(self, new):

        table = []

        # Search for new taggroups
        for new_taggroup in new.get_taggroups():

            current_row = {}
            current_row['ref'] = {'class': '', 'tags': []}
            # Write the new one
            new_tags = []
            for t in new_taggroup.get_tags():
                new_tags.append({'key': t.get_key(),
                                'value': t.get_value()})
            current_row['new'] = {'class': 'add', 'tags': new_tags}

            table.append(current_row)

        # Write involvements:
        involvements_table = []
        for inv in new.get_involvements():

            current_row = {}

            current_row['ref'] = {'class': '', 'tags': []}

            new_inv_tags = []
            for t in inv._feature.to_tags():
                new_inv_tags.append(t)

            current_row['new'] = {'class': '', 'tags': new_inv_tags}
            involvements_table.append(current_row)

        return {'taggroups': table, 'involvements': involvements_table}

    def _get_active_pending_versions(self, mappedClass, uid):
        """
        Returns the current active version and the pending version to review
        """

        # Get the current active version number
        av = Session.query(mappedClass.version).filter(mappedClass.identifier == uid).filter(mappedClass.fk_status == 2).first()

        try:
            active_version = int(av[0])
        except TypeError:
            return None, 1

        # Get the lowest pending version
        pv = Session.query(min(mappedClass.version)).\
            filter(mappedClass.identifier == uid).\
            filter(mappedClass.fk_status == 1).\
            filter(mappedClass.version > active_version).\
            first()

        try:
            pending_version = int(pv[0])
        except TypeError:
            pending_version = None

        # Some logging
        log.debug("active version: %s" % active_version)
        log.debug("pending version: %s" % pending_version)

        return active_version, pending_version

    def _get_active_pending_version_descriptions(self, mappedClass, uid, active_version, pending_version):

        _ = self.request.translate

        active_title = pending_title = ''
        active_status = pending_status = None

        try:
            active_timestamp, active_status = Session.query(Changeset.timestamp, Status.name).\
                join(mappedClass).\
                join(Status).\
                filter(mappedClass.identifier == uid).\
                filter(mappedClass.version == active_version).first()
        except TypeError:
            pass
        try:
            pending_timestamp, pending_status = Session.query(Changeset.timestamp, Status.name).\
                join(mappedClass).\
                join(Status).\
                filter(mappedClass.identifier == uid).\
                filter(mappedClass.version == pending_version).first()
        except TypeError:
            pass

        try:
            active_title = "%s version %s as of %s" % (string.capitalize(_(statusMap[active_status])), active_version, active_timestamp.strftime('%H:%M, %d-%b-%Y'));
        except:
            pass
        try:
            pending_title = "%s version %s as of %s" % (string.capitalize(_(statusMap[pending_status])), pending_version, pending_timestamp.strftime('%H:%M, %d-%b-%Y'));
        except:
            pass

        return active_title, pending_title