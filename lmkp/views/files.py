import hashlib
import logging
import os
import simplejson as json
import string
import uuid

from lmkp.config import check_valid_uuid
from lmkp.config import upload_directory_path
from lmkp.config import upload_max_file_size
from lmkp.models.database_objects import File
from lmkp.models.meta import DBSession as Session

from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

@view_config(route_name='file_upload', permission='edit')
def file_upload(request):
    """
    Handle the upload of a new file.
    Note that when uploading a file using a form in Ext, the content-type of the
    server response needs to be in 'text/html', otherwise Ext will throw an
    error when trying to decode the JSON string
    http://stackoverflow.com/a/10388091

    http://code.google.com/p/file-uploader/
    """

    TEMP_FOLDER_NAME = 'temp'

    ret = {'success': False}
    valid = True

    filename = None
    filetype = None
    file = None
    try:
        filename = request.POST['file'].filename
        file = request.POST['file'].file
        filetype = request.POST['file'].type
    except:
        ret['msg'] = _('server-error_not-all-post-values',
            default='Not all necessary values were provided.')
        valid = False

    if (filename is not None and file is not None and filetype is not None
        and valid is True):
        
        # Check upload directory
        if valid is True:
            upload_path = upload_directory_path(request)
            if upload_path is None or not os.path.exists(upload_path):
                valid = False
                ret['msg'] = _('server-error_files-no-upload-directory',
                    default='Upload directory not specified or not found.')

        # Check filetype
        if valid is True:
            fileextension = get_valid_file_extension(filetype)
            if fileextension is None:
                valid = False
                ret['msg'] = _('server-error_invalid-file-type',
                    default='File type is not valid.')

        # Check filesize
        if valid is True:
            size = get_file_size(file)
            if size > upload_max_file_size(request):
                valid = False
                ret['msg'] = _('server-error_uploaded-file-too-big',
                    default='File is too big.')

        if valid is True:
            # Do the actual file processing

            # Strip leading path from file name to avoid directory traversal
            # attacks
            old_filename = os.path.basename(filename)

            # Internet Explorer will attempt to provide full path for filename
            # fix
            old_filename = old_filename.split('\\')[-1]

            # Remove the extension and check the filename
            clean_filename = '.'.join(old_filename.split('.')[:-1])
            clean_filename = _clean_filename(clean_filename)

            # Make sure the filename is not too long
            if len(clean_filename) > 500:
                clean_filename = clean_filename[:500]

            # Append the predefined file extension
            clean_filename = '%s.%s' % (clean_filename, fileextension)

            # Use a randomly generated UUID as filename
            file_identifier = uuid.uuid4()
            new_filename = '%s.%s' % (file_identifier, fileextension)

            # Check if the directories already exist. If not, create them.
            if not os.path.exists(os.path.join(upload_path, TEMP_FOLDER_NAME)):
                os.makedirs(os.path.join(upload_path, TEMP_FOLDER_NAME))

            new_filepath = os.path.join(
                upload_path, TEMP_FOLDER_NAME, new_filename
            )

            # Open the new file for writing
            f = open(new_filepath, 'wb', 10000)

            datalength = 0

            # Read the file in chunks
            for chunk in _file_buffer(file):
                f.write(chunk)
                datalength += len(chunk)
            f.close()

            # Open the file again to get the hash
            hash = get_file_hash(new_filepath)

            # Database values
            db_file = File(
                identifier = file_identifier,
                name = clean_filename,
                mime = filetype,
                size = datalength,
                hash = hash
            )
            Session.add(db_file)

            log.debug('The uploaded file (%s) was saved as %s at %s'
                % (clean_filename, new_filename, new_filepath))

            ret['filename'] = clean_filename
            ret['fileidentifier'] = str(file_identifier)
            
            ret['msg'] = _('server-success_files-upload-successful',
                default='File was successfully uploaded')
            ret['success'] = True

    localizer = get_localizer(request)
    ret['msg'] = localizer.translate(ret['msg'])

    # Send the response with content-type 'text/html'
    return Response(content_type='text/html', body=json.dumps(ret))

@view_config(route_name='file_view')
def file_view(request):
    """
    Show an uploaded file.
    .../{action}/{identifier}
    """

    TEMP_FOLDER_NAME = 'temp'

    try:
        action = request.matchdict['action']
        identifier = request.matchdict['identifier']
    except KeyError:
        raise HTTPNotFound()

    # Check if the action is valid
    if not (action == 'view' or action == 'download'):
        raise HTTPNotFound()

    # Check if the identifier is valid
    if check_valid_uuid(identifier) is False:
        raise HTTPNotFound()

    # Try to find necessary information of the file (mime-type)
    db_file_query = Session.query(
            File
        ).\
        filter(File.identifier == identifier)

    try:
        db_file = db_file_query.one()
    except NoResultFound:
        raise HTTPNotFound()
    except MultipleResultsFound:
        # This should actually never happen since we are dealing with UUIDs
        raise HTTPNotFound()

    # Get file extension
    extension = get_valid_file_extension(db_file.mime)
    if extension is None:
        # This should also never happen because files without valid mime type
        # should not have been uploaded in the first place
        raise HTTPNotFound()

    # Put together the filename
    filename = '%s.%s' % (identifier, extension)

    # Try to find the file on disk
    upload_path = upload_directory_path(request)
    folder1, folder2 = get_folders_from_identifier(str(identifier))
    filepath = os.path.join(upload_path, folder1, folder2, filename)

    # Check that the file is on the disk
    if not os.path.exists(filepath):
        # If the file was not found in its proper directory, try to find it in
        # the temporary upload directory
        filepath = os.path.join(upload_path, TEMP_FOLDER_NAME, filename)
        if not os.path.exists(filepath):
            # If it is still not found, raise error
            raise HTTPNotFound()

    # Open the file
    file = open(filepath, 'rb').read()

    response = Response(
        body=file,
        content_type=str(db_file.mime)
    )

    if action == 'download':
        response.content_disposition='attachment; filename=%s' % db_file.name

    return response

