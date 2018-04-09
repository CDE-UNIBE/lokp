import copy
import json
import logging

import colander
import datetime
import deform
from mako.template import Template
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
from pyramid.i18n import TranslationStringFactory
from pyramid.path import AssetResolver
from pyramid.renderers import render
from pyramid.threadlocal import get_current_request
from pyramid.view import view_config

from lokp.config.customization import get_customized_template_path
from lokp.config.form import getCategoryList
from lokp.models import DBSession
from lokp.protocols.activity_protocol import ActivityProtocol
from lokp.protocols.stakeholder_protocol import StakeholderProtocol
from lokp.utils.form import calculate_deletion_diff, formdataToDiff, \
    doClearFormSessionData, addCreatedInvolvementToSession, \
    getFormdataFromItemjson, checkValidItemjson, mergeFormdata

log = logging.getLogger(__name__)
_ = TranslationStringFactory('lokp')
lokpAssetResolver = AssetResolver('lokp')


@view_config(route_name='config_geomtaggroups', renderer='json')
def form_geomtaggroups(request):
    """
    Simple service to return all the mainkeys of taggroups which can have
    geometries as defined in the configuration yaml.
    """
    categorylist = getCategoryList(request, 'activities')
    return {
        'mainkeys': categorylist.getMainkeyWithGeometry(withTranslation=True)
    }


