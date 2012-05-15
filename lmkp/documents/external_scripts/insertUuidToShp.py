#!/usr/bin/env python

from PyQt4.QtCore import QChar
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QUuid
from PyQt4.QtCore import QVariant
from qgis.core import *


# Supply path to your QGIS installation
QgsApplication.setPrefixPath("/usr", True)

# Load providers
QgsApplication.initQgis()

vlayer = QgsVectorLayer("/home/adrian/Documents/ObservatoryLandAcquisitions/Data/deals_with_geom.shp", "landmatrix", "ogr")
if not vlayer.isValid():
    print "Layer failed to load!"

provider = vlayer.dataProvider()

feat = QgsFeature()

fieldIndex = 0
for (i, field) in provider.fields().iteritems():
    if field.name() == "uuid1":
        fieldIndex = i

allAttrs = provider.attributeIndexes()

# start data retreival: fetch geometry and all attributes for each feature
#provider.select([fieldIndex])
provider.select(allAttrs)

caps = provider.capabilities()

# retreive every feature with its geometry and attributes
while provider.nextFeature(feat):

    # fetch map of attributes
    attrs = feat.attributeMap()

    # attrs is a dictionary: key = field index, value = QgsFeatureAttribute
    # show all attributes and their values
    for (k, attr) in attrs.iteritems():
        if k == fieldIndex:
            #if attr.toString() == "":
            if caps & QgsVectorDataProvider.ChangeAttributeValues:
                identifier = QUuid().createUuid().toString()
                # Remove the unwanted brackets
                identifier.remove(QChar('{'), Qt.CaseInsensitive)
                identifier.remove(QChar('}'), Qt.CaseInsensitive)
                print "Newly create UUID: %s" % identifier
                attrs = { fieldIndex : QVariant(identifier)}
                success = provider.changeAttributeValues({ feat.id() : attrs })
                #print success

QgsApplication.exitQgis()
