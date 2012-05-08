from geoalchemy import WKBSpatialElement
from geoalchemy.functions import functions
from lmkp.models.database_objects import *
import logging
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPCreated
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from shapely.geometry import asShape
from shapely.geometry.polygon import Polygon
import simplejson as json
from sqlalchemy import select
from sqlalchemy import join
from sqlalchemy import alias
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.expression import or_

log = logging.getLogger(__name__)

class Tag(object):

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def get_key(self):
        return self.key

    def get_value(self):
        return self.value

    def to_table(self):
        return {'key': self.key, 'value': self.value}

class TagGroup(object):
    
    def __init__(self, id=None, main_key=None):
        self._id = id
        self._main_key = main_key
        self._tags = []

    def add_tag(self, tag):
        self._tags.append(tag)

    def get_id(self):
        return self._id

    def get_value_by_key(self, key):
        if key in self.__dict__:
            return self.__dict__[key]

        return None

    def to_table(self):
        tags = []
        for t in self._tags:
            tags.append(t.to_table())
        return {'id': self._id, 'main_key': self._main_key, 'tags': tags}

class ActivityFeature2(object):

    def __init__(self, guid, geometry=None, ** kwargs):
        self._taggroups = []
        self._guid = guid
        self._geometry = geometry

    def add_taggroup(self, taggroup):
        self._taggroups.append(taggroup)

    def find_taggroup_by_id(self, id):
        for t in self._taggroups:
            if t.get_id() == id:
                return t
        
        return None

    def to_table(self):
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

        return {'id': self._guid, 'taggroups': tg, 'geometry': geometry}

    def get_guid(self):
        return self._guid


