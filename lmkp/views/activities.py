from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session
import logging
from pyramid.view import view_config
import yaml

log = logging.getLogger(__name__)

@view_config(route_name='get_activities', renderer='json')
def get_activities(request):
    """
    Returns all activities according to the conditions.
    Implements the read functionality (HTTP GET) in the CRUD model
    """

    # Get a stream of the config yaml file to extract the fields
    stream = open('lmkp/config.yaml', 'r')

    # Read the config stream
    yamlConfig = yaml.load(stream)

    # Get all (mandatory and optional) fields
    yamlFields = yamlConfig['application']['fields']

    # New list that holds the fields
    fields = []

    # First process the mandatory fields
    for name in yamlFields['mandatory']:
        fields.append(name)
    # Then process also the optional fields
    for name in yamlFields['optional']:
        fields.append(name)

    log.info(fields)

    # Result object
    activitiesResult = []

    # It is necessary to create first all activities with empty attribute
    # values. Without doing this empty attributes are skipped in the later
    # database query.

    index = 0

    for identifier in Session.query(Activity.id).order_by(Activity.id):
        id = identifier[0]
        activitiesResult.append({})
        activitiesResult[index]['id'] = id
        for field in fields:
            activitiesResult[index][field] = None

        index += 1

    # Join table of activities
    activities = Session.query(Activity).join(A_Event).join(A_Tag).join(A_Key)

    # Loop all fields and append

    

    for field in fields:
        index = 0
        for i in activities.filter(A_Key.key == field).order_by(Activity.id):
            #activitiesResult[i.id][field] = i.events[0].tags[0].value.value
            activitiesResult[index][field] = i.events[0].tags[0].value.value
            index += 1

    return {'activities': activitiesResult}

@view_config(route_name='add_activity', renderer='json')
def add_activitiy(request):
    """
    Add a new activity.
    Implements the create functionality (HTTP POST) in the CRUD model
    """
    return {}

@view_config(route_name='activities_tree', renderer='json')
def get_activities_tree(request):
    """
    Returns a ExtJS tree store configuration object
    """

    nameField = 'Spatial uncertainty'

    result = {}
    result['children'] = []

    # Join table of activities
    activities = Session.query(Activity).join(A_Event).join(A_Tag).join(A_Key)

    # Loop all fields and append
    for i in activities.filter(A_Key.key == nameField).order_by(Activity.id):
        result['children'].append({'id': i.id, 'text': i.events[0].tags[0].value.value, 'leaf': True, 'checked': False})

    return result