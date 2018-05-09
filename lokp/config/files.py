import mimetypes

from pyramid.settings import aslist


def upload_directory_path(request):
    """
    Returns the absolute path to the directory used for file uploads
    """
    if 'lokp.file_upload_dir' in request.registry.settings:
        return request.registry.settings['lokp.file_upload_dir']
    return None


def upload_max_file_size(request):
    """
    Returns the maximum file size (in kilobytes) for uploads.
    Default: 5120 (5MB)
    """
    if 'lokp.file_upload_max_size' in request.registry.settings:
        try:
            return int(
                request.registry.settings['lokp.file_upload_max_size']) * 1024
        except ValueError:
            pass
    return 5120 * 1024


def valid_mime_extensions(request):
    """
    Returns the valid mime-types as well as the file extension for each.
    """
    if 'lokp.file_mime_extensions' not in request.registry.settings: # file extensions can be added to registry by changing development.ini
        return {}

    vfme = {}
    fme = request.registry.settings['lokp.file_mime_extensions']

    for row in aslist(fme, flatten=False):
        mime, extension = row.split(' ')

        # Make sure that the mime type defined in the ini is valid.
        try:
            mimetypes.types_map[extension]
        except KeyError:
            continue

        # Make sure that the extension defined in the ini is valid for its
        # mime type
        if extension not in mimetypes.guess_all_extensions(mime):
            continue

        vfme[mime] = extension

    # Add special types by Internet Explorer
    # http://msdn.microsoft.com/en-us/library/ms775147%28v=vs.85%29.
    # aspx#_replace
    if 'image/jpeg' in vfme.keys():
        vfme['image/pjpeg'] = '.jpg'
    if 'image/png' in vfme.keys():
        vfme['image/x-png'] = '.png'

    return vfme


def getFileUploadValidExtensions(request):
    """
    Return an ordered list of valid file extensions for uploads as defined in
    the ini configuration of the application.
    """
    extensions = []
    validExtensions = valid_mime_extensions(request)
    for currentExtension in validExtensions:
        for knownExtension in mimetypes.guess_all_extensions(currentExtension):
            # Add each extension only once
            if knownExtension not in extensions:
                extensions.append(knownExtension)
    return sorted(extensions)


def getFileUploadMaximumSize(request):
    """
    Return a nicely rendered string of the maximum file size for uploads as
    defined in the ini configuration of the application.
    """
    maxSize = upload_max_file_size(request)
    if maxSize < (1024 * 1024):
        maxSize = '%s KB' % (maxSize / 1024)
    else:
        maxSize = '%s MB' % round(maxSize / (1024 * 1024.0), 1)
    return maxSize
