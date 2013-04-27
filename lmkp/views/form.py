import colander
import deform
import copy
import yaml
import csv

from lmkp.config import profile_directory_path

from pyramid.view import view_config

class ConfigThematicgroupList(object):

    def __init__(self):
        self.thematicgroups = []

    def addThematicgroup(self, thematicgroup):
        if isinstance(thematicgroup, ConfigThematicgroup) and thematicgroup not in self.thematicgroups:
            self.thematicgroups.append(thematicgroup)

    def getThematicgroups(self):
        return self.thematicgroups


class ConfigThematicgroup(object):

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.taggroups = []

    def getId(self):
        return self.id

    def addTaggroup(self, taggroup):
        if isinstance(taggroup, ConfigTaggroup) and taggroup not in self.taggroups:
            self.taggroups.append(taggroup)

    def getTaggroups(self):
        return self.taggroups

    def findTaggroupByKey(self, key):
        if isinstance(key, ConfigKey):
            for tg in self.getTaggroups():
                pass

    def getName(self):
        return self.name

    def getForm(self):

        thg_form = colander.SchemaNode(
            colander.Mapping(), 
            name=self.getName()
        )

        for i, tg in enumerate(self.getTaggroups()):
            # Get the Form for each Taggroup
            tg_form = tg.getForm()

            name = 'taggroup_%s' % (i+1)

            if tg.getRepeatable() is False:
                tg_form.missing = colander.null
                tg_form.name = name
                thg_form.add(tg_form)
            else:
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

    def __init__(self):
        self.taggroups = []

    def addTaggroup(self, taggroup):
        if isinstance(taggroup, ConfigTaggroup) and taggroup not in self.taggroups:
            self.taggroups.append(taggroup)

    def getTaggroups(self):
        return self.taggroups

    def findTaggroupByKey(self, key):
        if isinstance(key, ConfigKey):
            for tg in self.getTaggroups():
                pass


class ConfigTaggroup(object):

    def __init__(self):
        self.maintag = None
        self.tags = []
        self.repeatable = False

    def setMaintag(self, tag):
        if isinstance(tag, ConfigTag):
            self.maintag = tag

    def getMaintag(self):
        return self.maintag

    def addTag(self, tag):
        if isinstance(tag, ConfigTag) and tag not in self.tags:
            self.tags.append(tag)

    def getTags(self):
        return self.tags

    def setRepeatable(self, repeatable):
        self.repeatable = repeatable

    def getRepeatable(self):
        return self.repeatable

    def getForm(self):

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

        tg_form.validator = self.maintag_validator

        return tg_form

    def maintag_validator(self, form, value):

        mainkey = self.getMaintag().getKey().getName()

        # If the maintag is empty, ...
        if value[mainkey] == colander.null:
            # ... check if one of the other values is set
            otherValueSet = False
            for (k, v) in value.iteritems():
                if k != mainkey and v != colander.null:
                    otherValueSet = True

            if otherValueSet:
                exc = colander.Invalid(form, 'The maintag (%s) cannot be empty!' % mainkey)
                raise exc


class ConfigTag(object):

    def __init__(self):
        self.key = None
        self.values = []
        self.mandatory = False

    def setKey(self, key):
        if isinstance(key, ConfigKey):
            self.key = key

    def getKey(self):
        return self.key

    def addValue(self, value):
        if isinstance(value, ConfigValue) and value not in self.values:
            self.values.append(value)

    def getValues(self):
        return self.values

    def setMandatory(self, mandatory):
        self.mandatory = mandatory

    def getMandatory(self):
        return self.mandatory is True

    def getForm(self):

        # Prepare the choices for keys with predefined values
        valuechoices = tuple((x.getName(), x.getName()) for x in self.getValues())
        selectchoice = ('', '- Select -')
        choices = (selectchoice,) + valuechoices

        # Get name and type of key
        name = self.getKey().getName()
        type = self.getKey().getType()

        if type.lower() == 'predefined' and len(self.getValues()) > 0:
            # Dropdown
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

        if self.getMandatory() is False:
            form.missing = colander.null

        if self.getKey().getValidator() is not None:
            form.validator = eval(self.getKey().getValidator())

        return form
#        # Radio
#        return colander.SchemaNode(
#            colander.String(),
#            validator=colander.OneOf([x[0] for x in choices]),
#            widget=deform.widget.RadioChoiceWidget(values=choices),
#            name=self.getKey().getName()
#        )


class ConfigKeyList(object):

    def __init__(self):
        self.keys = []

    def addKey(self, key):
        if isinstance(key, ConfigKey) and self.findKeyById(key.getId()) is None:
            self.keys.append(key)

    def findKeyById(self, id):
        # TODO: Try to speed up (?) by looking directly using the index
        for k in self.keys:
            if k.getId() == str(id):
                return k
        return None

    def getKeys(self):
        return self.keys

