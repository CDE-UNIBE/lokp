
from operator import attrgetter

from geoalchemy import WKBSpatialElement
from geoalchemy.functions import functions
import geojson
from lmkp.models.database_objects import *
from logging import getLogger
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPCreated
from pyramid.httpexceptions import HTTPNotFound
from shapely.geometry import asShape
from shapely.geometry.point import Point
from shapely.geometry.polygon import Polygon
import simplejson as json
from sqlalchemy.orm.util import class_mapper
from sqlalchemy.sql import and_
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.expression import select
import transaction

log = getLogger(__name__)

def _get_col_epsg(mapped_class, geom_attr):
    """
    Get the EPSG code associated with a geometry attribute.

    Arguments:

    geom_attr
        the key of the geometry property as defined in the SQLAlchemy
        mapper. If you use ``declarative_base`` this is the name of
        the geometry attribute as defined in the mapped class.
    """
    col = class_mapper(mapped_class).get_property(geom_attr).columns[0]
    return col.type.srid

def create_geom_filter(request, within_distance_additional_params={}):
    """
    Create MapFish geometry filter based on the request params. Either
    a box or within or geometry filter, depending on the request params.
    Additional named arguments are passed to the spatial filter.

    Arguments:

    request
        the request.

    mapped_class
        the SQLAlchemy mapped class.

    geom_attr
        the key of the geometry property as defined in the SQLAlchemy
        mapper. If you use ``declarative_base`` this is the name of
        the geometry attribute as defined in the mapped class.

    within_distance_additional_params
    additional_params to pass to the ``within_distance`` function.
    """
    tolerance = float(request.params.get('tolerance', 0.0))
    epsg = None
    if 'epsg' in request.params:
        epsg = int(request.params['epsg'])
    box = request.params.get('bbox')
    geometry = None
    if box is not None:
        box = map(float, box.split(','))
        geometry = Polygon(((box[0], box[1]), (box[0], box[3]),
                           (box[2], box[3]), (box[2], box[1]),
                           (box[0], box[1])))
    elif 'lon' and 'lat' in request.params:
        geometry = Point(float(request.params['lon']),
                         float(request.params['lat']))
    elif 'geometry' in request.params:
        geometry = loads(request.params['geometry'], object_hook=GeoJSON.to_instance)
        geometry = asShape(geometry)
    if geometry is None:
        return None
    column_epsg = _get_col_epsg(Activity, "point")
    epsg = column_epsg if epsg is None else epsg
    if epsg != column_epsg:
        geom_attr = functions.transform(geom_attr, epsg)
    wkb_geometry = WKBSpatialElement(buffer(geometry.wkb), epsg)
    log.debug("Filter geometry: %s" % wkb_geometry.coords)
    return functions._within_distance(Activity.point, wkb_geometry, tolerance,
                                      within_distance_additional_params)

def create_attr_filter(request):
    """
    Create an ``and_`` SQLAlchemy filter (a ClauseList object) based
    on the request params (``queryable``, ``eq``, ``ne``, ...).

    Arguments:

    request
    the request.

    mapped_class
    the SQLAlchemy mapped class.
    """

    mapping = {
        'eq': '__eq__',
        'ne': '__ne__',
        'lt': '__lt__',
        'lte': '__le__',
        'gt': '__gt__',
        'gte': '__ge__',
        'like': 'like',
        'ilike': 'ilike'
    }
    
    filters = []
    if 'queryable' in request.params:
        queryable = request.params['queryable'].split(',')
        for k in request.params:
            if len(request.params[k]) <= 0 or '__' not in k:
                continue
            col, op = k.split("__")
            if col not in queryable or op not in mapping.keys():
                continue
            column = getattr(Activity, col)
            f = getattr(column, mapping[op])(request.params[k])
            filters.append(f)
    return and_(*filters) if len(filters) > 0 else None

def create_filter(request, ** kwargs):
    """
    Create MapFish default filter based on the request params.
    Arguments:

    request
    the request.

    mapped_class
    the SQLAlchemy mapped class.

    geom_attr
    the key of the geometry property as defined in the SQLAlchemy
    mapper. If you use ``declarative_base`` this is the name of
    the geometry attribute as defined in the mapped class.


    \**kwargs
    additional arguments passed to ``create_geom_filter()``.
    """
    #attr_filter = create_attr_filter(request)
    # Attribute filtering has to be done client-side i.e. in the controller and
    # not on the database

    geom_filter = create_geom_filter(request, ** kwargs)
    if geom_filter is None: # and attr_filter is None:
        return None
    #return and_(geom_filter, attr_filter)
    return geom_filter

