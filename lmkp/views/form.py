import colander
import copy
import deform
import logging
from mako.template import Template
#from datetime import datetime
import datetime

from lmkp.views.form_config import *
from lmkp.models.meta import DBSession as Session

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPFound
from pyramid.path import AssetResolver
from pyramid.threadlocal import get_current_request
from pyramid.view import view_config

log = logging.getLogger(__name__)

lmkpAssetResolver = AssetResolver('lmkp')

@view_config(route_name='form_clear_session')
def form_clear_session(request):
    """
    View that can be called to clear the session of any form-related data.
    Then redirects to url provided as request parameter or to the home view.
    """

    # Clear the session
    doClearFormSessionData(request)

    # Redirect to provided url
    url = request.params.get('url', None)
    if url is not None:
        return HTTPFound(location=url)

    # Else redirect home
    return HTTPFound(request.route_url('index'))

def renderForm(request, itemType, **kwargs):

    # TODO: Translation
    activity = 'Deal'
    noticeTitle = 'Notice'
    notice1 = 'Unsaved data of this item was found in the session. You may continue to edit this form.'
    notice2 = 'Unsaved data from another form %s was found in the session and will be deleted if you continue to edit this form.'
    action1 = 'Click here to delete the session data to clear the form.'
    action2 = 'See the unsaved changes of this Deal and submit it.'
    successTitle = 'Success'
    dealSuccess = 'The Deal was successfully created or updated. It is now pending and needs to be reviewed by a moderator before it is publicly visible.'
    dealLink = 'View the Deal.'
    emptyTitle = 'Empty Form'
    emptyText = 'You submitted an empty form or did not make any changes.'
    stakeholderSuccess = 'The Stakeholder was successfully created or updated. It is not pending and needs to be reviewed by a moderator before it is publicly visible.'
    stakeholderLink = 'View the Stakeholder'
    errorTitle = 'Error'

    itemJson = kwargs.get('itemJson', None)
    embedded = kwargs.get('embedded', False)

    # If an embedded Stakeholder form is submitted, the itemType is still
    # 'activities' although the submitted __formid__ hints at Stakeholders.
    if (itemType == 'activities' and '__formid__' in request.POST
        and request.POST['__formid__'] == 'stakeholderform'):
        itemType = 'stakeholders'

    # If an embedded Stakeholder form is submitted with errors, the 'embedded'
    # keyword is not set. Instead, a hidden parameter 'embedded' inside the form
    # can be used to know it is embedded (and AJAX should be used again)
    if 'embedded' in request.POST:
        embedded = True

    # Activity or Stakeholder
    if itemType == 'activities':
        # The initial category of the form
        newCategory = 1
        formid = 'activityform'
    elif itemType == 'stakeholders':
        # The initial category of the form
        newCategory = 40
        formid = 'stakeholderform'
    else:
        raise HTTPBadRequest('Unknown itemType (neither "activities" nor "stakeholders")')

    session = request.session
    oldCategory = None

    log.debug('Session before processing the form: %s' % session)

    # Use a different template rendering engine (mako instead of chameleon)
    deform.Form.set_default_renderer(mako_renderer)

    # Check if anything was submitted at all. If so, remember which category was
    # the one submitted.
    formSubmit = False
    if request.POST != {}:
        formSubmit = True
        for p in request.POST:
            if p == 'category':
                oldCategory = request.POST[p]
                break

    if embedded is True:
        # An embedded stakeholder form is submitted using AJAX. After the form
        # was submitted, populate the fields of the Activity form with the
        # involvement data. A html span element with a unique id is used to mark
        # the fieldset where the values are to be inserted.
        ajaxOptions = """
        {
            success: function (rText, sText, xhr, form) {
                $('#stakeholderFormLoading').hide();
                if (typeof stakeholderdata !== 'undefined') {
                    setInvolvementContent(stakeholderdata);
                }
                return false;
            }
        }
        """

    # Get the configuration of the categories (as defined in the config yaml)
    configCategoryList = getCategoryList(request, itemType)

    # Collect a list with id and names of all available categories which will be
    # used to create the buttons
    categoryListButtons = []
    for cat in sorted(configCategoryList.getCategories(),
        key=lambda cat: cat.order):
        categoryListButtons.append((cat.getId(), cat.getName()))

    captured = None
    formHasErrors = False
    # Some sort of data used for feedback. Can be Javascript or something else
    feedbackData = None

    # Handle form submission
    for p in request.POST:
        if p.startswith('step_') or p == 'submit':
            # Do a validation of the submitted form data. To do this, it is
            # necessary to recreate a form with the same category that was
            # submitted.

            # Prepare the form with the submitted category
            oldschema = addHiddenFields(colander.SchemaNode(colander.Mapping()),
                itemType, embedded=embedded)
            oldCat = configCategoryList.findCategoryById(oldCategory)
            if oldCat is not None:
                oldschema.add(oldCat.getForm(request))

            showSessionCategories = 'activity' if itemType == 'activities' else None
            buttons = getFormButtons(request, categoryListButtons, oldCategory,
                showSessionCategories=showSessionCategories)

            if embedded is True:
                # If the form is embedded, use AJAX to submit it.
                form = deform.Form(oldschema, buttons=buttons, formid=formid,
                    use_ajax=True, ajax_options=ajaxOptions)
            else:
                form = deform.Form(oldschema, buttons=buttons, formid=formid)

            try:
                # Try to validate the form
                captured = form.validate(request.POST.items())

            except deform.ValidationFailure as e:
                # The submitted values contains errors. Render the same form
                # again with error messages. It will be returned later.
                html = e.render()
                formHasErrors = True

            if formHasErrors is False:
                # The form is valid, store the captured data in the session.

                log.debug('Data captured by the form: %s' % captured)

                posted_formid = request.POST['__formid__']

                # Only store Activity form to session
                if posted_formid == 'activityform':

                    if 'activity' in session:
                        # There is already some data in the session.
                        sessionActivity = session['activity']
                        if (captured['id'] == sessionActivity['id']
                            and captured['version'] == sessionActivity['version']
                            and oldCategory in captured):
                            # It is the same item as already in the session, add or
                            # overwrite the form data.
                            updatedCategory = captured[oldCategory]
                            sessionActivity[oldCategory] = updatedCategory

                            log.debug('Updated session item: Category %s' % oldCategory)

                        else:
                            # A different item is already in the session. It will be
                            # overwriten.
                            if 'category' in captured:
                                del(captured['category'])
                            session['activity'] = captured

                            log.debug('Replaced session item')

                    else:
                        # No data is in the session yet. Store the captured data
                        # there.
                        if 'category' in captured:
                            del(captured['category'])
                        session['activity'] = captured

                        log.debug('Added session item')

                if p.startswith('step_'):
                    # A button with a next category was clicked, set a new
                    # current category to show in the form
                    c = p.split('_')
                    newCategory = c[1]

                else:
                    # The final submit button was clicked. Calculate the diff,
                    # delete the session data and redirect to a confirm page.

                    success = False

                    # Activity
                    if (posted_formid == 'activityform'
                        and 'activity' in session):
                        formdata = copy.copy(session['activity'])

                        log.debug('The complete formdata as in the session: %s' % formdata)

                        diff = formdataToDiff(request, formdata, itemType)

                        log.debug('The diff to create/update the activity: %s' % diff)

                        if diff is None:
                            return {
                                'form': '<h3 class="text-info">%s</h3><p>%s</p>' % (emptyTitle, emptyText),
                                'css_links': [],
                                'js_links': [],
                                'js': None,
                                'success': False
                            }

                        success, feedback = doActivityUpdate(request, diff)

                        if success is True:
                            feedbackMessage = ('<h3 class="text-success">%s</h3><p>%s</p><p><a href="%s">%s</a></p>'
                                % (
                                    successTitle,
                                    dealSuccess,
                                    request.route_url('activities_read_one', output='html', uid=feedback),
                                    dealLink
                                ))

                            # Clear the session
                            doClearFormSessionData(request)

                        else:
                            feedbackMessage = '<h3 class="text-error">%s</h3>: %s' % (errorTitle, feedback)

                    # Stakeholder
                    elif posted_formid == 'stakeholderform':

                        diff = formdataToDiff(request, captured, itemType)

                        log.debug('The diff to create/update the stakeholder: %s' % diff)

                        if diff is None:
                            return {
                                'form': '<h3 class="text-info">%s</h3><p>%s</p>' % (emptyTitle, emptyText),
                                'css_links': [],
                                'js_links': [],
                                'js': None,
                                'success': False
                            }

                        # Create or update the Stakeholder
                        success, js, identifier = doStakeholderUpdate(request, diff)

                        if success is True:
                            feedbackMessage = ('<h3 class="text-success">%s</h3><p>%s</p><p><a href="%s">%s</a></p>'
                                % (
                                    successTitle,
                                    stakeholderSuccess,
                                    request.route_url('stakeholders_read_one', output='html', uid=identifier),
                                    stakeholderLink
                                ))
                            feedbackData = js

                        else:
                            feedbackMessage = '<h3 class="text-error">%s</h3>%s' % (errorTitle, js)

                    else:
                        feedbackMessage = '<h3 class="text-error">%s</h3>: Unknown form' % errorTitle

                    return {
                        'form': feedbackMessage,
                        'css_links': [],
                        'js_links': [],
                        'js': feedbackData,
                        'success': success
                    }

            break

    if formHasErrors is False:
        # If nothing was submitted or the captured form data was stored
        # correctly, create a form with the (new) current category.
        newschema = addHiddenFields(colander.SchemaNode(colander.Mapping()),
            itemType, embedded=embedded)
        newCat = configCategoryList.findCategoryById(newCategory)
        if newCat is not None:
            newschema.add(newCat.getForm(request))
        showSessionCategories = 'activity' if itemType == 'activities' else None
        buttons = getFormButtons(request, categoryListButtons, newCategory,
            showSessionCategories=showSessionCategories)

        if embedded is True:
            # If the form is embedded, use AJAX to submit it.
            form = deform.Form(newschema, buttons=buttons, formid=formid,
                use_ajax=True, ajax_options=ajaxOptions)
        else:
            form = deform.Form(newschema, buttons=buttons, formid=formid)

        # The form contains empty data by default
        data = {'category': newCategory}

        # Decide which data to show in the form
        if itemType == 'activities' and itemJson is not None and 'activity' not in session:
            # An item was provided to show in the form (edit form) and no values
            # are in the session yet.
            # Simply show the data of the provided item in the form.
            data = getFormdataFromItemjson(request, itemJson, itemType,
                newCategory)
        elif itemType == 'activities' and itemJson is not None and 'activity' in session:
            # An item was provided to show in the form (edit form) and there are
            # some values in the session.

            sessionActivity = copy.copy(session['activity'])

            if (itemJson['id'] == sessionActivity['id']
                and itemJson['version'] == sessionActivity['version']):
                # The item in the session and the item provided are the same.
                if str(newCategory) in sessionActivity:
                    # The current category of the form is already in the session
                    # so we display this data.
                    sessionActivity['category'] = newCategory
                    data = sessionActivity
                else:
                    # The current category of the form is not yet in the session
                    # so we use the data of the itemjson to populate the form.
                    data = getFormdataFromItemjson(request, itemJson, itemType,
                        newCategory)
                if formSubmit is False:
                    # If the form is rendered for the first time, inform the
                    # user that session was used.

                    url = request.route_url('form_clear_session', _query={'url':request.url})
                    session.flash('<strong>%s</strong>: %s<br/><a href="%s">%s</a>' % (noticeTitle, notice1, url, action1))

            else:
                # The item in the session is not the same as the item provided.
                # Use the itemjson to populate the form
                data = getFormdataFromItemjson(request, itemJson, itemType,
                    newCategory)

                # Inform the user that there is data in the session.
                item_name = (sessionActivity['id'][:6]
                    if sessionActivity['id'] != colander.null
                    else 'New Activity')
                if sessionActivity['id'] != colander.null:
                    item_url = request.route_url('activities_read_one',
                        output='form', uid=sessionActivity['id'])
                else:
                    item_url = request.route_url('activities_read_many',
                        output='form')

                try:
                    notice2 = notice2 % '(%s %s)' % (activity, item_name)
                except TypeError:
                    pass

                session.flash('<strong>%s</strong>: %s<br/><a href="%s">%s</a>' % (noticeTitle, notice2, item_url, action2));

        elif itemType == 'activities' and itemJson is None and 'activity' in session:
            # No item was provided (create form) but some data was found in the
            # session.

            if (session['activity']['id'] != colander.null
                and session['activity']['version'] != colander.null):
                # The item in the session is not new. Show empty form data
                # (already defined) and inform the user.
                item_name = (session['activity']['id'][:6]
                    if session['activity']['id'] != colander.null
                    else 'Unknown Activity')
                if session['activity']['id'] != colander.null:
                    item_url = request.route_url('activities_read_one',
                        output='form', uid=session['activity']['id'])
                else:
                    item_url = request.route_url('activities_read_many',
                        output='form')

                try:
                    notice2 = notice2 % '(%s %s)' % (activity, item_name)
                except TypeError:
                    pass

                session.flash('<strong>%s</strong>: %s<br/><a href="%s">%s</a>' % (noticeTitle, notice2, item_url, action2));

            else:
                # Use the data in the session to populate the form.
                sessionActivity = copy.copy(session['activity'])
                sessionActivity['category'] = newCategory
                data = sessionActivity
                if formSubmit is False and embedded is False:
                    # If the form is rendered for the first time, inform the
                    # user that session was used.
                    url = request.route_url('form_clear_session', _query={'url':request.url})
                    session.flash('<strong>%s</strong>: %s<br/><a href="%s">%s</a>' % (noticeTitle, notice1, url, action1))

        elif itemType == 'stakeholders' and itemJson is not None:
            # An item was provided to show in the form (edit form)
            # Simply show the data of the provided item in the form.
            data = getFormdataFromItemjson(request, itemJson, itemType,
                newCategory)

        else:
            # No itemjson and no sessionitem, do nothing (empty data already
            # defined above).
            pass

