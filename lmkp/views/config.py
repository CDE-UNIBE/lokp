# To change this template, choose Tools | Templates
# and open the template in the editor.
__author__ = "Adrian Weber, Centre for Development and Environment, University of Bern"
__date__ = "$Jan 20, 2012 10:39:24 AM$"

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
    stream = open('lmkp/config.yaml', 'r')

    try:
        # If format=ext is set
        if request.GET['format'] == 'ext':
            # Get the configuration file from the YAML file
            yamlConfig = yaml.load(stream)
            extObject = []
            # Do the translation work from custom configuration format to an
            # ExtJS configuration object.
            fields = yamlConfig['application']['fields']

            # First process the mandatory fields
            for (name, config) in fields['mandatory'].iteritems():
                extObject.append(_get_field_config(name, config, True))
            # Then process also the optional fields
            for (name, config) in fields['optional'].iteritems():
                extObject.append(_get_field_config(name, config))

            return extObject
    except KeyError:
        return yaml.load(stream)


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
        fieldConfig['xtype'] = 'combo'
    except KeyError:
        pass

    fieldConfig['xtype'] = xtype

    return fieldConfig