from geoalchemy import functions
from lmkp.models.database_objects import Activity
from lmkp.models.database_objects import Changeset
from lmkp.models.database_objects import Profile
from lmkp.models.database_objects import Stakeholder
from lmkp.models.database_objects import Status
from lmkp.models.database_objects import User
from lmkp.models.meta import DBSession as Session
from lmkp.views.config import get_mandatory_keys
from lmkp.views.views import BaseView
import logging
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPBadRequest
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import not_
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.functions import min
import json

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
        toDelete = True
        for new_taggroup in new.get_taggroups():
            if old.find_taggroup_by_tg_id(new_taggroup.get_tg_id()) is None:
                current_row = {}
                # Write the new one
                new_tags = []
                for t in new_taggroup.get_tags():
                    if t.get_key() is not None and t.get_value() is not None:
                        # Only add tag if it is not empty (happens when item is
                        # deleted.
                        new_tags.append({'key': t.get_key(),
                                        'value': t.get_value()})
                        toDelete = False
                if len(new_tags) > 0:
                    # Only add tags if there is some content in them
                    current_row['new'] = {'class': 'add', 'tags': new_tags}
                    current_row['ref'] = {'class': '', 'tags': []}
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
                for t in inv._feature.to_tags(self.request):
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
                for t in inv._feature.to_tags(self.request):
                    old_tags.append(t)
                current_row['ref'] = {'class': 'remove involvement', 'tags': old_tags}
                # Write the new one
                new_tags = []
                new_tags = []
                for t in new_inv._feature.to_tags(self.request):
                    new_tags.append(t)
                current_row['new'] = {'class': 'add involvement', 'tags': new_tags}

                involvements_table.append(current_row)

            else:
                current_row = {}
                # Write the old one
                old_tags = []
                for t in inv._feature.to_tags(self.request):
                    old_tags.append(t)
                current_row['ref'] = {'class': 'involvement', 'tags': old_tags}
                # Write the new one
                new_tags = []
                for t in new_inv._feature.to_tags(self.request):
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

                for t in inv._feature.to_tags(self.request):
                    new_tags.append(t)

                reviewable = 0
                reviewable = self._review_check_involvement(
                    inv._feature.getMappedClass(),
                    inv._feature.get_guid(),
                    inv._feature.get_version()
                )
                current_row['reviewable'] = reviewable

                current_row['new'] = {
                    'class': 'add involvement',
                    'identifier': inv._feature.get_guid(),
                    'tags': new_tags
                }

                involvements_table.append(current_row)

        return {
            'taggroups': table,
            'involvements': involvements_table,
            'to_delete': toDelete
        }

    def _review_check_involvement(self, mappedClass, identifier, version):
        """
        Function to check if an item can be reviewed through involvements or
        not.
        Assumptions: Involvements can only be reviewed from Activity side.

        mappedClass: The class where a review of the version is to be made
          through the involvement
        identifier: The identifier of the item to review through the involvement
        version: The version of the item to review through the involvement
        """

        if mappedClass == Stakeholder:
            """
            The Stakeholder CANNOT be reviewed if:
            [-1] The Stakeholder does not exist.
            [-2] There is no active version of the Stakeholder.

            The Stakeholder CAN be reviewed if:
            [1] There exists an active version of the Stakeholder.
            """

            q = Session.query(
                    Stakeholder.fk_status
                ).\
                filter(Stakeholder.identifier == identifier).\
                all()

            if q is None:
                # The Stakeholder does not exist
                return -1

            for s in q:
                if s.fk_status == 2:
                    # There exists an active version of the Stakeholder.
                    return 1

            # There is no active version of the Stakeholder.
            return -2

        elif mappedClass == Activity:
            """
            The Activity cannot be reviewed from Stakeholder side
            [-3]
            """

            return -3

        return 0

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
            for t in inv._feature.to_tags(self.request):
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
            for t in inv._feature.to_tags(self.request):
                new_inv_tags.append(t)

            reviewable = 0
            reviewable = self._review_check_involvement(
                    inv._feature.getMappedClass(),
                    inv._feature.get_guid(),
                    inv._feature.get_version()
                )
            current_row['reviewable'] = reviewable

            current_row['new'] = {
                'class': 'add involvement',
                'identifier': inv._feature.get_guid(),
                'tags': new_inv_tags
            }
            involvements_table.append(current_row)

        return {'taggroups': table, 'involvements': involvements_table}

    def _get_active_pending_versions(self, mappedClass, uid):
        """
        Returns the current active version and the pending version to review
        """
        # TODO: Is this still needed?

        def _check_mandatory_keys():
            mandatory_keys = get_mandatory_keys(self.request, 'a')
            log.debug(mandatory_keys)

        # Get the current active version number
        av = Session.query(
                mappedClass.version
            ).\
            filter(mappedClass.identifier == uid).\
            filter(mappedClass.fk_status == 2).\
            first()
        active_version = av.version if av is not None else None

        # Get the lowest pending version
        pv = Session.query(min(mappedClass.version)).\
            filter(mappedClass.identifier == uid).\
            filter(mappedClass.fk_status == 1).\
            first()
        pending_version = pv.version if pv is not None else None

        # Some logging
        log.debug("active version: %s" % active_version)
        log.debug("pending version: %s" % pending_version)

        return active_version, pending_version

    def _get_metadata(self, mappedClass, uid, refVersion, newVersion):

        refTimestamp = newTimestamp = None
        refUserid = newUserid = None
        refUsername = newUsername = None

        refQuery = Session.query(
                Changeset.timestamp,
                User.id.label('userid'),
                User.username
            ).\
            join(mappedClass).\
            join(User, Changeset.fk_user == User.id).\
            filter(mappedClass.identifier == uid).\
            filter(mappedClass.version == refVersion).\
            first()

        if refQuery is not None:
            refTimestamp = refQuery.timestamp
            refUserid = refQuery.userid
            refUsername = refQuery.username

        newQuery = Session.query(
                Changeset.timestamp,
                User.id.label('userid'),
                User.username
            ).\
            join(mappedClass).\
            join(User, Changeset.fk_user == User.id).\
            filter(mappedClass.identifier == uid).\
            filter(mappedClass.version == newVersion).\
            first()

        if newQuery is not None:
            newTimestamp = newQuery.timestamp
            newUserid = newQuery.userid
            newUsername = newQuery.username

        metadata = {
            'ref_version': refVersion,
            'ref_timestamp': str(refTimestamp),
            'ref_userid': refUserid,
            'ref_username': refUsername,
            'new_version': newVersion,
            'new_timestamp': str(newTimestamp),
            'new_userid': newUserid,
            'new_username': newUsername,
            'identifier': uid,
            'type': mappedClass.__table__.name,
        }

        return metadata

    def _get_available_versions(self, mappedClass, uid, review=False):
        """
        Returns an array with all versions that are available to the current
        user. Moderators get all versions for Stakeholders and Activity if later
        lies within the moderator's profile. Editors get all active and inactive
        versions as well as their own edits. Public users only get inactive and
        active versions.
        If 'review' is true, only return the active and any pending versions.
        """

        def _get_query_for_editors():
            """
            Returns a query that selects versions available to editors.
            """
            active_versions = Session.query(
                    mappedClass.version,
                    mappedClass.fk_status
                ).\
                filter(mappedClass.identifier == uid).\
                filter(or_(mappedClass.fk_status == 2, mappedClass.fk_status == 3))

            own_filters = and_(mappedClass.identifier == uid, \
                               not_(mappedClass.fk_status == 2), \
                               not_(mappedClass.fk_status == 3), \
                               User.username == self.request.user.username)
            own_versions = Session.query(
                    mappedClass.version,
                    mappedClass.fk_status
                ).\
                join(Changeset).\
                join(User).\
                filter(*own_filters)
            return active_versions.union(own_versions)


        # Query that selects available versions
        versions_query = None

