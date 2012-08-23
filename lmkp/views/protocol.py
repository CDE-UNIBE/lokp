from lmkp.config import locale_profile_directory_path
from lmkp.config import profile_directory_path
from lmkp.models.database_objects import A_Key
from lmkp.models.database_objects import A_Tag
from lmkp.models.database_objects import A_Value
from lmkp.models.database_objects import Group
from lmkp.models.database_objects import Permission
from lmkp.models.database_objects import Review_Decision
from lmkp.models.database_objects import SH_Key
from lmkp.models.database_objects import SH_Tag
from lmkp.models.database_objects import SH_Value
from lmkp.models.database_objects import Stakeholder_Role
from lmkp.models.database_objects import Status
from lmkp.views.config import merge_profiles
from lmkp.models.database_objects import User
from shapely import wkb
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import between
from sqlalchemy.types import Float
import datetime
from sqlalchemy import func
import yaml
from pyramid.security import unauthenticated_userid

from lmkp.views.translation import statusMap

class Protocol(object):
    """
    A class that contains general methods for the activity protocol and the
    stakeholder protocol as well
    """

    def __init__(self):
        self.configuration = None
    
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

    def _get_status(self, request, from_history=False):
        """
        Returns an ClauseElement array of requested activity status.
        Default value is active.
        It is possible to request activities with different status using
        status=active,pending
        """

        statusParameter = request.params.get('status', None)

        try:
            status = statusParameter.split(',')
            # Hard coded list of possible activity statii. Not very nice ... But more
            # performant than requesting the database
            arr = []
            for s in status:
                if s in statusMap:
                    arr.append(Status.name == s)

            if len(arr) > 0:
                return arr
        except AttributeError:
            pass

        # Special case: request came from history, return None
        if from_history is True:
            return None

        return [Status.name == "active"]

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
        if ('a__queryable' in request.params or 
            'sh__queryable' in request.params):
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
                if prefix == 'a' and col in request.params['a__queryable']:
                    values = request.params[k].split(',')
                    for v in values:
                        q = self.Session.query(
                                A_Tag.fk_a_tag_group.label('a_filter_tg_id')
                            ).\
                            join(A_Key).\
                            join(A_Value).\
                            filter(A_Key.key == col).\
                            filter(__get_filter_expression(prefix, v, op))
                        a_filter_expr.append(q)
                # Second: Stakeholder attributes
                elif prefix == 'sh' and col in request.params['sh__queryable']:
                    values = request.params[k].split(',')
                    for v in values:
                        q = self.Session.query(
                                SH_Tag.fk_sh_tag_group.label('sh_filter_tg_id')
                            ).\
                            join(SH_Key).\
                            join(SH_Value).\
                            filter(SH_Key.key == col).\
                            filter(__get_filter_expression(prefix, v, op))
                        sh_filter_expr.append(q)
            
            # Do a union of all filter expressions and return it
            a_tag = (a_filter_expr[0].union(* a_filter_expr[1:]) 
                    if len(a_filter_expr) > 0 
                    else self.Session.query(
                        A_Tag.fk_a_tag_group.label("a_filter_tg_id")))
            
            sh_tag = (sh_filter_expr[0].union(* sh_filter_expr[1:]) 
                    if len(sh_filter_expr) > 0 
                    else self.Session.query(
                        SH_Tag.fk_sh_tag_group.label("sh_filter_tg_id")))
            
            return (a_tag.subquery(), len(a_filter_expr), 
                    sh_tag.subquery(), len(sh_filter_expr))

        # Default (no filtering)
        return (self.Session.query(
                    A_Tag.fk_a_tag_group.label("a_filter_tg_id")).subquery(), 
                len(a_filter_expr), 
                self.Session.query(
                    SH_Tag.fk_sh_tag_group.label("sh_filter_tg_id")).subquery(),
                len(sh_filter_expr))

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

    def _get_order(self, request, Mapped_Class, Tag_Group, Tag, Key, Value,
        Changeset):
        """
        Returns
        - a SubQuery with an ordered list of Activity IDs and
          the values by which they will be ordered.
        - a Boolean indicating order values are numbers or not
        """
        order_key = request.params.get('order_by', None)
        if order_key is not None:
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

    def _add_review(self, request, item, previous_item, Changeset_Item, Db_Item,
        user):
        """
        Add a review decision
        """

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
        # Same for review decisions
        reviewdecisionArray = [
            'approved',
            'rejected',
            'edited'
        ]

        ret = {'success': False}

        # Collect POST values
        review_decision = self.Session.query(Review_Decision).\
            get(request.POST['review_decision'])
        if review_decision is None:
            ret['msg'] = 'Review decision not provided or not found.'
            return ret

        review_comment = None
        if ('comment_checkbox' in request.POST and
            request.POST['comment_textarea'] != ''):
            review_comment = request.POST['comment_textarea']

        if review_decision.id == reviewdecisionArray.index('approved') + 1:
            # Approved
            if previous_item is not None:
                # Set previous version to 'inactive' if it was active before
                if previous_item.fk_status == statusArray.index('active') + 1:
                    previous_item.fk_status = statusArray.index('inactive') + 1
                # Set previous version to 'edited' if it was pending before
                elif previous_item.fk_status == statusArray.index('pending') + 1:
                    previous_item.fk_status = statusArray.index('edited') + 1

            # Check if Item was deleted (no more tags)
            empty_item = True
            for tg in item.tag_groups:
                for t in tg.tags:
                    empty_item = False
                    break

            if empty_item is True:
                # Set new version to 'deleted'
                item.fk_status = statusArray.index('deleted') + 1
            else:
                # Set new version to 'active'. But first make sure there is no
                # other one active by setting any with 'active' to 'inactive'
                self.Session.query(Db_Item).\
                    filter(Db_Item.identifier == item.identifier).\
                    filter(Db_Item.fk_status == statusArray.index('active')+1).\
                    update({Db_Item.fk_status: statusArray.index('inactive')+1})
                item.fk_status = statusArray.index('active') + 1

        elif review_decision.id == reviewdecisionArray.index('rejected') + 1:
            # Rejected: Do not modify previous version and set new version to
            # 'rejected'
            item.fk_status = statusArray.index('rejected') + 1

        elif review_decision.id == reviewdecisionArray.index('edited') + 1:
            # Edited: Do not modify previous version and set new version to
            # 'edited'
            item.fk_status = statusArray.index('edited') + 1

        # Add Changeset_Review
        changeset_review = Changeset_Item(review_comment)
        changeset_review.changeset = item.changesets[0]
        changeset_review.user = user
        changeset_review.review_decision = review_decision

        ret['success'] = True
        ret['msg'] = 'Review successful.'
        return ret

    def _key_value_is_valid(self, request, configuration, key, value):
        """
        Validate if key and value are in the current configuration
        """

        # Trim white spaces
        try:
            value = value.strip()
        except AttributeError:
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

    def _read_configuration(self, request, filename):

        # Read the global configuration file
        global_stream = open("%s/%s" % (profile_directory_path(request), filename), 'r')
        self.configuration = yaml.load(global_stream)

        # Read the localized configuration file
        try:
            locale_stream = open("%s/%s" % (locale_profile_directory_path(request), filename), 'r')
            locale_config = yaml.load(locale_stream)

            # If there is a localized config file then merge it with the global one
            self.configuration = merge_profiles(self.configuration, locale_config)

        except IOError:
            # No localized configuration file found!
            pass

        return self.configuration

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

    def __init__(self, id=None, main_tag_id=None):
        """
        Create a new TagGroup object with id and the main_tag_id
        """

        # The TagGroup id
        self._id = id
        # The id of the main tag (not the tag itself!)
        self._main_tag_id = main_tag_id
        # List to store the tags
        self._tags = []
        self._diffFlag = None

    def add_tag(self, tag):
        """
        Add a new tag to the internal tag list
        """
        self._tags.append(tag)

    def get_id(self):
        return self._id

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

        return {'id': self._id, 'main_tag': main_tag, 'tags': tags}

