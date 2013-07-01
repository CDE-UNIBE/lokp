from datetime import timedelta
from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession
import logging
import urllib
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import view_config
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from lmkp.views.profile import get_current_profile
from lmkp.views.profile import get_current_locale

log = logging.getLogger(__name__)

class BaseView(object):
    """
    Base class for all view classes that need to be aware of the requested locale.
    """

    def __init__(self, request):
        self.request = request

    def _handle_parameters(self):
        # Check if language (_LOCALE_) is set
        if self.request is not None:
            response = self.request.response
            if '_LOCALE_' in self.request.params:
                response.set_cookie('_LOCALE_', self.request.params.get('_LOCALE_'), timedelta(days=90))
            elif '_LOCALE_' in self.request.cookies:
                pass


        # Check if profile (_PROFILE_) is set
        if self.request is not None:
            response = self.request.response
            if '_PROFILE_' in self.request.params:
                response.set_cookie('_PROFILE_', self.request.params.get('_PROFILE_'), timedelta(days=90))
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

class MainView(BaseView):

    @view_config(route_name='index', renderer='lmkp:templates/index.mak')
    def index(self):
        """
        Returns the main HTML page
        """

        self._handle_parameters()
        
        return {}

    @view_config(route_name='map_view', renderer='lmkp:templates/map_view.mak')
    def map_view(self):

        self._handle_parameters()

        return {"profile": get_current_profile(self.request), "locale": get_current_locale(self.request)}

    @view_config(route_name='grid_view', renderer='lmkp:templates/grid_view.mak')
    def grid_view(self):

        self._handle_parameters()

        request = self.request

        # Default limit of how many entries are listed per page
        limit = 10

        # Default item type: activities
        item_type = request.params.get('tab', 'a')

        if item_type == 'sh':
            from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
            protocol = StakeholderProtocol3(DBSession)
        else:
            from lmkp.views.activity_protocol3 import ActivityProtocol3
            protocol = ActivityProtocol3(DBSession)

        # Default page: 1
        page = request.params.get('page', None)
        try:
            page = int(page)
        except TypeError:
            page = 1

        # Temporarily set limit and offset so the protocol makes use of this
        request.GET.add('limit', str(limit))
        request.GET.add('offset', str(limit * page - limit))

        spatialfilter = 'profile'
        location = self.request.cookies.get('_LOCATION_')
        if location is not None:
            location = urllib.unquote(location)
            if len(location.split(',')) == 4:
                spatialfilter = 'mapextent'
                request.GET.add('bbox', location)
                request.GET.add('epsg', '900913')

        # Query the items
        items = protocol.read_many(request, public=False)

        # Remove limit and offset parameters
        request.GET.pop('limit')
        request.GET.pop('offset')
        
        try:
            request.GET.pop('bbox')
            request.GET.pop('epsg')
        except KeyError:
            pass

        data = items['data'] if 'data' in items else []
        total = items['total'] if 'total' in items else 0

        return {
            'profile': get_current_profile(self.request),
            'locale': get_current_locale(self.request),
            'data': data,
            'total': total,
            'currentpage': page,
            'pagesize': limit,
            'paginationneighbours': 2,
            'activetab': item_type,
            'spatialfilter': spatialfilter
        }

    @view_config(route_name='charts_view', renderer='lmkp:templates/charts_view.mak')
    def charts_view(self):

        self._handle_parameters()

        return {"profile": get_current_profile(self.request), "locale": get_current_locale(self.request)}

    @view_config(route_name='embedded_index', renderer='lmkp:templates/embedded.mak')
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

    @view_config(route_name='moderation_html', renderer='lmkp:templates/moderation.mak', permission='moderate')
    def moderation_html(self):
        """
        Returns the moderation HTML page
        """

        self._handle_parameters()

        return {
            'openItem': '',
            'type': '',
            'identifier': ''
        }

    @view_config(route_name='translation', renderer='lmkp:templates/translation.mak', permission='translate')
    def translation(self):
        """
        Returns the translation HTML page
        """
        
        self._handle_parameters()

        return {}

    @view_config(route_name='administration', renderer='lmkp:templates/administration.mak', permission='administer')
    def administration(self):
        """
        Returns the administration HTML page
        """

        self._handle_parameters()

        return {}

    @view_config(route_name='privileges_test', renderer='lmkp:templates/privilegestest.mak')
    def privileges_test(self):
        """
        Simple view to output the current privileges
        """
        return {}