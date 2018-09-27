import geojson
from geoalchemy2.shape import to_shape


def geometry_as_geojson(geometry):
    try:
        feature = geojson.Feature(geometry=to_shape(geometry))
        return feature['geometry']
    except:
        return None