class Inv(object):

    def __init__(self, guid, feature, role):
        self._guid = guid
        self._feature = feature
        self._role = role

    def get_guid(self):
        return self._guid

    def get_role(self):
        return self._role

    def to_table(self):
        if self._feature is None:
            return {'id': str(self._guid), 'role': self._role}
        else:
            return {'data': self._feature.to_table(), 'role': self._role}

class Feature(object):

    def __init__(self, guid, order_value, version=None, status=None,
        timestamp=None, diff_info=None, ** kwargs):
        self._taggroups = []
        self._involvements = []
        self._guid = guid
        self._order_value = order_value
        self._version = version
        self._timestamp = timestamp
        self._diff_info = diff_info
        self._status = status
        self._pending = []
        self._missing_keys = None

    def add_taggroup(self, taggroup):
        """
        Adds a new tag group to the internal tag group list
        """
        self._taggroups.append(taggroup)

    def add_involvement(self, involvement):
        self._involvements.append(involvement)

    def find_involvement(self, guid, role):
        for i in self._involvements:
            if i.get_guid() == guid and i.get_role() == role:
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

    def get_taggroups(self):
        return self._taggroups

    def get_version(self):
        return self._version

    def get_status(self):
        return self._status

    def set_pending(self, pending):
        self._pending = pending

    def remove_taggroup(self, taggroup):
        if taggroup in self.get_taggroups():
            self.get_taggroups().remove(taggroup)

    def mark_complete(self, mandatory_keys):

        # Make a copy of mandatory keys
        mk = mandatory_keys[:]

        for k in mandatory_keys:
            for tg in self.get_taggroups():
                if tg.get_tag_by_key(k) is not None:
                    mk.remove(k)
                    break

        self._missing_keys = mk

    def to_table(self):
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
            ret['status'] = self._status
        if self._diff_info is not None:
            for k in self._diff_info:
                ret[k] = self._diff_info[k]
        if len(self._pending) != 0:
            pending = []
            for p in self._pending:
                pending.append(p.to_table())
            ret['pending'] = sorted(pending, key=lambda k: k['version'],
                reverse=True)
        if self._missing_keys is not None:
            ret['missing_keys'] = self._missing_keys

        # Involvements
        if len(self._involvements) != 0:
            sh = []
            for i in self._involvements:
                sh.append(i.to_table())
            ret['involvements'] = sh

        return ret

    def create_diff(self, previous=None):
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
                    inv_new.append(invn.to_table())

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
                    inv_old.append(invo.to_table())

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
        return self._diff_info['previous_version']