#        log.debug("effective principals: %s" % self.request.effective_principals)

        # An administrator sees in any cases all versions
        if self.request.effective_principals is not None and 'group:administrators' in self.request.effective_principals:
            versions_query = Session.query(
                    mappedClass.version,
                    mappedClass.fk_status,
                    mappedClass.id
                ).filter(mappedClass.identifier == uid)

        # An user with moderator privileges can see all versions within his profile
        elif self.request.effective_principals is not None and 'group:moderators' in self.request.effective_principals:

            # Try if mappedClass is an Activity and lies within the moderator's profile
            try:
                profile_filters = []
                # Get all profiles for the current moderator
                profiles = Session.query(Profile).filter(Profile.users.any(username=self.request.user.username))
                for p in profiles.all():
                    profile_filters.append(functions.intersects(mappedClass.point, p.geometry))

                # Check if current Activity is within the moderator's profile
                count = Session.query(mappedClass).filter(mappedClass.identifier == uid).filter(or_(*profile_filters)).count()
                # Activity is within the moderator's profile, then show all versions
                if count > 0:
                    versions_query = Session.query(
                            mappedClass.version,
                            mappedClass.fk_status,
                            mappedClass.id
                        ).filter(mappedClass.identifier == uid)
                # If not the moderator gets normal editor privileges
                else:
                    versions_query = _get_query_for_editors()
            # In case mappedClass is a Stakeholder, show anyway all versions
            except AttributeError:
                versions_query = Session.query(
                        mappedClass.version,
                        mappedClass.fk_status,
                        mappedClass.id
                    ).filter(mappedClass.identifier == uid)

        # An user with at least editor privileges can see all public versions_query
        # and his own edits
        elif self.request.effective_principals is not None and 'group:editors' in self.request.effective_principals:
            versions_query = _get_query_for_editors()

        # Public users i.e. not logged in users see only active and inactive versions
        else:
            versions_query = Session.query(
                    mappedClass.version,
                    mappedClass.fk_status,
                    mappedClass.id
                ).\
                filter(mappedClass.identifier == uid).\
                filter(or_(mappedClass.fk_status == 2, mappedClass.fk_status == 3))

        # Create a list of available versions
        available_versions = []
        for i in versions_query.order_by(mappedClass.version).all():
            if review is False or i.fk_status == 1 or i.fk_status == 2:
                available_versions.append({
                    'version': i.version,
                    'status': i.fk_status
                })

