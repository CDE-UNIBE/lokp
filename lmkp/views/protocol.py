import logging
from lmkp.config import locale_profile_directory_path
from lmkp.config import profile_directory_path
from lmkp.models.database_objects import Activity
from lmkp.models.database_objects import A_Key
from lmkp.models.database_objects import A_Tag
from lmkp.models.database_objects import A_Tag_Group
from lmkp.models.database_objects import A_Value
from lmkp.models.database_objects import Changeset
from lmkp.models.database_objects import Group
from lmkp.models.database_objects import Involvement
from lmkp.models.database_objects import Language
from lmkp.models.database_objects import Permission
from lmkp.models.database_objects import SH_Key
from lmkp.models.database_objects import SH_Tag
from lmkp.models.database_objects import SH_Tag_Group
from lmkp.models.database_objects import SH_Value
from lmkp.models.database_objects import Stakeholder
from lmkp.models.database_objects import Stakeholder_Role
from lmkp.models.database_objects import Status
from lmkp.views.config import merge_profiles
from lmkp.views.config import ACTIVITY_YAML
from lmkp.views.config import STAKEHOLDER_YAML
from lmkp.views.files import check_file_location_name
from lmkp.views.form_config import getCategoryList
from lmkp.models.database_objects import User
from shapely import wkb
from shapely.geometry import mapping as asGeoJSON
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import between
from sqlalchemy.types import Float
import datetime
from sqlalchemy import func
import yaml
import collections
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import unauthenticated_userid
from pyramid.security import effective_principals
from pyramid.i18n import get_localizer
from lmkp.views.review import BaseReview
import json
import geojson
from shapely.geometry import asShape

from lmkp.views.translation import statusMap
from lmkp.views.translation import get_translated_status

log = logging.getLogger(__name__)

