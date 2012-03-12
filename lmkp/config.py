# To change this template, choose Tools | Templates
# and open the template in the editor.

import os.path

from pyramid.i18n import get_localizer

def config_file_path(request=None):
    """
    Returns the absolute path to the config.yaml file
    """
    return "%s/config.yml" % os.path.dirname(__file__)

def locale_config_file_path(request):
    """
    Returns the absolute path to the localized config.yaml file
    """

    # Get the localizer
    localizer = get_localizer(request)

    return "%s/locale/%s/LC_CONFIG/config.yml" % (os.path.dirname(__file__), localizer.locale_name)