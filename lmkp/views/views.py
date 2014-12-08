import re
import logging
import urllib
import urlparse

from datetime import timedelta
from geoalchemy.functions import functions as geofunctions
from geoalchemy import utils
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.renderers import render_to_response
from pyramid.renderers import render
from pyramid.view import view_config
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from lmkp.custom import get_customized_template_path
from lmkp.models.database_objects import Profile
from lmkp.models.meta import DBSession
from lmkp.views.config import get_default_profile
from lmkp.views.form_config import getCategoryList


log = logging.getLogger(__name__)


class BaseView(object):
    """
    Base class for all view classes that need to be aware of the
    requested locale and profile.
    """

    def __init__(self, request):
        self.request = request
        self.template_values = self.get_base_template_values()
        self._handle_parameters()

    def get_base_template_values(self):
        """
        Return a dict with the base values needed for all HTML views
        based on the ``customization/{custom}/templates/base.mak``
        template such as Map View, Grid or Detail View of an
        :term:`Item` and others.

        Returns:
            ``dict``. A dict with the values of the base template
            containing the following values:

                ``profile``: The current profile

                ``locale``: The current locale
        """
        return {
            'profile': get_current_profile(self.request),
            'locale': get_current_locale(self.request)
        }

    def _handle_parameters(self):

        response = self.request.response

        # Make sure the _LOCATION_ cookie is correctly set: The old version GUI
        # version used to store the map center and the zoom level which is not
        # understood by new GUI (which stores the map extent as 4 coordinates)
        if '_LOCATION_' in self.request.cookies:
            c = urllib.unquote(self.request.cookies['_LOCATION_'])
            if len(c.split('|')) == 3:
                response.delete_cookie('_LOCATION_')

        # Check if language (_LOCALE_) is set
        if self.request is not None:
            if '_LOCALE_' in self.request.params:
                response.set_cookie('_LOCALE_', self.request.params.get(
                    '_LOCALE_'), timedelta(days=90))
            elif '_LOCALE_' in self.request.cookies:
                pass

        # Check if profile (_PROFILE_) is set
        if self.request is not None:
            if '_PROFILE_' in self.request.params:
                # Set the profile cookie
                profile_code = self.request.params.get('_PROFILE_')
                response.set_cookie(
                    '_PROFILE_', profile_code, timedelta(days=90))

                # Update _LOCATION_ from cookies to profile geometry bbox
                # retrieved from database
                profile_db = DBSession.query(Profile).\
                    filter(Profile.code == profile_code).\
                    first()

                if profile_db is not None:
                    # Calculate and transform bounding box
                    bbox = DBSession.scalar(geofunctions.envelope(
                        geofunctions.transform(
                            profile_db.geometry, '900913')).wkt)

                    geojson = utils.from_wkt(bbox)

                    coords = geojson['coordinates'][0]
                    p1 = coords[0]
                    p2 = coords[2]

                    l = '%s,%s' % (','.join([str(x) for x in p1]),
                        ','.join([str(x) for x in p2]))

                    response.set_cookie(
                        '_LOCATION_', urllib.quote(l), timedelta(days=90))

            elif '_PROFILE_' in self.request.cookies:
                # Profile already set, leave it
                pass
            else:
                # If no profile is set, set the default profile
                response.set_cookie('_PROFILE_', get_default_profile(
                    self.request), timedelta(days=90))

    def _send_email(self, recipients, subject, body):
        """
        Sends an email message to all recipients using the SMTP host and
        default sender configured in the .ini file.
        """

        mailer = get_mailer(self.request)
        message = Message(subject=subject, recipients=recipients, body=body)
        mailer.send(message)


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


