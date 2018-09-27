import urllib.parse

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config

from lokp.config.customization import get_customized_template_path
from lokp.views.base import BaseView
from lokp.utils.views import change_profile


class MainView(BaseView):
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

    @view_config(route_name='profile_myanmar')
    def profile_myanmar(self):
        return change_profile(self.request, 'myanmar')

    @view_config(route_name='profile_global')
    def profile_global(self):
        return change_profile(self.request, 'global')

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
           :class:`lokp.views.activities.ActivityView.read_many`

        Returns:
            ``HTTPResponse``. A HTML response.
        """
        scheme, netloc, path, query_string, fragment = urllib.parse.urlsplit(
            self.request.url)
        qp = urllib.parse.parse_qs(query_string)

        return HTTPFound(
            location=self.request.route_url(
                'activities_read_many', output='html', _query=qp))
