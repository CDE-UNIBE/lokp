import urllib.parse
from datetime import timedelta

import geojson
from geoalchemy2 import functions as geofunctions
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from lokp.models import DBSession
from lokp.config.customization import get_default_profile
from lokp.models import Profile
from lokp.utils.views import get_current_profile, get_current_locale


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
            c = urllib.parse.unquote(self.request.cookies['_LOCATION_'])
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
            # TODO
            if '_PROFILE_' in self.request.params:
                # Set the profile cookie
                profile_code = self.request.params.get('_PROFILE_')
                response.set_cookie(
                    '_PROFILE_', profile_code, timedelta(days=90))

                # Update _LOCATION_ from cookies to profile geometry bbox
                # retrieved from database
                profile_db = DBSession.query(Profile). \
                    filter(Profile.code == profile_code). \
                    first()

                if profile_db is not None:

                    # Calculate and transform bounding box
                    # bbox = DBSession.scalar(geofunctions.ST_Envelope(profile_db.geometry))
                    bbox = DBSession.scalar(geofunctions.ST_Envelope(
                        geofunctions.ST_Transform(
                            profile_db.geometry, 900913)))

                    gjson = geojson.loads(
                        DBSession.scalar(geofunctions.ST_AsGeoJSON(bbox)))

                    coords = gjson['coordinates'][0]
                    p1 = coords[0]
                    p2 = coords[2]

                    l = '%s,%s' % (','.join([str(x) for x in p1]),
                                   ','.join([str(x) for x in p2]))

                    response.set_cookie(
                        '_LOCATION_', urllib.parse.quote(l), timedelta(days=90))

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
