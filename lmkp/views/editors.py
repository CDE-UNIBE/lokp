import logging
from pyramid.view import view_config

from lmkp.views.profile import _getCurrentProfileExtent

log = logging.getLogger(__name__)

@view_config(route_name='edit_toolbar_config', renderer='javascript', permission='edit')
def edit_toolbar_config(request):
    """
    Returns an array of JavaScript objects for users with editing permission.
    """

    _ = request.translate
    
    # Write the JavaScript and instantiate the global variable Lmkp.ts
    str = "Ext.namespace('Lmkp');\n"

    # Flag if user is logged in (editor) or not. This determines if buttons to
    # add or edit Activities or Stakeholders are shown.
    str += "Lmkp.editor = true;\n"

    # Login form: Show current user and button to log out.
    str += "Lmkp.login_form = {xtype: 'toolbar', border: false, items: [\n";
    str += "{xtype: 'label', text: '%s', border: 0, bodyCls: 'toolbar_username'},\n" % _('Logged in as:')
    str += "{id: 'user_button', text: '%s', tooltip: '%s'},\n" % (request.user.username, _('Show user profile'))
    str += "{id: 'logout_button', text: '%s'}]};\n" % _('Logout')

    # Specific controllers for editors.
    str += "Lmkp.editorControllers = ['activities.NewActivity', 'editor.Map', 'stakeholders.NewStakeholder'];\n"

    # The current profile extent.
    str += "Lmkp.currentProfileExtent = %s" % _getCurrentProfileExtent(request)

    return str

