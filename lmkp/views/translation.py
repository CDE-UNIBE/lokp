import logging

from lmkp.models.database_objects import A_Key
from lmkp.models.database_objects import A_Value
from lmkp.models.database_objects import Language
from lmkp.models.database_objects import SH_Key
from lmkp.models.database_objects import SH_Value
from lmkp.models.meta import DBSession as Session
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.view import view_config
import simplejson as json
from sqlalchemy.orm import aliased

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

# Translatable hashmap with all possible statuses
reviewdecisionMap = {
    'approved': _('reviewdecision_approved', default='approved'),
    'rejected': _('reviewdecision_rejected', default='rejected')
}

# Translatable hashmap with all possible user groups
usergroupMap = {
    'editors': _('usergroup_editors', default='Editors'),
    'moderators': _('usergroup_moderators', default='Moderators'),
    'administrators': _('usergroup_administrators', default='Administrators')
}

# Translatable hashmap with all possible user roles
# TODO: Once the involvements attributes are properly solved using YAML or
# something similar, the translation of the roles should not happen here anymore
stakeholderroleMap = {
    'Investor': _('stakeholderrole_investor', default='Investor')
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

        # Review decision
        'reviewdecision_approved': reviewdecisionMap['approved'],
        'reviewdecision_rejected': reviewdecisionMap['rejected'],

        # User groups
        'usergroup_editors': usergroupMap['editors'],
        'usergroup_moderators': usergroupMap['moderators'],
        'usergroup_administrators': usergroupMap['administrators'],

        # Buttons
        'button_add-attribute-filter': _('button_add-attribute-filter', default='Add attribute filter'),
        'button_add-new-tag': _('button_add-new-tag', default='Add more specific information'),
        'button_add-new-taggroup': _('button_add-new-taggroup', default='Add further information'),
        'button_add-time-filter': _('button_add-time-filter', default='Add time filter'),
        'button_back': _('button_back', default='Back'),
        'button_cancel': _('button_cancel', default='Cancel'),
        'button_clear': _('button_clear', default='Clear'),
        'button_close': _('button_close', default='Close'),
        'button_continue': _('button_continue', default='Continue'),
        'button_delete': _('button_delete', default='Delete'),
        'button_edit': _('button_edit', default='Edit'),
        'button_filter-activate': _('button_filter-activate', default='Activate'),
        'button_filter-delete': _('button_filter-delete', default='Delete'),
        'button_link': _('button_link', default='Link'),
        'button_map_base-layers': _('button_map_base-layers', default='Base Layers'),
        'button_map_context-layers': _('button_map_context-layers', default='Context Layers'),
        'button_map_satellite-map': _('button_map_satellite-map', default='Satellite Imagery'),
        'button_map_show-legend': _('button_map_show-legend', default='Show Legend'),
        'button_map_street-map': _('button_map_street-map', default='Street Map'),
        'button_map_terrain-map': _('button_map_terrain-map', default='Terrain Map'),
        'button_next': _('button_next', default='Next'),
        'button_no': _('button_no', default='No'),
        'button_ok': _('button_ok', default='OK'),
        'button_refresh': _('button_refresh', default='Refresh'),
        'button_submit': _('button_submit', default='Submit'),
        'button_yes': _('button_yes', default='Yes'),

        # Tooltips
        'tooltip_add-attribute-filter': _('tooltip_add-attribute-filter', default='Add a filter based on attribute'),
        'tooltip_add-time-filter': _('tooltip_add-time-filter', default='Add a filter based on time'),
        'tooltip_close-window': _('tooltip_close-window', default='Close Window'),
        'tooltip_filter-activate': _('tooltip_filter-activate', default='Click to activate this filter'),
        'tooltip_filter-delete': _('tooltip_filter-delete', default='Click to delete this filter'),
        'tooltip_map_identify-feature': _('tooltip_map_identify-feature', default='Identify Feature'),
        'tooltip_map_pan': _('tooltip_map_pan', default='Pan'),
        'tooltip_map_zoom-in': _('tooltip_map_zoom-in', default='Zoom In'),
        'tooltip_map_zoom-out': _('tooltip_map_zoom-out', default='Zoom Out'),
        'tooltip_map_zoom-to-profile-region': _('tooltip_map_zoom-to-profile-region', default='Zoom to Profile Region'),
        'tooltip_remove-stakeholder': _('tooltip_remove-stakeholder', default='Remove this stakeholder'),

        # General GUI text
        'gui_anonymous': _('gui_anonymous', default='Anonymous'),
        'gui_clear-selection': _('gui_clear-selection', default='Clear Selection'),
        'gui_confirm': _('gui_confirm', default='Please confirm'),
        'gui_currently-seeing-pending-version': _('gui_currently-seeing-pending-version', default='You are seeing a {0} version, which needs to be reviewed before it is publicly visible'),
        'gui_currently-seeing-inactive-version': _('gui_currently-seeing-inactive-version', default='You are seeing an {0} version, which was previously active and publicly visible.'),
        'gui_currently-seeing-deleted-version': _('gui_currently-seeing-deleted-version', default='You are seeing a {0} version, which was previously active and publicly visible.'),
        'gui_currently-seeing-rejected-version': _('gui_currently-seeing-rejected-version', default='You are seeing a {0} version, which was never publicly visible.'),
        'gui_currently-seeing-edited-version': _('gui_currently-seeing-edited-version', default='You are seeing an {0} version, which was edited by a moderator and was never publicly visible.'),
        'gui_date': _('gui_date', default='Date'),
        'gui_last-change': _('gui_last-change', default='Last change'),
        'gui_delete-all-filters': _('gui_delete-all-filters', default='Delete all Filters'),
        'gui_details': _('gui_details', default='Details'),
        'gui_filter-count': _('gui_filter-count', default='Filter ({0} active)'),
        'gui_history': _('gui_history', default='History'),
        'gui_id': _('gui_id', default='ID'),
        'gui_language': _('gui_language', default='Language'),
        'gui_loading': _('gui_loading', default='Loading ...'),
        'gui_no-attributes': _('gui_no-attributes', default='No attributes to show'),
        'gui_paging-before': _('gui_paging-before', default='Page'),
        'gui_paging-after': _('gui_paging-after', default='of {0}'),
        'gui_previous-version': _('gui_previous-version', default='Previous Version'),
        'gui_profile': _('gui_profile', default='Profile'),
        'gui_search': _('gui_search', default='Search'),
        'gui_show-details': _('gui_show-details', default='Show Details'),
        'gui_timestamp': _('gui_timestamp', default='Timestamp'),
        'gui_unknown': _('gui_unknown', default='Unknown'),
        'gui_user': _('gui_user', default='User'),
        'gui_version': _('gui_version', default='Version'),

        # Feedback
        'feedback_failure': _('feedback_failure', default='Failure'),
        'feedback_new-activity-created': _('feedback_new-activity-created', default='The deal was successfully created. It will be reviewed shortly.'),
        'feedback_new-activity-not-created': _('feedback_new-activity-not-created', default='The deal could not be created.'),
        'feedback_new-stakeholder-created': _('feedback_new-stakeholder-created', default='The Stakeholder was successfully created. It will be reviewed shortly'),
        'feedback_new-stakeholder-not-created': _('feedback_new-stakeholder-not-created', default='The Stakeholder could not be created.'),
        'feedback_no-changes-made': _('feedback_no-changes-made', default='No changes made'),
        'feedback_no-changes-made-explanation': _('feedback_no-changes-made-explanation', default='You did not make any changes.'),
        'feedback_pending-edit-submitted': _('feedback_pending-edit-submitted', default='Edited changes were successfully submitted'),
        'feedback_pending-edit-not-submitted': _('feedback_pending-edit-not-submitted', default='Edited changes could not be submitted'),
        'feedback_some-attributes-not-editable-because-of-profile': _('feedback_some-attributes-not-editable-because-of-profile', default='Some of the attributes cannot be edited because they are not part of the currently selected profile.'),
        'feedback_success': _('feedback_success', default='Success'),

        # Activities
        'activities_add-new-activity': _('activities_add-new-activity', default='Add new Deal'),
        'activities_edit-activity': _('activities_edit-activity', default='Edit Deal (version {0})'),
        'activities_details-title': _('activities_details-title', default='Details on Deal'),
        'activities_filter-title': _('activities_filter-title', default='Filter Deal'),
        'activities_new-step-1': _('activities_new-step-1', default='Step 1: Please select a point on the map.'),
        'activities_new-step-1-explanation': _('activities_new-step-1-explanation', default='You can drag and drop the point. Once you are done, click "Continue".'),
        'activities_new-title': _('activities_new-title', default='New Deal'),
        'activities_paging-message': _('activities_paging-message', default='Displaying Deals {0} - {1} of {2}'),
        'activities_paging-empty': _('activities_paging-empty', default='No Deals found'),
        'activities_title': _('activities_title', default='Deals'),

        # Involvements
        'involvements_edit-involvement': _('involvements_edit-involvement', default='Edit this involvement'),
        'involvements_stakeholder-role': _('involvements_stakeholder-role', default='Role'),
        'involvements_title': _('involvements_title', default='Involvements'),

        # Stakeholders
        'stakeholders_add-stakeholders': _('stakeholders_add-stakeholders', default='Add Stakeholders'),
        'stakeholders_associated-stakeholders': _('stakeholders_associated-stakeholders', default='Associated Stakeholders'),
        'stakeholders_create-new-stakeholder': _('stakeholders_create-new-stakeholder', default='Create new Stakeholder'),
        'stakeholders_edit-stakeholder': _('stakeholders_edit-stakeholder', default='Edit Stakeholder (version {0})'),
        'stakeholders_details-title': _('stakeholders_details-title', default='Details on Stakeholder '),
        'stakeholders_filter-title': _('stakeholders_filter-title', default='Filter Stakeholders'),
        'stakeholders_no-associated-stakeholders-yet': _('stakeholders_no-associated-stakeholders-yet', default='No associated Stakeholders so far. You can search and select a Stakeholder using the Search field below. Or you can create a new Stakeholder by clicking on the button above.'),
        'stakeholders_paging-message': _('stakeholders_paging-message', default='Displaying stakeholders {0} - {1} of {2}'),
        'stakeholders_paging-empty': _('stakeholders_paging-empty', default='No stakeholders found'),
        'stakeholders_search': _('stakeholders_search', default='Search Stakeholder'),
        'stakeholders_select-stakeholder': _('stakeholders_select-stakeholder', default='Select Stakeholder'),
        'stakeholders_title': _('stakeholder_title', default='Stakeholders'),

        # Comments
        'comments_comment-by': _('comments_comment-by', default='Comment by'),
        'comments_confirm-delete-comment': _('comments_confirm-delete-comment', default='Do you really want to delete this comment?'),
        'comments_empty': _('comments_empty', default='No comments yet.'),
        'comments_leave-comment': _('comments_leave-comment', default='Leave a comment'),
        'comments_singular': _('comments_singular', default='Comment'),
        'comments_title': _('comments_title', default='Comments'),

        # Moderator
        'moderator_changes-not-based-on-active': _('moderator_changes-not-based-on-active', default='These changes are based on a version which is not the active version.'),
        'moderator_multiple-changes-pending': _('moderator_multiple-changes-pending', default='There are multiple changes pending! They may be conflicting.'),
        'moderator_pending-version-title': _('moderator_pending-version-title', default='Pending version'),
        'moderator_review-comment': _('moderator_review-comment', default='Review Comment'),
        'moderator_review-decision': _('moderator_review-decision', default='Review Decision'),
        'moderator_review-pending-changes': _('moderator_review-pending-changes', default='Review pending changes'),
        'moderator_show-pending-changes': _('moderator_show-pending-changes', default='Show pending changes'),

        # Filter
        'filter_logical-operator': _('filter_logical-operator', default='Logical Operator'),
        'filter_logical-operator-and': _('filter_logical-operator-and', default='and'),
        'filter_logical-operator-or': _('filter_logical-operator-or', default='or'),
        'filter_operator-is': _('filter_operator-is', default='is'),
        'filter_operator-is-not': _('filter_operator-is-not', default='is not'),
        'filter_operator-contains-case-sensitive': _('filter_operator-contains-case-sensitive', default='contains (case sensitive)'),
        'filter_operator-contains-case-insensitive': _('filter_operator-contains-case-insensitive', default='contains (case insensitive)'),
        'filter_operator-contains-not-case-sensitive': _('filter_operator-contains-not-case-sensitive', default='contains not (case sensitive)'),
        'filter_operator-contains-not-case-insensitive': _('filter_operator-contains-not-case-insensitive', default='contains not (case insensitive)'),
        'filter_operator-equals': _('filter_operator-equals', default='equals'),
        'filter_operator-less-than': _('filter_operator-less-than', default='less than'),
        'filter_operator-less-than-or-equal': _('filter_operator-less-than-or-equal', default='less than or equal'),
        'filter_operator-greater-than': _('filter_operator-greater-than', default='greater than'),
        'filter_operator-greater-than-or-equal': _('filter_operator-greater-than-or-equal', default='greater than or equal'),
        'filter_operator-not-equals': _('filter_operator-not-equals', default='not equals'),
        'filter_specify-number-value': _('filter_specify-number-value', default='Specify number value'),
        'filter_specify-text-value': _('filter_specify-text-value', default='Specify value'),
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
    """

    # Activity keys: Must be exactly (!) the same as in global activity.yml
    # If you change anything here, make sure to check the copying to the uiMap
    # further below!
    aKeys = [
        'Spatial Accuracy',         # 0
        'Negotiation Status',       # 1
        'Country',                  # 2
        'Intended area (ha)',       # 3
        'Intention of Investment',  # 4
        'Data source'               # 5
    ]
    aKeysTranslateQuery = get_translated_db_keys(A_Key, aKeys, db_lang)
    aKeysTranslated = []
    for k in aKeys:
        translation = k
        for tk in aKeysTranslateQuery:
            if tk.original == k:
                translation = tk.translation
        aKeysTranslated.append(translation)

    # Store the keys to the uiMap: Store original (needed for sorting) as well
    # as the translation
    uiMap['activity_db-key-spatialaccuracy-original'] = aKeys[0]
    uiMap['activity_db-key-spatialaccuracy'] = aKeysTranslated[0]
    uiMap['activity_db-key-negotiationstatus-original'] = aKeys[1]
    uiMap['activity_db-key-negotiationstatus'] = aKeysTranslated[1]
    uiMap['activity_db-key-country-original'] = aKeys[2]
    uiMap['activity_db-key-country'] = aKeysTranslated[2]
    uiMap['activity_db-key-intendedarea-original'] = aKeys[3]
    uiMap['activity_db-key-intendedarea'] = aKeysTranslated[3]
    uiMap['activity_db-key-intentionofinvestment-original'] = aKeys[4]
    uiMap['activity_db-key-intentionofinvestment'] = aKeysTranslated[4]
    uiMap['activity_db-key-datasource-original'] = aKeys[5]
    uiMap['activity_db-key-datasource'] = aKeysTranslated[5]

    # Stakeholder keys: Must be exactly (!) the same as in global
    # stakeholder.yml
    # If you change anything here, make sure to check the copying to the uiMap
    # further below!
    shKeys = [
        'Name',                 # 0
        'Country of origin'     # 1
    ]
    shKeysTranslateQuery = get_translated_db_keys(SH_Key, shKeys, db_lang)
    shKeysTranslated = []
    for k in shKeys:
        translation = k
        for tk in shKeysTranslateQuery:
            if tk.original == k:
                translation = tk.translation
        shKeysTranslated.append(translation)

    # Store the keys to the uiMap: Store original (needed for sorting) as well
    # as the translation
    uiMap['stakeholder_db-key-name-original'] = shKeys[0]
    uiMap['stakeholder_db-key-name'] = shKeysTranslated[0]
    uiMap['stakeholder_db-key-countryoforigin-original'] = shKeys[1]
    uiMap['stakeholder_db-key-countryoforigin'] = shKeysTranslated[1]

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

def get_translated_db_keys(mappedClass, db_keys, db_lang):
    """
    Returns a query array with original and translated keys from the database.
    """
    translation = aliased(mappedClass)

    q = Session.query(
            mappedClass.key.label('original'),
            translation.key.label('translation')
        ).\
        join(translation, mappedClass.translations).\
        filter(mappedClass.key.in_(db_keys)).\
        filter(mappedClass.original == None).\
        filter(translation.language == db_lang).\
        all()

    if q is not None:
        return q

    # If nothing found, return None
    return None