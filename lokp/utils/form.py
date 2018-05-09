import copy
import json
import logging

import colander
import datetime
from pyramid.httpexceptions import HTTPBadRequest

from lokp.config.form import getCategoryList
from lokp.models import DBSession
from lokp.protocols.activity_protocol import ActivityProtocol
from lokp.protocols.stakeholder_protocol import StakeholderProtocol
from lokp.review.activities import ActivityReview
from lokp.review.stakeholders import StakeholderReview
from lokp.utils.views import validate_item_type

log = logging.getLogger(__name__)


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
            a, d = structHasOnlyNullValues(cstruct[c], depth + 1)
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


def calculate_deletion_diff(request, item_type):

    identifier = request.POST.get('id')
    version = request.POST.get('version')

    if not identifier or not version:
        raise HTTPBadRequest(
            'Unknown item to delete')

    if validate_item_type(item_type) == 'a':
        protocol = ActivityProtocol(DBSession)
        other_item_type = 'stakeholders'
    else:
        protocol = StakeholderProtocol(DBSession)
        other_item_type = 'activities'

    item = protocol.read_one_by_version(
        request, identifier, version, translate=False).to_table(request)

    # Collect every taggroup and tag, mark all to be deleted.
    taggroups_diff = []
    for taggroup in item.get('taggroups', []):
        tags_diff = []
        for tag in taggroup.get('tags', []):
            tags_diff.append({
                'key': tag.get('key'),
                'value': tag.get('value'),
                'op': 'delete'
            })
        taggroups_diff.append({
            'tg_id': taggroup.get('tg_id'),
            'tags': tags_diff,
            'op': 'delete'
        })

    # Collect every involvement and mark them to be deleted.
    involvement_diff = []
    for involvement in item.get('involvements', []):
        involvement_diff.append({
            'id': involvement.get('data', {}).get('id'),
            'version': involvement.get('version'),
            'role': involvement.get('role_id'),
            'op': 'delete'
        })

    diff = {
        item_type: [{
            'taggroups': taggroups_diff,
            'id': identifier,
            'version': version
        }]
    }
    if involvement_diff:
        diff[item_type][0][other_item_type] = involvement_diff

    return diff