#        log.debug('Data used to populate the form: %s' % data)

        html = form.render(data)

    # If the current category contains involvements (eg. to add Stakeholders to
    # an Activity), show a (initially empty) div which will contain the form for
    # Stakeholders.
    if str(newCategory) in configCategoryList.getInvolvementCategoryIds():
        html += '<div id="stakeholderformcontainer"></div>'

    # Add JS and CSS requirements (for widgets)
    resources = form.get_widget_resources()

    log.debug('Session after processing the form: %s' % session)

    return {
        'form': html,
        'css_links': resources['css'],
        'js_links': resources['js'],
        'success': not formHasErrors
    }

def renderReadonlyForm(request, itemType, itemJson):
    """
    Function to return a rendered form in readonly mode. The form is based on
    the configuration.
    """

    deform.Form.set_default_renderer(mako_renderer)
    configCategoryList = getCategoryList(request, itemType)
    schema = addHiddenFields(colander.SchemaNode(colander.Mapping()), itemType)
    schema.add(colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextInputWidget(template='hidden'),
        name='statusId',
        title='',
        missing = colander.null
    ))
    for cat in configCategoryList.getCategories():
        schema.add(cat.getForm(request))

    if itemType == 'stakeholders':
        # For Stakeholders, the readonly detail view should also contain the
        # involvements which are not part of the edit form so we need to add it
        # explicitely.

        activitiesCategoryList = getCategoryList(request, 'activities')
        overviewKeys = [k[0] for k in activitiesCategoryList.getInvolvementOverviewKeyNames()]

        mappingNames = ['primaryinvestors', 'secondaryinvestors']

        for mn in mappingNames:
            schema.add(getInvolvementWidget(
                mn,
                'customInvolvementMapping',
                'readonly/customInvolvementMappingActivity',
                overviewKeys,
                True,
                ''
            ))

    form = deform.Form(schema)
    data = getFormdataFromItemjson(request, itemJson, itemType)
    data['itemType'] = itemType
    statusId = itemJson['status_id'] if 'status_id' in itemJson else colander.null
    data['statusId'] = statusId
    html = form.render(data, readonly=True)

    coords = (itemJson['geometry']['coordinates'] if 'geometry' in itemJson
        and 'coordinates' in itemJson['geometry'] else None)

    return {
        'form': html,
        'coords': coords
    }

