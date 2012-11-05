from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session
from lmkp.views.activity_protocol2 import ActivityProtocol2
from lmkp.views.activity_protocol3 import ActivityProtocol3
from lmkp.views.config import get_mandatory_keys
import logging
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPCreated
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.renderers import render_to_response
from pyramid.security import ACLAllowed
from pyramid.security import authenticated_userid
from pyramid.security import effective_principals
from pyramid.security import has_permission
from pyramid.url import route_url
from pyramid.view import view_config
from sqlalchemy.sql.expression import or_, and_
import yaml
import simplejson as json

from lmkp.renderers.renderers import translate_key

log = logging.getLogger(__name__)

#_ = TranslationStringFactory('lmkp')

activity_protocol2 = ActivityProtocol2(Session)
activity_protocol3 = ActivityProtocol3(Session)

def get_timestamp(request):
    """
    Gets the timestamp from the request url and returns it
    """
    pass

@view_config(route_name='activities_read_many')
def read_many(request):
    """
    Read many, returns also pending Activities by currently logged in user and
    all pending Activities if logged in as moderator.
    Default output format: JSON
    """
    
    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    if output_format == 'json':
        activities = activity_protocol3.read_many(request, public=False)
        return render_to_response('json', activities, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    elif output_format == 'geojson':
        activities = activity_protocol3.read_many_geojson(request, public=False)
        return render_to_response('json', activities, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='activities_public_read_many')
def read_many_public(request):
    """
    Read many, does not return any pending Activities.
    Default output format: JSON
    """

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    if output_format == 'json':
        activities = activity_protocol3.read_many(request, public=True)
        return render_to_response('json', activities, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    elif output_format == 'geojson':
        activities = activity_protocol3.read_many_geojson(request, public=True)
        return render_to_response('json', activities, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='activities_bystakeholder')
def by_stakeholder(request):
    """
    Read many Activities based on a Stakeholder ID. Also return pending
    Activities by currently logged in user and all pending Activities if logged
    in as moderator.
    Default output format: JSON
    """

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    uid = request.matchdict.get('uid', None)

    if output_format == 'json':
        activities = activity_protocol3.read_many_by_stakeholder(request,
            uid=uid, public=False)
        return render_to_response('json', activities, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='activities_bystakeholder_public')
def by_stakeholder_public(request):
    """
    Read many Activities based on a Stakeholder ID. Do not return any pending
    versions.
    Default output format: JSON
    """

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    uid = request.matchdict.get('uid', None)

    if output_format == 'json':
        activities = activity_protocol3.read_many_by_stakeholder(request,
            uid=uid, public=True)
        return render_to_response('json', activities, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='activities_read_one')
def read_one(request):
    """
    Read one Activity based on ID and return all versions of this Activity. Also
    return pending versions by currently logged in user and all pending versions
    of this Activity if logged in as moderator.
    Default output format: JSON
    """

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    uid = request.matchdict.get('uid', None)

    if output_format == 'json':
        activities = activity_protocol3.read_one(request, uid=uid, public=False)
        return render_to_response('json', activities, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()
   
@view_config(route_name='activities_read_one_public')
def read_one_public(request):
    """
    Read one Activity based on ID and return all versions of this Activity. Do
    not return any pending versions.
    Default output format: JSON
    """

    uid = request.matchdict.get('uid', None)

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    if output_format == 'json':
        activities = activity_protocol3.read_one(request, uid=uid, public=True)
        return render_to_response('json', activities, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='activities_read_one_active')
def read_one_active(request):
    """
    Read one Activity based on ID and return only the active version of the
    Activity.
    Default output format: JSON
    """

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    uid = request.matchdict.get('uid', None)

    if output_format == 'json':
        activities = activity_protocol3.read_one_active(request, uid=uid)
        return render_to_response('json', activities, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='activities_read_pending', renderer='lmkp:templates/rss.mak')
def read_pending(request):
    activities = activity_protocol2.read(request) #, filter={'status_filter': (Status.id==2)})
    return {'data': activities['data']}

@view_config(route_name='activities_review', renderer='json')
def review(request):
    """
    Insert a review decision for a pending Activity
    """

    _ = request.translate
    
    # Check if the user is logged in and he/she has sufficient user rights
    userid = authenticated_userid(request)
    if userid is None:
        raise HTTPUnauthorized(_('User is not logged in.'))
    if not isinstance(has_permission('moderate', request.context, request),
        ACLAllowed):
        raise HTTPUnauthorized(_('User has no permissions to add a review.'))
    user = Session.query(User).\
            filter(User.username == authenticated_userid(request)).first()

    # Check for profile
    profile_filters = activity_protocol2._create_bound_filter_by_user(request)
    if len(profile_filters) == 0:
        raise HTTPBadRequest(_('User has no profile attached'))
    activity = Session.query(Activity).\
        filter(Activity.activity_identifier == request.POST['identifier']).\
        filter(Activity.version == request.POST['version']).\
        filter(or_(* profile_filters)).\
        first()
    if activity is None:
        raise HTTPUnauthorized(_('The Activity was not found or is not situated within the user\'s profiles'))

    # If review decision is 'approved', make sure that all mandatory fields are 
    # there, except if it is to be deleted
    try:
        review_decision = int(request.POST['review_decision'])
    except:
        review_decision = None

    if review_decision == 1: # Approved
        # Only check for mandatory keys if new version is not to be deleted
        # (has no tag groups)
        if len(activity.tag_groups) > 0:
            mandatory_keys = get_mandatory_keys(request, 'a')
            # Query keys
            activity_keys = Session.query(A_Key.key).\
                join(A_Tag).\
                join(A_Tag_Group, A_Tag.fk_tag_group == A_Tag_Group.id).\
                filter(A_Tag_Group.activity == activity)
            keys = []
            for k in activity_keys.all():
                keys.append(k.key)
            for mk in mandatory_keys:
                if mk not in keys:
                    raise HTTPBadRequest(_('Not all mandatory keys are provided'))

    # Also query previous Activity if available
    previous_activity = Session.query(Activity).\
        filter(Activity.activity_identifier == request.POST['identifier']).\
        filter(Activity.version == activity.previous_version).\
        first()

    # The user can add a review
    ret = activity_protocol3._add_review(
        request, activity, previous_activity, Activity, user
    )

    return ret

@view_config(route_name='activities_create', renderer='json')
def create(request):
    """
    Add a new activity.
    Implements the create functionality (HTTP POST) in the CRUD model

    Test the POST request e.g. with
    curl -u "user1:pw" -d @addNewActivity.json -H "Content-Type: application/json" http://localhost:6543/activities

    """

    # Check if the user is logged in and he/she has sufficient user rights
    userid = authenticated_userid(request)

    if userid is None:
        raise HTTPForbidden()
    if not isinstance(has_permission('edit', request.context, request), ACLAllowed):
        raise HTTPForbidden()

    ids = activity_protocol3.create(request)

    response = {}
    response['data'] = [i.to_json() for i in ids]
    response['total'] = len(response['data'])

    request.response.status = 201
    return response

#@view_config(route_name='taggroups_model', renderer='string')
def model(request):
    """
    Controller that returns a dynamically generated JavaScript that builds the
    client-side TagGroup model, which is related (belongsTo / hasMany) to the 
    static Activity model. The model is set up based on the defined mandatory
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
    object['belongsTo'] = 'Lmkp.model.Activity'

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
        o = _get_extjs_config(name, config, lang)
        if o is not None:
            o['mandatory'] = 1
            fields.append(o)
    # Then process also the optional fields
    for (name, config) in fieldsConfig['optional'].iteritems():
        o = _get_extjs_config(name, config, lang)
        if o is not None:
            fields.append(o)

    fields.append({'name': 'id', 'type': 'string'})

    object['fields'] = fields

    return "Ext.define('Lmkp.model.TagGroup', %s);" % object

def _check_difference(new, old, localizer=None):

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
                        changes[str(translate_key(None, localizer, obj))] = 'new' # attribute is new
                # there exists an older version
                else:
                    # attribute is not in older version
                    if obj not in old.__dict__:
                        changes[str(translate_key(None, localizer, obj))] = 'new' # attribute is new
                    # attribute is already in older version
                    else:
                        # for some reason (?), attribute can already be there in older versions 
                        # (set to None). this should be treated as if attribute was not there yet
                        if old.__dict__[obj] is None and new.__dict__[obj] is not None:
                            changes[str(translate_key(None, localizer, obj))] = 'new' # attribute is 'new'
                        # check if attribute is the same in both versions
                        elif new.__dict__[obj] != old.__dict__[obj]:
                            changes[str(translate_key(None, localizer, obj))] = 'modified' # attribute was modified
    
    # do comparison based on old version
    if old is not None:
        # loop through attributes
        for obj in old.__dict__:
            if obj not in ignored and new is not None:
                # check if attribute is not there anymore in new version
                if obj not in new.__dict__:
                    changes[str(translate_key(None, localizer, obj))] = 'deleted' # attribute was deleted
    
    if new is not None: # when deleted
        new.changes = changes
    return new

#def _history_get_changeset_details(object):
#    """
#    Appends details from Changeset of an ActivityProtocol object based on the ID of the activity
#    and returns this object.
#    """
#    if object.id is not None:
#        changeset = Session.query(A_Changeset).filter(A_Changeset.fk_activity == object.id).first()
#        object.userid = changeset.user.id
#        object.username = changeset.user.username
#        object.source = changeset.source
#        return object


def _get_extjs_config(name, config, language):

    fieldConfig = {}
    
    # check if translated name is available
    originalKey = Session.query(A_Key.id).filter(A_Key.key == name).filter(A_Key.fk_a_key == None).first()
    
    # if no original value is found in DB, return None (this cannot be selected)
    if not originalKey:
        return None
    
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
