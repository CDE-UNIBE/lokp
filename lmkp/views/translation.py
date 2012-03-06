import logging
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.view import view_config

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

@view_config(route_name='ui_translation', renderer='string')
def get_language_store_config(request):

    lang = request.matchdict.get('lang', 'en')

    localizer = get_localizer(request)

    uiMap = {
    'zoom-button': _('zoom-button', default='Zoom'),
    'pan-button': _('pan-button', default='Pan'),
    'file-menu': _('file-menu', default='File'),
    'view-menu': _('view-menu', default='View'),
    }

    str = "Ext.namespace('Lmkp');Lmkp.ts = Ext.create('Ext.util.HashMap',{alias:['ts']});"
    for i in uiMap:
        str = "%sLmkp.ts.add('%s','%s');" % (str, i, localizer.translate(uiMap[i]))

    return str