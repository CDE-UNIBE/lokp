import copy

import colander
import datetime
import deform
import os

import yaml
from pyramid.i18n import get_localizer, TranslationStringFactory
from pyramid.renderers import render

from lokp.config.customization import get_customized_template_path, \
    profile_directory_path, local_profile_directory_path
from lokp.models import A_Key, SH_Key, DBSession, Language, A_Value, SH_Value, \
    Stakeholder_Role, Category
from lokp.utils.views import validate_item_type


_ = TranslationStringFactory('lokp')


def getValidKeyTypes():
    """
    Function to return all valid key types that can be set in the config yaml.
    """
    return [
        'dropdown',
        'checkbox',
        'number',
        'integer',
        'text',
        'date',
        'string',
        'file',
        'inputtoken',
        'integerdropdown'
    ]


class ConfigCategoryList(object):
    """
    A class representing a list of Form Category objects as defined in the
    configuration file (csv).
    """

    def __init__(self):
        self.categories = []

    def addCategory(self, category):
        """
        Add a category to the list.
        """
        if (isinstance(category, ConfigCategory)
                and category not in self.categories):
            self.categories.append(category)

    def getCategories(self):
        """
        Return all categories as a list.
        """
        return self.categories

    def findCategoryById(self, id):
        """
        Find and return a category by its id.
        """
        for cat in self.getCategories():
            if str(cat.getId()) == str(id):
                return cat
        return None

    def findThematicgroupById(self, id):
        """
        Find and return a thematic group by its id.
        """
        for cat in self.getCategories():
            for thmg in cat.getThematicgroups():
                if str(thmg.getId()) == str(id):
                    return thmg
        return None

    def getAllTaggroups(self):
        """
        Return them sorted.
        """
        taggroups = []
        for cat in sorted(self.getCategories(), key=lambda c: c.getOrder()):
            for thg in sorted(
                    cat.getThematicgroups(), key=lambda t: t.getOrder()):
                taggroups.extend(sorted(
                    thg.getTaggroups(), key=lambda tg: tg.getOrder()))
        return taggroups

    def getAllTags(self):
        tags = []
        for cat in self.getCategories():
            for thg in cat.getThematicgroups():
                for tg in thg.getTaggroups():
                    for t in tg.getTags():
                        tags.append(t)
        return tags

    def findTagByKeyName(self, name):
        """
        Find and return tag by a given key name.
        """
        for cat in self.getCategories():
            for thg in cat.getThematicgroups():
                for tg in thg.getTaggroups():
                    for t in tg.getTags():
                        if t.getKey().getName() == name:
                            return t
        return None

    def findTagByKey(self, key):
        """
        Find and return tag by a given key object.
        """
        for cat in self.getCategories():
            for thg in cat.getThematicgroups():
                for tg in thg.getTaggroups():
                    for t in tg.getTags():
                        if t.getKey() == key:
                            return t
        return None

    def getAllMainkeyNames(self):
        """
        Return a list with the names of all main keys in all categories.
        """
        mainkeys = []
        for cat in self.getCategories():
            for thg in cat.getThematicgroups():
                for tg in thg.getTaggroups():
                    mainkeys.append(tg.getMaintag().getKey().getName())
        return mainkeys

    def getAllKeys(self):
        """
        Return a list with all keys in all categories
        """
        keys = []
        for cat in sorted(self.getCategories(), key=lambda c: c.getOrder()):
            for thg in sorted(
                    cat.getThematicgroups(), key=lambda t: t.getOrder()):
                for tg in sorted(
                        thg.getTaggroups(), key=lambda tg: tg.getOrder()):
                    for t in sorted(
                            tg.getTags(), key=lambda t: t != tg.getMaintag()):
                        keys.append(t.getKey())
        return keys

    def getAllKeyNames(self):
        """
        Return a list with the names of all keys in all categories.
        """
        keys = []
        for cat in self.getCategories():
            for thg in cat.getThematicgroups():
                for tg in thg.getTaggroups():
                    for t in tg.getTags():
                        keys.append(t.getKey().getName())
        return keys

    def getDesiredKeyNames(self, translated=False, strict=False):
        """
        Return a list with the names (translated or not) of all desired and
        mandatory (!) keys in all categories.
        """
        desiredkeys = []
        for cat in self.getCategories():
            for thg in cat.getThematicgroups():
                for tg in thg.getTaggroups():
                    for t in tg.getTags():
                        if t.getMandatory() is False and strict is True:
                            continue
                        if t.getDesired() is True or t.getMandatory() is True:
                            if translated is True:
                                desiredkeys.append(
                                    t.getKey().getTranslatedName())
                            else:
                                desiredkeys.append(t.getKey().getName())
        return desiredkeys

    def getFilterableKeys(self):
        """
        Return a list with all the keys which are filterable.
        """
        keys = []
        for cat in self.getCategories():
            for thg in cat.getThematicgroups():
                for tg in thg.getTaggroups():
                    for t in tg.getTags():
                        if t.getFilterable() is True:
                            keys.append(t.getKey())
        return keys

    def get_default_search_key(self):
        """
        Return the key which can be searched by default or None.
        """
        for tag in self.getAllTags():
            if tag.get_default_search():
                return tag.getKey()
        return None

    def getFirstCategoryId(self):
        """
        Return the ID of the first category of the list
        """
        categories = sorted(self.getCategories(), key=lambda c: c.getOrder())
        if len(categories) > 0:
            return categories[0].getId()
        return 0

    def getMainkeyWithGeometry(self, withTranslation=True):
        """
        Return a list with the names of all main keys of taggroups which can
        have a geometry
        """
        mainkeys = []
        for cat in self.getCategories():
            for thg in cat.getThematicgroups():
                for tg in thg.getTaggroups():
                    if tg.getGeometry() is True:
                        if withTranslation is True:
                            mainkeys.append([
                                tg.getMaintag().getKey().getTranslatedName(),
                                tg.getMaintag().getKey().getName()
                            ])
                        else:
                            mainkeys.append(tg.getMaintag().getKey().getName())
        return mainkeys

    def findCategoryThematicgroupTaggroupByMainkey(self, mainkey):
        """
        Find and return
        - the id of the Category
        - the id of the Thematic Group
        - the Taggroup object
        based on a mainkey name.
        """
        for c in self.getCategories():
            for thg in c.getThematicgroups():
                for tg in thg.getTaggroups():
                    if tg.getMaintag().getKey().getName() == mainkey:
                        return c.getId(), thg.getId(), tg
        return None, None, None

    def findCategoryByInvolvementName(self, involvementName):
        """
        Find and return the category which contains an involvement with the
        given name
        """
        for c in self.getCategories():
            for thg in c.getThematicgroups():
                if (thg.getInvolvement() is not None
                        and thg.getInvolvement().getName() == involvementName):
                    return c
        return None

    def findThematicgroupByInvolvementName(self, involvementName):
        """
        Find and return the thematic group which contains a given involvement
        data.
        """
        for cat in self.getCategories():
            for thg in cat.getThematicgroups():
                if (thg.getInvolvement() is not None
                        and thg.getInvolvement().getName() == involvementName):
                    return thg
        return None

    def getGroupsByRoleId(self, roleId):
        """
        Find and return
        - Category
        - Thematic Group
        containing an Involvement based on the Involvement's role.
        """
        for cat in self.getCategories():
            for thg in cat.getThematicgroups():
                inv = thg.getInvolvement()
                if inv is None:
                    continue
                if inv.findRoleById(roleId) is not None:
                    return cat, thg
        return None, None

    def getInvolvementCategoryIds(self):
        """
        Find and return the IDs of all categories containing information about
        involvements.
        """
        categories = []
        for cat in self.getCategories():
            for thg in cat.getThematicgroups():
                if thg.getInvolvement() is not None:
                    categories.append(str(cat.getId()))
        return categories

    def getInvolvementThematicgroupIds(self):

        thematicgroups = []
        for cat in self.getCategories():
            for thg in cat.getThematicgroups():
                if thg.getInvolvement() is not None:
                    thematicgroups.append(str(thg.getId()))
        return thematicgroups

    def getMapCategoryIds(self):
        """
        Find and return the IDs of all categories containing some kind of map.
        """
        categories = []
        for cat in self.getCategories():
            for thg in cat.getThematicgroups():
                if thg.getMap() is not None:
                    categories.append(str(cat.getId()))
        return categories

    def getMapThematicgroupIds(self):
        """
        Find and return the IDs of all thematicgroups containing some kind of a
        map.
        """
        thematicgroups = []
        for cat in self.getCategories():
            for thg in cat.getThematicgroups():
                if thg.getMap() is not None:
                    thematicgroups.append(str(thg.getId()))
        return thematicgroups

    def checkValidKeyValue(self, key, value):
        """
        Check if a key and value are valid within the current category list.
        Both need to be valid in order to return True.
        """
        key_is_valid = False
        value_is_valid = False

        if key.startswith('map') and value == {'geometry': colander.null}:
            return True

        for k in self.getAllKeys():
            if key == k.getName():
                # The current key is valid.
                key_is_valid = True
                if k.getType().lower() in [
                    'dropdown', 'checkbox', 'inputtoken']:
                    # If there are predefined values for this key, check if the
                    # value belongs to this key.
                    tag = self.findTagByKey(k)
                    if tag is not None:
                        for v in tag.getValues():
                            if str(value) == v.getName():
                                value_is_valid = True
                else:
                    # If the key has no predefined values, the given value is
                    # assumed to be valid.
                    value_is_valid = True

        # Return only True if key and value are both valid
        return key_is_valid and value_is_valid

    def getInvolvementOverviewKeyNames(self):
        """
        Return the names of the keys of all tags which should appear in the
        involvement overview along with the value for involvementoverview in
        the configuration yaml.
        Returns an array where each entry is an array with
        - name of the key (translated)
        - involvementoverview data (usually an order number)
        """
        keyNames = []
        for cat in self.getCategories():
            for thmg in cat.getThematicgroups():
                for tg in thmg.getTaggroups():
                    for t in tg.getTags():
                        if t.getInvolvementOverview() is not None:
                            keyNames.append([
                                t.getKey().getTranslatedName(),
                                t.getInvolvementOverview()])
        return keyNames

    def getInvolvementOverviewRawKeyNames(self):
        """
        Return the names of the keys of all tags which should appear in the
        involvement overview along with the value for involvementoverview in
        the configuration yaml.
        Returns an array where each entry is an array with
        - name of the key ** NOT translated **
        - involvementoverview data (usually an order number)
        """
        keyNames = []
        for cat in self.getCategories():
            for thmg in cat.getThematicgroups():
                for tg in thmg.getTaggroups():
                    for t in tg.getTags():
                        if t.getInvolvementOverview() is not None:
                            keyNames.append([
                                t.getKey().getName(),
                                t.getInvolvementOverview()])
        return keyNames

    def getGridColumnKeyNames(self):
        """
        Return the names of the keys of all tags which should appear as grid
        column along with the value for gridcolumn in the configuration yaml.
        Returns an array where each entry is an array with
        - original name of the key
        - translated name of the key
        - gridcolumn data (usually an order number)
        """
        keyNames = []
        for cat in self.getCategories():
            for thmg in cat.getThematicgroups():
                for tg in thmg.getTaggroups():
                    for t in tg.getTags():
                        if t.getGridColumn() is not None:
                            keyNames.append([
                                t.getKey().getName(),
                                t.getKey().getTranslatedName(),
                                t.getGridColumn()
                            ])
        return keyNames

    def get_map_detail_keys(self):
        """
        Return a list with the names of the keys which are used for details
        display on the map (marked with "mapdetail: true" in the configuration
        YAML.
        """
        for cat in self.getCategories():
            for thmg in cat.getThematicgroups():
                for tg in thmg.getTaggroups():
                    for t in tg.getTags():
                        if t.map_detail is True:
                            yield t.getKey().getName()

    def getMapSymbolKeyNames(self):
        """
        Return the names of the keys which have a value set for mapSymbol in
        the configuration yaml.
        Returns an array where each entry is an array with
        - name of the key (translated)
        - name of the key (original)
        - mapsymbol data (usually an order number)
        """
        keyNames = []
        for cat in self.getCategories():
            for thmg in cat.getThematicgroups():
                for tg in thmg.getTaggroups():
                    for t in tg.getTags():
                        if t.getMapSymbol() is not None:
                            keyNames.append([
                                t.getKey().getTranslatedName(),
                                t.getKey().getName(), t.getMapSymbol()])
        return keyNames


