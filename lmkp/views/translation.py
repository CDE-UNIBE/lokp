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

# Translatable hashmap with all possible statuses
statusMap = {
    'pending': _('status_pending', default='pending'),
    'active': _('status_active', default='active'),
    'inactive': _('status_inactive', default='inactive'),
    'deleted': _('status_deleted', default='deleted'),
    'rejected': _('status_rejected', default='rejected'),
    'edited': _('status_edited', default='edited')
}

@view_config(route_name='ui_translation', renderer='javascript')
def ui_messages(request):

    # A dictionary that contains all messages that need to be translated in the
    # user interface.
    # Add new messages to this dict!
    uiMap = {
        # Status
        'status_name': _('status_name', default='Status'),
        'status_pending': statusMap['pending'],
        'status_active': statusMap['active'],
        'status_inactive': statusMap['inactive'],
        'status_deleted': statusMap['deleted'],
        'status_rejected': statusMap['rejected'],
        'status_edited': statusMap['edited'],

        # Buttons
        'button_back': _('button_back', default='Back'),
        'button_map_base-layers': _('button_map_base-layers', default='Base Layers'),
        'button_map_context-layers': _('button_map_context-layers', default='Context Layers'),
        'button_map_satellite-map': _('button_map_satellite-map', default='Satellite Imagery'),
        'button_map_show-legend': _('button_map_show-legend', default='Show Legend'),
        'button_map_street-map': _('button_map_street-map', default='Street Map'),
        'button_map_terrain-map': _('button_map_terrain-map', default='Terrain Map'),

        # Tooltips
        'tooltip_map_identify-feature': _('tooltip_map_identify-feature', default='Identify Feature'),
        'tooltip_map_pan': _('tooltip_map_pan', default='Pan'),
        'tooltip_map_zoom-in': _('tooltip_map_zoom-in', default='Zoom In'),
        'tooltip_map_zoom-out': _('tooltip_map_zoom-out', default='Zoom Out'),
        'tooltip_map_zoom-to-profile-region': _('tooltip_map_zoom-to-profile-region', default='Zoom to Profile Region'),

        # General GUI text
        'gui_clear-selection': _('gui_clear-selection', default='Clear Selection'),
        'gui_delete-all-filters': _('gui_delete-all-filters', default='Delete all Filters'),
        'gui_details': _('gui_details', default='Details'),
        'gui_filter-count': _('gui_filter-count', default='Filter ({0} active)'),
        'gui_history': _('gui_history', default='History'),
        'gui_language': _('gui_language', default='Language'),
        'gui_loading': _('gui_loading', default='Loading ...'),
        'gui_paging-before': _('gui_paging-before', default='Page'),
        'gui_paging-after': _('gui_paging-after', default='of {0}'),
        'gui_profile': _('gui_profile', default='Profile'),
        'gui_show-details': _('gui_show-details', default='Show Details'),
        'gui_timestamp': _('gui_timestamp', default='Timestamp'),
        'gui_unknown': _('gui_unknown', default='Unknown'),
        'gui_version': _('gui_version', default='Version'),
        'gui_previous-version': _('gui_previous-version', default='Previous Version'),

        # Activities
        'activities_title': _('activities_title', default='Activities'),
        'activities_paging-message': _('activities_paging-message', default='Displaying Activities {0} - {1} of {2}'),
        'activities_paging-empty': _('activities_paging-empty', default='No Activities found'),
        'activities_add-new-activity': _('activities_add-new-activity', default='Add new Activity'),
        'activity_details-title': _('activities_details-title', default='Details on Activity'),

        # Stakeholders
        'stakeholders_title': _('stakeholder_title', default='Stakeholders'),
        'stakeholders_paging-message': _('stakeholders_paging-message', default='Displaying stakeholders {0} - {1} of {2}'),
        'stakeholders_paging-empty': _('stakeholders_paging-empty', default='No stakeholders found'),
        'stakeholder_details-title': _('stakeholders_details-title', default='Details on Stakeholder '),

        # Moderator
        'moderator_show-pending-changes': _('moderator_show-pending-changes', default='Show pending changes'),
        'moderator_review-pending-changes': _('moderator_review-pending-changes', default='Review pending changes'),
        'moderator_changes-not-based-on-active': _('moderator_changes-not-based-on-active', default='These changes are based on a version which is not the active version.'),
        'moderator_multiple-changes-pending': _('moderator_multiple-changes-pending', default='There are multiple changes pending! They may be conflicting.'),
        'moderator_pending-version-title': _('moderator_pending-version-title', default='Pending version'),

        'file-menu': _('file-menu', default='File'),
        'view-menu': _('view-menu', default='View'),
        'date-label': _('date-label', default='Date'),
        'unknown-name': _('unknown-name', default='Unknown name'),
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
        'activity-select': _('activity-select', default='Select an activity to show its details'),
        'activate-button': _('activate-button', default='Activate'),
        'activate-tooltip': _('activate-tooltip', default='Click to activate this filter'),
        'delete-button': _('delete-button', default='Delete'),
        'deletefilter-tooltip': _('deletefilter-tooltip', default='Click to delete this filter'),
        # stakeholders
        'stakeholders-table_view': _('stakeholders-table_view', default='Stakeholders Table View'),
        'stakeholder-name': _('stakholder-name', default='Name'),
        'stakeholder-country': _('stakholder-country', default='Country'),
        'filter-stakeholder_title': _('filter-stakeholder_title', default='Filter Stakeholders'),
        # involvements
        'involvements-title': _('involvements-title', default='Involvement'),
        'involvements-role': _('involvements-role', default='Role'),
        # details
        'details-toggle_all': _('details-toggle_all', default='Toggle all details'),

        # comments
        'comment': _('comment', default='Comment'),
        'comments': _('comments', default='Comments'),
        'comments-empty': _('comments-empty', default='No comments yet.'),
        'comments-by': _('comments-by', default='Comment by'),
        'comments-leave': _('comments-leave', default='Leave a comment'),
        'anonymous': _('anonymous', default='Anonymous'),
        'confirm-delete-comment': _('confirm-delete-comment', default='Do you really want to delete this comment?'),
        # reviews
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

    """
    For the table view of Activities and Stakeholders, Ext needs to know the key
    from the database (for example to correctly address table columns). It is
    also necessary to check if there are translations of these keys available.
    However, where columns are to be sorted, the original data index needs to be
    known as well.
    See the first example for details how this is done.
    """

    # Activity key: Country
    aKeyCountry = 'Country' # Must be exactly (!) as in global activity.yml

    # Prepare a query for the original key (original == None)
    original_query = Session.query(
            A_Key.id,
            A_Key.key
        ).\
        filter(A_Key.key == aKeyCountry).\
        filter(A_Key.original == None)

    # A subquery is needed to correctly join the translated query with the
    # original key
    original_subquery = original_query.subquery()

    # Prepare a query for the translated key (original == original key from
    # query above)
    translation_query = Session.query(
            A_Key.id,
            A_Key.key
        ).\
        join(original_subquery, original_subquery.c.id == A_Key.fk_a_key).\
        filter(A_Key.language == db_lang)
    
    # Also store the original of the key (needed for sorting)
    uiMap['activity_db-key-country-original'] = aKeyCountry

    # Union and do a single query. The original is always the first, so if there is a 
    # translated entry (2nd), simply overwrite the original.
    uiMap['activity_db-key-country'] = aKeyCountry # Fallback
    for k in original_query.union(translation_query).all():
        uiMap['activity_db-key-country'] = k.key

    # Activity key: Year of Agreement
    aKeyYearofagreement = 'Year of agreement' # Must be exactly (!) as in global activity.yml
    original_query = Session.query(A_Key.id, A_Key.key).\
        filter(A_Key.key == aKeyYearofagreement).\
        filter(A_Key.original == None)
    original_subquery = original_query.subquery()
    translation_query = Session.query(A_Key.id, A_Key.key).\
        join(original_subquery, original_subquery.c.id == A_Key.fk_a_key).\
        filter(A_Key.language == db_lang)
    uiMap['activity_db-key-yearofagreement-original'] = aKeyYearofagreement
    uiMap['activity_db-key-yearofagreement'] = aKeyYearofagreement
    for k in original_query.union(translation_query).all():
        uiMap['activity_db-key-yearofagreement'] = k.key

    # Activity key: Contract area
    aKeyContractarea = 'Contract area (ha)' # Must be exactly (!) as in global activity.yml
    original_query = Session.query(A_Key.id, A_Key.key).\
        filter(A_Key.key == aKeyContractarea).\
        filter(A_Key.original == None)
    original_subquery = original_query.subquery()
    translation_query = Session.query(A_Key.id, A_Key.key).\
        join(original_subquery, original_subquery.c.id == A_Key.fk_a_key).\
        filter(A_Key.language == db_lang)
    uiMap['activity_db-key-contractarea-original'] = aKeyContractarea
    uiMap['activity_db-key-contractarea'] = aKeyContractarea
    for k in original_query.union(translation_query).all():
        uiMap['activity_db-key-contractarea'] = k.key

    # Stakeholder key: Name
    shKeyName = 'Name' # Must be exactly (!) as in global stakeholder.yml
    original_query = Session.query(SH_Key.id, SH_Key.key).\
        filter(SH_Key.key == shKeyName).\
        filter(SH_Key.original == None)
    original_subquery = original_query.subquery()
    translation_query = Session.query(SH_Key.id, SH_Key.key).\
        join(original_subquery, original_subquery.c.id == SH_Key.fk_sh_key).\
        filter(SH_Key.language == db_lang)
    uiMap['stakeholder_db-key-name-original'] = shKeyName
    uiMap['stakeholder_db-key-name'] = shKeyName
    for k in original_query.union(translation_query).all():
        uiMap['stakeholder_db-key-name'] = k.key

    # Stakeholder key: Country
    shKeyCountry = 'Country' # Must be exactly (!) as in global stakeholder.yml
    original_query = Session.query(SH_Key.id, SH_Key.key).\
        filter(SH_Key.key == shKeyCountry).\
        filter(SH_Key.original == None)
    original_subquery = original_query.subquery()
    translation_query = Session.query(SH_Key.id, SH_Key.key).\
        join(original_subquery, original_subquery.c.id == SH_Key.fk_sh_key).\
        filter(SH_Key.language == db_lang)
    uiMap['stakeholder_db-key-country-original'] = shKeyCountry
    uiMap['stakeholder_db-key-country'] = shKeyCountry
    for k in original_query.union(translation_query).all():
        uiMap['stakeholder_db-key-country'] = k.key

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
    if 'original' and 'translation' and 'language' and 'keyvalue' and 'item_type' in request.params:
        # find language
        language = Session.query(Language).filter(Language.locale == request.params['language']).all()
        if language and len(language) == 1:
            if request.params['keyvalue'] == 'key':
                # Activity or Stakeholder?
                Key = None
                if request.params['item_type'] == 'activity':
                    Key = A_Key
                elif request.params['item_type'] == 'stakeholder':
                    Key = SH_Key
                # find original (fk_a_key empty)
                original = Session.query(Key).filter(Key.key == request.params['original']).filter(Key.original == None).all()
                if original and len(original) == 1:
                    # check if a translation of this key is already there
                    oldTranslation = Session.query(Key).filter(Key.original == original[0]).filter(Key.language == language[0]).all()
                    if oldTranslation and len(oldTranslation) == 1:
                        # translation found, just update it.
                        oldTranslation[0].key = request.params['translation']
                        success = True
                        msg = 'Updated translation (<b>%s</b> for key <b>%s</b>.' % (request.params['translation'], request.params['original'])
                    else:
                        # no translation available yet, add it to DB
                        translation = Key(request.params['translation'])
                        translation.original = original[0]
                        translation.language = language[0]
                        Session.add(translation)
                        success = True
                        msg = 'Added translation (<b>%s</b>) for key <b>%s</b>.' % (request.params['translation'], request.params['original'])
                else:
                    msg = 'Original key not found' # should never happen
            if request.params['keyvalue'] == 'value':
                # Activity or Stakeholder?
                Value = None
                if request.params['item_type'] == 'activity':
                    Value = A_Value
                elif request.params['item_type'] == 'stakeholder':
                    Value = SH_Value
                # find original (fk_a_value empty)
                original = Session.query(Value).filter(Value.value == request.params['original']).filter(Value.original == None).all()
                if original and len(original) == 1:
                    # check if a translation of this value is already there
                    oldTranslation = Session.query(Value).filter(Value.original == original[0]).filter(Value.language == language[0]).all()
                    if oldTranslation and len(oldTranslation) == 1:
                        # translation found, just update it.
                        oldTranslation[0].value = request.params['translation']
                        success = True
                        msg = 'Updated translation (<b>%s</b>) for value <b>%s</b>.' % (request.params['translation'], request.params['original'])
                    else:
                        # no translation available yet, add it to DB
                        translation = Value(request.params['translation'])
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

def get_translated_status(request, status):
    """
    Get the translated name of a status. A request is needed to know in which
    language to translate
    """
    localizer = get_localizer(request)
    if status in statusMap:
        return localizer.translate(statusMap[status])