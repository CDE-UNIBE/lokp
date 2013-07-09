from lmkp.config import locale_profile_directory_path
from pyramid.view import view_config
import yaml

@view_config(route_name='context_layers', renderer='javascript')
def get_context_layers(request):

    res = "Ext.namespace('Lmkp');"
    res += "Lmkp.layers=["

    # Read the global configuration file
    try:
        global_stream = open("%s/%s" % (locale_profile_directory_path(request), 'application.yml'), 'r')
        config = yaml.load(global_stream)
    except IOError:
        return

    if 'layers' in config['application']:
        layers = config['application']['layers']

        for layer in layers:
            res += "new OpenLayers.Layer.WMS(\""
            res += layer['name']
            res += "\",\""
            res += layer['url']
            res += "\",{\n"

            for o in layer['wms_options']:
                for config, value in o.iteritems():
                    res += "%s: %s,\n" % (config,_cast_type(config, value))

            res += "},{\n"
            for o in layer['ol_options']:
                for config, value in o.iteritems():
                    res += "%s: %s,\n" % (config,_cast_type(config, value))

            res += "}"
            res += "),\n"

    res += "]\n"

    return res

@view_config(route_name='context_layers2', renderer='javascript')
def get_context_layers2(request):

    res = "var contextLayers = ["

    # Read the global configuration file
    try:
        global_stream = open("%s/%s" % (locale_profile_directory_path(request), 'application.yml'), 'r')
        config = yaml.load(global_stream)
    except IOError:
        return

    if 'layers' in config['application']:
        layers = config['application']['layers']

        for layer in layers:
            res += "new OpenLayers.Layer.WMS(\""
            res += layer['name']
            res += "\",\""
            res += layer['url']
            res += "\",{\n"

            for o in layer['wms_options']:
                for config, value in o.iteritems():
                    res += "%s: %s,\n" % (config,_cast_type(config, value))

            res += "},{\n"
            for o in layer['ol_options']:
                for config, value in o.iteritems():
                    res += "%s: %s,\n" % (config,_cast_type(config, value))

            res += "}"
            res += "),\n"

    res += "]\n"

    return res

def _cast_type(config, value):
    if config.lower() == "maxextent":
        return "new OpenLayers.Bounds(%s, %s, %s, %s)" % (value[0], value[1], value[2], value[3])
    elif value == True or value == False:
        return str(value).lower()

    # Try to cast the value for EPSG to integer
    if config.lower() == 'epsg':
        try:
            return int(value)
        except ValueError:
            pass

    try:
        return float(value)
    except ValueError:
        pass

    return "\"%s\"" % value
