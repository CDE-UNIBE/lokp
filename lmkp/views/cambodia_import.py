import os.path
import re
from numbers import Number
from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session
from lmkp.views import shapefile
import psycopg2
from pyramid.view import view_config
from sqlalchemy.sql.expression import and_

def cambodia_read_activities(request):
    import sys

    sys.path.append('/usr/lib/python2.7/dist-packages')

    from qgis.core import QgsApplication
    from qgis.core import QgsCoordinateReferenceSystem
    from qgis.core import QgsFeature
    from qgis.core import QgsCoordinateTransform
    from qgis.core import QgsVectorLayer
    import simplejson as json

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

    transformMap = {
    "Purpose": "Main Crop",
    "Cancelled": "Project Status",
    "Name": "Investor"
    }

    # Supply path to where is your qgis installed
    QgsApplication.setPrefixPath("/usr", True)

    # Load providers
    QgsApplication.initQgis()

    # Base directory to the data. The scripts assumes that the Shapefile and all
    # CSV files are within the same directory
    basedir = "/home/adrian/Data/Cambodia/OpenDevelopmentCambodia/economic_land_concessions"

    vlayer = QgsVectorLayer("%s/Government_Data_Complete.shp" % basedir, "landmatrix", "ogr")
    if not vlayer.isValid():
        print "Layer failed to load!"

    provider = vlayer.dataProvider()

    feature = QgsFeature()

    # List of attribute indexes to select
    attributeIndexes = []
    # Dict that maps the field index to the fields defined in the global YAML
    fieldIndexMap = {}
    for (i, field) in provider.fields().iteritems():
        if str(field.name()) in transformMap:
            attributeIndexes.append(i)
            fieldIndexMap[i] = transformMap[str(field.name())]

    # Start data retreival: fetch geometry and all attributes for each feature
    provider.select(attributeIndexes)

    caps = provider.capabilities()

    src_crs = QgsCoordinateReferenceSystem(32648, QgsCoordinateReferenceSystem.EpsgCrsId)
    dst_crs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
    crs_transform = QgsCoordinateTransform(src_crs, dst_crs)

    # Main dict to output
    activityDiffObject = {}
    activityDiffObject['activities'] = []

    # Retreive every feature with its geometry and attributes
    while provider.nextFeature(feature):

        # A dict for the current stakeholder
        activityObject = {}
        activityObject['taggroups'] = []
        stakeholdersObject = []

        # Fetch map of attributes
        attrs = feature.attributeMap()

        tagGroups = list({'tags': []} for i in range(1))

        # Loop all attributes
        for (k, attr) in attrs.iteritems():

            # Write all attributes that are not empty or None.
            # It is necessary to add the op property!
            # Each attribute is written to a separate taggroup
            if fieldIndexMap[k] == 'Project Status':
                if attr.toString() != "" or attr is not None:
                    tagGroups[0]['tags'].append({"key": "Project Status", "value": "Cancelled", "op": "add"})
                else:
                    tagGroups[0]['tags'].append({"key": "Project Status", "value": "Operational", "op": "add"})

            elif fieldIndexMap[k] == 'Investor':

                investor_name = regex_name(str(attr.toString()))

                sh = Session.query(Stakeholder).join(SH_Tag_Group).\
                    join(SH_Tag, SH_Tag_Group.id == SH_Tag.fk_sh_tag_group).\
                    join(SH_Key).\
                    join(SH_Value).filter(and_(SH_Key.key == 'Name', SH_Value.value == investor_name)).first()
                stakeholdersObject.append({"id": str(sh.stakeholder_identifier), "op": "add", "role": 6, "version": 1})

            elif attr.toString() != "" and attr is not None:
                #print "%s: %s" % (fieldIndexMap[k], attr.toString())

                # First search the correct taggroup to append
                attributeName = provider.fields()[k].name()

                # Get the value
                value = unicode(attr.toString())
                # Check if the value has to be looked up
                if fieldIndexMap[k] in ['Country', 'Country of Investor']:
                    value = countriesMap[value]

                tagGroups[0]['tags'].append({"key": fieldIndexMap[k], "value": value, "op": "add"})
                tagGroups[0]['op'] = 'add'
                if fieldIndexMap[k] == 'Main Crop':
                    tagGroups[0]['main_tag'] = {"key": fieldIndexMap[k], "value": value}

        # Add general tags just to satisfy the yml
        tagGroups[0]['tags'].append({"key": "Year of Investment (agreed)", "value": 0, "op": "add"})
        tagGroups[0]['tags'].append({"key": "Size of Investment", "value": int(feature.geometry().area() / 10000), "op": "add"})
        tagGroups[0]['tags'].append({"key": "Country", "value": "Cambodia", "op": "add"})

        for tg in tagGroups:
            if len(tg['tags']) > 0:
                activityObject['taggroups'].append(tg)

        # Handle the geometry:
        centroid = feature.geometry().centroid().asPoint()
        g = crs_transform.transform(centroid)
        activityObject['geometry'] = {"coordinates": [g.x(), g.y()], "type": "Point"}

        activityObject['stakeholders'] = stakeholdersObject
        # Append the stakeholder to the main object
        activityDiffObject['activities'].append(activityObject)

    QgsApplication.exitQgis()

    return activityDiffObject

