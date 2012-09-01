from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session
import psycopg2
from pyramid.view import view_config
import re
from sqlalchemy.sql.expression import and_

@view_config(route_name='lao_read_stakeholders', renderer='json', permission='administer')
def lao_import_stakeholders(request):

    connection = psycopg2.connect("dbname=landconcessions user=stefan password=stefan host=localhost")

    cursor = connection.cursor()

    # Select all relevant stakeholders. Relevant are stakeholders linked to
    # projects in Bokeo and to projects with a georeference
    sh_sql_query = "SELECT data.project.id_company FROM data.geo_point\
    JOIN data.project ON data.geo_point.project_code = data.project.project_code\
    WHERE data.project.project_code ILIKE '05%' GROUP BY data.project.id_company;"

    cursor.execute(sh_sql_query)

    stakeholders = []

    stakeholder = {}
    

    for sh_record in cursor:

        taggroups = []

        single_sh_cursor = connection.cursor()

        # Get the full information for each stakeholder
        single_sh_query = "SELECT data.lut_company.id, data.lut_company.name_eng, data.lut_country.name_eng FROM data.lut_company\
        JOIN data.lut_country ON data.lut_company.id_country = data.lut_country.id\
        WHERE data.lut_company.id = " + str(sh_record[0]) + ";"

        
        single_sh_cursor.execute(single_sh_query)
        try:
            id, name, country = single_sh_cursor.fetchone()

            # Special case lao-china
            if country == 'Lao-China':
                countries = ['Laos', 'China']
                # Init taggroup
                taggroup = {}
                taggroup['op'] = 'add'
                taggroup['tags'] = []
                taggroup['tags'].append({'key': 'origin_db_id', 'op': 'add', 'value': id})
                taggroup['tags'].append({'key': 'Name', 'op': 'add', 'value': name})
                taggroup['tags'].append({'key': 'Country', 'op': 'add', 'value': countries[0]})
                taggroup['main_tag'] = {'key': 'Name', 'op': 'add', 'value': name}
                taggroups.append(taggroup)
                # Init taggroup
                taggroup = {}
                taggroup['op'] = 'add'
                taggroup['tags'] = []
                taggroup['tags'].append({'key': 'Country', 'op': 'add', 'value': countries[1]})
                taggroup['main_tag'] = {'key': 'Country', 'op': 'add', 'value': countries[1]}
                taggroups.append(taggroup)

            else:
                # Init taggroup
                taggroup = {}
                taggroup['op'] = 'add'
                taggroup['tags'] = []
                # Append keys
                taggroup['tags'].append({'key': 'origin_db_id', 'op': 'add', 'value': id})
                taggroup['tags'].append({'key': 'Name', 'op': 'add', 'value': name})
                taggroup['tags'].append({'key': 'Country', 'op': 'add', 'value': country})
                taggroup['main_tag'] = {'key': 'Name', 'op': 'add', 'value': name}
                taggroups.append(taggroup)

            stakeholder = {'taggroups': taggroups}
            stakeholders.append(stakeholder)
                
        except TypeError:
            # In case no stakeholder is found
            pass

    return {"stakeholders": stakeholders}

@view_config(route_name='lao_read_activities', renderer='json', permission='administer')
def lao_import_activities(request):
    activities = []

    connection = psycopg2.connect("dbname=landconcessions user=stefan password=stefan host=localhost")

    cursor = connection.cursor()

    a_sql_query = "SELECT\
    ST_X(ST_Transform(data.geo_point.the_geom,4326)),\
    ST_Y(ST_Transform(data.geo_point.the_geom,4326)),\
    data.project.id,\
    'Laos' AS \"Country\",\
    data.project.name_eng AS \"Name\",\
    data.lut_status.name_eng AS \"Status\",\
    data.project.area_ha_final AS \"Size of Investment\",\
    CASE WHEN data.doc_agreement.sign_date IS NOT NULL THEN to_char(data.doc_agreement.sign_date, 'YYYY') ELSE '0' END AS \"Year of Investment (agreed)\",\
    data.lut_sources.name_eng AS \"Source\",\
    data.lut_subsect.name_eng AS \"Main Crop\",\
    data.lut_company.id AS \"Company id\"\
    FROM data.project\
    JOIN data.geo_point ON data.project.project_code = data.geo_point.project_code\
    JOIN data.lut_status ON data.project.id_status = data.lut_status.id\
    JOIN data.doc_agreement ON data.project.id_doc_agreement = data.doc_agreement.id\
    JOIN data.lut_sources ON data.project.id_sources_status = data.lut_sources.id\
    JOIN data.lut_subsect ON data.project.id_subsect = data.lut_subsect.id\
    JOIN data.lut_company ON data.project.id_company = data.lut_company.id\
    WHERE data.project.project_code ILIKE '05%';"

    cursor.execute(a_sql_query)

    for lon, lat, id, country, name, status, size_of_investment, year_of_investment, source, main_crop, company_id in cursor:
        activity = {}
        activity['geometry'] = {'coordinates': [lon, lat], 'type': 'Point'}

        taggroup = {}
        taggroup['tags'] = []
        taggroup['tags'].append(create_tag_dict('origin_db_id', id))
        taggroup['tags'].append(create_tag_dict('Country', country))
        taggroup['tags'].append(create_tag_dict('Project Status', status))
        taggroup['tags'].append(create_tag_dict('Size of Investment', size_of_investment))
        taggroup['tags'].append(create_tag_dict('Year of Investment (agreed)', int(year_of_investment)))
        taggroup['tags'].append(create_tag_dict('Data Source (Research Paper)', source))
        taggroup['tags'].append(create_tag_dict('Main Crop', main_crop))
        taggroup['op'] = 'add'
        taggroup['main_tag'] = create_tag_dict('Country', country)

        activity['taggroups'] = []
        activity['taggroups'].append(taggroup)

        # The stakeholder link
        try:
            sh = Session.query(Stakeholder).join(SH_Tag_Group).\
            join(SH_Tag, SH_Tag_Group.id == SH_Tag.fk_sh_tag_group).\
            join(SH_Key).\
            join(SH_Value).filter(and_(SH_Key.key == 'origin_db_id', SH_Value.value == str(company_id))).first()

            stakeholders = []
            stakeholders.append({
                                "id": str(sh.stakeholder_identifier),
                                "op": "add",
                                "role": 6,
                                "version": 1
                                })

            activity['stakeholders'] = stakeholders

        except AttributeError:
            # No stakeholder is found
            pass

        activities.append(activity)

    return {'activities': activities}

def create_tag_dict(key, value):
    return {'key': key, 'op': 'add', 'value': value}

@view_config(route_name='cambodia_read_activities', renderer='json', permission='administer')
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

@view_config(route_name='cambodia_read_stakeholders', renderer='json', permission='administer')
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

def regex_name(value):
    value = re.sub(r'\ \(Region [IV]*\)$', '', value)
    value = re.sub(r'\ Region \([0-9]*\)$', '', value)
    value = re.sub(r'\ [IV]*$', '', value)

    return value