def renderForm(request, itemType, **kwargs):
    """
    Render the form for either Activity or Stakeholder
    """

    # Get the kwargs
    itemJson = kwargs.get('itemJson', None)
    newInvolvement = kwargs.get('inv', None)

    emptyTitle = _('Empty Form')
    emptyText = _('You submitted an empty form or did not make any changes.')
    errorTitle = _('Error')

    # Activity or Stakeholder
    if itemType == 'activities':
        # The initial category of the form
        formid = 'activityform'
        otherItemType = 'stakeholders'
    elif itemType == 'stakeholders':
        # The initial category of the form
        formid = 'stakeholderform'
        otherItemType = 'activities'
    else:
        raise HTTPBadRequest(
            'Unknown itemType (neither "activities" nor "stakeholders")')

    session = request.session
    oldCategory = None

    log.debug('Session before processing the form: %s' % session)

    # Use a different template rendering engine (mako instead of chameleon)
    deform.Form.set_default_renderer(mako_renderer)

    # Check if anything was submitted at all. If so, remember which category
    # was the one submitted.
    formSubmit = False
    if request.POST != {}:
        formSubmit = True
        for p in request.POST:
            if p == 'category':
                oldCategory = request.POST[p]
                break

    # Get the configuration of the categories (as defined in the config yaml)
    configCategoryList = getCategoryList(request, itemType)

    # Determine which category to show. If reopening the form after creating a
    # new Involvement, use the category of the Involvement. Else use the first
    # category of the configuration.
    if newInvolvement is not None:
        newInvCat = configCategoryList.findCategoryByInvolvementName(
            newInvolvement)
        if newInvCat is not None:
            newCategory = newInvCat.getId()
        else:
            newCategory = configCategoryList.getFirstCategoryId()
    else:
        newCategory = configCategoryList.getFirstCategoryId()

    # Collect a list with id and names of all available categories which will
    # be used to create the buttons based cat
    categoryListButtons = []
    for cat in sorted(
            configCategoryList.getCategories(), key=lambda cat: cat.order):
        displayName = (
            cat.getTranslation() if cat.getTranslation() is not None
            else cat.getName())
        categoryListButtons.append((cat.getId(), displayName))

    captured = None
    formHasErrors = False
    # Some sort of data used for feedback. Can be Javascript or something else
    feedbackData = None

    # Handle form submission: This can also be just the "submission" of a
    # single category which does not submit the item but stores the
    # information of the submitted category in the session.
    for p in request.POST:

        if (not (p.startswith('step_') or p in ['submit', 'delete']
                 or p.startswith('createinvolvement_'))):
            continue

        createInvolvement = False
        if p.startswith('createinvolvement_'):
            # If the form was "submitted" because a new involvement is to be
            # created, we need to remove the 'create_involvement' POST value,
            # otherwise Deform cannot validate the form.
            x = p.split('_')
            createInvolvement = x[1]
            request.POST.pop(p)

        # Do a validation of the submitted form data. To do this, it is
        # necessary to recreate a form with the same category that was
        # submitted.
        buttons = []

        # Prepare a form with the submitted category
        oldschema = addHiddenFields(
            colander.SchemaNode(colander.Mapping()), itemType)
        oldCat = configCategoryList.findCategoryById(oldCategory)
        if oldCat is not None:
            oldschema.add(oldCat.getForm(request))
            showSessionCategories = None
            if (itemJson is None or (itemType in session
                                     and 'form' in session[itemType]
                                     and 'id' in session[itemType]['form']
                                     and session[itemType]['form']['id'] == itemJson['id'])):
                showSessionCategories = itemType
            buttons = getFormButtons(
                request, categoryListButtons, oldCategory,
                showSessionCategories=showSessionCategories)
        # creates form?
        form = deform.Form(oldschema, buttons=buttons, formid=formid)

        if p == 'delete':
            captured = {}
        else:
            try:
                # Try to validate the form
                captured = form.validate(request.POST.items())  # captured contains input values

            except deform.ValidationFailure as e:
                # The submitted values contains errors. Render the same form
                # again with error messages. It will be returned later.
                html = e.render()
                formHasErrors = True
        ## TODO Write geometry to session
        ## TODO Create polygon from session
        if formHasErrors is False:
            # The form is valid, store the captured data in the session.

            log.debug('Data captured by the form: %s' % captured)

            # If there is already some data in the session.
            if itemType in session and 'form' in session[itemType]:
                sessionItem = session[itemType]['form']  # sessionItem contains values saved in session
                if (captured.get('id') == sessionItem.get('id')
                        and captured.get('version') == sessionItem.get('version')
                        and oldCategory in captured):
                    # It is the same item as already in the session, add or
                    # overwrite the form data.
                    updatedCategory = captured[oldCategory]
                    sessionItem[oldCategory] = updatedCategory

                    log.debug(
                        'Updated session item: Category %s' % oldCategory)

                else:
                    # A different item is already in the session. It will be
                    # overwriten.
                    if 'category' in captured:
                        del (captured['category'])
                    session[itemType]['form'] = captured

                    log.debug('Replaced session item')

            else:
                # No data is in the session yet. Store the captured data
                # there.
                if 'category' in captured:
                    del (captured['category'])
                if itemType not in session:
                    session[itemType] = {}
                session[itemType]['form'] = captured  # write session data to form of itemType (can be activity etc.)

                log.debug('Added session item')

            if p.startswith('step_'):
                # A button with a next category was clicked, set a new
                # current category to show in the form
                c = p.split('_')
                newCategory = c[1]

            if createInvolvement is not False:
                # A new form is opened to create an Involvement. Store the
                # current form information in the session (camefrom).
                if itemType in session and 'camefrom' in session[itemType]:
                    # TODO
                    print("*************************")
                    print("*************************")
                    print("*************************")
                    print("there is already an activity in the session")
                    print("*************************")
                    print("*************************")
                    print("*************************")
                itemId = '' if itemJson is None or 'id' not in itemJson \
                    else itemJson['id']
                session[itemType]['camefrom'] = {
                    'id': itemId,
                    'timestamp': datetime.datetime.now(),
                    'inv': createInvolvement
                }
                if itemType == 'activities':
                    msg = render(
                        get_customized_template_path(
                            request,
                            'parts/messages/stakeholder_form_through_'
                            'involvement.mak'),
                        {
                            'url': request.route_url(
                                'activities_read_many', output='form',
                                _query={'inv': createInvolvement})
                        },
                        request
                    )
                    session.flash(msg)
                    url = request.route_url(
                        'stakeholders_read_many', output='form')
                else:
                    url = request.route_url(
                        'activities_read_many', output='form')

                # Redirect to the other form.
                return HTTPFound(url)

            if p in ['submit', 'delete']:
                # The final submit button was clicked. Calculate the diff,
                # delete the session data and redirect to a confirm page.

                success = False
                posted_formid = request.POST['__formid__']

                if posted_formid not in ['activityform', 'stakeholderform']:
                    # TODO: Is this the correct way to return an error message?
                    feedbackMessage = '<span class="text-error">{}</span>: Unknown form'.format(errorTitle)
                    return {
                        'form': feedbackMessage,
                        'css_links': [],
                        'js_links': [],
                        'js': None,
                        'success': False
                    }

                if p == 'delete':
                    # The Item is to be deleted. Calculate the diff to delete
                    # all tags
                    diff = calculate_deletion_diff(request, itemType)

                else:
                    if (itemType not in session
                            or 'form' not in session[itemType]):
                        # TODO: Is this the correct way to return an error
                        # message?
                        feedbackMessage = 'Session not active'
                        return {
                            'form': feedbackMessage,
                            'css_links': [],
                            'js_links': [],
                            'js': None,
                            'success': False
                        }

                    formdata = copy.copy(session[itemType]['form'])

                    log.debug(
                        'The complete formdata as in the session: %s'
                        % formdata)
                    # check
                    diff = formdataToDiff(request, formdata, itemType)

                log.debug('The uncleaned diff to create/update the activity: %s' % diff)

                if diff is None:
                    # TODO: Is this the correct way to return an error message?
                    return {
                        'form': '<h3 class="text-info">%s</h3><p>%s</p>' % (
                            emptyTitle, emptyText),
                        'css_links': [],
                        'js_links': [],
                        'js': None,
                        'success': False
                    }

                # Create or update the Item
                success, returnValues = doUpdate(request, itemType, diff)

                if success is True:

                    # Clear the session
                    doClearFormSessionData(request, itemType, 'form')

                    if (otherItemType in session
                            and 'camefrom' in session[otherItemType]):
                        # The form was submitted "indirectly"

                        camefrom = session[otherItemType]['camefrom']

                        # Clear the camefrom flag
                        doClearFormSessionData(
                            request, otherItemType, 'camefrom')

                        addToSession = addCreatedInvolvementToSession(
                            request, session, otherItemType, camefrom['inv'],
                            returnValues)
                        if addToSession is True:
                            msg = render(
                                get_customized_template_path(
                                    request,
                                    'parts/messages/stakeholder_created_'
                                    'through_involvement.mak'),
                                {},
                                request
                            )
                            session.flash(msg, 'success')

                        # Route to the other form again.
                        if itemType == 'activities':
                            url = request.route_url(
                                'stakeholders_read_many', output='form',
                                _query={'inv': camefrom['inv']})
                        else:
                            activity_id = camefrom.get('id')
                            if activity_id is not None and activity_id != '':
                                url = request.route_url(
                                    'activities_read_one', output='form',
                                    uid=activity_id,
                                    _query={'inv': camefrom['inv']})
                            else:
                                url = request.route_url(
                                    'activities_read_many', output='form',
                                    _query={'inv': camefrom['inv']})

                        return HTTPFound(url)

                    else:
                        if itemType == 'activities':
                            feedbackMessage = render(
                                get_customized_template_path(
                                    request,
                                    'parts/messages/activity_created_'
                                    'success.mak'),
                                {
                                    'url': request.route_url(
                                        'activities_read_one', output='html',
                                        uid=returnValues['id'])},
                                request
                            )
                        else:
                            feedbackMessage = render(
                                get_customized_template_path(
                                    request,
                                    'parts/messages/stakeholder_created_'
                                    'success.mak'),
                                {
                                    'url': request.route_url(
                                        'stakeholders_read_one', output='html',
                                        uid=returnValues['id'])},
                                request
                            )

                else:
                    feedbackMessage = '<h3 class="text-error">%s</h3>%s' % (
                        errorTitle, returnValues)

                return {
                    'form': feedbackMessage,
                    'css_links': [],
                    'js_links': [],
                    'js': feedbackData,
                    'success': success
                }
    # END Post-request
    if formHasErrors is False:
        # If nothing was submitted or the captured form data was stored
        # correctly, create a form with the (new) current category.
        newschema = addHiddenFields(
            colander.SchemaNode(colander.Mapping()), itemType)
        newCat = configCategoryList.findCategoryById(newCategory)
        if newCat is not None:
            newschema.add(newCat.getForm(request))  # send get request to config/form.py
        showSessionCategories = None
        if (itemJson is None or (itemType in session
                                 and 'id' in session[itemType]
                                 and session[itemType]['id'] == itemJson['id'])):
            showSessionCategories = itemType
        buttons = getFormButtons(
            request, categoryListButtons, newCategory,
            showSessionCategories=showSessionCategories)

        form = deform.Form(newschema, buttons=buttons, formid=formid)

        # The form contains empty data by default
        data = {'category': newCategory}

        # Decide which data to show in the form
        sessionItem = None
        if itemType in session and 'form' in session[itemType]:
            sessionItem = copy.copy(session[itemType]['form'])

        if itemJson is not None and itemType not in session:
            # An item was provided to show in the form (edit form) and no
            # values are in the session yet.
            # Simply show the data of the provided item in the form.
            data = getFormdataFromItemjson(
                request, itemJson, itemType, newCategory)
        elif itemJson is not None and sessionItem is not None:
            # An item was provided to show in the form (edit form) and there
            # are some values in the session.

            if (itemJson['id'] == sessionItem['id']
                    and itemJson['version'] == sessionItem['version']):
                # The item in the session and the item provided are the same.
                if str(newCategory) in sessionItem:
                    # The current category of the form is already in the
                    # session so we display this data.
                    sessionItem['category'] = newCategory
                    data = sessionItem
                else:
                    # The current category of the form is not yet in the
                    # session so we use the data of the itemjson to populate
                    # the form.
                    data = getFormdataFromItemjson(
                        request, itemJson, itemType, newCategory)
                if formSubmit is False and request.params.get('inv') is None:
                    # If the form is rendered for the first time, inform the
                    # user that session was used.

                    url = request.route_url(
                        'form_clear_session', item=itemType, attr='form',
                        _query={'url': request.url})
                    msg = render(
                        get_customized_template_path(
                            request,
                            'parts/messages/unsaved_data_same_form.mak'),
                        {'url': url},
                        request
                    )
                    session.flash(msg)

            else:
                # The item in the session is not the same as the item provided.
                # Use the itemjson to populate the form
                data = getFormdataFromItemjson(
                    request, itemJson, itemType, newCategory)

                # Inform the user that there is data in the session.
                item_name = sessionItem['id'][:6] \
                    if sessionItem['id'] != colander.null else ''
                if sessionItem['id'] != colander.null:
                    if itemType == 'activities':
                        item_url = request.route_url(
                            'activities_read_one', output='form',
                            uid=sessionItem['id'])
                    elif itemType == 'stakeholders':
                        item_url = request.route_url(
                            'stakeholders_read_one', output='form',
                            uid=sessionItem['id'])
                else:
                    if itemType == 'activities':
                        item_url = request.route_url(
                            'activities_read_many', output='form')
                    elif itemType == 'stakeholders':
                        item_url = request.route_url(
                            'stakeholders_read_many', output='form')

                msg = render(
                    get_customized_template_path(
                        request,
                        'parts/messages/unsaved_data_different_form.mak'),
                    {
                        'url': item_url,
                        'name': item_name,
                        'type': itemType
                    },
                    request
                )
                session.flash(msg)

        elif itemJson is None and sessionItem is not None:
            # No item was provided (create form) but some data was found in the
            # session.

            if (sessionItem['id'] != colander.null
                    and sessionItem['version'] != colander.null):
                # The item in the session is not new. Show empty form data
                # (already defined) and inform the user.
                item_name = sessionItem['id'][:6] \
                    if sessionItem['id'] != colander.null \
                    else _('Unknown Item')
                if sessionItem['id'] != colander.null:
                    if itemType == 'activities':
                        item_url = request.route_url(
                            'activities_read_one', output='form',
                            uid=sessionItem['id'])
                    elif itemType == 'stakeholders':
                        item_url = request.route_url(
                            'stakeholders_read_one', output='form',
                            uid=sessionItem['id'])
                else:
                    if itemType == 'activities':
                        item_url = request.route_url(
                            'activities_read_many', output='form')
                    elif itemType == 'stakeholders':
                        item_url = request.route_url(
                            'stakeholders_read_many', output='form')

                msg = render(
                    get_customized_template_path(
                        request,
                        'parts/messages/unsaved_data_different_form.mak'),
                    {
                        'url': item_url,
                        'name': item_name,
                        'type': itemType
                    },
                    request
                )
                session.flash(msg)

            else:
                # The item in the session is new.
                # If the form is rendered for the first time, inform the
                # user that session was used.

                sessionItem['category'] = newCategory
                data = sessionItem

                if formSubmit is False and newInvolvement is None:
                    # Inform the user that data from the session is used.
                    url = request.route_url(
                        'form_clear_session', item=itemType, attr='form',
                        _query={'url': request.url})
                    msg = render(
                        get_customized_template_path(
                            request,
                            'parts/messages/unsaved_data_same_form.mak'),
                        {'url': url},
                        request
                    )
                    session.flash(msg)

        elif itemJson is not None:
            # An item was provided to show in the form (edit form)
            # Simply show the data of the provided item in the form.
            data = getFormdataFromItemjson(
                request, itemJson, itemType, newCategory)

        else:
            # No itemjson and no sessionitem, do nothing (empty data already
            # defined above).
            pass

        #        log.debug('Data used to populate the form: %s' % data)

        html = form.render(data)

    # If the current category contains involvements (eg. to add Stakeholders to
    # an Activity), show a (initially empty) div which will contain the form
    # for Stakeholders.
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
    taggroup_count = len(itemJson.get('taggroups', []))
    # Hack to avoid showing involvements of items to be deleted (with no
    # taggroups)
    if taggroup_count == 0:
        itemJson['involvements'] = []

    deform.Form.set_default_renderer(mako_renderer)
    configCategoryList = getCategoryList(request, itemType)
    schema = addHiddenFields(colander.SchemaNode(colander.Mapping()), itemType)
    schema.add(colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextInputWidget(template='hidden'),
        name='statusId',
        title='',
        missing=colander.null
    ))
    for cat in sorted(
            configCategoryList.getCategories(), key=lambda cat: cat.order):
        schema.add(cat.getForm(request, readonly=True))

    form = deform.Form(schema)
    data = getFormdataFromItemjson(request, itemJson, itemType, readOnly=True)

    if data == {}:
        # If no formdata is available, it is very likely that the form has some
        # errors. In this case show an error message.
        errorList = checkValidItemjson(
            configCategoryList, itemJson, output='list')
        if len(errorList) > 0:
            url = None
            routeName = 'activities_read_one_history' \
                if itemType == 'activities' \
                else 'stakeholders_read_one_history'
            if 'id' in itemJson:
                url = request.route_url(
                    routeName, output='html', uid=itemJson['id'])
            errorMsg = render(
                get_customized_template_path(
                    request, 'parts/messages/item_requested_not_valid.mak'),
                {'url': url},
                request
            )
            return {
                'form': errorMsg
            }

    if 'category' in data and data['category'] is None:
        data['category'] = 0

    data['itemType'] = itemType
    statusId = itemJson['status_id'] if 'status_id' in itemJson \
        else colander.null
    data['statusId'] = statusId
    data['taggroup_count'] = taggroup_count
    html = form.render(data, readonly=True)

    geometry = json.dumps(
        itemJson['geometry']) if 'geometry' in itemJson else None

    # extract deal areas as polygons, contained in dictionary
    dealAreas = getTaggroupGeometries(itemJson)

    return {
        'form': html,
        'geometry': geometry,
        'dealAreas': json.dumps(dealAreas)
    }


