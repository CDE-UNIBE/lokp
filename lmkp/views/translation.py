import logging
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.view import view_config

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

@view_config(route_name='ui_translation', renderer='json')
def get_language_store_config(request):

    lang = request.matchdict.get('lang', 'en')

    localizer = get_localizer(request)

    uiMap = {
    'zoom-button': _('zoom-button', default='Zoom'),
    'pan-button': _('pan-button', default='Pan')
    }

    records = []
    for i in uiMap:
        records.append({'msgid': i, 'msgstr': localizer.translate(uiMap[i])})

    return records