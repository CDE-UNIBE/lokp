# To change this template, choose Tools | Templates
# and open the template in the editor.

import os.path

def locale_profile_directory_path(request):
    """
    Returns the absolute path to the profile .yaml file, based on params _PROFILE_ or
    cookie _PROFILE_
    """

    filepath = os.path.dirname(__file__)

    if '_PROFILE_' in request.params:
        p = "%s/profiles/%s" % (filepath, request.params['_PROFILE_'])
        if os.path.exists(p):
            return p
    elif '_PROFILE_' in request.cookies:
        p = "%s/profiles/%s" % (filepath, request.cookies['_PROFILE_'])
        if os.path.exists(p):
            return p

    return '%s/profiles' % filepath

def profile_directory_path(request=None):
    """
    Returns the absolute path to the directory containing the profiles
    """
    return "%s/profiles/" % os.path.dirname(__file__)
