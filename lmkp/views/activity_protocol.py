import geojson
from operator import attrgetter
from lmkp.models.database_objects import *
import logging
from pyramid.httpexceptions import HTTPError
from collections import namedtuple

log = logging.getLogger(__name__)

def asbool(val):
    # Convert the passed value to a boolean.
    if isinstance(val, basestring):
        return val.lower() not in ['false', '0']
    else:
        return bool(val)

class ActivityProtocol(object):
    """
    The FeatureProtocol class implements the mapfish protcol but using the
    underlying data model developped within the Land Matrix Knowledge Platform
    aka Observartory on Land Acquisitions (OLAAAA!) project.
    It is heavily inspired by the Papyrus project and reuses a lot of this code base.

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

    def _filter_attrs(self, feature, request):
        """
        Remove some attributes from the feature and set the geometry to None
        in the feature based ``attrs`` and the ``no_geom`` parameters.
        """
        if 'attrs' in request.params:
            attrs = request.params['attrs'].split(',')
            props = feature.properties
            new_props = {}
            for name in attrs:
                if name in props:
                    new_props[name] = props[name]
            feature.properties = new_props
        if asbool(request.params.get('no_geom', False)):
            feature.geometry = None
        return feature

    def _get_order_by(self, request):
        """
        Return an SA order_by
        """
        return request.params.get('sort', request.params.get('order_by'))

    def geofy(self, resultSet, request):
        """
        Takes a query result set and transform it to geo objects
        """

        features = {}

        for result in resultSet:
            if result.id not in features:
                features[result.id] = {'id': result.id, 'properties': {}, 'geometry': None}

            features[result.id]['id'] = result.id
            features[result.id]['properties'][result.key] = result.value
            features[result.id]['geometry'] = wkb.loads(str(result.geometry.geom_wkb))


        geoobjects = []
        for index in features:
            f = features[index]
            geoobjects.append(geojson.Feature(id=f['id'], geometry=f['geometry'], properties=f['properties']))

        return geoobjects

    def _query(self, request, filter=None):
        """
        Build a query based on the filter and the request params,
        and send the query to the database.
        """
        limit = None
        offset = None
        if 'maxfeatures' in request.params:
            limit = int(request.params['maxfeatures'])
        if 'limit' in request.params:
            limit = int(request.params['limit'])
        if 'offset' in request.params:
            offset = int(request.params['offset'])
        #if filter is None:
            #   filter = create_filter(request, self.mapped_class, self.geom_attr)
        query = self.Session.query(Activity.point.label("geometry"),
                                   Activity.id.label("id"),
                                   Activity.activity_identifier.label("activity_identifier"),
                                   A_Key.key.label("key"),
                                   A_Value.value.label("value")
                                   ).join(A_Tag_Group).join(A_Tag).join(A_Key).join(A_Value).join(Status).filter(Status.name == 'active').group_by(Activity.id, A_Key.key, A_Value.value).order_by(Activity.id)
        #order_by = self._get_order_by(request)
        #if order_by is not None:
         #   query = query.order_by(order_by)
        #query = query.limit(limit).offset(offset)
        return query.all()

    def _order(self, features, request):
        """
        Namedtuple to sort
        """

        orderByAttribute = self._get_order_by(request)
        if orderByAttribute is None:
            return features
        
        attributes = ['id', 'geometry']
        emptyAttributes = [None, None]
        
        for feature in features:
            for attr in feature.properties:
                if attr not in attributes:
                    attributes.append(attr)
                    emptyAttributes.append(None)

        if orderByAttribute not in attributes:
            return features

        ActivityRow = namedtuple('ActivityRow', attributes, rename=True)

        # An empty activity that serves as template for all features
        templateActivity = ActivityRow(*emptyAttributes)

        unsortedActivities = []
        for feature in features:

            actDict = {'id': feature.id, 'geometry': feature.geometry}

            for property in feature.properties:

                try:
                    value = int(feature.properties[property])
                except ValueError:
                    try:
                        value = float(feature.properties[property])
                    except ValueError:
                        value = str(feature.properties[property])

                actDict[property] = value
                currentActivity = templateActivity._replace(**actDict)

            unsortedActivities.append(currentActivity)

        sortedActivities = sorted(unsortedActivities, key = attrgetter(orderByAttribute))

        sortedFeatures = []
        for a in sortedActivities:
            properties = {}
            for index in a._asdict():
                # Ignore the reserved keywords id and geometry
                if index not in ['id', 'geometry']:
                    properties[index] = (getattr(a,index))
            sortedFeatures.append(geojson.Feature(id=a.id, geometry=a.geometry, properties=properties))

        return sortedFeatures
        

    def read(self, request, filter=None, id=None):
        """
        Build a query based on the filter or the idenfier, send the query
        to the database, and return a Feature or a FeatureCollection.
        """
        ret = None
        if id is not None:

            table = self.Session.query(Activity.point.label("geometry"), Activity.id.label("id"), Activity.activity_identifier, A_Key.key.label("key"), A_Value.value.label("value"))

            o = table.filter(Activity.id == id).join(A_Tag_Group).join(A_Tag).join(A_Key).join(A_Value).join(Status).filter(Status.name == 'active').group_by(Activity.id, A_Key.key, A_Value.value).order_by(Activity.id)

            if o is None:
                return HTTPNotFound()

            resultActivities = self.geofy(o, request)

            # Only one feature can be returned!
            if len(resultActivities) != 1:
                return HTTPError()

            # FIXME: we return a Feature here, not a mapped object, do
            # we really want that?
            ret = self._filter_attrs(resultActivities[0], request)
        else:
            objs = self.geofy(self._query(request, filter), request)

            # Sort the table
            objs = self._order(objs, request)

            ret = geojson.FeatureCollection([self._filter_attrs(o.__geo_interface__, request) for o in objs if o is not None])
        return ret