class ConfigCategory(object):
    """
    A class representing a Form Category object as defined in the configuration
    file (csv). This is the top container of the form structure, for example
    'Spatial Data' or 'General Information' and it contains Form Thematic
    Groups as the next lower form structure.
    """

    def __init__(self, id, name, translation=None):
        self.id = id
        self.name = name
        self.translation = translation
        self.order = 9999
        self.thematicgroups = []

    def getId(self):
        """
        Return the id (as defined in the configuration file) of the category.
        """
        return self.id

    def getName(self):
        """
        Return the name (as defined in the configuration file) of the category.
        """
        return self.name

    def setTranslation(self, translation):
        """
        Set the translation of this category.
        """
        self.translation = translation

    def getTranslation(self, orEmpty=False):
        """
        Return the translation of this category.
        """
        if self.translation is not None:
            return self.translation
        elif orEmpty is True:
            return ''
        else:
            return self.name

    def addThematicgroup(self, thematicgroup):
        """
        Add a thematic group to this category.
        """
        if (isinstance(thematicgroup, ConfigThematicgroup)
                and thematicgroup not in self.thematicgroups):
            self.thematicgroups.append(thematicgroup)

    def getThematicgroups(self):
        """
        Return a list of all thematic groups in this category.
        """
        return self.thematicgroups

    def findThematicgroupById(self, id):
        """
        Find and return a thematic group based on its id.
        """
        for thmg in self.getThematicgroups():
            if str(thmg.getId()) == str(id):
                return thmg
        return None

    def setOrder(self, order):
        """
        Set the order of this category.
        """
        self.order = order

    def getOrder(self):
        """
        Return the order of this category.
        """
        return self.order

    def getForm(self, request, readonly=False, compare=''):
        """
        Prepare the form node for this category, append the forms of its
        thematic groups and return it.
        If the form is to be rendered for comparison, a hidden field 'change'
        is added.
        """
        title = (self.getTranslation() if self.getTranslation() is not None
        else self.getName())
        cat_form = colander.SchemaNode(
            colander.Mapping(),
            widget=deform.widget.MappingWidget(
                item_template='mapping/mapping_thematicgroup'
            ),
            name=str(self.getId()),
            title=title
        )
        if compare is not '':
            cat_form.add(colander.SchemaNode(
                colander.String(),
                name='change',
                title='',
                default=colander.null,
                widget=deform.widget.HiddenWidget()
            ))
        # iterates over all thematic groups, creates a form for them and adds it to cat_form
        for thg in sorted(
                self.getThematicgroups(), key=lambda thmg: thmg.getOrder()):
            # Get the Form for each Thematicgroup
            thg_form = thg.getForm(request, readonly=readonly, compare=compare)
            thg_form.missing = colander.null
            thg_form.name = str(thg.getId())
            cat_form.add(thg_form)
        return cat_form


