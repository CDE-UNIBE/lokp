# To change this template, choose Tools | Templates
# and open the template in the editor.
__author__ = "Adrian Weber, Centre for Development and Environment, University of Bern"
__date__ = "$Jan 20, 2012 10:39:24 AM$"

from datetime import timedelta
from lmkp.models.database_objects import User
from lmkp.models.meta import DBSession
from lmkp.views.views import BaseView
import logging
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationStringFactory
from pyramid.renderers import render
from pyramid.renderers import render_to_response
from pyramid.security import effective_principals
from pyramid.security import forget
from pyramid.security import remember
from pyramid.view import view_config

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
        # Prevent an empty header if /login is directly requested (should actually
        # never happen)
        headers = []
        if 'form.submitted' in self.request.params:
            login = self.request.params['login']
            password = self.request.params['password']

            if User.check_password(login, password):
                log.debug('Login succeed')
                headers = remember(self.request, login, max_age=timedelta(days=30).total_seconds())
            else:
                log.debug('Login failed')
                headers = forget(self.request)
                msg = _(u"Login failed! Please try again.")
                return render_to_response('lmkp:templates/login_form.mak', {'came_from': came_from, 'warning': msg}, self.request)

        return HTTPFound(location=came_from, headers=headers)

    @view_config(route_name='login_form', renderer='lmkp:templates/login_form.mak')
    def login_form(self):
        """
        Renders the simple login form
        """

        # Prevent endless loops
        if self.request.referer is not None\
            and self.request.referer != self.request.route_url('reset_form')\
            and not self.request.referer.startswith(self.request.route_url('login_form')):
            came_from = self.request.referer
        else:
            came_from = self.request.route_url('index')

        # Make sure the user is not logged in
        principals = effective_principals(self.request)
        if "system.Authenticated" in principals:
            return HTTPFound(location=came_from)

        return {"came_from": came_from, "warning": None}

    @view_config(route_name='reset', renderer='json')
    def reset(self):

        if self.request.params.get('came_from') is not None:
            came_from = self.request.params.get('came_from')
        else:
            came_from = self.request.route_url('index')

        # Make sure the user is not logged in
        principals = effective_principals(self.request)
        if "system.Authenticated" in principals:
            return HTTPFound(location=came_from)

        email = self.request.params.get('email')

        user = DBSession.query(User).filter(User.email == email).first()
        if user is None:
            msg = _(u"No registered user found with this email address.")
            return {'success': False, 'msg': msg}

        new_password = user.set_new_password()

        body = render('lmkp:templates/emails/reset_password_email.mak', {'user': user.username, 'new_password': new_password}, self.request)
        self._send_email([user.email], _(u"Land Observatory - Password reset"), body)

        msg = _(u"Password reset was successful. An email containing the new password has been sent to your email address.")
        msg += "<br/><a href=\"%s\">" % self.request.route_url('login_form')
        msg += _(u"Proceed to the login page")
        msg += "</a>."

        return {'success': True, 'msg': msg}

    @view_config(route_name='reset_form', renderer='lmkp:templates/reset_form.mak')
    def reset_form(self):

        came_from = self.request.params.get('came_from', None)
        return {'came_from': came_from}

    @view_config(route_name='logout', renderer='lmkp:templates/index.pt')
    def logout(self):
        headers = forget(self.request)
        return HTTPFound(location=self.request.route_url('index'), headers=headers)