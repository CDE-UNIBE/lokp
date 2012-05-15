#!/usr/bin/env python

from qgis.core import *
import simplejson as json


# Supply path to where is your qgis installed
QgsApplication.setPrefixPath("/usr", True)

# Load providers
QgsApplication.initQgis()

# This dict maps the attribute names from the landmatrix input Shapefile to the
# fields defined in the global definition yaml
transformMap = {
    "uuid1": "identifier",
    "Country": "Country",
    "Size of In": "Size of Investement",
    "Year Inves": "Year of Investment (agreed)",
    "Main Crop": "Main Crop",
    "Main Cro_1": "Main Crop",
    "Main Cro_2": "Main Crop",
    "Main Cro_3": "Main Crop",
    "Main Cro_4": "Main Crop",
    "Main Cro_5": "Main Crop",
    "Main Anima": "Main Animal",
    "Main Ani_1": "Main Animal",
    "Main Ani_2": "Main Animal",
    "Main Ani_3": "Main Animal",
    "Mineral 1": "Mineral",
    "Mineral 2": "Mineral",
    "Mineral 3": "Mineral",
    "Mineral 4": "Mineral",
    "Mineral 1": "Mineral",
    "Other Land": "Other Landuse",
    "Other La_1": "Other Landuse",
    "Name of In": "Name of Investor",
    "Name of_1": "Name of Investor",
    "Name of_2": "Name of Investor",
    "Country of": "Country of Investor",
    "Country_1": "Country of Investor",
    "Country_2": "Country of Investor",
    "Domestic P": "Domestic Partners",
    "Data Sourc": "Data Source (Research Paper)",
    "Spatial Accuracy": "Spatial Accuracy"
}

vlayer = QgsVectorLayer("/home/adrian/Documents/ObservatoryLandAcquisitions/Data/deals_with_geom.shp", "landmatrix", "ogr")
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

# Main dict to output
activityDiffObject = {}
activityDiffObject['activities'] = []

# Retreive every feature with its geometry and attributes
while provider.nextFeature(feature):

    # A dict for the current activity
    activityObject = {}
    activityObject['taggroups'] = []

    # Fetch map of attributes
    attrs = feature.attributeMap()

    # Fetch geometry
    geometry = feature.geometry()
    # Write the geometry to GeoJSON format
    if geometry.type() == QGis.Point:
        p = geometry.asPoint()
        geometryObject = {}
        geometryObject['type'] = 'Point'
        geometryObject['coordinates'] = [p.x(), p.y()]
    # Insert the geometry to the activity
    activityObject['geometry'] = geometryObject

    # Loop all attributes
    for (k, attr) in attrs.iteritems():
        # Handle the identifier differently
        if fieldIndexMap[k] == "identifier":
            activityObject['id'] = str(attr.toString())

        # Write all attributes that are not empty or None.
        # It is necessary to add the op property!
        # Each attribute is written to a separate taggroup
        elif attr.toString() != "" and attr is not None:
            #print "%s: %s" % (fieldIndexMap[k], attr.toString())

            taggroupObject = {}
            taggroupObject['tags'] = []
            taggroupObject['tags'].append({"key": fieldIndexMap[k], "value": unicode(attr.toString()), "op": "add"})
            activityObject['taggroups'].append(taggroupObject)

    # Append the activity to the main object
    activityDiffObject['activities'].append(activityObject)

print json.dumps(activityDiffObject, sort_keys=True, indent='    ')