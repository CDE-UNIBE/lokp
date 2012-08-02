# To change this template, choose Tools | Templates
# and open the template in the editor.
__author__ = "Adrian Weber, Centre for Development and Environment, University of Bern"
__date__ = "$Jan 20, 2012 10:39:24 AM$"

import geojson
from lmkp.config import locale_profile_directory_path
from lmkp.config import profile_directory_path
from lmkp.models.database_objects import A_Key
from lmkp.models.database_objects import A_Value
from lmkp.models.database_objects import Language
from lmkp.models.database_objects import Profile
from lmkp.models.database_objects import SH_Key
from lmkp.models.database_objects import SH_Value
from lmkp.models.meta import DBSession as Session
from lmkp.views.profile import get_current_profile
import logging
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
import shapely
import simplejson as json
import yaml
from sqlalchemy import func

log = logging.getLogger(__name__)

from pyramid.i18n import get_localizer

# File names in the locale profile directory
APPLICATION_YAML = 'application.yml'
ACTIVITY_YAML = 'activity.yml'
STAKEHOLDER_YAML = 'stakeholder.yml'

def merge_profiles(global_config, locale_config):
    """
    Wrapper to merge a global and local configuration dictionary
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
                    # add indicator that field is from local YAML
                    global_config[key] = {'values': locale_config[key], 'local': True}
        # Handle the AttributeError if the locale config file is empty
        except AttributeError:
            pass

    _merge_config(None, global_config, locale_config)

    return global_config

def get_mandatory_keys(request, item):
    if item == 'a':
        config_yaml = ACTIVITY_YAML
    elif item == 'sh':
        config_yaml = STAKEHOLDER_YAML

    # Read the global configuration file
    global_stream = open("%s/%s" % (profile_directory_path(request), config_yaml), 'r')
    global_config = yaml.load(global_stream)

    if 'fields' not in global_config:
        return None

    fields = global_config['fields']

    keys = []
    if 'mandatory' in fields:
        for (name, config) in fields['mandatory'].iteritems():
            keys.append(name)

    if len(keys) > 0:
        return keys

    return None

def get_current_keys(request, item, profile):
    """
    Returns a list of all keys (original, no translation) of a given profile
    (combined with global profile)
    """

    if item == 'a':
        config_yaml = ACTIVITY_YAML
    elif item == 'sh':
        config_yaml = STAKEHOLDER_YAML

    # Read the global configuration file
    global_stream = open("%s/%s" % (profile_directory_path(request), config_yaml), 'r')
    global_config = yaml.load(global_stream)

    # Read the localized configuration file
    if profile != 'global':
        try:
            locale_stream = open("%s/%s" % (locale_profile_directory_path(request), config_yaml), 'r')
            locale_config = yaml.load(locale_stream)

            # If there is a localized config file then merge it with the global one
            global_config = merge_profiles(global_config, locale_config)

        except IOError:
            # No localized configuration file found!
            pass

    if 'fields' not in global_config:
        return None

    fields = global_config['fields']

    keys = []
    if 'mandatory' in fields:
        for (name, config) in fields['mandatory'].iteritems():
            keys.append(name)
    if 'optional' in fields:
        for (name, config) in fields['optional'].iteritems():
            keys.append(name)

    if len(keys) > 0:
        return keys

    return None

@view_config(route_name='config', renderer='json')
def get_config(request):
    """
    Return the configuration file in lmkp/config.yaml as JSON. Using parameter
    format=ext an ExtJS form fields configuration object is returned based on
    the configuration in config.yaml.
    """

    # Get the requested output format
    parameter = request.matchdict['parameter']

    config_yaml = None
    if parameter.lower() == 'activities':
        config_yaml = ACTIVITY_YAML
        Key = A_Key
        Value = A_Value
    elif parameter.lower() == 'stakeholders':
        config_yaml = STAKEHOLDER_YAML
        Key = SH_Key
        Value = SH_Value
    else:
        raise HTTPNotFound()


    # Read the global configuration file
    global_stream = open("%s/%s" % (profile_directory_path(request), config_yaml), 'r')
    global_config = yaml.load(global_stream)

    # Read the localized configuration file
    try:
        locale_stream = open("%s/%s" % (locale_profile_directory_path(request), config_yaml), 'r')
        locale_config = yaml.load(locale_stream)

        # If there is a localized config file then merge it with the global one
        global_config = merge_profiles(global_config, locale_config)

    except IOError:
        # No localized configuration file found!
        pass

    # Get the configuration file from the YAML file
    extObject = []
    # Do the translation work from custom configuration format to an
    # ExtJS configuration object.
    fields = global_config['fields']

    # language is needed because fields are to be displayed translated
    localizer = get_localizer(request)
    lang = Session.query(Language).filter(Language.locale == localizer.locale_name).first()
    if lang is None:
        lang = Language(1, 'English', 'English', 'en')

    # First process the mandatory fields
    for (name, config) in fields['mandatory'].iteritems():
        o = _get_field_config(Key, Value, name, config, lang, True)
        if o is not None:
            extObject.append(o)
    # Then process also the optional fields
    if 'optional' in fields:
        for (name, config) in fields['optional'].iteritems():
            # Don't do a database query for indicators that values are from local
            # YAML (added during merge_yaml above)
            if name == 'local' or name == 'values':
                pass
            else:
                o = _get_field_config(Key, Value, name, config, lang)
            if o is not None:
                extObject.append(o)
    return extObject


@view_config(route_name='yaml_translate_activities', renderer='json', permission='administer')
def yaml_translate_activities(request):
    """

    """

    # Read the global configuration file
    global_stream = open("%s/%s" % (profile_directory_path(request), ACTIVITY_YAML), 'r')
    global_config = yaml.load(global_stream)

    # Read the localized configuration file
    try:
        locale_stream = open("%s/%s" % (locale_profile_directory_path(request), ACTIVITY_YAML), 'r')
        locale_config = yaml.load(locale_stream)

        # If there is a localized config file then merge it with the global one
        global_config = merge_profiles(global_config, locale_config)

    except IOError:
        # No localized configuration file found!
        pass
    
    return get_translated_keys(request, global_config, A_Key, A_Value)

@view_config(route_name='yaml_translate_stakeholders', renderer='json', permission='administer')
def yaml_translate_stakeholders(request):

    # Read the global configuration file
    global_stream = open("%s/%s" % (profile_directory_path(request), STAKEHOLDER_YAML), 'r')
    global_config = yaml.load(global_stream)

    # Read the localized configuration file
    try:
        locale_stream = open("%s/%s.yml" % (locale_profile_directory_path(request), STAKEHOLDER_YAML), 'r')
        locale_config = yaml.load(locale_stream)

        # If there is a localized config file then merge it with the global one
        global_config = merge_profiles(global_config, locale_config)

    except IOError:
        # No localized configuration file found!
        pass

    return get_translated_keys(request, global_config, SH_Key, SH_Value)

def get_translated_keys(request, global_config, Key, Value):

    # get keys already in database. their fk_a_key must be None (= original)
    db_keys = []
    for db_key in Session.query(Key.key).filter(Key.fk_key == None).all():
        db_keys.append(db_key.key)

    # get values already in database. their fk_a_value must be None (= original)
    db_values = []
    for db_value in Session.query(Value.value).filter(Value.fk_value == None).all():
        db_values.append(db_value.value)

    extObject = []
    # Do the translation work from custom configuration format to an
    # ExtJS configuration object.
    fields = global_config['fields']

    localizer = get_localizer(request)
    
    lang = Session.query(Language).filter(Language.locale == localizer.locale_name).first()
    
    if lang is None:
        lang = Language(1, 'English', 'English', 'en')
    #lang = Session.query(Language).get(2)
    
    # First process the mandatory fields
    for (name, config) in fields['mandatory'].iteritems():
        try:
            # predefined values available
            config['predefined']
            currObject = _get_yaml_scan('key', True, name, db_keys, lang, False)
            currChildren = []
            for val in config['predefined']:
                currChildren.append(_get_yaml_scan('value', True, val, db_values, lang, True))
            currObject['children'] = currChildren
        except KeyError:
            # no predefined values available
            currObject = _get_yaml_scan('key', True, name, db_keys, lang, True)
        extObject.append(currObject)
    # Then process the optional fields
    for (name, config) in fields['optional'].iteritems():
        
        # check if the field stems from global or local yaml
        local = False
        try:
            config['local']
            local = True
        except KeyError:
            pass
        
        try:
            # global predefined values available
            config['predefined']
            currObject = _get_yaml_scan('key', False, name, db_keys, lang, False, local)
            currChildren = []
            for val in config['predefined']:
                currChildren.append(_get_yaml_scan('value', False, val, db_values, lang, True, local))
            currObject['children'] = currChildren
        except KeyError:
            try:
                # local predefined values available
                config['values']['predefined']
                currObject = _get_yaml_scan('key', False, name, db_keys, lang, False, local)
                currChildren = []
                for val in config['values']['predefined']:
                    currChildren.append(_get_yaml_scan('value', False, val, db_values, lang, True, local))
                currObject['children'] = currChildren
            except KeyError:
                # no predefined values available
                currObject = _get_yaml_scan('key', False, name, db_keys, lang, True, local)
        extObject.append(currObject)
        
    ret = {}
    ret['success'] = True
    ret['children'] = extObject
    return ret

# @todo: change template used for yaml_add_db (possibly create own) 
@view_config(route_name='yaml_add_activity_fields', renderer='lmkp:templates/sample_values.pt', permission='administer')
def yaml_add_activity_fields(request):

    # Read the global configuration file
    global_stream = open("%s/%s" % (profile_directory_path(request), ACTIVITY_YAML), 'r')
    global_config = yaml.load(global_stream)

    # Read the localized configuration file
    try:
        locale_stream = open("%s/%s" % (locale_profile_directory_path(request), ACTIVITY_YAML), 'r')
        locale_config = yaml.load(locale_stream)

        # If there is a localized config file then merge it with the global one
        global_config = merge_profiles(global_config, locale_config)

    except IOError:
        # No localized configuration file found!
        pass
    
    ret = _add_to_db(global_config, A_Key, A_Value)
    
    # Also scan application YAML (geometry etc.)
    app_scan = _handle_application_config(request)
    if app_scan is not None:
        ret['messagestack'] += app_scan
    
    return ret

def _handle_application_config(request):

    def __check_geometry(yaml_geom, profile_name):
        yaml_geom_geojson = geojson.loads(json.dumps(yaml_geom),
                                          object_hook=geojson.GeoJSON.to_instance)
        yaml_geom_shape = shapely.geometry.asShape(yaml_geom_geojson)
        # Query database
        db_profile = Session.query(Profile).\
            filter(Profile.code == profile_name).first()
        if db_profile is None:
            # Global profile does not yet exist, create it
            Session.add(Profile(profile_name, yaml_geom_shape.wkt))
            return "Geometry for profile '%s' created." % profile_name
        else:
            # Compare existing geometry with the one in config file
            geom_db = shapely.wkb.loads(str(db_profile.geometry.geom_wkb))
            if geom_db.equals(yaml_geom_shape) is True:
                return ("Geometry for profile '%s' did not change." 
                        % profile_name)
            else:
                # Update geometry from global profile
                db_profile.geometry = yaml_geom_shape.wkt
                return "Geometry for profile '%s' updated." % profile_name
    
    msg = []
    
    # First check global application configuration
    app_stream = open("%s/%s" % 
                      (profile_directory_path(request), APPLICATION_YAML), 'r')
    app_config = yaml.load(app_stream)
    
    if ('application' in app_config and 
        'geometry' in app_config['application']):

        msg.append(__check_geometry(app_config['application']['geometry'], 
                   'global'))
    
    # Then check local application configuration if available
    # Try to find the profile in parameters
    locale_code = get_current_profile(request)

    # Only continue if a profile was found
    if locale_code is not None:
        try:
            locale_app_stream = open("%s/%s" % 
                                     (locale_profile_directory_path(request), APPLICATION_YAML), 'r')
            locale_app_config = yaml.load(locale_app_stream)
            
            if ('application' in locale_app_config and
                'geometry' in locale_app_config['application']):

                msg.append(__check_geometry(
                           locale_app_config['application']['geometry'], locale_code))
            
        except IOError:
            # No localized application configuration file found
            pass

    return msg

@view_config(route_name='yaml_add_stakeholder_fields', renderer='lmkp:templates/sample_values.pt', permission='administer')
def yaml_add_stakeholder_fields(request):

    # Read the global configuration file
    global_stream = open("%s/%s" % (profile_directory_path(request), STAKEHOLDER_YAML), 'r')
    global_config = yaml.load(global_stream)

    # Read the localized configuration file
    try:
        locale_stream = open("%s/%s" % (locale_profile_directory_path(request), STAKEHOLDER_YAML), 'r')
        locale_config = yaml.load(locale_stream)

        # If there is a localized config file then merge it with the global one
        global_config = merge_profiles(global_config, locale_config)

    except IOError:
        # No localized configuration file found!
        pass

    ret = _add_to_db(global_config, SH_Key, SH_Value)
    
    # Also scan application YAML (geometry etc.)
    app_scan = _handle_application_config(request)
    if app_scan is not None:
        ret['messagestack'] += app_scan
    
    return ret

def _add_to_db(config, Key, Value):

    stack = []
    stack.append('Scan results:')

    # check for english language (needs to have id=1)
    english_language = Session.query(Language).filter(Language.id == 1).filter(Language.english_name == 'English').all()
    if len(english_language) == 1:
        language = english_language[0]
    else:
        # language not found, insert it.
        language = Language(1, 'English', 'English', 'en')
        Session.add(language)
        stack.append('Language (English) added.')

    # get keys already in database. their fk_sh_key must be None (= original)
    db_keys = []
    for db_key in Session.query(Key.key).filter(Key.fk_key == None).all():
        db_keys.append(db_key.key)

    # get values already in database. their fk_sh_value must be None (= original)
    db_values = []
    for db_value in Session.query(Value.value).filter(Value.fk_value == None).all():
        db_values.append(db_value.value)

    config_items = config["fields"]["mandatory"].items() + config["fields"]["optional"].items()
    for key, value in config_items:
        # check if key is already in database
        if key in db_keys:
            # key is already there, do nothing
            stack.append('Key already in database: %s' % key)
        else:
            # key is not yet in database, insert it
            new_key = Key(key=key)
            new_key.language = language
            Session.add(new_key)
            stack.append('Key added to database: %s' % key)

        # do the same with values
        if value.items():
            for k, val in value.items():
                if k == 'predefined':
                    for v in val:
                        # check if value is already in database
                        if v in db_values:
                            # value is already there, do nothing
                            stack.append('Value already in database: %s' % v)
                        else:
                            # value is not yet in database, insert it
                            new_value = Value(v)
                            new_value.language = language
                            Session.add(new_value)
                            stack.append('Value added to database: %s' % v)

    return {'messagestack': stack}


"""
{name} is the original key as in the yaml (in english)
"""
def _get_field_config(Key, Value, name, config, language, mandatory=False):

    # Determine XType
    xtype = 'textfield'
    try:
        if config['type'] == 'Number':
            xtype = 'numberfield'
        elif config['type'] == 'Date':
            #xtype = 'datefield'
            xtype = 'numberfield'
        elif 'predefined' in config:
            xtype = 'combobox'
    except KeyError:
        pass

    if language.id == 1:
        # English: no database query needed because YAML is in English by
        # default
        fieldLabel = fieldName = name

        if xtype == 'combobox':
            # For combobox, sort the values before returning it
            store = []
            for i in sorted(config['predefined']):
                store.append([i, i])

    else:
        # Not English: Prepare query to translated keys
        keyTranslated = Session.query(
                Key.fk_key.label('original_id'),
                Key.key.label('translated')
            ).\
            filter(Key.language == language).\
            subquery()

        keys = Session.query(
                Key.key.label('original'),
                keyTranslated.c.translated.label('translated'),
                # Use column 'keyorvalue' to separate keys (0) from values (1)
                func.char_length('').label('keyorvalue')
            ).\
            filter(Key.key == name).\
            filter(Key.original == None).\
            outerjoin(keyTranslated, keyTranslated.c.original_id == Key.id)

        query = keys

        # If predefined values are available, query these values as well (use
        # union to perform only one query)
        if xtype == 'combobox':
            # Collect values
            all_vals = []
            for val in config['predefined']:
                all_vals.append(val)

            valuesTranslated = Session.query(
                    Value.fk_value.label('original_id'),
                    Value.value.label('translated')
                ).\
                filter(Value.language == language).\
                subquery()

            values = Session.query(
                    Value.value.label('original'),
                    valuesTranslated.c.translated.label('translated'),
                    # Use column 'keyorvalue' to separate keys (0) from values (1)
                    func.char_length(' ').label('keyorvalue')
                ).\
                filter(Value.value.in_(all_vals)).\
                filter(Value.original == None).\
                outerjoin(valuesTranslated, valuesTranslated.c.original_id == Value.id)

            query = keys.union(values)

        # Collect the values
        store = []
        for x in query.all():
            if x.keyorvalue == 0:
                # Key
                fieldName = x.original
                fieldLabel = (x.translated
                    if x.translated is not None
                    else x.original)
            elif x.keyorvalue == 1:
                # Value: First value is internal (original) value, second is
                # external (translated) value
                s = []
                s.append(x.original)
                if x.translated is not None:
                    s.append(x.translated)
                else:
                    s.append(x.original)
                store.append(s)
        # Sort store by their display (translated) value
        if len(store) > 0:
            store = sorted(store, key=lambda value: value[1])

    # Prepare return object
    fieldConfig = {
        'allowBlank': not mandatory,
        'fieldLabel': fieldLabel,
        'xtype': xtype,
        'name': fieldName
    }
    if xtype == 'combobox':
        fieldConfig['store'] = store
    try:
        fieldConfig['validator'] = config['validator']
    except KeyError:
        pass

    return fieldConfig


def _get_yaml_scan(kv, mandatory, value, db_values, language, leaf, local=False):
    
    fieldConfig = {}
    
    fieldConfig['keyvalue'] = kv
    fieldConfig['mandatory'] = mandatory
    fieldConfig['exists'] = value in db_values
    fieldConfig['value'] = value
    fieldConfig['language'] = language.english_name
    fieldConfig['local'] = local
    if leaf:
        fieldConfig['leaf'] = True
    else:
        fieldConfig['expanded'] = True
        
    if kv == 'key':
        fieldConfig['iconCls'] = 'ico-key'
    else:
        fieldConfig['iconCls'] = 'ico-value'

    if language.id != 1:
        if kv == 'key':
            # try to find original
            original = Session.query(A_Key).filter(A_Key.fk_a_key == None).filter(A_Key.key == value).first()
            translated = Session.query(A_Key).filter(A_Key.original == original).filter(A_Key.language == language).first()
            if original and translated:
                fieldConfig['translation'] = translated.key
            else:
                fieldConfig['translation'] = 1  # not yet translated
        if kv == 'value':
            # try to find original
            original = Session.query(A_Value).filter(A_Value.fk_a_value == None).filter(A_Value.value == value).first()
            translated = Session.query(A_Value).filter(A_Value.original == original).filter(A_Value.language == language).first()
            if translated:
                fieldConfig['translation'] = translated.value
            else:
                fieldConfig['translation'] = 1  # not yet translated
    else:
        fieldConfig['translation'] = 0          # key/value is already in english
    
    return fieldConfig