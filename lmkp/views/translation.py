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
    'activitypaging-before': _('activitypaging-before', default='Page'),
    'activitypaging-after': _('activitypaging-after', default='of {0}'),
    'activitypaging-message': _('paging-message', default='Displaying activities {0} - {1} of {2}'),
    'activitypaging-empty': _('activitypaging-empty', default='No activities found'),
    'activity-select': _('activity-select', default='Select an activity above to show its details'),
    'activate-button': _('activate-button', default='Activate'),
    'activate-tooltip': _('activate-tooltip', default='Click to activate this filter'),
    'delete-button': _('delete-button', default='Delete'),
    'deletefilter-tooltip': _('deletefilter-tooltip', default='Click to delete this filter'),
    'date-label': _('date-label', default='Date'),
    'profile-label': _('profile-label', default='Profile'),
    'language-label': _('language-label', default='Language'),
    'unnamed-activity': _('unnamed-activity', default='Unnamed Activity'),
    'status-pending': _('status-pending', default='pending'),
    'status-active': _('status-active', default='active'),
    'status-overwritten': _('status-overwritten', default='overwritten'),
    'status-deleted': _('status-deleted', default='deleted'),
    'status-rejected': _('status-rejected', default='rejected'),
    'loading': _('loading', default='Loading ...'),
    'comment': _('comment', default='Comment'),
    'comments': _('comments', default='Comments'),
    'comments-empty': _('comments-empty', default='No comments yet.'),
    'comments-by': _('comments-by', default='Comment by'),
    'comments-leave': _('comments-leave', default='Leave a comment'),
    'anonymous': _('anonymous', default='Anonymous'),
    'unknown': _('unknown', default='Unknown'),
    'confirm-title': _('confirm-title', default='Please confirm'),
    'confirm-delete-comment': _('confirm-delete-comment', default='Do you really want to delete this comment?'),
    'success': _('success', default='Success'),
    'failure': _('failure', default='Failure'),
    'submit': _('submit', default='Submit')
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
    
    # Add translated name for key "Name of Investor" (needed by Ext as dataIndex when displaying the grid with activities).
    nameofinvestorKeyEnglish = Session.query(A_Key).filter(A_Key.key == 'Name of Investor').filter(A_Key.original == None).first()
    nameofinvestorKeyLocale = Session.query(A_Key).filter(A_Key.original == nameofinvestorKeyEnglish).filter(A_Key.language == db_lang).first()
    if nameofinvestorKeyLocale:
        uiMap['activity-nameofinvestor'] = nameofinvestorKeyLocale.key
    else:
        uiMap['activity-nameofinvestor'] = 'Name of Investor'
    
    # Add translated name for key "Year of Investment" (needed by Ext as dataIndex when displaying the grid with activities).
    yearofinvestmentKeyEnglish = Session.query(A_Key).filter(A_Key.key == 'Year of Investment (agreed)').filter(A_Key.original == None).first()
    yearofinvestmentKeyLocale = Session.query(A_Key).filter(A_Key.original == yearofinvestmentKeyEnglish).filter(A_Key.language == db_lang).first()
    if yearofinvestmentKeyLocale:
        uiMap['activity-yearofinvestment'] = yearofinvestmentKeyLocale.key
    else:
        uiMap['activity-yearofinvestment'] = 'Year of Investment (agreed)'

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

@view_config(route_name='edit_translation', renderer='json', permission='administer')
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
                        msg = 'Updated translation (<b>%s</b>) for value <b>%s</b>.' % (request.params['translation'], request.params['original'])
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