class ConfigThematicgroup(object):
    """
    A class representing a Form Thematic Group object as defined in the
    configuration file (csv). This is second top container of the form
    structure, for example 'Intention of Investment' in the Category 'General
    Information'. It contains Form Taggroups as the next lower form structure.
    """

    def __init__(self, id, name, translation=None):
        self.id = id
        self.name = name
        self.translation = translation
        self.order = 9999
        self.taggroups = []
        self.involvement = None
        self.map = None
        self.showInDetails = False

    def getId(self):
        """
        Return the id (as defined in the configuration file) of the thematic
        group.
        """
        return self.id

    def addTaggroup(self, taggroup):
        """
        Add a taggroup to this thematic group.
        """
        if (isinstance(taggroup, ConfigTaggroup)
                and taggroup not in self.taggroups):
            self.taggroups.append(taggroup)

    def getTaggroups(self):
        """
        Return a list of all taggroups in this thematic group.
        """
        return self.taggroups

    def findTaggroupById(self, id):
        """
        Find and return a taggroup based on its id.
        """
        for tg in self.getTaggroups():
            if str(tg.getId()) == str(id):
                return tg
        return None

    def getName(self):
        """
        Return the name (as defined in the configuration file) of the thematic
        group.
        """
        return self.name

    def getTranslation(self, orEmpty=False):
        """
        Return the translation of this category.
        """
        if self.translation is not None and self.translation != '':
            return self.translation
        elif orEmpty is True:
            return ''
        else:
            return self.name

    def setTranslation(self, translation):
        """
        Set the translation of this category.
        """
        self.translation = translation

    def setOrder(self, order):
        """
        Set the order of this thematic group.
        """
        self.order = order

    def getOrder(self):
        """
        Return the order of this thematic group.
        """
        return self.order

    def setInvolvement(self, involvement):
        """
        Set the involvement of this thematic group.
        """
        if isinstance(involvement, ConfigInvolvement):
            self.involvement = involvement

    def getInvolvement(self):
        """
        Return the involvement of this thematic group.
        """
        return self.involvement

    def setMap(self, map):
        """
        Set the map of this thematic group.
        """
        if isinstance(map, ConfigMap):
            self.map = map

    def getMap(self):
        """
        Return the map of this thematic group.
        """
        return self.map

    def setShowInDetails(self, bool):
        """
        Set the boolean if this thematic group is to be shown in details.
        """
        self.showInDetails = bool

    def getShowInDetails(self):
        """
        Return the boolean if this thematic group is to be shown in details.
        """
        return self.showInDetails

    def getForm(self, request, readonly=False, compare=''):
        """
        Prepare the form node for this thematic group, append the forms of its
        taggroups and return it.
        If the form is to be rendered for comparison, a hidden field 'change'
        is added and each taggroup is added twice (once as 'ref_[ID]' and once
        as 'new_[ID]'.

        Returns thg_form (colander SchemaNode)
        """
        title = (self.getTranslation() if self.getTranslation() is not None # self: thematic group (like location)
        else self.getName())
        # For the details (readonly=True), add the title of the thematic group
        # only if specified in the configuration.
        if readonly is True and self.getShowInDetails() is False:
            title = ''

        # initialises an empty form node for this thematic group
        thg_form = colander.SchemaNode(
            colander.Mapping(),
            widget=deform.widget.MappingWidget(
                item_template='mapping/mapping_taggroup'
            ),
            title=title
        )

        if compare is not '':
            thg_form.add(colander.SchemaNode(
                colander.String(),
                name='change',
                title='',
                default=colander.null,
                widget=deform.widget.HiddenWidget()
            ))


        # get map widget
        if self.getMap() is not None:
            # If there is some map data in this thematic group, get the widget
            # and add it to the form.
            mapWidget = getMapWidget(self, geometry_type={'geometry_type': 'point'})
            thg_form.add(mapWidget)

        # Iterates over each taggroup in this thematic group and creates a form (tg_form) for each taggroup
        for tg in sorted(self.getTaggroups(), key=lambda tg: tg.getOrder()):
            # Get the Form for each Taggroup
            tg_form = tg.getForm(request, compare=compare)
            name = str(tg.getId())
            if compare is not '':
                tg_form.add(colander.SchemaNode(
                    colander.String(),
                    name='change',
                    title='',
                    default=colander.null,
                    widget=deform.widget.HiddenWidget()
                ))
                name = 'ref_%s' % str(tg.getId())
            if tg.getRepeatable() is False:
                # Add them as single node or ...
                tg_form.missing = colander.null
                tg_form.name = name
                thg_form.add(tg_form)
            else:
                # ... add them as sequence if the taggroup is repeatable.
                thg_form.add(colander.SchemaNode(
                    colander.Sequence(),
                    tg_form,
                    missing=colander.null,
                    default=[colander.null],
                    widget=deform.widget.SequenceWidget(
                        min_len=1
                    ),
                    name=name,
                    title=''
                ))

            if compare is not '':
                tg_form = tg.getForm(request, compare=compare)
                tg_form.add(colander.SchemaNode(
                    colander.String(),
                    name='change',
                    title='',
                    default=colander.null,
                    widget=deform.widget.HiddenWidget()
                ))
                name = 'new_%s' % str(tg.getId())
                if tg.getRepeatable() is False:
                    # Add them as single node or ...
                    tg_form.missing = colander.null
                    tg_form.name = name
                    thg_form.add(tg_form)
                else:
                    # ... add them as sequence if the taggroup is repeatable.
                    thg_form.add(colander.SchemaNode(
                        colander.Sequence(),
                        tg_form,
                        missing=colander.null,
                        default=[colander.null],
                        widget=deform.widget.SequenceWidget(
                            min_len=1
                        ),
                        name=name,
                        title=''
                    ))

        if self.getInvolvement() is not None:
            # If there is some involvement data in this thematic group, get the
            # corresponding involvement widget and add it to the form.

            # (So far,) Involvements can only be added from the Activity side.
            # Therefore, for Stakeholders (itemType of involvement =
            # activities) add the Involvements widget only if in readonly mode
            if (self.getInvolvement().getItemType() != 'activities'
                    or readonly is True):
                shortForm = getInvolvementWidget(
                    request, self.getInvolvement(), compare=compare)
                if compare is not '':
                    shortForm.name = 'ref_%s' % shortForm.name
                    thg_form.add(shortForm)

                    newShortForm = getInvolvementWidget(
                        request, self.getInvolvement(), compare=compare)
                    newShortForm.name = 'new_%s' % newShortForm.name
                    thg_form.add(newShortForm)
                else:
                    thg_form.add(shortForm)

        return thg_form


class ConfigTaggroupList(object):
    """
    A class representing a list of Form Taggroups.
    """

    def __init__(self):
        self.taggroups = []

    def addTaggroup(self, taggroup):
        """
        Add a taggroup to the list.
        """
        if (isinstance(taggroup, ConfigTaggroup)
                and taggroup not in self.taggroups):
            self.taggroups.append(taggroup)

    def getTaggroups(self):
        """
        Return all taggroups as a list.
        """
        return self.taggroups


class ConfigTaggroup(object):
    """
    A class representing a Form Taggroup object as defined in the configuration
    file (csv). This is third level of the form structure. It is used to group
    tags belonging together and can be used to show this combination of tags
    multiple times. It contains a Form Tag as a Maintag and optionally other
    Form Tags as the next lower form structure..
    """

    def __init__(self, id):
        self.id = id
        self.maintag = None
        self.tags = []
        self.repeatable = False
        self.geometry = False
        self.order = 9999
        self.map = None

    def setMap(self, map):
        """
        Set the map of this thematic group.
        """
        if isinstance(map, ConfigMap):
            self.map = map

    def getMap(self):
        """
        Return the map of this thematic group.
        """
        return self.map

    def getId(self):
        """
        Return the id (as defined in the configuration file) of the taggroup.
        """
        return self.id

    def setMaintag(self, tag):
        """
        Set a tag as the Maintag of this taggroup.
        """
        if isinstance(tag, ConfigTag):
            self.maintag = tag

    def getMaintag(self):
        """
        Return the maintag of this taggroup.
        """
        return self.maintag

    def addTag(self, tag):
        """
        Add a tag to this taggroup.
        """
        if isinstance(tag, ConfigTag) and tag not in self.tags:
            self.tags.append(tag)

    def getTags(self):
        """
        Return a list of all tags in this taggroup.
        """
        return self.tags

    def setRepeatable(self, repeatable):
        """
        Set this taggroup as repeatable or not.
        """
        self.repeatable = repeatable

    def getRepeatable(self):
        """
        Return a boolean whether this taggroup is repeatable or not.
        """
        return self.repeatable is True

    def setGeometry(self, geometry):
        """
        Set if this taggroup can have a geometry or not.
        """
        self.geometry = geometry

    def getGeometry(self):
        """
        Return a boolean whether this taggroup can have a geometry or not.
        """
        return self.geometry is True

    def setOrder(self, order):
        """
        Set the order of this taggroup.
        """
        self.order = order

    def getOrder(self):
        """
        Return the order of this taggroup.
        """
        return self.order

    def hasKey(self, key):
        """
        Try to find a key in this taggroup. Return true if found, false if not.
        """
        for t in self.getTags():
            if t.getKey().getName() == key:
                return True
        return False

    def getForm(self, request, compare=''):
        """
        Prepare the form node for this taggroup, append the forms of its  tags
        and return it.
        """
        tg_form = colander.SchemaNode(
            colander.Mapping(),
            name='tg')
        maintag = self.getMaintag()
        # First add the maintag
        if maintag is not None:
            tg_form.add(maintag.getForm(request))
        # Remove the maintag from the list and get the form of the remaining
        # tags
        if maintag in self.getTags():
            self.getTags().remove(maintag)
        for t in self.getTags():
            # Get the Form for each tag
            tg_form.add(t.getForm(request))
        # Add a hidden field for the tg_id. As when adding the version and
        # identifier, the deform.widget.HiddenWidget() does not seem to work
        # here. Instead, user TextInputWidget with hidden template
        tg_form.add(colander.SchemaNode(
            colander.Int(),
            widget=deform.widget.TextInputWidget(template='hidden'),
            name='tg_id',
            title='',
            missing=colander.null
        ))
        tg_form.validator = self.maintag_validator

        # Only add map widget in normal form view. In compare and review mode,
        # do not add map widget as polygons are shown all on the same map
        # (rendered separately) and adding the map widget only screws up the
        # hierarchy of cstruct data.
        if self.getMap() is not None and compare == '':
            # If there is some map data in this tag group, get the widget
            # and add it to the form.
            mapWidget = getMapWidget(self, {'geometry_type': 'polygon'})
            tg_form.add(mapWidget)

        return tg_form

    def maintag_validator(self, form, value):
        """
        Helper function to validate a taggroup form: If there are some fields
        filled out in a taggroup, the maintag of this taggroup needs to be set
        as well. If not, raise an error indicating that the maintag cannot be
        empty.
        """
        mainkey = self.getMaintag().getKey().getName()
        # If the maintag is empty, ...
        if value[mainkey] in [colander.null, set()]:
            # ... check if one of the other values is set
            hasOtherValuesSet = False
            for (k, v) in value.items():
                if k != mainkey and v != colander.null and k != 'tg_id' and v != {'geometry': colander.null}:  # allow validation when geometry is empty
                    hasOtherValuesSet = True
            if hasOtherValuesSet:
                # TODO: Translation
                exc = colander.Invalid(
                    form, 'The maintag (%s) cannot be empty!' % mainkey)
                raise exc