def asbool(val):
    # Convert the passed value to a boolean.
    if isinstance(val, basestring):
        return val.lower() not in ['false', '0']
    else:
        return bool(val)

class ActivityFeature(object):
    """
    Define a new class instead of a named tuple, see also comments of
    this post:
    http://pysnippet.blogspot.com/2010/01/named-tuple.html
    The attribute columns id and geometry are reserved and mandatory.
    """

    def __init__(self, ** kwargs):
        self.__dict__.update(kwargs)

    @property
    def __tree_interface__(self):
        name  = ""
        if self.__dict__['Name'] is not None:
            name = self.__dict__['Name']
        else:
            name = "Activity id %s" % self.__dict__['id']

        return {'id': self.__dict__['id'], 'Name': name, 'leaf': True}

    @property
    def __geo_interface__(self):
        """
        Implement the __geo_interface__ that is used by the geojson
        renderer
        """
        properties = {}

        # Loop all attributes
        for index in self.__dict__:
            # Ignore the reserved keywords id and geometry
            if index not in ['id', 'geometry']:
                attribute_value = getattr(self, index)
                # Append only not null attributes to the properties
                if attribute_value is not None:
                    # Try to cast the value to integer or float
                    try:
                        properties[index] = int(attribute_value)
                    except:
                        try:
                            properties[index] = float(attribute_value)
                        except:
                            # Finally write it as it is, GeoJson will handle
                            # it as String
                            properties[index] = attribute_value

        if self.geometry is not None:
            geom = wkb.loads(str(self.geometry.geom_wkb))
        else:
            geom = None
        # Return a new Feature
        return geojson.Feature(id=self.id, geometry=geom, properties=properties)
    

