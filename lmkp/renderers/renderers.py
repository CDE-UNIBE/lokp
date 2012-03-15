from lmkp.views.activity_protocol import ActivityFeature
from logging import getLogger
import simplejson as json

log = getLogger(__name__)

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
                                      'name': i.__tree_interface__['Name'],
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

class ExtJSGrid(object):

    def __call__(self, info):

        def _render(value, system):

            class ActivityFeatureEncoder(json.JSONEncoder):

                def default(self, obj):
                    
                    feature = {}
                    for d in obj.__dict__:
                        if obj.__dict__[d] is None:
                            continue
                        try:
                            feature[d] = int(obj.__dict__[d])
                        except:
                            try:
                                feature[d] = float(obj.__dict__[d])
                            except:
                                try:
                                    feature[d] = unicode(obj.__dict__[d])
                                except:
                                    pass
                    # append constructed name if feature has no name
                    if "Name" not in feature:
                        feature["Name"] = "Activity " + str(feature["id"])
                    return feature

            # Get the request and set the response content type to JSON
            request = system.get('request')
            if request is not None:
                response = request.response
                response.content_type = 'application/json'

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