class ConfigTag(object):
    """
    A class representing a Form Tag object. This is fourth level of the form
    structure. It is used to display a key and a field for its value. It
    contains a key and optional values as the next lower form structures.
    """

    def __init__(self):
        self.key = None
        self.values = []
        self.mandatory = False
        self.desired = False
        self.map_detail = False
        self.involvementOverview = None
        self.gridColumn = None
        self.mapSymbol = None
        self.filterable = False
        self.default_search = False

    def setKey(self, key):
        """
        Set a key for this tag.
        """
        if isinstance(key, ConfigKey):
            self.key = key

    def getKey(self):
        """
        Get the key of this tag.
        """
        return self.key

    def addValue(self, value):
        """
        Add a tag to this tag.
        """
        if isinstance(value, ConfigValue) and value not in self.values:
            self.values.append(value)

    def getValues(self):
        """
        Return a list of all values in this tag.
        """
        return self.values

    def setMandatory(self, mandatory):
        """
        Set this tag as mandatory or not.
        """
        self.mandatory = mandatory

    def getMandatory(self):
        """
        Return a boolean whether this tag is mandatory or not.
        """
        return self.mandatory is True

    def setDesired(self, desired):
        """
        Set this tag as desired or not.
        """
        self.desired = desired

    def getDesired(self):
        """
        Return a boolean whether this tag is desired or not.
        """
        return self.desired is True

    def setInvolvementOverview(self, overview):
        """
        Set the value for involvement overview.
        """
        self.involvementOverview = overview

    def getInvolvementOverview(self):
        """
        Return the value set in involvement overview.
        """
        return self.involvementOverview

    def setGridColumn(self, column):
        """
        Set the value for the grid column.
        """
        self.gridColumn = column

    def getGridColumn(self):
        """
        Return the value set in grid column.
        """
        return self.gridColumn

    def get_default_search(self):
        return self.default_search is True

    def set_default_search(self, default_search):
        self.default_search = default_search

    def setMapSymbol(self, symbol):
        """
        Set the value for map symbol.
        """
        self.mapSymbol = symbol

    def getMapSymbol(self):
        """
        Return the value set in map symbole.
        """
        return self.mapSymbol

    def setFilterable(self, filterable):
        """
        Set if this tag should be used in the filters or not.
        """
        self.filterable = filterable

    def getFilterable(self):
        """
        Return a boolean whether this tag should be used in the filters or not.
        """
        return self.filterable is True

    def findValueByName(self, name):
        """
        Find and return a value object in the list of this tag's values by its
        name.
        """
        for v in self.getValues():
            if v.getName() == name:
                return v
        return None

    def getForm(self, request):
        """
        Prepare the form node for this tag, append the nodes of its keys
        (depending on its type) and return it.
        """
        key = self.getKey()
        # Get name and type of key
        name = key.getName()
        title = (key.getTranslatedName() if key.getTranslatedName() is not None
        else key.getName())
        type = key.getType()
        helptext = (key.getTranslatedHelptext() if key.getTranslatedHelptext()
                                                   is not None else key.getHelptext())
        desired = self.getDesired()
        # Decide which type of form to add
        if ((type.lower() == 'dropdown' and len(self.getValues()) > 0)
                or type.lower() == 'integerdropdown'):
            # Dropdown
            # Prepare the choices for keys with predefined values
            choiceslist = [('', '- ' + _('Select') + ' -')]
            if type.lower() == 'dropdown':
                for v in sorted(
                        self.getValues(), key=lambda val: val.getOrderValue()):
                    choiceslist.append((v.getName(), v.getTranslation()))
            else:
                # Integer dropdown
                dropdownRange = self.getKey().getValidator()
                if isinstance(dropdownRange, list) and len(dropdownRange) == 2:
                    try:
                        dropdownRangeInt = [int(d) for d in dropdownRange]
                    except ValueError:
                        dropdownRangeInt = None
                    if dropdownRangeInt is not None:
                        for v in range(
                                dropdownRangeInt[0], dropdownRangeInt[1] + 1):
                            choiceslist.append((v, v))
            choices = tuple(choiceslist)
            form = colander.SchemaNode(
                colander.String(),
                validator=colander.OneOf([x[0] for x in choices]),
                widget=CustomSelectWidget(
                    values=choices,
                    helptext=helptext,
                    desired=desired
                ),
                name=name,
                title=title
            )
        elif type.lower() in ['checkbox', 'inputtoken'] and len(
                self.getValues()) > 0:
            # Checkbox or Input Token
            # Prepare the choices for keys with predefined values
            choices = []
            for v in sorted(
                    self.getValues(), key=lambda val: val.getOrderValue()):
                choices.append((v.getName(), v.getTranslation()))
            if type.lower() == 'checkbox':
                # Checkbox
                widget = CustomCheckboxWidget(
                    values=tuple(choices),
                    helptext=helptext,
                    desired=desired
                )
            else:
                # Input Token
                deform.widget.default_resource_registry.set_js_resources(
                    'inputtoken', None, '../static/v2/form_inputtoken.js'
                )
                deform.widget.default_resource_registry.set_css_resources(
                    'inputtoken', None, '../static/v2/form_inputtoken.css'
                )
                widget = CustomInputTokenWidget(
                    values=tuple(choices),
                    helptext=helptext,
                    desired=desired
                )
            form = colander.SchemaNode(
                colander.Set(),
                widget=widget,
                name=name,
                title=title
            )
        elif type.lower() == 'number' or type.lower() == 'integer':
            # Number or Integer field
            min = None
            max = None
            val = self.getKey().getValidator()
            if isinstance(val, list):
                try:
                    min = val[0]
                    max = val[1]
                except IndexError:
                    pass
            options = {}
            if min is not None:
                options['min'] = min
            if max is not None:
                options['max'] = max
            if type.lower() == 'number':
                # Specific options for 'number'
                options['step'] = 0.01
                options['numberFormat'] = 'n'
                colanderType = colander.Float()
            else:
                # Specific options for 'integer'
                colanderType = colander.Int()
            form = colander.SchemaNode(
                colanderType,
                widget=CustomTextInputWidget(
                    helptext=helptext,
                    desired=desired
                ),
                name=name,
                title=title
            )
        elif type.lower() == 'text':
            # Textarea
            form = colander.SchemaNode(
                colander.String(),
                widget=CustomTextAreaWidget(
                    rows=5,
                    cols=60,
                    style='float:left;',
                    helptext=helptext,
                    desired=desired
                ),
                name=name,
                title=title
            )
        elif type.lower() == 'date':
            # Date
            form = colander.SchemaNode(
                colander.Date(),
                widget=CustomDateInputWidget(
                    helptext=helptext,
                    desired=desired
                ),
                validator=colander.Range(
                    min=datetime.date(1900, 1, 1)
                ),
                name=name,
                title=title
            )
        elif type.lower() == 'file':
            # File
            form = colander.SchemaNode(
                colander.String(),
                widget=deform.widget.TextInputWidget(
                    template='customFileDisplay',
                    readonly_template='readonly/customFileDisplay'
                ),
                name=name,
                title=title
            )
        else:
            # Default: Textfield
            form = colander.SchemaNode(
                colander.String(),
                widget=CustomTextInputWidget(
                    size=50,
                    helptext=helptext,
                    desired=desired
                ),
                name=name,
                title=title
            )
        # Is this tag mandatory?
        if self.getMandatory() is False:
            form.missing = colander.null
        # Add a validator for this key if there is one
        if self.getKey().getValidator() is not None:
            val = self.getKey().getValidator()
            if isinstance(val, list):
                form.validator = colander.Range(*val)
        return form


class ConfigKeyList(object):
    """
    A class representing a list of Form Tags.
    """

    def __init__(self):
        self.keys = []

    def addKey(self, key):
        """
        Add a key to the list.
        """
        if isinstance(key, ConfigKey) \
                and self.findKeyById(key.getId()) is None:
            self.keys.append(key)

    def getKeys(self):
        """
        Return all keys as a list.
        """
        return self.keys

    def findKeyById(self, id):
        """
        Find and return a key by its id.
        """
        # TODO: Try to speed up (?) by looking directly using the index
        for k in self.getKeys():
            if str(k.getId()) == str(id):
                return k
        return None