def renderReadonlyCompareForm(
        request, itemType, refFeature, newFeature, review=False):
    """
    Return a rendered form used for comparison (for comparison or review
    purposes).
    """
    reviewableMessage = None

    deform.Form.set_default_renderer(mako_renderer_compare)
    configCategoryList = getCategoryList(request, itemType)

    compareMode = 'review' if review is True else 'compare'
    schema = addHiddenFields(colander.SchemaNode(colander.Mapping()), itemType)
    for cat in configCategoryList.getCategories():
        schema.add(cat.getForm(request, readonly=True, compare=compareMode))

    schema.add(colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        name='geomchange',
        title='',
        missing=colander.null
    ))

    form = deform.Form(schema)
    validComparison = True

    refData = {}
    if refFeature is not None:
        refData = getFormdataFromItemjson(
            request, refFeature.to_table(request), itemType, readOnly=True)
        if refData == {}:
            validComparison = False

    newData = {}
    if newFeature is not None:
        newData = getFormdataFromItemjson(
            request, newFeature.to_table(request), itemType, readOnly=True,
            compareFeature=newFeature)
        if newData == {}:
            validComparison = False

        if review is True and 'reviewable' in newData:
            reviewable = newData['reviewable']
            if reviewable == -2:
                reviewableMessage = _(
                    'At least one of the involvements prevents automatic '
                    'revision. Please review these involvements separately.')
            elif reviewable == -3:
                reviewableMessage = _(
                    'This version contains changed involvements which prevent '
                    'automatic revision. Please review these involvements.')
            elif reviewable < 0:
                reviewableMessage = 'Something went wrong.'

        if review is True and 'reviewable' not in newData and refFeature and \
                newFeature and len(refFeature.get_involvements()) > \
                len(newFeature.get_involvements()) and \
                itemType == 'stakeholders':
            # If the Stakeholder is to be deleted (no taggroups), do not show
            # the warning and enable review
            if len(newFeature.get_taggroups()) > 0:
                reviewableMessage = _(
                    'At least one of the involvements prevents automatic '
                    'revision. Please review these involvements separately.')

    if validComparison is False:
        # If no formdata is available, it is very likely that the form has some
        # errors. In this case show an error message.
        url = None
        routeName = 'activities_read_one_history' if itemType == 'activities' \
            else 'stakeholders_read_one_history'
        if refFeature is not None:
            url = request.route_url(
                routeName, output='html', uid=refFeature.get_guid())
        elif newFeature is not None:
            url = request.route_url(
                routeName, output='html', uid=newFeature.get_guid())
        errorMsg = render(
            get_customized_template_path(
                request, 'parts/messages/comparison_not_valid.mak'),
            {'url': url},
            request
        )
        return {
            'error': errorMsg
        }

    data = mergeFormdata(refData, newData)



    geometry = None
    if itemType == 'activities':
        newGeometry = newFeature.get_geometry() if newFeature is not None \
            else None
        refGeometry = refFeature.get_geometry() if refFeature is not None \
            else None

        # get polygeon geometries from taggroups
        newDealAreas = getTaggroupGeometriesCompare(newData)
        refDealAreas = getTaggroupGeometriesCompare(refData)

        geometry = json.dumps({
            'ref': {
                'geometry': refGeometry,
                'dealAreas': json.dumps(refDealAreas)
            },
            'new': {
                'geometry': newGeometry,
                'dealAreas': json.dumps(newDealAreas)
            },
        })

    # renders form; passes variables (readonly and geometry) to template
    ## TODO: in custom map mapping: pass params like this
    html = form.render(data, readonly=True, geometry=geometry)

    return {
        'form': html,
        'geometry': geometry,
        'reviewableMessage': reviewableMessage,
    }


