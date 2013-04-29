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
        cat_form = colander.SchemaNode(
            colander.Mapping(),
            name=self.getId(),
            title=self.getName()
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

    def __init__(self, id, name):
        self.id = id
        self.name = name
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

    def getForm(self):
        """
        Prepare the form node for this thematic group, append the forms of its
        taggroups and return it.
        """
        thg_form = colander.SchemaNode(
            colander.Mapping(),
            name=self.getName()
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
        return self.repeatable

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
        type = self.getKey().getType()
        # Decide which type of form to add
        if type.lower() == 'predefined' and len(self.getValues()) > 0:
            # Dropdown
            # Prepare the choices for keys with predefined values
            valuechoices = tuple((x.getName(), x.getName())
                for x in self.getValues())
            selectchoice = ('', '- Select -')
            choices = (selectchoice,) + valuechoices
            form = colander.SchemaNode(
                colander.String(),
                validator=colander.OneOf([x[0] for x in choices]),
                widget=deform.widget.SelectWidget(values=choices),
                name=name
            )
        elif type.lower() == 'number':
            # Number field
            form = colander.SchemaNode(
                colander.Int(),
                name=name
            )
        elif type.lower() == 'text':
            # Textarea
            form = colander.SchemaNode(
                colander.String(),
                widget=deform.widget.TextAreaWidget(rows=10, cols=60),
                name=name
            )
        elif type.lower() == 'date':
            # Date
            form = colander.SchemaNode(
                colander.Date(),
                widget=deform.widget.DateInputWidget(),
                name=name,
            )
        else:
            # Default: Textfield
            form = colander.SchemaNode(
                colander.String(),
                widget=deform.widget.TextInputWidget(size=50),
                name=name
            )
        # Is this tag mandatory?
        if self.getMandatory() is False:
            form.missing = colander.null
        # Add a validator for this key if there is one
        if self.getKey().getValidator() is not None:
            form.validator = eval(self.getKey().getValidator())
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
        Return the validator of this key.
        """
        return self.validator

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


class ConfigValue(object):
    """
    A class representing a Form Key object as defined in the configuration 
    file (csv). This is the lowest structure of the form.
    """

    def __init__(self, id, name, fk_key, order):
        self.id = id
        self.name = name
        self.fk_key = fk_key
        self.order = order

        self.key = None

    def getId(self):
        """
        Return the id (as defined in the configuration file) of the value.
        """
        return self.id

    def getName(self):
        """
        Return the name (as defined in the configuration file) of the category.
        """
        return self.name

    def getOrder(self):
        """
        Return the order of this value.
        """
        return self.order


def getConfigKeyList(request, itemType):
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
    return configKeys

def getConfigValueList(request, itemType):
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
    return configValues

def getConfigCategoryList(request, itemType):
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
    return configCategories

def getCategoryList(request, itemType):
    """
    Function to scan through the configuration yaml and put together the list of
    categories which can be used to create the form.
    itemType: activities / stakeholders
    """
    # Scan the configuration files for keys, values and categories
    configKeys = getConfigKeyList(request, itemType)
    configValues = getConfigValueList(request, itemType)
    configCategories = getConfigCategoryList(request, itemType)
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
                thematicCategory.getId(), thematicCategory.getName()
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

                        # We need to make a copy of the original object.
                        # Otherwise we are not able to add a custom validator
                        # only for one key.
                        tag.setKey(copy.copy(configKey))

                        if key_config is not None:

                            if 'values' in key_config:
                                # If available, loop the values of the key
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

                        taggroup.addTag(tag)

                    except ValueError:
                        # Configuration of taggroup
                        if key_id == 'repeat' and key_config is True:
                            taggroup.setRepeatable(True)

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