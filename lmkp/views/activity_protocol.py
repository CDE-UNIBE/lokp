
from operator import attrgetter

from geoalchemy import WKBSpatialElement
from geoalchemy.functions import functions
import geojson
from lmkp.models.database_objects import *
from logging import getLogger
from pyramid.httpexceptions import HTTPNotFound
from shapely.geometry import asShape
from shapely.geometry.point import Point
from shapely.geometry.polygon import Polygon
from sqlalchemy.orm.util import class_mapper
from sqlalchemy.sql import and_

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
        if self.__dict__['name'] is not None:
            name = self.__dict__['name']
        else:
            name = "Activity id %s" % self.__dict__['id']

        return {'id': self.__dict__['id'], 'name': name, 'leaf': True}

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

        # Create an empty dictionnary with an activity id as index
        activities = {}
        for row in rows:
            if row.id not in activities:
                activities[row.id] = ActivityFeature(id=row.id, geometry=row.geometry)
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
                if a not in ['id', 'geometry'] and a not in attrs:
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
        id | geometry | activity_identifier | key | value

        """

        # Create the query
        query = self.Session.query(Activity.id.label("id"),
                                   Activity.point.label("geometry"),
                                   Activity.activity_identifier.label("activity_identifier"),
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
        log.debug(offset)
        log.debug(limit)
        return features[offset:(offset+limit)]

    def _filter_features(self, features, request):
        """
        The features filtering is slightly more complicated than the original
        mapfish protocol implementation, since the filtering has to be done
        in Python.
        Important: Specifying several queryable layers, a logical AND operator
        is assumed, similar to the reference implementation.
        """
        
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


        if 'queryable' in request.params:
            queryable = request.params['queryable'].split(',')
            for k in request.params:
                if len(request.params[k]) <= 0 or '__' not in k:
                    continue
                col, op = k.split("__")

                # Unfortunately it is necessary to separate comparison of number
                # types and string types.

                # First handle number comparison
                if col in queryable and op in nbr_map.keys():

                    def __attribute_test(item):

                        # Exclude all features with null values in this attribute.
                        # Is this the correct?
                        if getattr(item, col) is None:
                            return False

                        # Create the expression
                        try:
                            # Try to cast the values to a number
                            attr = float((getattr(item, col)))
                            val = float(request.params[k])
                            expression = "%f %s %f" % (attr, nbr_map[op], val)
                        except:
                            # If the casting fails, Strings are assumed
                            expression = "'%s' %s '%s'" % (getattr(item, col), nbr_map[op], request.params[k])
                        log.debug("expression: %s, column: %s, value: %s" % (expression, col, request.params[k]))
                        return eval(expression)

                    features = filter(__attribute_test, features)

                # Handle the string specific like and ilike comparisons.
                # String comparisons are always case-insensitiv
                elif col in queryable and op in str_map.keys():
                    def __attribute_test(item):

                        # Exclude all features with null values in this attribute.
                        # Is this the correct?
                        if getattr(item, col) is None:
                            return False

                        # Create the expression
                        expression = "'%s'.lower() in '%s'.lower()" % (request.params[k], getattr(item, col))
                        log.debug("expression: %s, column: %s, value: %s" % (expression, col, request.params[k]))
                        return eval(expression)

                    features = filter(__attribute_test, features)

                else:
                    continue

        return features

    
    def read(self, request, filter=None, id=None):
        """
        Build a query based on the filter or the idenfier, send the query
        to the database, and return a Feature or a FeatureCollection.
        """

        # Simple case: a certain activity is requested by id
        if id is not None:

            # Create the logical AND filter that is passed to the query
            filter = and_(filter, Activity.id == id)

            features = self._create_layer(self._query(request, filter), request)

            # Return a HTTP not found exception if no feature is found
            if len(features)  == 0:
                return HTTPNotFound()

            # It is assumed that there is only returned feature, since the
            # activity ids *should* be unique!
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
        """
         # Create the logical AND filter that is passed to the query
        filter = and_(filter, create_filter(request))

        # Create the query and create a GIS compatible flat table layer
        rows = self._create_layer(self._query(request, filter), request)

        # Filter the attributes according to the request
        rows = self._filter_features(rows, request)

        # Order the features
        #rows = self._order(rows, request)

        # Set the offset and the limit
        #rows = self._limit_features(rows, request)

        return len(rows) #[self._filter_attrs(r, request) for r in rows if r is not None]