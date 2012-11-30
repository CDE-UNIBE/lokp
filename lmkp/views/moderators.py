import logging
from pyramid.view import view_config

from lmkp.views.profile import _getCurrentProfileExtent

log = logging.getLogger(__name__)

class ToolbarHandler(object):

    def __init__(self, context, request):
        self.request = request

    @view_config(route_name='moderator_toolbar_config', renderer='javascript', permission='moderate')
    def moderator_toolbar_config(self):
        """
        Returns an array of JavaScript objects for users with moderating permission.
        """

        _ = self.request.translate

        # Write the JavaScript and instantiate the global variable Lmkp.ts
        str = "Ext.namespace('Lmkp');\n"

        # Flag if user is logged in (editor) or not. This determines if buttons to
        # add or edit Activities or Stakeholders are shown.
        str += "Lmkp.editor = true;\n"

        # Login form: Show current user and button to log out.
        str += "Lmkp.login_form = {\n\txtype: 'toolbar',\n\tborder: false,\n\titems: [\n";
        str += "\t\t{xtype: 'label', text: \"%s\", border: 0, bodyCls: 'toolbar_username'},\n" % _('Logged in as:')
        str += "\t\t{id: 'user_button', text: \"%s\", tooltip: \"%s\"},\n" % (self.request.user.username, _('Show user profile'))
        str += "\t\t{id: 'logout_button', text: \"%s\"}\n\t]\n};\n" % _('Logout')

        # Specific controllers for moderators. The ones for editors need to be
        # included as well.
        str += "Lmkp.moderatorControllers = ['moderator.Main', 'moderator.Details', 'activities.NewActivity', 'editor.Map', 'stakeholders.NewStakeholder'];\n"

        # The current profile extent.
        str += "Lmkp.currentProfileExtent = %s" % _getCurrentProfileExtent(self.request)

        return str
