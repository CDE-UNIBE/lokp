# To change this template, choose Tools | Templates
# and open the template in the editor.
__author__ = "Adrian Weber, Centre for Development and Environment, University of Bern"
__date__ = "$Jan 20, 2012 10:39:24 AM$"

import logging
from pyramid.view import view_config

log = logging.getLogger(__name__)

@view_config(route_name='manage_events', renderer='lmkp:templates/index.pt')
def manage_events(request):
    return {'header': 'welcome', 'login': True, 'username': 'username', 'script': 'manage'}
