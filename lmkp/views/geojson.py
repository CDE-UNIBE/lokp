from lmkp.models.database_objects import *
import logging
from pyramid.view import view_config


log = logging.getLogger(__name__)

@view_config(route_name='geojson_test', renderer='json')
def read_geojson(request):

    result = {}
    result['type'] = 'FeatureCollection'
    result['features'] = []
    result['features'].append({"type": "Feature", "geometry": {"type": "Point",
                              "coordinates": [102.0, 19.0]},
                              "properties": {"name": "testname", "area": 849, "pop": 300},
                              "id": 102})
    result['features'].append({"type": "Feature", "geometry": {"type": "Point",
                              "coordinates": [102.5, 18.2]},
                              "properties": {"name": "Some name", "area": 774, "pop": 100},
                              "id": 104})

    return result