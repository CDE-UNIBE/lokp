# To change this template, choose Tools | Templates
# and open the template in the editor.
__author__ = "Adrian Weber, Centre for Development and Environment, University of Bern"
__date__ = "$Jan 20, 2012 10:39:24 AM$"

from lmkp.config import config_file_path
from lmkp.config import locale_config_file_path
import logging
from pyramid.view import view_config
import yaml

log = logging.getLogger(__name__)

@view_config(route_name='config', renderer='json')
def get_config(request):
    """
    Return the configuration file in lmkp/config.yaml as JSON. Using parameter
    format=ext an ExtJS form fields configuration object is returned based on
    the configuration in config.yaml.
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

    # Get the requested output format
    parameter = request.matchdict['parameter']

    # If parameter=bbox is set
    if parameter is not None and parameter.lower() == 'bbox':
        return {'bbox': global_config['application']['bbox']}

    # If parameter=form is set
    elif parameter is not None and parameter.lower() == 'form':
        # Get the configuration file from the YAML file
        extObject = []
        # Do the translation work from custom configuration format to an
        # ExtJS configuration object.
        fields = global_config['application']['fields']

        # First process the mandatory fields
        for (name, config) in fields['mandatory'].iteritems():
            extObject.append(_get_field_config(name, config, True))
        # Then process also the optional fields
        for (name, config) in fields['optional'].iteritems():
            extObject.append(_get_field_config(name, config))

        return extObject

    # In all other cases return the configuration as JSON
    else:
        return global_config


def _get_field_config(name, config, mandatory=False):

    fieldConfig = {}
    fieldConfig['allowBlank'] = not mandatory
    fieldConfig['name'] = name
    fieldConfig['fieldLabel'] = name

    xtype = 'textfield'
    try:
        if config['type'] == 'Number':
            xtype = 'numberfield'
        if config['type'] == 'Date':
            #xtype = 'datefield'
            xtype = 'numberfield'
    except KeyError:
        pass

    try:
        # If it's a combobox
        fieldConfig['store'] = config['predefined']
        xtype = 'combo'
    except KeyError:
        pass

    try:
        fieldConfig['validator'] = config['validator']
    except KeyError:
        pass

    fieldConfig['xtype'] = xtype

    return fieldConfig