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

    def _merge_config(global_config, locale_config):

        for key, value in locale_config.items():
            try:
                value.items()
                _merge_config(global_config[key], locale_config[key])
            except:
                global_config[key] = locale_config[key]

    global_stream = open(config_file_path(request), 'r')
    global_config = yaml.load(global_stream)

    try:
        locale_stream = open(locale_config_file_path(request), 'r')
        locale_config = yaml.load(locale_stream)

        _merge_config(global_config, locale_config)

    except IOError:
        # File not found!
        pass

    parameter = request.matchdict['parameter']

    # if parameter=bbox is set
    if parameter is not None and parameter.lower() == 'bbox':
        return {'bbox': global_config['application']['bbox']}

    # if format=ext is set
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
    else:
        return global_config


def _get_field_config(name, config, mandatory=False):

    fieldConfig = {}
    fieldConfig['allowBlank'] = not mandatory
    fieldConfig['name'] = name
    fieldConfig['fieldLabel'] = name

    xtype = 'textfield'
    if config['type'] == 'Number':
        xtype = 'numberfield'
    if config['type'] == 'Date':
        #xtype = 'datefield'
        xtype = 'numberfield'

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