def structHasOnlyNullValues(cstruct, depth=0):
    """
    Recursive function checking if the 'struct' value of a form only contains
    empty values.
    Also return the depth of the recursion, which allows to identify what type
    the current 'struct' value is:
    0: A single tag
    1: A Taggroup
    2: A Thematic Group
    3: A Category
    """
    allNull = True
    newDepth = None
    if cstruct == colander.null:
        allNull = allNull and True
    elif isinstance(cstruct, dict):
        # A dict. Go one level deeper for each.
        for c in cstruct:
            a, d = structHasOnlyNullValues(cstruct[c], depth+1)
            if newDepth is None:
                newDepth = d
            else:
                newDepth = max(newDepth, d)
            allNull = allNull and a
    elif isinstance(cstruct, list):
        # A list. Go through each item of the list (though this does not mean a
        # recursion level deeper)
        for c in cstruct:
            a, d = structHasOnlyNullValues(c, depth)
            newDepth = d if newDepth is None else max(newDepth, d)
            allNull = allNull and a
    else:
        # Values are not null.
        allNull = allNull and False
    return allNull, newDepth if newDepth is not None else depth

def doClearFormSessionData(request):
    """
    Function to clear the session of any form-related data.
    """
    # Clear the session of any form data
    if 'activity' in request.session:
        del(request.session['activity'])

def doActivityUpdate(request, diff):
    """
    Function to do the update / create of an Activity.
    Returns a boolean indicating the success of the update and an additional
    variable, being either the error message (success == False) or the
    identifier of the newly create Activity (success == True)
    """
    from lmkp.views.activity_protocol3 import ActivityProtocol3
    protocol = ActivityProtocol3(Session)

    # Use the protocol to create/update the Activity
    ids = protocol.create(request, data=diff)

    if ids is None or len(ids) != 1:
        # TODO: Translation
        return False, 'The Activity could not be created or updated.'

    activity = ids[0]

    return True, activity.identifier

def doStakeholderUpdate(request, diff):
    """
    Function to do the update / create of a Stakeholder.
    Returns a boolean indicating the success of the update and an additional
    variable (js)
    If the update was successful, 'success' is True and 'js' contains a JS dict
    variable (stakeholderdata) which contains some information about the created
    Stakeholder verison.
    If the update ws not successful, 'success' is False and 'js' contains an
    error message.
    """
    from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
    protocol = StakeholderProtocol3(Session)

    # Use the protocol to create/update the Stakeholder
    ids = protocol.create(request, data=diff)

    if ids is None or len(ids) != 1:
        # TODO: Translation
        return False, 'The Stakeholder could not be created or updated.', None

    stakeholder = ids[0]

    # Now we need to re-collect the values for the feedback to the user. This is
    # especially important if the form is embedded.

    # Use the protocol to query the created item
    shFeature = protocol.read_one_by_version(request,
        stakeholder.identifier, stakeholder.version)

    if shFeature is None:
        return False, 'The Stakeholder was created but not found.', None

    # TODO: Translation
    unknownString = 'Unknown'

    # We need to know which fields of the stakeholder are used to populate the
    # display fields in the involvement overview.
    categorylist = getCategoryList(request, 'stakeholders')

    # Set all values to 'unknown' first
    keyValues = []
    overviewKeys = [o[0] for o in categorylist.getInvolvementOverviewKeyNames()]
    for k in overviewKeys:
        keyValues.append([k, unknownString])

    # Update the value if available
    for tg in shFeature.get_taggroups():
        for k in keyValues:
            if tg.get_tag_by_key(k[0]) is not None:
                k[1] = tg.get_tag_by_key(k[0]).get_value()

    js = """
    {
        var stakeholderdata = {
            id: "%s",
            version: %s,
            %s
        }
    }
    """ % (stakeholder.identifier, stakeholder.version,
        ', '.join('"%s": "%s"' % (n[0], n[1]) for n in keyValues)
    )

    return True, js, stakeholder.identifier

