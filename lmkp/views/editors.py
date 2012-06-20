import logging
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.view import view_config
import simplejson as json

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

@view_config(route_name='edit_toolbar_config', renderer='javascript', permission='edit')
def edit_toolbar_config(request):
    """
    Returns an array of objects that configure an ExtJS toolbar for users with
    editing permission.
    """
    
    # Write the JavaScript and instantiate the global variable Lmkp.ts
    str = "Ext.namespace('Lmkp');\n"
    str += "Lmkp.toolbar = [{"
    str += "xtype: 'toolbar', dock: 'bottom', items: ['->',"
    str += "{id: 'add-taggroup-button', text: '%s', tooltip: '%s'}," % (_('Add further information', default='Add further information'), _('Submit further information to an existing activity', default='Submit further information to an existing activity'))
    str += "{id: 'add-activity-button', text: '%s', tooltip: '%s'}" % (_('Add new activity', default='Add new activity'), _('Submit information about a new activity', default='Submit information about a new activity'))
    str += "]}];\n"
    
    str += "Lmkp.login_form = [{xtype: 'panel', html: '%s', border: 0, bodyCls: 'toolbar_username'}," % _('Logged in as:', default='Logged in as:')
    str += "{id: 'user_button', text: '%s', tooltip: '%s'},'-'," % (request.user.username, _('Show user profile', default='Show user profile'))
    str += "{id: 'logout_button', text: '%s'}];\n" % _('Logout', default='Logout')

    str += "Lmkp.mainControllers = ['Main', 'Map', 'Filter', 'Stakeholder','EditFilter'];\n"

    return str

