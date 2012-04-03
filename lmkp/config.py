# To change this template, choose Tools | Templates
# and open the template in the editor.

import os.path

def config_file_path(request=None):
    """
    Returns the absolute path to the global.yaml file
    """
    return "%s/profiles/global.yml" % os.path.dirname(__file__)

def locale_config_file_path(request):
    """
    Returns the absolute path to the profile .yaml file, based on params _PROFILE_ or
    cookie _PROFILE_
    """
    
    if '_PROFILE_' in request.params:
        return "%s/profiles/%s.yml" % (os.path.dirname(__file__), request.params['_PROFILE_'])
    if '_PROFILE_' in request.cookies:
        return "%s/profiles/%s.yml" % (os.path.dirname(__file__), request.cookies['_PROFILE_'])
    else:
        return ''

def profile_directory_path(request=None):
    """
    Returns the absolute path to the directory containing the profiles
    """
    return "%s/profiles/" % os.path.dirname(__file__)