def addHiddenFields(schema, itemType, embedded=False):
    """
    Function to add hidden fields (for meta data of the item) to a form schema.
    Fields are added for:
    - id (the identifier of the item)
    - version (the version being edited)
    - category (the category of the form which is being edited)
    [- embedded]: When submitting an embedded form with AJAX, it is necessary to
    re-render this form in embedded mode (to use AJAX again on submission)
    """
    # For some reason, the deform.widget.HiddenWidget() does not seem to work.
    # Instead, the TextInputWidget is used with the hidden template.
    schema.add(colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextInputWidget(template='hidden'),
        name='id',
        title='',
        missing = colander.null
    ))
    schema.add(colander.SchemaNode(
        colander.Int(),
        widget=deform.widget.TextInputWidget(template='hidden'),
        name='version',
        title='',
        missing = colander.null
    ))
    schema.add(colander.SchemaNode(
        colander.Int(),
        widget=deform.widget.TextInputWidget(template='hidden'),
        name='category',
        title='',
        missing = colander.null
    ))
    schema.add(colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextInputWidget(template='hidden'),
        name='itemType',
        title='',
        missing = colander.null,
        default = itemType
    ))
    if embedded is True:
        schema.add(colander.SchemaNode(
            colander.Boolean(),
            widget=deform.widget.TextInputWidget(template='hidden'),
            name='embedded',
            title='',
            missing = False
        ))

    return schema

def getFormButtons(request, categorylist, currentCategory=None, **kwargs):
    """
    Function returning an array of form buttons (one button for each category
    and one final submit button). If a current category is provided, the button
    of this category gets a special css class.
    kwargs:
    - showSessionCategories [sessionName]: Tries to find [sessionName] in the
      session and loops its categories. The button of each category found gets
      the css_class 'formstepvisited'.
    """

    sessionCategories = []
    sessionKeyword = kwargs.pop('showSessionCategories', None)
    if sessionKeyword is not None and sessionKeyword in request.session:
        for c in request.session['activity']:
            try:
                # Only keep integers
                int(c)
                sessionCategories.append(c)
            except ValueError:
                pass

    _ = request.translate
    buttons = []
    # Only show categories if there is more than 1 category
    if len(categorylist) > 1:
        for cat in categorylist:
            b = deform.Button('step_%s' % str(cat[0]), cat[1], css_class='')
            if str(cat[0]) in sessionCategories:
                b.css_class='formstepvisited'
            if currentCategory is not None and str(cat[0]) == str(currentCategory):
                b.css_class='formstepactive'
            buttons.append(b)
    buttons.append(deform.Button('submit', _('Submit'), css_class='formsubmit'))
    return buttons

def checkValidItemjson(categorylist, itemJson, output='dict'):
    validMainkeys = categorylist.getAllMainkeyNames()

    taggroups = itemJson['taggroups']

    errors = []
    for taggroup in taggroups:
        maintag = taggroup['main_tag']

        # Make sure the maintag exists and contains values
        if maintag is None or 'key' not in maintag or maintag['key'] is None:
            errors.append('Undefined Maintag: Maintag of taggroup %s is not defined or has no values.' % taggroup)
            continue

        # Make sure that the maintag is in the list of valid maintags according
        # to the configuration
        if maintag['key'] not in validMainkeys:
            errors.append('Invalid Maintag: Maintag (%s) of taggroup %s is not a valid maintag according to the configuration.' % (maintag['key'], taggroup))

        # Make sure that the taggroup contains only one mainkey according to the
        # configuration
        keys = []
        for tag in taggroup['tags']:
            keys.append(tag['key'])

        mainkeys = []
        for k in keys:
            if k in validMainkeys:
                mainkeys.append(k)

        if len(mainkeys) > 1:
            errors.append('Too many Mainkeys: The taggroup %s should contain only 1 mainkey according to the configuration. It contains %s: %s' % (taggroup, len(mainkeys), ', '.join(mainkeys)))

        # Make sure that all the tags are valid keys in the same taggroup
        # according to the configuration
        if len(mainkeys) == 1:
            catId, thgId, confTaggroup = categorylist.findCategoryThematicgroupTaggroupByMainkey(maintag['key'])
            if confTaggroup is not None:
                for k in keys:
                    if confTaggroup.hasKey(k) is False:
                        errors.append('Wrong key in taggroup: The key %s is not valid in a taggroup with mainkey %s' % (k, maintag['key']))

    if len(errors) > 0:
        log.debug('\n\n==================================\nThe itemJson is not valid according to the yaml configuration. The following errors exist:\n** FORM ERROR ** %s\n==================================\n\n'
            % '\n** FORM ERROR ** '.join(errors))

    if output == 'dict':
        ret = {'errors': errors}
        if len(errors) > 0:
            ret['itemJson is valid'] = False
            ret['errorCount'] = len(errors)
        else:
            ret['itemJson is valid'] = True
        return ret

    elif output == 'list':
        return errors

    return None

