import logging

from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.view import view_config

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

@view_config(route_name='moderator_toolbar_config', renderer='javascript', permission='moderate')
def moderator_toolbar_config(request):

    str = "Ext.namespace('Lmkp.moderator');\n"
    str += "Lmkp.moderator.toolbar = [{\n"

    str += "}];\n"
    
    str += "Lmkp.moderator.showPendingActivitiesCheckbox = {\n"
    str += "boxLabel: 'Activities with pending changes', checked: true, itemId: 'showPendingActivitiesCheckbox', xtype: 'checkbox'\n"
    str += "};\n"

    str += "Lmkp.moderator.showPendingStakeholdersCheckbox = {\n"
    str += "boxLabel: 'Stakeholders with pending changes', checked: true, itemId: 'showPendingStakeholdersCheckbox', xtype: 'checkbox'\n"
    str += "};\n"

    str += "Lmkp.login_form = {xtype: 'toolbar', border: false, items: [\n";
    str += "{xtype: 'label', text: '%s', border: 0, bodyCls: 'toolbar_username'},\n" % _('Logged in as:', default='Logged in as:')
    str += "{id: 'user_button', text: '%s', tooltip: '%s'},\n" % (request.user.username, _('Show user profile', default='Show user profile'))
    str += "{id: 'logout_button', text: '%s'}]};\n" % _('Logout', default='Logout')


    return str
