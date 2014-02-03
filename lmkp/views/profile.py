from lmkp.config import profile_directory_path
from lmkp.config import locale_profile_directory_path
import os
from pyramid.view import view_config
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

def get_current_locale(request):

    if '_LOCALE_' in request.params:
        return request.params['_LOCALE_']
    if '_LOCALE_' in request.cookies:
        return request.cookies['_LOCALE_']

    return 'en'

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

    # Get the path of the yaml
    path = locale_profile_directory_path(request)

    if os.path.exists(os.path.join(path, APPLICATION_YAML)):
        profile_stream = open(os.path.join(path, APPLICATION_YAML))
        profile_config = yaml.load(profile_stream)

        if 'application' not in profile_config:
            # Not a valid config file
            return 'null'

        if 'geometry' in profile_config['application']:
            return profile_config['application']['geometry']

    # No local or global file found
    return 'null'

def get_spatial_accuracy_map(request):
    """
    Returns a hashmap
    """

    # Get the path of the yaml
    path = locale_profile_directory_path(request)

    if os.path.exists(os.path.join(path, APPLICATION_YAML)):
        profile_stream = open(os.path.join(path, APPLICATION_YAML))
        profile_config = yaml.load(profile_stream)

        if 'application' not in profile_config:
            # Not a valid config file
            return None

        if 'spatial_accuracy' in profile_config['application']:
            map = profile_config['application']['spatial_accuracy']

            """
            # Translate the spatial accuracy map ...
            # This is the SQL query that needs to be written:
            # SELECT loc.value, eng.value FROM
            # (SELECT * FROM data.a_values WHERE fk_language = (SELECT id FROM data.languages WHERE locale = 'fr' LIMIT 1)) AS loc JOIN
            # (SELECT * FROM data.a_values WHERE fk_language = 1 AND "value" IN ('1km to 10km', 'better than 100m')) AS eng
            # ON loc.fk_a_value = eng.id
            localizer = get_localizer(request)
            
            locale = localizer.locale_name

            fk_lang, = DBSession.query(Language.id).filter(Language.locale == locale).first()

            loc_query = DBSession.query(A_Value.id.label("loc_id"),
                                        A_Value.value.label("loc_value"),
                                        A_Value.fk_a_value.label("loc_fk_a_value")).filter(A_Value.fk_language == fk_lang).subquery("loc")

            eng_query = DBSession.query(A_Value.id.label("eng_id"),
                                        A_Value.value.label("eng_value")).\
                                        filter(A_Value.fk_language == 1).\
                                        filter(A_Value.value.in_(map.keys())).subquery("eng")

            join_query = DBSession.query(loc_query, eng_query).filter(loc_query.c.loc_fk_a_value == eng_query.c.eng_id).subquery("join_tables")

            query = DBSession.query(join_query.c.eng_value, join_query.c.loc_value)

            values_map = {}
            for english, translated in query.all():
                values_map[english] = translated

            translated_map = {}
            for k, v in map.items():
                translated_map[values_map[k]] = v"""

            return map

    # Spatial accuracy map is not in application.yml
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