class Protocol(object):
    """
    A class that contains general methods for the activity protocol and the
    stakeholder protocol as well
    """

    def __init__(self):
        # The following is a ConfigCategoryList object as in form_config.py
        self.categoryList = None

    def _get_timestamp_filter(self, request, AorSH, Changeset):
        """
        Returns a filter of IDs of a given timestamp.
        """

        # Item is now either still 'active' or it is 'inactive'
        status_list = ['active', 'inactive']

        timestamp = request.params.get('timestamp', None)
        if timestamp is not None:
            # Check if timestamp is valid
            try:
                t = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None

            # Subquery to get latest version for each identifier at given time
            version_subquery = self.Session.query(
                    AorSH.identifier.label('timestamp_identifier'),
                    func.max(AorSH.version).label('timestamp_version')
                ).\
                join(Changeset).\
                join(Status).\
                filter(Changeset.timestamp <= t).\
                filter(Status.name.in_(status_list)).\
                group_by(AorSH.identifier).\
                subquery()

            # Join the latest version again with itself to get its ID
            timestamp_subquery = self.Session.query(
                    AorSH.id.label('timestamp_id')
                ).\
                join(version_subquery, and_(
                    version_subquery.c.timestamp_identifier
                        == AorSH.identifier,
                    version_subquery.c.timestamp_version == AorSH.version)).\
                subquery()

            return timestamp_subquery

        return None

    def _get_versions(self, request):
        """
        Returns the requested versions if provided, else None
        """
        versions = request.params.get('versions', None)
        if versions is None:
            return None

        for v in versions.split(","):
            try:
                int(v)
            except ValueError:
                return None
        return versions.split(",")

    def _get_limit(self, request):

        limit = request.params.get('limit', None)
        if limit is not None:
            try:
                return int(limit)
            except ValueError:
                pass

        return None

    def _get_offset(self, request):
        """
        Returns the requested offset, default value is 0
        """
        offset = request.params.get('offset', 0)
        try:
            return int(offset)
        except ValueError:
            pass

        return 0

    def _get_user_status(self, principals=None):

        if principals is not None:
            return (
                'system.Authenticated' in principals,
                'group:moderators' in principals
            )

        return (
            None,
            None
        )

    def _get_status_detail(self, request, public_query):
        """
        For detail view.
        Default values are 'active', 'inactive' and 'deleted', as well as
        'pending' and 'edited' for moderators
        Only moderators can query 'pending' and 'edited'.
        """

        statusParameter = request.params.get('status', None)

        logged_in, is_moderator = self._get_user_status(
            effective_principals(request))

        try:
            status = statusParameter.split(',')
            arr = []
            for s in status:
                if s in statusMap:
                    if s == 'pending' or s == 'edited':
                        if logged_in and is_moderator:
                            arr.append(Status.name == s)
                    else:
                        arr.append(Status.name == s)
            if len(arr) > 0:
                return arr
        except AttributeError:
            pass

        ret = [
            Status.name == 'active',
            Status.name == 'inactive',
            Status.name == 'deleted'
        ]
        if logged_in and is_moderator and not public_query:
            ret.append(Status.name == 'pending')
            ret.append(Status.name == 'edited')
        return ret


    def _get_status(self, request, from_history=False):
        """
        Returns an ClauseElement array of requested activity status.
        Default value is active.
        It is possible to request activities with different status using
        status=active,pending
        Only moderators can query 'pending' and 'edited'.
        """

        statusParameter = request.params.get('status', None)

        logged_in, is_moderator = self._get_user_status(
            effective_principals(request))

        try:
            status = statusParameter.split(',')
            # Hard coded list of possible activity statii. Not very nice ... But more
            # performant than requesting the database
            arr = []
            for s in status:
                if s in statusMap:
                    if s == 'pending' or s == 'edited':
                        if logged_in and is_moderator:
                            arr.append(Status.name == s)
                    else:
                        arr.append(Status.name == s)

            if len(arr) > 0:
                return arr
        except AttributeError:
            pass

        # Special case: request came from history, return None
        if from_history is True:
            return None

        return [Status.name == "active"]

    def _get_involvement_status(self, request):
        """
        Returns a ClauseElement array of statuses used upon involvements.
        Default value is active.
        They are based on the following rules:
        - If not logged in, only show 'active' involvements
        """

        logged_in, is_moderator = self._get_user_status(
            effective_principals(request))

        statuses = [
            Status.name == 'active',
            Status.name == 'inactive'
        ]

        if logged_in:
            statuses.append(
                Status.name == 'pending'
            )


        #log.debug("Involvement statuses [array]:\n%s" % statuses)

        return statuses

    def _flag_add_involvement(self, this_object, this_status_id,
        other_status_id, other_identifier, other_version, other_user_id,
        stakeholder_role, request_user_id, public_query, logged_in,
        is_moderator):
        """
        Decide whether to attach an Involvement (to the _other_ object) to a
        Feature (to _this_ object).
        ''this_object'': The Feature object (activity / stakeholder) where the
          Involvement is to be attachted
        ''this_status_id'': The status id of the current Feature object
        ''other_status_id'': The status id of the other Feature object
        ''other_identifier'': The identifier of the other Feature object
        ''other_version'': The version of the other Feature object
        ''other_user_id'': The id of the user who submitted the other Feature
          object
        ''stakeholder_role'': The stakeholder role of the Involvement
        ''request_user_id'': The id of the currently logged in user
        ''public_query'': Boolean whether it is a public query (do not show
          pending) or not
        ''logged_in'': Boolean whether a user is logged in or not
        ''is_moderator'': Boolean whether a user is moderator for the current
          profile or not
        """

        # Flag indicating if Involvement to this Activity is not yet found
        # ('none') or not to be added ('false')
        inv = None

        # If ''this_status'' is 'deleted', do not show any Involvements
        if this_status_id == 4:
            inv = False

        # Involvements where Feature is 'pending' ...
        if inv is None and other_status_id == 1:
            # ... are never shown for public queries or if not logged in
            if public_query is True or not logged_in:
                inv = False
            else:
                # ... are only shown to moderators or to the user who submitted
                # the 'pending' other Feature
                if not is_moderator and other_user_id != request_user_id:
                    inv = False

        if inv is None:
            # Check if an Involvement to this Feature already exists
            inv = this_object.find_involvement_by_guid(other_identifier)
            if inv is not None:
                # Check if current Involvement has a different Role than the
                # Involvement already existing
                inv = this_object.find_involvement_by_role(other_identifier,
                    stakeholder_role)
                if inv is not None:
                    # Check if current Involvement points to a different Feature
                    # version than the Involvement already existing
                    inv = this_object.find_involvement(other_identifier,
                        stakeholder_role, other_version)
                    if inv is not None:
                        # If the current Involvement is 'active' and the
                        # previous Involvement was 'inactive', replace the
                        # previous Involvement
                        if (other_status_id == 2 and
                            this_object.find_involvement_by_role(
                                other_identifier, stakeholder_role).get_status()
                                == 3):
                            this_object.remove_involvement(
                                this_object.find_involvement_by_role(
                                    other_identifier, stakeholder_role))

        return inv

    def _get_pending_by_user(self, request):
        """
        """
        pending_user = request.params.get('show_pending', None)

        return pending_user is not None and pending_user == 'true'

    def _get_mark_complete(self, request):

        mark_complete = request.params.get('mark_complete', None)

        return mark_complete is not None and mark_complete == 'true'


    def _filter(self, request):
        """
        Returns
        - a SubQuery of A_Tags containing a union of all Key/Value pairs which
          fulfill the filter condition(s) for Activity attributes
        - a count of the Activity filters
        - a SubQuery of SH_Tags containing a union of all Key/Value pairs which
          fulfill the filter condition(s) for Stakeholder attributes
        - a count of the Stakeholder filters
        """

        def __get_filter_expression(prefix, value, op):

            # Use prefix to determine if A_Value or SH_Value
            if prefix == 'a':
                v = A_Value
            elif prefix == 'sh':
                v = SH_Value
            else:
                return None

            # Use cast function provided by SQLAlchemy to convert
            # database values to Float.
            # Note: PostgreSQL throws a cast error if comparison operator
            # 'equal' (=) is used. Therefore, 'between' is used.
            nbr_map = {
                'eq': between(cast(v.value, Float), value, value),
                'ne': cast(v.value, Float) != value,
                'lt': cast(v.value, Float) < value,
                'lte': cast(v.value, Float) <= value,
                'gt': cast(v.value, Float) > value,
                'gte': cast(v.value, Float) >= value
            }

            str_map = {
                # See http://www.postgresql.org/docs/9.1/static/functions-matching.html#FUNCTIONS-POSIX-REGEXP
                'like': v.value.op("~")(value),
                'ilike': v.value.op("~*")(value),
                'nlike': v.value.op("!~")(value),
                'nilike': v.value.op("!~*")(value)
            }

            # number comparison
            if op in nbr_map.keys():
                # make sure submitted value is a number
                try:
                    float(value)
                    return nbr_map[op]
                except:
                    pass

            elif op in str_map.keys():
                return str_map[op]

            return None

        a_filter_expr = []
        sh_filter_expr = []
        for k in request.params:
            # Collect filter expressions
            if len(request.params[k]) <= 0 or '__' not in k:
                continue
            try:
                prefix, col, op = k.split('__')
            except ValueError:
                continue
            # Several values can be queried for one attributes e.g.
            # project_use equals pending and signed. Build the URL
            # like: queryable=project_use&project_use__eq=pending,signed
            # First: Activity attributes
            if prefix == 'a':
                values = request.params[k].split(',')
                for v in values:
                    q = self.Session.query(
                            A_Tag.fk_a_tag_group.label('a_filter_tg_id')
                        ).\
                        join(A_Key).\
                        join(A_Value, A_Tag.fk_value == A_Value.id).\
                        filter(A_Key.key == col).\
                        filter(__get_filter_expression(prefix, v, op))
                    a_filter_expr.append(q)
            # Second: Stakeholder attributes
            elif prefix == 'sh':
                values = request.params[k].split(',')
                for v in values:
                    q = self.Session.query(
                            SH_Tag.fk_sh_tag_group.label('sh_filter_tg_id')
                        ).\
                        join(SH_Key).\
                        join(SH_Value, SH_Tag.fk_value == SH_Value.id).\
                        filter(SH_Key.key == col).\
                        filter(__get_filter_expression(prefix, v, op))
                    sh_filter_expr.append(q)

        return (a_filter_expr, len(a_filter_expr),
            sh_filter_expr, len(sh_filter_expr))

    def _get_logical_operator(self, request):
        """
        Return the logical operator if set, default is 'and'
        """
        return request.params.get("logical_op", "and").lower()

    def _get_order_direction(self, request):
        """
        Return the direction of ordering only if it is set to DESC
        """
        if request.params.get('dir', '').upper() == 'DESC':
            return 'DESC'

    def _get_translatedKV(self, lang, Key, Value):
        """
        Returns
        - a SubQuery with a list of all translated keys
        - a SubQuery with a list of all translated values
        """
        key_query = self.Session.query(Key.fk_key.label("key_original_id"),
                                Key.key.label("key_translated")).\
                    filter(Key.language == lang).\
                    subquery()
        value_query = self.Session.query(Value.fk_value.label("value_original_id"),
                                 Value.value.label("value_translated")).\
                     filter(Value.language == lang).\
                     subquery()
        return key_query, value_query

    def _get_order(self, request, Mapped_Class, Tag_Group, Tag, Key, Value):
        """
        Returns
        - a SubQuery with an ordered list of Activity IDs and
          the values by which they will be ordered.
        - a Boolean indicating order values are numbers or not
        """
        order_key = request.params.get('order_by', None)
        if order_key is not None:
            # Ordering
            if order_key == 'timestamp':
                q = self.Session.query(
                    Mapped_Class.id,
                    Changeset.timestamp.label('value')
                ).\
                join(Changeset).\
                subquery()
                return q, False
            else:
                # Query to order number values (cast to Float)
                q_number = self.Session.query(
                    Mapped_Class.id,
                    cast(Value.value, Float).label('value')).\
                join(Tag_Group).\
                join(Tag, Tag.fk_tag_group == Tag_Group.id).\
                join(Value).\
                join(Key).\
                filter(Key.key.like(order_key))
                # Query to order string values
                q_text = self.Session.query(
                    Mapped_Class.id,
                    Value.value.label('value')).\
                join(Tag_Group).\
                join(Tag, Tag.fk_tag_group == Tag_Group.id).\
                join(Value).\
                join(Key).\
                filter(Key.key.like(order_key))

                # Try to query numbered values and cast them
                try:
                    x = q_number.all()
                    return q_number.subquery(), True
                except:
                    # Rolling back of Session is needed to completely erase error thrown above
                    self.Session.rollback()
                    return q_text.subquery(), False
        else:
            # No ordering, use dummy value
            q_no_order = self.Session.query(
                    Mapped_Class.id,
                    func.char_length('').label('value') # Dummy value
                )
            return q_no_order.subquery(), None

        return None, None

    def _get_sh_role_filter(self, request):
        """
        Returns the filter for Stakeholder_Role(s) if set
        """

        sh_role = request.params.get('sh_role', None)
        if sh_role is not None:
            roles = sh_role.split(',')
            filters = []
            for r in roles:
                filters.append(Stakeholder_Role.name.like(r))
            return filters

        return None

    def _get_user_filter(self, request, Mapped_Class, Changeset_Class):
        """

        """

        username = request.params.get('user', None)
        if username is not None:
            return self.Session.query(Mapped_Class.id).\
                join(Changeset_Class).\
                join(User).\
                filter(User.username == username).\
                subquery()

        return None

    def _get_return_stakeholders(self, request):
        ret = request.params.get('return_sh', None)
        if ret is not None and ret.lower() == 'true':
            return True
        return False

    def _get_return_activities(self, request):
        ret = request.params.get('return_a', None)
        if ret is not None and ret.lower() == 'true':
            return True
        return False

    def _get_sh_id(self, request):
        return request.params.get('sh_id', None)

    def _get_a_id(self, request):
        return request.params.get('a_id', None)

    def _get_attrs(self, request):
        """
        Return a list of attributes if set.

        So far, only special parameter 'all' is supported, returns True
        """

        attrs = request.params.get('attrs', None)
        if attrs is not None:
            if attrs == 'all':
                return True

        return None

    def _check_moderator(self, request):
        """
        Return True if currently logged in user has moderator privileges
        (permission = 'moderate'), else False.
        """

        if unauthenticated_userid(request) is None:
            return False

        moderator_rights = self.Session.query(Permission).\
            join(Permission.groups).\
            join(Group.users).\
            filter(User.username == unauthenticated_userid(request)).\
            filter(Permission.name == 'moderate').\
            all()
        if len(moderator_rights) > 0:
            return True

        return False

    def _add_review(self, request, item, mappedClass, user,
        implicit = False):
        """
        Add a review decision
        item: {Database object} (Activity or Stakeholder)
        mappedClass: database_model object
        user: {Database object}
        implicit: {Boolean} To prevent circular reviewing when handling
        involvements
        """

        _ = request.translate

        reviewed_involvements = []
        json_diff = None

        # Hard coded list of statii as in database. Needs to be in same order!
        # Not very nice but efficient and more comprehensible than just using
        # the indices.
        statusArray = [
            'pending',
            'active',
            'inactive',
            'deleted',
            'rejected',
            'edited'
        ]

        ret = {'success': False}

        # Activity or Stakeholder?
        diff_keyword = None
        if mappedClass == Activity:
            diff_keyword = 'activities'
            other_diff_keyword = 'stakeholders'
            otherMappedClass = Stakeholder
        elif mappedClass == Stakeholder:
            diff_keyword = 'stakeholders'
            other_diff_keyword = 'activities'
            otherMappedClass = Activity
        else:
            ret['msg'] = _('Unknown object to review.')
            return ret

        # Collect POST values
        review_decision = request.POST['review_decision']
        if review_decision is None:
            ret['msg'] = _('Review decision not provided.')
            return ret
        try:
            review_decision = int(review_decision)
        except:
            ret['msg'] = _('Unknown review decision')
            return ret
        review_comment = None
        if (request.POST['comment_textarea'] != ''):
            review_comment = request.POST['comment_textarea']

        # TODO: Also delegate involvement review if rejected (review_decision == 2)


        # Try to also review any affected involvement.
        if implicit is False:

            # Query the diff
            diff_query = self.Session.query(
                    Changeset.diff
                ).\
                join(mappedClass).\
                filter(mappedClass.identifier == item.identifier).\
                filter(mappedClass.version == item.version).\
                first()
            json_diff = json.loads(diff_query.diff)

            # Loop through the diff to find and collect all the affected
            # Stakeholders and their version at the time of the changes
            affected_involvements = []
            if mappedClass == Activity and 'activities' in json_diff:
                for a_diff in json_diff['activities']:
                    if ('id' in a_diff and a_diff['id'] == str(item.identifier)
                        and 'stakeholders' in a_diff):
                        for sh_diff in a_diff['stakeholders']:
                            version = (sh_diff['version']
                                    if 'version' in sh_diff
                                    else None)
                            affected_involvements.append({
                                'identifier': sh_diff['id'],
                                'version': version,
                                'op': sh_diff['op']
                            })
            elif mappedClass == Stakeholder and 'activities' in json_diff:
                for a_diff in json_diff['activities']:
                    if 'id' in a_diff and 'stakeholders' in a_diff:
                        version = (a_diff['version'] if 'version' in a_diff else None)
                        for sh_diff in a_diff['stakeholders']:
                            if 'id' in sh_diff and sh_diff['id'] == str(item.identifier):
                                affected_involvements.append({
                                    'identifier': a_diff['id'],
                                    'version': version,
                                    'op': sh_diff['op']
                                })

            log.debug('%s affected involvements found: %s'
                % (len(affected_involvements), affected_involvements))

            basereview = BaseReview(request)

            if review_decision == 1 or mappedClass == Stakeholder:
                # Approved. Normally check reviewable only for approval.
                # Exception for Stakeholders: Activiites through involvements
                # can always only be reviewed from Activity side.

                # First check if a review can be done for all the involvements
                reviewPossible = True
                for ai in affected_involvements:
                    reviewable = basereview._review_check_involvement(
                            otherMappedClass, ai['identifier'], ai['version']
                        )
                    if reviewPossible is True and reviewable > 0:
                        continue
                    reviewPossible = reviewable

                if reviewPossible is not True:
                    if reviewPossible == -2:
                        ret['msg'] = _('At least one of the involved Stakeholders cannot be reviewed. Click on the icon next to the involvement for further details.')
                    elif reviewPossible == -3:
                        ret['msg'] = _('At least one of the involved Activities cannot be reviewed. Click on the icon next to the involvement for further details.')
                    return ret

            # Do a review for all the involvements
            for ai in affected_involvements:

                # Query the Stakeholder version that was created by the
                # involvement
                if ai['op'] == 'add':
                    # If a new involvement was added, it is possible to find the
                    # exact version through the involvement.
                    sh = self.Session.query(
                            Stakeholder
                        ).\
                        join(Involvement).\
                        join(Activity).\
                        filter(Stakeholder.identifier == ai['identifier']).\
                        filter(Stakeholder.previous_version == ai['version']).\
                        filter(Activity.identifier == item.identifier).\
                        filter(Activity.version == item.version).\
                        first()
                elif ai['op'] == 'delete':
                    # If an involvement was deleted, it is obviously not
                    # possible to find the version through the involvement.
                    # Instead, we must try to find it through its identifier and
                    # version ...
                    # TODO: Is this enough to find the version or do we need
                    # additional indicators (changeset.diff?)
                    sh = self.Session.query(
                            Stakeholder
                        ).\
                        filter(Stakeholder.identifier == ai['identifier']).\
                        filter(Stakeholder.previous_version == ai['version']).\
                        first()

                if sh is None:
                    ret['msg'] = _('One of the Stakeholders to review was not found.')
                    return ret

                log.debug('Reviewing involvement: Stakeholder with identifier %s, version %s and status %s'
                        % (sh.identifier, sh.version, sh.fk_status))

                # Do a review, but implicitely
                reviewed_inv = self._add_review(
                    request,
                    sh,
                    Stakeholder,
                    user,
                    implicit = True
                )

                reviewed_involvements.append(reviewed_inv)

        # Do the actual review of the current item
        if review_decision == 1:
            # Approved

            # Check if Item was deleted (no more tags)
            empty_item = True
            for tg in item.tag_groups:
                for t in tg.tags:
                    empty_item = False
                    break

            # Query the previous version of the item
            previous_version = self.Session.query(
                    mappedClass
                ).\
                filter(mappedClass.identifier == item.identifier).\
                filter(mappedClass.version == item.previous_version).\
                first()

            # Query the active version of the item (review always happens
            # against the active version)
            ref_version = self.Session.query(
                    mappedClass
                ).\
                filter(mappedClass.identifier == item.identifier).\
                filter(mappedClass.fk_status == statusArray.index('active')+1).\
                first()

            if (empty_item is True or previous_version is None
                or previous_version.fk_status == statusArray.index('active')+1):
                # There is no previous version (the item is brand new) or it is
                # based directly on the active version.

                # If there is a previous active version, set it to 'inactive'
                if previous_version:
                    previous_version.fk_status = statusArray.index('inactive')+1

                if empty_item is True:
                    # Set the status of the item to 'deleted'
                    item.fk_status = statusArray.index('deleted') + 1

                    log.debug('Set version %s of %s with identifier %s to "deleted"'
                        % (item.version, mappedClass.__table__.name, item.identifier))

                else:
                    # Set the status of the item to 'active'
                    item.fk_status = statusArray.index('active')+1

                    log.debug('Set version %s of %s with identifier %s to "active"'
                        % (item.version, mappedClass.__table__.name, item.identifier))

            elif ref_version is None and mappedClass == Stakeholder:
                # For stakeholders, editing a pending version not always sets
                # the older version to 'edited'. This can lead to the situation
                # that the version to accept is based on another version.
                # Normally, this version should be recalculated but there exists
                # no active version yet.
                # In this case just set the version to review to 'active'.

                if empty_item is True:
                    # Set the status of the item to 'deleted'
                    item.fk_status = statusArray.index('deleted') + 1

                    log.debug('Set version %s of %s with identifier %s to "deleted"'
                        % (item.version, mappedClass.__table__.name, item.identifier))

                else:
                    # Set the status of the item to 'active'
                    item.fk_status = statusArray.index('active')+1

                    log.debug('Set version %s of %s with identifier %s to "active"'
                        % (item.version, mappedClass.__table__.name, item.identifier))

            else:
                # Recalculation of the item is needed.

                if ref_version is None:
                    ret['msg'] = _('No active version was found to base the review upon. Try to review an earlier version first.')
                    return ret

                # Query the diff. If it is already available (queried while
                # handling involvements earlier), no need to query it again
                if json_diff is None:
                    # Query the diff
                    diff_query = self.Session.query(
                            Changeset.diff
                        ).\
                        join(mappedClass).\
                        filter(mappedClass.identifier == item.identifier).\
                        filter(mappedClass.version == item.version).\
                        first()
                    json_diff = json.loads(diff_query.diff.replace('\'', '"'))

                # Cut to the part of the diff which is relevant for this item
                relevant_diff = None
                if (diff_keyword in json_diff and
                    json_diff[diff_keyword] is not None):
                    for diff in json_diff[diff_keyword]:
                        if 'id' in diff and diff['id'] == str(item.identifier):
                            relevant_diff = diff

                if relevant_diff is None:
                    ret['msg'] = _('The diff seems to be incorrect (identifier not found)')
                    return ret

                # Set the reference version to 'inactive'
                ref_version.fk_status = statusArray.index('inactive')+1

                # Set the pending version to 'edited'
                item.fk_status = statusArray.index('edited')+1

                # Prepare a changeset
                changeset = Changeset()
                changeset.user = request.user
                # TODO: could/should this just be the relevant_diff?
                changeset.diff = str(self._convert_utf8(json_diff))

                # Create a new version of the object
                new_version, ret_diff = self._update_object(
                    request, ref_version, relevant_diff, changeset,
                    status='active'
                )

                #TODO: handle returned diff correctly

                if len(reviewed_involvements) > 0:
                    # Attach the involvements which were reviewed earlier
                    inv_diff = (relevant_diff[other_diff_keyword]
                        if other_diff_keyword in relevant_diff
                        else None)
                    for inv in reviewed_involvements:
                        self._handle_involvements(
                            request,
                            ref_version,
                            new_version,
                            inv_diff,
                            changeset,
                            implicit = True,
                            db_object = inv
                        )

                log.debug('Created new version out of version %s of %s with identifier %s'
                        % (item.version, mappedClass.__table__.name, item.identifier))

        elif review_decision == 2:
            # Rejected: Do not modify previous version and set new version to
            # 'rejected'
            item.fk_status = statusArray.index('rejected') + 1

        else:
            ret['msg'] = _('Unknown review decision')
            return ret

        # Add review stuff
        item.user_review = user
        item.timestamp_review = datetime.datetime.now()
        item.comment_review = review_comment

        if implicit is True:
            return item

        ret['success'] = True
        ret['msg'] = _('Review successful.')
        return ret

    def _apply_diff(self, request, mappedClass, uid, version, diff, item, db):

        """
        item is either a db item or an activity feature
        diff: a diff concerning only a certain Activity or Stakeholder
        db: boolean
        """

