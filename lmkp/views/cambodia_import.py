import os.path
import re
from numbers import Number
from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session
from lmkp.views import shapefile
from pyramid.view import view_config
from sqlalchemy.sql.expression import and_

@view_config(route_name='cambodia_read_stakeholders', renderer='json')
def cambodia_read_stakeholders2(request):

    filepath = "%s/documents/cambodia/data/Government_Data_Complete_4326_points2" % os.path.dirname(os.path.dirname(__file__))

    # This dictionary maps the attribute in the Shapefile to the mandatory and
    # optional fields
    attributeMap = {
        10: 'Name',
        8: 'Country of origin',
        3: 'Address'
    }

    # Map the country names from the input file to the defined countries in the
    # database
    countriesMap = {
    "American": "United States",
    "Cambodia": "Cambodia",
    "Cambodian": "Cambodia",
    "chinese": "China",
    "Chinese": "China",
    "India": "India",
    "Indian": "India",
    "Israeli": "Israel",
    "Korean": "South Korea",
    "Malaysian": "Malaysia",
    "Taiwanese": "Taiwan",
    "Thai": "Thailand",
    "Vietnam": "Vietnam",
    "Vietnamese": "Vietnam"
    }


    shp = shapefile.Reader(filepath)
    records = shp.shapeRecords()


    # Main dict to output
    stakeholderDiffObject = {}
    stakeholderDiffObject['stakeholders'] = []

    # List of already considered stakeholders (name)
    knownStakeholders = []

    # Retreive every feature with its geometry and attributes
    for record in records:
        #if record.record[2].strip() != '' and record.record[2] is not None:
        #    pass

        # A dict for the current stakeholder
        stakeholderObject = {}
        stakeholderObject['taggroups'] = []

        # Loop all attributes
        for i in [10, 8, 3]:

            tagGroup = {}
            tagGroup['tags'] = []

            # Write all attributes that are not empty or None.
            # It is necessary to add the op property!
            # Each attribute is written to a separate taggroup
            if record.record[i].strip() != "":

                # Get the value
                value = unicode(record.record[i])
                # Check if the value has to be looked up
                if attributeMap[i] == 'Name':
                    value = regex_name(value)
                    stakeholderName = value

                if attributeMap[i] == 'Country of origin':
                    value = countriesMap[value]

                tagGroup['tags'].append({"key": attributeMap[i], "value": value, "op": "add"})
                tagGroup['op'] = 'add'
                tagGroup['main_tag'] = {"key": attributeMap[i], "value": value}

                stakeholderObject['taggroups'].append(tagGroup)


        if stakeholderName not in knownStakeholders:
            # Append the stakeholder to the main object
            stakeholderDiffObject['stakeholders'].append(stakeholderObject)
            knownStakeholders.append(stakeholderName)

    return stakeholderDiffObject

@view_config(route_name='cambodia_read_activities', renderer='json')
def cambodia_read_activities2(request):
    filepath = "%s/documents/cambodia/data/Government_Data_Complete_4326_points2" % os.path.dirname(os.path.dirname(__file__))

    # This dictionary maps the attribute in the Shapefile to the mandatory and
    # optional fields
    attributeMap = {
        0: 'Intended area (ha)',
        5: 'Intention of Investment',
#        7: 'Year of agreement',
        10: 'Investor',
        13: 'Negotiation Status',
    }

    shp = shapefile.Reader(filepath)
    records = shp.shapeRecords()

    # Main dict to output
    activityDiffObject = {}
    activityDiffObject['activities'] = []

    # List of already used stakeholders
    usedStakeholders = []

    # Retreive every feature with its geometry and attributes
    for record in records:

        # A dict for the current stakeholder
        activityObject = {}
        activityObject['taggroups'] = []
        stakeholdersObject = []

        # Loop all attributes
        for k in [0, 5, 7, 10, 13]:


            if k == 13:
                taggroup = {}
                taggroup['tags'] = []
                taggroup['op'] = "add"

                if record.record[k].strip() == '':
                    taggroup['tags'].append({'key': attributeMap[k], 'op': "add", 'value': 'Contract signed'})
                    taggroup['main_tag'] = {'key': attributeMap[k], 'value': record.record[k][0]}
                else:
                    taggroup['tags'].append({'key': attributeMap[k], 'op': "add", 'value': 'Contract cancelled'})
                    taggroup['main_tag'] = {'key': attributeMap[k], 'value': record.record[k][0]}

                activityObject['taggroups'].append(taggroup)