class ConfigKey(object):
    """
    A class representing a Form Key object as defined in the configuration
    file (csv). This is the lowest structure of the form.
    """

    def __init__(
            self, id, name, type, helptext, description, validator, t_key,
            t_helptext, t_description):
        self.id = id
        self.name = name
        self.type = type
        self.helptext = helptext
        # The description (and its translation) are stored but not really used
        # so far.
        self.description = description
        self.validator = validator
        self.translated_name = t_key
        self.translated_helptext = t_helptext
        self.translated_description = t_description

    def getId(self):
        """
        Return the id (as defined in the configuration file) of the key.
        """
        return self.id

    def getName(self):
        """
        Return the name (as defined in the configuration file) of the category.
        """
        return self.name

    def setTranslation(self, name, helptext):
        """
        Set the translation of this key.
        """
        self.translated_name = name
        self.translated_helptext = helptext

    def getTranslatedName(self, orEmpty=False):
        """
        Return the translated name of this key if there is a translation set,
        else return the name.
        """
        if self.translated_name is not None:
            return self.translated_name
        elif orEmpty is True:
            return ''
        else:
            return self.name

    def getTranslatedHelptext(self, orEmpty=False):
        """
        Return the translated helptext of this key
        """
        if self.translated_helptext is not None:
            return self.translated_helptext
        elif orEmpty is True:
            return ''
        else:
            return self.getHelptext()

    def getType(self):
        """
        Return the type of this key.
        """
        return self.type

    def getHelptext(self):
        """
        Return the helptext for this tag
        """
        if self.helptext is None:
            return ''
        return self.helptext

    def setValidator(self, validator):
        """
        Set a validator for this key.
        """
        self.validator = validator

    def getValidator(self):
        """
        Return the validator of this key. So far, only ranges as arrays are
        valid.
        """
        if self.validator is None:
            # If there is no validator, do not try to parse it or anything.
            return None
        if isinstance(self.validator, list):
            # If it is already a list, return it as it is
            return self.validator
        # Try to parse the string to a list
        if self.validator[:1] == '[' and self.validator[-1:] == ']':
            arr = self.validator[1:-1].split(',')
            for i, a in enumerate(arr):
                try:
                    if self.getType().lower() == 'integer':
                        arr[i] = int(a)
                    elif self.getType().lower() == 'number':
                        arr[i] = float(a)
                except ValueError:
                    pass
            if len(arr) > 0 and len(arr) <= 2:
                return arr
        return None


class ConfigValueList(object):
    """
    A class representing a list of Form Values.
    """

    def __init__(self):
        self.values = []

    def addValue(self, value):
        """
        Add a value to the list.
        """
        if (isinstance(value, ConfigValue)
                and self.findValueById(value.getId()) is None):
            self.values.append(value)

    def getValues(self):
        """
        Return all values as a list.
        """
        return self.values

    def findValueById(self, id):
        """
        Find and return a value by its id.
        """
        # TODO: Try to speed up (?) by looking directly using the index
        for v in self.getValues():
            if v.getId() == str(id):
                return v
        return None

    def findValuesByFkkey(self, fk_key):
        """
        Find and return a list of values by a fk_key.
        """
        values = []
        for v in self.getValues():
            if str(v.getFkkey()) == str(fk_key):
                values.append(v)
        return values


class ConfigValue(object):
    """
    A class representing a Form Key object as defined in the configuration
    file (csv). This is the lowest structure of the form.
    """

    def __init__(self, id, name, fk_key, order, translation):
        self.id = id
        self.name = name
        self.translation = translation
        self.fk_key = fk_key
        self.order = order

    def getId(self):
        """
        Return the id (as defined in the configuration file) of the value.
        """
        return self.id

    def getName(self):
        """
        Return the name (as defined in the configuration file) of the value.
        """
        return self.name

    def setTranslation(self, translation):
        """
        Set the translation of this value.
        """
        self.translation = translation

    def getTranslation(self, orEmpty=False):
        """
        Return the translation of this value.
        """
        if self.translation is not None:
            return self.translation
        elif orEmpty is True:
            return ''
        else:
            return self.name

    def getFkkey(self):
        """
        Return the fk_key (as defined in the configuration file) of the value.
        """
        return self.fk_key

    def getOrder(self):
        """
        Return the order of this value.
        """
        return self.order

    def getOrderValue(self):
        """
        Returns the order value if one is set else the name of the value (use
        the translation)
        """
        if self.getOrder() != '' and self.getOrder() is not None:
            return self.getOrder()
        return self.getTranslation()


class ConfigInvolvementRoleList(object):
    """
    A class representing a list of Involvement Roles.
    """

    def __init__(self):
        self.roles = []

    def addRole(self, role):
        """
        Add a new Involvement Role to the list. Add each only once.
        """
        if (isinstance(role, ConfigInvolvementRole)
                and self.findRoleById(role.getId()) is None):
            self.roles.append(role)

    def getRoles(self):
        """
        Get all the Involvement Roles.
        """
        return self.roles

    def findRoleById(self, id):
        """
        Find and return a role by its id.
        """
        for r in self.getRoles():
            if str(r.getId()) == str(id):
                return r
        return None


class ConfigInvolvementRole(object):
    """
    A class representing an Involvement Role object as defined in the database.
    It corresponds to the database table "Stakeholder_Role".
    """

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def getId(self):
        """
        Return the ID of the Involvement Role
        """
        return self.id

    def getName(self):
        """
        Return the name of the Involvement Role
        """
        return self.name


class ConfigMap(object):
    """
    A class representing the configuration of the map.
    """

    def __init__(self, name):
        self.name = name
        self.mode = 'singlepoint'

    def getName(self):
        """
        Returns the name of the map
        """
        return self.name

    def setMode(self, mode):
        """
        Set the mode of the map
        """
        if mode in [
            'singlepoint',
            'multipoints'
        ]:
            self.mode = mode

    def getMode(self):
        """
        Returns the mode of the map
        """
        return self.mode


class ConfigInvolvement(object):
    """
    A class representing the configuration of an Involvement.
    """

    def __init__(self, name, itemType):
        self.name = name
        self.itemType = itemType
        self.roles = []
        self.repeatable = False

    def getName(self):
        """
        Returns the name of the Involvement
        """
        return self.name

    def getItemType(self):
        """
        Returns the ItemType (activities/stakeholders) of this Involvement
        """
        return self.itemType

    def addRole(self, role):
        """
        Add a new Involvement Role
        """
        if (isinstance(role, ConfigInvolvementRole)
                and self.findRoleById(role.getId()) is None):
            self.roles.append(role)

    def findRoleById(self, id):
        """
        Find and return an Involvement Role by its id.
        """
        for r in self.getRoles():
            if str(r.getId()) == str(id):
                return r
        return None

    def getRoles(self):
        """
        Return all the Involvement Roles
        """
        return self.roles

    def setRepeatable(self, repeatable):
        """
        Set the Involvement to repeatable or not
        """
        self.repeatable = repeatable is True

    def getRepeatable(self):
        """
        Return a boolean if the Involvement is repeatable or not
        """
        return self.repeatable is True


def getConfigKeyList(request, itemType, **kwargs):
    """
    Function to collect and return all the keys from the database. It returns a
    list of all keys found in the original language along with the translation
    in the language requested. This list will be filtered later to match the
    configuration in the (local) YAML.
    itemType: activities / stakeholders
    """

    lang = kwargs.get('lang', None)

    if itemType == 'activities':
        MappedClass = A_Key
    elif itemType == 'stakeholders':
        MappedClass = SH_Key

    configKeys = ConfigKeyList()

    # Query the config keys from database
    localizer = get_localizer(request)
    if lang is None:
        lang = localizer.locale_name
    translationQuery = DBSession.query(
        MappedClass.fk_key.label('original_id'),
        MappedClass.key.label('t_key'),
        MappedClass.helptext.label('t_helptext'),
        MappedClass.description.label('t_description')
    ). \
        join(Language). \
        filter(Language.locale == lang). \
        subquery()
    keys = DBSession.query(
        MappedClass.id,
        MappedClass.key,
        MappedClass.type,
        MappedClass.helptext,
        MappedClass.description,
        MappedClass.validator,
        translationQuery.c.t_key,
        translationQuery.c.t_helptext,
        translationQuery.c.t_description
    ). \
        filter(MappedClass.fk_language == None). \
        outerjoin(
        translationQuery,
        translationQuery.c.original_id == MappedClass.id)
    for k in keys.all():
        configKeys.addKey(ConfigKey(
            k.id, k.key, k.type, k.helptext, k.description, k.validator,
            k.t_key, k.t_helptext, k.t_description))

    return configKeys


