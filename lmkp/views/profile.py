import fnmatch
from lmkp.config import profile_directory_path
import os
from pyramid.view import view_config
import re
import yaml
from lmkp.models.meta import DBSession
from lmkp.models.database_objects import Profile
import geojson
import shapely

APPLICATION_YAML = 'application.yml'

def get_current_profile(request):

    if '_PROFILE_' in request.params:
        return request.params['_PROFILE_']
    if '_PROFILE_' in request.cookies:
        return request.cookies['_PROFILE_']

    return 'global'

@view_config(route_name='profile_store', renderer='json')
def profile_store(request):
    """
    Return a JSON representation (can be used to build an Ext Store) of all
    available profiles.
    In order to appear in this list, a profile needs to be a valid YAML (.yml)
    file located in /profiles and it must contain an attribute "name".
    Furthermore, the profile must be listed in the database. To do this, add its
    keys and values to the database:
    - config/add/activities?_PROFILE_=XXX
    - config/add_stakeholders?_PROFILE_=XXX
    This needs to be done even if profile does not contain any additional keys
    compared to global config files.
    """

    ret = {'success': False}
    data = []

    profiles_db = DBSession.query(Profile)
    for p in profiles_db.all():

        if p.code == 'global':
            # Always insert global on top
            profile = _processProfile(request, p, True)
            if profile is not None:
                data.insert(0, profile)
        else:
            profile = _processProfile(request, p)
            if profile is not None:
                data.append(profile)

    if len(data) > 0:
        ret['data'] = data
        ret['total'] = len(data)
        ret['success'] = True

    return ret

def _getCurrentProfileExtent(request):
    """
    Get the extent from current profile. Get it from YAML, which saves a
    database query
    """

#    from pyramid.renderers import render
#    return render('javascript', 'basdfasdf', request)
    current_profile = get_current_profile(request)

    path = APPLICATION_YAML
    if current_profile != 'global':
        path = "%s/%s" % (current_profile, APPLICATION_YAML)

    try:
        profile_stream = open("%s/%s" % (profile_directory_path(request),
            path), 'r')
        profile_config = yaml.load(profile_stream)

        if 'application' not in profile_config:
            # Not a valid config file
            return None

        if 'geometry' in profile_config['application']:
            return profile_config['application']['geometry']

    except IOError:
        # File not found
        pass

    return None

def _processProfile(request, dbProfile, isGlobal=False):

    yaml_file = APPLICATION_YAML
    if isGlobal is False:
        yaml_file = "%s/%s" % (dbProfile.code, APPLICATION_YAML)

    if isGlobal is False:
        pass

    # Try to find and open profile config file
    try:
        profile_stream = open("%s/%s" % (profile_directory_path(request),
            yaml_file), 'r')
        profile_config = yaml.load(profile_stream)

        if 'application' not in profile_config:
            # Not a valid config file
            return None

        app_config = profile_config['application']

        # Collect values
        code = dbProfile.code
        name = app_config['name'] if 'name' in app_config else 'Unknown'
        active = get_current_profile(request) == dbProfile.code
        geometry = None
        if dbProfile.geometry is not None:
            geometry = geojson.loads(geojson.dumps(shapely.wkb.loads(
                str(dbProfile.geometry.geom_wkb)
            )))

        return {
            'name': name,
            'profile': code,
            'geometry': geometry,
            'active': active
        }

    except IOError:
        # File not found
        return None

