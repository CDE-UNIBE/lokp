import logging
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.view import view_config
import simplejson as json

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

@view_config(route_name='view_toolbar_config', renderer='javascript', permission='view')
def view_toolbar_config(request):
    """
    Returns an array of objects that configure an ExtJS toolbar for users without
    editing permission.
    """

    # Write the JavaScript and instantiate the global variable Lmkp.ts
    str = "Ext.ns('Lmkp');\n"
    str += "Lmkp.toolbar = false;\n"
    
    str += "Lmkp.login_form = { border: false, xtype: 'toolbar', defaultType: 'textfield', items: [\n";
    str += "{id: 'username', emptyText: '%s'},\n" % _('Username', default='Username')
    str += "{id: 'password', emptyText: '%s', inputType: 'password'},\n" % _('Password', default='Password')
    str += "{xtype: 'button', id:'login_submit', text: '%s'}]};\n" % _('Login', default='Login')

    str += "Lmkp.mainControllers = ['Main', 'Layers', 'Map', 'Filter', 'Stakeholder'];\n"

    return str