def getFormdataFromItemjson(request, itemJson, itemType, category=None):
    """
    Use the JSON representation of a feature (Activity or Stakeholder) to get
    the values in a way the form can handle to display it. This can be used to
    display a form with some values already filled out to edit an existing
    Activity or Stakeholder.
    The values of the form depend on the configuration yaml. If a Tag is not
    found there, it is ignored and not returned by this function.
    - itemjson: The JSON representation of an object. This should only be
      exactly 1 version of an item (starting with {'activities': {...}} or
      {'stakeholders': {...}}
    - itemType: activities / stakeholders
    """

    # TODO: Translation
    unknownString = 'Unknown'

    def _getInvolvementData(involvementData, keyNames):
        """
        Helper function to extract the involvement data needed for the display
        fields of the involvement overview.
        """

        if involvementData is None or 'data' not in involvementData:
            return None

        data = involvementData['data']

        if 'taggroups' not in data:
            return None

        # Set them to null by default
        fields = {}
        for keyName in keyNames:
            fields[keyName] = unknownString

        for tg in data['taggroups']:
            if 'main_tag' not in tg or tg['main_tag'] is None:
                continue
            maintag = tg['main_tag']
            for f in fields:
                if ('key' in maintag and 'value' in maintag
                    and maintag['key'] == f):
                    fields[f] = maintag['value']

        fields['id'] = data['id']
        fields['version'] = involvementData['version']
        fields['role_id'] = involvementData['role_id']

        return fields

    # Get the list of categories (needed to validate the tags)
    categorylist = getCategoryList(request, itemType)
    validJsonErrors = checkValidItemjson(categorylist, itemJson, output='list')
    if len(validJsonErrors) > 0:
        return {}

    data = {
        'id': itemJson['id'],
        'version': itemJson['version'],
        'category': category
    }

    if ('involvements' in itemJson and (category is None or
        str(category) in categorylist.getInvolvementCategoryIds())):

        # Have a look at the involvements
        involvements = itemJson['involvements']

        if itemType == 'activities':
            # Activities: The involvements of an activity generally consist of
            # one Primary Investor and multiple Secondary Investors.

            # Collect the involvements and if they are primary or secondary
            # investors.
            primaryinvestor = None
            secondaryinvestors = []
            for i in involvements:

                if 'role_id' not in i:
                    # The role_id should always be there. If not, skip.
                    continue

                if i['role_id'] == 6 and primaryinvestor is None:
                    # If there is more than one primary investor, only the first one
                    # is treated as primary investor, all others as secondary.
                    primaryinvestor = i
                else:
                    secondaryinvestors.append(i)

            # The configuration of the other side of the involvement is needed to
            # know which fields are to be used for the overview display of the
            # involvement.
            otherItemType = 'stakeholders'
            otherCategoryList = getCategoryList(request, otherItemType)
            keyNames = [k[0] for k in otherCategoryList.getInvolvementOverviewKeyNames()]

            cat = {}

            # Primary investor
            f = _getInvolvementData(primaryinvestor, keyNames)
            thmg = categorylist.findThematicgroupByInvolvement('primaryinvestor')
            if f is not None and thmg is not None:
                cat[str(thmg.getId())] = {
                    'primaryinvestor': f
                }

            # Secondary investors
            thmg = categorylist.findThematicgroupByInvolvement('secondaryinvestor')
            siForm = []
            for si in secondaryinvestors:
                f = _getInvolvementData(si, keyNames)
                if f is not None:
                    siForm.append(f)
            if len(siForm) > 0 and thmg is not None:
                cat[str(thmg.getId())] = {
                    'secondaryinvestor': siForm
                }

            cat_id = (categorylist.getInvolvementCategoryIds()[0]
                if category is None else str(category))

            data[cat_id] = cat

        else:
            # Stakeholders. There can be multiple Primary Investors and multiple
            # Secondary Investors.

            # Collect the involvements and if they are primary or secondary
            # investors
            primaryinvestors = []
            secondaryinvestors = []
            for i in involvements:

                if 'role_id' not in i:
                    # The role_id should always be there.
                    continue

                if i['role_id'] == 6:
                    primaryinvestors.append(i)
                else:
                    secondaryinvestors.append(i)

            # The configuration of the other side of the involvement is needed to
            # know which fields are to be used for the overview display of the
            # involvement.
            otherItemType = 'activities'
            otherCategoryList = getCategoryList(request, otherItemType)
            keyNames = [k[0] for k in otherCategoryList.getInvolvementOverviewKeyNames()]

            cat = {}

            piForm = []
            for pi in primaryinvestors:
                f = _getInvolvementData(pi, keyNames)
                if f is not None:
                    piForm.append(f)
            data['primaryinvestors'] = piForm

            siForm = []
            for si in secondaryinvestors:
                f = _getInvolvementData(si, keyNames)
                if f is not None:
                    siForm.append(f)
            data['secondaryinvestors'] = siForm

    for taggroup in itemJson['taggroups']:

        # Get the category and thematic group based on the maintag
        mt = taggroup['main_tag']

        if mt is None:
            # If the maintag is empty, move on and do not add it to the form
            continue

        cat, thmg, tg = categorylist.findCategoryThematicgroupTaggroupByMainkey(
            mt['key'])

        # Treat the id's all as strings
        cat = str(cat)
        thmg = str(thmg)

        if tg is None:
            # If the Form Taggroup for this maintag was not found, move on and
            # do not add it to form
            continue

        tgid = str(tg.getId())
        maintag = tg.getMaintag()

        if maintag.getKey().getType().lower() == 'checkbox':
            # Checkboxes are represented as a list of tuples containing their
            # names and tg_id's.
            tagsdata = {}
        else:
            # Prepare the data of the tags
            tagsdata = {'tg_id': taggroup['tg_id']}
        for t in taggroup['tags']:
            # Add the tag only if the key exists in this taggroup
            if tg.hasKey(t['key']):
                configTag = categorylist.findTagByKeyName(t['key'])
                if maintag.getKey().getType().lower() == 'checkbox':
                    # Checkboxes: List of tuples with name and tg_id
                    tagsdata[t['key']] = [(t['value'], taggroup['tg_id'])]
                elif configTag.getKey().getType().lower() == 'date':
                    try:
                        d = datetime.datetime.strptime(t['value'], '%Y-%m-%d')
                        tagsdata[t['key']] = d
                    except ValueError:
                        pass
                else:
                    tagsdata[t['key']] = t['value']

        if tg.getRepeatable():
            tagsdata = [tagsdata]

        if cat in data:
            # Category already exists, check thematic group
            if thmg in data[cat]:
                # Thematic group already exists, check taggroup
                if tgid in data[cat][thmg]:
                    # Taggroup already exists. This should only happen if
                    # taggroup is reapeatable or if the tags are checkboxes.
                    # In this case add taggroup to the array of taggroups
                    if tg.getRepeatable():
                        # Repeatable: Add the data to the list of taggroups
                        data[cat][thmg][tgid].append(tagsdata[0])
                    elif (maintag.getKey().getType().lower() == 'checkbox'
                        and t['key'] in data[cat][thmg][tgid]):
                        # Checkboxes: Add the data to the list of tuples
                        data[cat][thmg][tgid][t['key']].append(
                            (t['value'], taggroup['tg_id'])
                        )
                    else:
                        log.debug('DUPLICATE TAGGROUP: Taggroup %s in thematic group %s and category %s appears twice although it is not repeatable!' % (tgid, thmg, cat))
                else:
                    # Taggroup does not exist yet, tags can be added
                    data[cat][thmg][tgid] = tagsdata
            else:
                # Thematic group does not exist yet, taggroup and tags can be
                # added
                data[cat][thmg] = {tgid: tagsdata}
        else:
            # Category does not exist yet, thematic group and taggroup and tags
            # can be added
            # Add the category only if the category is to be visible in the
            # current form.
            if category is None or cat == str(category):
                data[cat] = {thmg: {tgid: tagsdata}}

        # Map: Look only if the category contains a thematic group which has a
        # map.
        if (cat in categorylist.getMapCategoryIds()
            and thmg in categorylist.getMapThematicgroupIds()):
            # Make sure all the necessary values are there and add it only once.
            # TODO: The parameter 'map' is defined in the yaml (map: map) and
            # therefore rather static. Should this be made more dynamic?
            if (cat in data and thmg in data[cat]
                and 'map' not in data[cat][thmg] and 'geometry' in itemJson):
                geometry = itemJson['geometry']
                # Make sure the geometry is valid
                if ('coordinates' in geometry
                    and isinstance(geometry['coordinates'], list)
                    and len(geometry['coordinates']) == 2):
                    data[cat][thmg]['map'] = {
                        'lon': geometry['coordinates'][0],
                        'lat': geometry['coordinates'][1]
                    }

    log.debug('Formdata created by ItemJSON: %s' % data)

    return data

