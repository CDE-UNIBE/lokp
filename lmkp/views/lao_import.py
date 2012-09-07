import os.path
import re

from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session
from lmkp.views import shapefile
from pyramid.view import view_config
from sqlalchemy.sql.expression import and_

@view_config(route_name='lao_read_stakeholders', renderer='json')
def lao_read_stakeholders2(request):

    filepath = "%s/documents/laos/data/lc_champasak_attapeu_grouped_4326" % os.path.dirname(os.path.dirname(__file__))

    # This dictionary maps the attribute in the Shapefile to the mandatory and
    # optional fields
    attributeMap = {
        2: 'Name',
        3: 'Country'
    }

    # Map the country names from the input file to the defined countries in the
    # database
    countriesMap = {
    "Hongkong": "China",
    "Korea": "South Korea"
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

        # A dict for the current stakeholder
        stakeholderObject = {}
        stakeholderObject['taggroups'] = []

        # A list to store all already added stakeholders
        knownStakeholders = []

        # Loop all attributes
        for i in [2, 3]:

            # Handle the stakeholder names
            if i == 2:
                # Each attribute is written to a separate taggroup
                if record.record[i].strip() != '':

                    attributeValue = record.record[i]

                    # Check if we already added this stakeholder
                    if attributeValue not in knownStakeholders:

                        stakeholderObject['taggroups'].append(create_taggroup_dict(attributeMap[i], attributeValue))
                        knownStakeholders.append(attributeValue)

            # Handle the stakeholder origin country
            if i == 3:

                attributeValue = record.record[i]
                if attributeValue.strip() != '':

                    # Handle joint venture stakeholders
                    if len(attributeValue.split('-')) > 1:
                        countries = attributeValue.split('-')
                        for c in countries:
                            value = c.strip()

                            if value in countriesMap:
                                value = countriesMap[value]

                            stakeholderObject['taggroups'].append(create_taggroup_dict(attributeMap[i], value))
                    else:

                        value = attributeValue.strip()
                        if value in countriesMap:
                            value = countriesMap[value]

                        stakeholderObject['taggroups'].append(create_taggroup_dict(attributeMap[i], value))

        stakeholderDiffObject['stakeholders'].append(stakeholderObject)


    return stakeholderDiffObject

@view_config(route_name='lao_read_activities', renderer='json')
def lao_read_activities2(request):
    filepath = "%s/documents/laos/data/lc_champasak_attapeu_grouped_4326" % os.path.dirname(os.path.dirname(__file__))

    # This dictionary maps the attribute in the Shapefile to the mandatory and
    # optional fields
    attributeMap = {
        2: 'Name',
        27: 'Contract area (ha)',
        136: 'Intention of Investment', # Product1 needs to be mapped probably
        59: 'Year of agreement'
    }

    shp = shapefile.Reader(filepath)
    records = shp.shapeRecords()

    # Main dict to output
    activityDiffObject = {}
    activityDiffObject['activities'] = []

    # Retreive every feature with its geometry and attributes
    for record in records:

        # A dict for the current stakeholder
        activityObject = {}
        activityObject['taggroups'] = []
        stakeholdersObject = []

        for k in [2, 27, 1, 59]:

            if k == 27:
                activityObject['taggroups'].append(create_taggroup_dict(attributeMap[k], float(record.record[k])))

            if k == 1:
                value = guess_intention(record.record[k])
                activityObject['taggroups'].append(create_taggroup_dict(attributeMap[k], value))

            if k == 59:
                year = 0
                dates = record.record[k].split('/')
                if len(dates) == 3:
                    lastdigits = int(dates[-1])
                    if lastdigits > 20:
                        year = 1900 + lastdigits
                    else:
                        year = 2000 + lastdigits

                activityObject['taggroups'].append(create_taggroup_dict(attributeMap[k], year))
            
            if k == 2:

                investor_name = record.record[k]

                sh = Session.query(Stakeholder).join(SH_Tag_Group).\
                    join(SH_Tag, SH_Tag_Group.id == SH_Tag.fk_sh_tag_group).\
                    join(SH_Key).\
                    join(SH_Value).filter(and_(SH_Key.key == 'Name', SH_Value.value == investor_name)).first()

                stakeholdersObject.append({"id": str(sh.stakeholder_identifier), "op": "add", "role": 6, "version": 1})
                activityObject['stakeholders'] = stakeholdersObject

        activityObject['taggroups'].append(create_taggroup_dict('Country', 'Laos'))
        # Not sure about these sources
        activityObject['taggroups'].append(create_taggroup_dict('Data source', 'Government sources'))
        # Not sure about the negotiation status
        activityObject['taggroups'].append(create_taggroup_dict('Negotiation Status', 'Contract signed'))
        activityObject['taggroups'].append(create_taggroup_dict('Spatial Accuracy', 'very accurate'))

        # Add geometry to activity
        activityObject['geometry'] = {'coordinates': [record.shape.points[0][0], record.shape.points[0][1]], 'type': 'Point'}
        
        activityDiffObject['activities'].append(activityObject)

    return activityDiffObject


def create_tag_dict(key, value):
    return {'key': key, 'op': 'add', 'value': value}


def create_taggroup_dict(key, value):
    taggroup = {}
    taggroup['op'] = 'add'
    taggroup['tags'] = []
    taggroup['tags'].append({"key": key, "value": value, "op": "add"})
    taggroup['main_tag'] = {"key": key, "value": value}
    return taggroup

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
    if re.match(r'.*agro.*|.*coffee.*', value, re.I):
        return "Agriculture"
    if re.match(r'.*acacia.*|.*onion.*', value, re.I):
        return "Agriculture"
    if re.match(r'.*corn.*|.*vegetables.*|.*tree.*', value, re.I):
        return "Agriculture"
    if re.match(r'.*eucalyptus.*|.*goats.*|.*seed.*', value, re.I):
        return "Agriculture"

    if re.match(r'.*tourism.*|.*turi.*|.*hotel.*', value, re.I):
        return "Tourism"

    if re.match(r'.*dam.*|.*ember.*', value, re.I):
        return "Renewable energy"

    if re.match(r'.*port.*|.*funitur.*|.*furnitur.*', value, re.I):
        return "Other"

    if re.match(r'.*clay.*|.*gold.*|.*sand.*', value, re.I):
        return "Mining"

    if re.match(r'.*gas.*|.*sawmill.*|.*additives.*', value, re.I):
        return "Industry"


    return 'Other'