#        print "============================================="
#        log.debug("diff:\n%s" % diff)

        if mappedClass == Activity:
            Db_Tag_Group = A_Tag_Group
            Db_Tag = A_Tag
            Db_Key = A_Key
            Db_Value = A_Value
        elif mappedClass == Stakeholder:
            Db_Tag_Group = SH_Tag_Group
            Db_Tag = SH_Tag
            Db_Key = SH_Key
            Db_Value = SH_Value
        else:
            return None


        if db is False:
            from lmkp.views.protocol import Tag
            from lmkp.views.protocol import TagGroup

            # Reset taggroups
            item._taggroups = []


        # Loop the tag groups from the previous version to check if they were
        # modified
        db_taggroup_query = self.Session.query(
                Db_Tag_Group
            ).\
            join(mappedClass).\
            filter(mappedClass.identifier == uid).\
            filter(mappedClass.version == version).\
            all()

        # Collect all tg_ids while we are at it
        tg_ids = []
        for db_taggroup in db_taggroup_query:

            # Remember if the main tag of a taggroup was deleted. In this case
            # we will set it again at the end
            maintag_deleted = False

            tg_ids.append(db_taggroup.tg_id)

            #TODO: clean up! Also make sure it works for all cases
            #TODO: Handle translations correctly

#            print "---------------------------------------------"
#            log.debug(
#                "Currently looking at db_taggroup with tg_id: %s"
#                % db_taggroup.tg_id
#            )

            # Create a new tag group but don't add it yet to the new activity
            # version. Indicator (taggroupadded) is needed for database items
            # because the moment when to add a taggroup to database is a very
            # delicate thing in SQLAlchemy.
            taggroupadded = False
            if db is True:
                new_taggroup = Db_Tag_Group(db_taggroup.tg_id)
                if mappedClass == Activity:
                    # Copy the old geometry of the taggroup (even if 'none')
                    new_taggroup.geometry = db_taggroup.geometry
            else:
                new_taggroup = TagGroup(tg_id = db_taggroup.tg_id)

            # Step 1: Loop the existing tags
            for db_tag in db_taggroup.tags:

