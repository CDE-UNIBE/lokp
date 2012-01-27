from pyramid.view import view_config

from ..models.meta import (
    DBSession,
    )

from ..models.database_objects import *

#@view_config(route_name='home', renderer='../templates/mytemplate.pt')
def my_view(request):
# deleted from autocreated
#    one = DBSession.query(MyModel).filter(MyModel.name=='one').first()
#    return {'one':one, 'project':'MyProject'}
    return {'one':'one', 'project':'MyProject'}

@view_config(route_name='db_test', renderer='../templates/db_test.pt')
def db_test(request):
    object = DBSession.query(A_Event).first()
    return {'object':object}

@view_config(route_name='geo_test', renderer='geojson')
def geo_test(request):
    return {
            'type': 'Feature',
            'id': 1,
            'geometry': {'type': 'Point', 'coordinates': [53, -4]},
            'properties': {'title': 'Dict 1'}
            }

@view_config(route_name='index', renderer='lmkp:templates/index.pt')
def index(request):
    print request
    lang='en'
    return {'header': 'welcome'}
