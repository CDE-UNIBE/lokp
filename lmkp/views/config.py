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
            originConfig = yaml.load(stream)
            extObject = []
            # Do the translation work from custom configuration format to an
            # ExtJS configuration object.
            # First process the mandatory fields
            #
            # Code clean-up required!
            for i in originConfig['application']['fields']['mandatory']:
                field = originConfig['application']['fields']['mandatory'][i]
                xtype = 'textfield'
                if field['type'] == 'Number':
                    xtype = 'numberfield'
                if field['type'] == 'Date':
                    xtype = 'datefield'
                try:
                    # If it's a combobox
                    extObject.append({'allowBlank': False, 'name': i, 'fieldLabel': i, 'xtype': 'combo', 'store': field['predefined']})
                except:
                    extObject.append({'allowBlank': False, 'name': i, 'fieldLabel': i, 'xtype': xtype})
            # Then process also the optional fields
            for j in originConfig['application']['fields']['optional']:
                field = originConfig['application']['fields']['optional'][j]
                xtype = 'textfield'
                if field['type'] == 'Number':
                    xtype = 'numberfield'
                if field['type'] == 'Date':
                    xtype = 'datefield'
                # allowBlank is per default true
                extObject.append({'name': j, 'fieldLabel': j, 'xtype': xtype, 'format': 'Y'})
            return extObject
    except:
        return yaml.load(stream)
        