def formdataToDiff(request, newform, itemType):
    """
    Use the formdata captured on submission of the form and compare it with the
    old version of an object to create a diff which allows to create/update the
    object.
    Approach: Loop all items of the newform and check if they are new or
    changed compared to the oldform. If so, add them to diff and set their
    values to null in the oldform. Any remaining items (with non-null values)
    of oldform were deleted and need to be added to diff as well.
    - newform: The form data captured on submission
    - itemType: activities / stakeholders
    """

    def _addInvolvementDictToList(invList, invDict):
        """
        Append an involvement in dict-form to a list of involvements.
        Add it only if it does not contain null values.
        """
        if ('id' in invDict and invDict['id'] != colander.null
                and 'version' in invDict and invDict['version'] != colander.null
                and 'role_id' in invDict
                and invDict['role_id'] != colander.null):
            try:
                int(invDict['role_id'])
                invList.append(invDict)
            except:
                pass
        return invList

    def _findRemoveTgByCategoryThematicgroupTgid(
            form, category, thematicgroup, tg_id, checkbox=False):
        """
        Helper function to find a taggroup by its category, thematic group and
        tg_id. If it was found, its values in the form are set to null and the
        tags are returned.
        """
        # Loop the categories of the form to find the one with the given id.
        for (cat, thmgrps) in form.items():
            if cat == category:
                # Loop the thematic groups of the category to find the one with
                # the given id.
                for (thmgrp, tgroups) in thmgrps.items():
                    if thmgrp == thematicgroup:
                        # Loop the taggroups of the thematic group
                        for (tgroup, tags) in tgroups.items():
                            # Transform them all to lists to handle them all
                            # the same.
                            if not isinstance(tags, list):
                                tags = [tags]
                            # Look at each taggroup and check the tg_id
                            for t in tags:
                                if 'tg_id' in t and t['tg_id'] == tg_id:
                                    ret = {}
                                    for (k, v) in t.items():
                                        # Copy the keys and values
                                        ret[k] = v
                                        # Set the values to null
                                        t[k] = colander.null
                                    return form, ret
                                elif checkbox is True and (
                                        'tg_id' not in t
                                        or t['tg_id'] == colander.null):
                                    # Checkboxes: The actual taggroups are in a
                                    # list one level further down
                                    for (k, v) in t.items():
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

                                                return form, True  # Return
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

    if 'itemType' in newform:
        # ItemType is not needed
        del newform['itemType']

    if 'statusId' in newform:
        # statusId is not needed
        del newform['statusId']

    if 'taggroup_count' in newform:
        del newform['taggroup_count']

    if identifier != colander.null and version != colander.null:

        # Use the protocol to query the values of the version which was edited
        if itemType == 'stakeholders':
            protocol = StakeholderProtocol(DBSession)
        else:
            protocol = ActivityProtocol(DBSession)

        item = protocol.read_one_by_version(
            request, identifier, version, translate=False
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
            # The form for Stakeholders has involvement fields in them which
            # are only used for display purposes (since involvements can only
            # be added on Activity side). We need to remove them before
            # processing the diff.
            if 'primaryinvestors' in oldform:
                del oldform['primaryinvestors']
            if 'secondaryinvestors' in oldform:
                del oldform['secondaryinvestors']

        for (oldcat, othmgrps) in oldform.items():
            # It is not sure that all of the form is in the session (the
            # newform variable). This is the case for example if a user did not
            # open a category of the form when editing the item.

            if oldcat not in newform:
                # For each category which is not in the newform but in the old
                # original form, copy the original to the newform.
                for (oldthmgrp, oldtgroups) in othmgrps.items():
                    # Because the values in the newform are rendered when
                    # submitted by the form, some values of the original form
                    # (which was not captured) need to be adopted to match.
                    for (oldtgroup, oldtags) in oldtgroups.items():
                        if not isinstance(oldtags, list):
                            if 'tg_id' not in oldtags:
                                oldtags['tg_id'] = colander.null
                            for (oldkey, oldvalue) in oldtags.items():
                                if isinstance(oldvalue, list):
                                    oldtags[oldkey] = set(oldvalue)

                newform[oldcat] = othmgrps

    categorylist = getCategoryList(request, itemType)
    taggroupdiffs = []
    involvementdiffs = []
    geometrydiff = None

    # Loop the newform to check if there are taggroups which changed or are new

    # Loop the categories of the form
    for (cat, thmgrps) in newform.items():

        try:
            thmgrpsitems = thmgrps.items()
        except AttributeError:
            continue

        # Loop the thematic groups of the category   // TODO: iterate over taggroup 12
        for (thmgrp, tgroups) in thmgrpsitems:

            if (thmgrp in categorylist.getInvolvementThematicgroupIds()
                    and itemType != 'stakeholders'):
                # Important: Involvements can only be changed from the side of
                # the activities!

                # In a first step, collect all the involvements there are in
                # the new form and the involvements that were in the oldform.
                # Use them only if they have an id, a version and a role_id.
                newInvolvements = []
                oldInvolvements = []

                for (tgrp, involvements) in tgroups.items():

                    if isinstance(involvements, dict):
                        newInvolvements = _addInvolvementDictToList(
                            newInvolvements, involvements)

                    elif isinstance(involvements, list):
                        for i in involvements:
                            newInvolvements = _addInvolvementDictToList(
                                newInvolvements, i)

                # Collect the old involvement data from the original form with
                # the same category and thematic group.
                if (str(cat) in oldform and str(thmgrp) in oldform[str(cat)]):
                    oldInvgrp = oldform[str(cat)][str(thmgrp)]

                    for (invName, invData) in oldInvgrp.items():
                        if isinstance(invData, dict):
                            oldInvolvements = _addInvolvementDictToList(
                                oldInvolvements, invData)

                        elif isinstance(invData, list):
                            for i in invData:
                                oldInvolvements = _addInvolvementDictToList(
                                    oldInvolvements, i)

                # Loop the new involvements and try to find them in the old
                # involvements (based on their identifier, version and
                # role_id). If they are found, remove them from the list of
                # old involvements. If they are not found, mark them as newly
                # added.
                for ni in newInvolvements:
                    found = False

                    for oi in oldInvolvements:

                        if (ni['id'] == oi['id']
                                and ni['version'] == oi['version']
                                and str(ni['role_id']) == str(oi['role_id'])):
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

            if thmgrp in categorylist.getMapThematicgroupIds():
                # Map data

                cfgThmg = categorylist.findThematicgroupById(thmgrp)

                for (tgrp, map) in tgroups.items():

                    if tgrp != cfgThmg.getMap().getName():
                        continue

                    oldgeom = None
                    if (cat in oldform and thmgrp in oldform[cat]
                            and cfgThmg.getMap().getName()
                            in oldform[cat][thmgrp]):
                        oldgeom = oldform[cat][thmgrp][
                            cfgThmg.getMap().getName()]
                        oldgeometry = json.loads(oldgeom['geometry'])

                    geometry = (
                        map['geometry'] if 'geometry' in map
                                           and map['geometry'] != colander.null else None)

                    if geometry is None:
                        continue

                    geometry = json.loads(geometry)

                    if oldgeom is None:
                        geometrydiff = geometry
                        continue

                    oldgeom = json.loads(oldgeom['geometry']) if 'geometry' in oldgeom else oldgeom
                    if json.dumps(oldgeom, sort_keys=True) != json.dumps(geometry, sort_keys=True):
                        geometrydiff = geometry

            # Loop the tags of each taggroup
            for (tgroup, tags) in tgroups.items():

                # Transform all to list so they can be treated all the same
                if not isinstance(tags, list):
                    tags = [tags]

                for t in tags:
                    if 'tg_id' not in t:
                        continue

                    if t['tg_id'] != colander.null:
                        # Taggroup was there before because it contains a
                        # tg_id. Check if it contains changed values.

                        # Make a copy of the tags because the function to find
                        # and remove below modifies t.
                        t_copy = copy.copy(t)

                        # Try to find the taggroup by its tg_id in the oldform
                        oldform, oldtaggroup = \
                            _findRemoveTgByCategoryThematicgroupTgid(
                                oldform, cat, thmgrp, t['tg_id'])

                        if oldtaggroup is None:
                            # This should never happen since all tg_ids should
                            # be known.
                            log.debug(
                                '\n\n*** TG_ID NOT FOUND: When trying to find '
                                'and remove taggroup by tg_id (%s), the '
                                'taggroup was not found in the old form.\n\n'
                                % t['tg_id'])
                            continue

                        deletedtags = []
                        addedtags = []

                        for (k, v) in t_copy.items():

                            if type(v) == datetime.date \
                                    or type(v) == datetime.datetime:
                                v = datetime.datetime.strftime(v, '%Y-%m-%d')

                            oldv = oldtaggroup[k] if k in oldtaggroup else None
                            if type(oldv) == datetime.date \
                                    or type(oldv) == datetime.datetime:
                                oldv = datetime.datetime.strftime(
                                    oldv, '%Y-%m-%d')

                            if (k != 'tg_id'):
                                if (oldv is not None and
                                        str(v) != str(oldv)
                                        and v != colander.null):
                                    # Because the form renders values as
                                    # floats, it is important to compare them
                                    # correctly with an integer value
                                    try:
                                        if float(oldv) == float(v):
                                            continue
                                    except ValueError:
                                        pass
                                    except TypeError:
                                        pass

                                    # If a key is there in both forms but its
                                    # value changed, add it once as deleted and
                                    # once as added.
                                    deletedtags.append({
                                        'key': k,
                                        'value': oldv
                                    })
                                    addedtags.append({
                                        'key': k,
                                        'value': v
                                    })
                                elif (k not in oldtaggroup
                                      and v != colander.null):
                                    # If a key was not there in the oldform,
                                    # add it as added.
                                    addedtags.append({
                                        'key': k,
                                        'value': v
                                    })
                                elif (k in oldtaggroup
                                      and str(v) !=
                                      str(oldtaggroup[k])
                                      and v == colander.null):
                                    # If a key was in the oldform but not in
                                    # the new one anymore, add it as deleted.
                                    oldv = oldtaggroup[k]
                                    if type(oldv) == datetime.date or type(
                                            oldv) == datetime.datetime:
                                        oldv = datetime.datetime.strftime(
                                            oldv, '%Y-%m-%d')
                                    deletedtags.append({
                                        'key': k,
                                        'value': oldtaggroup[k]
                                    })

                        # Put together diff for the taggroup
                        if len(deletedtags) > 0 or len(addedtags) > 0:
                            tagdiffs = []
                            for dt in deletedtags:
                                del(oldtaggroup[dt['key']])
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
                            tgdiff = {
                                'tg_id': t['tg_id'],
                                'tags': tagdiffs
                            }
                            # If there are no tags left in the old taggroup,
                            # mark the entire taggroup diff to be deleted.
                            del(oldtaggroup['tg_id'])
                            if len(addedtags) == 0 and len(deletedtags) > 0 \
                                    and oldtaggroup == {}:
                                tgdiff['op'] = 'delete'
                            taggroupdiffs.append(tgdiff)

                    else:
                        # Taggroup has no tg_id. It is either a new taggroup to
                        # be added (if it contains values) or it may be a group
                        # of checkboxes (with tg_ids a level lower)
                        # For Checkboxes: Values cannot really change, they can
                        # only be added (if another checkbox is selected, a new
                        # taggroup is created). If a checkbox was submitted
                        # with a tg_id, it was there before already.
                        addedtags = []
                        addedtaggroups = []
                        for (k, v) in t.items():
                            if (k != 'tg_id' and v != colander.null):
                                if isinstance(v, set):
                                    # If the value is a set, the form displayed
                                    # a group of checkboxes. Each of the values
                                    # is treated as a separate taggroup.
                                    for (value, tg_id) in v:
                                        # Since we transformed all values to
                                        # unicode, also 'None' is a string now.
                                        if tg_id is None or tg_id == 'None':
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
                                            oldform, oldtaggroup = \
                                                _findRemoveTgByCategoryThematicgroupTgid(
                                                    oldform, cat, thmgrp,
                                                    tg_id, True)
                                            if oldtaggroup is None:
                                                # This basically should not
                                                # happen because the tg_id
                                                # always should be found.
                                                log.debug(
                                                    '\n\n*** TG_ID NOT FOUND: '
                                                    'When trying to find and '
                                                    'remove taggroup by tg_id '
                                                    '(%s), the taggroup was '
                                                    'not found in the old '
                                                    'form.\n\n' % tg_id)
                                else:
                                    # Write dates as string
                                    if type(v) == datetime.date or \
                                            type(v) == datetime.datetime:
                                        v = datetime.datetime.strftime(
                                            v, '%Y-%m-%d')

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

                            # Store date maintags also as string
                            if type(mainvalue) == datetime.date or type(
                                    mainvalue) == datetime.datetime:
                                mainvalue = datetime.datetime.strftime(
                                    mainvalue, '%Y-%m-%d')

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
    for (cat, thmgrps) in oldform.items():
        # Loop the thematic groups of the category
        for (thmgrp, tgroups) in thmgrps.items():
            # Loop the tags of each taggroup
            for (tgroup, tags) in tgroups.items():
                # Transform all to list so they can be treated all the same
                if not isinstance(tags, list):
                    tags = [tags]

                for t in tags:
                    if 'tg_id' in t and t['tg_id'] != colander.null:
                        deletedtags = []
                        for (k, v) in t.items():

                            if type(v) == datetime.date or \
                                    type(v) == datetime.datetime:
                                v = datetime.datetime.strftime(v, '%Y-%m-%d')

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
                        for (k, v) in t.items():
                            if not isinstance(v, list):
                                continue
                            for (value, taggroupid) in v:
                                # Add it directly to taggroups
                                taggroupdiffs.append({
                                    'op': 'delete',
                                    'tg_id': taggroupid,
                                    'tags': [{
                                        'key': k,
                                        'value': value,
                                        'op': 'delete'
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


def getFormdataFromItemjson(
        request, itemJson, itemType, category=None, **kwargs):
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

    readOnly = kwargs.get('readOnly', False)
    compareFeature = kwargs.get('compareFeature', None)
    if compareFeature is not None:
        if itemType == 'activities':
            review = ActivityReview(request)
        else:
            review = StakeholderReview(request)

    mapAdded = False

    if itemType == 'activities':
        otherItemType = 'stakeholders'
    else:
        otherItemType = 'activities'

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

        if compareFeature is not None:
            reviewable = 0
            inv = compareFeature.find_involvement_by_guid(data['id'])

            # Check if the involvement is reviewable. This is only important if
            # the version on the other side is pending or edited.
            if inv is not None and inv.get_status() in [1, 6]:
                reviewable = review._review_check_involvement(
                    inv._feature.getMappedClass(), inv._feature.get_guid(),
                    inv._feature.get_version())

            fields['reviewable'] = reviewable

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

    if ('involvements' in itemJson and (
            category is None or
            str(category) in categorylist.getInvolvementCategoryIds())):

        # Have a look at the involvements
        involvements = itemJson['involvements']

        otherCategoryList = getCategoryList(request, otherItemType)
        invOverviewKeys = [
            k[0] for k in otherCategoryList.getInvolvementOverviewKeyNames()]

        for inv in involvements:

            if 'role_id' not in inv:
                continue

            invCat, invThmg = categorylist.getGroupsByRoleId(inv['role_id'])
            if invCat is None or invThmg is None:
                continue

            invConfig = invThmg.getInvolvement()
            invData = _getInvolvementData(inv, invOverviewKeys)
            if 'reviewable' in invData:
                # For multiple involvements, do not always overwrite the flag
                # whether an involvement is reviewable or not. As error
                # messages have a negative code, use the minimal error code of
                # all involvements.
                if 'reviewable' in data:
                    data['reviewable'] = min(
                        data['reviewable'], invData['reviewable'])
                else:
                    data['reviewable'] = invData['reviewable']

            if readOnly and 'role_id' in invData:
                # For readonly forms, we need to populate the role_name with
                # the name of the Stakeholder_Role
                invRole = invConfig.findRoleById(invData['role_id'])
                if invRole is not None:
                    invData['role_name'] = invRole.getName()

            if str(invCat.getId()) not in data:
                data[str(invCat.getId())] = {}
            dataCat = data[str(invCat.getId())]

            if str(invThmg.getId()) not in dataCat:
                dataCat[str(invThmg.getId())] = {}
            dataThmg = dataCat[str(invThmg.getId())]

            if invConfig.getRepeatable() is True:
                if invConfig.getName() in dataThmg and len(
                        dataThmg[invConfig.getName()]) > 0:
                    dataThmg[invConfig.getName()].append(invData)
                else:
                    dataThmg[invConfig.getName()] = [invData]
            else:
                dataThmg[invConfig.getName()] = invData

    for taggroup in itemJson['taggroups']:

        # Get the category and thematic group based on the maintag
        mt = taggroup['main_tag']

        if mt is None:
            # If the maintag is empty, move on and do not add it to the form
            continue

        cat, thmg, tg = categorylist. \
            findCategoryThematicgroupTaggroupByMainkey(mt['key'])

        # Treat the id's all as strings
        cat = str(cat)
        thmg = str(thmg)

        if tg is None:
            # If the Form Taggroup for this maintag was not found, move on and
            # do not add it to form
            continue

        tgid = str(tg.getId())
        maintag = tg.getMaintag()

        if maintag.getKey().getType().lower() in ['checkbox', 'inputtoken']:
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

                v = t['value']
                if readOnly is True and configTag is not None:
                    # If the form is rendered for readOnly, use the translated
                    # value (of checkboxes, dropdowns etc.) if there is one.
                    configValue = configTag.findValueByName(v)
                    if configValue is not None:
                        v = configValue.getTranslation()

                if maintag.getKey().getType().lower() in [
                    'checkbox', 'inputtoken']:
                    # Checkboxes: List of tuples with name and tg_id
                    tagsdata[t['key']] = [(v, taggroup['tg_id'])]
                elif (configTag is not None
                      and configTag.getKey().getType().lower() == 'date'):
                    try:
                        d = datetime.datetime.strptime(v, '%Y-%m-%d')
                        tagsdata[t['key']] = d
                    except ValueError:
                        pass
                else:
                    tagsdata[t['key']] = v

        if 'geometry' in taggroup:
            #tagsdata['geometry'] = taggroup['geometry']
            tagsdata[tg.map.name] = {'geometry': taggroup['geometry']} # geometry values of polygons are added to edit session

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
                    elif (maintag.getKey().getType().lower() in [
                        'checkbox', 'inputtoken']
                          and t['key'] in data[cat][thmg][tgid]):
                        # Checkboxes: Add the data to the list of tuples
                        data[cat][thmg][tgid][t['key']] += tagsdata[t['key']]
                    else:
                        log.debug(
                            'DUPLICATE TAGGROUP: Taggroup %s in thematic group'
                            ' %s and category %s appears twice although it is '
                            'not repeatable!' % (tgid, thmg, cat))
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
            # Make sure all the necessary values are there and add it only
            # once.
            # TODO: The parameter 'map' is defined in the yaml (map: map) and
            # therefore rather static. Should this be made more dynamic?
            if (cat in data and thmg in data[cat]
                    and 'map' not in data[cat][thmg]
                    and 'geometry' in itemJson):
                mapAdded = True
                data[cat][thmg]['map'] = {
                    'geometry': json.dumps(itemJson['geometry'])
                }

    # Map
    if (category is not None
            and str(category) in categorylist.getMapCategoryIds()
            and mapAdded is False):
        # The current category contains a map which has not yet been added to
        # the form data. This may be the case if there are no other taggroups
        # in this category or thematic group filled out.
        cat = categorylist.findCategoryById(category)
        catId = str(cat.getId())

        if catId not in data:
            data[catId] = {}

        thematicgroup = None
        for thmg in categorylist.getMapThematicgroupIds():
            if cat.findThematicgroupById(thmg) is not None:
                thematicgroup = cat.findThematicgroupById(thmg)
                break

        if thematicgroup is not None and 'geometry' in itemJson:
            thmgId = str(thematicgroup.getId())

            if thmgId not in data[catId]:
                data[catId][thmgId] = {}

            data[catId][thmgId]['map'] = {
                'geometry': json.dumps(itemJson['geometry'])
            }

    log.debug('Formdata created by ItemJSON: %s' % data)

    return data


def checkValidItemjson(categorylist, itemJson, output='dict'):
    validMainkeys = categorylist.getAllMainkeyNames()

    taggroups = itemJson['taggroups']

    errors = []
    for taggroup in taggroups:
        maintag = taggroup['main_tag']

        # Make sure the maintag exists and contains values
        if maintag is None or 'key' not in maintag or maintag['key'] is None:
            errors.append(
                'Undefined Maintag: Maintag of taggroup %s is not defined or '
                'has no values.' % taggroup)
            continue

        # Make sure that the maintag is in the list of valid maintags according
        # to the configuration
        if maintag['key'] not in validMainkeys:
            errors.append(
                'Invalid Maintag: Maintag (%s) of taggroup %s is not a valid '
                'maintag according to the configuration.' % (
                    maintag['key'], taggroup))

        # Make sure that the taggroup contains only one mainkey according to
        # the configuration
        keys = []
        for tag in taggroup['tags']:
            keys.append(tag['key'])

        mainkeys = []
        for k in keys:
            if k in validMainkeys:
                mainkeys.append(k)

        if len(mainkeys) > 1:
            errors.append(
                'Too many Mainkeys: The taggroup %s should contain only 1 '
                'mainkey according to the configuration. It contains %s: %s'
                % (taggroup, len(mainkeys), ', '.join(mainkeys)))

        # Make sure that all the tags are valid keys in the same taggroup
        # according to the configuration
        if len(mainkeys) == 1:
            catId, thgId, confTaggroup = categorylist. \
                findCategoryThematicgroupTaggroupByMainkey(maintag['key'])
            if confTaggroup is not None:
                for k in keys:
                    if confTaggroup.hasKey(k) is False:
                        errors.append(
                            'Wrong key in taggroup: The key %s is not valid in'
                            ' a taggroup with mainkey %s' % (
                                k, maintag['key']))

    if len(errors) > 0:
        log.debug(
            '\n\n==================================\nThe itemJson is not valid'
            ' according to the yaml configuration. The following errors exist:'
            '\n** FORM ERROR ** %s\n==================================\n\n'
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


def doClearFormSessionData(request, item, attr):
    """
    Function to clear the session of any form-related data.
    """
    # Clear the session of any form data
    if item in request.session and attr in request.session[item]:
        del(request.session[item][attr])


def addCreatedInvolvementToSession(
        request, session, itemType, invName, created):
    """
    Add a newly created Involvement to the session so it is accessible when
    switching back to the original form.
    """

    if itemType not in session or 'form' not in session[itemType] \
            or invName is None:
        return False

    configList = getCategoryList(request, itemType)

    cat = configList.findCategoryByInvolvementName(invName)
    if cat is None or str(cat.getId()) not in session[itemType]['form']:
        return False
    sessionCat = session[itemType]['form'][str(cat.getId())]

    thmg = configList.findThematicgroupByInvolvementName(invName)
    if thmg is None or str(thmg.getId()) not in sessionCat:
        return False
    sessionThmg = sessionCat[str(thmg.getId())]

    if invName not in sessionThmg:
        return False

    sessionInv = sessionThmg[invName]
    newInv = created

    # Add a role to the new involvement. By default, use the first one
    # available
    configInv = thmg.getInvolvement()
    configRoles = configInv.getRoles()
    if len(configRoles) < 1:
        return False
    newInv['role_id'] = configRoles[0].getId()

    if isinstance(sessionInv, dict):
        # The involvemnt is not repeatable, there is only one which is to be
        # replaced
        sessionInv = newInv

    elif isinstance(sessionInv, list):
        # The involvements are repeatable.
        invAdded = False
        for i, inv in enumerate(sessionInv):
            # Try to use the first empty entry (no version or id)
            if inv['version'] != colander.null or inv['id'] != colander.null:
                continue
            sessionInv[i] = newInv
            invAdded = True

        if invAdded is False:
            # If the involvement was not added (because no empty entry was
            # found), add it to the end of the list
            sessionInv.append(newInv)

    else:
        return False

    # Update the session
    session[itemType]['form'][str(cat.getId())][str(thmg.getId())][invName] = \
        sessionInv

    log.debug('Added involvement to session: %s' % newInv)

    return True


def mergeFormdata(ref, new):
    """
    Merge two formdatas to create a single formdata which can be used in a
    compareForm as rendered by the function renderReadonlyCompareForm.
    The formdata has the following structure:
    '1': {
        '5': {
            'ref_1': [
                {
                    'tg_id': 0,
                    '[A] Integerfield 1': 1,
                    '[A] Numberfield 2': 2,
                    'change': 'change'
                }
            ],
            'new_1': [
                {
                    'tg_id': 0,
                    '[A] Integerfield 1': 3,
                    '[A] Numberfield 2': 4,
                    'change': 'change'
                }
            ],
            'change': 'change'
        },
        'change': 'change'
    }
    """

    def _addPrefixToEachTaggroup(data, prefix):
        """
        Adds a prefix to each taggroup in the form:
        [PREFIX]_[ID]
        """
        new_data = {}
        for cat_id, cat in data.items():
            if cat_id in ['category', 'version', 'id', 'reviewable']:
                continue
            new_cat = {}
            for thmg_id, thmg in cat.items():
                new_thmg = {}
                for tg_id, tg in thmg.items():
                    new_thmg['%s_%s' % (prefix, tg_id)] = tg
                new_cat[thmg_id] = new_thmg
            new_data[cat_id] = new_cat
        return new_data

    def _mergeDicts(a, b, path=None):
        """
        Merge one dict in another.
        http://stackoverflow.com/a/7205107/841644
        """
        if path is None:
            path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    _mergeDicts(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass  # same leaf value
                else:
                    raise Exception(
                        'Conflict at %s' % '.'.join(path + [str(key)]))
            else:
                a[key] = b[key]
        return a

    # Mark all taggroups of the two versions with 'ref' or 'new' respectively.
    # Then merge the two dicts.
    merged = _mergeDicts(
        _addPrefixToEachTaggroup(ref, 'ref'),
        _addPrefixToEachTaggroup(new, 'new'))

    # Mark each thematicgroup and category which have changes in them. Also
    # make sure that each taggroups missing in one version receive a flag so
    # they are displayed as well in the form table.
    geomChanged = False
    for cat_id, cat in merged.items():
        catChanged = False
        for thmg_id, thmg in cat.items():
            thmgChanged = False
            missingTgs = []
            for tg_id, tg in thmg.items():
                prefix, id = tg_id.split('_')
                if prefix == 'ref':
                    otherTaggroup = '%s_%s' % ('new', id)
                else:
                    otherTaggroup = '%s_%s' % ('ref', id)
                if otherTaggroup not in thmg:
                    missingTgs.append((otherTaggroup, tg))
                if isinstance(tg, dict):
                    changed = False
                    if otherTaggroup not in thmg:
                        # Taggroup did not exist previously
                        changed = True
                    else:
                        # Check contents of taggroup to see if it changed
                        d = DictDiffer(tg, thmg[otherTaggroup])
                        diff = d.added().union(d.removed()).union(d.changed())
                        if 'reviewable' in diff:
                            diff.remove('reviewable')
                        if 'change' in diff:
                            diff.remove('change')
                        if 'geometry' in diff:
                            geomChanged = True
                            diff.remove('geometry')
                        if len(diff) > 0:
                            changed = True
                    if changed is True:
                        tg['change'] = 'change'
                        # Changes in the map "taggroup" should not mark the
                        # whole thematic group as changed.
                        if id != 'map':
                            thmgChanged = True
                elif isinstance(tg, list):
                    if otherTaggroup not in thmg:
                        for t in tg:
                            t['change'] = 'change'
                            thmgChanged = True
                    else:
                        for t in tg:
                            changed = True
                            for ot in thmg[otherTaggroup]:
                                d = DictDiffer(t, ot)
                                diff = d.added().union(d.removed()).union(
                                    d.changed())
                                if 'reviewable' in diff:
                                    diff.remove('reviewable')
                                if 'change' in diff:
                                    diff.remove('change')
                                if 'geometry' in diff:
                                    geomChanged = True
                                    diff.remove('geometry')
                                if len(diff) == 0:
                                    changed = False
                            if changed is True:
                                t['change'] = 'change'
                                thmgChanged = True
            for missingTaggroup, oldTg in missingTgs:
                prefix, id = missingTaggroup.split('_')
                if isinstance(oldTg, dict):
                    thmg[missingTaggroup] = {'change': 'change'}
                elif isinstance(oldTg, list):
                    thmg[missingTaggroup] = [{'change': 'change'}]
                if id == 'map' or 'geometry' in oldTg:
                    geomChanged = True
            if thmgChanged is True:
                thmg['change'] = 'change'
                catChanged = True
        if catChanged is True:
            cat['change'] = 'change'

    if ref == {}:
        # Special case: If there is no previous version, it is assumed that the
        # geometry has changed in any case.
        geomChanged = True

    merged['geomchange'] = 'change' if geomChanged is True else ''

    log.debug('Merged formdata: %s' % merged)

    return merged


class DictDiffer(object):
    """
    Thanks to http://stackoverflow.com/a/1165552/841644
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(
            past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)

    def added(self):
        return self.set_current - self.intersect

    def removed(self):
        return self.set_past - self.intersect

    def changed(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] == self.current_dict[o])


def get_main_keys_from_item_json(item_json):
    """
    Returns the keys of all main tags found in the complete json (a
    Python dict) of an Activity or a Stakeholder as created by the
    Protocol.

    Args:
        item_json (dict): The complete json of an Activity or a
            Stakeholder as created by the Protocol.

    Returns:
        list. A list with all main keys of the item json.
    """
    main_keys = []
    if not isinstance(item_json, dict):
        return main_keys
    for taggroup in item_json.get('taggroups', []):
        main_key = taggroup.get('main_tag', {}).get('key', None)
        if main_key:
            main_keys.append(main_key)
    return main_keys


def get_value_by_key_from_taggroup_json(taggroup_json, key):
    if not isinstance(taggroup_json, dict):
        return None
    found_tag = next((
        tag for tag in taggroup_json.get('tags', []) if tag['key'] == key),
        None)
    if found_tag:
        return found_tag['value']
    return None


def get_value_by_key_from_item_json(item_json, key):
    """
    Returns the value of a tag found by its key in the complete json
    (a Python dict) of an Activity or a Stakeholder as created by the
    Protocol.

    .. important::

       This function only returns the value of the first occurence of
       the key. However, there may be further Taggroups containing the
       same key.

    Args:
        item_json (dict): The complete json of an Activity or a
            Stakeholder as created by the Protocol.
        key (str): The key to search inside the tags.

    Returns:
        str or None. The value of the tag if found, None if the key was
            not found or if the json is invalid.
    """
    if not isinstance(item_json, dict):
        return None
    for taggroup in item_json.get('taggroups', []):
        found_tag = next((
            tag for tag in taggroup.get('tags', []) if tag['key']
                                                       == key), None)
        if found_tag:
            return found_tag['value']
    return None
