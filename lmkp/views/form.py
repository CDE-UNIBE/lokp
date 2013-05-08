import colander
import copy
import deform
import logging
from mako.template import Template

from lmkp.views.form_config import *

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
    return HTTPFound(request.route_url('/'))

def renderForm(request, itemType, itemJson=None):

    # TODO: Get this from request or somehow
    lang = 'fr' # So far, it doesn't matter what stands here

    session = request.session

    log.debug('Session before processing the form: %s' % session)

    # Define the initial categories of the form
    oldCategory = None
    newCategory = 2

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
    
    # Get the configuration of the categories (as defined in the config yaml)
    configCategoryList = getCategoryList(request, itemType, lang)

    # Collect a list with id and names of all available categories which will be
    # used to create the buttons
    categoryListButtons = []
    for cat in sorted(configCategoryList.getCategories(),
        key=lambda cat: cat.order):
        categoryListButtons.append((cat.getId(), cat.getName()))

    captured = None
    formHasErrors = False

    # Handle form submission
    for p in request.POST:
        if p.startswith('step_') or p == 'submit':
            # Do a validation of the submitted form data. To do this, it is
            # necessary to recreate a form with the same category that was
            # submitted.

            # Prepare the form with the submitted category
            oldschema = addHiddenFields(colander.SchemaNode(colander.Mapping()))
            oldCat = configCategoryList.findCategoryById(oldCategory)
            if oldCat is not None:
                oldschema.add(oldCat.getForm(request))
            buttons = getFormButtons(request, categoryListButtons, oldCategory)
            form = deform.Form(oldschema, buttons=buttons)

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

                    if 'activity' in session:
                        formdata = copy.copy(session['activity'])

                        # TODO: Do the actual POST request to create/update the
                        # stuff.

                        log.debug('The complete formdata as in the session: %s' % formdata)

                        diff = formdataToDiff(request, formdata, itemType)

                        log.debug('The diff to create/update the item: %s' % diff)

                        # Clear the session
                        doClearFormSessionData(request)

                        feedbackMessage = 'Form submitted! (well, actually not yet)'
                    else:
                        feedbackMessage = 'Nothing submitted (something went wrong)'

                    return {
                        'form': feedbackMessage,
                        'css_links': [],
                        'js_links': []
                    }

            break

    if formHasErrors is False:
        # If nothing was submitted or the captured form data was stored
        # correctly, create a form with the (new) current category.
        newschema = addHiddenFields(colander.SchemaNode(colander.Mapping()))
        newCat = configCategoryList.findCategoryById(newCategory)
        if newCat is not None:
            newschema.add(newCat.getForm(request))
        buttons = getFormButtons(request, categoryListButtons, newCategory)
        form = deform.Form(newschema, buttons=buttons)

        # The form contains empty data by default
        data = {'category': newCategory}

        # Decide which data to show in the form
        if itemJson is not None and 'activity' not in session:
            # An item was provided to show in the form (edit form) and no values
            # are in the session yet.
            # Simply show the data of the provided item in the form.
            data = getFormdataFromItemjson(request, itemJson, itemType,
                newCategory)
        elif itemJson is not None and 'activity' in session:
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
                    session.flash('Unsaved data of this item was found in the session. You may continue to edit this form.<br/><a href="/form/clearsession?url=%s">Click here to delete the session data to clear the form.</a>' % request.url)

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
                session.flash('Unsaved data from another form (item: %s) was found in the session and will be deleted if you edit this form.<br/><a href="%s">Click here to see the other item and submit it.</a>' % (item_name, item_url))

        elif itemJson is None and 'activity' in session:
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
                session.flash('Unsaved data from another form (item: %s) was found in the session and will be deleted if you edit this form.<br/><a href="%s">Click here to see the other item and submit it.</a>' % (item_name, item_url))

            else:
                # Use the data in the session to populate the form.
                sessionActivity = copy.copy(session['activity'])
                sessionActivity['category'] = newCategory
                data = sessionActivity
                if formSubmit is False:
                    # If the form is rendered for the first time, inform the
                    # user that session was used.
                    session.flash('Unsaved data of this item was found in the session. You may continue to edit this form.<br/><a href="/form/clearsession?url=%s">Click here to delete the session data to clear the form.</a>' % request.url)
        
        else:
            # No itemjson and no sessionitem, do nothign (empty data already defined above)
            # If there is no existing item, show the form with empty data
            pass # Empty data already defined above

        log.debug('Data used to populate the form: %s' % data)

        html = form.render(data)

    # Add JS and CSS requirements (for widgets)
    resources = form.get_widget_resources()

    log.debug('Session after processing the form: %s' % session)

    return {
        'form': html,
        'css_links': resources['css'],
        'js_links': resources['js']
    }

def doClearFormSessionData(request):
    """
    Function to clear the session of any form-related data.
    """
    # Clear the session of any form data
    if 'activity' in request.session:
        del(request.session['activity'])