#                log.debug(
#                    "Currently looking at db_tag with key/value:\n%s | %s" %
#                    (db_tag.key.key, db_tag.value.value)
#                )

                # Before copying the tag, make sure that it is not to delete
                copy_tag = True
                if diff is not None and 'taggroups' in diff:
                    for taggroup_dict in diff['taggroups']:
                        if ('tg_id' in taggroup_dict and
                            taggroup_dict['tg_id'] == db_taggroup.tg_id):

                            # Overwrite the geometry of the taggroup if it is
                            # set
                            if ('geometry' in taggroup_dict
                                and mappedClass == Activity and db is True):
                                tg_geom_diff = taggroup_dict['geometry']
                                if tg_geom_diff == {}:
                                    # Empty geometry: Set it to 'none'
                                    new_taggroup.geometry = None
                                else:
                                    tg_geom = geojson.loads(json.dumps(tg_geom_diff),
                                        object_hook = geojson.GeoJSON.to_instance)
                                    try:
                                        # Make sure it is a valid type
                                        tg_shape = asShape(tg_geom)
                                        geometrytype = tg_shape.geom_type
                                    except:
                                        raise HTTPBadRequest(detail="Invalid geometry type of taggroup")
                                    # Store the geometry only if it is a polygon
                                    # or multipolygon
                                    if (geometrytype == 'Polygon'
                                        or geometrytype == 'MultiPolygon'):
                                        new_taggroup.geometry = tg_shape.wkt
                                    else:
                                        raise HTTPBadRequest(detail='Invalid geometry type of taggroup: Only Polygon or MultiPolygon is supported.')

                            # Check which tags we have to edit
                            for tag_dict in taggroup_dict['tags']:
                                # Make sure it is exactly this tag (same key)
                                # and it is to be deleted.
                                if (tag_dict['op'] == 'delete'
                                    and db_tag.key.key and tag_dict['key']
                                    and db_tag.key.key == tag_dict['key']):