class MainView(BaseView):
    """
    This is the main class for most HTML views of the LOKP.

    Inherits from:
        :class:`lmkp.views.views.BaseView`
    """

    @view_config(route_name='profile_cambodia')
    def profile_cambodia(self):
        return change_profile(self.request, 'cambodia')

    @view_config(route_name='profile_laos')
    def profile_laos(self):
        return change_profile(self.request, 'laos')

    @view_config(route_name='profile_peru')
    def profile_peru(self):
        return change_profile(self.request, 'peru')

    @view_config(route_name='profile_madagascar')
    def profile_madagascar(self):
        return change_profile(self.request, 'madagascar')

    @view_config(route_name='profile_global')
    def profile_global(self):
        return change_profile(self.request, 'global')

    @view_config(route_name='index')
    def index(self):
        """
        Returns the root HTML page. This is the landing page, where
        users can for example select the profile before continuing to
        the map view.

        :term:`Customized template` used: ``landing_page.mak``.

        Returns:
            ``HTTPResponse``. A HTML response.
        """
        return render_to_response(
            get_customized_template_path(self.request, 'landing_page.mak'),
            self.template_values, self.request)

    @view_config(route_name='map_view')
    def map_view(self):
        """
        Returns the HTML page with the main map, eg. the Map View.

        :term:`Customized template` used: ``map_view.mak``.

        Returns:
            ``HTTPResponse``. A HTML response.
        """
        return render_to_response(
            get_customized_template_path(self.request, 'map_view.mak'),
            self.template_values, self.request)

    @view_config(route_name='grid_view')
    def grid_view(self):
        """
        Returns the default HTML page with the grid, eg. the Grid View.

        This view actually returns the default representation of many
        :term:`Activities`. Query parameters are passed through.

        .. seealso::
           :class:`lmkp.views.activities.ActivityView.read_many`

        Returns:
            ``HTTPResponse``. A HTML response.
        """
        scheme, netloc, path, query_string, fragment = urlparse.urlsplit(
            self.request.url)
        qp = urlparse.parse_qs(query_string)

        return HTTPFound(
            location=self.request.route_url(
                'activities_read_many', output='html', _query=qp))

    @view_config(route_name='charts_view')
    def charts_view(self):
        """
        Returns the HTML page with the chart, eg. the Chart View.

        For the time being, this view returns the overview view of the
        Charts.

        .. seealso::
           :class:`lmkp.views.charts.ChartsView.charts_overview`

        Returns:
            ``HTTPResponse``. A HTML response.
        """
        return HTTPFound(location=self.request.route_url('charts_overview'))

        return render_to_response(
            get_customized_template_path(self.request, 'charts_view.mak'),
            self.template_values, self.request)

    @view_config(route_name='about_view')
    def about_view(self):
        """
        Returns the HTML page with the "about" information.

        :term:`Customized template` used: ``about_view.mak``.

        Returns:
            ``HTTPResponse``. A HTML response.
        """
        return render_to_response(
            get_customized_template_path(self.request, 'about_view.mak'),
            self.template_values, self.request)

    @view_config(route_name='faq_view')
    def faq_view(self):
        """
        Returns the HTML page with the FAQ.

        :term:`Customized template` used: ``faq_view.mak``.

        Returns:
            ``HTTPResponse``. A HTML response.
        """
        return render_to_response(
            get_customized_template_path(self.request, 'faq_view.mak'),
            self.template_values, self.request)

    @view_config(route_name='showcases_view')
    def showcases_view(self):
        """
        Returns the HTML page with the Showcases.

        :term:`Customized template` used: ``showcases_view.mak``.

        Returns:
            ``HTTPResponse``. A HTML response.
        """
        return render_to_response(
            get_customized_template_path(self.request, 'showcases_view.mak'),
            self.template_values, self.request)

    @view_config(route_name='partners_view')
    def partners_view(self):
        """
        Returns the HTML page with the Partners.

        :term:`Customized template` used: ``partners_view.mak``.

        Returns:
            ``HTTPResponse``. A HTML response.
        """
        return render_to_response(
            get_customized_template_path(self.request, 'partners_view.mak'),
            self.template_values, self.request)

    @view_config(route_name='moderation_html')
    def moderation_html(self):
        """
        Returns a view for the :term:`Moderators`.

        This view actually returns the default representation of many
        :term:`Activities`, filtered by status (pending).

        .. seealso::
           :class:`lmkp.views.activities.ActivityView.read_many`

        Returns:
            ``HTTPResponse``. A HTML response.
        """
        return HTTPFound(location=self.request.route_url(
            'activities_read_many', output='html',
            _query={'status': 'pending'}))

    @view_config(
        route_name='administration',
        renderer='lmkp:templates/ext_administration.mak',
        permission='administer')
    def administration(self):
        """
        Returns a view for the :term:`Administrators`.

        Returns:
            ``HTTPResponse``. A HTML response.
        """
        return {}

    @view_config(route_name='simple_proxy', renderer='string')
    def simple_proxy(self):

        allowedHosts = ['^http://cdetux2.unibe.ch']

        if "url" not in self.request.params:
            raise HTTPNotFound()

        url = self.request.params.get("url")

        for host in allowedHosts:
            pattern = re.compile(host)
            if pattern.search(url) is not None:
                handle = urllib.urlopen(url)
                return handle.read()

        raise HTTPBadRequest("Host not allowed.")


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


