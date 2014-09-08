import logging
from datetime import timedelta
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationStringFactory
from pyramid.renderers import (
    render,
    render_to_response,
)
from pyramid.security import (
    effective_principals,
    forget,
    remember,
)
from pyramid.view import view_config

from lmkp.config import getTemplatePath
from lmkp.models.database_objects import User
from lmkp.models.meta import DBSession
from lmkp.views.views import BaseView

_ = TranslationStringFactory('lmkp')

log = logging.getLogger(__name__)


class LoginView(BaseView):

    def __init__(self, request):

        self.request = request

    @view_config(route_name='login')
    def login(self):
        """
        Login controller
        """
        login_url = self.request.route_url('login')
        referrer = self.request.path
        if referrer == login_url:
            # never use the login form itself as came_from
            referrer = '/'
        came_from = self.request.params.get('came_from', referrer)
        login = ''
        password = ''
        # Prevent an empty header if /login is directly requested (should
        # actually never happen)
        headers = []
        if 'form.submitted' in self.request.params:
            login = self.request.params['login']
            password = self.request.params['password']

            if User.check_password(login, password):
                log.debug('Login succeed')
                headers = remember(
                    self.request, login,
                    max_age=timedelta(days=30).total_seconds())
            else:
                log.debug('Login failed')
                headers = forget(self.request)
                msg = _(u"Login failed! Please try again.")
                return render_to_response(
                    getTemplatePath(self.request, 'login_form.mak'),
                    {
                        'came_from': came_from,
                        'warning': msg
                    },
                    self.request)

        return HTTPFound(location=came_from, headers=headers)

    @view_config(route_name='login_form')
    def login_form(self):
        """
        Renders the simple login form
        """

        # Prevent endless loops
        if self.request.referer is not None\
            and self.request.referer != self.request.route_url('reset_form')\
            and not self.request.referer.startswith(
                self.request.route_url('login_form')):
            came_from = self.request.referer
        else:
            came_from = self.request.route_url('map_view')

        # Make sure the user is not logged in
        principals = effective_principals(self.request)
        if "system.Authenticated" in principals:
            return HTTPFound(location=came_from)

        return render_to_response(
            getTemplatePath(self.request, 'login_form.mak'),
            {
                'came_from': came_from,
                'warning': None
            },
            self.request)

    @view_config(route_name='reset', renderer='json')
    def reset(self):

        if self.request.params.get('came_from') is not None:
            came_from = self.request.params.get('came_from')
        else:
            came_from = self.request.route_url('map_view')

        # Make sure the user is not logged in
        principals = effective_principals(self.request)
        if "system.Authenticated" in principals:
            return HTTPFound(location=came_from)

        username = self.request.params.get("username")

        user = DBSession.query(User).filter(User.username == username).first()
        if user is None:
            msg = _(u"No registered user found with this email address.")
            return render_to_response(
                getTemplatePath(
                    self.request, 'users/reset_password_form.mak'),
                {
                    'came_from': came_from,
                    'warning': msg
                },
                self.request)

        new_password = user.set_new_password()

        body = render(
            getTemplatePath(self.request, 'emails/reset_password.mak'),
            {
                'user': user.username,
                'new_password': new_password
            },
            self.request)
        self._send_email([user.email], _(u"Password reset"), body)

        return render_to_response(
            getTemplatePath(self.request, 'users/reset_password_success.mak'),
            {}, self.request)

    @view_config(route_name='reset_form')
    def reset_form(self):

        came_from = self.request.params.get('came_from', None)

        return render_to_response(
            getTemplatePath(self.request, 'users/reset_password_form.mak'),
            {
                'came_from': came_from,
                "warning": None
            },
            self.request)

    @view_config(route_name='logout')
    def logout(self):
        headers = forget(self.request)
        return HTTPFound(
            location=self.request.route_url('map_view'), headers=headers)
