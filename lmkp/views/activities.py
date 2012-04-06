from lmkp.config import config_file_path
from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session
from lmkp.views.activity_protocol import ActivityProtocol
import logging
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.security import ACLAllowed
from pyramid.security import authenticated_userid
from pyramid.security import has_permission
from pyramid.url import route_url
from pyramid.view import view_config
from sqlalchemy.sql.expression import or_, and_
import yaml


log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

activity_protocol = ActivityProtocol(Session)

# Translatable hashmap with all possible activity status
statusMap = {
'active': _('Active Activities', default='Active Activities'),
'overwritten': _('Overwritten Activities', default='Overwritten Activities'),
'pending': _('Pending Activities', default='Pending Activities'),
'deleted': _('Deleted Activities', default='Deleted Activities'),
'rejected': _('Rejected Activities', default='Rejected Activities')
}

def get_status(request):
    """
    Returns a list of requested and valid status
    """

    # Set the default status
    defaultStatus = ['active']

    # Get the status parameter if set, else active per default
    requestedStatus = request.params.get('status', defaultStatus)
    try:
        status = requestedStatus.split(',')
    except AttributeError:
        status = requestedStatus

    # Make sure that all status elements are in the statusMap. If not, remove it
    for s in status:
        if s not in statusMap:
            status.remove(s)

    # Make sure that not an empty status is returned
    if len(status) == 0:
        status = defaultStatus

    # Return a list of valid status
    return status

def get_status_filter(request):
    status = get_status(request)
    if len(status) == 0:
        return None
    elif len(status) == 1:
        return (Status.name == status[0])
    else:
        filters = []
        for s in status:
            filters.append((Status.name == s))
        return or_(* filters)

def get_timestamp(request):
    """
    Gets the timestamp from the request url and returns it
    """
    pass

@view_config(route_name='activities_read_one', renderer='geojson')
def read_one(request):
    """
    Returns the feature with the requested id
    """
    uid = request.matchdict.get('uid', None)
    return activity_protocol.read(request, filter=get_status_filter(request), uid=uid)

#@view_config(route_name='activities_read_one', renderer='lmkp:templates/table.mak')
def read_one_html(request):
    """
    Returns the feature with the requested id
    """
    uid = request.matchdict.get('uid', None)
    return { 'result': [activity_protocol.read(request, filter=get_status_filter(request), uid=uid)]}

@view_config(route_name='activities_read_many', renderer='geojson')
def read_many(request):
    """
    Reads many active activities
    """

    log.debug(get_status_filter(request))

    return activity_protocol.read(request, filter=get_status_filter(request))

@view_config(route_name='activities_read_one_json', renderer='json')
def read_one_json(request):
    """
    Returns the feature with the requested id
    """
    id = request.matchdict.get('id', None)
    return {
        'success': True,
        'data': activity_protocol.read(request, filter=get_status_filter(request), id=id)
    }

@view_config(route_name='activities_read_many_json', renderer='json')
def read_many_json(request):
    """
    Reads many activities
    """

    return {
        'data': activity_protocol.read(request, filter=get_status_filter(request)),
        'success': True,
        'total': activity_protocol.count(request, filter=get_status_filter(request))
    }


@view_config(route_name='activities_read_many_html', renderer='lmkp:templates/table.mak')
def read_many_html(request):

    return {'result': activity_protocol.read(request, filter=get_status_filter(request))}

@view_config(route_name='activities_read_many_kml', renderer='kml')
def read_many_kml(request):

    return activity_protocol.read(request, filter=get_status_filter(request))


@view_config(route_name='activities_count', renderer='string')
def count(request):
    """
    Count activities
    """
    return activity_protocol.count(request, filter=get_status_filter(request))


@view_config(route_name='activities_create', renderer='json')
def create(request):
    """
    Add a new activity.
    Implements the create functionality (HTTP POST) in the CRUD model

    Test the POST request e.g. with
    curl --data @line.json http://localhost:6543/activities

    """

    # Check if the user is logged in and he/she has sufficient user rights
    userid = authenticated_userid(request)
    if userid is None:
        return HTTPForbidden()
    if not isinstance(has_permission('edit', request.context, request), ACLAllowed):
        return HTTPForbidden()

    return activity_protocol.create(request)

@view_config(route_name='activities_tree', renderer='tree')
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

    localizer = get_localizer(request)

    status = get_status(request)
    if len(status) <= 1:
        return activity_protocol.read(request, filter=get_status_filter(request))
    else:
        result = []
        for s in status:
            a = ActivityFolder(
                               id=s,
                               name=localizer.translate(statusMap[s]),
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
    object['proxy'] = {'type': 'ajax', 'url': '/activities', 'reader': {'type': 'json', 'root': 'children'}}

    # Get a stream of the config yaml file to extract the fields
    stream = open(config_file_path(), 'r')

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


@view_config(route_name='rss_feed', renderer='lmkp:templates/rss.mak')
def read_many_rss(request):
    status = "active"

    if 'status' in request.matchdict:
        status = request.matchdict['status']
        
    if 'order_by' not in request.params or 'dir' not in request.params:
        return HTTPFound(route_url('rss_feed', request, status=status, _query={'order_by': 'timestamp', 'dir': 'desc'}))

    return {'data' : activity_protocol.read(request, filter=(Status.name == status))}

#@view_config(route_name='activities_history', renderer='lmkp:templates/activity_history.mak')
@view_config(route_name='activities_history', renderer='json')
def activities_history(request):
    uid = request.matchdict.get('uid', None)

    # The ActivityProtocol does not perform filter operations when UUID is passed as a parameter.
    # As a workaround, UUID is passed as a filter.
    overwrittenfilter = []
    overwrittenfilter.append((Status.name == 'overwritten'))
    overwrittenfilter.append((Activity.activity_identifier == uid))
    
    # Query the active and overwritten activities based on the given UUID.
    active = activity_protocol.read(request, filter=(Status.name == 'active'), uid=uid)
    activeCount = 1
    overwritten = activity_protocol.read(request, filter=and_(* overwrittenfilter))
    
    # If there is no active activity, the ActivityProtocol returns a HTTPNotFound object.
    # This object cannot be processed by the json renderer because it has no ID (required to build name)
    # Therefore, the object explicitly needs to be set to None.
    if isinstance(active, HTTPNotFound):
        active = None
        activeCount = 0
    else:
        # append changeset details
        active = _history_get_changeset_details(active)

    for o in overwritten:
        # append changeset details
        o = _history_get_changeset_details(o)

    return {
        'data': {
            'active': active,
            'overwritten': overwritten
        },
        'success': True,
        'total': len(overwritten) + activeCount
    }

def _history_get_changeset_details(object):
    """
    Appends details from Changeset of an ActivityProtocol object based on the ID of the activity
    and returns this object. 
    """
    if object.id is not None:
        changeset = Session.query(A_Changeset).filter(A_Changeset.fk_activity == object.id).first()
        object.userid = changeset.user.id
        object.username = changeset.user.username
        object.source = changeset.source
        return object


def _get_extjs_config(name, config):

    fieldConfig = {}
    fieldConfig['Name'] = name

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
    stream = open(config_file_path(), 'r')

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

@view_config(route_name='timestamp_test', renderer="lmkp:templates/table.mak")
def timestamp_test(request):
    query = activity_protocol._query_timestamp(request)

    #return {'query': query.all()}
    return {'result': query.all(), 'nbr': len(query.all())}
    
