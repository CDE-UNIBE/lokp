from geoalchemy import WKBSpatialElement
from geoalchemy.functions import functions
from lmkp.models.database_objects import *
import logging
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPCreated
from pyramid.httpexceptions import HTTPNotFound
from shapely.geometry import asShape
from shapely.geometry.polygon import Polygon
import simplejson as json
from sqlalchemy import select
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import desc

log = logging.getLogger(__name__)

class TagGroup(object):
    
    def __init__(self, id, ** kwargs):
        self.__dict__.update(kwargs)
        self.id = id

    def get_id(self):
        return self.id

    def get_value_by_key(self, key):
        if key in self.__dict__:
            return self.__dict__[key]

        return None

    def append_tag(self, key, value):
        self.__dict__[key] = value

    def to_table(self):
        return self.__dict__

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

        geom = wkb.loads(str(self._geometry.geom_wkb))
        geometry = {}
        geometry['type'] = 'Point'
        geometry['coordinates'] = [geom.x, geom.y]

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

        # Check if the json body is a valid GeoJSON
        if 'data' not in raw:
            return HTTPBadRequest(detail="Not a valid format")

        for activity in raw['data']:
            self._add_activity(request, activity)

        # Return the newly created object with 201 Created HTTP code status
        return HTTPCreated(detail="ok")

    def _add_activity(self, request, activity):

        # The unique identifier
        try:
            identifier = activity['id']
            if identifier is None:
                identifier = uuid.uuid4()
        except KeyError:
            identifier = uuid.uuid4()

        geom = geojson.loads(json.dumps(activity['geometry']),
                                          object_hook=geojson.GeoJSON.to_instance)

        # The geometry
        shape = asShape(geom)
        version = 1

        # Get the latest version if the activity already exists
        v = self.Session.query(Activity.version).filter(Activity.activity_identifier == identifier).order_by(desc(Activity.version)).first()
        if v is not None:
            # Increase the version
            version = (v[0]+1)

        # Add a representative point to the activity
        db_activity = Activity(activity_identifier=identifier, version=version, point=shape.representative_point().wkt)
        # Set the activity status to pending
        db_activity.status = self.Session.query(Status).filter(Status.name == 'pending').first()
        # Add it to the database
        self.Session.add(db_activity)

        # Loop all tag groups
        for taggroup in activity['taggroups']:
            log.debug(taggroup)
            
            if 'id' in taggroup:
                db_taggroup = self.Session.query(A_Tag_Group).filter(A_Tag_Group.id == taggroup['id']).first()
            else:
                db_taggroup = A_Tag_Group()
                #self.Session.add(db_taggroup)
                db_activity.tag_groups.append(db_taggroup)
            

            for key in taggroup:
                if key not in ['id']:
                    log.debug(key)
                    value = taggroup[key]

                    # If the key is not yet in the database, create a new key
                    k = self.Session.query(A_Key).filter(A_Key.key == key).first()
                    if k is None:
                        k = A_Key(key=key)
                        k.fk_language = 1

                    # If the value is not yet in the database, create a new value
                    v = self.Session.query(A_Value).filter(A_Value.value == unicode(value)).first()
                    if v is None:
                        v = A_Value(value = value)
                        v.fk_language = 1


                    # Create a new tag with key and value and append it to the tag group
                    a_tag = A_Tag()
                    db_taggroup.tags.append(a_tag)
                    a_tag.key = k
                    a_tag.value = v
                    #db_taggroup.tags.append(a_tag)

        # Create a new changeset
        changeset = A_Changeset(source='[pending] %s' % activity)
        # Get the user from the request
        changeset.user = self.Session.query(User).filter(User.username == request.user.username).first()
        changeset.activity = db_activity
        self.Session.add(changeset)
    

    def _filter(self, request, activities):


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

        query = self.Session.query(activityQuery.id.label("id"),
                                   activityQuery.activity_identifier.label("activity_identifier"),
                                   activityQuery.point.label("geometry"),
                                   activityQuery.timestamp.label("timestamp"),
                                   activityQuery.version.label("version"),
                                   A_Tag_Group.id.label("taggroup"),
                                   A_Tag.id.label("tag"),
                                   A_Key.key.label("key"),
                                   A_Value.value.label("value")
                                   ).join(A_Tag_Group).join(A_Tag).join(A_Key).join(A_Value)
                                 
        activities = []
        for i in query.all():

            # The activity identifier
            uid = str(i[1])

            # The geometry
            g = i[2]

            # The current tag group id (not global unique)
            taggroup_id = int(i[5])

            key = i[7]
            value = i[8]
            
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
                taggroup = TagGroup(taggroup_id)
                activity.add_taggroup(taggroup)

            taggroup.append_tag(key, value)

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

        