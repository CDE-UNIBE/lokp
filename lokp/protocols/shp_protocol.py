import shapefile
from pyramid.view import view_config
from pyramid.response import Response

'''
This handler is called from customMapMapping.mak in order to extract coordinates from a shapefile. An ajax call is required
to access the coordinates from the .mak file.

The request handled by this method requires a zipped shapefile (as base64!) for input. The shapefile's coordinates are returned as json.
'''
@view_config(
    route_name='shp_upload', renderer='json') # json renderer allows to return json object
def get_coordinates_from_shp(request):
    print('response_shp_protocol')
    ## try: copy-paste existing file upload? - user must select dbf, shp and prj?

    ## 2 issues: unzip zipfile? Get zipfile to ajax request

    ## read shapefile from zip
    ## -https://gis.stackexchange.com/questions/250092/using-pyshp-to-read-a-file-like-object-from-a-zipped-archive

    ## read coordinates from shapefile

    coordinates_json = {
        'xCoord': 10,
        'yCoord': 20
    }
    return coordinates_json

