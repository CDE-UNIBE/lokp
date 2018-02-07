import json

import yaml
from pyramid.view import view_config

from lokp.config.customization import local_profile_directory_path
from lokp.config.form import getCategoryList
from lokp.views.filter import getFilterValuesForKey


def getMapSymbolKeys(request):
    """
    Return a list with the keys which are used for the map symbols.
    Each entry of the array has
    - name of the key (translated)
    - name of the key (original)
    - mapsymbol data (usually an order number)
    If there is an attribute set, it is moved to the top of the list with the
    help of the order number
    """
    mapSymbolKeys = getCategoryList(
        request, 'activities').getMapSymbolKeyNames()

    attrs = request.params.get('attrs', None)

    if attrs is not None:
        for m in mapSymbolKeys:
            if m[1] in attrs:
                m[2] = 0

    return sorted(mapSymbolKeys, key=lambda k: k[2])


@view_config(route_name='map_variables', renderer='javascript')
def get_map_variables(request):
    """
    Dump map variables such as available keys for symbolization of points etc.
    as a JS variable to be used when creating maps.
    """
    map_symbols = getMapSymbolKeys(request)
    map_criteria = map_symbols[0]
    map_symbol_values = [
        v[0] for v in sorted(getFilterValuesForKey(
            request, predefinedType='a', predefinedKey=map_criteria[1]),
            key=lambda value: value[1])]

    return 'var mapVariables = ' + json.dumps({
        'map_symbol_values': map_symbol_values,
        'map_criteria': map_criteria,
        'map_criteria_all': map_symbols,
    })


@view_config(route_name='context_layers', renderer='javascript')
def get_context_layers(request):

    res = "var contextLayers = ["

    # Read the global configuration file
    try:
        global_stream = open("%s/%s" % (
            local_profile_directory_path(request), 'application.yml'), 'r')
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
                for config, value in o.items():
                    res += "%s: %s,\n" % (config, _cast_type(config, value))

            res += "},{\n"
            for o in layer['ol_options']:
                for config, value in o.items():
                    res += "%s: %s,\n" % (config, _cast_type(config, value))

            res += "}"
            res += "),\n"

    res += "]\n"

    return res


def _cast_type(config, value):
    if config.lower() == "maxextent":
        return "new OpenLayers.Bounds(%s, %s, %s, %s)" % (
            value[0], value[1], value[2], value[3])
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