class ConfigValueList(object):

    def __init__(self):
        self.values = []

    def addValue(self, value):
        if isinstance(value, ConfigValue) and self.findValueById(value.getId()) is None:
            self.values.append(value)

    def findValueById(self, id):
        # TODO: Try to speed up (?) by looking directly using the index
        for v in self.values:
            if v.getId() == str(id):
                return v
        return None

    def getValues(self):
        return self.values

class ConfigCategoryList(object):

    def __init__(self):
        self.categories = []

    def addCategory(self, category):
        if isinstance(category, ConfigCategory) and category not in self.categories:
            self.categories.append(category)

    def getCategories(self):
        return self.categories

    def findCategoryById(self, id):
        # TODO: Try to speed up (?) by looking directly using the index
        for c in self.categories:
            if c.getId() == str(id):
                return c
        return None

    def getAllMainkeys(self):
        mainkeys = []
        for cat in self.getCategories():
            for thg in cat.getThematicgroups():
                for tg in thg.getTaggroups():
                    mainkeys.append(tg.getMaintag().getKey().getName())
        return mainkeys

    def getAllKeys(self):
        keys = []
        for cat in self.getCategories():
            for thg in cat.getThematicgroups():
                for tg in thg.getTaggroups():
                    for t in tg.getTags():
                        keys.append(t.getKey().getName())
        return keys

class ConfigKey(object):

    def __init__(self, id, name, type, helptext, validator):
        self.id = id
        self.name = name
        self.type = type
        self.helptext = helptext
        self.validator = validator if validator != '' else None

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def getType(self):
        return self.type

    def setValidator(self, validator):
        self.validator = validator

    def getValidator(self):
        return self.validator

class ConfigValue(object):

    def __init__(self, id, name, fk_key, order):
        self.id = id
        self.name = name
        self.fk_key = fk_key
        self.order = order

        self.key = None

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def getFkKey(self):
        return self.fk_key

    def getOrder(self):
        return self.order

class ConfigCategory(object):

    def __init__(self, id, name, level, fk_category):
        self.id = id
        self.name = name
        self.level = level
        self.fk_category = fk_category

        self.thematicgroups = []

    def getId(self):
        return self.id

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def addThematicgroup(self, thematicgroup):
        if isinstance(thematicgroup, ConfigThematicgroup) and thematicgroup not in self.thematicgroups:
            self.thematicgroups.append(thematicgroup)

    def getThematicgroups(self):
        return self.thematicgroups

    def getForm(self):

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