#            elif type(record.record[k]) == type(list()):
#                if k == 7:
#                    taggroup = {}
#                    taggroup['tags'] = []
#                    taggroup['op'] = "add"
#                    taggroup['tags'].append({'key': attributeMap[k], 'op': "add", 'value': record.record[k][0]})
#                    taggroup['main_tag'] = {'key': attributeMap[k], 'value': record.record[k][0]}
#                    activityObject['taggroups'].append(taggroup)


            # Write all attributes that are not empty or None.
            # It is necessary to add the op property!
            # Each attribute is written to a separate taggroup
            elif isinstance(record.record[k], basestring) and record.record[k].strip() != '':


                if k == 5:
                    taggroup = {}
                    taggroup['tags'] = []
                    taggroup['op'] = "add"
                    value = guess_intention(record.record[k])
                    taggroup['tags'].append({'key': attributeMap[k], 'op': "add", 'value': value})
                    taggroup['main_tag'] = {'key': attributeMap[k], 'value': value}
                    activityObject['taggroups'].append(taggroup)

#                if k == 7:
#                    taggroup = {}
#                    taggroup['tags'] = []
#                    taggroup['op'] = "add"
#                    taggroup['tags'].append({'key': attributeMap[k], 'op': "add", 'value': int(record.record[k].split('/')[0])})
#                    taggroup['main_tag'] = {'key': attributeMap[k], 'value': int(record.record[k].split('/')[0])}
#                    activityObject['taggroups'].append(taggroup)

                if k == 10:
                    investor_name = regex_name(record.record[k])

                    sh = Session.query(Stakeholder).join(SH_Tag_Group).\
                        join(SH_Tag, SH_Tag_Group.id == SH_Tag.fk_sh_tag_group).\
                        join(SH_Key).\
                        join(SH_Value).filter(and_(SH_Key.key == 'Name', SH_Value.value == investor_name)).first()

                    if sh is not None:
                        previous_version = usedStakeholders.count(str(sh.stakeholder_identifier))

                        # TODO: For the moment, add the same stakeholder only
                        # once because it crashes otherwise (Changeset issue).
                        if previous_version == 0:

                            stakeholdersObject.append({"id": str(sh.stakeholder_identifier), "op": "add", "role": 6, "version": (previous_version + 1)})

                            usedStakeholders.append(str(sh.stakeholder_identifier))


            elif isinstance(record.record[k], Number):

                taggroup = {}
                taggroup['tags'] = []
                taggroup['op'] = "add"

                taggroup['tags'].append({'key': attributeMap[k], 'op': "add", 'value': record.record[k]})
                taggroup['main_tag'] = {'key': attributeMap[k], 'value': record.record[k]}
                activityObject['taggroups'].append(taggroup)

        taggroup = {}
        taggroup['tags'] = []
        taggroup['op'] = "add"
        taggroup['tags'].append({'key': 'Country', 'op': "add", 'value': 'Cambodia'})
        taggroup['main_tag'] = {'key': 'Country', 'value': 'Cambodia'}
        activityObject['taggroups'].append(taggroup)

        taggroup = {}
        taggroup['tags'] = []
        taggroup['op'] = "add"
        taggroup['tags'].append({'key': 'Data source', 'op': "add", 'value': 'Government sources'})
        taggroup['main_tag'] = {'key': 'Data source', 'value': 'Government sources'}
        activityObject['taggroups'].append(taggroup)

        # Add the missing mandatory key: Spatial accuracy
        activityObject['taggroups'].append(create_taggroup_dict('Spatial Accuracy', '100m to 1km'))

        # Add the geometry

        activityObject['geometry'] = {'coordinates': [record.shape.points[0][0], record.shape.points[0][1]], 'type': 'Point'}

        activityObject['stakeholders'] = stakeholdersObject
        # Append the stakeholder to the main object
        activityDiffObject['activities'].append(activityObject)

    return activityDiffObject

def create_taggroup_dict(key, value):
    taggroup = {}
    taggroup['op'] = 'add'
    taggroup['tags'] = []
    taggroup['tags'].append({"key": key, "value": value, "op": "add"})
    taggroup['main_tag'] = {"key": key, "value": value}
    return taggroup

def regex_name(value):
    value = re.sub(r'\ \(Region [IV]*\)$', '', value)
    value = re.sub(r'\ Region \([0-9]*\)$', '', value)
    value = re.sub(r'\ [IV]*$', '', value)

    return value

def guess_intention(value):

    """
      - Agriculture
      - Forestry
      - Mining
      - Tourism
      - Industry
      - Conservation
      - Renewable energy
      - Other
    """

    if re.match(r'.*oil.*|.*rubber.*|.*cassava.*|.*shrimp.*|.*tapioca.*|.*sugar.*|.*tree.*|.*plantation.*', value, re.I):
        return "Agriculture"
    if re.match(r'.*agro.*', value, re.I):
        return "Agriculture"
    if re.match(r'.*acacia.*', value, re.I):
        return "Agriculture"
    if re.match(r'.*corn.*', value, re.I):
        return "Agriculture"

    if re.match(r'.*tourism.*|.*turi.*', value, re.I):
        return "Tourism"

    if re.match(r'.*dam.*', value, re.I):
        return "Renewable energy"

    if re.match(r'.*port.*', value, re.I):
        return "Other"


    return "Other"