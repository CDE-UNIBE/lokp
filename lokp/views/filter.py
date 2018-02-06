import urllib.parse

from pyramid.renderers import render
from pyramid.view import view_config

from lokp.config.customization import get_customized_template_path
from lokp.config.form import getCategoryList


@view_config(route_name='filterValues', renderer='json')
def getFilterValuesForKey(request, predefinedType=None, predefinedKey=None):
    """
    Return a JSON representation of all the values for a given key.
    The JSON array contains an array for each entry with:
    - [0]: The display name (translated)
    - [1]: The internal name
    """

    type = request.params.get('type', predefinedType)
    key = request.params.get('key', predefinedKey)

    if type is None:
        return {
            'error': 'No type specified.'
        }

    if key is None:
        return {
            'error': 'No key specified'
        }

    itemType = None
    if type == 'a':
        itemType = 'activities'
    elif type == 'sh':
        itemType = 'stakeholders'

    if itemType is None:
        return {
            'error': 'Type not valid.'
        }

    categoryList = getCategoryList(request, itemType)

    tag = categoryList.findTagByKeyName(key)

    if tag is None:
        return {
            'error': 'Key not found.'
        }

    values = tag.getValues()

    if len(values) == 0:
        return {
            'error': 'No values found for this key.'
        }

    ret = []
    for v in sorted(values, key=lambda val: val.getOrderValue()):
        ret.append([
            v.getTranslation(),
            v.getName()
        ])

    return ret


def getFilterKeys(request):
    """
    Return two lists (the first for Activities, the second for Stakeholders)
    with the keys which can be filtered.
    Each list contains:
    - [0]: display name (translated)
    - [1]: internal name
    - [2]: the type of the key
    """

    def getList(categoryList):
        list = []
        for key in categoryList.getFilterableKeys():
            name = key.getName()
            translation = key.getTranslatedName()
            type = key.getType()
            list.append([
                translation if translation is not None else name,
                name,
                type.lower()
            ])
        return list

    aList = getList(getCategoryList(request, 'activities'))
    shList = getList(getCategoryList(request, 'stakeholders'))

    return aList, shList


def getActiveFilters(request):
    """
    Get the active filters of a request in a list.
    The list contains another list for each active filter with
    - [0]: the query string as provided in the parameter
    - [1]: a clean text representation (translated) of the filter
    """

    # Map the operators
    operators = {
        'like': '=',
        'nlike': '!=',
        'ilike': '=',
        'eq': '=',
        'ne': '!=',
        'lt': '<',
        'lte': '<=',
        'gt': '>',
        'gte': '>='
    }

    aList = getCategoryList(request, 'activities')
    shList = getCategoryList(request, 'stakeholders')

    # Extract query_strings from url
    scheme, netloc, path, query_string, fragment = urllib.parse.urlsplit(
        request.url)
    queryparams = urllib.parse.parse_qs(query_string)

    filters = []
    for q in queryparams:
        if q.startswith('a__') or q.startswith('sh__'):
            queryparts = q.split('__')

            if len(queryparts) != 3:
                continue

            if queryparts[0] == 'a':
                itemName = render(
                    get_customized_template_path(
                        request, 'parts/items/activity.mak'), {}, request
                )
                configList = aList
            elif queryparts[0] == 'sh':
                itemName = render(
                    get_customized_template_path(
                        request, 'parts/items/stakeholder.mak'), {}, request
                )
                configList = shList
            else:
                continue

            key = queryparts[1]
            op = queryparts[2]

            # Use translated key for display
            displayKey = key
            tag = configList.findTagByKeyName(key)
            if tag is not None:
                displayKey = tag.getKey().getTranslatedName()

            for v in queryparams[q]:
                v = v
                q = q
                if type(displayKey) != str:
                    displayKey = displayKey
                # Use translated value for display
                displayValue = v
                if tag is not None:
                    valueObject = tag.findValueByName(v)
                    if valueObject is not None:
                        displayValue = valueObject.getTranslation()
                q_string = '%s=%s' % (q, v)
                q_display = (
                        '(%s) %s %s %s'
                        % (itemName, displayKey, operators[op], displayValue))
                filters.append([q_string, q_display])

    return filters
