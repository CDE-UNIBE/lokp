from geojson import *
from lmkp.models.database_objects import *
import logging

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

        # Get the feature id and the geometry
        id = feature[0].id
        geometry = wkb.loads(str(feature[0].geometry.geom_wkb))

        # Get the requested attributes from the query
        if 'attrs' in request.params:
            attrs = request.params['attrs'].split(',')

        # Loop all key and value pairs and add the requested attributes. If
        # attrs is not present in the request, add all attributes.
        properties = {}
        for f in feature:
            try:
                if f.key in attrs:
                    properties[f.key] = f.value;
            except:
                properties[f.key] = f.value;

        # Check if the geometry is requested or not
        if asbool(request.params.get('no_geom', False)):
            geometry = None

        # Return a new feature
        return geojson.Feature(id=id, geometry=geometry, properties=properties)

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
        if filter is None:
            filter = create_filter(request, self.mapped_class, self.geom_attr)
        query = self.Session.query(Activity.point.label("geometry"), Activity.id.label("id"), Activity.activity_identifier, A_Key.key.label("key"), A_Value.value.label("value"))
        #query = self.Session().query(self.mapped_class).filter(filter)
        order_by = self._get_order_by(request)
        if order_by is not None:
            query = query.order_by(order_by)
        query = query.limit(limit).offset(offset)
        return query.all()

    def read(self, request, filter=None, id=None):
        """
        Build a query based on the filter or the idenfier, send the query
        to the database, and return a Feature or a FeatureCollection.
        """
        ret = None
        if id is not None:
            #o = self.Session().query(self.mapped_class).get(id)

            table = self.Session.query(Activity.point.label("geometry"), Activity.id.label("id"), Activity.activity_identifier, A_Key.key.label("key"), A_Value.value.label("value"))

            o = table.filter(Activity.id == id).join(A_Tag_Group).join(A_Tag).join(A_Key).join(A_Value).join(Status).filter(Status.name == 'active').group_by(Activity.id, A_Key.key, A_Value.value).order_by(Activity.id)

            if o is None:
                return HTTPNotFound()
            # FIXME: we return a Feature here, not a mapped object, do
            # we really want that?
            ret = self._filter_attrs(o, request)
        else:
            objs = self._query(request, filter)

            for o in objs:
                log.info(o)

            #ret = FeatureCollection([self._filter_attrs(o.__geo_interface__, request) for o in objs if o is not None])
        return ret