def getConfigValueList(request, itemType, **kwargs):
    """
    Function to collect and return all the keys from the database. It returns a
    list of all keys found in the original language with some fk_key value (in
    order not to return all the values entered by users) along with the
    translation in the language requested. This list will be filtered later to
    match the configuration in the (local) YAML.
    itemType: activities / stakeholders
    """

    lang = kwargs.get('lang', None)

    if itemType == 'activities':
        MappedClass = A_Value
    elif itemType == 'stakeholders':
        MappedClass = SH_Value

    configValues = ConfigValueList()

    # Query the config values from database
    localizer = get_localizer(request)
    if lang is None:
        lang = localizer.locale_name
    translationQuery = DBSession.query(
        MappedClass.fk_value.label('original_id'),
        MappedClass.value.label('t_value')
    ). \
        join(Language). \
        filter(Language.locale == lang). \
        subquery()
    values = DBSession.query(
        MappedClass.id,
        MappedClass.value,
        MappedClass.fk_key,
        MappedClass.order,
        translationQuery.c.t_value
    ). \
        filter(MappedClass.fk_language == 1). \
        filter(MappedClass.fk_key != None). \
        outerjoin(
        translationQuery, translationQuery.c.original_id == MappedClass.id)
    for v in values.all():
        configValues.addValue(ConfigValue(
            v.id, v.value, v.fk_key, v.order, v.t_value))

    return configValues


def getConfigInvolvementRoleList(request, **kwargs):
    """
    Function to collect and return all the involvement roles from the database.
    """
    # TODO: Translation

    configRoles = ConfigInvolvementRoleList()

    # Query the config values from database
    roles = DBSession.query(
        Stakeholder_Role.id,
        Stakeholder_Role.name
    )
    for r in roles.all():
        configRoles.addRole(ConfigInvolvementRole(r.id, r.name))

    return configRoles


def getConfigCategoryList(request, itemType, **kwargs):
    """
    Function to collect and return all the categories from the database. It
    returns a list of all categories found in the original language along with
    the translation in the language requested. This list will be filtered later
    to match the configuration in the (local) YAML.
    - itemType: activities / stakeholders
    """

    lang = kwargs.get('lang', None)

    configCategories = ConfigCategoryList()

    # Query the config categories from database
    localizer = get_localizer(request)
    if lang is None:
        lang = localizer.locale_name
    translationQuery = DBSession.query(
        Category.fk_category.label('original_id'),
        Category.name.label('translation')
    ). \
        join(Language). \
        filter(Language.locale == lang). \
        subquery()
    categories = DBSession.query(
        Category.id,
        Category.name,
        translationQuery.c.translation
    ). \
        filter(Category.type == itemType). \
        filter(Category.fk_language == 1). \
        outerjoin(
        translationQuery, translationQuery.c.original_id == Category.id)
    for cat in categories.all():
        configCategories.addCategory(ConfigCategory(
            cat.id, cat.name, cat.translation))

    return configCategories


def getCategoryList(request, itemType, **kwargs):
    """
    Function to scan through the configuration yaml and put together the list
    of categories which can be used to create the form.
    itemType: activities / stakeholders
    """
    if itemType not in ['activities', 'stakeholders']:
        itemType = validate_item_type(itemType)
        itemType = 'activities' if itemType == 'a' else 'stakeholders'
    # Scan the configuration files for keys, values and categories
    configKeys = getConfigKeyList(request, itemType, **kwargs)
    configValues = getConfigValueList(request, itemType, **kwargs)
    configCategories = getConfigCategoryList(request, itemType, **kwargs)
    configInvolvementRoles = getConfigInvolvementRoleList(request, **kwargs)

    # Do some first test on the keys: Check that each type is defined correctly
    unknowntypes = []
    knowntypes = getValidKeyTypes()
    for k in configKeys.getKeys():
        if k.getType().lower() not in knowntypes:
            unknowntypes.append(k.getName())

    if len(unknowntypes) > 0:
        raise NameError(
            'One or more keys have unknown types: %s' % ', '.join(
                unknowntypes))

    # Load the yaml
    if itemType == 'stakeholders':
        NEW_STAKEHOLDER_YAML = 'new_stakeholder.yml'
        filename = NEW_STAKEHOLDER_YAML
        otherItemType = 'activities'
    else:
        NEW_ACTIVITY_YAML = 'new_activity.yml'
        filename = NEW_ACTIVITY_YAML
        otherItemType = 'stakeholders'

    yaml_stream = open(
        os.path.join(profile_directory_path(request), filename), 'r')
    yaml_config = yaml.load(yaml_stream)

    categorylist = ConfigCategoryList()
    emptymaintag = []
    unknownkeys = []

    # Loop the categories of the yaml config file
    for (cat_id, thmgrps) in yaml_config['fields'].items():

        # Find the category in the list of csv categories
        category = configCategories.findCategoryById(cat_id)

        if category is None:
            # If category is not found, move on
            continue

        # Loop the thematic groups of the category
        for (thmgrp_id, taggroups) in thmgrps.items():

            if thmgrp_id == 'order':
                category.setOrder(taggroups)
                continue

            # The name of the thematic group also stands in the categories csv.
            # So it is necessary to find the category there
            thematicCategory = configCategories.findCategoryById(thmgrp_id)

            if thematicCategory is None:
                # If thematic group is not found, move on
                continue

            # Create a thematicgroup out of it
            thematicgroup = ConfigThematicgroup(
                thematicCategory.getId(),
                thematicCategory.getName(),
                thematicCategory.getTranslation(True)
            )

            # Loop the taggroups of the thematic group
            # whose ids can be order/map defined in .yml
            for (tgroup_id, tags) in taggroups.items():

                if tgroup_id == 'order':
                    thematicgroup.setOrder(tags)  # ??
                    continue

                if tgroup_id == 'showindetails':
                    thematicgroup.setShowInDetails(tags)
                    continue

                if tgroup_id == 'involvement':
                    # Involvement configuration
                    if 'name' in tags:
                        inv = ConfigInvolvement(tags['name'], otherItemType)
                    else:
                        continue

                    if 'roles' in tags and len(tags['roles']) > 0:
                        for r in tags['roles']:
                            inv.addRole(configInvolvementRoles.findRoleById(r))

                    if 'repeat' in tags and tags['repeat'] is True:
                        inv.setRepeatable(True)

                    thematicgroup.setInvolvement(inv)
                    continue

                if tgroup_id == 'map':
                    # Map configuration
                    if 'name' in tags:
                        map = ConfigMap(tags['name'])

                    if 'mode' in tags:
                        map.setMode(tags['mode'])

                    thematicgroup.setMap(map)
                    continue

                # Create a taggroup out of it (only if all above conditions are false)
                taggroup = ConfigTaggroup(tgroup_id)

                # Loop the keys of the taggroup
                for (key_id, key_config) in tags.items():

                    try:
                        int(key_id)

                        # Definition of tag and its values
                        tag = ConfigTag()

                        configKey = configKeys.findKeyById(key_id)
                        if configKey is None:
                            # Error handling if key is not found
                            unknownkeys.append(str(key_id))
                            continue

                        # We need to make a copy of the original object.
                        # Otherwise we are not able to add a custom validator
                        # only for one key.
                        tag.setKey(copy.copy(configKey))

                        if key_config is not None:

                            if 'values' in key_config:
                                # If there are values available in the YAML,
                                # then use these. Else use the ones defined in
                                # the values config csv.
                                for v in key_config['values']:
                                    tag.addValue(configValues.findValueById(v))

                            if ('mandatory' in key_config
                                    and key_config['mandatory'] is True):
                                tag.setMandatory(True)

                            if ('desired' in key_config
                                    and key_config['desired'] is True):
                                tag.setDesired(True)

                            if 'validator' in key_config:
                                tag.getKey(). \
                                    setValidator(key_config['validator'])

                            if 'maintag' in key_config:
                                taggroup.setMaintag(tag)

                            if 'involvementoverview' in key_config:
                                tag.setInvolvementOverview(
                                    key_config['involvementoverview'])

                            if 'gridcolumn' in key_config:
                                tag.setGridColumn(key_config['gridcolumn'])

                            if 'mapdetail' in key_config:
                                tag.map_detail = True

                            if 'mapsymbol' in key_config:
                                tag.setMapSymbol(key_config['mapsymbol'])

                            if ('filterable' in key_config
                                    and key_config['filterable'] is True):
                                tag.setFilterable(True)

                            if ('default_search' in key_config
                                    and key_config['default_search'] is True):
                                tag.set_default_search(True)

                        # If the values are predefined and they are not set
                        # already (defined explicitly in YAML), then get the
                        # values from the value config csv.
                        if configKey.getType().lower() in [
                            'dropdown', 'checkbox', 'inputtoken']:
                            for v in configValues. \
                                    findValuesByFkkey(configKey.getId()):
                                tag.addValue(v)

                        taggroup.addTag(tag)

                    except ValueError:
                        # Configuration of taggroup
                        if key_id == 'repeat' and key_config is True:
                            taggroup.setRepeatable(True)

                        if key_id == 'geometry' and key_config is True:
                            taggroup.setGeometry(True)  # defines whether the tag group can have geometry
                            map = ConfigMap('map'+ str(taggroup.getId()))
                            map.setMode('singlepoint')
                            taggroup.setMap(map)

                        if key_id == 'order' and key_config is not None:
                            taggroup.setOrder(key_config)

                if taggroup.getMaintag() is None:
                    emptymaintag.append(taggroup)
                else:
                    thematicgroup.addTaggroup(taggroup)

            category.addThematicgroup(thematicgroup)

        categorylist.addCategory(category)

    # Look for local profiles if there is any local profile set.
    local_yaml_config = None
    if (local_profile_directory_path(request)
            != profile_directory_path(request)):
        try:
            local_yaml_stream = open(
                "%s/%s"
                % (local_profile_directory_path(request), filename), 'r')
            local_yaml_config = yaml.load(local_yaml_stream)
        except IOError:
            pass

    # Apply the configuration of the local yaml. So far, only additional
    # categories, taggroups and keys can be defined in the local yaml. It is
    # not yet possible to remove any categories or keys.
    if local_yaml_config is not None and 'fields' in local_yaml_config:

        # Loop the categories of the local yaml config file
        for (cat_id, thmgrps) in local_yaml_config['fields'].items():
            newCategory = False

            # Try to find the category in the existing configuration
            category = categorylist.findCategoryById(cat_id)

            if category is None:
                # If the category is not in the existing configuration, it
                # needs to be found in the database
                category = configCategories.findCategoryById(cat_id)
                newCategory = True

            if category is None:
                # If category is still not found, skip it
                continue

            # Loop the thematic groups of the local yaml config file
            for (thmgrp_id, taggroups) in thmgrps.items():
                newThematicgroup = False

                # Try to find the thematic group in the existing configuration
                thematicgroup = category.findThematicgroupById(thmgrp_id)

                if thematicgroup is None:
                    # If the thematic group is not in the existing config, it
                    # needs to be found in the database
                    thmg = configCategories.findCategoryById(thmgrp_id)
                    if thmg is not None:
                        # Create a thematicgroupobject out of it
                        thematicgroup = ConfigThematicgroup(
                            thmg.getId(),
                            thmg.getName(),
                            thmg.getTranslation(True)
                        )
                        newThematicgroup = True
                    else:
                        # If the thematic group is still not found, skip it
                        continue

                # Loop the taggroups of the local yaml config file
                for (tgroup_id, tags) in taggroups.items():
                    newTaggroup = False

                    # Try to find the taggroup in the existing configuration
                    taggroup = thematicgroup.findTaggroupById(tgroup_id)

                    if taggroup is None:
                        # If the taggroup is not in the existing config, it
                        # needs to be created
                        taggroup = ConfigTaggroup(tgroup_id)
                        newTaggroup = True

                    # Loop the keys of the taggroup
                    for (key_id, key_config) in tags.items():

                        # Make sure the key exists in the database
                        configKey = configKeys.findKeyById(key_id)
                        if configKey is None:
                            unknownkeys.append(str(key_id))
                            continue

                        # Create the configtag object
                        tag = ConfigTag()
                        tag.setKey(copy.copy(configKey))

                        if key_config is not None:
                            # Additional configuration of the key. Not
                            # everything can be configured in the local yaml

                            if 'maintag' in key_config:
                                taggroup.setMaintag(tag)

                            if 'validator' in key_config:
                                tag.getKey().setValidator(
                                    key_config['validator'])

                            if (configKey.getType().lower() in
                                    ['dropdown', 'checkbox', 'inputtoken']):
                                for v in configValues.findValuesByFkkey(
                                        configKey.getId()):
                                    tag.addValue(v)

                        taggroup.addTag(tag)

                    # If the taggroup did not exist in the global configuration
                    # and it is valid (has a maintag), add it to the thematic
                    # group.
                    if newTaggroup is True:
                        if taggroup.getMaintag() is None:
                            emptymaintag.append(taggroup)
                        else:
                            thematicgroup.addTaggroup(taggroup)

                # If the thematic group did not exist in the global
                # configuration, add it to the category.
                if newThematicgroup is True:
                    category.addThematicgroup(thematicgroup)

            # If the category did not exist in the global configuration, add it
            # to the list of categories.
            if newCategory is True:
                categorylist.addCategory(category)

    # Keys not found
    if len(unknownkeys) > 0:
        raise NameError(
            'One or more keys were not found in the database: %s'
            % ', '.join(unknownkeys))

    # Tags where the maintag is not found
    if len(emptymaintag) > 0:
        # Collect the names of the tags in the taggroup to give nicer feedback
        emptystack = []
        for e in emptymaintag:
            tags = []
            for t in e.getTags():
                tags.append(
                    '%s [%s]' % (t.getKey().getName(), t.getKey().getId()))
            emptystack.append('Taggroup [%s]' % ', '.join(tags))
        raise NameError(
            'One or more Taggroups do not have a maintag: %s'
            % ', '.join(emptystack))

    # Check that each mainkey is unique (is only set once throughout all keys)
    allkeys = categorylist.getAllKeyNames()
    allmainkeys = categorylist.getAllMainkeyNames()
    duplicates = []
    for mainkey in allmainkeys:
        if allkeys.count(mainkey) > 1:
            if mainkey not in duplicates:
                duplicates.append(mainkey)

    if len(duplicates) > 0:
        # TODO: Error handling
        raise NameError('Duplicated mainkey(s): %s' % ', '.join(duplicates))

    return categorylist


