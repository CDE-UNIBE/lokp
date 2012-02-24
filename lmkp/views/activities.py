from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session
import logging
from pyramid.view import view_config
import yaml
from lmkp.views.activity_protocol import ActivityProtocol

log = logging.getLogger(__name__)

activity_protocol = ActivityProtocol(Session)

#@view_config(route_name='activities_read_one', renderer='geojson')
@view_config(route_name='activities_read_one', renderer='lmkp:templates/db_test.pt')
def read_one_test(request):

    id = request.matchdict.get('id', None)
    return activity_protocol.read(request, id=id)



def read_one(request):
    """
    Returns an activity.
    """
    try:
        id = int(request.matchdict.get('id', None))
    except ValueError:
        return {}
    
    # Result object
    activityResult = {}

    fields = _get_config_fields()

    # Join table of activities
    activities = Session.query(Activity.id, A_Value.value).join(A_Tag_Group).join(A_Tag).join(A_Key).join(A_Value).filter(Activity.id == id)

    activityResult['id'] = id
    for field in fields:
        activityResult[field] = None

    # Loop all fields and query the corresponding activities
    for field in fields:
        for id, value in activities.filter(A_Key.key == field):
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
            activityResult[field] = value

    # This JSON object is formatted that it can be used from a Ext.form.Panel
    # load method.
    # Reference ExtJS kurz & gut, page 166
    return {'success': True, 'data': activityResult}


def get_activities(request):
    """
    Returns all activities according to the conditions.
    Implements the read functionality (HTTP GET) in the CRUD model
    """
    # Result object
    activitiesResult = []

    fields = _get_config_fields()

    # Join table of activities
    activities = Session.query(Activity.id, A_Value.value).join(A_Event).join(A_Tag).join(A_Key).join(A_Value)

    # It is necessary to create first all activities with empty attribute
    # values. Without doing this empty attributes are skipped in the later
    # database query.
    for (id, value) in activities:
        activity = {}
        activity['id'] = id
        # Append the leaf=True property since we want to use the output *also*
        # in a tree store
        activity['leaf'] = True
        for field in fields:
            activity[field] = None
        activitiesResult.append(activity)

    # Loop all fields and query the corresponding activities
    for field in fields:
        for (id, value) in activities.filter(A_Key.key == field):
            for a in activitiesResult:
                if a['id'] == id:
                    a[field] = value

    #return {'activities': activitiesResult}
    return activitiesResult

@view_config(route_name='activities_read_many', renderer='json')
def read_many(request):
    """
    Alternative implementation
    """
    
    node = request.params.get('node')

    #if node is None or node == 'root':
    #    return {'activities': [{'id': 'pending', 'name': 'Pending activities'}, {'id': 'active', 'name': 'Active activities'}]}
    
    #if node == 'pending' or node == 'active':
    #    return get_activities(request)
    
    result = {}
    result['activitylists'] = []

    pendingActivities = [{'id': 'None', 'name': 'None', 'leaf': True}]
    result['activitylists'].append({'id': 'pending', 'name': 'Pending activities', 'activities': pendingActivities})

    activeActivities = get_activities(request)
    
    result['activitylists'].append({'id': 'active', 'name': 'Active activities', 'activities': activeActivities})

    return result


@view_config(route_name='activities_create', renderer='json')
def create(request):
    """
    Add a new activity.
    Implements the create functionality (HTTP POST) in the CRUD model
    """
    return {}

@view_config(route_name='activities_tree', renderer='lmkp:templates/db_test.pt')
#@view_config(route_name='activities_tree', renderer='json')
def tree(request):

    tree = {}

    tree['activities'] = []

    pendingActivities = []
    for i in Session.query(Activity.id, A_Value.value).join(A_Tag_Group).join(A_Tag).join(A_Key).join(A_Value).filter(A_Key.key == 'name').join(Status).filter(Status.name == 'pending').group_by(Activity.id,A_Value.value).order_by(Activity.id):
        pendingActivities.append({'id': i[0], 'name': i[1], 'leaf': True})

    tree['activities'].append({'id': 'pending', 'name': 'Pending activities', 'activities': pendingActivities})

    activeActivities = []
    for i in Session.query(Activity.id, A_Value.value).join(A_Tag_Group).join(A_Tag).join(A_Key).join(A_Value).filter(A_Key.key == 'name').join(Status).filter(Status.name == 'active').group_by(Activity.id,A_Value.value).order_by(Activity.id):
        activeActivities.append({'id': i[0], 'name': i[1], 'leaf': True})
    
    tree['activities'].append({'id': 'active', 'name': 'Active activities', 'activities': activeActivities})

    return tree

@view_config(route_name='activities_model', renderer='string')
def model(request):
    """
    Controller that returns a dynamically generated JavaScript that builds the
    client-side Activity model. The model is set up based on the defined mandatory
    and optional field in the configuration yaml file.
    """
    object = {}

    object['extend'] = 'Ext.data.Model'
    object['proxy'] = {'type': 'ajax', 'url': '/activities', 'reader': {'type': 'json', 'root': 'activities'}}

    # Get a stream of the config yaml file to extract the fields
    stream = open('lmkp/config.yaml', 'r')

    # Read the config stream
    yamlConfig = yaml.load(stream)

    fields = []
    fieldsConfig = yamlConfig['application']['fields']

    # First process the mandatory fields
    for (name, config) in fieldsConfig['mandatory'].iteritems():
        fields.append(_get_extjs_config(name, config))
    # Then process also the optional fields
    for (name, config) in fieldsConfig['optional'].iteritems():
        fields.append(_get_extjs_config(name, config))

    fields.append({'name': 'id', 'type': 'string'})

    object['fields'] = fields

    return "Ext.define('DyLmkp.model.Activity', %s);" % object

def _get_extjs_config(name, config):

    fieldConfig = {}
    fieldConfig['name'] = name

    type = 'string'
    if config['type'] == 'Number':
        type = 'number'
    if config['type'] == 'Date':
        type = 'number'

    fieldConfig['type'] = type

    return fieldConfig

def _get_config_fields():
    """
    Return a list of mandatory and optional fields extracted from the application
    configuration file (yaml)
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

    return fields