def addHiddenFields(schema):
    """
    Function to add hidden fields (for meta data of the item) to a form schema.
    Fields are added for:
    - id (the identifier of the item)
    - version (the version being edited)
    - category (the category of the form which is being edited)
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
    return schema

def getFormButtons(request, categorylist, currentCategory=None):
    """
    Function returning an array of form buttons (one button for each category
    and one final submit button). If a current category is provided, the button
    of this category gets a special css class.
    """
    _ = request.translate
    buttons = []
    for cat in categorylist:
        b = deform.Button('step_%s' % cat[0], cat[1], css_class='')
        if currentCategory is not None and cat[0] == str(currentCategory):
            b.css_class='formstepactive'
        buttons.append(b)
    buttons.append(deform.Button('submit', _('Submit'), css_class='formsubmit'))
    return buttons

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

    # Get the list of categories (needed to validate the tags)
    categorylist = getCategoryList(request, itemType)

    taggroups = itemJson['taggroups']

    data = {
        'id': itemJson['id'],
        'version': itemJson['version'],
        'category': category
    }

    for taggroup in taggroups:

        # Get the category and thematic group based on the maintag
        mt = taggroup['main_tag']
        cat, thmg, tg = categorylist.findCategoryThematicgroupTaggroupByMainkey(
            mt['key'])

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
                if maintag.getKey().getType().lower() == 'checkbox':
                    # Checkboxes: List of tuples with name and tg_id
                    tagsdata[t['key']] = [(t['value'], taggroup['tg_id'])]
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
                        log.debug('DUPLICATE TAGGROUP: Taggroup %s in thematic group %s and category %s appears twice although it is not repeatable!' % (cat, thmg, tg))
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

    log.debug('Formdata created by ItemJSON: %s' % data)
    
    return data

def formdataToDiff(request, newform, itemType, category=None):
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

    def findRemoveTgByCategoryThematicgroupTgid(form, category, thematicgroup,
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
                                elif checkbox is True and 'tg_id' not in t:
                                    # Checkboxes: The actual taggroups are in a
                                    # list one level further down
                                    for (k, v) in t.iteritems():
                                        if not isinstance(v, list):
                                            continue
                                        for (value, taggroupid) in v:
                                            if str(taggroupid) == tg_id:
                                                # If the taggroup was found,
                                                # remove it from the list.
                                                v.remove((value, taggroupid))
                                                if len(v) == 0:
                                                    # If there is no further
                                                    # taggroup in the lits, set
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
        # Category should be the same as parameter in function
        if category is not None and newform['category'] != category:
            log.debug('NOT THE SAME CATEGORIES: %s vs %s' % (newform['category'], category))
        del newform['category']

    if identifier != colander.null and version != colander.null:

        # Use the protocol to query the values of the version which was edited
        if itemType == 'stakeholders':
            # TODO: Make this work for stakeholders as well.
            print "**STAKEHOLDERS NOT YET IMPLEMENTED**"
        else:
            from lmkp.views.activity_protocol3 import ActivityProtocol3
            from lmkp.models.meta import DBSession as Session
            protocol = ActivityProtocol3(Session)

        item = protocol.read_one_by_version(
            request, identifier, version
        )
        olditemjson = item.to_table(request)

        # Look only at the values transmitted to the form and therefore visible
        # to the editor.
        oldform = getFormdataFromItemjson(request, olditemjson, itemType, category)
        if 'id' in oldform:
            del oldform['id']
        if 'version' in oldform:
            del oldform['version']
        if 'category' in oldform:
            del oldform['category']

    taggroupdiffs = []

    # Loop the newform to check if there are taggroups which changed or are new

    # Loop the categories of the form
    for (cat, thmgrps) in newform.iteritems():
        # Loop the thematic groups of the category
        for (thmgrp, tgroups) in thmgrps.iteritems():
            # Loop the tags of each taggroup
            for (tgroup, tags) in tgroups.iteritems():

                # Transform all to list so they can be treated all the same
                if not isinstance(tags, list):
                    tags = [tags]

                for t in tags:
                    if t['tg_id'] != colander.null:
                        # Taggroup was there before because it contains a tg_id.
                        # Check if it contains changed values.

                        # Try to find the taggroup by its tg_id in the oldform
                        oldform, oldtaggroup = findRemoveTgByCategoryThematicgroupTgid(
                            oldform, cat, thmgrp, t['tg_id'])

                        if oldtaggroup is None:
                            # This should never happen since all tg_ids should
                            # be known.
                            continue

                        deletedtags = []
                        addedtags = []

                        for (k, v) in t.iteritems():

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
                                elif (k in oldtaggroup and v != oldtaggroup[k]
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
                                                }]
                                            })
                                        else:
                                            # Try to find and remove the
                                            # taggroup in the old form
                                            oldform, oldtaggroup = findRemoveTgByCategoryThematicgroupTgid(
                                                oldform, cat, thmgrp, tg_id, True)
                                            if oldtaggroup is not True:
                                                # This basically should not happen because the tg_id always should be found.
                                                log.debug('TG_ID NOT FOUND: When trying to find and remove taggroup by tg_id (%s), the taggroup was not found in the old form.' % tg_id)
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
                            tagdiffs = []
                            for at in addedtags:
                                tagdiffs.append({
                                    'key': at['key'],
                                    'value': at['value'],
                                    'op': 'add'
                                })
                            taggroupdiffs.append({
                                'op': 'add',
                                'tags': tagdiffs
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

    if len(taggroupdiffs) > 0:
        itemdiff = {
            'taggroups': taggroupdiffs
        }
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

    # Make the translation method (_) available in the templates.
    request = get_current_request()
    kw['_'] = request.translate

    return template.render(**kw)