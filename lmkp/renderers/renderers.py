from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session
from lmkp.views.activity_protocol import ActivityFeature
from logging import getLogger
from lxml import etree
from pykml.factory import KML_ElementMaker as kml
from pykml.parser import Schema
from pyramid.i18n import get_localizer
from shapely import wkb
import simplejson as json
from sqlalchemy.sql.expression import and_
from uuid import UUID

log = getLogger(__name__)

def translate_key(request, localizer, key):
    # Get the language independent key id
    try:
        key_id = Session.query(A_Key.id).filter(A_Key.key == key).first()[0]
    except TypeError:
        return key

    # Create the filter
    f = and_(A_Key.fk_a_key == key_id, Language.locale == localizer.locale_name)
    # And query the translated key
    translated_key = Session.query(A_Key.key).join(Language).filter(f).first()

    try:
        return translated_key[0]
    except TypeError:
        return key

def translate_value(request, localizer, value):
    # Get the language independent value id
    print "**************************************"
    print value
    try:
        value_id = Session.query(A_Value.id).filter(A_Value.value == value).first()[0]
    except TypeError:
        return value

    # Create the filter
    f = and_(A_Value.fk_a_value == value_id, Language.locale == localizer.locale_name)
    # And query the translated value
    translated_value = Session.query(A_Value.value).join(Language).filter(f).first()

    try:
        return translated_value[0]
    except TypeError:
        return value

class ExtJSTree(object):
    """
    A renderer that returns a ExtJS tree configuration JSON from a GeoJSON
    feature or featurecollection.
    """

    def __call__(self, info):

        def _render(value, system, parent=None):

            if parent is None:
                parent = []

            for i in value:
                try:
                    if i.__tree_interface__['children'] is not None:
                        children = []

                        _render(i.__tree_interface__['children'], system, children)
                        parent.append({
                                      'id': i.__tree_interface__['id'],
                                      'Name': i.__tree_interface__['name'],
                                      'children': children
                                      })
                except KeyError:
                    pass
                try:
                    if i.__tree_interface__['leaf'] is True:
                        parent.append(i.__tree_interface__)
                except KeyError:
                    pass

            # Get the request and set the response content type to JSON
            request = system.get('request')
            if request is not None:
                response = request.response
                response.content_type = 'application/json'

            return json.dumps({'children': parent})

        return _render

class JsonRenderer(object):
    """
    UUID compatible JSON renderer
    """

    def __call__(self, info):

        def _render(value, system):
            
            # Get the request and set the response content type to JSON
            request = system.get('request')
            if request is not None:
                response = request.response
                response.content_type = 'application/json'

            # Get the localizer from the request
            localizer = get_localizer(request)

            class ActivityFeatureEncoder(json.JSONEncoder):
                """
                A JSON encoder to encode Activity Features
                """

                def default(self, obj):
                    
                    feature = {}
                    for d in obj.__dict__:

                        # Translate the key
                        key = translate_key(request, localizer, d)

                        if obj.__dict__[d] is None:
                            continue

                        # Cast the attribute values.
                        # It is important to check first if it's an global unique
                        # id, else the uuid is casted to integer.
                        if isinstance(obj.__dict__[d], UUID):
                            feature[key] = str(obj.__dict__[d])
                        else:
                            # First try if it's possible to cast the value to integer
                            try:
                                feature[key] = int(obj.__dict__[d])
                            except:
                                # As next we try to cast it to float
                                try:
                                    feature[key] = float(obj.__dict__[d])
                                except:
                                    try:
                                        # Finally the value is casted to unicode and translated
                                        # according to the language in the request
                                        feature[key] = translate_value(request, localizer, unicode(obj.__dict__[d]))
                                    except:
                                        pass
                                    
                    # append constructed name if feature has no name
                    #if "Name" not in feature:
                    #    feature["Name"] = "Activity " + str(feature["id"])
                    return feature



            return json.dumps(value, cls=ActivityFeatureEncoder)

        return _render

class JavaScriptRenderer(object):
    def __call__(self, info):

        def _render(value, system):

            # Get the request and set the response content type to JSON
            request = system.get('request')
            if request is not None:
                response = request.response
                response.content_type = 'application/javascript'

            return value

        return _render

class KmlRenderer(object):

    def __call__(self, info):

        def _make_placemark(feature):
            """
            Make a new placemark and return it
            """

            # Load the coordinates
            coords = wkb.loads(str(feature.geometry.geom_wkb)).coords[0]

            # Create the extended data
            extendedData = kml.ExtendedData()

            try:
                name = getattr(feature, "name")
                if name is None:
                    name = "Activity %s" % feature.id
            except:
                name = "Activity %s" % feature.id

            # Append all attributes
            for key in feature.__dict__:
                if feature.__dict__[key] is not None:
                    try:
                        extendedData.append(kml.Data(kml.value(feature.__dict__[key]), name=key))
                    except TypeError:
                        pass
                    
            point = kml.Point(kml.coordinates('{lon},{lat}'.format(lon=coords[0], lat=coords[1])))

            return kml.Placemark(kml.name(name), kml.styleUrl('#activity'), extendedData, point)


        def _render(value, system):
            """
            
            """

            schema_ogc = Schema("ogckml22.xsd")

            schema_gx = Schema("kml22gx.xsd")

            # Create a document element with a single icon style

            style = kml.Style(kml.IconStyle(kml.scale(2), kml.Icon(kml.href("http://maps.google.com/mapfiles/kml/paddle/L.png"))))

            kmlobj = kml.kml(kml.Document(style, id="activity"))

            if isinstance(value, ActivityFeature):
                kmlobj.Document.append(_make_placemark(value))
            else:
                # For each each ActivityFeature add a placemark to the Document element
                for v in value:
                    kmlobj.Document.append(_make_placemark(v))

            # Get the request and set the response content type to JSON
            request = system.get('request')
            if request is not None:
                response = request.response
                response.content_type = 'text/xml'
                #response.content_type = 'application/vnd.google-earth.kml+xml'

            # Make sure the KML is valid
            schema_ogc.assertValid(kmlobj)

            # Debugging messages
            log.debug("KML document is OGC valid: %s" % schema_ogc.validate(kmlobj))
            log.debug("KML document is GX valid: %s" % schema_gx.validate(kmlobj))

            return etree.tostring(etree.ElementTree(kmlobj), pretty_print=True)

        return _render
