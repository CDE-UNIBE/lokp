import logging
from pyramid.view import view_config

from lmkp.views.profile import _getCurrentProfileExtent

log = logging.getLogger(__name__)

@view_config(route_name='view_toolbar_config', renderer='javascript', permission='view')
def view_toolbar_config(request):
    """
    Returns an array of JavaScript objects for users without editing permission.
    """

    _ = request.translate

    # Write the JavaScript and instantiate the global variable Lmkp.ts
    str = "Ext.ns('Lmkp');\n"

    # Flag if user is logged in (editor) or not. This determines if buttons to
    # add or edit Activities or Stakeholders are shown.
    str += "Lmkp.editor = false;\n"

    # Login form: Fields to enter username and password.
    str += "Lmkp.login_form = { border: false, xtype: 'toolbar', defaultType: 'textfield', items: [\n";
    str += "{id: 'username', emptyText: '%s'},\n" % _('Username')
    str += "{id: 'password', emptyText: '%s', inputType: 'password', enableKeyEvents: true},\n" % _('Password')
    str += "{xtype: 'button', id:'login_submit', text: '%s'}]};\n" % _('Login')

    # The current profile extent.
    str += "Lmkp.currentProfileExtent = %s" % _getCurrentProfileExtent(request)

    return str
