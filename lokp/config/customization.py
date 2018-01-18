# File names in the locale profile directory
import os

import geojson
import shapely
import yaml
from pyramid.request import Request
from pyramid.testing import DummyRequest

from lokp.utils.views import get_current_profile

APPLICATION_YAML = 'application.yml'
ACTIVITY_YAML = 'activity.yml'
NEW_ACTIVITY_YAML = 'new_activity.yml'
STAKEHOLDER_YAML = 'stakeholder.yml'
NEW_STAKEHOLDER_YAML = 'new_stakeholder.yml'


def get_default_profile(request):
    """
    Return the name of the default profile to be used if no profile was
    specified.

    Return the default profile as set in the application's configuration
    YAML (key ``default_profile``). If no default profile is set in the
    configuration, use ``global`` as default profile.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object.

    Returns:
        ``str``. The default profile as set in the configuration or
        ``global``.
    """
    default_profile = 'global'
    try:
        app_stream = open(
            "%s/%s" % (profile_directory_path(request), APPLICATION_YAML), 'r')
    except IOError:
        return default_profile

    config = yaml.load(app_stream)

    return config.get(
        'application', {}).get('default_profile', default_profile)


def profile_directory_path(request=None):
    """
    Returns the path to the directory containing the profiles
    """
    try:
        profiles_dir = request.registry.settings['lokp.profiles_dir']
    except KeyError:
        raise Exception(
            'No profile directory specified! There is no profile directory '
            '(lokp.profiles_dir) specified in the application''s .ini file!')

    prefix = get_customization_name(request=request)

    # Check if such a folder exists
    profiles_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'customization', prefix,
        'profiles', profiles_dir)
    if not os.path.exists(profiles_path):
        raise Exception(
            'Profile directory not found! The folder for the profile (%s) is '
            'not found. Make sure it is situated at '
            'lokp/customization/%s/profiles/%s.' % (profiles_dir, prefix,
                                                    profiles_dir))

    return profiles_path


def local_profile_directory_path(request):
    """
    Returns the absolute path to the profile .yaml file, based on params
    _PROFILE_ or cookie _PROFILE_
    """

    profiles_dir = request.registry.settings['lokp.profiles_dir']
    prefix = get_customization_name(request=request)

    profiles_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'customization', prefix,
        'profiles', profiles_dir)

    if '_PROFILE_' in request.params:
        p = os.path.join(profiles_path, request.params['_PROFILE_'])
        if os.path.exists(p):
            return p
    elif '_PROFILE_' in request.cookies:
        p = os.path.join(profiles_path, request.cookies['_PROFILE_'])
        if os.path.exists(p):
            return p

    return profiles_path


def get_customization_name(request=None, settings=None):
    """
    Return the name of the customization.

    The customization name is defined in the application's ini file as
    the configuration ``lokp.customization``. A folder with the same
    name needs to exist in ``lokp/customization/``.

    Kwargs:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        which contains a settings dictionary at
        ``request.registry.settings``.
        Either ``request`` or ``settings`` are required.

        ``settings`` (dict): A settings dictionary object.
        Either ``request`` or ``settings`` are required.

    Returns:
        ``str``. The name of the customization.

    Raises:
        ``Exception``. If no customization is specified or if there is
        no folder for the customization.
    """

    if (request and isinstance(request, Request)
            or isinstance(request, DummyRequest)):
        settings = request.registry.settings
    elif not settings or not isinstance(settings, dict):
        raise Exception(
            'You must provide either the request or the settings (dict) '
            'parameters')

    customization = settings.get('lokp.customization')
    if customization is None:
        raise Exception(
            'No customization specified! There is no customization '
            '(lokp.customization) specified in the application''s .ini file!')

    # Check if such a folder exists
    if not os.path.exists(os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'customization',
            customization)):
        raise Exception(
            'Customization folder not found! The folder for the customization '
            '(%s) is not found. Make sure it is situated at '
            'lokp/customization/%s.' % (customization, customization))

    return customization


def get_customized_template_path(request, custom_template_path):
    """
    Get the path to the customized templates.

    It is assumed that the templates are situated in a subfolder
    'templates' of the customization folder, eg. inside:
    ``lokp/customization/{custom}/templates/`` where ``{custom}`` is the
    name of the customization as returned by
    :class:`lokp.customization.get_customization_name`.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object.

        ``custom_template_path`` (str): The relative path to the
        customized template inside the template subfolder of the
        customization folder.

    Returns:
        ``str``. The full path of the customized template which can be
        used by :term:`Pyramid` renderers.
    """
    prefix = get_customization_name(request=request)
    return 'lokp:customization/%s/templates/%s' % (
        prefix, custom_template_path)


def getOverviewKeys(request):
    """
    Return two lists (the first for Activities, the second for Stakeholders)
    with the keys which are to be used in the involvement overview. Because
    these are the keys of the other side, the first one actually contains the
    keys for Stakeholders, the second one the keys for Activities!
    """
    from lokp.config.form import getCategoryList
    return (
        getCategoryList(
            request, 'activities').getInvolvementOverviewKeyNames(),
        getCategoryList(
            request, 'stakeholders').getInvolvementOverviewKeyNames()
    )


def getOverviewRawKeys(request):
    """
    Return two lists (the first for Activities, the second for Stakeholders)
    with the keys which are to be used in the involvement overview. Because
    these are the keys of the other side, the first one actually contains the
    keys for Stakeholders, the second one the keys for Activities!
    These keys are not translated.
    """
    from lokp.config.form import getCategoryList
    return (
        getCategoryList(
            request, 'activities').getInvolvementOverviewRawKeyNames(),
        getCategoryList(
            request, 'stakeholders').getInvolvementOverviewRawKeyNames()
    )


def get_mandatory_keys(request, item, translated=False):
    from lokp.config.form import getCategoryList
    if item == 'a':
        configList = getCategoryList(request, 'activities')
    elif item == 'sh':
        configList = getCategoryList(request, 'stakeholders')
    return configList.getDesiredKeyNames(translated=translated, strict=True)


def getGridColumnKeys(request, itemType):
    """
    Return the keys used for the grid columns in the order specified in the
    configuration yaml.
    It returns an array where each entry contains
    - the original key name (used for ordering the column)
    - the translated key name (for display purposes)
    """
    from lokp.config.form import getCategoryList
    categoryList = getCategoryList(request, itemType)
    keys = []
    for key in sorted(
            categoryList.getGridColumnKeyNames(), key=lambda k: k[2]):
        keys.append([key[0], key[1]])
    return keys


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


def get_spatial_accuracy_map(request):
    """
    Returns a hashmap
    """

    # Get the path of the yaml
    path = local_profile_directory_path(request)

    if os.path.exists(os.path.join(path, APPLICATION_YAML)):
        profile_stream = open(os.path.join(path, APPLICATION_YAML))
        profile_config = yaml.load(profile_stream)

        if 'application' not in profile_config:
            # Not a valid config file
            return None

        if 'spatial_accuracy' in profile_config['application']:
            return profile_config['application']['spatial_accuracy']

    # Spatial accuracy map is not in application.yml
    return None
