from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session
from lmkp.views.activity_protocol import ActivityProtocol
import logging
from pyramid.view import view_config
import yaml

log = logging.getLogger(__name__)

activity_protocol = ActivityProtocol(Session)

# Not yet very nice.
# This hashmap has to be translatable using an external
# translation file or database.
statusMap = {
'active': 'Active Activities',
'overwritten': 'Overwritten Activities',
'pending': 'Pending Activities'
}

def get_status(request):
    """
    Returns a list of requested and valid status
    """

    # Get the status parameter if set, else active per default
    requestedStatus = request.params.get('status', ['active'])
    try:
        status = requestedStatus.split(',')
    except AttributeError:
        status = requestedStatus

    # Make sure that all status elements are in the statusMap. If not, remote it
    for s in status:
        if s not in statusMap:
            status.remove(s)

    # Return a list of valid status
    return status
    

@view_config(route_name='activities_read_one', renderer='geojson')
def read_one(request):
    """
    Returns the feature with the requested id
    """
    id = request.matchdict.get('id', None)
    return activity_protocol.read(request, filter=(Status.name == 'active'), id=id)

@view_config(route_name='activities_read_many', renderer='geojson')
def read_many(request):
    """
    Reads many active activities
    """
    return activity_protocol.read(request, filter=(Status.name == 'active'))

@view_config(route_name='activities_count', renderer='string')
def count(request):
    """
    Count activities
    """
    return activity_protocol.count(request, filter=(Status.name == 'active'))


@view_config(route_name='activities_create', renderer='json')
def create(request):
    """
    Add a new activity.
    Implements the create functionality (HTTP POST) in the CRUD model
    """
    return {}

@view_config(route_name='activities_tree', renderer='extjstree')
def tree(request):
    """
    Returns a ExtJS tree configuration of requested activities. Geographical
    and attribute filter are applied!
    """

    class ActivityFolder(object):
        """
        Define a new class instead of a named tuple, see also comments of
        this post:
        http://pysnippet.blogspot.com/2010/01/named-tuple.html
        The attribute columns id and geometry are reserved and mandatory.
        """

        def __init__(self, ** kwargs):
            self.__dict__.update(kwargs)

        @property
        def __tree_interface__(self):
            return {
            'id': self.__dict__['id'],
            'name': self.__dict__['name'],
            'children': self.__dict__['children']
            }

    status = get_status(request)
    if len(status) == 0:
        return []
    elif len(status) == 1:
        return activity_protocol.read(request, filter=(Status.name == status[0]))
    else:
        result = []
        for s in status:
            a = ActivityFolder(
                               id=s,
                               name=statusMap[s],
                               children=activity_protocol.read(request, filter=(Status.name == s))
                               )
            result.append(a)
        return result


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
