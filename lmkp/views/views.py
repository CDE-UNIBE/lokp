from datetime import timedelta
from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession
import logging
import urllib
from geoalchemy.functions import functions as geofunctions
from geoalchemy import utils
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.renderers import render
from pyramid.view import view_config
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from urlparse import parse_qs, urlsplit, urlunsplit
from urllib import urlencode
from lmkp.views.profile import get_current_profile
from lmkp.views.profile import get_current_locale
from lmkp.views.form_config import getCategoryList
from lmkp.config import getTemplatePath
import re

log = logging.getLogger(__name__)

class BaseView(object):
    """
    Base class for all view classes that need to be aware of the requested locale.
    """

    def __init__(self, request):
        self.request = request

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
                response.set_cookie('_LOCALE_', self.request.params.get('_LOCALE_'), timedelta(days=90))
            elif '_LOCALE_' in self.request.cookies:
                pass

        # Check if profile (_PROFILE_) is set
        if self.request is not None:
            if '_PROFILE_' in self.request.params:
                # Set the profile cookie
                profile_code = self.request.params.get('_PROFILE_')
                response.set_cookie('_PROFILE_', profile_code, timedelta(days=90))

                # Update _LOCATION_ from cookies to profile geometry bbox
                # retrieved from database
                profile_db = DBSession.query(Profile).\
                    filter(Profile.code == profile_code).\
                    first()

                if profile_db is not None:
                    # Calculate and transform bounding box
                    bbox = DBSession.scalar(geofunctions.envelope(
                            geofunctions.transform(profile_db.geometry, '900913')
                        ).wkt)

                    geojson = utils.from_wkt(bbox)

                    coords = geojson['coordinates'][0]
                    p1 = coords[0]
                    p2 = coords[2]

                    l = '%s,%s' % (','.join([str(x) for x in p1]), ','.join([str(x) for x in p2]))

                    response.set_cookie('_LOCATION_', urllib.quote(l), timedelta(days=90))

            elif '_PROFILE_' in self.request.cookies:
                # Profile already set, leave it
                pass
            else:
                # If no profile is set, set 'global' profile
                response.set_cookie('_PROFILE_', 'global', timedelta(days=90))

    def _send_email(self, recipients, subject, body):
        """
        Sends an email message to all recipients using the SMTP host and default
        sender configured in the .ini file.
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
        Returns the main HTML page
        """

        self._handle_parameters()

        return render_to_response(getTemplatePath(self.request, 'landing_page.mak'), {
            'profile': get_current_profile(self.request),
            'locale': get_current_locale(self.request)
        }, self.request)

    @view_config(route_name='map_view')
    def map_view(self):

        self._handle_parameters()

        return render_to_response(getTemplatePath(self.request, 'map_view.mak'), {
            'profile': get_current_profile(self.request),
            'locale': get_current_locale(self.request)
        }, self.request)

    @view_config(route_name='grid_view')
    def grid_view(self):
        """
        This view is basically only a redirect to the read_many view of the
        Activities. Keep query parameters so for example filters are also active
        in grid.
        """

        # Extract query_strings from url
        scheme, netloc, path, query_string, fragment = urlsplit(self.request.url)
        qp = parse_qs(query_string)

        return HTTPFound(
            location=self.request.route_url('activities_read_many',
            output='html', _query=qp)
        )

    @view_config(route_name='charts_view')
    def charts_view(self):

        self._handle_parameters()

        # TEMP
        return HTTPFound(location=self.request.route_url('charts_overview'))

        return render_to_response(getTemplatePath(self.request, 'charts_view.mak'), {
            'profile': get_current_profile(self.request),
            'locale': get_current_locale(self.request)
        }, self.request)

    @view_config(route_name='about_view')
    def about_view(self):

        self._handle_parameters()

        return render_to_response(getTemplatePath(self.request, 'about_view.mak'), {
            'profile': get_current_profile(self.request),
            'locale': get_current_locale(self.request)
        }, self.request)

    @view_config(route_name='faq_view')
    def faq_view(self):

        self._handle_parameters()

        return render_to_response(getTemplatePath(self.request, 'faq_view.mak'), {
            'profile': get_current_profile(self.request),
            'locale': get_current_locale(self.request)
        }, self.request)
        
    @view_config(route_name='showcases_view')
    def faq_view(self):

        self._handle_parameters()

        return render_to_response(getTemplatePath(self.request, 'showcases_view.mak'), {
            'profile': get_current_profile(self.request),
            'locale': get_current_locale(self.request)
        }, self.request)

    @view_config(route_name='partners_view')
    def partners_view(self):

        self._handle_parameters()

        return render_to_response(getTemplatePath(self.request, 'partners_view.mak'), {
            'profile': get_current_profile(self.request),
            'locale': get_current_locale(self.request)
        }, self.request)

    @view_config(route_name='embedded_index', renderer='lmkp:templates/old_embedded.mak')
    def embedded_version(self):
        """
        Returns a version of the Land Observatory that can be embedded in other
        website or land portals. The main (and currently the only) difference to
        the normal index view is the missing combobox to select another profile.
        """

        # Get the requested profile from the URL
        profile = self.request.matchdict.get('profile', 'global')

        # Custom handling of the standard parameters: don't use method _handle_parameters
        # since we get the profile parameter from the routing and not as URL parameter.
        if self.request is not None:
            response = self.request.response
            # Manipulate the cookies of the request object to make sure, that
            # method get_current_profile in lmkp.views.profile gets the correct
            # profile.
            self.request.cookies['_PROFILE_'] = profile
            # Set the cookie with a validity of three months
            self.request.response.set_cookie('_PROFILE_', profile, timedelta(days=90))

            # Check if language (_LOCALE_) is set
            if '_LOCALE_' in self.request.params:
                response.set_cookie('_LOCALE_', self.request.params.get('_LOCALE_'), timedelta(days=90))
            elif '_LOCALE_' in self.request.cookies:
                pass

        return {}

    @view_config(route_name='enclosing_demo_site')
    def enclosing_demo_site(self):
        """
        This view provides a *very* simple example how the Land Observatory can
        be embedded in any website with a fixed profile and a hidden profile combobox.
        """

        html = """
<html>
    <head>
        <title>Embedded Land Observatory</title>
    </head>
    <body>
        <div style="width: 100%;">
            <div style="height: 10%;">
                This is a very basic example of how to embed the Land Observatory
                platform in a custom website using a HTML iframe:
                <pre>
&lt;iframe style="height: 90%; width: 100%; border: 0;" src="http://localhost:6543/embedded/Madagascar?_LOCALE_=fr"&gt;
&lt;/iframe&gt;
                </pre>
            </div>
            <div>
                <iframe style="height: 90%; width: 100%; border: 0;" src="http://localhost:6543/embedded/Madagascar?_LOCALE_=fr">
                </iframe>
            </div>
        </div>
    </body>
</html>
    """

        return Response(html, content_type='text/html', status_int=200)

    @view_config(route_name='moderation_html')
    def moderation_html(self):
        """
        Returns the moderation HTML page.
        This actually reroutes to the HTML representation of Activities, showing
        only the pending versions.
        """

        return HTTPFound(location=self.request.route_url('activities_read_many',
            output='html', _query={'status': 'pending'}))

    @view_config(route_name='translation', renderer='lmkp:templates/ext_translation.mak', permission='translate')
    def translation(self):
        """
        Returns the translation HTML page
        """

        self._handle_parameters()

        return {}

    @view_config(route_name='administration', renderer='lmkp:templates/ext_administration.mak', permission='administer')
    def administration(self):
        """
        Returns the administration HTML page
        """

        self._handle_parameters()

        return {}

    @view_config(route_name='privileges_test', renderer='lmkp:templates/old_privilegestest.mak')
    def privileges_test(self):
        """
        Simple view to output the current privileges
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

def getQueryString(url, **kwargs):
    """
    Function to update the query parameters of a given URL.
    kwargs:
    - add: array of tuples with key and value to add to the URL. If the key
      already exists, it will be replaced with the new value.
      Example: add=[('page', 1)]
    - remove: array of keys to remove from the URL.
    - ret: fullUrl (default) / queryString. Use 'queryString' to return only the
      query string instead of the full URL.
    """

    if 'add' not in kwargs and 'remove' not in kwargs and 'ret' not in kwargs:
        return url

    # Collect the values to add / remove
    add = kwargs.pop('add', {})
    remove = kwargs.pop('remove', [])

    # Extract query_strings from url
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    qp = parse_qs(query_string)

    # Always remove 'epsg' as it is not needed (map is stored in cookie)
    if 'epsg' in qp: del(qp['epsg'])

    # Always remove 'bbox' if it is not set to 'profile' (bbox of map is stored
    # in cookie)
    if 'bbox' in qp and 'profile' not in qp['bbox']:
        del(qp['bbox'])

    # Always remove 'page'
    if 'page' in qp: del(qp['page'])

    # Remove
    for d in remove:
        if d in qp:
            del(qp[d])

    # Add
    for k, v in add:
        qp[k] = v

    # Put URL together again and return it
    new_query_string = urlencode(qp, doseq=True)

    # What is to be returned?
    returnWhat = kwargs.pop('ret', 'fullUrl')

    if returnWhat == 'queryString':
        if len(qp) == 0:
            return ''
        # Return only the query string (with leading '?')
        return '%s%s' % ('?', new_query_string)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))

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

def getOverviewKeys(request):
    """
    Return two lists (the first for Activities, the second for Stakeholders)
    with the keys which are to be used in the involvement overview. Because
    these are the keys of the other side, the first one actually contains the
    keys for Stakeholders, the second one the keys for Activities!
    """
    return (
        getCategoryList(request, 'activities').getInvolvementOverviewKeyNames(),
        getCategoryList(request, 'stakeholders').getInvolvementOverviewKeyNames()
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
        getCategoryList(request, 'activities').getInvolvementOverviewRawKeyNames(),
        getCategoryList(request, 'stakeholders').getInvolvementOverviewRawKeyNames()
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
    mapSymbolKeys = getCategoryList(request, 'activities').getMapSymbolKeyNames()

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

    _ = request.translate

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
    scheme, netloc, path, query_string, fragment = urlsplit(request.url)
    queryparams = parse_qs(query_string)

    filters = []
    for q in queryparams:
        if q.startswith('a__') or q.startswith('sh__'):
            queryparts = q.split('__')

            if len(queryparts) != 3:
                continue

            if queryparts[0] == 'a':
                itemName = render(
                    getTemplatePath(request, 'parts/items/activity.mak'), {}, request
                )
                configList = aList
            elif queryparts[0] == 'sh':
                itemName = render(
                    getTemplatePath(request, 'parts/items/stakeholder.mak'), {}, request
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
                # Use translated value for display
                displayValue = v
                if tag is not None:
                    valueObject = tag.findValueByName(v)
                    if valueObject is not None:
                        displayValue = valueObject.getTranslation()
                q_string = '%s=%s' % (q, v)
                q_display = ('(%s) %s %s %s' % (itemName, displayKey,
                    operators[op], displayValue))
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