import mimetypes
import os.path
import re
from pyramid.request import Request
from pyramid.testing import DummyRequest


def locale_profile_directory_path(request):
    """
    Returns the absolute path to the profile .yaml file, based on params
    _PROFILE_ or cookie _PROFILE_
    """

    profiles_dir = request.registry.settings['lmkp.profiles_dir']
    prefix = getCustomizationName(request)

    profiles_path = os.path.join(
        os.path.dirname(__file__), 'customization', prefix, 'profiles',
        profiles_dir)

    if '_PROFILE_' in request.params:
        p = os.path.join(profiles_path, request.params['_PROFILE_'])
        if os.path.exists(p):
            return p
    elif '_PROFILE_' in request.cookies:
        p = os.path.join(profiles_path, request.cookies['_PROFILE_'])
        if os.path.exists(p):
            return p

    return profiles_path


def profile_directory_path(request=None):
    """
    Returns the path to the directory containing the profiles
    """
    try:
        profiles_dir = request.registry.settings['lmkp.profiles_dir']
    except KeyError:
        raise Exception(
            'No profile directory specified! There is no profile directory '
            '(lmkp.profiles_dir) specified in the application''s .ini file!')

    prefix = getCustomizationName(request)

    # Check if such a folder exists
    profiles_path = os.path.join(
        os.path.dirname(__file__), 'customization', prefix, 'profiles',
        profiles_dir)
    if not os.path.exists(profiles_path):
        raise Exception(
            'Profile directory not found! The folder for the profile (%s) is '
            'not found. Make sure it is situated at '
            'lmkp/customization/%s/profiles/%s.' % (profiles_dir, prefix,
            profiles_dir))

    return profiles_path


def translation_directory_path():
    """
    Returns the absolute path to the directory containing the files for batch
    translation
    """
    return "%s/documents/translation" % os.path.dirname(__file__)


def upload_directory_path(request):
    """
    Returns the absolute path to the directory used for file uploads
    """
    if 'lmkp.file_upload_dir' in request.registry.settings:
        return request.registry.settings['lmkp.file_upload_dir']
    return None


def upload_max_file_size(request):
    """
    Returns the maximum file size (in kilobytes) for uploads.
    Default: 5120 (5MB)
    """
    if 'lmkp.file_upload_max_size' in request.registry.settings:
        try:
            return int(
                request.registry.settings['lmkp.file_upload_max_size']) * 1024
        except ValueError:
            pass
    return 5120 * 1024


def valid_mime_extensions(request):
    """
    Returns the valid mime-types as well as the file extension for each.
    """
    if 'lmkp.file_mime_extensions' in request.registry.settings:
        fme = request.registry.settings['lmkp.file_mime_extensions']

        # Create a new dict which contains only the entries recognized as valid
        # mime types by python's own mimetypes module.
        vfme = {}
        for mt in fme:
            # Make sure that the mime type defined in the ini is valid.
            try:
                mimetypes.types_map[fme[mt]]
            except KeyError:
                continue

            # Make sure that the extension defined in the ini is valid for its
            # mime type
            if fme[mt] not in mimetypes.guess_all_extensions(mt):
                continue

            # Copy it
            vfme[mt] = fme[mt]

        # Add special types by Internet Explorer
        # http://msdn.microsoft.com/en-us/library/ms775147%28v=vs.85%29.
        # aspx#_replace
        if 'image/jpeg' in vfme:
            vfme['image/pjpeg'] = '.jpg'
        if 'image/png' in vfme:
            vfme['image/x-png'] = '.png'

        return vfme

    return {}


def check_valid_uuid(uuid):
    """
    Check if a given uuid is valid
    """
    uuid4hex = re.compile('[0-9a-f-]{36}\Z', re.I)
    return uuid4hex.match(uuid) is not None


def getTemplatePath(request, tplName):
    """
    Get the path to the customized Mako templates. Use the folder name set in
    the application's ini file or use the default folder name if no
    customization is specified.
    """

    prefix = getCustomizationName(request)

    return 'lmkp:customization/%s/templates/%s' % (prefix, tplName)


def getCustomizationName(requestOrSettings):
    """
    Return the name of the customization as defined in the application's ini
    file. If none is specified, an error is raised.
    """

    if (isinstance(requestOrSettings, Request)
            or isinstance(requestOrSettings, DummyRequest)):
        settings = requestOrSettings.registry.settings
    elif isinstance(requestOrSettings, dict):
        settings = requestOrSettings

    # Check if a customization parameter is set
    if 'lmkp.customization' in settings:
        customization = settings['lmkp.customization']
    else:
        raise Exception(
            'No customization specified! There is no customization '
            '(lmkp.customization) specified in the application''s .ini file!')

    # Check if such a folder exists
    if not os.path.exists(os.path.join(
            os.path.dirname(__file__), 'customization', customization)):
        raise Exception(
            'Customization folder not found! The folder for the customization '
            '(%s) is not found. Make sure it is situated at '
            'lmkp/customization/%s.' % (customization, customization))

    return customization