@view_config(route_name='form_tests', renderer='lmkp:templates/form_test.pt')
def form_tests(request):

    # Read and collect all Keys based on CSV list
    configKeys = ConfigKeyList()
    keys_stream = open('%s/%s' % (profile_directory_path(request), 'akeys.csv'), 'rb')
    keys_csv = csv.reader(keys_stream, delimiter=';')
    for row in keys_csv:
        # Skip the first row
        if keys_csv.line_num > 1:
            configKeys.addKey(ConfigKey(*row))

    # Read and collect all Values based on CSV list
    configValues = ConfigValueList()
    values_stream = open('%s/%s' % (profile_directory_path(request), 'avalues.csv'), 'rb')
    values_csv = csv.reader(values_stream, delimiter=';')
    for row in values_csv:
        # Skip the first row
        if values_csv.line_num > 1:
            configValues.addValue(ConfigValue(*row))

    # Read and collect all Categories based on CSV list
    configCategories = ConfigCategoryList()
    categories_stream = open('%s/%s' % (profile_directory_path(request), 'categories.csv'), 'rb')
    categories_csv = csv.reader(categories_stream, delimiter=';')
    for row in categories_csv:
        # Skip the first row
        if categories_csv.line_num > 1:
            configCategories.addCategory(ConfigCategory(*row))


    yaml_stream = open("%s/%s" % (profile_directory_path(request), 'test3.yml'), 'r')
    yaml_config = yaml.load(yaml_stream)

    categorylist = ConfigCategoryList()

    emptymaintag = []
    unknownkeys = []


    # Loop the categories of the yaml config file
    for (cat, thmgrps) in yaml_config['fields'].iteritems():

        # Find the category in the list of csv categories
        category = configCategories.findCategoryById(cat)

        if category is None:
            continue

        # Loop the thematic groups of the category
        for (thmgrp, taggroups) in thmgrps.iteritems():

            # The name of the thematic group also stands in the categories csv.
            # So it is necessary to find the category there
            thematicCategory = configCategories.findCategoryById(thmgrp)

            if thematicCategory is None:
                continue

            # Create a thematicgroup out of it
            thematicgroup = ConfigThematicgroup(
                thematicCategory.getId(), thematicCategory.getName()
            )

            # Loop the taggroups of the thematic group
            for tags in taggroups:

                taggroup = ConfigTaggroup()

                # Loop the keys of the taggroup
                for (key, key_config) in tags.iteritems():

                    try:
                        int(key)

                        # Definition of tag and its values
                        tag = ConfigTag()

                        configKey = configKeys.findKeyById(key)

                        if configKey is None:
                            unknownkeys.append(str(key))

                        # We need to make a copy of the original object.
                        # Otherwise we are not able to add a custom validator
                        # only for one key.
                        tag.setKey(copy.copy(configKey))

                        if key_config is not None:

                            if 'values' in key_config:
                                # If available, loop the values of the key
                                for v in key_config['values']:
                                    tag.addValue(configValues.findValueById(v))

                            if 'mandatory' in key_config and key_config['mandatory'] is True:
                                tag.setMandatory(True)

                            if 'validator' in key_config:
                                tag.getKey().setValidator(key_config['validator'])

                            if 'maintag' in key_config:
                                taggroup.setMaintag(tag)

                        taggroup.addTag(tag)

                    except ValueError:
                        # Configuration of taggroup
                        if key == 'repeat' and key_config is True:
                            taggroup.setRepeatable(True)

                if taggroup.getMaintag() is None:
                    emptymaintag.append(taggroup)
                else:
                    thematicgroup.addTaggroup(taggroup)

            category.addThematicgroup(thematicgroup)

        categorylist.addCategory(category)

    # Keys not found
    if len(unknownkeys) > 0:
        raise NameError('One or more keys were not found in CSV file: %s' % ', '.join(unknownkeys))

    # Tags where the maintag is not found
    if len(emptymaintag) > 0:
        # Collect the names of the tags in the taggroup to give nicer feedback
        emptystack = []
        for e in emptymaintag:
            tags = []
            for t in e.getTags():
                tags.append('%s [%s]' % (t.getKey().getName(), t.getKey().getId()))
            emptystack.append('Taggroup [%s]' % ', '.join(tags))
        raise NameError('One or more Taggroups do not have a maintag: %s' % ', '.join(emptystack))

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


#    duplicates = [x for x, y in collections.Counter(a).items() if y > 1]
#    if len(duplicates) > 0:
#        # TODO: Error handling
#        raise NameError('Duplicated mainkey(s): %s' % duplicates)

    # Collect the forms for each category
    cat_forms = []
    for cat in categorylist.getCategories():
        cat_forms.append(cat.getForm())

    # Put together all categories to one Schema
    schema = colander.SchemaNode(colander.Mapping())
    for cat_form in cat_forms:
        schema.add(cat_form)

    form = deform.Form(schema, buttons=('submit',))

    # JS and CSS requirements (for widgets)
    resources = form.get_widget_resources()

    captured = None
    success = None


    data = {
      '2': {
        '13': {
          'taggroup_1': {
            'How much do investors pay for water': 'blabla'
          }
        },
        '12': {
          'taggroup_2': [
            {
              'Contract area (ha)': 200,
              'Year': 2000
            }
          ]
        }
      }
    }

    if 'submit' in request.POST:
        # the request represents a form submission
        try:
            # try to validate the submitted values
            controls = request.POST.items()
            captured = form.validate(controls)
            if success:
                response = success()
                if response is not None:
                    return response

            print "---------"
            print captured

#            formToDiff(captured)

            html = form.render(captured)
        except deform.ValidationFailure as e:
            # the submitted values could not be validated
            html = e.render()

    else:
        html = form.render(data)

    jsonToForm('bla')

    return {
        'form': html,
        'css_links': resources['css'],
        'js_links': resources['js']
    }

def jsonToForm(json):

