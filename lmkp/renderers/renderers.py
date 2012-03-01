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
                        print "Has children %s" % i.__tree_interface__['children']
                        children = []

                        _render(i.__tree_interface__['children'], system, children)
                        parent.append({
                        'id': i.__tree_interface__['id'],
                        'name': i.__tree_interface__['name'],
                        'children': children
                        })
                except KeyError:
                    pass
                try:
                    if i.__tree_interface__['leaf'] is True:
                        print "Leaf name %s" % i.__tree_interface__['name']
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