#                                    log.debug(
#                                        "Tag is deleted (not copied) from taggroup."
#                                    )

                                    if db_taggroup.main_tag == db_tag:
                                        maintag_deleted = True

                                    copy_tag = False

                # Create and append the new tag only if requested
                if copy_tag:
                    # Get the key and value SQLAlchemy object
                    k = self.Session.query(Db_Key).get(db_tag.fk_key)
                    v = self.Session.query(Db_Value).get(db_tag.fk_value)

                    if db is True:
                        new_tag = Db_Tag()
                        new_taggroup.tags.append(new_tag)
                        new_tag.key = k
                        new_tag.value = v
                    else:
                        new_tag = Tag(db_tag.id, k.key, v.value)
                        new_taggroup.add_tag(new_tag)

#                    log.debug(
#                        "Tag was copied and added to taggroup."
#                    )

                    # Set the main tag
                    if db_taggroup.main_tag == db_tag:
                        if db is True:
                            new_taggroup.main_tag = new_tag
                        else:
                            new_taggroup._main_tag = new_tag

                    if taggroupadded is False:
                        # It is necessary to add taggroup to database
                        # immediately, otherwise SQLAlchemy tries to do this the
                        # next time a tag is created and throws an error because
                        # of assumingly null values
                        if db is True:
                            item.tag_groups.append(new_taggroup)
                        else:
                            if len(new_taggroup.get_tags()) > 0:
                                item.add_taggroup(new_taggroup)

#                        log.debug(
#                            "Taggroup was added (copied) to item."
#                        )

                        taggroupadded = True

            # Step 2: Add new tags (who don't have an ID yet) to this taggroup
            if diff is not None and 'taggroups' in diff:
                for taggroup_dict in diff['taggroups']:
                    if ('tg_id' in taggroup_dict and
                        taggroup_dict['tg_id'] == db_taggroup.tg_id):
                        # Taggroup of dict is already in DB
                        for tag_dict in taggroup_dict['tags']:
                            if 'id' not in tag_dict and tag_dict['op'] == 'add':
                                if db is True:
                                    new_tag = self._create_tag(
                                        request, new_taggroup.tags,
                                        tag_dict['key'], tag_dict['value'],
                                        Db_Tag, Db_Key, Db_Value
                                    )
                                else:
                                    new_tag = Tag(
                                        None, tag_dict['key'], tag_dict['value']
                                    )
                                    new_taggroup.add_tag(new_tag)

#                                log.debug(
#                                    "Tag (%s | %s) was created and added to taggroup."
#                                    % (tag_dict['key'], tag_dict['value'])
#                                )

                                # Set the main tag
                                if 'main_tag' in taggroup_dict:
                                    if (db is True and
                                        taggroup_dict['main_tag']['key'] ==
                                            new_tag.key.key and
                                        taggroup_dict['main_tag']['value'] ==
                                            new_tag.value.value):
                                        new_taggroup.main_tag = new_tag
                                    elif (db is False and
                                        taggroup_dict['main_tag']['key'] ==
                                            new_tag.get_key() and
                                        taggroup_dict['main_tag']['value'] ==
                                            new_tag.get_value()):
                                        new_taggroup._main_tag = new_tag

                            # If taggroups were not added to database yet, then
                            # do it now. But only add new tag groups to the new
                            # version if they have any tags in them (which is
                            # not the case if they were deleted).
                            if (db is True and len(new_taggroup.tags) > 0
                                and taggroupadded is False):
                                item.tag_groups.append(new_taggroup)
                            elif (db is False
                                and len(new_taggroup.get_tags()) > 0
                                and taggroupadded is False):
                                item.add_taggroup(new_taggroup)

            # If the main tag was deleted and no new one was set, we will simply
            # use the first tag as a new main tag.
            if (maintag_deleted is True and new_taggroup.main_tag is None
                and len(new_taggroup.tags) > 0):
                new_taggroup.main_tag = new_taggroup.tags[0]


        # Finally new tag groups (without id) need to be added
        # (and loop all again)
        if diff is not None and 'taggroups' in diff:

            for taggroup_dict in diff['taggroups']:

                tg_id = None

                if ('tg_id' in taggroup_dict and
                    taggroup_dict['tg_id'] not in tg_ids and
                    ('op' not in taggroup_dict or
                    ('op' in taggroup_dict
                    and taggroup_dict['op'] != 'delete'))):
                    # Taggroup of dict has a tg_id, but does not yet exist for
                    # the current version. It can be treated as if new but with
                    # an existing tg_id
                    tg_id = taggroup_dict['tg_id']

#                    print "---------------------------------------------"
#                    log.debug(
#                        "Currently looking at a taggroup with tg_id %s which does not yet exist for the old version"
#                        % (tg_id)
#                    )

                if (('tg_id' not in taggroup_dict
                    or ('tg_id' in taggroup_dict and
                    taggroup_dict['tg_id'] is None))
                    and taggroup_dict['op'] == 'add'):
                    # Taggroup of dict has no tg_id and does not yet exist at
                    # all for the current item.

                    # Find next empty tg_id (over all versions)
                    tg_id_q = self.Session.query(func.max(Db_Tag_Group.tg_id)).\
                        join(mappedClass).\
                        filter(mappedClass.identifier
                               == uid).\
                        first()
                    tg_id = tg_id_q[0] + 1

#                    print "---------------------------------------------"
#                    log.debug(
#                        "Currently looking at a brand new taggroup with tg_id %s"
#                        % (tg_id)
#                    )

                if (tg_id is not None):

                    if db is True:
                        new_taggroup = Db_Tag_Group(tg_id)
                        item.tag_groups.append(new_taggroup)
                    else:
                        new_taggroup = TagGroup(tg_id = tg_id)
                        item.add_taggroup(new_taggroup)
                    for tag_dict in taggroup_dict['tags']:

                        if 'id' not in tag_dict and tag_dict['op'] == 'add':

                            if db is True:
                                new_tag = self._create_tag(
                                    request, new_taggroup.tags, tag_dict['key'],
                                    tag_dict['value'], Db_Tag, Db_Key, Db_Value
                                )
                            else:
                                new_tag = Tag(
                                    None, tag_dict['key'], tag_dict['value']
                                )
                                new_taggroup.add_tag(new_tag)

#                            log.debug(
#                                "Tag (%s | %s) was created and added to taggroup."
#                                % (tag_dict['key'], tag_dict['value'])
#                            )

                            # Set the main tag
                            if 'main_tag' in taggroup_dict:
                                if (db is True and
                                    taggroup_dict['main_tag']['key'] ==
                                        new_tag.key.key and
                                    taggroup_dict['main_tag']['value'] ==
                                        new_tag.value.value):
                                    new_taggroup.main_tag = new_tag
                                elif (db is False and
                                    taggroup_dict['main_tag']['key'] ==
                                        new_tag.get_key() and
                                    taggroup_dict['main_tag']['value'] ==
                                        new_tag.get_value()):
                                    new_taggroup._main_tag = new_tag

#        print "============================================="

        return item


    def recalculate_diffs(self, request, mappedClass, uid, old_version,
        new_diff, old_diff):
        """
        request: The request
        uid: The identifier of the object
        old_version: The old version of the object
        new_diff: A diff containing only the part which is relevant to the
          object:
          {
            'taggroups': [],
            'version': '',
            ...
          }
        old_diff: A whole changeset diff:
          {
            'activities': []
          }
          or
          {
            'stakeholders': []
          }
        """

        def _merge_involvements(old_diff, new_inv):
            """
            Helper function to merge a new involvement diff (new_inv) into an
            existing diff of an Activity.
            """

            if 'stakeholders' in old_diff:
                # Loop the involvements of the old diff to find if some of the
                # changes to the new diff are made to involvements already
                # modified by the old diff
                new_involvements_processed = False
                for old_inv in old_diff['stakeholders']:

                    if ('id' in old_inv and 'id' in new_inv
                        and old_inv['id'] == new_inv['id']):

                        # TODO: Is this simple replacement enough?
                        if new_inv['op'] == 'delete' and old_inv['op'] == 'add':
                            # Replace
                            old_inv = new_inv

