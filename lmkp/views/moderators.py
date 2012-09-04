import logging

from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.view import view_config

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

@view_config(route_name='moderator_toolbar_config', renderer='javascript', permission='moderate')
def moderator_toolbar_config(request):

    str = "Ext.namespace('Lmkp');\n"

    str += "Lmkp.login_form = {\n\txtype: 'toolbar',\n\tborder: false,\n\titems: [\n";
    str += "\t\t{xtype: 'label', text: '%s', border: 0, bodyCls: 'toolbar_username'},\n" % _('Logged in as:', default='Logged in as:')
    str += "\t\t{id: 'user_button', text: '%s', tooltip: '%s'},\n" % (request.user.username, _('Show user profile', default='Show user profile'))
    str += "\t\t{id: 'logout_button', text: '%s'}\n\t]\n};\n" % _('Logout', default='Logout')

    str += "Lmkp.moderatorControllers = ['moderator.Main']"

    return str
