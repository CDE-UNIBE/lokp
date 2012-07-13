import os
from PyQt4.QtCore import QRegExp
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import QString

def getTagGroupsConfiguration(filename):
    """
    Configure in an external file the attributes that belong together to a
    taggroup. This configuration file is also used to decide which attributes
    are considered. The file needs to be in the ini format in the following
    form:
    [taggroup1]
    attribute1_name=key1
    attribute2_name=key2

    [taggroup2]
    attribute3_name=key1
    attribute4_name=key2

    etc.

    The ini format has been chosen because Qt has the in-built class QSettings
    to read that format (unlike e.g. YAML)

    """
    settings = QSettings("%s/%s" % (os.path.dirname(__file__), filename), QSettings.IniFormat)

    # Two-dimensional array with taggroups
    groups = []
    # Dictionary that maps the attribute names to LO keys
    transformMap = {}
    # The attribute column in the GIS layer that holds the Uuid
    identifierColumn = None

    # Loop all groups
    for i in settings.childGroups():
        settings.beginGroup(i)
        keys = []
        # Check if the current group defines a taggroup
        if QString(i).contains(QRegExp('taggroup[0-9+]')):
            for j in settings.allKeys():
                keys.append(str(j))
                transformMap[str(j)] = str(settings.value(j).toString())
            # Append the keys to the taggroup
            groups.append(keys)
        # Check if the current group defines general settings
        elif QString(i).contains(QRegExp('settings')):
            for j in settings.allKeys():
                if settings.value(j) == QString('activity_identifier'):
                    identifierColumn = str(j)

        # End this group
        settings.endGroup()

    return identifierColumn, transformMap, groups