def getMapWidget(thematicgroup, geometry_type):
    """
    Return a widget to be used to display the map in the form.
    The map widget (resp. its hidden lon/lat fields) is mandatory, only one
    field is marked as mandatory (lon) in order to prevent double error
    messages if it is missing.
    """
    try:
        label = thematicgroup.getMaintag().getKey().getName()
    except AttributeError:
        label = ''
    mapWidget = colander.SchemaNode(
        colander.Mapping(),
        widget=CustomMapWidget(
            template='customMapMapping',
            geometry_type=geometry_type,
            edit_mode=thematicgroup.getMap().getMode(),
            label=label,
        ),
        name=thematicgroup.getMap().getName(),
        title='map'+ str(thematicgroup.id)    # add unique title for the map widget (title serves as id in customMapMapping)
    )

    # elements added below are children of mapWidget
    mapWidget.add(colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextInputWidget(template='hidden'),
        name='geometry',
        title='geometry',
        missing = colander.null
    ))

    # all methods within the loader .js can be accessed within the widget
    deform.widget.default_resource_registry.set_js_resources(
        'mapwidget', None,
        'lokp:static/lib/leaflet/leaflet.js',
        'lokp:static/lib/leaflet/leaflet.markercluster.js',
        'lokp:static/lib/leaflet/Leaflet.GoogleMutant.js',
        'lokp:static/lib/leaflet/leaflet.draw.js',
        '/app/view/map_variables.js',
        'lokp:static/lib/chroma/chroma.min.js',
        'lokp:static/js/maps/base.js',
        'lokp:static/js/maps/form.js',
        'lokp:static/js/maps/drawPolygonFeature.js',
        'lokp:static/lib/dropzone/dropzone.min.js',
    )
    deform.widget.default_resource_registry.set_css_resources(
        'mapwidget', None,
        'lokp:static/css/leaflet.css',
        'lokp:static/css/leaflet.draw.css',
        'lokp:static/lib/dropzone/dropzone.min.css',
    )
    return mapWidget



