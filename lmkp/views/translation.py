import logging
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.view import view_config
import simplejson as json

from ..models.meta import DBSession as Session
from ..models.database_objects import (
    Language,
    A_Key,
    A_Value,
    SH_Key,
    SH_Value
)

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

# Translatable hashmap with all possible status
statusMap = {
    'pending': _('pending', default='pending'),
    'active': _('active', default='active'),
    'inactive': _('inactive', default='inactive'),
    'deleted': _('deleted', default='deleted'),
    'rejected': _('rejected', default='rejected'),
    'edited': _('edited', default='edited')
}

@view_config(route_name='ui_translation', renderer='javascript')
def ui_messages(request):

    # A dictionary that contains all messages that need to be translated in the
    # user interface.
    # Add new messages to this dict!
    uiMap = {
        # map functions
        'zoom-button': _('zoom-button', default='Zoom'),
        'pan-button': _('pan-button', default='Pan'),
        # general GUI text
        'file-menu': _('file-menu', default='File'),
        'view-menu': _('view-menu', default='View'),
        'date-label': _('date-label', default='Date'),
        'profile-label': _('profile-label', default='Profile'),
        'language-label': _('language-label', default='Language'),
        'loading': _('loading', default='Loading ...'),
        'unknown': _('unknown', default='Unknown'),
        'confirm-title': _('confirm-title', default='Please confirm'),
        'success': _('success', default='Success'),
        'failure': _('failure', default='Failure'),
        'submit': _('submit', default='Submit'),
        'id': _('id', default='ID'),
        'edit': _('edit', default='edit'),
        'details': _('details', default='details'),
        'map-view': _('map-view', default='Map View'),
        'version': _('version', default='Version'),
        'yes': _('yes', default='Yes'),
        'no': _('no', default='No'),
        'ok': _('ok', default='OK'),
        'cancel': _('cancel', default='Cancel'),
        # activities / filtering
        'activities-title': _('activities-title', default='Activities'),
        'activities-table_view': _('activities-table_view', default='Activities Table View'),
        'activities-add_further_information': _('activities-add_further_information', default='Submit further information to an existing activity'),
        'addattributefilter-button': _('addattributefilter-button', default='Add attribute filter'),
        'addattributefilter-tooltip': _('addattributefilter-tooltip', default='Add a filter based on attribute'),
        'addtimefilter-button': _('addtimefilter-button', default='Add time filter'),
        'addtimefilter-tooltip': _('addtimefilter-tooltip', default='Add a filter based on time'),
        'deleteallfilter-button': _('deleteallfilter-button', default='Delete all filters'),
        'deleteallfilter-tooltip': _('deleteallfilter-tooltip', default='Delete all attribute and temporal filters'),
        'filter-activity_title': _('filter-title', default='Filter Activities'),
        'filter-apply_spatial': _('filter-apply_spatial', default='Apply spatial filter'),
        'filter-connect_to_activities': _('filter-connect_to_activities', default='Combine with filter on Activities'),
        'filter-connect_to_stakeholders': _('filter-connect_to_stakeholders', default='Combine with filter on Stakeholders'),
        'activitypaging-before': _('activitypaging-before', default='Page'),
        'activitypaging-after': _('activitypaging-after', default='of {0}'),
        'activitypaging-message': _('paging-message', default='Displaying activities {0} - {1} of {2}'),
        'activitypaging-empty': _('activitypaging-empty', default='No activities found'),
        'activity-select': _('activity-select', default='Select an activity to show its details'),
        'activate-button': _('activate-button', default='Activate'),
        'activate-tooltip': _('activate-tooltip', default='Click to activate this filter'),
        'delete-button': _('delete-button', default='Delete'),
        'deletefilter-tooltip': _('deletefilter-tooltip', default='Click to delete this filter'),
        # stakeholders
        'stakeholders-title': _('stakeholder-title', default='Stakeholders'),
        'stakeholders-table_view': _('stakeholders-table_view', default='Stakeholders Table View'),
        'stakeholder-name': _('stakholder-name', default='Name'),
        'stakeholder-country': _('stakholder-country', default='Country'),
        'filter-stakeholder_title': _('filter-stakeholder_title', default='Filter Stakeholders'),
        'stakeholder-paging_message': _('stakeholder-paging_message', default='Displaying stsakeholders {0} - {1} of {2}'),
        'stakeholder-paging_empty': _('stakeholder-paging_empty', default='No stakeholders found'),
        # involvements
        'involvements-title': _('involvements-title', default='Involvement'),
        'involvements-role': _('involvements-role', default='Role'),
        # details
        'details-toggle_all': _('details-toggle_all', default='Toggle all details'),
        # status
        # Maybe hashmap (see top) could be used? > Used by store/Status.js
        'status-pending': _('status-pending', default='pending'),
        'status-active': _('status-active', default='active'),
        'status-inactive': _('status-inactive', default='inactive'),
        'status-deleted': _('status-deleted', default='deleted'),
        'status-rejected': _('status-rejected', default='rejected'),
        'status-edited': _('status-edited', default='edited'),
        # comments
        'comment': _('comment', default='Comment'),
        'comments': _('comments', default='Comments'),
        'comments-empty': _('comments-empty', default='No comments yet.'),
        'comments-by': _('comments-by', default='Comment by'),
        'comments-leave': _('comments-leave', default='Leave a comment'),
        'anonymous': _('anonymous', default='Anonymous'),
        'confirm-delete-comment': _('confirm-delete-comment', default='Do you really want to delete this comment?'),
        # reviews
        'reviewpanel-empty_msg': _('reviewpanel-empty_msg', default='Select an item on the left.'),
        'reviewpanel-multiple_changes': _('reviewpanel-multiple_changes', default='There are multiple changes pending! They may be conflicting.'),
        'reviewpanel-not_active_changed': _('reviewpanel-not_active_changed', default='These changes are based on a version which is not the active version.'),
        'reviewpanel-pending_title': _('reviewpanel-pending_title', default='Pending version'),
        'reviewpanel-previous_title': _('reviewpanel-previous_title', default='Previous version'),
        'review-diff_title': _('review-diff_title', default='Difference'),
        'review-diff_inv_added': _('review-diff_inv_added', default='Involvement added'),
        'review-diff_inv_deleted': _('review-diff_inv_deleted', default='Involvement deleted'),
        'review-diff_attr_added': _('review-diff_attr_added', default='Attribute(s) added'),
        'review-diff_attr_deleted': _('review-diff_attr_deleted', default='Attribute(s) deleted'),
        'reviewdecision-approved': _('reviewdecision-approved', default='approved'),
        'reviewdecision-rejected': _('reviewdecision-rejected', default='rejected'),
        # filter operators
        'filter-operator_is': _('filter-operator_is', default='is'),
        'filter-operator_is-not': _('filter-operator_is-not', default='is not'),
        'filter-operator_contains-case-sensitive': _('filter-operator_contains-case-sensitive', default='contains (case sensitive)'),
        'filter-operator_contains-case-insensitive': _('filter-operator_contains-case-insensitive', default='contains (case insensitive)'),
        'filter-operator_contains-not-case-sensitive': _('filter-operator_contains-not-case-sensitive', default='contains not (case sensitive)'),
        'filter-operator_contains-not-case-insensitive': _('filter-operator_contains-not-case-insensitive', default='contains not (case insensitive)'),
        'filter-operator_equals': _('filter-operator_equals', default='equals'),
        'filter-operator_less-than': _('filter-operator_less-than', default='less than'),
        'filter-operator_less-than-or-equal': _('filter-operator_less-than-or-equal', default='less than or equal'),
        'filter-operator_greater-than-or-equal': _('filter-operator_greater-than-or-equal', default='greater than or equal'),
        'filter-operator_greater-than': _('filter-operator_greater-than', default='greater than'),
        'filter-operator_not-equals': _('filter-operator_not-equals', default='not equals')
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
    
    # TODO: is this still needed?
    # Add translated name for key "Name of Investor" (needed by Ext as dataIndex when displaying the grid with activities).
    nameofinvestorKeyEnglish = Session.query(A_Key).filter(A_Key.key == 'Country').filter(A_Key.original == None).first()
    nameofinvestorKeyLocale = Session.query(A_Key).filter(A_Key.original == nameofinvestorKeyEnglish).filter(A_Key.language == db_lang).first()
    if nameofinvestorKeyLocale:
        uiMap['activity-attr_country'] = nameofinvestorKeyLocale.key
    else:
        uiMap['activity-attr_country'] = 'Country'
    
    # Add translated name for key "Year of Investment" (needed by Ext as dataIndex when displaying the grid with activities).
    yearofinvestmentKeyEnglish = Session.query(A_Key).filter(A_Key.key == 'Year of Investment (agreed)').filter(A_Key.original == None).first()
    yearofinvestmentKeyLocale = Session.query(A_Key).filter(A_Key.original == yearofinvestmentKeyEnglish).filter(A_Key.language == db_lang).first()
    if yearofinvestmentKeyLocale:
        uiMap['activity-attr_yearofinvestment'] = yearofinvestmentKeyLocale.key
    else:
        uiMap['activity-attr_yearofinvestment'] = 'Year of Investment (agreed)'

    # Add translated name for SH_Key "Name" (needed by Ext as dataIndex when displaying the grid with stakeholders)
    shNameKeyEnglish = Session.query(SH_Key).filter(SH_Key.key == 'Name').filter(SH_Key.original == None).first()
    shNameKeyLocale = Session.query(SH_Key).filter(SH_Key.original == shNameKeyEnglish).filter(SH_Key.language == db_lang).first()
    uiMap['stakeholder-attr_name'] = (shNameKeyLocale.key 
        if shNameKeyLocale is not None else 'Name')
    
    # Add translated name for SH_Key "Country" (needed by Ext as dataIndex when displaying the grid with stakeholders)
    shNameKeyEnglish = Session.query(SH_Key).filter(SH_Key.key == 'Country').filter(SH_Key.original == None).first()
    shNameKeyLocale = Session.query(SH_Key).filter(SH_Key.original == shNameKeyEnglish).filter(SH_Key.language == db_lang).first()
    uiMap['stakeholder-attr_country'] = (shNameKeyLocale.key 
        if shNameKeyLocale is not None else 'Country')
        
        
    # Write the JavaScript and instantiate the global variable Lmkp.ts
    #str = "Ext.namespace('Lmkp');\n"
    #str += "Lmkp.ts = Ext.create('Ext.util.MixedCollection');\n" #,{\n"

    # Add a new method that returns the requested key instead of undefined
    # if a key does not exist. Use this method in the ExtJS views.
    #str += "Lmkp.ts.msg = function(key) {\n"
    #str += "\treturn this.containsKey(key) ? this.get(key) : key;\n"
    #str += "};\n"

    # Add all translated keys and values to this MixedCollection
    #str += "Lmkp.ts.addAll("
    #json_ustr = json.dumps(uiMap, ensure_ascii=False, indent=8, sort_keys=True)
    #str += json_ustr.encode('utf-8')
    #str += ");\n"

    # Define Lmkp.ts as class with static objects
    str = "Ext.define('Lmkp.ts',{\n"
    str += "\tstatics: {\n"
    str += "\t\tstrings: "
    json_ustr = json.dumps(uiMap, ensure_ascii=False, indent=8, sort_keys=True)
    str += json_ustr.encode('utf-8')
    str += ",\n"

    str += "\t\tmsg: function(key) {\n"
    str += "\t\t\treturn this.strings[key] ? this.strings[key] : key;\n"
    str += "\t\t}\n"
    str += "\t}\n"

    str += "});"

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