def get_default_search_key(request, item_type):

    category_list = getCategoryList(request, item_type)
    search_key = category_list.get_default_search_key()
    if search_key:
        return search_key.getTranslatedName(), search_key.getName()
    return None, None


def getOverviewKeys(request):
    """
    Return two lists (the first for Activities, the second for Stakeholders)
    with the keys which are to be used in the involvement overview. Because
    these are the keys of the other side, the first one actually contains the
    keys for Stakeholders, the second one the keys for Activities!
    """
    return (
        getCategoryList(
            request, 'activities').getInvolvementOverviewKeyNames(),
        getCategoryList(
            request, 'stakeholders').getInvolvementOverviewKeyNames()
    )


def getOverviewRawKeys(request):
    """
    Return two lists (the first for Activities, the second for Stakeholders)
    with the keys which are to be used in the involvement overview. Because
    these are the keys of the other side, the first one actually contains the
    keys for Stakeholders, the second one the keys for Activities!
    These keys are not translated.
    """
    return (
        getCategoryList(
            request, 'activities').getInvolvementOverviewRawKeyNames(),
        getCategoryList(
            request, 'stakeholders').getInvolvementOverviewRawKeyNames()
    )


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
    scheme, netloc, path, query_string, fragment = urlparse.urlsplit(
        request.url)
    queryparams = urlparse.parse_qs(query_string)

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
                v = v.decode('utf-8')
                q = q.decode('utf-8')
                if type(displayKey) != unicode:
                    displayKey = displayKey.decode('utf-8')
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

        ``cookies`` (bool): A boolean indicating whether to look for the
        location cookie as fallback or no.

    Returns:
        ``str`` or ``None``. The bounding box or None.

        ``str`` or ``None``. The epsg parameter or None.
    """
    bbox = request.params.get('bbox')
    epsg = request.params.get('epsg', '900913')
    if cookies and bbox is None:
        location = request.cookies.get('_LOCATION_')
        if location:
            bbox = urllib.unquote(location)
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


def get_current_profile(request):
    """
    Return the currently selected :term:`Profile`.

    First, parameters in the request are considered. If no parameter is
    set, the profile cookie is used. As a fallback, the default profile
    is returned.

    .. seealso::
           :class:`lmkp.views.config.get_default_profile`

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        with optional parameter ``_PROFILE_`` or a cookie ``_PROFILE_``
        set.

    Returns:
        ``str``. The name of the :term:`Profile` or the default profile.
    """
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


def get_current_attribute_filters(request):
    """
    Return the currently active filters on both :term:`Activity` and
    :term:`Stakeholder` attributes from the request.

    The filters have the form: ``a__Key__eq=Value``.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        with optional filter parameter.

    Returns:
        ``list``. A list with attribute filters.
    """
    filters = []
    for param in request.params:
        try:
            prefix, col, op = param.split('__')
        except ValueError:
            continue
        if prefix not in ['a', 'sh']:
            continue
        filters.append((prefix, col, op, request.params[param]))
    return filters


def get_current_logical_filter_operator(request):
    """
    Return the currently active logical filter operator from the request
    to apply on multiple attribute filters. Valid operators are ``and``
    (default) and ``or``.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        with optional parameter ``logical_op`` set to either ``and`` or
        ``or``.

    Returns:
         ``str``. The logical operator: Either ``and`` (default) or
         ``or``
    """
    default = 'and'
    op = request.params.get('logical_op', default).lower()
    if op in ['and', 'or']:
        return op
    return default


def get_current_order_key(request):
    """
    Return the key to order :term:`Items` by. The key should be a valid
    attribute key for :term:`Activities` or :term:`Stakeholder`. By
    default, :term:`Items` are ordered by the timestamp of their
    creation.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        with optional parameter ``order_by`` set.

    Returns:
        ``str``. The key or ``timestamp`` if none is set.
    """
    return request.params.get('order_by', 'timestamp')


def get_current_order_direction(request):
    """
    Return the direction to order :term:`Items` by from the request.
    Valid directions are ``asc`` (default) and ``desc``. If the order
    key is ``timestamp``, the default order direction is ``desc``!

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        with optional parameter ``dir`` set.

    Returns:
         ``str``. The order direction: Either ``asc`` (default) or
         ``desc``
    """
    default = 'asc'
    if get_current_order_key(request) == 'timestamp':
        default = 'desc'
    order = request.params.get('dir', default).lower()
    if order in ['asc', 'desc']:
        return order
    return default


def get_current_involvement_details(request):
    """
    Return the keyword of how much details of the :term:`Involvements`
    are to be shown. Valid keywords are ``full`` (default), ``none``.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        with optional parameter ``involvements`` set.

    Returns:
        ``str``. The key or ``full`` if none is set.
    """
    default = 'full'
    details = request.params.get('involvements', default).lower()
    if details in ['full', 'none']:
        return details
    return default


def get_current_limit(request):
    """
    Return the current limit from the request. The limit indicates how
    many :term:`Items` are shown at once when querying many. Together
    with the ``offset`` parameter it allows pagination.

    .. seealso::
       :class:`lmkp.views.views.get_current_offset`

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        with optional parameter ``limit`` set.

    Returns:
        ``int`` or ``None``. A absolute integer if one was provided in
        the request, else None.
    """
    default = None
    limit = request.params.get('limit', default)
    try:
        return abs(int(limit))
    except:
        return default


def get_current_offset(request):
    """
    Return the current offset from the request. The offset indicates how
    many :term:`Items` are skipped when querying many. Together with the
    ``limit`` parameter it allows pagination.

    .. seealso::
       :class:`lmkp.views.views.get_current_offset`

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        with optional parameter ``offset`` set.

    Returns:
        ``int``. A absolute integer if one was provided in the request
        or 0 by default.
    """
    default = 0
    offset = request.params.get('offset', default)
    try:
        return abs(int(offset))
    except:
        return default


def get_current_translation_parameter(request):
    """
    Return the current translate parameter from the request. Usually
    indicates whether to translate the response or not.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        with optional parameter ``translate`` set (either to ``true`` or
        ``false``).

    Returns:
        ``bool``. A boolean indicating whether the parameter
        ``translate`` was set and is true or not. Defaults to ``True``
        even if the parameter is not set.
    """
    default = 'true'
    translate = request.params.get('translate', default).lower()
    return translate != 'false'


def get_current_taggroup_geometry_parameter(request):
    """
    Return the current taggroup geometry parameter from the request.
    Indicates whether to return the geometries of taggroups or not.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        with optional parameter ``taggroup_geometry`` set (either to
        ``true`` or ``false``). Parameter ``tggeom`` is also supported
        but with lower priority (not respected if ``taggroup_geometry``
        is set)

    Returns:
        ``bool``. A boolean indicating whether the parameter
        ``taggroup_geometry`` was set and is true or not. Defaults to
        ``False`` even if the parameter is not set.
    """
    default = 'false'
    taggroup_geometry = request.params.get(
        'taggroup_geometry', request.params.get('tggeom', default)).lower()
    return taggroup_geometry == 'true'


def get_current_attributes(request):
    """
    Return the current attributes parameter from the request. This is
    used for example to filter the resulting output to contain only the
    provided attributes.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        with optional parameter ``attributes`` set to a comma-separated
        list of attributes. Parameter ``attrs`` is also supported
        but with lower priority (not respected if ``attributes`` is set)

    Returns:
        ``list``. A list with the attributes or an empty list by
        default.
    """
    attrs = request.params.get('attributes', request.params.get('attrs'))
    try:
        return attrs.split(',')
    except AttributeError:
        return []


def get_current_version(request):
    """
    Return the current version from the request.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        with optional parameter ``version`` set. Parameter ``v`` is also
        supported but with lower priority (not respected if ``version``
        is set).

    Returns:
        ``int``. A absolute integer if one was provided in the request
        or None by default.
    """
    version = request.params.get('version', request.params.get('v'))
    try:
        return abs(int(version))
    except:
        return None