#                            log.debug('Replaced old involvement (%s) with new involvement (%s)' % (old_inv, new_inv))

                            new_involvements_processed = True


                if new_involvements_processed is False:
                    # New involvements did not affect any of the already
                    # modified involvements. It is assumed that it is brand new
                    # and is added to the existing diff
                    if 'stakeholders' in old_diff:
                        old_diff['stakeholders'].append(new_inv)
                    else:
                        old_diff['stakeholders'] = new_inv

            else:
                # If no involvements in old_diff, add the one from the new_inv
                # as it is
                old_diff['stakeholders'] = new_inv

#                log.debug('Added new involvement diff: %s' % new_inv)

            return old_diff

        def _merge_taggroups(old_diff, new_tg):
            """
            Helper function to merge a new taggroup diff (new_tg) into an
            existing diff of an Activity or a Stakeholder.
            """

            if 'taggroups' in old_diff:
                # Loop the taggroups of the old diff to find if some of the
                # changes of the new diff are made to taggroups already modified
                # by the old diff
                new_taggroup_processed = False
                for old_tg in old_diff['taggroups']:
                    if ('tg_id' in old_tg and 'tg_id' in new_tg
                        and old_tg['tg_id'] == new_tg['tg_id']):
                        # An existing taggroup diff has further changes

#                        log.debug('Merging diff of taggroups. Old taggroup diff:\n%s\nNew taggroup diff:\n%s'
#                            % (old_tg, new_tg))

                        tags_to_delete = []
                        tags_to_add = []

                        for old_t in old_tg['tags']:
                            # Loop through the tags of the old diff

                            for new_t in new_tg['tags']:
                                # Loop through the tags of the new diff

                                # If there is a tag previously added (old_t['op'] == 'add') and now to be deleted again (new_t['op'] == 'delete'), then remove it
                                if (new_t['op'] == 'delete'
                                    and old_t['op'] == 'add'
                                    and new_t['key'] == old_t['key']
                                    and str(new_t['value'])
                                        == str(old_t['value'])):
                                    # Remove
                                    tags_to_delete.append(old_t)

                                else:
                                    # Add new diff
                                    tags_to_add.append(new_t)

                        for tdt in tags_to_delete:
                            old_tg['tags'].remove(tdt)

#                            log.debug('Removed old tag diff: %s' % tdt)

                        for tda in tags_to_add:
                            old_tg['tags'].append(tda)

#                            log.debug('Added new tag diff: %s' % tda)

                        new_taggroup_processed = True

                if new_taggroup_processed is False or 'tg_id' not in new_tg:
                    # New taggroup did not affect any of the already modified
                    # taggroups or it has no tg_id. It is therefore assumed that
                    # it is brand new and is added to the old diff.
                    if 'taggroups' in old_diff:
                        old_diff['taggroups'].append(new_tg)
                    else:
                        old_diff['taggroups'] = [new_tg]

            else:
                # If no taggroups yet in old_diff, add the one from the new_tg
                # as it is
                old_diff['taggroups'] = [new_tg]

#                log.debug('Added new taggroup diff: %s' % new_tg)

            return old_diff

        # Activity or Stakeholder?
        if mappedClass == Activity:
            diff_keyword = 'activities'
        elif mappedClass == Stakeholder:
            diff_keyword = 'stakeholders'
        else:
            return None

        rel_diff = None
        # Cut down old_diff to find the interesting stuff
        if diff_keyword in old_diff and old_diff[diff_keyword] is not None:
            for diff in old_diff[diff_keyword]:
                if 'id' in diff and diff['id'] == str(uid):
                    rel_diff = diff

        if rel_diff is None:
            return None

        log.debug('Diff before recalculation:\n%s' % rel_diff)

        # The tg_id's are needed to make a meaningful merge of the diffs. If
        # they are not known (eg. when looking at the diff of the very first
        # version, try to add them by looking them up in the database.
        if 'taggroups' in rel_diff:
            feature = None
            for rel_tg in rel_diff['taggroups']:
                if 'tg_id' not in rel_tg:

                    if feature is None:
                        # Query the feature
                        # TODO: Does this still work in different languages?
                        feature = self.read_one_by_version(request, uid,
                            old_version)

                    # Try to find the tg_id of the rel_tg. All the tags of
                    # rel_tg need to be found in the same taggroup of the
                    # feature
                    rel_tags = {}
                    rel_keys = []
                    # Have a look at each tag in rel_tg
                    for rel_t in rel_tg['tags']:
                        rel_tags[rel_t['key']] = rel_t['value']
                        rel_keys.append(rel_t['key'])
                    found_tg_id = None
                    for f_tg in feature.get_taggroups():
                        if found_tg_id is None:
                            f_tags = {}
                            for f_t in f_tg.get_tags():
                                f_tags[f_t.get_key()] = f_t.get_value()
                            if list(set(rel_tags) & set(f_tags)) == rel_keys:
                                found_tg_id = f_tg.get_tg_id()
                    if found_tg_id is not None:
                        rel_tg['tg_id'] = found_tg_id

        # Merge taggroups
        if 'taggroups' in new_diff:

#            log.debug('Diff before doing taggroup merges:\n%s' % rel_diff)

            for new_tg in new_diff['taggroups']:
                rel_diff = _merge_taggroups(rel_diff, new_tg)

#            log.debug('Diff after doing taggroup merges:\n%s' % rel_diff)

        # Merge involvements (only for Stakeholders)
        if mappedClass == Activity and 'stakeholders' in new_diff:

#            log.debug('Diff before doing involvement merges:\n%s' % rel_diff)

            for new_inv in new_diff['stakeholders']:
                rel_diff = _merge_involvements(rel_diff, new_inv)

#            log.debug('Diff after doing involvement merges:\n%s' % rel_diff)

        log.debug('Diff after recalculation:\n%s' % rel_diff)

        return rel_diff

    def _key_value_is_valid(self, request, itemType, key, value):
        """
        Validate if key and value are in the current configuration
        """

        if itemType is None or itemType not in ['activities', 'stakeholders']:
            return False

        if self.categoryList is None:

#            log.debug('Created a new ConfigCategoryList object of type %s' % itemType)
            
            # TODO: language parameter
            pass
#            self.categoryList = getCategoryList(request, itemType, lang=None)

        # Trim white spaces
        try:
            value = value.strip()
        except AttributeError:
            pass

        # TODO: Make use of this! Delete the rest below.
        # TODO: Also delete imports above
