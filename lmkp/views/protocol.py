from geoalchemy import WKBSpatialElement
from geoalchemy.functions import functions
from shapely import wkb
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Float

class Protocol(object):
    """
    A class that contains general methods for the activity protocol and the
    stakeholder protocol as well
    """

    def __init__(self):
        pass

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

    def _get_status(self, request):
        """
        Returns the requested activity status, default value is active.
        """

        status = request.params.get('status', None)
        # Hard coded list of possible activity statii. Not very nice ... But more
        # performant than requesting the database
        if status in ["pending", "active", "overwritten", "deleted", "rejected"]:
            return status

        return "active"

    def _filter(self, request, Tag, Key, Value):
        """
        Returns
        - a SubQuery of Tags containing a union of all Key/Value pairs which fulfill
          the filter condition(s)
        - a count of the filters
        """

        def __get_filter_expression(value, op):

            # Use cast function provided by SQLAlchemy to convert
            # database values to Float.
            nbr_map = {
                'eq': cast(Value.value, Float) == value,
                'ne': cast(Value.value, Float) != value,
                'lt': cast(Value.value, Float) < value,
                'lte': cast(Value.value, Float) <= value,
                'gt': cast(Value.value, Float) > value,
                'gte': cast(Value.value, Float) >= value
            }

            str_map = {
                # See http://www.postgresql.org/docs/9.1/static/functions-matching.html#FUNCTIONS-POSIX-REGEXP
                'like': Value.value.op("~")(value),
                'ilike': Value.value.op("~*")(value)
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

        if 'queryable' in request.params:
            filter_expr = []
            for k in request.params:
                # Collect filter expressions
                if len(request.params[k]) <= 0 or '__' not in k:
                    continue
                col, op = k.split('__')
                # Several values can be queried for one attributes e.g.
                # project_use equals pending and signed. Build the URL
                # like: queryable=project_use&project_use__eq=pending,signed
                values = request.params[k].split(',')
                for v in values:
                    q = self.Session.query(Tag.id.label('filter_tag_id')).\
                        join(Key).\
                        join(Value).\
                        filter(Key.key == col).\
                        filter(__get_filter_expression(v, op))
                    filter_expr.append(q)

            # Do a union of all filter expressions and return it
            if len(filter_expr) > 0:
                tag = filter_expr[0].union(*filter_expr[1:])
                return tag.subquery(), len(filter_expr)

        # Default (no filtering)
        return self.Session.query(Tag.id.label("filter_tag_id")).subquery(), 0

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

    def __init__(self, guid, order_value, version=None, diff_info=None, ** kwargs):
        self._taggroups = []
        self._involvements = []
        self._guid = guid
        self._order_value = order_value
        self._version = version
        self._diff_info = diff_info

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

    def remove_taggroup(self, taggroup):
        if taggroup in self.get_taggroups():
            self.get_taggroups().remove(taggroup)

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
        if self._diff_info is not None:
            for k in self._diff_info:
                ret[k] = self._diff_info[k]

        return ret

    def create_diff(self, previous=None):
        """
        Append a diff object. Try to find TagGroups and Tags of current version
        in previous version.
        """
        if previous is not None:
            # Collect new TagGroups
            diff_new = []
            # Loop through TagGroups of current version
            for tg in self._taggroups:
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

            self._diff_info['diff'] = {'new': diff_new, 'old': diff_old}

    def get_guid(self):
        return self._guid

    def get_order_value(self):
        return self._order_value

    def get_previous_version(self):
        return self._diff_info['previous_version']