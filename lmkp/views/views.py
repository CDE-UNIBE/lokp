from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession
from pyramid.security import authenticated_userid
from pyramid.view import view_config

#@view_config(route_name='home', renderer='../templates/mytemplate.pt')
def my_view(request):
# deleted from autocreated
#    one = DBSession.query(MyModel).filter(MyModel.name=='one').first()
#    return {'one':one, 'project':'MyProject'}
    return {'one':'one', 'project':'MyProject'}

@view_config(route_name='db_test', renderer='lmkp:templates/db_test.pt')
def db_test(request):

    activities = []
    for i in DBSession.query(Activity).join(A_Event).join(A_Tag).join(A_Key).filter(A_Key.key == 'Spatial uncertainty'):
        activities.append({'uuid': i.uuid, 'value': i.events[0].tags[0].value.value})


    return {'object': activities}

    #object = DBSession.query(A_Event).get(1)
    #return {'object':object.tags[0].key.language}

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
    """
    Returns the main HTML page
    """
    lang = 'en'
    # Check if the user is logged in
    username = authenticated_userid(request)
    # Assume the user is not logged in per default
    login = False
    if username is not None:
        login = True
    else:
        username = 'unknown user'
    return {'header': 'welcome', 'login': login, 'username': username, 'script': 'main'}

@view_config(route_name='ext_tests', renderer='lmkp:templates/tests.pt')
def ext_tests(request):
    return {}