#        log.debug("Available Versions for object %s:\n%s" % (uid, available_versions))

        return available_versions

    def _get_valid_versions(self, mappedClass, uid, review=False):
        """
        Returns two version numbers:
        - the base version number: if not indicated explicitely, the active
          version is returned if available, else version 1
        - the version number to compare with: if not indicated explicitely, the
          first pending version is returned else version 1
        """

        # Check permissions
        available_versions = self._get_available_versions(
            mappedClass, uid, review=review
        )

        # Find out available versions and if possible active and first pending
        # version
        v = []
        active_version = pending_version = None
        for av in available_versions:
            v.append(av.get('version'))
            if av.get('status') == 2:
                active_version = av.get('version')
            if av.get('status') == 1:
                if pending_version is None or pending_version > av.get('version'):
                    pending_version = av.get('version')

        # Try to get the versions or set reference and new version
        versions = self.request.matchdict.get('versions')
        try:
            ref_version = int(versions[0])
        except (IndexError, TypeError):
            #
            ref_version = active_version if active_version is not None else 0
        except ValueError as e:
            raise HTTPBadRequest("ValueError: %s" % e)

        try:
            new_version = int(versions[1])
        except (IndexError, TypeError):
            if pending_version is not None:
                new_version = pending_version
            elif active_version is not None:
                new_version = active_version
            else:
                new_version = 1
        except ValueError as e:
            raise HTTPBadRequest("ValueError: %s" % e)

        if ((ref_version == 0 and new_version not in v)
            or (ref_version != 0 and ref_version not in v or new_version not in v)):
            raise HTTPForbidden()

        return ref_version, new_version

    def recalc(self, mappedClass, item, diff):
        """
        Function to extract parts relevant to a given item out of a complete
        changeset diff. It then applies this diff to the item and returns the
        item
        """

        if mappedClass == Activity:
            diff_keyword = 'activities'
            other_diff_keyword = 'stakeholders'
        elif mappedClass == Stakeholder:
            diff_keyword = 'stakeholders'
            other_diff_keyword = 'activities'
        else:
            diff_keyword = None

        new_item = None
        if (diff_keyword is not None and diff_keyword in diff
            and diff[diff_keyword] is not None):
            for item_diff in diff[diff_keyword]:
                if ('id' in item_diff and item_diff['id'] is not None
                    and item_diff['id'] == item.get_guid()):
                        
                    # Apply the diff to show a preview of the new version
                    new_item = self.protocol._apply_diff(
                        self.request,
                        mappedClass,
                        item.get_guid(),
                        item.get_version(),
                        item_diff,
                        item,
                        db = False,
                        review = True
                    )

                    # Also handle involvements
                    inv_diff = (item_diff[other_diff_keyword]
                        if other_diff_keyword in item_diff
                        else None)
                    self.protocol._handle_involvements(
                        self.request,
                        item,
                        new_item,
                        inv_diff,
                        None,
                        db = False
                    )

        if new_item is None:
            new_item = item

        return new_item

    def get_comparison(self, mappedClass, uid, ref_version_number,
        new_version_number):
        """
        Function to do the actual comparison and return a json
        """
        
        recalculated = False

        if (ref_version_number == 0
            or (new_version_number == 1 and ref_version_number == 1)):
            ref_object = None
            ref_version_number = None
        else:
            # Get the reference object
            ref_object = self.protocol.read_one_by_version(
                self.request, uid, ref_version_number, translate=False
            )

        # Check to see if the new version is based directly on the ref version
        new_previous_version = Session.query(
                mappedClass.previous_version
            ).\
            filter(mappedClass.identifier == uid).\
            filter(mappedClass.version == new_version_number).\
            first()

        if (ref_object is None and new_previous_version is not None or
            new_version_number == 1 or
            ref_version_number == new_version_number or
            (new_previous_version is not None
            and new_previous_version.previous_version == ref_version_number)):
            # Show the new version as it is in the database
            new_object = self.protocol.read_one_by_version(
                self.request, uid, new_version_number, translate=False
            )
        else:
            # Query the diff of the new version to apply to the ref version
            new_diff_query = Session.query(
                    Changeset.diff
                ).\
                join(mappedClass).\
                filter(mappedClass.identifier == uid).\
                filter(mappedClass.version == new_version_number).\
                first()
            new_diff = json.loads(new_diff_query.diff)

            # Get the reference object
            new_object = self.protocol.read_one_by_version(
                self.request, uid, ref_version_number, translate=False
            )

            # Apply the diff to the ref_object
            new_object = self.recalc(mappedClass, new_object, new_diff)
            recalculated = True

        return [ref_object, new_object], recalculated