class ActivityProtocol2(object):

    def __init__(self, Session):

        self.Session = Session

    def read(self, request, filter=None, uid=None):

        # Query the database
        activities = self._query(request, filter)

        # Filter the attributes
        activities = self._filter(request, activities)

        # Get the total number of features before limiting the result set
        count = len(activities)

        # Offset and limit
        offset = self._get_offset(request)
        try:
            limit = self._get_limit(request) + offset
        except TypeError:
            limit = None
        activities = activities[offset:limit]

        return {'total': count, 'data': [a.to_table() for a in activities]}

    def create(self, request):
        """
        Add or update activities
        """
        
        raw = request.json_body

        # Check if the json body is a valid diff file
        if 'create' not in raw and 'modify' not in raw and 'delete' not in raw:
            return HTTPBadRequest(detail="Not a valid format")

        # Handle first the request to create new activities
        if 'create' in raw:
            if 'activities' in raw['create']:
                for activity in raw['create']['activities']:
                    self._create_activity(request, activity)

        # Return the newly created object with 201 Created HTTP code status
        return HTTPCreated(detail="ok")

    def _create_activity(self, request, activity):

        # Create a new unique identifier
        identifier = uuid.uuid4()
        # The initial version is 1 of course
        version = 1

        # Try to get the geometry
        try:
            geom = geojson.loads(json.dumps(activity['geometry']),
                                 object_hook=geojson.GeoJSON.to_instance)

            # The geometry
            shape = asShape(geom)
            # Create a new activity and add a representative point to the activity
            db_activity = Activity(activity_identifier=identifier, version=version, point=shape.representative_point().wkt)
        except KeyError:
            # If no geometry is submitted, create a new activity without a geometry
            db_activity = Activity(activity_identifier=identifier, version=version)

        db_activity.tag_groups = []
        # Set the activity status to pending
        db_activity.status = self.Session.query(Status).filter(Status.name == 'pending').first()
        # Add it to the database
        self.Session.add(db_activity)

        # Loop all tag groups
        for taggroup in activity['taggroups']:

            db_taggroup = A_Tag_Group()
            db_activity.tag_groups.append(db_taggroup)

            # Reset the main_key string
            main_key = None
            # Try to get the main_key from the input JSON file. The main_key
            # is not mandatory
            try:
                main_key = taggroup['main_key']
            except KeyError:
                pass

            # Loop all tags within a tag group
            for tag in taggroup['tags']:
                # Get the key and the value of the current tag
                key = tag['key']
                value = tag['value']

                # The key has to be already in the database
                k = self.Session.query(A_Key).filter(A_Key.key == key).first()

                # If the value is not yet in the database, create a new value
                v = self.Session.query(A_Value).filter(A_Value.value == unicode(value)).first()
                if v is None:
                    v = A_Value(value=value)
                    v.fk_language = 1

                # Create a new tag with key and value and append it to the tag group
                a_tag = A_Tag()
                db_taggroup.tags.append(a_tag)
                a_tag.key = k
                a_tag.value = v

                # Check if the current tag is the main tag of this tag group. If
                # yes, set the main_tag attribute to this tag
                if a_tag.key.key == main_key:
                    db_taggroup.main_tag = a_tag

        # Create a new changeset
        changeset = A_Changeset(source='[pending] %s' % activity)
        # Get the user from the request
        changeset.user = self.Session.query(User).filter(User.username == request.user.username).first()
        changeset.activity = db_activity
        self.Session.add(changeset)
    
    def _filter(self, request, activities):
        """
        """

        logicalOperator = request.params.get("logical_op", "and").lower()

        nbr_map = {
            'eq': '==',
            'ne': '!=',
            'lt': '<',
            'lte': '<=',
            'gt': '>',
            'gte': '>='
        }

        str_map = {
            'like': 'like',
            'ilike': 'ilike'
        }

        def __filter(f, attribute, value):

            queryable = request.params['queryable'].split(',')
            col, op = attribute.split("__")

            # If col is not in the queryable attribute list, return an empty list
            if col not in queryable:
                return []

            # First handle number comparison
            if op in nbr_map.keys():
                def __attribute_test(item):
                    """
                        item is an ActivityFeature2 object
                        """

                    is_valid = False

                    for taggroup in item._taggroups:

                        try:
                            attribute = getattr(taggroup, col)
                        except AttributeError:
                            continue

                        # Create the expression
                        try:
                            # Exclude all features with null values in this attribute.
                            # Is this correct?
                            if attribute is None:
                                #return False
                                continue

                            # Try to cast the values to a number
                            attr = float((attribute))
                            v = float(value)
                            expression = "%f %s %f" % (attr, nbr_map[op], v)
                        except:
                            # If the casting fails, Strings are assumed
                            v = str(value)
                            expression = "'%s' %s '%s'" % (attribute, nbr_map[op], v)

                        log.debug("expression: %s, column: %s, value: %s" % (expression, col, v))

                        evalutated = eval(expression)
                        if evalutated:
                            is_valid = evalutated

                    # Return true for the whole activity if one tag group passes
                    # the attribute filter
                    return is_valid

                f = [i for i in f if __attribute_test(i)]

            # Handle the string specific like and ilike comparisons.
            # String comparisons are always case-insensitiv
            elif op in str_map.keys():
                def __attribute_test(item):

                    is_valid = False

                    for taggroup in item._taggroups:

                        # Check if the current taggroup has this feature, if not
                        # this taggroup is excluded
                        try:
                            attribute = getattr(taggroup, col)
                        except AttributeError:
                            continue

                        # Create the expression
                        expression = "'%s'.lower() in '%s'.lower()" % (value, attribute)

                        log.debug("expression: %s, column: %s, value: %s" % (expression, col, value))
                        evalutated = eval(expression)
                        if evalutated:
                            is_valid = evalutated

                    # Return true for the whole activity if one tag group passes
                    # the attribute filter
                    return is_valid

                f = [i for i in f if __attribute_test(i)]

            else:
                pass

            log.debug(len(f))
            return f

        if 'queryable' in request.params:

            # Implement the logical OR operator
            if logicalOperator == 'or':

                # A list of features that have fulfilled at least on condition
                filteredActivities = []
                for k in request.params:
                    if len(request.params[k]) <= 0 or '__' not in k:
                        continue
                    # Several values can be queried for one attributes e.g.
                    # project_use equals pending and signed. Build the URL
                    # like: queryable=project_use&project_use__eq=pending,signed
                    values = request.params[k].split(",")
                    for v in values:
                        filteredActivities.append(__filter(activities, k, v))

                # Merge all lists:
                f = []
                for ff in filteredActivities:
                    for feature in ff:
                        if feature not in f:
                            f.append(feature)

                activities = f

            # Implement the logical AND operator
            elif logicalOperator == 'and':

                for k in request.params:
                    if len(request.params[k]) <= 0 or '__' not in k:
                        continue
                    values = request.params[k].split(",")
                    for v in values:
                        activities = __filter(activities, k, v)

        return activities


    def _query(self, request, filter=None):
        """

            """

        # Get the status
        status_id = self.Session.query(Status.id).filter(Status.name == self._get_status(request))

        # Create the query
        limited_select = select([Activity.id,
                                Activity.activity_identifier,
                                Activity.point,
                                Activity.point,
                                Activity.timestamp,
                                Activity.version
                                ]).where(and_(Activity.fk_status == status_id, self._create_geom_filter(request))).alias("limited_activites")

        # An aliased helper class
        activityQuery = AliasedClass(Activity, alias=limited_select)

        #joined_main_key = select([A_Tag_Group.id, A_Tag.key.key]).join(A_Tag_Group, A_Tag, A_Tag_Group.fk_a_tag == A_Tag.id).alias("joined_taggroups")
        #joined_main_key = select([A_Tag_Group.id, A_Tag.key.key]).select_from(A_Tag_Group).alias("joined_taggroups")

        t1 = select([A_Tag_Group.id, A_Tag_Group.fk_a_tag]).alias("t1")
        t2 = select([A_Tag.id, A_Tag.key]).alias("t2")

        #joined_main_key = select([A_Tag.key, A_Tag_Group.id]).join(t1,t2)
        #main_key_query = AliasedClass(A_Tag_Group, alias=joined_main_key)

        #for i in joined_main_key:
        #    print i

        query = self.Session.query(activityQuery.id.label("id"),
                                   activityQuery.activity_identifier.label("activity_identifier"),
                                   activityQuery.point.label("geometry"),
                                   activityQuery.timestamp.label("timestamp"),
                                   activityQuery.version.label("version"),
                                   A_Tag_Group.id.label("taggroup"),
                                   A_Tag_Group.fk_a_tag.label("main_key"),
                                   A_Tag.id.label("tag"),
                                   A_Key.key.label("key"),
                                   A_Value.value.label("value")
                                   ).join(A_Tag_Group).join(A_Tag, A_Tag_Group.id == A_Tag.fk_a_tag_group).join(A_Key).join(A_Value)

        activities = []
        for i in query.all():

            # The activity identifier
            uid = str(i[1])

            # The geometry
            g = i[2]

            # The current tag group id (not global unique)
            taggroup_id = int(i[5])

            key = i[8]
            value = i[9]

            activity = None
            for a in activities:
                if a.get_guid() == uid:
                    activity = a

            if activity == None:
                activity = ActivityFeature2(uid, geometry=g)
                activities.append(activity)

            # Check if there is already this tag group present in the current
            # activity
            taggroup = None
            if activity.find_taggroup_by_id(taggroup_id) is not None:
                taggroup = activity.find_taggroup_by_id(taggroup_id)
            else:
                taggroup = TagGroup(taggroup_id, i[6])
                activity.add_taggroup(taggroup)

            taggroup.add_tag(Tag(key, value))

        return activities

    def _create_geom_filter(self, request):
        """
            """

        try:
            epsg = int(request.params.get('epsg', 4326))
        except:
            epsg = 4326

        bbox = request.params.get('bbox', None)
        if bbox is not None:
            box = map(float, bbox.split(','))
            geometry = Polygon((
                               (box[0], box[1]),
                               (box[0], box[3]),
                               (box[2], box[3]),
                               (box[2], box[1]),
                               (box[0], box[1]))
                               )

            wkb_geometry = WKBSpatialElement(buffer(geometry.wkb), epsg)

            return functions.intersects(Activity.point, wkb_geometry)

        return None


    def _get_limit(self, request):

        limit = request.params.get('limit', None)
        if limit is not None:
            try:
                return int(limit)
            except ValueError:
                pass

        return None

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

        