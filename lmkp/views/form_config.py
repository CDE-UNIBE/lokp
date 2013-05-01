import colander
import copy
import csv
import deform
import yaml

from lmkp.config import profile_directory_path

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
        # TODO: Try to speed up (?) by looking directly using the index
        for c in self.categories:
            if c.getId() == str(id):
                return c
        return None

    def getAllMainkeys(self):
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
        Return a list with the names of all keys in all categories.
        """
        keys = []
        for cat in self.getCategories():
            for thg in cat.getThematicgroups():
                for tg in thg.getTaggroups():
                    for t in tg.getTags():
                        keys.append(t.getKey().getName())
        return keys

    def getMainkeyWithGeometry(self):
        """
        Return a list with the names of all main keys of taggroups which can
        have a geometry
        """
        mainkeys = []
        for cat in self.getCategories():
            for thg in cat.getThematicgroups():
                for tg in thg.getTaggroups():
                    if tg.getGeometry() is True:
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

class ConfigCategory(object):
    """
    A class representing a Form Category object as defined in the configuration 
    file (csv). This is the top container of the form structure, for example
    'Spatial Data' or 'General Information' and it contains Form Thematic Groups
    as the next lower form structure.
    """

    def __init__(self, id, name, level, fk_category):
        self.id = id
        self.name = name
        self.translation = None
        self.level = level
        self.fk_category = fk_category
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

    def getTranslation(self):
        """
        Return the translation of this category.
        """
        return self.translation

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

    def getForm(self):
        """
        Prepare the form node for this category, append the forms of its
        thematic groups and return it.
        """
        title = (self.getTranslation() if self.getTranslation() is not None
            else self.getName())
        cat_form = colander.SchemaNode(
            colander.Mapping(),
            name=self.getId(),
            title=title
        )
        for thg in self.getThematicgroups():
            # Get the Form for each Thematicgroup
            thg_form = thg.getForm()
            thg_form.missing = colander.null
            thg_form.name = thg.getId()
            cat_form.add(thg_form)
        return cat_form

class ConfigThematicgroup(object):
    """
    A class representing a Form Thematic Group object as defined in the 
    configuration file (csv). This is second top container of the form
    structure, for example 'Intention of Investment' in the Category 'General
    Information'. It contains Form Taggroups as the next lower form structure.
    """

    def __init__(self, id, name, translation):
        self.id = id
        self.name = name
        self.translation = translation
        self.taggroups = []

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

    def getName(self):
        """
        Return the name (as defined in the configuration file) of the thematic
        group.
        """
        return self.name

    def getTranslation(self):
        """
        Return the translation of this thematic group.
        """
        return self.translation

    def getForm(self):
        """
        Prepare the form node for this thematic group, append the forms of its
        taggroups and return it.
        """
        title = (self.getTranslation() if self.getTranslation() is not None
            else self.getName())
        thg_form = colander.SchemaNode(
            colander.Mapping(),
            title=title
        )
        for tg in self.getTaggroups():
            # Get the Form for each Taggroup
            tg_form = tg.getForm()
            name = str(tg.getId())
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
                    widget=deform.widget.SequenceWidget(min_len=1),
                    name=name,
                    title=''
                ))
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
        Return a list of all thematic groups in this category.
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

    def hasKey(self, key):
        """
        Try to find a key in this taggroup. Return true if found, false if not.
        """
        for t in self.getTags():
            if t.getKey().getName() == key:
                return True
        return False

    def getForm(self):
        """
        Prepare the form node for this taggroup, append the forms of its  tags
        and return it.
        """
        tg_form = colander.SchemaNode(colander.Mapping())
        maintag = self.getMaintag()
        # First add the maintag
        if maintag is not None:
            tg_form.add(maintag.getForm())
        # Remove the maintag from the list and get the form of the remaining
        # tags
        if maintag in self.getTags():
            self.getTags().remove(maintag)
        for t in self.getTags():
            # Get the Form for each tag
            tg_form.add(t.getForm())
        # Add a hidden field for the tg_id
        tg_form.add(colander.SchemaNode(
            colander.Int(),
            widget=deform.widget.HiddenWidget(),
            name='tg_id',
            missing = colander.null
        ))
        tg_form.validator = self.maintag_validator
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
        if value[mainkey] == colander.null:
            # ... check if one of the other values is set
            hasOtherValuesSet = False
            for (k, v) in value.iteritems():
                if k != mainkey and v != colander.null and k != 'tg_id':
                    hasOtherValuesSet = True
            if hasOtherValuesSet:
                exc = colander.Invalid(form, 'The maintag (%s) cannot be empty!'
                    % mainkey)
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

    def getForm(self):
        """
        Prepare the form node for this tag, append the nodes of its keys
        (depending on its type) and return it.
        """
        # Get name and type of key
        name = self.getKey().getName()
        title = (self.getKey().getTranslation()
            if self.getKey().getTranslation() is not None
            else self.getKey().getName())
        type = self.getKey().getType()
        # Decide which type of form to add
        if type.lower() == 'dropdown' and len(self.getValues()) > 0:
            # Dropdown
            # Prepare the choices for keys with predefined values
            valuechoices = tuple((x.getName(), x.getTranslation())
                for x in self.getValues())
            selectchoice = ('', '- Select -')
            choices = (selectchoice,) + valuechoices
            form = colander.SchemaNode(
                colander.String(),
                validator=colander.OneOf([x[0] for x in choices]),
                widget=deform.widget.SelectWidget(values=choices),
                name=name,
                title=title
            )
        elif type.lower() == 'checkbox' and len(self.getValues()) > 0:
            # Checkbox
            # Prepare the choices for keys with predefined values
            choices = []
            for v in self.getValues():
                choices.append((v.getName(), v.getTranslation()))

            form = colander.SchemaNode(
                colander.Set(),
                widget=CBWidget(values=tuple(choices)),
                name=name,
                title=title
            )
        elif type.lower() == 'number' or type.lower() == 'integer':
            # Number or Integer field
            deform.widget.default_resource_registry.set_js_resources(
                'jqueryspinner',None,'../static/jquery-ui-1.9.2.custom.min.js')
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
                widget=NumberSpinnerWidget(options=options),
                name=name,
                title=title
            )
        elif type.lower() == 'text':
            # Textarea
            form = colander.SchemaNode(
                colander.String(),
                widget=deform.widget.TextAreaWidget(rows=5, cols=60),
                name=name,
                title=title
            )
        elif type.lower() == 'date':
            # Date
            form = colander.SchemaNode(
                colander.Date(),
                widget=deform.widget.DateInputWidget(),
                name=name,
                title=title
            )
        else:
            # Default: Textfield
            form = colander.SchemaNode(
                colander.String(),
                widget=deform.widget.TextInputWidget(size=50),
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
        if isinstance(key, ConfigKey) and self.findKeyById(key.getId()) is None:
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
            if k.getId() == str(id):
                return k
        return None

class ConfigKey(object):
    """
    A class representing a Form Key object as defined in the configuration 
    file (csv). This is the lowest structure of the form.
    """

    def __init__(self, id, name, type, helptext, validator):
        self.id = id
        self.name = name
        self.translation = None
        self.type = type
        self.helptext = helptext
        self.validator = validator if validator != '' else None

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

    def setTranslation(self, translation):
        """
        Set the translation of this key.
        """
        self.translation = translation

    def getTranslation(self):
        """
        Return the translation of this key.
        """
        return self.translation

    def getType(self):
        """
        Return the type of this key.
        """
        return self.type

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
            if v.getFkkey() == str(fk_key):
                values.append(v)
        return values

class ConfigValue(object):
    """
    A class representing a Form Key object as defined in the configuration 
    file (csv). This is the lowest structure of the form.
    """

    def __init__(self, id, name, fk_key, order):
        self.id = id
        self.name = name
        # The initial value of the translation is set to be the same as the name
        self.translation = name
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

    def getTranslation(self):
        """
        Return the translation of this value.
        """
        return self.translation

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


def getConfigKeyList(request, itemType, lang=None):
    """
    Function to collect and return all the keys from the configuration file
    (csv).
    itemType: activities / stakeholders
    """
    if itemType == 'stakeholders':
        filename = 'skeys.csv'
    else:
        filename = 'akeys.csv'
    # Read and collect all Keys based on CSV list
    configKeys = ConfigKeyList()
    keys_stream = open('%s/%s'
        % (profile_directory_path(request), filename), 'rb')
    keys_csv = csv.reader(keys_stream, delimiter=';')
    for row in keys_csv:
        # Skip the first row
        if keys_csv.line_num > 1:
            configKeys.addKey(ConfigKey(*row))
    # Translation
    if lang is not None:
        # TODO
        t_filename = 'akeys_translated.csv'

        translationStream = open('%s/%s'
            % (profile_directory_path(request), t_filename), 'rb')
        translationCsv = csv.reader(translationStream, delimiter=';')
        for row in translationCsv:
            # Skip the first row
            if translationCsv.line_num > 1 and len(row) == 2:
                k = configKeys.findKeyById(row[0])
                if k is not None:
                    k.setTranslation(row[1])
    return configKeys

def getConfigValueList(request, itemType, lang=None):
    """
    Function to collect and return all the values from the configuration file
    (csv).
    itemType: activities / stakeholders
    """
    if itemType == 'stakeholders':
        filename = 'svalues.csv'
    else:
        filename = 'avalues.csv'
    # Read and collect all Values based on CSV list
    configValues = ConfigValueList()
    values_stream = open('%s/%s'
        % (profile_directory_path(request), filename), 'rb')
    values_csv = csv.reader(values_stream, delimiter=';')
    for row in values_csv:
        # Skip the first row
        if values_csv.line_num > 1:
            configValues.addValue(ConfigValue(*row))
    # Translation
    if lang is not None:
        # TODO
        t_filename = 'avalues_translated.csv'

        translationStream = open('%s/%s'
            % (profile_directory_path(request), t_filename), 'rb')
        translationCsv = csv.reader(translationStream, delimiter=';')
        for row in translationCsv:
            # Skip the first row
            if translationCsv.line_num > 1 and len(row) == 2:
                v = configValues.findValueById(row[0])
                if v is not None:
                    v.setTranslation(row[1])

    return configValues

def getConfigCategoryList(request, itemType, lang=None):
    """
    Function to collect and return all the categories from the configuration
    file (csv). Both categories and thematic groups are treated as the same type
    of 'categories' in this csv.
    itemType: activities / stakeholders
    """
    if itemType == 'stakeholders':
        filename = 'scategories.csv'
    else:
        filename = 'acategories.csv'
    # Read and collect all Categories based on CSV list
    configCategories = ConfigCategoryList()
    categories_stream = open('%s/%s'
        % (profile_directory_path(request), filename), 'rb')
    categories_csv = csv.reader(categories_stream, delimiter=';')
    for row in categories_csv:
        # Skip the first row
        if categories_csv.line_num > 1:
            configCategories.addCategory(ConfigCategory(*row))
    # Translation
    if lang is not None:
        # TODO
        t_filename = 'acategories_translated.csv'

        translationStream = open('%s/%s'
            % (profile_directory_path(request), t_filename), 'rb')
        translationCsv = csv.reader(translationStream, delimiter=';')
        for row in translationCsv:
            # Skip the first row
            if translationCsv.line_num > 1 and len(row) == 2:
                c = configCategories.findCategoryById(row[0])
                if c is not None:
                    c.setTranslation(row[1])
    return configCategories

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
        'string'
    ]

def getCategoryList(request, itemType, lang=None):
    """
    Function to scan through the configuration yaml and put together the list of
    categories which can be used to create the form.
    itemType: activities / stakeholders
    """
    # Scan the configuration files for keys, values and categories
    configKeys = getConfigKeyList(request, itemType, lang)
    configValues = getConfigValueList(request, itemType, lang)
    configCategories = getConfigCategoryList(request, itemType, lang)

    # Do some first test on the keys: Check that each type is defined correctly
    unknowntypes = []
    knowntypes = getValidKeyTypes()
    for k in configKeys.getKeys():
        if k.getType().lower() not in knowntypes:
            unknowntypes.append(k.getName())

    if len(unknowntypes) > 0:
        raise NameError('One or more keys have unknown types: %s'
            % ', '.join(unknowntypes))

    # Load the yaml
    if itemType == 'stakeholders':
        # TODO
        filename = ''
    else:
        filename = 'test3.yml'
    yaml_stream = open("%s/%s"
        % (profile_directory_path(request), filename), 'r')
    yaml_config = yaml.load(yaml_stream)

    categorylist = ConfigCategoryList()
    emptymaintag = []
    unknownkeys = []

    # Loop the categories of the yaml config file
    for (cat_id, thmgrps) in yaml_config['fields'].iteritems():

        # Find the category in the list of csv categories
        category = configCategories.findCategoryById(cat_id)

        if category is None:
            # If category is not found, move on
            continue

        # Loop the thematic groups of the category
        for (thmgrp_id, taggroups) in thmgrps.iteritems():

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
                thematicCategory.getTranslation()
            )

            # Loop the taggroups of the thematic group
            for (tgroup_id, tags) in taggroups.iteritems():

                # Create a taggroup out of it
                taggroup = ConfigTaggroup(tgroup_id)

                # Loop the keys of the taggroup
                for (key_id, key_config) in tags.iteritems():

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

                            if 'validator' in key_config:
                                tag.getKey().\
                                    setValidator(key_config['validator'])

                            if 'maintag' in key_config:
                                taggroup.setMaintag(tag)

                            # If the values are predefined and they are not set
                            # already (defined explicitly in YAML), then get the
                            # values from the value config csv.
                            if (configKey.getType().lower() == 'dropdown'
                                or configKey.getType().lower() == 'checkbox'):
                                for v in configValues.\
                                    findValuesByFkkey(configKey.getId()):
                                    tag.addValue(v)

                        taggroup.addTag(tag)

                    except ValueError:
                        # Configuration of taggroup
                        if key_id == 'repeat' and key_config is True:
                            taggroup.setRepeatable(True)

                        if key_id == 'geometry' and key_config is True:
                            taggroup.setGeometry(True)

                if taggroup.getMaintag() is None:
                    emptymaintag.append(taggroup)
                else:
                    thematicgroup.addTaggroup(taggroup)

            category.addThematicgroup(thematicgroup)

        categorylist.addCategory(category)

    # Keys not found
    if len(unknownkeys) > 0:
        raise NameError('One or more keys were not found in CSV file: %s'
            % ', '.join(unknownkeys))

    # Tags where the maintag is not found
    if len(emptymaintag) > 0:
        # Collect the names of the tags in the taggroup to give nicer feedback
        emptystack = []
        for e in emptymaintag:
            tags = []
            for t in e.getTags():
                tags.append('%s [%s]'
                    % (t.getKey().getName(), t.getKey().getId()))
            emptystack.append('Taggroup [%s]' % ', '.join(tags))
        raise NameError('One or more Taggroups do not have a maintag: %s'
            % ', '.join(emptystack))

    # Check that each mainkey is unique (is only set once throughout all keys)
    allkeys = categorylist.getAllKeys()
    allmainkeys = categorylist.getAllMainkeys()
    duplicates = []
    for mainkey in allmainkeys:
        if allkeys.count(mainkey) > 1:
            if mainkey not in duplicates:
                duplicates.append(mainkey)

    if len(duplicates) > 0:
        # TODO: Error handling
        raise NameError('Duplicated mainkey(s): %s' % ', '.duplicates)

    return categorylist

class NumberSpinnerWidget(deform.widget.Widget):
    """
    Custom Deform widget. Adds a spinner to a input field using the jQuery UI
    library.
    """
    template = 'lmkp:templates/form/numberspinner_template'
    readonly_template = 'readonly/textinput'
    type_name = 'number'
    size = None
    style = None
    requirements = ( ('jqueryui', None), ('jqueryspinner', None), )
    default_options = ()

    def __init__(self, *args, **kwargs):
        self.options = dict(self.default_options)
        deform.widget.Widget.__init__(self, *args, **kwargs)

    def serialize(self, field, cstruct, **kw):
        if cstruct in (colander.null, None):
            cstruct = ''
        readonly = kw.get('readonly', self.readonly)
        template = readonly and self.readonly_template or self.template
        kw.setdefault('options', self.options)
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct in ('', colander.null):
            return colander.null
        return pstruct


class CBWidget(deform.widget.Widget):
    """
    Custom Deform widget. Based very much on the default checkbox choice widget.
    It allows to save a tg_id to the value before showing the checkboxes and
    extracts this value again after submission.
    """
    template = 'lmkp:templates/form/checkbox_template'
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
        # checkbox can contain only one real value, the tg_id needs to be stored
        # in the inner (submit) value of the checkbox.
        formdata = []
        for c in cstruct:
            # Transform tuples to list to access them more easily
            valuelist = list(values)
            for i, (name, title) in enumerate(valuelist):
                if name == c[0]:
                    # Update the (internal) name of the values
                    newname = '%s%s%s' % (c[1], self.separator, name)
                    valuelist[i] = (newname, title)

            # Transform the list back to tuples
            values = tuple(valuelist)
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
                n = p[separatorposition+1:]
                old_tg_id = p[:separatorposition]

            for (name, title) in self.values:
                # Look for the name and set the old tg_id if available.
                if name == n:
                    ret.append((n, old_tg_id))

        return tuple(ret)