def check_file_location_name(request, filevaluestring):
    """
    Check if the files in a filevaluestring of the format 
      cleanfilename|fileidentifier,cleanfilename|fileidentifier
    are still in the temporary upload directory (meaning that they were just 
    recently uploaded). If so, move them to their proper directory (create it if
    necessary).
    (Also check if the file was renamed. In this case, update the database
    entry.) - see comments below
    """

    TEMP_FOLDER_NAME = 'temp'

    # A database query is needed to find out the mime-type (for the file
    # extension) and the name of the file.

    fileidentifiers = []
    filenames = []

    fileobjects = filevaluestring.split(',')
    for file in fileobjects:
        # Collect all fileidentifiers to query the database only once
        f = file.split('|')
        if len(f) != 2:
            # Something is wrong with the filevaluestring: skip it
            continue
        fileidentifiers.append(f[1])
        filenames.append(f[0])

    files_query = Session.query(File).\
        filter(File.identifier.in_(fileidentifiers)).\
        all()

    for i, fileidentifier in enumerate(fileidentifiers):
        # Loop all the file identifiers
        for f_db in files_query:
            # For each file identifier, try to find it in the database query
            if str(f_db.identifier) != fileidentifier:
                continue

            # Check if the file needs to be moved. This is the case if the file
            # is found in the temporary upload directory.

            extension = get_valid_file_extension(f_db.mime)
            if extension is None:
                # This should also never happen because files without valid mime
                # type should not have been uploaded in the first place
                continue

            # Put together the filename
            filename = '%s.%s' % (fileidentifier, extension)

            # Try to find the file in the temporary directory
            upload_path = upload_directory_path(request)
            filepath = os.path.join(upload_path, TEMP_FOLDER_NAME, filename)

            if os.path.exists(filepath):
                # If the file is still in the temporary directory, move it
                folder1, folder2 = get_folders_from_identifier(fileidentifier)
                new_location = os.path.join(upload_path, folder1, folder2)

                # If the directory does not yet exist, create it
                if not os.path.exists(new_location):
                    os.makedirs(new_location)

                # Rename works to move the file
                os.rename(filepath, os.path.join(new_location, filename))

                log.debug('Moved file %s from temporary folder to new location at %s.'
                    % (f_db.name, new_location))

            # TODO
            # Maybe renaming a file in the database should only happen after
            # review. Maybe it is not necessary at all because the filename to
            # display always comes from 'value' of tag.
            """
            # Check if the file was renamed
            if f_db.name != filenames[i]:

                # Update the filename
                Session.query(File).\
                    filter(File.identifier == fileidentifier).\
                    update({'name': filenames[i]})

                log.debug('Renamed file to %s' % filenames[i])
            """
                
def get_file_hash(filepath, hexdigest=True):
    """
    Calculate the hash digest of a file.
    """
    f = open(filepath, 'r', 10000)
    h = hashlib.sha1()
    for chunk in _file_buffer(f):
        h.update(chunk)
    f.close()
    if hexdigest is True:
        return h.hexdigest()
    return h.digest()

def get_file_size(file):
    """
    Return the size of a file.
    """
    file.seek(0, 2) # Seek to the end of the file
    size = file.tell() # Get the position of EOF
    file.seek(0) # Reset the file position to the beginning
    return size

def get_valid_file_extension(mimetype):
    """
    Helper function to return a standard file extension for a given mimetype.
    Also used to check valid file types (return None if not supported)
    Many thanks to Internet Explorer for treating everything a little different
    once again.
    (http://msdn.microsoft.com/en-us/library/ms775147%28v=vs.85%29.aspx#_replace)
    """
    if mimetype == 'image/jpeg' or mimetype == 'image/pjpeg':
        # for .jpeg and .jpg return .jpg
        return 'jpg'
    elif mimetype == 'image/png' or mimetype == 'image/x-png':
        return 'png'
    elif mimetype == 'image/gif':
        return 'gif'
    else:
        return None

def get_folders_from_identifier(identifier):
    """
    Return the folder structure based on an identifier.
    Folder 1: the first two digits of the identifier
    Folder 2: the third digit of the identifier
    """
    return identifier[:2], identifier[2:3]

def _file_buffer(f, chunk_size=10000):
    """
    Helper function to process a file chunkwise
    """
    while True:
        chunk = f.read(chunk_size)
        if not chunk: break
        yield chunk

def _clean_filename(filename):
    """
    Return a clean filename by removing all invalid characters from the input.
    """
    # Then make sure the filename is valid by removing all invalid characters
    valid_chars = frozenset("-_.() %s%s"
        % (string.ascii_letters, string.digits))
    filename = ''.join(
        c for c in filename if c in valid_chars)
    if filename == '':
        # If all the characters were removed, use a default filename
        filename = 'defaultfilename'
    return filename