def formdataToDiff(request, newform, itemType):
    """
    Use the formdata captured on submission of the form and compare it with the
    old version of an object to create a diff which allows to create/update the
    object.
    Approach: Loop all items of the newform and check if they are new or changed
    compared to the oldform. If so, add them to diff and set their values to
    null in the oldform. Any remaining items (with non-null values) of oldform
    were deleted and need to be added to diff as well.
    - newform: The form data captured on submission
    - itemType: activities / stakeholders
    """

    def _findRemoveTgByCategoryThematicgroupTgid(form, category, thematicgroup,
        tg_id, checkbox=False):
        """
        Helper function to find a taggroup by its category, thematic group and
        tg_id. If it was found, its values in the form are set to null and the
        tags are returned.
        """
        # Loop the categories of the form to find the one with the given id.
        for (cat, thmgrps) in form.iteritems():
            if cat == category:
                # Loop the thematic groups of the category to find the one with
                # the given id.
                for (thmgrp, tgroups) in thmgrps.iteritems():
                    if thmgrp == thematicgroup:
                        # Loop the taggroups of the thematic group
                        for (tgroup, tags) in tgroups.iteritems():
                            # Transform them all to lists to handle them all the
                            # same.
                            if not isinstance(tags, list):
                                tags = [tags]
                            # Look at each taggroup and check the tg_id
                            for t in tags:
                                if 'tg_id' in t and t['tg_id'] == tg_id:
                                    ret = {}
                                    for (k, v) in t.iteritems():
                                        # Copy the keys and values
                                        ret[k] = v
                                        # Set the values to null
                                        t[k] = colander.null
                                    return form, ret
                                elif checkbox is True and ('tg_id' not in t
                                    or t['tg_id'] == colander.null):
                                    # Checkboxes: The actual taggroups are in a
                                    # list one level further down
                                    for (k, v) in t.iteritems():
                                        if isinstance(v, set):
                                            # Turn sets into lists
                                            v = list(v)
                                        if not isinstance(v, list):
                                            continue
                                        for (value, taggroupid) in v:
                                            if str(taggroupid) == str(tg_id):
                                                # If the taggroup was found,
                                                # remove it from the list.
                                                v.remove((value, taggroupid))
                                                if len(v) == 0:
                                                    # If there is no further
                                                    # taggroup in the list, set
                                                    # value of key to null.
                                                    t[k] = colander.null
                                            
                                            return form, True
        return form, None

    identifier = colander.null
    version = colander.null
    oldform = {}

    if 'id' in newform:
        # If the form contains an identifier, it is an edit of an existing item
        identifier = newform['id']
        del newform['id']

    if 'version' in newform:
        # If the form contains an identifier, it should also have a version
        version = newform['version']
        del newform['version']

    if 'category' in newform:
        # The category is not needed
        del newform['category']

    if 'embedded' in newform:
        # Embedded indicator is to be removed
        del newform['embedded']

    if 'itemType' in newform:
        # ItemType is not needed
        del newform['itemType']

    if 'statusId' in newform:
        # statusId is not needed
        del newform['statusId']

    if identifier != colander.null and version != colander.null:

        # Use the protocol to query the values of the version which was edited
        from lmkp.models.meta import DBSession as Session
        if itemType == 'stakeholders':
            from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
            protocol = StakeholderProtocol3(Session)
        else:
            from lmkp.views.activity_protocol3 import ActivityProtocol3
            protocol = ActivityProtocol3(Session)

        item = protocol.read_one_by_version(
            request, identifier, version
        )
        olditemjson = item.to_table(request)

        # Look only at the values transmitted to the form and therefore visible
        # to the editor.
        oldform = getFormdataFromItemjson(request, olditemjson, itemType)
        if 'id' in oldform:
            del oldform['id']
        if 'version' in oldform:
            del oldform['version']
        if 'category' in oldform:
            del oldform['category']

        if itemType == 'stakeholders':
            # The form for Stakeholders has involvement fields in them which are
            # only used for display purposes (since involvements can only be
            # added on Activity side). We need to remove them before processing
            # the diff.
            if 'primaryinvestors' in oldform:
                del oldform['primaryinvestors']
            if 'secondaryinvestors' in oldform:
                del oldform['secondaryinvestors']

        for (oldcat, othmgrps) in oldform.iteritems():
            # It is not sure that all of the form is in the session (the
            # newform variable). This is the case for example if a user did not
            # open a category of the form when editing the item.

            if oldcat not in newform:
                # For each category which is not in the newform but in the old
                # original form, copy the original to the newform.
                for (oldthmgrp, oldtgroups) in othmgrps.iteritems():
                    # Because the values in the newform are rendered when
                    # submitted by the form, some values of the original form
                    # (which was not captured) need to be adopted to match.
                    for (oldtgroup, oldtags) in oldtgroups.iteritems():
                        if not isinstance(oldtags, list):
                            if 'tg_id' not in oldtags:
                                oldtags['tg_id'] = colander.null
                            for (oldkey, oldvalue) in oldtags.iteritems():
                                if isinstance(oldvalue, list):
                                    oldtags[oldkey] = set(oldvalue)

                newform[oldcat] = othmgrps

    categorylist = getCategoryList(request, itemType)
    taggroupdiffs = []
    involvementdiffs = []
    geometrydiff = None

    # Loop the newform to check if there are taggroups which changed or are new

    # Loop the categories of the form
    for (cat, thmgrps) in newform.iteritems():

        if cat in categorylist.getInvolvementCategoryIds():

            # The form division between primaryinvestor and secondaryinvestor
            # is ignored if there already is a role_id available (because for
            # example if there are multiple primary investors they are also
            # shown as secondary investors).
            # In a first step, collect all the involvements there are in the new
            # form and the involvements that were in the oldform. Use them only
            # if they have an id, a version and a role_id.
            newInvolvements = []
            oldInvolvements = []

            for (thmgrp, involvements) in thmgrps.iteritems():
                if 'primaryinvestor' in involvements:
                    i = involvements['primaryinvestor']
                    if ('id' in i and i['id'] != colander.null
                        and 'version' in i and i['version'] != colander.null
                        and 'role_id' in i):
                        if i['role_id'] == colander.null:
                            i['role_id'] = 6
                        newInvolvements.append(i)

                elif 'secondaryinvestor' in involvements:
                    for i in involvements['secondaryinvestor']:
                        if ('id' in i and i['id'] != colander.null
                            and 'version' in i and i['version'] != colander.null
                            and 'role_id' in i):
                            if i['role_id'] == colander.null:
                                i['role_id'] = 7
                            newInvolvements.append(i)

            for (oldCat, oldThmgrps) in oldform.iteritems():
                if oldCat == 'involvements' or oldCat in categorylist.getInvolvementCategoryIds():
                    for (thmgrp, involvements) in oldThmgrps.iteritems():
                        if 'primaryinvestor' in involvements:
                            i = involvements['primaryinvestor']
                            if ('id' in i and i['id'] != colander.null
                                and 'version' in i
                                and i['version'] != colander.null
                                and 'role_id' in i):
                                if i['role_id'] == colander.null:
                                    i['role_id'] = 6
                                oldInvolvements.append(i)
                        elif 'secondaryinvestor' in involvements:
                            for i in involvements['secondaryinvestor']:
                                if ('id' in i and i['id'] != colander.null
                                    and 'version' in i
                                    and i['version'] != colander.null
                                    and 'role_id' in i):
                                    if i['role_id'] == colander.null:
                                        i['role_id'] = 7
                                    oldInvolvements.append(i)

            # Loop the new involvements and try to find them in the old
            # involvements (based on their identifier, version and role_id). If
            # they are found, remove them from the list of old involvements. If
            # they are not found, mark them as newly added.
            for ni in newInvolvements:
                found = False

                for oi in oldInvolvements:

                    if (ni['id'] == oi['id'] and ni['version'] == oi['version']
                        and ni['role_id'] == oi['role_id']):
                        found = True
                        oldInvolvements.remove(oi)
                        break

                if found is False:
                    # Involvement is new
                    involvementdiffs.append({
                        'id': ni['id'],
                        'version': ni['version'],
                        'role': ni['role_id'],
                        'op': 'add'
                    })

            # Loop the remaining old involvements and mark them as deleted.
            for oi in oldInvolvements:
                involvementdiffs.append({
                    'id': oi['id'],
                    'version': oi['version'],
                    'role': oi['role_id'],
                    'op': 'delete'
                })

            continue

        try:
            thmgrpsitems = thmgrps.iteritems()
        except AttributeError:
            continue

        # Loop the thematic groups of the category
        for (thmgrp, tgroups) in thmgrpsitems:
            # Loop the tags of each taggroup
            for (tgroup, tags) in tgroups.iteritems():

                # TODO: The parameter 'map' is defined in the yaml (map: map)
                # and therefore rather static. Should this be made more dynamic?
                if tgroup == 'map':

                    oldpoint = None
                    if (cat in oldform and thmgrp in oldform[cat]
                        and 'map' in oldform[cat][thmgrp]):
                        oldpoint = oldform[cat][thmgrp]['map']

                    lon = (tags['lon'] if 'lon' in tags
                        and tags['lon'] != colander.null else None)
                    lat = (tags['lat'] if 'lat' in tags
                        and tags['lat'] != colander.null else None)

                    if lon is not None and lat is not None:
                        if (oldpoint is None or lon != oldpoint['lon']
                            or lat != oldpoint['lat']):

                            geometrydiff = {
                                'type': 'Point',
                                'coordinates': [lon, lat]
                            }

                # Transform all to list so they can be treated all the same
                if not isinstance(tags, list):
                    tags = [tags]

                for t in tags:
                    if 'tg_id' not in t:
                        continue

                    if t['tg_id'] != colander.null:
                        # Taggroup was there before because it contains a tg_id.
                        # Check if it contains changed values.

                        # Make a copy of the tags because the function to find
                        # and remove below modifies t.
                        t_copy = copy.copy(t)

                        # Try to find the taggroup by its tg_id in the oldform
                        oldform, oldtaggroup = _findRemoveTgByCategoryThematicgroupTgid(
                            oldform, cat, thmgrp, t['tg_id'])

                        if oldtaggroup is None:
                            # This should never happen since all tg_ids should
                            # be known.
                            log.debug('\n\n*** TG_ID NOT FOUND: When trying to find and remove taggroup by tg_id (%s), the taggroup was not found in the old form.\n\n' % t['tg_id'])
                            continue

                        deletedtags = []
                        addedtags = []

                        for (k, v) in t_copy.iteritems():

                            if (k != 'tg_id'):
                                if (k in oldtaggroup
                                    and str(v) != oldtaggroup[k]
                                    and v != colander.null):
                                    # Because the form renders values as floats,
                                    # it is important to compare them correctly
                                    # with an integer value
                                    try:
                                        if float(oldtaggroup[k]) == float(v):
                                            continue
                                    except ValueError:
                                        pass
                                    except TypeError:
                                        continue

                                    # If a key is there in both forms but its
                                    # value changed, add it once as deleted and
                                    # once as added.
                                    deletedtags.append({
                                        'key': k,
                                        'value': oldtaggroup[k]
                                    })
                                    addedtags.append({
                                        'key': k,
                                        'value': v
                                    })
                                elif (k not in oldtaggroup
                                    and v != colander.null):
                                    # If a key was not there in the oldform, add
                                    # it as added.
                                    addedtags.append({
                                        'key': k,
                                        'value': v
                                    })
                                elif (k in oldtaggroup and str(v) != oldtaggroup[k]
                                    and v == colander.null):
                                    # If a key was in the oldform but not in the
                                    # new one anymore, add it as deleted.
                                    deletedtags.append({
                                        'key': k,
                                        'value': oldtaggroup[k]
                                    })

                        # Put together diff for the taggroup
                        if len(deletedtags) > 0 or len(addedtags) > 0:
                            tagdiffs = []
                            for dt in deletedtags:
                                tagdiffs.append({
                                    'key': dt['key'],
                                    'value': dt['value'],
                                    'op': 'delete'
                                })
                            for at in addedtags:
                                tagdiffs.append({
                                    'key': at['key'],
                                    'value': at['value'],
                                    'op': 'add'
                                })
                            taggroupdiffs.append({
                                'tg_id': t['tg_id'],
                                'tags': tagdiffs
                            })

                    else:
                        # Taggroup has no tg_id. It is either a new taggroup to
                        # be added (if it contains values) or it may be a group
                        # of checkboxes (with tg_ids a level lower)
                        # For Checkboxes: Values cannot really change, they can
                        # only be added (if another checkbox is selected, a new
                        # taggroup is created). If a checkbox was submitted with
                        # a tg_id, it was there before already.
                        addedtags = []
                        addedtaggroups = []
                        for (k, v) in t.iteritems():
                            if (k != 'tg_id' and v != colander.null):
                                if isinstance(v, set):
                                    # If the value is a set, the form displayed
                                    # a group of checkboxes. Each of the values
                                    # is treated as a separate taggroup.
                                    for (value, tg_id) in v:
                                        if tg_id is None:
                                            # No tg_id, treat it as a new
                                            # taggroup
                                            addedtaggroups.append({
                                                'op': 'add',
                                                'tags': [{
                                                    'key': k,
                                                    'value': value,
                                                    'op': 'add'
                                                }],
                                                'main_tag': {
                                                    'key': k,
                                                    'value': value
                                                }
                                            })
                                        else:
                                            # Try to find and remove the
                                            # taggroup in the old form
                                            oldform, oldtaggroup = _findRemoveTgByCategoryThematicgroupTgid(
                                                oldform, cat, thmgrp, tg_id, True)
                                            if oldtaggroup is None:
                                                # This basically should not happen because the tg_id always should be found.
                                                log.debug('\n\n*** TG_ID NOT FOUND: When trying to find and remove taggroup by tg_id (%s), the taggroup was not found in the old form.\n\n' % tg_id)
                                else:
                                    # No checkbox, simply a new tag
                                    addedtags.append({
                                        'key': k,
                                        'value': v
                                    })

                        # For checkboxes, the diff is already a taggroup.
                        if len(addedtaggroups) > 0:
                            for tg in addedtaggroups:
                                taggroupdiffs.append(tg)

                        # Put together diff for taggroup
                        elif len(addedtags) > 0:

                            # Newly added taggroups need to have a valid
                            # main_tag. We need to find out the main_tag of the
                            # current taggroup for the diff
                            cCat = categorylist.findCategoryById(cat)
                            if cCat is None:
                                continue

                            cThmg = cCat.findThematicgroupById(thmgrp)
                            if cThmg is None:
                                continue

                            cTg = cThmg.findTaggroupById(tgroup)
                            if cTg is None:
                                continue

                            mainkey = cTg.getMaintag().getKey().getName()

                            if mainkey is None or mainkey not in t:
                                continue

                            mainvalue = t[mainkey]
                            if mainvalue is None:
                                continue

                            tagdiffs = []
                            for at in addedtags:
                                tagdiffs.append({
                                    'key': at['key'],
                                    'value': at['value'],
                                    'op': 'add'
                                })
                            taggroupdiffs.append({
                                'op': 'add',
                                'tags': tagdiffs,
                                'main_tag': {
                                    'key': mainkey,
                                    'value': mainvalue
                                }
                            })

    # Loop the oldform to check if there are any tags remaining which have
    # values in them, meaning that they are not in the newform anymore and are
    # therefore to be deleted.

    # Loop the categories of the form
    for (cat, thmgrps) in oldform.iteritems():
        # Loop the thematic groups of the category
        for (thmgrp, tgroups) in thmgrps.iteritems():
            # Loop the tags of each taggroup
            for (tgroup, tags) in tgroups.iteritems():
                # Transform all to list so they can be treated all the same
                if not isinstance(tags, list):
                    tags = [tags]

                for t in tags:
                    if 'tg_id' in t and t['tg_id'] != colander.null:
                        deletedtags = []
                        for (k, v) in t.iteritems():
                            if (k != 'tg_id' and v != colander.null):
                                deletedtags.append({
                                    'key': k,
                                    'value': v
                                })

                        if len(deletedtags) > 0:
                            tagdiffs = []
                            for dt in deletedtags:
                                tagdiffs.append({
                                    'key': dt['key'],
                                    'value': dt['value'],
                                    'op': 'delete'
                                })
                            taggroupdiffs.append({
                                'op': 'delete',
                                'tg_id': t['tg_id'],
                                'tags': tagdiffs
                            })
                    else:
                        # Checkbox: Look one level deeper
                        for (k, v) in t.iteritems():
                            if not isinstance(v, list):
                                continue
                            for (value, taggroupid) in v:
                                # Add it directly to taggroups
                                taggroupdiffs.append({
                                    'op': 'delete',
                                    'tg_id': taggroupid,
                                    'tags': [{
                                        'key': k,
                                        'value': value
                                    }]
                                })

    ret = None

    if (len(taggroupdiffs) > 0 or len(involvementdiffs) > 0
        or geometrydiff is not None):
        itemdiff = {}

        if len(taggroupdiffs) > 0:
            itemdiff['taggroups'] = taggroupdiffs

        if len(involvementdiffs) > 0:
            kw = 'activities' if itemType == 'stakeholders' else 'stakeholders'
            itemdiff[kw] = involvementdiffs

        if geometrydiff is not None:
            itemdiff['geometry'] = geometrydiff

        itemdiff['version'] = version if version is not colander.null else 1
        if identifier is not colander.null:
            itemdiff['id'] = identifier

        ret = {}
        ret[itemType] = [itemdiff]

    return ret

def mako_renderer(tmpl_name, **kw):
    """
    A helper function to use the mako rendering engine.
    It seems to be necessary to locate the templates by using the asset
    resolver.
    """
    resolver = lmkpAssetResolver.resolve('templates/form/%s.mak' % tmpl_name)
    template = Template(filename=resolver.abspath())

    # Add the request to the keywords so it is available in the templates.
    request = get_current_request()
    kw['request'] = request

    return template.render(**kw)