#    json = {
#        "total": 1,
#        "data": [
#            {
#                "status": "active",
#                "previous_version": 1,
#                "status_id": 2,
#                "geometry": {
#                    "type": "Point",
#                    "coordinates": [
#                        102.44012553528,
#                        19.472002471451
#                    ]
#                },
#                "taggroups": [
#                    {
#                        "tg_id": 2,
#                        "main_tag": {
#                            "value": "Laos",
#                            "id": 560,
#                            "key": "Country"
#                        },
#                        "id": 536,
#                        "tags": [
#                            {
#                                "value": "Laos",
#                                "id": 560,
#                                "key": "Country"
#                            }
#                        ]
#                    },
#                    {
#                        "tg_id": 4,
#                        "main_tag": {
#                            "value": "Mining",
#                            "id": 562,
#                            "key": "Intention of Investment"
#                        },
#                        "id": 538,
#                        "tags": [
#                            {
#                                "value": "Mining",
#                                "id": 562,
#                                "key": "Intention of Investment"
#                            }
#                        ]
#                    },
#                    {
#                        "tg_id": 1,
#                        "main_tag": {
#                            "value": "100",
#                            "id": 559,
#                            "key": "Intended area (ha)"
#                        },
#                        "id": 535,
#                        "tags": [
#                            {
#                                "value": "100",
#                                "id": 559,
#                                "key": "Intended area (ha)"
#                            }
#                        ]
#                    },
#                    {
#                        "tg_id": 6,
#                        "main_tag": {
#                            "value": "100m to 1km",
#                            "id": 564,
#                            "key": "Spatial Accuracy"
#                        },
#                        "id": 540,
#                        "tags": [
#                            {
#                                "value": "100m to 1km",
#                                "id": 564,
#                                "key": "Spatial Accuracy"
#                            }
#                        ]
#                    },
#                    {
#                        "tg_id": 3,
#                        "main_tag": {
#                            "value": "Contract",
#                            "id": 561,
#                            "key": "Data source"
#                        },
#                        "id": 537,
#                        "tags": [
#                            {
#                                "value": "Contract",
#                                "id": 561,
#                                "key": "Data source"
#                            }
#                        ]
#                    },
#                    {
#                        "tg_id": 7,
#                        "main_tag": {
#                            "value": "d0f5b496-edcd-458c-84a9-72ca4e1135f5",
#                            "id": 565,
#                            "key": "Remark"
#                        },
#                        "id": 541,
#                        "tags": [
#                            {
#                                "value": "d0f5b496-edcd-458c-84a9-72ca4e1135f5",
#                                "id": 565,
#                                "key": "Remark"
#                            }
#                        ]
#                    },
#                    {
#                        "tg_id": 5,
#                        "main_tag": {
#                            "value": "Contract signed",
#                            "id": 563,
#                            "key": "Negotiation Status"
#                        },
#                        "id": 539,
#                        "tags": [
#                            {
#                                "value": "Contract signed",
#                                "id": 563,
#                                "key": "Negotiation Status"
#                            }
#                        ]
#                    }
#                ],
#                "version": 2,
#                "user": {
#                    "username": "user2",
#                    "id": 3
#                },
#                "timestamp": "2013-04-23 14:40:37.099000",
#                "id": "d0f5b496-edcd-458c-84a9-72ca4e1135f5"
#            }
#        ]
#    }

    json = {
        "total": 1,
        "data": [
            {
                "status": "active",
                "previous_version": 1,
                "status_id": 2,
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        102.44012553528,
                        19.472002471451
                    ]
                },
                "taggroups": [
                    {
                        "tg_id": 1,
                        "main_tag": {
                            "value": 50,
                            "id": 560,
                            "key": "Current Area In Operation (Ha)"
                        },
                        "id": 536,
                        "tags": [
                            {
                                "value": 50,
                                "id": 560,
                                "key": "Current Area In Operation (Ha)"
                            }
                        ]
                    },
                    {
                        "tg_id": 2,
                        "main_tag": {
                            "value": 100,
                            "id": 562,
                            "key": "Intended Area (Ha)"
                        },
                        "id": 538,
                        "tags": [
                            {
                                "value": 100,
                                "id": 562,
                                "key": "Intended Area (Ha)"
                            }
                        ]
                    },
                    {
                        "tg_id": 3,
                        "main_tag": {
                            "value": "blabla",
                            "id": 559,
                            "key": "How Much Do Investors Pay For Water"
                        },
                        "id": 535,
                        "tags": [
                            {
                                "value": "blabla",
                                "id": 559,
                                "key": "How Much Do Investors Pay For Water"
                            }
                        ]
                    }
                ],
                "version": 2,
                "user": {
                    "username": "user2",
                    "id": 3
                },
                "timestamp": "2013-04-23 14:40:37.099000",
                "id": "d0f5b496-edcd-458c-84a9-72ca4e1135f5"
            }
        ]
    }

#    print json


    activity = json['data'][0]

    taggroups = activity['taggroups']

    for tg in taggroups:
        print "---"
        print tg

        # Get the category and thematic group based on the maintag
        maintag = tg['main_tag']

        print maintag



def formToDiff(form):

    print "****"

    diff = {}

    # Loop the categories of the form
    for (cat, thmgrps) in form.iteritems():

        # Loop the thematic groups of the category
        for (thmgrp, tgroups) in thmgrps.iteritems():

            # Loop the tags of each taggroup
            for (tgroup, tags) in tgroups.iteritems():



#                print tgroup
#                print tags

                # Transform all to list so they can be treated all the same
                if not isinstance(tags, list):
                    tags = [tags]

                for t in tags:
#                    print t
                    print "---"

                    for (k, v) in t.iteritems():
                        print "%s: %s" % (k, v)


        

