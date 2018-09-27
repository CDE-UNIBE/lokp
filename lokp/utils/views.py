import re
import urllib.parse
from datetime import timedelta

from pyramid.httpexceptions import HTTPFound


def get_current_profile(request):
    """
    Return the currently selected :term:`Profile`.

    First, parameters in the request are considered. If no parameter is
    set, the profile cookie is used. As a fallback, the default profile
    is returned.

    .. seealso::
           :class:`lokp.views.config.get_default_profile`

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        with optional parameter ``_PROFILE_`` or a cookie ``_PROFILE_``
        set.

    Returns:
        ``str``. The name of the :term:`Profile` or the default profile.
    """
    from lokp.config.customization import get_default_profile
    return request.params.get(
        '_PROFILE_', request.cookies.get(
            '_PROFILE_', get_default_profile(request)))


def get_current_locale(request):
    """
    Return the currently selected :term:`Locale`.

    First, parameters in the request are considered. If no parameter is
    set, the locale cookie is used. As a fallback, the default locale
    ``en`` is returned.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        with optional parameter ``_LOCALE_`` or a cookie ``_LOCALE_``
        set.

    Returns:
        ``str``. The name of the :term:`Locale` or ``en`` by
        default.
    """
    return request.params.get(
        '_LOCALE_', request.cookies.get('_LOCALE_', 'en'))


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
        return [float(p) for p in bbox_parts]
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
    if type(item_type) in [str]:
        if item_type.lower() in ['a', 'activity', 'activities']:
            return 'a'
        elif item_type.lower() in ['sh', 'stakeholder', 'stakeholders']:
            return 'sh'
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
    if not type(uuid) in [str]:
        return False
    uuid4hex = re.compile('[0-9a-f-]{36}\Z', re.I)
    return uuid4hex.match(uuid) is not None


def shorten_uuid(uuid):
    """
    Return a short representation of a Universally Unique Identifier (
    :term:`UUID`).

    Args:
        ``uuid`` (str): The string representation of a :term:`UUID`.

    Returns:
        ``str``. A short representation of the :term:`UUID` or an empty
        string if the :term:`UUID` is not valid.
    """
    if validate_uuid(uuid) is True:
        return uuid.split("-")[0]
    return ''


def handle_query_string(url, add=[], remove=[], return_value='full_url'):
    """
    Update the query string of an URL. Keeps existing, adds or removes
    query parameters

    This function can be used to pass certain query parameters (eg.
    filters) from one view to another, eg. from grid to map view.

    Args:
        ``url`` (str): The URL, optionally with existing query
        string

    Kwargs:
        ``add`` (arr): An array of tuples, each with key and value of
        query parameters to be added to the URL.
        Example: ``add=[('page', 1)]``.

        ``remove`` (arr): An array of keys to be removed from the URL's
        query string.

        ``return_value`` (str): The format of the returned string.
        Default is ``full_url``, use ``query_string`` to return only the
        query string.

    Returns:
        ``str``. The URL or query string with query parameters.
    """
    scheme, netloc, path, query_string, fragment = urllib.parse.urlsplit(url)
    qp = urllib.parse.parse_qs(query_string)

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

    new_query_string = urllib.parse.urlencode(qp, doseq=True)
    if return_value == 'query_string':
        if len(qp) == 0:
            return ''
        return '%s%s' % ('?', new_query_string)
    return urllib.parse.urlunsplit((
        scheme, netloc, path, new_query_string, fragment))


def change_profile(request, profile):
    """
    Sets a cookie for the given profile and deletes any location set in the
    cookies.
    Returns a response which directs to the map view.
    """
    response = HTTPFound(location=request.route_url('map_view'))
    response.set_cookie('_PROFILE_', profile, timedelta(days=90))

    if '_LOCATION_' in request.cookies:
        response.delete_cookie('_LOCATION_')

    return response


def get_output_format(request):
    """
    Return the output format as it is defined in the request Matchdict
    (eg. /activities/{json}/...)
    The default output format is JSON.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        with a Matchdict.

    Returns:
        ``string``. The output format.
    """
    try:
        return request.matchdict['output']
    except KeyError:
        return 'json'


def get_page_parameters(request):
    """
    Return a tuple with the page parameters from the request.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        with optional parameters ``page`` and ``pagesize``.

    Returns:
        ``int``. The current page. Defaults to 1.

        ``int``. The page size. Defaults to 10.
    """
    page = request.params.get('page', 1)
    try:
        page = int(page)
    except:
        page = 1
    page = max(page, 1)  # Page should be >= 1

    page_size = request.params.get('pagesize', 10)
    try:
        page_size = int(page_size)
    except:
        page_size = 10
    page_size = max(page_size, 1)  # Page size should be >= 1
    page_size = min(page_size, 50)  # Page size should be <= 50
    return page, page_size


def get_bbox_parameters(request, cookies=True):
    """
    Return a tuple with the bounding box parameters from the request.

    First, parameters in the request are considered. If no parameters
    are set, the location cookie is used.

    .. important::
        This function does not validate the bounding box parameters. In
        order to do this, use the function
        :class:`lmkp.utils.validate_bbox`.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        with optional parameters ``bbox`` and ``epsg`` or a cookie
        ``_LOCATION_`` set.

    Kwargs:
        ``cookies`` (bool): A boolean indicating whether to look for the
        location cookie as fallback or no.

    Returns:
        ``str`` or ``None``. The bounding box or None.

        ``str`` or ``None``. The epsg parameter or None.
    """
    bbox = request.params.get('bbox')
    epsg = request.params.get('epsg', '4326')
    if cookies and bbox is None:
        location = request.cookies.get('_LOCATION_')
        if location:
            bbox = urllib.parse.unquote(location)
    return bbox, epsg


def get_status_parameter(request):
    """
    Return the status parameter from the request.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        with optional parameter ``status``.

    Returns:
        ``str`` or ``None``. The status or None.
    """
    return request.params.get('status', None)