class ActivityProtocol(object):
    """
    The ActivityProtocol class implements the mapfish protcol but using the
    underlying data model developped within the Observartory on Land Acquisitions
    project.
    It is heavily inspired by the Papyrus project and reuses a lot of this code
    base.
    More information about the MapFish protocol:
    http://trac.mapfish.org/trac/mapfish/wiki/MapFishProtocol

    Session
        an SQLAlchemy ``Session`` class.

    mapped_class
        the class mapped to a database table in the ORM.

    geom_attr
        the key of the geometry property as defined in the SQLAlchemy
        mapper. If you use ``declarative_base`` this is the name of
        the geometry attribute as defined in the mapped class.

    readonly
        ``True`` if this protocol is read-only, ``False`` otherwise. If
        ``True``, the methods ``create()``, ``update()`` and ``delete()``
        will set 405 (Method Not Allowed) as the response status and
        return right away.

    \**kwargs
        before_create
            a callback function called before a feature is inserted
            in the database table, the function receives the request,
            the feature read from the GeoJSON document sent in the
            request, and the database object to be updated. The
            latter is None if this is is an actual insertion.

        before_update
            a callback function called before a feature is updated
            in the database table, the function receives the request,
            the feature read from the GeoJSON document sent in the
            request, and the database object to be updated.

        before_delete
            a callback function called before a feature is deleted
            in the database table, the function receives the request
            and the database object about to be deleted.
    """
    
    def __init__(self, Session, readonly=False, ** kwargs):
        self.Session = Session
        self.readonly = readonly
        self.mapped_class = Activity
        self.before_create = kwargs.get('before_create')
        self.before_update = kwargs.get('before_update')
        self.before_delete = kwargs.get('before_delete')

    def _create_layer(self, rows, request=None):
        """
        This method takes a list of resulting rows from the database with the
        following columns: id, geometry, activity_identifier, key, value
        and converts the list to a flat GIS layer table with the following
        columns: id, geometry, attribute1, attribute2, attribute3 ...
        A list of ActivityFeature objects are returned. Since the ActivityFeature
        class implements the __geo_interface__, these objects can directly
        passed to the geojson renderer.
        """

        # First extract all available attributes
        attributes = []
        for row in rows:
            if row.key not in attributes:
                attributes.append(row.key)

        log.debug(attributes)

        # Create an empty dictionnary with an activity id as index
        activities = {}
        for row in rows:
            if row.id not in activities:
                activities[row.id] = ActivityFeature(id=row.id,
                                                     activity_identifier=row.activity_identifier,
                                                     geometry=row.geometry,
                                                     timestamp=row.timestamp,
                                                     version=row.version)
                # Set all available attributes for this activity feature to None.
                # This is necessary to be able to sort the features in method
                # self._order
                for attr in attributes:
                    setattr(activities[row.id], attr, None)

            # Set the actual attribute value
            setattr(activities[row.id], row.key, row.value)

        # Create an empty list
        features = []

        # Loop all features in activities and append it to the features list
        for fid in activities:
            features.append(activities[fid])

        return features
        

    def _filter_attrs(self, feature, request):
        """
        Remove some attributes from the feature and set the geometry to None
        in the feature based ``attrs`` and the ``no_geom`` parameters.
        """

        if asbool(request.params.get('no_geom', False)):
            feature.geometry = None

        if 'attrs' in request.params:
            attrs = request.params['attrs'].split(',')
            for a in feature.__dict__:
                if a not in ['id', 'geometry', 'timestamp', 'version'] and a not in attrs:
                    setattr(feature, a, None)

        return feature

    def _get_order_by(self, request):
        """
        Return a tuple with the attribute column to sort and the direction or
        None if no sorting is requested
        """

        # Get the attribute column to sort
        sort = request.params.get('sort', request.params.get('order_by'))
        if sort is None:
            return None, None

        # Get the sorting direction, default is ascending sorting
        reverse = False
        if request.params.get('dir', '').upper() == 'DESC':
            reverse = True
        return sort, reverse

    def _query(self, request, filter=None):
        """
        Build a query based on the filter and the request params,
        and send the query to the database.

        Returns a set of tuples with the following attributes:
        id | activity_identifier | geometry | timestamp | version | key | value

        """

        # Check if a timestamp is set
        if request.params.get('timestamp', None) is not None:
            return self._query_timestamp(request, filter).all()

        # Create the query
        query = self.Session.query(Activity.id.label("id"),
                                   Activity.activity_identifier.label("activity_identifier"),
                                   Activity.point.label("geometry"),
                                   Activity.timestamp.label("timestamp"),
                                   Activity.version.label("version"),
                                   A_Key.key.label("key"),
                                   A_Value.value.label("value")
                                   ).join(A_Tag_Group).join(A_Tag).join(A_Key).join(A_Value).join(Status).group_by(Activity.id, A_Key.key, A_Value.value).order_by(Activity.id).filter(filter)
        return query.all()

    def _order(self, features, request):
        """
        Sorts the features according as requested
        """

        orderByAttribute, reverse = self._get_order_by(request)
        if orderByAttribute is None:
            # If no sorting is requested, just return the feature list
            return features
        
        try:
            # Try to sort the list
            return sorted(features, key=attrgetter(orderByAttribute), reverse=reverse)
        except:
            return features

    def _limit_features(self, features, request):
        """
        Sets a limit and an offset
        """

        limit = None
        offset = 0
        if 'maxfeatures' in request.params:
            limit = int(request.params['maxfeatures'])
        if 'limit' in request.params:
            limit = int(request.params['limit'])
        if 'offset' in request.params:
            offset = int(request.params['offset'])

        if limit is not None:
            limit = limit + offset

        return features[offset:limit]

    def _filter_features(self, features, request):
        """
        The features filtering is slightly more complicated than the original
        mapfish protocol implementation, since the filtering has to be done
        in Python.
        Important: Specifying several queryable layers, a logical AND operator
        is assumed, similar to the reference implementation.
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

            # Unfortunately it is necessary to separate comparison of number
            # types and string types.

            # First handle number comparison
            if op in nbr_map.keys():

                def __attribute_test(item):

                    # Exclude all features with null values in this attribute.
                    # Is this correct?
                    if getattr(item, col) is None:
                        return False

                    # Create the expression
                    try:
                        # Try to cast the values to a number
                        attr = float((getattr(item, col)))
                        v = float(value)
                        expression = "%f %s %f" % (attr, nbr_map[op], v)
                    except:
                        # If the casting fails, Strings are assumed
                        v = str(value)
                        expression = "'%s' %s '%s'" % (getattr(item, col), nbr_map[op], v)

                    log.debug("expression: %s, column: %s, value: %s" % (expression, col, v))
                    return eval(expression)

                f = filter(__attribute_test, f)

            # Handle the string specific like and ilike comparisons.
            # String comparisons are always case-insensitiv
            elif op in str_map.keys():
                def __attribute_test(item):

                    # Exclude all features with null values in this attribute.
                    # Is this correct?
                    if getattr(item, col) is None:
                        return False

                    # Create the expression
                    expression = "'%s'.lower() in '%s'.lower()" % (value, getattr(item, col))
                    log.debug("expression: %s, column: %s, value: %s" % (expression, col, value))
                    return eval(expression)

                f = filter(__attribute_test, f)

            else:
                pass

            return f

        if 'queryable' in request.params:

            # Implement the logical OR operator
            if logicalOperator == 'or':

                # A list of features that have fulfilled at least on condition
                filteredFeatures = []
                for k in request.params:
                    if len(request.params[k]) <= 0 or '__' not in k:
                        continue
                    # Several values can be queried for one attributes e.g.
                    # project_use equals pending and signed. Build the URL
                    # like: queryable=project_use&project_use__eq=pending,signed
                    values = request.params[k].split(",")
                    for v in values:
                        filteredFeatures.append(__filter(features, k, v))

                # Merge all lists:
                f = []
                for ff in filteredFeatures:
                    for feature in ff:
                        if feature not in f:
                            f.append(feature)

                features = f

            # Implement the logical AND operator
            elif logicalOperator == 'and':
                for k in request.params:
                    if len(request.params[k]) <= 0 or '__' not in k:
                        continue
                    values = request.params[k].split(",")
                    for v in values:
                        features = __filter(features, k, v)

        return features

    
    def read(self, request, filter=None, uid=None):
        """
        Build a query based on the filter or the idenfier, send the query
        to the database, and return a Feature or a FeatureCollection.
        """

        # Simple case: a certain activity is requested by id
        if uid is not None:

            # Create the logical AND filter that is passed to the query
            filter = and_(filter, Activity.activity_identifier == uid)

            features = self._create_layer(self._query(request, filter), request)

            # Return a HTTP not found exception if no feature is found
            if len(features)  == 0:
                return HTTPNotFound()

            # It is assumed that there is only returned feature, since there is
            # exacly one active activity version (make sure in data model)
            return self._filter_attrs(features[0], request)

        # In the other case it is necessary to request all activities and
        # do further processing in the controller.
        else:

            # Create the logical AND filter that is passed to the query
            filter = and_(filter, create_filter(request))

            # Create the query and create a GIS compatible flat table layer
            rows = self._create_layer(self._query(request, filter), request)

            # Filter the attributes according to the request
            rows = self._filter_features(rows, request)

            # Order the features
            rows = self._order(rows, request)

            # Set the offset and the limit
            rows = self._limit_features(rows, request)

            return [self._filter_attrs(r, request) for r in rows if r is not None]

    def count(self, request, filter=None):
        """
        Return the number of records matching the given filter.
        Offset and limit parameters are ignored.
        """
            # Create the logical AND filter that is passed to the query
        filter = and_(filter, create_filter(request))

        # Create the query and create a GIS compatible flat table layer
        rows = self._create_layer(self._query(request, filter), request)

        # Filter the attributes according to the request
        rows = self._filter_features(rows, request)

        return len(rows)

    def create(self, request):
        """
        Create a new activity and store it to the database
        """

        raw = request.json_body

        # Check if the json body is a valid GeoJSON
        if 'type' not in raw:
            return HTTPBadRequest(detail="Not a valid GeoJSON")

        if raw['type'] == 'FeatureCollection':
            # Dump the dictionary to string to reload it as GeoJSON
            featureCollection = geojson.loads(json.dumps(raw), object_hook=geojson.GeoJSON.to_instance)

            for feature in featureCollection.features:
                self._add_feature(request, feature)

        if raw['type'] == 'Feature':
            # Dump the dictionary to string to reload it as GeoJSON
            feature = geojson.loads(json.dumps(raw), object_hook=geojson.GeoJSON.to_instance)
            self._add_feature(request, feature)

        # Return the newly created object with 201 Created HTTP code status
        return HTTPCreated(detail=geojson.dumps(feature))

    def _add_feature(self, request, feature):
        """
        Add or update a new activity
        """

        # The unique identifier
        try:
            identifier = feature.id
            if identifier is None:
                identifier = uuid.uuid4()
        except AttributeError:
            identifier = uuid.uuid4()
        # The geometry
        shape = asShape(feature.geometry)
        version = 1

        # Get the latest version if the activity already exists
        v = self.Session.query(Activity.version).filter(Activity.activity_identifier == identifier).order_by(desc(Activity.version)).first()
        if v is not None:
            # Increase the version
            version = (v[0]+1)

        # Add a representative point to the activity
        activity = Activity(activity_identifier=identifier, version=version, point=shape.representative_point().wkt)
        # Set the activity status to pending
        activity.status = self.Session.query(Status).filter(Status.name == 'pending').first()
        # Add it to the database
        self.Session.add(activity)

        # Loop all feature attributes
        for property in feature.properties:
            # If the key is not yet in the database, create a new key
            k = self.Session.query(A_Key).filter(A_Key.key == property).first()
            if k is None:
                k = A_Key(key=property)
                k.fk_language = 1

            # If the value is not yet in the database, create a new value
            v = self.Session.query(A_Value).filter(A_Value.value == unicode(feature.properties[property])).first()
            if v is None:
                v = A_Value(value = feature.properties[property])
                v.fk_language = 1

            # Create a new tag group and append it to the activity
            tag_group = A_Tag_Group()
            activity.tag_groups.append(tag_group)
            # Create a new tag with key and value and append it to the tag group
            a_tag = A_Tag()
            a_tag.key = k
            a_tag.value = v
            tag_group.tags.append(a_tag)

        # Create a new changeset
        changeset = A_Changeset(source='[pending] %s' % activity)
        # Get the user from the request
        changeset.user = self.Session.query(User).filter(User.username == request.user.username).first()
        changeset.activity = activity
        self.Session.add(changeset)

    def _query_timestamp(self, request, filter=None):
        """
        Build a query based on the filter and the request params,
        and send the query to the database.

        Returns a set of tuples with the following attributes:
        id | activity_identifier | geometry | timestamp | version | key | value

        """

        # Get the timestamp from the request
        timestamp = request.params.get('timestamp', '2100-01-01 00:00:00')

        # Name the new column
        validid = "validid"

        # Set a status filter. Consider only active and overwritten activities.
        statusFilter = or_(Status.name == 'active', Status.name == 'overwritten')

        # Create alias and join already table activity to status
        a = self.Session.query(Activity).outerjoin(Status, Activity.fk_status == Status.id).filter(statusFilter).subquery("a")
        b = Activity.__table__.alias("b")

        # The latest id (and thus version and timestamp) for an activity
        valid_id_select = select([a.c.id],
                                 and_(a.c.activity_identifier == b.c.activity_identifier, a.c.timestamp < timestamp),
                                 order_by=desc(a.c.version),
                                 limit=1).label(validid)

        # Select a list of valid ids and the corresponding activity uuid
        s = select([valid_id_select,
                   b.c.activity_identifier,
                   ],
                   group_by="%s, b.activity_identifier" % validid,
                   order_by=validid).alias("latest_activities")

        # Remove duplicate and null ids
        t = select([s],
                   s.c.validid != None,
                   group_by=[s.c.validid, s.c.activity_identifier]
                   ).alias("t")

        # Create the main query and joins
        query = self.Session.query(t.c.validid.label("id"),
                                   t.c.activity_identifier.label("activity_identifier"),
                                   Activity.point.label("geometry"),
                                   Activity.timestamp.label("timestamp"),
                                   Activity.version.label("version"),
                                   A_Key.key.label("key"),
                                   A_Value.value.label("value")).\
            join(Activity, t.c.validid == Activity.id).\
            join(A_Tag_Group).join(A_Tag).join(A_Key).\
            join(A_Value).group_by(t.c.validid,
                                   t.c.activity_identifier,
                                   Activity.point,
                                   Activity.timestamp,
                                   Activity.version,
                                   A_Key.key,
                                   A_Value.value).order_by(t.c.validid).filter(filter)

        return query
