"""
:mod:`lmkp.utils` provides some useful helper functions.
"""

import re
import urllib
import urlparse


def validate_bbox(bbox):
    """
    Tests if a string is a valid bounding box. It is assumed valid if
    the string contains 4 comma-separated numbers. If valid, the
    bounding box is returned as list.

    Args:
        ``bbox`` (str): A string containing the bounding box.

    Returns:
        ``list`` or ``None``. If valid, a list with 4 float numbers is
        returned. If not valid, None is returned.
    """
    try:
        bbox_parts = bbox.split(',')
        if len(bbox_parts) != 4:
            return None
        return map(float, bbox_parts)
    except:
        return None


def validate_item_type(item_type):
    """
    Tests if a string is a valid item type for either :term:`Activities`
    or :term:`Stakeholders`. Returns a standardized short
    representation of it if valid.

    Args:
        ``item_type`` (str): A string with an item type.

        Valid item types are:

            ``a``, ``activity``, ``activities`` for :term:`Activities`.

            ``sh``, ``stakeholder``, ``stakeholders`` for :term:`Stakeholders`.

    Returns:
        ``str``. A short and standardized representation of the item type.

        ``a`` for :term:`Activities`.

        ``sh`` for :term:`Stakeholders`.

    Raises:
        ``Exception``. If the item type is not valid.
    """
    if item_type in ['a', 'activity', 'activities']:
        return 'a'
    elif item_type in ['sh', 'stakeholder', 'stakeholders']:
        return 'sh'
    else:
        raise Exception('"%s" is not a valid item type!' % item_type)


def validate_uuid(uuid):
    """
    Tests if a string is a valid Universally Unique Identifier
    (:term:`UUID`). Returns True if the UUID is valid and False
    otherwise.

    Args:
        ``uuid`` (str, unicode): The string representation of a
        :term:`UUID`.

    Returns:
        ``bool``. Whether the :term:`UUID` is valid or not.
    """
    if not type(uuid) in [str, unicode]:
        return False
    uuid4hex = re.compile('[0-9a-f-]{36}\Z', re.I)
    return uuid4hex.match(uuid) is not None


def handle_query_string(url, add=[], remove=[], return_value='full_url'):
    """
    Function to update the query parameters of a given URL.
    kwargs:
    add: array of tuples with key and value to add to the URL. If the
    key already exists, it will be replaced with the new value.
    Example: add=[('page', 1)]
    remove: array of keys to remove from the URL.
    ret: fullUrl (default) / queryString. Use 'queryString' to return
    only the query string instead of the full URL.
    """

    # Extract query_strings from url
    scheme, netloc, path, query_string, fragment = urlparse.urlsplit(url)
    qp = urlparse.parse_qs(query_string)

    # Always remove 'epsg' as it is not needed (map is stored in cookie)
    if 'epsg' in qp:
        del(qp['epsg'])

    # Always remove 'page'
    if 'page' in qp:
        del(qp['page'])

    # Always remove 'bbox' if it is not set to 'profile' (bbox of map is stored
    # in cookie)
    if 'bbox' in qp and 'profile' not in qp['bbox']:
        del(qp['bbox'])

    for d in remove:
        if d in qp:
            del(qp[d])

    for k, v in add:
        qp[k] = v

    # Put URL together again and return it
    new_query_string = urllib.urlencode(qp, doseq=True)

    if return_value == 'query_string':
        if len(qp) == 0:
            return ''
        # Return only the query string (with leading '?')
        return '%s%s' % ('?', new_query_string)

    return urlparse.urlunsplit((
        scheme, netloc, path, new_query_string, fragment))
