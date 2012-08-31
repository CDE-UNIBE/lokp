# To change this template, choose Tools | Templates
# and open the template in the editor.

import os.path
from os import sep as separator

def locale_profile_directory_path(request):
    """
    Returns the absolute path to the profile .yaml file, based on params _PROFILE_ or
    cookie _PROFILE_
    """

    profiles_dir = request.registry.settings['lmkp.profiles_dir']

    if '_PROFILE_' in request.params:
        p = profiles_dir + separator + request.params['_PROFILE_']
        if os.path.exists(p):
            return p
    elif '_PROFILE_' in request.cookies:
        p = profiles_dir + separator + request.cookies['_PROFILE_']
        if os.path.exists(p):
            return p

    return profiles_dir

def profile_directory_path(request=None):
    """
    Returns the absolute path to the directory containing the profiles
    """
    return request.registry.settings['lmkp.profiles_dir']

def codes_directory_path():
    """
    Returns the absolute path to the directory containing the files for code
    translation
    """
    return "%s/documents/codes" % os.path.dirname(__file__)