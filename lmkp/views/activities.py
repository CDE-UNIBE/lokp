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

    return {'activities': activitiesResult}

@view_config(route_name='add_activity', renderer='json')
def add_activity(request):
    """
    Add a new activity.
    Implements the create functionality (HTTP POST) in the CRUD model
    """
    return {}

@view_config(route_name='activity_model', renderer='string')
def activity_model(request):

    object = {}

    object['extend'] = 'Ext.data.Model'
    object['idProperty'] = 'id'
    object['leaf'] = 'true'
    object['proxy'] = {'type': 'ajax', 'url': '/activities/read', 'reader': { 'type': 'json', 'root': 'activities' }}

    # Get a stream of the config yaml file to extract the fields
    stream = open('lmkp/config.yaml', 'r')

    # Read the config stream
    yamlConfig = yaml.load(stream)

    fields = []
    fieldsConfig = yamlConfig['application']['fields']

    # First process the mandatory fields
    for (name, config) in fieldsConfig['mandatory'].iteritems():
        fields.append(_get_field_config(name, config))
    # Then process also the optional fields
    for (name, config) in fieldsConfig['optional'].iteritems():
        fields.append(_get_field_config(name, config))

    object['fields'] = fields

    return "Ext.define('DyLmkp.model.Activity', %s);" % object

def _get_field_config(name, config):

    fieldConfig = {}
    fieldConfig['name'] = name

    type = 'string'
    if config['type'] == 'Number':
        type = 'number'
    if config['type'] == 'Date':
        type = 'number'

    fieldConfig['type'] = type

    return fieldConfig