#@view_config(route_name='cambodia_read_stakeholders', renderer='json', permission='administer')
def cambodia_read_stakeholders(request):
    import sys

    sys.path.append('/usr/lib/python2.7/dist-packages')

    from qgis.core import QgsApplication
    from qgis.core import QgsFeature
    from qgis.core import QgsVectorLayer
    import simplejson as json

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

    transformMap = {
    "Name": "Name",
    "Nation": "Country"
    }

    # Supply path to where is your qgis installed
    QgsApplication.setPrefixPath("/usr", True)

    # Load providers
    QgsApplication.initQgis()

    # Base directory to the data. The scripts assumes that the Shapefile and all
    # CSV files are within the same directory
    basedir = "/home/adrian/Data/Cambodia/OpenDevelopmentCambodia/economic_land_concessions"

    vlayer = QgsVectorLayer("%s/Government_Data_Complete.shp" % basedir, "landmatrix", "ogr")
    if not vlayer.isValid():
        print "Layer failed to load!"

    provider = vlayer.dataProvider()

    feature = QgsFeature()

    # List of attribute indexes to select
    attributeIndexes = []
    # Dict that maps the field index to the fields defined in the global YAML
    fieldIndexMap = {}
    for (i, field) in provider.fields().iteritems():
        if str(field.name()) in transformMap:
            attributeIndexes.append(i)
            fieldIndexMap[i] = transformMap[str(field.name())]

    # Start data retreival: fetch geometry and all attributes for each feature
    provider.select(attributeIndexes)

    # Main dict to output
    stakeholderDiffObject = {}
    stakeholderDiffObject['stakeholders'] = []

    # List of already considered stakeholders (name)
    knownStakeholders = []

    # Retreive every feature with its geometry and attributes
    while provider.nextFeature(feature):

        # A dict for the current stakeholder
        stakeholderObject = {}
        stakeholderObject['taggroups'] = []

        # Fetch map of attributes
        attrs = feature.attributeMap()

        tagGroups = list({'tags': []} for i in range(1))

        # Loop all attributes
        for (k, attr) in attrs.iteritems():

            # Write all attributes that are not empty or None.
            # It is necessary to add the op property!
            # Each attribute is written to a separate taggroup
            if attr.toString() != "" and attr is not None:
                #print "%s: %s" % (fieldIndexMap[k], attr.toString())

                # Get the value
                value = unicode(attr.toString())
                # Check if the value has to be looked up
                if fieldIndexMap[k] == 'Name':
                    value = regex_name(value)
                    stakeholderName = value

                if fieldIndexMap[k] in ['Country', 'Country of Investor']:
                    value = countriesMap[value]

                tagGroups[0]['tags'].append({"key": fieldIndexMap[k], "value": value, "op": "add"})
                tagGroups[0]['op'] = 'add'
                tagGroups[0]['main_tag'] = {"key": fieldIndexMap[k], "value": value}

        for tg in tagGroups:
            if len(tg['tags']) > 0:
                stakeholderObject['taggroups'].append(tg)

        if stakeholderName not in knownStakeholders:
            # Append the stakeholder to the main object
            stakeholderDiffObject['stakeholders'].append(stakeholderObject)
            knownStakeholders.append(stakeholderName)

    QgsApplication.exitQgis()

    return stakeholderDiffObject

@view_config(route_name='cambodia_read_stakeholders', renderer='json')
def cambodia_read_stakeholders2(request):

    filepath = "%s/documents/cambodia/data/Government_Data_Complete_4326_points2" % os.path.dirname(os.path.dirname(__file__))

    # This dictionary maps the attribute in the Shapefile to the mandatory and
    # optional fields
    attributeMap = {
        10: 'Name',
        8: 'Country',
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

                if attributeMap[i] == 'Country':
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
        0: 'Contract area (ha)',
        5: 'Intention of Investment',
        7: 'Year of agreement',
        10: 'Investor',
        13: 'Negotiation Status',
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


            elif type(record.record[k]) == type(list()):
                if k == 7:
                    taggroup = {}
                    taggroup['tags'] = []
                    taggroup['op'] = "add"
                    taggroup['tags'].append({'key': attributeMap[k], 'op': "add", 'value': record.record[k][0]})
                    taggroup['main_tag'] = {'key': attributeMap[k], 'value': record.record[k][0]}
                    activityObject['taggroups'].append(taggroup)


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

                if k == 7:
                    taggroup = {}
                    taggroup['tags'] = []
                    taggroup['op'] = "add"
                    taggroup['tags'].append({'key': attributeMap[k], 'op': "add", 'value': int(record.record[k].split('/')[0])})
                    taggroup['main_tag'] = {'key': attributeMap[k], 'value': int(record.record[k].split('/')[0])}
                    activityObject['taggroups'].append(taggroup)

                if k == 10:
                    investor_name = regex_name(record.record[k])

                    sh = Session.query(Stakeholder).join(SH_Tag_Group).\
                        join(SH_Tag, SH_Tag_Group.id == SH_Tag.fk_sh_tag_group).\
                        join(SH_Key).\
                        join(SH_Value).filter(and_(SH_Key.key == 'Name', SH_Value.value == investor_name)).first()
                    stakeholdersObject.append({"id": str(sh.stakeholder_identifier), "op": "add", "role": 6, "version": 1})


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

        # Add the geometry

        activityObject['geometry'] = {'coordinates': [record.shape.points[0][0], record.shape.points[0][1]], 'type': 'Point'}

        activityObject['stakeholders'] = stakeholdersObject
        # Append the stakeholder to the main object
        activityDiffObject['activities'].append(activityObject)

    return activityDiffObject

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
    if re.match(r'.*corn.*', value, re.I):
        return "Agriculture"

    if re.match(r'.*tourism.*|.*turi.*', value, re.I):
        return "Tourism"

    if re.match(r'.*dam.*', value, re.I):
        return "Renewable energy"

    if re.match(r'.*port.*', value, re.I):
        return "Other"


    return value