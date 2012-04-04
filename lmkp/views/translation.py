import logging
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.view import view_config
import simplejson as json

from ..models.meta import DBSession as Session
from ..models.database_objects import (
    Language,
    A_Key,
    A_Value
)

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

@view_config(route_name='ui_translation', renderer='javascript')
def ui_messages(request):

    # A dictionary that contains all messages that need to be translated in the
    # user interface.
    # Add new messages to this dict!
    uiMap = {
    'zoom-button': _('zoom-button', default='Zoom'),
    'pan-button': _('pan-button', default='Pan'),
    'file-menu': _('file-menu', default='File'),
    'view-menu': _('view-menu', default='View'),
    'activities-title': _('activities-title', default='Activities'),
    'addattributefilter-button': _('addattributefilter-button', default='Add attribute filter'),
    'addattributefilter-tooltip': _('addattributefilter-tooltip', default='Add a filter based on attribute'),
    'addtimefilter-button': _('addtimefilter-button', default='Add time filter'),
    'addtimefilter-tooltip': _('addtimefilter-tooltip', default='Add a filter based on time'),
    'deleteallfilter-button': _('deleteallfilter-button', default='Delete all filters'),
    'deleteallfilter-tooltip': _('deleteallfilter-tooltip', default='Delete all attribute and temporal filters'),
    'filter-title': _('filter-title', default='Filter'),
    'name-column': _('name-column', default='Name'),
    'activitypaging-before': _('activitypaging-before', default='Page'),
    'activitypaging-after': _('activitypaging-after', default='of {0}'),
    'activitypaging-message': _('paging-message', default='Displaying activities {0} - {1} of {2}'),
    'activitypaging-empty': _('activitypaging-empty', default='No activities found'),
    'activate-button': _('activate-button', default='Activate'),
    'activate-tooltip': _('activate-tooltip', default='Click to activate this filter'),
    'delete-button': _('delete-button', default='Delete'),
    'deletefilter-tooltip': _('deletefilter-tooltip', default='Click to delete this filter'),
    'date-label': _('date-label', default='Date'),
    'profile-label': _('profile-label', default='Profile'),
    'language-label': _('language-label', default='Language')
    }

    # Get the localizer
    localizer = get_localizer(request)

    # Translate the user interface messages
    for i in uiMap:
        uiMap[i] = localizer.translate(uiMap[i])

    # Add information about locale to translation file so it is available to Ext
    db_lang = Session.query(Language).filter(Language.locale == localizer.locale_name).first()
    if db_lang is None: # fall back language: english
        db_lang = Language(1, 'English', 'English', 'en')
    uiMap['locale'] = db_lang.locale
    uiMap['locale_english-name'] = db_lang.english_name
    uiMap['locale_local-name'] = db_lang.local_name

    # Write the JavaScript and instantiate the global variable Lmkp.ts
    str = "Ext.namespace('Lmkp');\n"
    str += "Lmkp.ts = Ext.create('Ext.util.MixedCollection');\n" #,{\n"

    # Add a new method that returns the requested key instead of undefined
    # if a key does not exist. Use this method in the ExtJS views.
    str += "Lmkp.ts.msg = function(key) {\n"
    str += "\treturn this.containsKey(key) ? this.get(key) : key;\n"
    str += "};\n"

    # Add all translated keys and values to this MixedCollection
    str += "Lmkp.ts.addAll("
    json_ustr = json.dumps(uiMap, ensure_ascii=False, indent=8, sort_keys=True)
    str += json_ustr.encode('utf-8')
    str += ");\n"

    return str

@view_config(route_name='language_store', renderer='json')
def language_store(request):
    data = []
    langs = Session.query(Language).all()
    for l in langs:
        data.append({
            'locale': l.locale, 
            'english_name': l.english_name, 
            'local_name': l.local_name
        })
    ret = {}
    ret['data'] = data
    ret['success'] = True
    ret['total'] = len(langs)
    return ret

@view_config(route_name='edit_translation', renderer='json')
def edit_translation(request):
    success = False
    msg = 'Translation not successful'
    print request.params
    if 'original' and 'translation' and 'language' and 'keyvalue' in request.params:
        # find language
        language = Session.query(Language).filter(Language.locale == request.params['language']).all()
        if language and len(language) == 1:
            if request.params['keyvalue'] == 'key':
                # find original (fk_a_key empty)
                original = Session.query(A_Key).filter(A_Key.key == request.params['original']).filter(A_Key.fk_a_key == None).all()
                if original and len(original) == 1:
                    # check if a translation of this key is already there
                    oldTranslation = Session.query(A_Key).filter(A_Key.original == original[0]).filter(A_Key.language == language[0]).all()
                    if oldTranslation and len(oldTranslation) == 1:
                        # translation found, just update it.
                        oldTranslation[0].key = request.params['translation']
                        success = True
                        msg = 'Updated translation (<b>%s</b> for key <b>%s</b>.' % (request.params['translation'], request.params['original'])
                    else:
                        # no translation available yet, add it to DB
                        translation = A_Key(request.params['translation'])
                        translation.original = original[0]
                        translation.language = language[0]
                        Session.add(translation)
                        success = True
                        msg = 'Added translation (<b>%s</b>) for key <b>%s</b>.' % (request.params['translation'], request.params['original'])
                else:
                    msg = 'Original key not found' # should never happen
            if request.params['keyvalue'] == 'value':
                # find original (fk_a_value empty)
                original = Session.query(A_Value).filter(A_Value.value == request.params['original']).filter(A_Value.fk_a_value == None).all()
                if original and len(original) == 1:
                    # check if a translation of this value is already there
                    oldTranslation = Session.query(A_Value).filter(A_Value.original == original[0]).filter(A_Value.language == language[0]).all()
                    if oldTranslation and len(oldTranslation) == 1:
                        # translation found, just update it.
                        oldTranslation[0].value = request.params['translation']
                        success = True
                        msg = 'Updated translation (<b>%s</b> for value <b>%s</b>.' % (request.params['translation'], request.params['original'])
                    else:
                        # no translation available yet, add it to DB
                        translation = A_Value(request.params['translation'])
                        translation.original = original[0]
                        translation.language = language[0]
                        Session.add(translation)
                        success = True
                        msg = 'Added translation (<b>%s</b>) for value <b>%s</b>.' % (request.params['translation'], request.params['original'])
                else:
                    msg = 'Original value not found' # should never happen
        else:
            msg = 'Language not unique or not found in DB' # should never happen
    
    return {
        'success': success,
        'msg': msg
    }