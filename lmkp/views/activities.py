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

from lmkp.config import config_file_path
from lmkp.config import locale_config_file_path

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
    uid = request.matchdict.get('uid', None)
    return {
        'success': True,
        'data': activity_protocol.read(request, filter=get_status_filter(request), uid=uid)
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


@view_config(route_name='activities_read_one_html', renderer='lmkp:templates/table.mak')
def read_one_html(request):
    """
    Returns the feature with the requested id
    """
    uid = request.matchdict.get('uid', None)
    return {'result': [activity_protocol.read(request, filter=get_status_filter(request), uid=uid)]}


@view_config(route_name='activities_read_many_html', renderer='lmkp:templates/table.mak')
def read_many_html(request):

    return {'result': activity_protocol.read(request, filter=get_status_filter(request))}


@view_config(route_name='activities_read_one_kml', renderer='kml')
def read_one_kml(request):

    uid = request.matchdict.get('uid', None)
    return activity_protocol.read(request, filter=get_status_filter(request), uid=uid)


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
    def _merge_config(parent_key, global_config, locale_config):
        """
        Merges two configuration dictionaries together
        """

        try:
            for key, value in locale_config.items():
                try:
                    # If the value has items it's a dict, if not raise an error
                    value.items()
                    # Do not overwrite mandatory or optional keys in the global
                    # config. If the key is not in the global config, append it
                    # to the configuration
                    if parent_key == 'mandatory' or parent_key == 'optional':
                        if key not in global_config:
                            _merge_config(key, global_config[key], locale_config[key])
                        # else if the key is in global_config do nothing
                    else:
                        _merge_config(key, global_config[key], locale_config[key])
                except:
                    global_config[key] = locale_config[key]
        # Handle the AttributeError if the locale config file is empty
        except AttributeError:
            pass
    
    object = {}

    object['extend'] = 'Ext.data.Model'
    object['proxy'] = {'type': 'ajax', 'url': '/activities', 'reader': {'type': 'json', 'root': 'children'}}

    # Get a stream of the config yaml file to extract the fields
    stream = open(config_file_path(), 'r')

    # Read the global configuration file
    global_stream = open(config_file_path(request), 'r')
    global_config = yaml.load(global_stream)

    # Read the localized configuration file
    try:
        locale_stream = open(locale_config_file_path(request), 'r')
        locale_config = yaml.load(locale_stream)

        # If there is a localized config file then merge it with the global one
        _merge_config(None, global_config, locale_config)

    except IOError:
        # No localized configuration file found!
        pass


    fields = []
    fieldsConfig = global_config['application']['fields']

    # language is needed because fields are to be displayed translated
    localizer = get_localizer(request)
    lang = Session.query(Language).filter(Language.locale == localizer.locale_name).first()
    if lang is None:
        lang = Language(1, 'English', 'English', 'en')

    # First process the mandatory fields
    for (name, config) in fieldsConfig['mandatory'].iteritems():
        fields.append(_get_extjs_config(name, config, lang))
    # Then process also the optional fields
    for (name, config) in fieldsConfig['optional'].iteritems():
        fields.append(_get_extjs_config(name, config, lang))

    fields.append({'name': 'id', 'type': 'string'})

    object['fields'] = fields

    return "Ext.define('Lmkp.model.Activity', %s);" % object


@view_config(route_name='rss_feed', renderer='lmkp:templates/rss.mak')
def read_many_rss(request):
    status = "active"

    if 'status' in request.matchdict:
        status = request.matchdict['status']
        
    if 'order_by' not in request.params or 'dir' not in request.params:
        return HTTPFound(route_url('rss_feed', request, status=status, _query={'order_by': 'timestamp', 'dir': 'desc'}))

    return {'data': activity_protocol.read(request, filter=(Status.name == status))}

@view_config(route_name='activities_history', renderer='json')
def activities_history(request):
    uid = request.matchdict.get('uid', None)

    # The ActivityProtocol does not perform filter operations when UUID is passed as a parameter.
    # As a workaround, UUID is passed as a filter.
    overwrittenfilter = []
    overwrittenfilter.append((Status.name == 'overwritten'))
    overwrittenfilter.append((Activity.activity_identifier == uid))
    deletedfilter = []
    deletedfilter.append((Status.name == 'deleted'))
    deletedfilter.append((Activity.activity_identifier == uid))
    
    # Query the active and overwritten activities based on the given UUID.
    active = activity_protocol.read(request, filter=(Status.name == 'active'), uid=uid)
    activeCount = 1
    overwritten = activity_protocol.read(request, filter=and_(* overwrittenfilter))
    deleted = activity_protocol.read(request, filter=and_(* deletedfilter))
    
    # If there is no active activity, the ActivityProtocol returns a HTTPNotFound object.
    # This object cannot be processed by the json renderer because it has no ID (required to build name)
    # Therefore, the object explicitly needs to be set to None.
    if isinstance(active, HTTPNotFound):
        active = None
        activeCount = 0
    else:
        # append changeset details
        active = _history_get_changeset_details(active)

    # if there are no overwritten versions
    if len(overwritten) == 0:
        active = _check_difference(active, None)
        
    # Sort overwritten activities by their timestamp
    try:
        overwritten = sorted(overwritten, key=lambda overwritten:overwritten.timestamp, reverse=True)
    except:
        pass

    # process overwritten versions
    for i, o in enumerate(overwritten):
        
        # the first item (latest overwritten version)
        if i == 0:
            # compare with active
            active = _check_difference(active, o)
            # if the first item is not the last as well, ...
            if len(overwritten) > 1:
                # ... compare it with its previous version
                o = _check_difference(o, overwritten[i+1])
            # if the first item is also the last, ...
            else:
                # ... there is no previous version to compare it with
                o = _check_difference(o, None)
        
        # the last item (the first version)
        elif i == len(overwritten)-1:
            # there is no previous version to compare it with
            o = _check_difference(o, None)

        # all other cases
        else:
            # compare it with its previous version
            o = _check_difference(o, overwritten[i+1])

        # append changeset details
        o = _history_get_changeset_details(o)

    # process deleted if available
    if len(deleted) > 0:
        deleted = deleted[0] # there should only be one
        # append changeset details
        deleted = _history_get_changeset_details(deleted)
        deletedCount = 1
    else:
        deleted = None
        deletedCount = 0

    return {
        'data': {
            'active': active,
            'overwritten': overwritten,
            'deleted': deleted
        },
        'success': True,
        'total': len(overwritten) + activeCount + deletedCount
    }

def _check_difference(new, old):

    changes = {} # to collect the changes
    
    # not all attributes are of interest when looking at the difference between two versions
    # @todo: geometry needs to be processed differently, not yet implemented
    ignored = ['geometry', 'timestamp', 'id', 'version', 'username', 'userid', 'source', 
                'activity_identifier', 'modified', 'new', 'deleted']
    
    # do comparison based on new version, loop through attributes
    if new is not None:
        for obj in new.__dict__:
            # not all attributes are of interest
            if obj not in ignored:
                # there is no older version (all attributes are new)
                if old is None:
                    # for some reason (?), attribute (although it will be set in later versions)
                    # can already be there (set to None) - we don't want it yet
                    if new.__dict__[obj] is not None:
                        changes[obj] = 'new' # attribute is new
                # there exists an older version
                else:
                    # attribute is not in older version
                    if obj not in old.__dict__:
                        changes[obj] = 'new' # attribute is new
                    # attribute is already in older version
                    else:
                        # for some reason (?), attribute can already be there in older versions 
                        # (set to None). this should be treated as if attribute was not there yet
                        if old.__dict__[obj] is None and new.__dict__[obj] is not None:
                            changes[obj] = 'new' # attribute is 'new'
                        # check if attribute is the same in both versions
                        elif new.__dict__[obj] != old.__dict__[obj]:
                            changes[obj] = 'modified' # attribute was modified
    
    # do comparison based on old version
    if old is not None:
        # loop through attributes
        for obj in old.__dict__:
            if obj not in ignored and new is not None:
                # check if attribute is not there anymore in new version
                if obj not in new.__dict__:
                    changes[obj] = 'deleted' # attribute was deleted
    
    if new is not None: # when deleted
        new.changes = changes
    return new

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


def _get_extjs_config(name, config, language):

    fieldConfig = {}
    
    # check if translated name is available
    originalKey = Session.query(A_Key.id).filter(A_Key.key == name).filter(A_Key.fk_a_key == None).first()
    translatedName = Session.query(A_Key).filter(A_Key.fk_a_key == originalKey).filter(A_Key.language == language).first()
    
    if translatedName:
        fieldConfig['name'] = str(translatedName.key)
    else:
        fieldConfig['name'] = name

    type = 'string'
    try:
        config['type']
        if config['type'] == 'Number':
            type = 'number'
        if config['type'] == 'Date':
            type = 'number'
    except KeyError:
        pass

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
    