def addHiddenFields(schema, itemType):
    """
    Function to add hidden fields (for meta data of the item) to a form schema.
    Fields are added for:
    - id (the identifier of the item)
    - version (the version being edited)
    - category (the category of the form which is being edited)
    - itemType
    """
    # For some reason, the deform.widget.HiddenWidget() does not seem to work.
    # Instead, the TextInputWidget is used with the hidden template.
    schema.add(colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextInputWidget(template='hidden'),
        name='id',
        title='',
        missing=colander.null
    ))
    schema.add(colander.SchemaNode(
        colander.Int(),
        widget=deform.widget.TextInputWidget(template='hidden'),
        name='version',
        title='',
        missing=colander.null
    ))
    schema.add(colander.SchemaNode(
        colander.Int(),
        widget=deform.widget.TextInputWidget(template='hidden'),
        name='category',
        title='',
        missing=colander.null
    ))
    schema.add(colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextInputWidget(template='hidden'),
        name='itemType',
        title='',
        missing=colander.null,
        default=itemType
    ))
    schema.add(colander.SchemaNode(
        colander.Int(),
        widget=deform.widget.TextInputWidget(template='hidden'),
        name='taggroup_count',
        title='',
        missing=colander.null
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
        for c in request.session[sessionKeyword]:
            try:
                # Only keep integers
                int(c)
                sessionCategories.append(c)
            except ValueError:
                pass

    buttons = []
    # Only show categories if there is more than 1 category
    if len(categorylist) > 1:
        for cat in categorylist:
            b = deform.Button('step_%s' % str(cat[0]), cat[1], css_class='')
            if str(cat[0]) in sessionCategories:
                b.css_class = 'formstepvisited'
            if currentCategory is not None and str(cat[0]) == str(
                    currentCategory):
                b.css_class = 'formstepactive'
            buttons.append(b)
    buttons.append(
        deform.Button('submit', _('Submit'), css_class='formsubmit'))
    return buttons


def doUpdate(request, itemType, diff):
    """
    Function to do the update / create of an Activity or a Stakeholder.
    Returns
    - a boolean indicating the success of the update
    - either a dict with some return values of the newly created item (if
      success is true) or an error message (if success if false)
    """
    if itemType not in ['activities', 'stakeholders']:
        return False, 'Not a valid Item'

    if itemType == 'activities':
        protocol = ActivityProtocol(DBSession)
    else:
        protocol = StakeholderProtocol(DBSession)

    # Use the protocol to create/update the Item
    ids = protocol.create(request, data=diff)

    if ids is None or len(ids) != 1:
        return False, _('The Item could not be created or updated.')

    item = ids[0]

    # Query the Item again to put together the return values. This is needed if
    # the created Item is to be used directly as an involvement.

    # Use the protocol to query the created item
    feature = protocol.read_one_by_version(
        request, item.identifier, item.version)

    if feature is None:
        return False, _('The Item was created but not found.'), None

    unknownString = _('Unknown')

    # We need to know which fields of the Item are used to populate the display
    # fields in the involvement overview.
    categorylist = getCategoryList(request, itemType)

    # Set all values to 'unknown' first
    keyValues = []
    overviewKeys = [
        o[0] for o in categorylist.getInvolvementOverviewKeyNames()]
    for k in overviewKeys:
        keyValues.append([k, unknownString])

    # Update the value if available
    for tg in feature.get_taggroups():
        for k in keyValues:
            if tg.get_tag_by_key(k[0]) is not None:
                k[1] = tg.get_tag_by_key(k[0]).get_value()

    returnDict = {}
    for k in keyValues:
        returnDict[k[0]] = k[1]

    # Add the version and the id to the dict as well
    returnDict['version'] = item.version
    returnDict['id'] = str(item.identifier)

    return True, returnDict


def mako_renderer(tmpl_name, **kw):
    """
    A helper function to use the mako rendering engine.
    It seems to be necessary to locate the templates by using the asset
    resolver.
    """
    request = get_current_request()
    # Redirect base form templates to customized templates
    if tmpl_name in [
        'form', 'readonly/form', 'customInvolvementMapping',
        'readonly/customInvolvementMappingStakeholder',
        'readonly/customInvolvementMappingActivity'
    ]:
        resolver = lokpAssetResolver.resolve(get_customized_template_path(
            request, 'form/%s.mak' % tmpl_name))
    else:
        resolver = lokpAssetResolver.resolve(
            'templates/form/%s.mak' % tmpl_name)
    template = Template(filename=resolver.abspath())

    # Add the request to the keywords so it is available in the templates.
    kw['request'] = request
    kw['_'] = _

    return template.render(**kw)


def mako_renderer_compare(tmpl_name, **kw):
    """
    A helper function to use the mako rendering engine.
    It seems to be necessary to locate the templates by using the asset
    resolver.
    """
    request = get_current_request()
    # Redirect base form templates to customized templates
    if tmpl_name in ['readonly/form', 'customInvolvementMapping']:
        resolver = lokpAssetResolver.resolve(get_customized_template_path(
            request, 'review/%s.mak' % tmpl_name))
    else:
        resolver = lokpAssetResolver.resolve(
            'templates/review/%s.mak' % tmpl_name)
    template = Template(filename=resolver.abspath())

    # Add the request to the keywords so it is available in the templates.
    kw['request'] = request
    kw['_'] = _

    return template.render(**kw)

# get polygons (geometries) from itemJson
def getTaggroupGeometries(itemJson):
    taggroups = itemJson['taggroups']
    dealAreas = dict();
    for taggroup in taggroups:
        if 'geometry' in taggroup:
            key = taggroup.get('main_tag').get('key')
            dealAreas[key] = (taggroup.get('geometry'))
    return dealAreas

# get polygon geometries from data
## TODO: remove hardcoding!
def getTaggroupGeometriesCompare(data):
    dealAreas = dict();
    if bool(data): # returns false if dictionary is empty

        taggroups = data.get('1') # flatten dict
        taggroup_landarea = taggroups.get('12') # 12 is id for taggroup landarea

        taggroup_keys = taggroup_landarea.keys()

        for key in taggroup_keys:
            tag = taggroup_landarea.get(key)

            # if tag is a list, remove list
            if type(tag) is list:
                tag = tag[0]

            geometry = tag.get('map'+key)

            taggroup_keys = tag.keys()

            if 'Intended area (ha)' in taggroup_keys:
                dealAreas['Intended area (ha)'] = geometry
            if 'Contract area (ha)' in taggroup_keys:
                dealAreas['Contract area (ha)'] = geometry
            if 'Current area in operation (ha)' in taggroup_keys:
                dealAreas['Current area in operation (ha)'] = geometry

    return dealAreas