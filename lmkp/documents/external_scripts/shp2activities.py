#!/usr/bin/env python

from PyQt4.QtCore import QFile
from PyQt4.QtCore import QIODevice
from PyQt4.QtCore import QRegExp
from PyQt4.QtCore import QString
from qgis.core import *
import simplejson as json
import string

def createMap(filename):
    """
    Creates a Python dictionary from a CSV file. The CSV file must be semicolon
    separated (";") and must not contain quotes.
    """

    # Open the CSV file
    file = QFile( "%s/%s" % (basedir,filename))
    file.open(QIODevice.OpenMode(QIODevice.ReadOnly))

    map = {}

    # Read all lines
    while True:
        qByteArray = file.readLine()
        # Break the while loop when the end is reached
        if qByteArray.size() == 0:
            break
        # Remove the trailing end line
        line = QString(qByteArray).remove(QRegExp("\n"))
        # Split the line
        list = line.split(";")
        # Set the key and value to the map
        map[str(list[0].toUpper().toUtf8())] = str(list[1].toUtf8())

    return map


# Supply path to where is your qgis installed
QgsApplication.setPrefixPath("/usr", True)

# Load providers
QgsApplication.initQgis()

# Base directory to the data. The scripts assumes that the Shapefile and all
# CSV files are within the same directory
basedir = "/home/adrian/Documents/ObservatoryLandAcquisitions/Data/"

countriesMap = createMap('countries.csv')
maincropsMap = createMap('maincrops.csv')
mainanimalsMap = createMap('mainanimals.csv')
mineralsMap = createMap('minerals.csv')
otherlandusesMap = createMap('otherlanduses.csv')

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

vlayer = QgsVectorLayer("%s/deals_with_geom.shp" % basedir, "landmatrix", "ogr")
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

            # Get the value
            value = unicode(attr.toString())
            # Check if the value has to be looked up
            if fieldIndexMap[k] in ['Country','Country of Investor']:
                value = countriesMap[string.upper(value)]
            elif fieldIndexMap[k] in ['Main Crop']:
                value = maincropsMap[string.upper(value)]
            elif fieldIndexMap[k] in ['Main Animal']:
                value = mainanimalsMap[string.upper(value)]
            elif fieldIndexMap[k] in ['Mineral']:
                value = mineralsMap[string.upper(value)]
            elif fieldIndexMap[k] in ['Other Landuse']:
                value = otherlandusesMap[string.upper(value)]
            
            taggroupObject['tags'].append({"key": fieldIndexMap[k], "value": value, "op": "add"})
            activityObject['taggroups'].append(taggroupObject)

    # Append the activity to the main object
    activityDiffObject['activities'].append(activityObject)

print json.dumps(activityDiffObject, sort_keys=True, indent='    ')