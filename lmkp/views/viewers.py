import logging
from pyramid.view import view_config
from pyramid.i18n import TranslationStringFactory

from lmkp.views.profile import _getCurrentProfileExtent

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

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

    # Link to login form
    str += "Lmkp.login_form = { border: false, xtype: 'toolbar', items: [\n"
    str += "{href: '/login', hrefTarget: '', text: '%s', xtype: 'button'},\n" % _(u"Login")
    str += "{href: '/users/register', hrefTarget: '', text: '%s', xtype: 'button'}]};\n" % _(u"Register")

    # The current profile extent.
    str += "Lmkp.currentProfileExtent = %s" % _getCurrentProfileExtent(request)

    return str