def getInvolvementWidget(request, configInvolvement, compare=''):
    """
    Return a widget to be used to display the involvements in the form.
    """
    categoryList = getCategoryList(request, configInvolvement.getItemType())
    overviewKeys = [
        k[0] for k in categoryList.getInvolvementOverviewKeyNames()]

    template = 'customInvolvementMapping'
    if configInvolvement.getItemType() == 'stakeholders':
        readonlyTemplate = 'readonly/customInvolvementMappingStakeholder' # why read only template?
    else:
        readonlyTemplate = 'readonly/customInvolvementMappingActivity'

    deform.widget.default_resource_registry.set_js_resources(
        'involvementwidget', None, 'lokp:static/js/form/involvement.js',
        'lokp:static/lib/jquery-ui/jquery-ui.min.js'
    )

    deform.widget.default_resource_registry.set_css_resources(
        'involvementwidget', None, 'lokp:static/lib/jquery-ui/jquery-ui.min.css')
    invForm = colander.SchemaNode(
        colander.Mapping(),
        widget=CustomInvolvementWidget(
            template=template,
            readonly_template=readonlyTemplate
        ),
        name=configInvolvement.getName(),
        title=''
    )

    # Add all the hidden fields which are required to keep track of the
    # involvements.
    invForm.add(colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextInputWidget(template='hidden'),
        name='role_name',
        title='',
        missing=colander.null
    ))
    invForm.add(colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextInputWidget(template='hidden'),
        name='id',
        title='',
        missing=colander.null
    ))
    invForm.add(colander.SchemaNode(
        colander.Int(),
        widget=deform.widget.TextInputWidget(template='hidden'),
        name='version',
        title='',
        missing=colander.null
    ))

    # Then add the display fields used for showing the involvement overview
    for keyName in overviewKeys:
        invForm.add(colander.SchemaNode(
            colander.String(),
            widget=deform.widget.TextInputWidget(
                template='readonly/customTextinputReadonly'
            ),
            name=keyName,
            title=keyName,
            missing=colander.null
        ))

    choicesList = []
    for v in configInvolvement.getRoles():
        choicesList.append((v.getId(), v.getName()))
    choices = tuple(choicesList)
    shRole = render(
        get_customized_template_path(
            request,
            'parts/items/stakeholder_role.mak'
        ),
        {},
        request
    )
    invForm.add(colander.SchemaNode(
        colander.String(),
        missing=colander.null,
        validator=colander.OneOf([str(c[0]) for c in choices]),
        widget=CustomSelectWidget(
            values=choices
        ),
        name='role_id',
        title=shRole
    ))

    if compare is not '':
        invForm.add(colander.SchemaNode(
            colander.String(),
            name='change',
            title='',
            default=colander.null,
            widget=deform.widget.HiddenWidget()
        ))
        if compare == 'review':
            invForm.add(colander.SchemaNode(
                colander.String(),
                name='reviewable',
                title='',
                default=colander.null,
                widget=deform.widget.HiddenWidget()
            ))

    if configInvolvement.getRepeatable() is False:
        # If no sequence is required, return the node as it is
        return invForm

    else:
        # If a sequence is required, pack the node in a sequence and return it
        return colander.SchemaNode(
            colander.Sequence(),
            invForm,
            widget=deform.widget.SequenceWidget(
                min_len=1,
                add_subitem_text_template='',
            ),
            missing=colander.null,
            default=[colander.null],
            name=configInvolvement.getName(),
            title=''
        )


def custom_get_template_values(self, field, cstruct, kw):
    """
    This is a modification of the function get_template_values() called by
    deform.widget.Widget and its subclasses.
    It appends the keywords 'helptext' and 'desired' to the template values if
    available.
    """
    values = {'cstruct': cstruct, 'field': field}
    values.update(kw)
    values.pop('template', None)
    if 'helptext' in self.__dict__:
        values['helptext'] = self.__dict__['helptext']
    if 'desired' in self.__dict__:
        values['desired'] = self.__dict__['desired']
    return values


class CustomWidget(deform.widget.Widget):
    """
    Overwrite the function get_template_values() with a custom one to add more
    values to the template.
    """
    def get_template_values(self, field, cstruct, kw):
        return custom_get_template_values(self, field, cstruct, kw)


class CustomSelectWidget(deform.widget.SelectWidget):
    """
    Overwrite the function get_template_values() with a custom one to add more
    values to the template.
    """
    def get_template_values(self, field, cstruct, kw):
        return custom_get_template_values(self, field, cstruct, kw)


class CustomCheckboxWidget(CustomWidget):
    """
    Custom Deform widget. Based very much on the default checkbox choice
    widget. It allows to save a tg_id to the value before showing the
    checkboxes and extracts this value again after submission.
    """
    template = 'checkbox'
    readonly_template = 'readonly/checkbox_choice'
    values = ()
    separator = '|'

    def serialize(self, field, cstruct, **kw):
        if cstruct in (colander.null, None):
            cstruct = ()
        readonly = kw.get('readonly', self.readonly)
        values = kw.get('values', self.values)

        template = readonly and self.readonly_template or self.template

        # The data needs to be prepared before showing in the form. Because a
        # checkbox can contain only one real value, the tg_id needs to be
        # stored in the inner (submit) value of the checkbox.
        formdata = []
        for c in cstruct:
            # Transform tuples to list to access them more easily
            valuelist = list(values)
            newname = None
            for i, (name, title) in enumerate(valuelist):
                # If the form is readonly, the title is relevant, for the
                # normal form the name is relevant.
                if readonly and title == c[0] or not readonly and name == c[0]:
                    # Update the (internal) name of the values
                    newname = '%s%s%s' % (c[1], self.separator, name)
                    valuelist[i] = (newname, title)

            # Transform the list back to tuples
            values = tuple(valuelist)
            if newname is not None:
                formdata.append(newname)

        kw['values'] = values
        tmpl_values = self.get_template_values(field, formdata, kw)

        return field.renderer(template, **tmpl_values)

    def deserialize(self, field, pstruct):
        if pstruct is colander.null:
            return colander.null
        if isinstance(pstruct, deform.compat.string_types):
            return (pstruct,)

        # When submitted, additional data provided by the checkbox (old tg_id)
        # needs to be extracted and stored.
        ret = []
        for p in pstruct:
            # Default values (if no tg_id set)
            old_tg_id = None
            n = p

            if self.separator in p:
                # If a tg_id is set, separate it from the name and store it
                separatorposition = p.find(self.separator)
                n = p[separatorposition + 1:]
                old_tg_id = p[:separatorposition]

            for (name, title) in self.values:
                # Look for the name and set the old tg_id if available.
                if name == n:
                    ret.append((n, old_tg_id))

        return tuple(ret)


class CustomTextInputWidget(deform.widget.TextInputWidget):
    """
    Overwrite the function get_template_values() with a custom one to add more
    values to the template.
    """
    def get_template_values(self, field, cstruct, kw):
        return custom_get_template_values(self, field, cstruct, kw)


class CustomInputTokenWidget(CustomWidget):
    """
    Custom Deform widget. Search for an item to add it to the list of selected
    items.
    Can be seen as a replacement of very long checkbox lists and also works a
    lot like checkbox (saving and extracting tg_id)
    """
    template = 'inputtoken'
    readonly_template = 'readonly/inputtoken'
    values = ()
    separator = '|'
    requirements = (('inputtoken', None),)

    def serialize(self, field, cstruct, **kw):
        if cstruct in (colander.null, None):
            cstruct = ()
        readonly = kw.get('readonly', self.readonly)
        values = kw.get('values', self.values)

        template = readonly and self.readonly_template or self.template

        # The data needs to be prepared before showing in the form. Because an
        # Input Token can only contain one real value, the tg_id needs to be
        # stored in the inner (submit) value of the Token.
        formdata = []
        for c in cstruct:
            # Transform tuples to list to access them more easily
            valuelist = list(values)
            newname = None
            for i, (name, title) in enumerate(valuelist):
                # If the form is readonly, the title is relevant. For the
                # normal form, the name is relevant.
                if readonly and title == c[0] or not readonly and name == c[0]:
                    # Update the (internal) name of the values
                    newname = '%s%s%s' % (c[1], self.separator, name)
                    valuelist[i] = (newname, title)

            # Transform the list back to tuples
            values = tuple(valuelist)
            if newname is not None:
                formdata.append(newname)

        kw['values'] = values
        tmpl_values = self.get_template_values(field, formdata, kw)

        return field.renderer(template, **tmpl_values)

    def deserialize(self, field, pstruct):
        if pstruct is colander.null:
            return colander.null
        if isinstance(pstruct, deform.compat.string_types):
            return (pstruct,)

        # When submitted, additional data provided by the token (old tg_id)
        # needs to be extracted and stored.
        ret = []
        for p in pstruct:
            # Default values (if no tg_id set)
            old_tg_id = None
            n = p

            if self.separator in p:
                # If a tg_id is set, separate it from the name and store it
                separatorposition = p.find(self.separator)
                n = p[separatorposition + 1:]
                old_tg_id = p[:separatorposition]

            for (name, title) in self.values:
                # Look for the name and set the old tg_id if available.
                if name == n:
                    ret.append((n, old_tg_id))

        return tuple(ret)


class CustomTextAreaWidget(deform.widget.TextAreaWidget):
    """
    Overwrite the function get_template_values() with a custom one to add more
    values to the template.
    """
    def get_template_values(self, field, cstruct, kw):
        return custom_get_template_values(self, field, cstruct, kw)


class CustomDateInputWidget(deform.widget.DateInputWidget):
    """
    Overwrite the function get_template_values() with a custom one to add more
    values to the template.
    """
    def get_template_values(self, field, cstruct, kw):
        return custom_get_template_values(self, field, cstruct, kw)


class CustomInvolvementWidget(deform.widget.MappingWidget):
    """
    Custom widget only used to specify additional requirements.
    """
    requirements = (('involvementwidget', None),)


class CustomMapWidget(deform.widget.MappingWidget):
    requirements = (('mapwidget', None),)

    def get_template_values(self, field, cstruct, kw):
        kw.update({
            'geometry_type': self.geometry_type,
            'editmode': self.edit_mode,
            'label': self.label,
        })
        return super().get_template_values(field, cstruct, kw)
