# To change this template, choose Tools | Templates
# and open the template in the editor.
__author__ = "Adrian Weber, Centre for Development and Environment, University of Bern"
__date__ = "$Jan 20, 2012 10:39:24 AM$"

import logging
from lmkp.security import check_user
from pyramid.httpexceptions import HTTPFound
from pyramid.security import forget
from pyramid.security import remember
from pyramid.view import view_config

log = logging.getLogger(__name__)

@view_config(route_name='login')
def login(request):
    """
    Login controller
    """
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        # never use the login form itself as came_from
        referrer = '/'
    came_from = request.params.get('came_from', referrer)
    login = ''
    password = ''
    # Prevent an empty header if /login is directly requested (should actually
    # never happen)
    headers = []
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        if check_user(login, password):
            log.debug('Login succeed')
            headers = remember(request, login)
        else:
            log.debug('Login failed')
            headers = forget(request)

    return HTTPFound(location=came_from, headers=headers)

@view_config(route_name='logout', renderer='lmkp:templates/index.pt')
def logout(request):
    headers = forget(request)
    return HTTPFound(location=request.route_url('index'),
                     headers=headers)