#        return self.categoryList.checkValidKeyValue(key, value)


        if itemType == 'activities':
            filename = ACTIVITY_YAML
        elif itemType == 'stakeholders':
            filename = STAKEHOLDER_YAML

        # Read the global configuration file
        global_stream = open("%s/%s" % (profile_directory_path(request), filename), 'r')
        configuration = yaml.load(global_stream)

        # Read the localized configuration file
        try:
            locale_stream = open("%s/%s" % (locale_profile_directory_path(request), filename), 'r')
            locale_config = yaml.load(locale_stream)

            # If there is a localized config file then merge it with the global one
            configuration = merge_profiles(configuration, locale_config)

        except IOError:
            # No localized configuration file found!
            pass

        # Per default key and value are not valid
        key_is_valid = False
        value_is_valid = False

        # Loop the optional and mandatory fields
        for fields in configuration['fields']:

            # Loop all tags in fields
            for tags in configuration['fields'][fields].iteritems():
                # If the current key equals the key in the tag, set key_is_valid
                # to True
                if key == tags[0]:
                    key_is_valid = True
                    # Check the value in the next step:
                    # If the current key contains predefined values, check the
                    # value against these
                    if 'predefined' in tags[1]:
                        if value in tags[1]['predefined']:
                            value_is_valid = True
                    # In other cases (non-predefined values), set value_is_valid
                    # to True
                    else:
                        value_is_valid = True

        # Return only True if key as well as value are valid
        return key_is_valid and value_is_valid

    def _create_tag(self, request, parent, key, value, Tag_Item, Key_Item,
        Value_Item):
        """
        Creates a new SQLAlchemy tag object and appends it to the parent list.
        """

        # Activity or Stakeholder?
        itemType = None
        if Tag_Item == A_Tag:
            itemType = 'activities'
        elif Tag_Item == SH_Tag:
            itemType = 'stakeholders'

        # Validate the key and value pair with the configuration file
        if not self._key_value_is_valid(request, itemType, key, value):
            self.Session.rollback()
            raise HTTPBadRequest("Key: %s or Value: %s is not valid." %
                (key, value))

        # The key has to be already in the database. The key is supposed to be
        # always in English.
        k = self.Session.query(
                Key_Item
            ).\
            filter(Key_Item.key == key).\
            filter(Key_Item.fk_language == 1).\
            first()

        # If the value is not yet in the database, create a new value
        v = self.Session.query(Value_Item).\
            filter(Value_Item.value == unicode(value)).\
            filter(Value_Item.fk_language == 1).\
            first()
        if v is None:

            try:
                # For number values, set language 'English'
                float(value)
                lang_fk = 1
            except:
                # Add the currently set language to the key (fallback: English)
                localizer = get_localizer(request)
                language = self.Session.query(
                        Language
                    ).\
                    filter(Language.locale == localizer.locale_name).\
                    first()
                lang_fk = language.id if language is not None else 1

            # FILES!
            # Check if the files need to be moved (from temporary directory) or
            # renamed
            if key == 'Files':
                check_file_location_name(request, value)

            v = Value_Item(value=value)
            v.fk_language = lang_fk

        # Create a new tag with key and value and append it to the parent TG
        t = Tag_Item()
        parent.append(t)
        t.key = k
        t.value = v

        # Return the newly created tag
        return t

    def _convert_utf8(self, data):
        """
        Converts python unicode strings so they can be stored in the database
        without the u'
        http://stackoverflow.com/questions/1254454
        """
        if isinstance(data, unicode):
            return data.encode('utf-8')
        elif isinstance(data, collections.Mapping):
            return dict(map(self._convert_utf8, data.iteritems()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(self._convert_utf8, data))
        else:
            return data

class Tag(object):

    def __init__(self, id, key, value):
        self._id = id
        self._key = key
        self._value = value

    def get_key(self):
        return self._key

    def get_value(self):
        return self._value

    def get_id(self):
        return self._id

    def to_table(self):
        return {'id': self._id, 'key': self._key, 'value': self._value}

class TagGroup(object):

    def __init__(self, id=None, tg_id=None, main_tag_id=None):
        """
        Create a new TagGroup object with id and the main_tag_id
        """

        # The TagGroup id
        self._id = id
        # The id of the main tag (not the tag itself!)
        self._main_tag_id = main_tag_id
        self._tg_id = tg_id
        # List to store the tags
        self._tags = []
        self._diffFlag = None
        # Geometry (only used for Activity TagGroups)
        self._geometry = None

    def add_tag(self, tag):
        """
        Add a new tag to the internal tag list
        """
        self._tags.append(tag)

    def remove_tag(self, tag):
        if tag in self._tags:
            self._tags.remove(tag)

    def get_id(self):
        return self._id

    def get_tg_id(self):
        return self._tg_id

    def get_maintag_id(self):
        return self._main_tag_id

    def get_tag_by_key(self, key):
        """
        Returns a tag from this group if there is one with the requested key,
        else None is returned.
        """
        for t in self._tags:
            if t.get_key() == key:
                return t
        return None

    def get_tag_by_id(self, id):
        for t in self._tags:
            if t.get_id() == id:
                return t
        return None

    def get_tags(self):
        return self._tags

    def setDiffFlag(self, bool):
        self._diffFlag = bool

    def getDiffFlag(self):
        return self._diffFlag

    def set_geometry(self, geometry):
        self._geometry = geometry

    def to_table(self):
        """
        Returns a JSON compatible representation of this object
        """
        main_tag = None
        tags = []
        for t in self._tags:
            tags.append(t.to_table())
            if t.get_id() == self._main_tag_id:
                main_tag = t.to_table()

        ret = {
            'id': self._id,
            'tg_id': self._tg_id,
            'main_tag': main_tag,
            'tags': tags
        }

        # Geometry
        if self._geometry is not None:
            try:
                geom = wkb.loads(str(self._geometry.geom_wkb))
                ret['geometry'] = asGeoJSON(geom)
            except:
                pass

        return ret

class Inv(object):

    def __init__(self, guid, feature, role, role_id, version, status_id):
        self._guid = guid
        self._feature = feature
        self._role = role
        self._role_id = role_id
        self._version = version
        self._status_id = status_id

    def get_guid(self):
        return self._guid

    def get_role(self):
        return self._role

    def get_role_id(self):
        return self._role_id

    def get_version(self):
        return self._version

    def get_status(self):
        return self._status_id

    def to_table(self, request):
        if self._feature is None:
            return {
                'id': str(self._guid),
                'role': self._role,
                'role_id': self._role_id,
                'version': self._version,
                'status_id': self._status_id
            }
        else:
            return {
                'data': self._feature.to_table(request),
                'role': self._role,
                'role_id': self._role_id,
                'version': self._version,
                'status_id': self._status_id
            }

class Feature(object):

    def __init__(self, guid, order_value, version=None, status=None,
        status_id=None, timestamp=None, diff_info=None, ** kwargs):
        self._taggroups = []
        self._involvements = []
        self._guid = guid
        self._order_value = order_value
        self._version = version
        self._timestamp = timestamp
        self._diff_info = diff_info
        self._status = status
        self._status_id = status_id
        self._pending = []
        self._missing_keys = None

        self._previous_version = kwargs.pop('previous_version', None)

        self._user_privacy = kwargs.pop('user_privacy', None)
        self._user_id = kwargs.pop('user_id', None)
        self._user_name = kwargs.pop('user_name', None)
        self._user_firstname = kwargs.pop('user_firstname', None)
        self._user_lastname = kwargs.pop('user_lastname', None)

        self._institution_id = kwargs.pop('institution_id', None)
        self._institution_name = kwargs.pop('institution_name', None)
        self._institution_url = kwargs.pop('institution_url', None)
        self._institution_logo = kwargs.pop('institution_logo', None)

    def add_taggroup(self, taggroup):
        """
        Adds a new tag group to the internal tag group list
        """
        self._taggroups.append(taggroup)

    def add_involvement(self, involvement):
        self._involvements.append(involvement)

    def remove_involvement(self, involvement):
        self._involvements.remove(involvement)

    def find_involvement_by_guid(self, guid):
        for i in self._involvements:
            if (str(i.get_guid()) == str(guid)):
                return i
        return None

    def find_involvement_by_role(self, guid, role):
        for i in self._involvements:
            if (str(i.get_guid()) == str(guid) and i.get_role() == role):
                return i
        return None

    def find_involvement(self, guid, role, version):
        for i in self._involvements:
            if (str(i.get_guid()) == str(guid) and i.get_role() == role and
                i.get_version() == version):
                return i
        return None

    def find_involvement_feature(self, guid, role):
        for i in self._involvements:
            if i._feature._guid == str(guid) and i.get_role() == role:
                return i
        return None

    def find_taggroup_by_id(self, id):
        for t in self._taggroups:
            if t.get_id() == id:
                return t
        return None

    def find_taggroup_by_tg_id(self, tg_id):
        for t in self._taggroups:
            if t.get_tg_id() == tg_id:
                return t
        return None

    def get_taggroups(self):
        return self._taggroups

    def get_involvements(self):
        return self._involvements

    def get_version(self):
        return self._version

    def get_status(self):
        return self._status

    def get_status_id(self):
        return self._status_id

    def get_guid(self):
        return self._guid

    def set_pending(self, pending):
        self._pending = pending

    def remove_taggroup(self, taggroup):
        if taggroup in self.get_taggroups():
            self.get_taggroups().remove(taggroup)

    def mark_complete(self, mandatory_keys):
        """
        Return a list of missing mandatory keys. Return [0] if item is to be
        deleted
        """

        # Make a copy of mandatory keys
        mk = mandatory_keys[:]

        for k in mandatory_keys:
            for tg in self.get_taggroups():
                if tg.get_tag_by_key(k) is not None:
                    mk.remove(k)
                    break

        # If all mandatory keys are still there, check if version is pending to
        # be deleted
        if len(mk) == len(mandatory_keys):
            if len(self.get_taggroups()) > 0:
                if len(self.get_taggroups()[0].get_tags()) > 0:
                    if (self.get_taggroups()[0].get_tags()[0].get_key() is None
                        and self.get_taggroups()[0].get_tags()[0].get_value() is None):
                        mk = [0]

        self._missing_keys = mk

    def to_table(self, request):
        """
        Returns a JSON compatible representation of this object
        """
        tg = []
        for t in self._taggroups:
            tg.append(t.to_table())

        geometry = None

        try:
            geom = wkb.loads(str(self._geometry.geom_wkb))
            geometry = {}
            geometry['type'] = 'Point'
            geometry['coordinates'] = [geom.x, geom.y]
        except AttributeError:
            pass

        ret = {'id': self._guid, 'taggroups': tg}

        if geometry is not None:
            ret['geometry'] = geometry

        if self._version is not None:
            ret['version'] = self._version
        if self._timestamp is not None:
            ret['timestamp'] = str(self._timestamp)
        if self._status is not None:
            ret['status'] = get_translated_status(request, self._status)
        if self._status_id is not None:
            ret['status_id'] = self._status_id
        if self._diff_info is not None:
            for k in self._diff_info:
                # Try to translate status
                if k == 'status':
                    ret[k] = get_translated_status(request, self._diff_info[k])
                else:
                    ret[k] = self._diff_info[k]
        if len(self._pending) != 0:
            pending = []
            for p in self._pending:
                pending.append(p.to_table(request))
            ret['pending'] = sorted(pending, key=lambda k: k['version'],
                reverse=True)
        if self._missing_keys is not None:
            ret['missing_keys'] = self._missing_keys

        # Involvements
        if len(self._involvements) != 0:
            sh = []
            for i in self._involvements:
                sh.append(i.to_table(request))
            ret['involvements'] = sh

        if self._previous_version is not None:
            ret['previous_version'] = self._previous_version

        # User details
        user = {}
        if self._user_id is not None:
            user['id'] = self._user_id
        if self._user_name is not None:
            user['username'] = self._user_name
        # User details based on privacy settings
        if self._user_privacy is not None and self._user_privacy > 0:
            if self._user_firstname is not None:
                user['firstname'] = self._user_firstname
            if self._user_lastname is not None:
                user['lastname'] = self._user_lastname
        if user != {}:
            ret['user'] = user

        # Institutions
        institution = {}
        if self._institution_id is not None:
            institution['id'] = self._institution_id
        if self._institution_name is not None:
            institution['name'] = self._institution_name
        if self._institution_url is not None:
            institution['url'] = self._institution_url
        if self._institution_logo is not None:
            institution['logo'] = self._institution_logo
        if institution != {}:
            ret['institution'] = institution

        return ret

    def create_diff(self, request, previous=None):
        """
        Append a diff object. Try to find TagGroups and Tags of current version
        in previous version.
        Also find new or removed Involvements.
        """

        if previous is not None:
            # Collect new TagGroups
            diff_new = []
            # Loop through TagGroups of current version
            for tg in self._taggroups:
                # Special case: Item was deleted, then the taggroup has only one empty tag: Do not mark this as new attribute.
                if (len(tg.get_tags()) == 1
                    and tg.get_tags()[0].get_key() is None
                    and tg.get_tags()[0].get_value() is None):
                    pass
                else:
                    # Indicator (None, False or TagGroup) to check if all Tags were found in the same TagGroup
                    foundinsametaggroup = None
                    # Loop through Tags of current version
                    for t in tg.get_tags():
                        # Indicator (True or False) to flag if a Tag was found in the previous version
                        newtag_found = False
                        # Variable to store the old TagGroup where a Tag was found
                        foundintaggroup = None
                        # Try to find the same Tag in previous version by looping through TagGroups of previous version
                        for tg_old in previous.get_taggroups():
                            # Only look at old TagGroups that were not yet found
                            if tg_old.getDiffFlag() is not True:
                                # Loop through Tags of previous version
                                for t_old in tg_old.get_tags():
                                    # Compare Key and Value of current and previous Tag
                                    if t.get_key() == t_old.get_key() \
                                        and t.get_value() == t_old.get_value():
                                        # Tag is found in previous version, set indicator and store TagGroup
                                        newtag_found = True
                                        foundintaggroup = tg_old
                                        break

                        # Tag was found in old Tags
                        if newtag_found is True:
                            # For the first tag of a TagGroup, store the old TagGroup
                            if foundinsametaggroup is None:
                                foundinsametaggroup = foundintaggroup
                            # Check if the found Tag is not in the same TagGroup as the others
                            elif foundintaggroup != foundinsametaggroup:
                                foundinsametaggroup = False
                        # Tag was not found after looping through all old Tags
                        else:
                            foundinsametaggroup = False

                    # All Tags were in the same TagGroup
                    if foundinsametaggroup is not False:
                        if foundinsametaggroup is not None:
                            # Mark old TagGroup as found
                            foundinsametaggroup.setDiffFlag(True)
                    # Else, TagGroup is new
                    else:
                        diff_new.append(tg.to_table())

            # Collect old TagGroups that are not there anymore
            diff_old = []
            for tg_old in previous.get_taggroups():
                if tg_old.getDiffFlag() is not True:
                    diff_old.append(tg_old.to_table())

            # Reset all TagGroups to compare with next version
            for tg in self._taggroups:
                tg.setDiffFlag(None)
            # Also reset TagGroups of previous version
            for tg in previous._taggroups:
                tg.setDiffFlag(None)

            # Collect new Involvements
            inv_new = []
            # Loop through Involvements of current version
            for invn in self._involvements:
                newinv_found = False
                for invo in previous._involvements:
                    if (invn.get_guid() == invo.get_guid() and
                        invn.get_role() == invo.get_role()):
                        newinv_found = True
                        break
                if newinv_found is not True:
                    inv_new.append(invn.to_table(request))

            # Collect old Involvements (not there anymore)
            inv_old = []
            # Loop through Involvements of previous version
            for invo in previous._involvements:
                oldinv_found = False
                for invn in self._involvements:
                    if (invo.get_guid() == invn.get_guid() and
                        invo.get_role() == invn.get_role()):
                            oldinv_found = True
                            break
                if oldinv_found is not True:
                    inv_old.append(invo.to_table(request))

            # Put it all together
            diff_object = {}
            if len(diff_new) > 0:
                diff_object['new_attr'] = diff_new
            if len(diff_old) > 0:
                diff_object['old_attr'] = diff_old
            if len(inv_old) > 0:
                diff_object['old_inv'] = inv_old
            if len(inv_new) > 0:
                diff_object['new_inv'] = inv_new

            # Only add diff object if not empty
            if diff_object != {}:
                self._diff_info['diff'] = diff_object

    def get_guid(self):
        return self._guid

    def get_order_value(self):
        return self._order_value

    def get_previous_version(self):
        return self._previous_version