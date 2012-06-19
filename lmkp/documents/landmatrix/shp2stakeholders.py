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
basedir = "/home/adrian/Documents/LandObservatory/Matrix/Data"

countriesMap = createMap('countries.csv')

# This dict maps the attribute names from the landmatrix input Shapefile to the
# fields defined in the global definition yaml
transformMap = {
    "Name of In": "Name",
    "Name of_1": "Name",
    "Name of_2": "Name",
    "Country of": "Country",
    "Country_1": "Country",
    "Country_2": "Country",
    "Domestic P": "Domestic Partner",
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
stakeholderDiffObject = {}
stakeholderDiffObject['stakeholders'] = []

# Retreive every feature with its geometry and attributes
while provider.nextFeature(feature):

    # A dict for the current stakeholder
    stakeholderObject = {}
    stakeholderObject['taggroups'] = []

    # Fetch map of attributes
    attrs = feature.attributeMap()

    # Loop all attributes
    for (k, attr) in attrs.iteritems():
        # Handle the identifier differently
        if fieldIndexMap[k] == "identifier":
            stakeholderObject['id'] = str(attr.toString())

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

            taggroupObject['tags'].append({"key": fieldIndexMap[k], "value": value, "op": "add"})
            taggroupObject['op'] = 'add'
            taggroupObject['main_tag'] = {"key": fieldIndexMap[k], "value": value}
            stakeholderObject['taggroups'].append(taggroupObject)

    # Append the stakeholder to the main object
    stakeholderDiffObject['stakeholders'].append(stakeholderObject)

print json.dumps(stakeholderDiffObject, sort_keys=True, indent='    ')

QgsApplication.exitQgis()