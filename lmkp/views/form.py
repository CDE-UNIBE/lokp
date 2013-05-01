import colander
import deform
import logging


from lmkp.views.form_config import *

from pyramid.view import view_config

log = logging.getLogger(__name__)

@view_config(route_name='form_tests', renderer='lmkp:templates/form_test.pt')
def form_tests(request):

    # TODO: Get this from request or somehow
    itemType = 'activities'
    # TODO: Get version and identifier from request or somehow.
    version = None
    identifier = None
    lang = 'fr' # So far, it doesn't matter what stands here

    categorylist = getCategoryList(request, itemType, lang)

    # Collect the forms for each category
    cat_forms = []
    for cat in categorylist.getCategories():
        cat_forms.append(cat.getForm())

    # Put together all categories to one Schema
    schema = colander.SchemaNode(colander.Mapping())
    for cat_form in cat_forms:
        schema.add(cat_form)

    # Add hidden fields for the identifier and the version
    schema.add(colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget(),
        name='id',
        missing = colander.null
    ))
    schema.add(colander.SchemaNode(
        colander.Int(),
        widget=deform.widget.HiddenWidget(),
        name='version',
        missing = colander.null
    ))

    # Prepare the form
    form = deform.Form(schema, buttons=('submit',))

    # Add JS and CSS requirements (for widgets)
    resources = form.get_widget_resources()

    captured = None
    success = None

#    version = 2
#    identifier = 'd0f5b496-edcd-458c-84a9-72ca4e1135f5'

    version = 3
    identifier = 'd0f5b496-edcd-458c-84a9-72ca4e1135f5'

    if version is not None and identifier is not None:
        # If there is an existing item, use the protocol to find the values to
        # display in the form.
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
        itemjson = item.to_table(request)
        data = getFormdataFromItemjson(request, itemjson, itemType)

    else:
        # If there is no existing item, show the form with empty data
        data = {}

    if 'submit' in request.POST:
        # The request contains the data of a form submission.
        try:
            # Try to validate the submitted values
            controls = request.POST.items()
            captured = form.validate(controls)
            if success:
                response = success()
                if response is not None:
                    return response

            log.debug('Captured data by form: %s' % captured)

            diff = formdataToDiff(request, captured, itemType)

            log.debug('Diff of object: %s' % diff)

            html = form.render(captured)

        except deform.ValidationFailure as e:
            # The submitted values could not be validated, show the form again
            # but with error messages
            html = e.render()

    else:
        # No data submitted, show the form.
        html = form.render(data)

    return {
        'form': html,
        'css_links': resources['css'],
        'js_links': resources['js']
    }

def getFormdataFromItemjson(request, itemJson, itemType):
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
        'version': itemJson['version']
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
            data[cat] = {thmg: {tgid: tagsdata}}

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
        oldform = getFormdataFromItemjson(request, olditemjson, itemType)
        if 'id' in oldform:
            del oldform['id']
        if 'version' in oldform:
            del oldform['version']

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

